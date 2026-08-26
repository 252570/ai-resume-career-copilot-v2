"use client";

/**
 * Quiet Signal Studio workspace: an asymmetric paper-and-rail application shell.
 * The interface shows deterministic methods and source-linked evidence plainly;
 * vermilion signals the next deliberate action rather than decorative urgency.
 */
import { FormEvent, type ReactNode, useCallback, useEffect, useMemo, useState } from "react";

import { ResumeUploadPanel } from "./ResumeUploadPanel";
import { BrandMark } from "./BrandMark";
import { getResumeApiBaseUrl } from "../lib/api";

type User = { id: string; email: string; display_name: string };
type Resume = { id: string; filename: string; status: string; parsed: { candidate_name: string | null; skills: string[]; summary?: string | null } };
type Job = { id: string; title: string; company_name: string | null; source_url?: string | null; parsed: { required_skills: string[]; preferred_skills: string[] } };
type Gap = { skill: string; requirement_type: string; priority: string; job_evidence: string | null };
type Analysis = { id: string; match_score: number; matched_skills: string[]; missing_skills: string[]; partially_matched_areas: string[]; resume_evidence: Record<string, string[]>; ats: { keyword_coverage?: number; improvement_areas?: string[]; checks?: { name: string; passed: boolean; detail: string }[] }; skill_gaps: Gap[]; score_breakdown: Record<string, number> };
type Plan = { roadmap: { id: string; skill: string; priority: string; sequence: number; practice_suggestion: string; learning_stage: string; completed: boolean }[]; projects: { title: string; purpose: string; skills_developed: string[]; difficulty: string; portfolio_value: string }[] };
type Application = { id: string; company_name: string; role_title: string; status: string; applied_at: string | null; notes: string | null };
type Dashboard = { resume_count: number; job_count: number; application_count: number; interviews_in_progress: number; applications_by_status: Record<string, number>; recent_applications: Application[] };
type Interview = { id: string; title: string; questions: { index: number; category: string; prompt: string; focus_skill: string | null }[]; responses: { question_index: number; answer: string; feedback: { score: number; strengths: string[]; improvements: string[]; disclaimer: string } }[] };

const nav = ["Overview", "Resumes", "Jobs", "Match", "Roadmap", "Practice", "Applications", "Account"] as const;
type View = (typeof nav)[number];

const onboardingSteps = [
  { view: "Resumes" as View, label: "Add resume evidence", description: "Upload a PDF, DOCX, or TXT resume." },
  { view: "Jobs" as View, label: "Save a target role", description: "Paste the requirements you want to compare." },
  { view: "Match" as View, label: "Run an explainable match", description: "See strengths, gaps, and next evidence." },
] as const;

function errorText(payload: unknown) {
  return typeof payload === "object" && payload && "detail" in payload && typeof (payload as { detail: unknown }).detail === "string"
    ? (payload as { detail: string }).detail
    : "The requested operation could not be completed.";
}

export function CopilotWorkspace() {
  const [view, setView] = useState<View>("Overview");
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [interview, setInterview] = useState<Interview | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isHydrating, setIsHydrating] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "signup">("signup");
  const [showPassword, setShowPassword] = useState(false);
  const [showDemo, setShowDemo] = useState(false);
  const [jobDescription, setJobDescription] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [jobCompany, setJobCompany] = useState("");
  const [jobSourceUrl, setJobSourceUrl] = useState("");
  const [selectedResume, setSelectedResume] = useState("");
  const [selectedJob, setSelectedJob] = useState("");
  const [applicationCompany, setApplicationCompany] = useState("");
  const [applicationRole, setApplicationRole] = useState("");
  const [answer, setAnswer] = useState("");
  const [activeQuestion, setActiveQuestion] = useState(0);

  const api = getResumeApiBaseUrl();
  const hasApi = Boolean(api);

  const request = useCallback(async <T,>(path: string, init: RequestInit = {}, requiresAuth = true): Promise<T> => {
    if (!api) throw new Error("Set NEXT_PUBLIC_API_BASE_URL to connect the Copilot workspace to its FastAPI service.");
    const headers = new Headers(init.headers);
    if (requiresAuth && token && token !== "cookie") headers.set("Authorization", `Bearer ${token}`);
    if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");

    let response: Response;
    try {
      response = await fetch(`${api}${path}`, { ...init, headers, credentials: "include" });
    } catch {
      throw new Error("The career service is waking up or temporarily unreachable. Please wait a moment and try again.");
    }

    const body = await response.json().catch(() => null);
    if (!response.ok) throw new Error(errorText(body));
    return body as T;
  }, [api, token]);

  const refreshWorkspace = useCallback(async () => {
    if (!token) return;
    setIsRefreshing(true);
    try {
      const [profile, resumeData, jobData, dashboardData, applicationData] = await Promise.all([
        request<User>("/auth/me"),
        request<Resume[]>("/resumes"),
        request<Job[]>("/jobs"),
        request<Dashboard>("/dashboard"),
        request<Application[]>("/applications"),
      ]);
      setUser(profile);
      setResumes(resumeData);
      setJobs(jobData);
      setDashboard(dashboardData);
      setApplications(applicationData);
      setSelectedResume((value) => value || resumeData[0]?.id || "");
      setSelectedJob((value) => value || jobData[0]?.id || "");
    } catch (error) {
      const isExpiredSession = error instanceof Error && /token|authenticated|Authentication|expired/i.test(error.message);
      setMessage(isExpiredSession ? "Your session expired. Please sign in again." : error instanceof Error ? error.message : "Could not refresh your workspace.");
      if (isExpiredSession) {
        setToken(null);
        setUser(null);
      }
    } finally {
      setIsRefreshing(false);
    }
  }, [request, token]);

  useEffect(() => {
    // The browser cannot read the HttpOnly session cookie. A lightweight /auth/me
    // request below establishes whether this browser has a valid session.
    setToken("cookie");
    setIsHydrating(false);
  }, []);

  useEffect(() => {
    void refreshWorkspace();
  }, [refreshWorkspace]);

  const login = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsBusy(true);
    setMessage(null);
    const form = new FormData(event.currentTarget);
    try {
      const path = authMode === "signup" ? "/auth/signup" : "/auth/login";
      const body = authMode === "signup"
        ? { email: form.get("email"), password: form.get("password"), display_name: form.get("display_name") }
        : { email: form.get("email"), password: form.get("password") };
      const result = await request<{ access_token: string; user: User }>(path, { method: "POST", body: JSON.stringify(body) }, false);
      // The API sets the HttpOnly cookie. Keep the response token only in memory
      // for this page session so older browser cookie policies still have a fallback;
      // it is never persisted to localStorage or sessionStorage.
      setToken(result.access_token);
      setUser(result.user);
      setMessage("Your private workspace is ready.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Account access failed.");
    } finally {
      setIsBusy(false);
    }
  };

  const signOut = async () => {
    try {
      await request<void>("/auth/logout", { method: "POST" }, false);
    } catch {
      // Clear local React state even if the service is waking up; the cookie will expire server-side.
    } finally {
      setToken(null);
      setUser(null);
      setMessage(null);
      setView("Overview");
    }
  };

  const createJob = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsBusy(true);
    setMessage(null);
    try {
      await request<Job>("/jobs", { method: "POST", body: JSON.stringify({ title: jobTitle || null, company_name: jobCompany || null, source_url: jobSourceUrl || null, description: jobDescription }) });
      setJobDescription("");
      setJobTitle("");
      setJobCompany("");
      setJobSourceUrl("");
      setMessage("Job requirements were parsed and saved to your workspace.");
      await refreshWorkspace();
      setView("Match");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Job intake failed.");
    } finally {
      setIsBusy(false);
    }
  };

  const runMatch = async () => {
    if (!selectedResume || !selectedJob) {
      setMessage("Select both a resume and a job description before running an analysis.");
      return;
    }
    setIsBusy(true);
    setMessage(null);
    try {
      const result = await request<Analysis>("/analyses/match", { method: "POST", body: JSON.stringify({ resume_id: selectedResume, job_id: selectedJob }) });
      setAnalysis(result);
      setPlan(null);
      setMessage("The deterministic, source-linked match is ready to review.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Match analysis failed.");
    } finally {
      setIsBusy(false);
    }
  };

  const createPlan = async () => {
    if (!analysis) {
      setMessage("Run a match before creating a roadmap.");
      return;
    }
    setIsBusy(true);
    setMessage(null);
    try {
      const result = await request<Plan>(`/plans/${analysis.id}/generate`, { method: "POST" });
      setPlan(result);
      setView("Roadmap");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Roadmap generation failed.");
    } finally {
      setIsBusy(false);
    }
  };

  const toggleRoadmapItem = async (itemId: string, completed: boolean) => {
    setIsBusy(true);
    setMessage(null);
    try {
      const result = await request<Plan>(`/plans/items/${itemId}`, { method: "PATCH", body: JSON.stringify({ completed }) });
      setPlan(result);
      setMessage(completed ? "Roadmap step marked complete across your account." : "Roadmap step reopened.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Roadmap progress could not be saved.");
    } finally {
      setIsBusy(false);
    }
  };

  const beginPractice = async () => {
    setIsBusy(true);
    setMessage(null);
    try {
      const result = await request<Interview>("/interviews", { method: "POST", body: JSON.stringify({ resume_id: selectedResume || null, job_id: selectedJob || null, question_count: 4 }) });
      setInterview(result);
      setActiveQuestion(0);
      setAnswer("");
      setView("Practice");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not create an interview session.");
    } finally {
      setIsBusy(false);
    }
  };

  const saveAnswer = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!interview) return;
    setIsBusy(true);
    setMessage(null);
    try {
      const result = await request<Interview>(`/interviews/${interview.id}/responses`, { method: "POST", body: JSON.stringify({ question_index: activeQuestion, answer }) });
      setInterview(result);
      setMessage("Response saved with transparent structure feedback.");
      if (activeQuestion < interview.questions.length - 1) {
        const nextIndex = activeQuestion + 1;
        setActiveQuestion(nextIndex);
        setAnswer(result.responses.find((response) => response.question_index === nextIndex)?.answer ?? "");
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not save the response.");
    } finally {
      setIsBusy(false);
    }
  };

  const goToQuestion = (index: number) => {
    if (!interview) return;
    const next = Math.max(0, Math.min(index, interview.questions.length - 1));
    setActiveQuestion(next);
    setAnswer(interview.responses.find((response) => response.question_index === next)?.answer ?? "");
  };

  const addApplication = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsBusy(true);
    setMessage(null);
    try {
      await request<Application>("/applications", { method: "POST", body: JSON.stringify({ company_name: applicationCompany, role_title: applicationRole, job_id: selectedJob || null, status: "saved" }) });
      setApplicationCompany("");
      setApplicationRole("");
      setMessage("Application added to your private tracker.");
      await refreshWorkspace();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Application could not be saved.");
    } finally {
      setIsBusy(false);
    }
  };

  const exportAccount = async () => {
    setIsExporting(true);
    setMessage(null);
    try {
      const payload = await request<Record<string, unknown>>("/account/export");
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `career-copilot-export-${new Date().toISOString().slice(0, 10)}.json`;
      link.click();
      URL.revokeObjectURL(url);
      setMessage("Your account export was downloaded.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The account export could not be created.");
    } finally {
      setIsExporting(false);
    }
  };

  const deleteAccount = async () => {
    if (!window.confirm("Delete this account and all saved career records permanently? This cannot be undone.")) return;
    if (window.prompt("Type DELETE to permanently remove this account.") !== "DELETE") {
      setMessage("Account deletion cancelled.");
      return;
    }
    setIsDeleting(true);
    setMessage(null);
    try {
      await request<void>("/account", { method: "DELETE" });
      setToken(null);
      setUser(null);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The account could not be deleted.");
    } finally {
      setIsDeleting(false);
    }
  };

  if (!hasApi) {
    return <section className="service-boundary"><p className="eyebrow">Service boundary</p><h1>Connect the <em>career engine.</em></h1><p>Set <code>NEXT_PUBLIC_API_BASE_URL</code> to the FastAPI <code>/api/v1</code> address, then reload this static frontend. No account or resume data is stored in the browser.</p></section>;
  }

  if (isHydrating) {
    return <section className="status-screen" role="status" aria-live="polite"><span className="loading-mark" aria-hidden="true" /><p className="eyebrow">Private career workspace</p><h1>Opening your <em>dossier.</em></h1><p>Checking this browser for an existing session.</p></section>;
  }

  if (!token || !user) {
    return <section className="auth-stage">
      <div className="auth-intro">
        <div className="auth-folio"><BrandMark /><span>Private file / 01</span><i aria-hidden="true" /></div>
        <p className="eyebrow">Private career workspace</p>
        <h1>Trace each move back to <em>evidence.</em></h1>
        <p>Bring resumes, roles, deterministic gaps, practice answers, and application milestones into one owner-scoped record.</p>
        <div className="direction-index"><span>Source evidence</span><i /><span>Clear next step</span></div>
        <div className="auth-route" aria-hidden="true"><span>01</span><i /><span>Role signal</span></div>
      </div>
      <form className="auth-card" onSubmit={login} aria-label={authMode === "signup" ? "Create account" : "Sign in"}>
        <div className="auth-card-header"><span className="step-badge">{authMode === "signup" ? "01" : "02"}</span><p className="eyebrow">{authMode === "signup" ? "Create account" : "Sign in"}</p></div>
        <h2>{authMode === "signup" ? "Start a private dossier." : "Return to your dossier."}</h2>
        {authMode === "signup" && <label>Display name<input name="display_name" autoComplete="name" required minLength={2} placeholder="Your name" /></label>}
        <label>Email<input name="email" type="email" autoComplete="email" required placeholder="you@example.com" /></label>
        <label>Password<div className="password-field"><input name="password" type={showPassword ? "text" : "password"} autoComplete={authMode === "signup" ? "new-password" : "current-password"} required minLength={12} placeholder="12+ characters" /><button type="button" className="password-toggle" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? "Hide" : "Show"}</button></div></label>
        {authMode === "signup" && <p className="form-note">Use 12 or more characters. Passwords are hashed by the API; this frontend does not store them.</p>}
        <button className="signal-button" disabled={isBusy}>{isBusy ? "Working…" : authMode === "signup" ? "Create workspace" : "Sign in"}</button>
        <button type="button" className="quiet-button" onClick={() => { setAuthMode((mode) => mode === "signup" ? "login" : "signup"); setMessage(null); }}>{authMode === "signup" ? "I already have an account" : "Create a new account"}</button>
        <p className="auth-reassurance">Private by default. Your records are scoped to this account.</p>
        <button type="button" className="demo-button" onClick={() => setShowDemo((value) => !value)}>{showDemo ? "Hide sample result" : "See a sample result first"}</button>
        {showDemo && <DemoPreview />}
        {message && <p className="upload-error" role="alert">{message}</p>}
      </form>
    </section>;
  }

  return <section className="copilot-shell">
    <aside className="workspace-rail">
      <button className="brand rail-brand" onClick={() => setView("Overview")} aria-label="Open overview"><span className="mark"><span className="mark-fallback" /></span><span><strong>AI Resume</strong><small>Career Copilot</small></span></button>
      <p className="rail-label">Your evidence desk</p>
      <nav aria-label="Career workspace">{nav.map((item, index) => <button key={item} onClick={() => setView(item)} className={view === item ? "active" : ""} aria-current={view === item ? "page" : undefined}><span>0{index + 1}</span>{item}</button>)}</nav>
      <div className="rail-footer"><p>{user.display_name}</p><button className="quiet-button" onClick={() => void signOut()}>Sign out</button></div>
    </aside>
    <main className="workspace-main">
      <div className="mobile-toolbar"><button className="brand mobile-brand" onClick={() => setView("Overview")} aria-label="Open overview"><span className="mark"><span className="mark-fallback" /></span><span><strong>AI Resume</strong><small>Career Copilot</small></span></button><button className="mobile-signout" onClick={() => void signOut()}>Sign out</button></div>
      <header className="workspace-header"><div><p className="eyebrow">{view} / Owner-scoped workspace</p><h1>{view === "Overview" ? <>Find the signal in <em>your evidence.</em></> : view}</h1></div><div className="header-actions"><p className="header-status"><span /> Deterministic methods visible</p><button className="refresh-button" onClick={() => void refreshWorkspace()} disabled={isRefreshing} aria-label="Refresh workspace data">{isRefreshing ? "Refreshing…" : "Refresh"}</button></div></header>
      {message && <p className="workspace-message" role="status">{message}</p>}
      {view === "Overview" && <Overview dashboard={dashboard} analysis={analysis} resumes={resumes} jobs={jobs} onJump={setView} />}
      {view === "Resumes" && <ResumeUploadPanel accessToken={token} savedResumes={resumes} onUploaded={() => void refreshWorkspace()} />}
      {view === "Jobs" && <section className="workspace-panel"><div className="panel-intro"><p className="eyebrow">Role signal</p><h2>Save the requirements before you compare.</h2><p>Paste an authentic job description. The API extracts only explicitly evidenced requirements and keeps its deterministic output attached to your account.</p></div><form className="stack-form" onSubmit={createJob}><label>Role title <input value={jobTitle} onChange={(event) => setJobTitle(event.target.value)} placeholder="Backend Engineer" /></label><label>Company <input value={jobCompany} onChange={(event) => setJobCompany(event.target.value)} placeholder="Company name" /></label><label>Source URL <input type="url" value={jobSourceUrl} onChange={(event) => setJobSourceUrl(event.target.value)} placeholder="https://company.com/role" /></label><label>Job description <textarea value={jobDescription} onChange={(event) => setJobDescription(event.target.value)} required minLength={40} maxLength={50000} placeholder="Paste the job description and requirements…" /><span className="field-meta">{jobDescription.length.toLocaleString()} / 50,000 characters</span></label><button className="signal-button" disabled={isBusy || jobDescription.trim().length < 40}>{isBusy ? "Parsing…" : "Parse & save role"}</button></form><EvidenceList title="Saved roles" items={jobs.map((job) => <div key={job.id}><strong>{job.title}</strong><small>{job.company_name || "Company not detected"}{job.source_url ? <> · <a className="source-link" href={job.source_url} target="_blank" rel="noreferrer">Source ↗</a></> : null}</small><p>{job.parsed.required_skills.length ? `Required: ${job.parsed.required_skills.join(", ")}` : "No supported requirements detected yet."}</p></div>)} /></section>}
      {view === "Match" && <section className="workspace-panel match-surface"><div className="panel-intro"><p className="eyebrow">Explainable alignment</p><h2>Compare two source records.</h2><p>The score is a deterministic overlap measure with visible matched terms, gap priority, and ATS-style coverage notes. It is not a prediction of hiring outcomes.</p></div>{!resumes.length || !jobs.length ? <div className="guided-empty"><span className="step-badge">03</span><div><h3>Build the two source records first.</h3><p>{!resumes.length ? "Add a resume" : "Save a role"} to unlock a source-linked comparison.</p><button className="signal-button" onClick={() => setView(!resumes.length ? "Resumes" : "Jobs")}>{!resumes.length ? "Add resume evidence" : "Save a target role"}</button></div></div> : <><div className="match-controls"><label>Resume<select value={selectedResume} onChange={(event) => setSelectedResume(event.target.value)}><option value="">Choose a resume</option>{resumes.map((resume) => <option key={resume.id} value={resume.id}>{resume.filename}</option>)}</select></label><label>Job description<select value={selectedJob} onChange={(event) => setSelectedJob(event.target.value)}><option value="">Choose a role</option>{jobs.map((job) => <option key={job.id} value={job.id}>{job.title}</option>)}</select></label><button className="signal-button" onClick={runMatch} disabled={isBusy || !selectedResume || !selectedJob}>{isBusy ? "Comparing…" : "Run source-linked match"}</button></div>{analysis && <AnalysisCard analysis={analysis} onPlan={createPlan} onPractice={beginPractice} isBusy={isBusy} />}</>}</section>}
      {view === "Roadmap" && <section className="workspace-panel"><div className="panel-intro"><p className="eyebrow">Skill gap → proof</p><h2>Turn missing evidence into a sequence.</h2><p>Roadmaps and portfolio prompts follow the prioritized gaps in the last saved match. They are templates to adapt, not AI-generated claims about your readiness.</p></div>{plan ? <PlanCards plan={plan} onToggle={toggleRoadmapItem} isBusy={isBusy} /> : <div className="empty-evidence"><span>04</span><p>Run a match, then create its roadmap to see skill-specific steps and portfolio prompts here.</p></div>}</section>}
      {view === "Practice" && <section className="workspace-panel"><div className="panel-intro"><p className="eyebrow">Practice interview</p><h2>Rehearse with the role in view.</h2><p>Question sets use saved job skills. Feedback checks answer structure, stated skill reference, length, and measurable language; it does not claim to judge interview quality.</p></div>{!interview ? <button className="signal-button" onClick={beginPractice} disabled={isBusy}>{isBusy ? "Preparing…" : "Start role-focused practice"}</button> : <InterviewCard interview={interview} questionIndex={activeQuestion} onQuestionChange={goToQuestion} answer={answer} setAnswer={setAnswer} onSubmit={saveAnswer} isBusy={isBusy} />}</section>}
      {view === "Applications" && <section className="workspace-panel"><div className="panel-intro"><p className="eyebrow">Application ledger</p><h2>Keep the follow-through visible.</h2><p>Entries are user-scoped and support saved, applied, screening, interviewing, offer, rejected, and withdrawn stages.</p></div><form className="inline-form" onSubmit={addApplication}><input value={applicationCompany} onChange={(event) => setApplicationCompany(event.target.value)} placeholder="Company" required /><input value={applicationRole} onChange={(event) => setApplicationRole(event.target.value)} placeholder="Role title" required /><button className="signal-button" disabled={isBusy || !applicationCompany.trim() || !applicationRole.trim()}>Add application</button></form><EvidenceList title="Current ledger" items={applications.map((item) => <div key={item.id} className="application-row"><strong>{item.role_title}</strong><span>{item.company_name}</span><b>{item.status}</b></div>)} /></section>}
      {view === "Account" && <section className="workspace-panel account-panel"><div className="panel-intro"><p className="eyebrow">Account controls</p><h2>Keep ownership <em>in your hands.</em></h2><p>Download a portable copy of your career records or permanently remove this account and its stored resume files. These actions apply only to your account.</p></div><div className="account-actions"><div><h3>Export my records</h3><p>Download your profile, resumes, roles, analyses, applications, and interview practice as JSON.</p><button className="signal-button" onClick={() => void exportAccount()} disabled={isExporting}>{isExporting ? "Preparing export…" : "Download account export"}</button></div><div className="danger-zone"><h3>Delete my account</h3><p>This permanently removes your account, saved career records, and stored resume files. It cannot be undone.</p><button className="danger-button" onClick={() => void deleteAccount()} disabled={isDeleting}>{isDeleting ? "Deleting…" : "Permanently delete account"}</button></div></div></section>}
    </main>
  </section>;
}

function Overview({ dashboard, analysis, resumes, jobs, onJump }: { dashboard: Dashboard | null; analysis: Analysis | null; resumes: Resume[]; jobs: Job[]; onJump: (view: View) => void }) {
  const completed = [resumes.length > 0, jobs.length > 0, Boolean(analysis)];
  const completedCount = completed.filter(Boolean).length;
  return <>
    <section className="metric-ledger">{[["Resumes", dashboard?.resume_count || 0, "Resumes"], ["Saved roles", dashboard?.job_count || 0, "Jobs"], ["Applications", dashboard?.application_count || 0, "Applications"], ["Practice sessions", dashboard?.interviews_in_progress || 0, "Practice"]].map(([label, value, destination]) => <button key={String(label)} onClick={() => onJump(destination as View)}><span>{label}</span><b>{value}</b><i>→</i></button>)}</section>
    <section className="overview-split"><div className="overview-narrative"><p className="eyebrow">Working principle</p><h2>Every recommendation should point back to a <em>record.</em></h2><p>Start with a resume and a genuine job description. The workspace retains the parsed source, makes scoring criteria visible, and keeps your next steps in one private place.</p><button className="signal-button" onClick={() => onJump(completedCount === 3 ? "Match" : onboardingSteps[completedCount]?.view || "Resumes")}>{completedCount === 3 ? "Review latest match" : "Continue setup"}</button></div><div className="latest-signal"><p className="eyebrow">Latest alignment</p>{analysis ? <><div className="score-orbit"><b>{Math.round(analysis.match_score)}</b><span>match<br />score</span></div><p>{analysis.missing_skills.length ? `Next evidence to build: ${analysis.missing_skills.slice(0, 3).join(", ")}.` : "No missing supported skills were identified in the last comparison."}</p></> : <p>No match has been run yet. Complete the short setup below to surface source-linked gaps.</p>}<button className="quiet-button" onClick={() => onJump("Match")}>Review alignment →</button></div></section>
    <section className="onboarding-panel" aria-labelledby="setup-heading"><div className="onboarding-heading"><div><p className="eyebrow">Your first three moves</p><h2 id="setup-heading">Make the next step <em>obvious.</em></h2></div><span className="progress-count">{completedCount} / 3 complete</span></div><div className="onboarding-progress" aria-label={`${completedCount} of 3 setup steps complete`}><span style={{ width: `${(completedCount / 3) * 100}%` }} /></div><div className="onboarding-steps">{onboardingSteps.map((step, index) => <button key={step.view} className={completed[index] ? "complete" : index === completedCount ? "current" : ""} onClick={() => onJump(step.view)}><span className="step-number">{completed[index] ? "✓" : `0${index + 1}`}</span><span><strong>{step.label}</strong><small>{completed[index] ? "Completed — review or continue." : step.description}</small></span><i>→</i></button>)}</div></section>
  </>;
}

function DemoPreview() { return <div className="demo-preview" aria-live="polite"><p className="demo-kicker">Illustrative match / no account required</p><div className="demo-score"><strong>78</strong><span>match<br />score</span></div><p className="demo-copy">A transparent result compares explicit skills instead of guessing whether someone will be hired.</p><div className="demo-tags"><span>Python</span><span>FastAPI</span><span>PostgreSQL</span><span className="missing">Cloud deployment</span></div><small>Start with your own resume and role to see source-linked evidence.</small></div>; }
function EvidenceList({ title, items }: { title: string; items: ReactNode[] }) { return <div className="evidence-list"><p className="eyebrow">{title}</p>{items.length ? items : <div className="empty-list"><span>—</span><p>Nothing saved yet. Complete the next step to build your evidence desk.</p></div>}</div>; }
function AnalysisCard({ analysis, onPlan, onPractice, isBusy }: { analysis: Analysis; onPlan: () => void; onPractice: () => void; isBusy: boolean }) { return <div className="analysis-card"><div className="score-orbit"><b>{Math.round(analysis.match_score)}</b><span>match<br />score</span></div><div><p className="eyebrow">How this score was built</p><dl>{Object.entries(analysis.score_breakdown).map(([key, value]) => <div key={key}><dt>{key.replaceAll("_", " ")}</dt><dd>{Math.round(value)} pts</dd></div>)}</dl>{typeof analysis.ats.keyword_coverage === "number" && <p className="coverage-note"><strong>{Math.round(analysis.ats.keyword_coverage)}%</strong> explicit keyword coverage</p>}</div><div className="analysis-evidence"><p className="eyebrow">Evidence found</p>{analysis.matched_skills.length ? <div className="result-tags">{analysis.matched_skills.map((skill) => <span key={skill}>{skill}</span>)}</div> : <p>No supported skills matched yet.</p>}{analysis.partially_matched_areas.length > 0 && <><p className="eyebrow">Needs review</p><ul className="result-list">{analysis.partially_matched_areas.map((area) => <li key={area}>{area}</li>)}</ul></>}{analysis.missing_skills.length > 0 && <><p className="eyebrow">Priority gaps</p><div className="result-tags gap-tags">{analysis.skill_gaps.map((gap) => <span key={`${gap.requirement_type}-${gap.skill}`}><b>{gap.priority}</b> {gap.skill}</span>)}</div></>}</div><div className="analysis-detail"><p className="eyebrow">Source lines</p>{Object.entries(analysis.resume_evidence).filter(([, lines]) => lines.length).slice(0, 4).map(([skill, lines]) => <div className="evidence-snippet" key={skill}><strong>{skill}</strong><p>{lines[0]}</p></div>)}{analysis.ats.checks?.length ? <div className="ats-checks"><p className="eyebrow">ATS-style checks</p>{analysis.ats.checks.map((check) => <div key={check.name} className={check.passed ? "passed" : "needs-work"}><span>{check.passed ? "✓" : "!"}</span><div><strong>{check.name}</strong><small>{check.detail}</small></div></div>)}</div> : null}</div><div className="analysis-actions"><button className="signal-button" onClick={onPlan} disabled={isBusy}>Build roadmap</button><button className="quiet-button" onClick={onPractice} disabled={isBusy}>Practice role questions</button></div></div>; }
  function PlanCards({ plan, onToggle, isBusy }: { plan: Plan; onToggle: (itemId: string, completed: boolean) => void; isBusy: boolean }) {
  const completedCount = plan.roadmap.filter((item) => item.completed).length;
  return <div className="plan-grid"><div><div className="plan-progress"><p className="eyebrow">Learning sequence</p><span>{completedCount} / {plan.roadmap.length} steps marked complete</span></div>{plan.roadmap.map((item) => <article className={`plan-step ${item.completed ? "done" : ""}`} key={item.id}><button type="button" className="plan-check" onClick={() => onToggle(item.id, !item.completed)} disabled={isBusy} aria-label={`${item.completed ? "Reopen" : "Complete"} ${item.skill}`} aria-pressed={item.completed}>{item.completed ? "✓" : `0${item.sequence}`}</button><h3>{item.skill}</h3><b>{item.learning_stage} · {item.priority}</b><p>{item.practice_suggestion}</p></article>)}</div><div><p className="eyebrow">Portfolio proof</p>{plan.projects.map((item) => <article key={item.title}><h3>{item.title}</h3><b>{item.difficulty}</b><p>{item.purpose}</p><small>{item.portfolio_value}</small></article>)}</div></div>;
  }

function InterviewCard({ interview, questionIndex, onQuestionChange, answer, setAnswer, onSubmit, isBusy }: { interview: Interview; questionIndex: number; onQuestionChange: (index: number) => void; answer: string; setAnswer: (value: string) => void; onSubmit: (event: FormEvent<HTMLFormElement>) => void; isBusy: boolean }) {
  const question = interview.questions[questionIndex];
  if (!question) return <div className="empty-evidence"><span>—</span><p>No practice question was returned. Try starting a new session.</p></div>;
  const feedback = interview.responses.find((response) => response.question_index === questionIndex)?.feedback;
  const answered = new Set(interview.responses.map((response) => response.question_index));
  return <div className="practice-card">
    <div className="practice-progress"><p className="eyebrow">Role practice</p><span>{answered.size} / {interview.questions.length} responses reviewed</span></div>
    <div className="question-pager" aria-label="Interview questions">{interview.questions.map((item, index) => <button type="button" key={item.index} className={index === questionIndex ? "active" : answered.has(item.index) ? "answered" : ""} onClick={() => onQuestionChange(index)} aria-label={`Open question ${index + 1}`} aria-current={index === questionIndex ? "step" : undefined}>{index + 1}</button>)}</div>
    <p className="eyebrow">Question {String(questionIndex + 1).padStart(2, "0")} / {question.category}</p>
    <h3>{question.prompt}</h3>
    <form className="stack-form" onSubmit={onSubmit}><textarea value={answer} onChange={(event) => setAnswer(event.target.value)} minLength={20} maxLength={10000} placeholder="Write your response using a truthful example…" required /><span className="field-meta">{answer.length.toLocaleString()} / 10,000 characters</span><div className="interview-nav"><button type="button" className="quiet-button" onClick={() => onQuestionChange(questionIndex - 1)} disabled={questionIndex === 0}>Previous</button><button className="signal-button" disabled={isBusy}>{isBusy ? "Checking structure…" : questionIndex === interview.questions.length - 1 ? "Save final response" : "Save & continue"}</button></div></form>
    {feedback && <div className="feedback-card"><b>Structure score: {feedback.score}/100</b><p>{feedback.strengths.join(" ")}</p><p>{feedback.improvements.join(" ")}</p><small>{feedback.disclaimer}</small></div>}
  </div>;
}
