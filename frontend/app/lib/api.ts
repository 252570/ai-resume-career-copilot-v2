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
  summary?: string[];
  projects?: string[];
  certifications?: string[];
  links?: string[];
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

const configuredApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();

export const isResumeApiConfigured = Boolean(configuredApiBaseUrl);

export function getResumeApiBaseUrl(): string | null {
  return configuredApiBaseUrl ? configuredApiBaseUrl.replace(/\/$/, "") : null;
}

export async function updateResume(
  resumeId: string,
  parsed: ParsedResume,
  accessToken?: string,
): Promise<UploadedResume> {
  const apiBaseUrl = getResumeApiBaseUrl();
  if (!apiBaseUrl) throw new ResumeApiError("The resume service is not configured for this build.");
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}/resumes/${resumeId}`, {
      method: "PATCH",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(accessToken && accessToken !== "cookie" ? { Authorization: `Bearer ${accessToken}` } : {}),
      },
      body: JSON.stringify(parsed),
    });
  } catch {
    throw new ResumeApiError("The resume service could not be reached. Please retry shortly.");
  }
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new ResumeApiError(typeof body.detail === "string" ? body.detail : "The resume evidence could not be saved.");
  return body as UploadedResume;
}

export async function uploadResume(
  file: File,
  accessToken?: string
): Promise<UploadedResume> {
  const apiBaseUrl = getResumeApiBaseUrl();
  if (!apiBaseUrl) {
    throw new ResumeApiError(
      "The resume service is not configured for this build. Set NEXT_PUBLIC_API_BASE_URL to the deployed API base URL and rebuild the frontend."
    );
  }
  const payload = new FormData();
  payload.append("file", file);

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}/resumes/upload`, {
      method: "POST",
      body: payload,
      credentials: "include",
      headers: accessToken && accessToken !== "cookie"
        ? { Authorization: `Bearer ${accessToken}` }
        : undefined,
    });
  } catch {
    throw new ResumeApiError(
      "The configured resume service could not be reached. Check that the API is deployed, healthy, and that NEXT_PUBLIC_API_BASE_URL is correct."
    );
  }

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ResumeApiError(
      typeof body.detail === "string"
        ? body.detail
        : "The resume upload could not be completed."
    );
  }
  return body as UploadedResume;
}
