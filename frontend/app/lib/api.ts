/** Quiet Signal Studio: one explicit API boundary keeps upload behavior out of visual components. */

export type ParsedResume = {
  candidate_name: string | null;
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  github: string | null;
  skills: string[];
  education: string[];
  experience: string[];
};

export type UploadedResume = {
  id: string;
  filename: string;
  content_type: string;
  file_size: number;
  status: string;
  parsed: ParsedResume;
};

export class ResumeApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ResumeApiError";
  }
}

const apiBaseUrl = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8001/api/v1").replace(/\/$/, "");

export async function uploadResume(file: File): Promise<UploadedResume> {
  const payload = new FormData();
  payload.append("file", file);

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}/resumes/upload`, { method: "POST", body: payload });
  } catch {
    throw new ResumeApiError("The resume service could not be reached. Confirm that FastAPI is running on port 8001.");
  }

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ResumeApiError(typeof body.detail === "string" ? body.detail : "The resume upload could not be completed.");
  }
  return body as UploadedResume;
}
