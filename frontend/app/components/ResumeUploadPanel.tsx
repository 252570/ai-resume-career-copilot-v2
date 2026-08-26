"use client";

/**
 * Quiet Signal Studio: this is a field-note style upload interaction—paper, ink,
 * vermilion direction, and explicit evidence states rather than dashboard chrome.
 */
import { ChangeEvent, FormEvent, useRef, useState } from "react";

import {
  isResumeApiConfigured,
  ParsedResume,
  ResumeApiError,
  UploadedResume,
  uploadResume,
} from "../lib/api";

const MAX_UPLOAD_BYTES = 5 * 1024 * 1024;
const ACCEPTED_SUFFIXES = [".pdf", ".docx", ".txt"];

function ListBlock({
  label,
  items,
  empty,
}: {
  label: string;
  items: string[];
  empty: string;
}) {
  return (
    <div className="parsed-block">
      <p>{label}</p>
      {items.length ? (
        <ul>
          {items.map(item => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <span className="empty-field">{empty}</span>
      )}
    </div>
  );
}

function ContactField({
  label,
  value,
}: {
  label: string;
  value: string | null;
}) {
  return (
    <div className="contact-field">
      <span>{label}</span>
      <strong>{value ?? "Not detected"}</strong>
    </div>
  );
}

function ParsedEvidence({ parsed }: { parsed: ParsedResume }) {
  return (
    <div className="parsed-evidence" aria-live="polite">
      <div className="result-heading">
        <span>Parsed evidence</span>
        <i /> <b>Ready</b>
      </div>
      <div className="parsed-grid">
        <div className="contact-record">
          <p>Candidate</p>
          <h3>{parsed.candidate_name ?? "Name not detected"}</h3>
          <ContactField label="Email" value={parsed.email} />
          <ContactField label="Phone" value={parsed.phone} />
          <ContactField label="LinkedIn" value={parsed.linkedin} />
          <ContactField label="GitHub" value={parsed.github} />
        </div>
        <div className="evidence-lists">
          <ListBlock
            label="Skills"
            items={parsed.skills}
            empty="No supported skills detected"
          />
          <ListBlock
            label="Education"
            items={parsed.education}
            empty="No education section detected"
          />
          <ListBlock
            label="Experience"
            items={parsed.experience}
            empty="No experience section detected"
          />
        </div>
      </div>
    </div>
  );
}

export function ResumeUploadPanel({
  accessToken,
  onUploaded,
}: {
  accessToken?: string;
  onUploaded?: (resume: UploadedResume) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadedResume | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const apiConfigured = isResumeApiConfigured;

  const selectFile = (file: File | null) => {
    setError(null);
    setResult(null);
    if (!file) {
      setSelectedFile(null);
      return;
    }
    const suffix = `.${file.name.split(".").pop()?.toLowerCase() ?? ""}`;
    if (!ACCEPTED_SUFFIXES.includes(suffix)) {
      setSelectedFile(null);
      setError("Choose a PDF, DOCX, or TXT resume.");
      return;
    }
    if (file.size > MAX_UPLOAD_BYTES) {
      setSelectedFile(null);
      setError("The selected file exceeds the 5 MB limit.");
      return;
    }
    setSelectedFile(file);
  };

  const onFileChange = (event: ChangeEvent<HTMLInputElement>) =>
    selectFile(event.target.files?.[0] ?? null);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedFile) {
      setError("Choose a resume file before uploading.");
      return;
    }
    setIsUploading(true);
    setError(null);
    setResult(null);
    try {
      const uploaded = await uploadResume(selectedFile, accessToken);
      setResult(uploaded);
      onUploaded?.(uploaded);
    } catch (uploadError) {
      setError(
        uploadError instanceof ResumeApiError
          ? uploadError.message
          : "The resume upload could not be completed."
      );
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <section
      className="upload-ledger"
      id="resume-upload"
      aria-labelledby="upload-heading"
    >
      <div className="upload-intro">
        <p className="eyebrow">Career evidence / Resume intake</p>
        <h2 id="upload-heading">
          Bring the <em>source</em> into view.
        </h2>
        <p>
          Upload a resume. The parser extracts readable evidence without
          inventing profile details, then attaches it to your signed-in
          workspace when an account is active.
        </p>
        <dl>
          <div>
            <dt>Formats</dt>
            <dd>PDF / DOCX / TXT</dd>
          </div>
          <div>
            <dt>Limit</dt>
            <dd>5 MB maximum</dd>
          </div>
          <div>
            <dt>Method</dt>
            <dd>Deterministic parsing</dd>
          </div>
        </dl>
      </div>

      <div className="upload-workspace">
        <form className="upload-form" onSubmit={onSubmit}>
          {!apiConfigured && (
            <p className="local-only-note" role="status">
              <strong>Resume service configuration required.</strong> This
              frontend build has no API base URL. For local development, create{" "}
              <code>frontend/.env.local</code> with{" "}
              <code>NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001/api/v1</code>
              . For production, set the variable to the deployed API base URL
              before building.
            </p>
          )}
          <input
            ref={inputRef}
            className="file-input"
            id="resume-file"
            type="file"
            accept=".pdf,.docx,.txt,application/pdf,text/plain,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={onFileChange}
            onClick={(event) => { event.currentTarget.value = ""; }}
            aria-describedby="resume-file-help"
          />
          <label
            className={`drop-zone ${selectedFile ? "has-file" : ""}`}
            htmlFor="resume-file"
          >
            <span className="file-corner" aria-hidden="true" />
            <span className="drop-kicker">Source document</span>
            <strong>
              {selectedFile ? selectedFile.name : "Choose a resume file"}
            </strong>
            <small id="resume-file-help">
              {selectedFile
                ? `${Math.max(1, Math.ceil(selectedFile.size / 1024))} KB selected · ready to review`
                : "PDF, DOCX, or TXT · up to 5 MB"}
            </small>
          </label>
          <div className="form-actions">
            <button
              className="signal-button"
              type="submit"
              disabled={isUploading || !apiConfigured}
            >
              {isUploading
                ? "Reading evidence…"
                : apiConfigured
                  ? "Upload & parse"
                  : "Local API required"}
            </button>
            <button
              className="quiet-button"
              type="button"
              disabled={isUploading}
              onClick={() => {
                setSelectedFile(null);
                setResult(null);
                setError(null);
                if (inputRef.current) inputRef.current.value = "";
              }}
            >
              Clear
            </button>
          </div>
          {isUploading && (
            <p className="upload-progress" role="status" aria-live="polite">
              Reading the document and extracting only text-based evidence. Keep this tab open while the service responds.
            </p>
          )}
          {error && (
            <p className="upload-error" role="alert">
              {error}
            </p>
          )}
          {result && (
            <p className="upload-success" role="status">
              Stored {result.filename} · {result.status}. Review the extracted evidence below before using it in a match.
            </p>
          )}
        </form>
        {result ? (
          <>
            <p className="review-note"><strong>Review before comparing.</strong> Parsed fields are evidence from the uploaded source, not verified claims. Correct the source document and upload a new version if anything looks wrong.</p>
            <ParsedEvidence parsed={result.parsed} />
          </>
        ) : (
          <div className="empty-evidence" aria-live="polite">
            <span>01</span>
            <p>
              Parsed details will appear here after a readable resume is
              uploaded.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
