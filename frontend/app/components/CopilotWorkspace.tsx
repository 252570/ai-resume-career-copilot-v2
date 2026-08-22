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
type Job = { id: string; title: string; company_name: string | null; parsed: { required_skills: string[]; preferred_skills: string[] } };
type Gap = { skill: string; priority: string; reason: string };
type Analysis = { id: string; match_score: number; matched_skills: string[]; missing_skills: string[]; ats: { score?: number; notes?: string[] }; skill_gaps: Gap[]; score_breakdown: Record<string, number> };
type Plan = { roadmap: { skill: string; priority: string; sequence: number; practice_suggestion: string; learning_stage: string }[]; projects: { title: string; purpose: string; skills_developed: string[]; difficulty: string; portfolio_value: string }[] };
type Application = { id: string; company_name: string; role_title: string; status: string; applied_at: string | null; notes: string | null };
type Dashboard = { resume_count: number; job_count: number; application_count: number; interviews_in_progress: number; applications_by_status: Record<string, number>; recent_applications: Application[] };
type Interview = { id: string; title: string; questions: { index: number; category: string; prompt: string; focus_skill: string | null }[]; responses: { question_index: number; answer: string; feedback: { score: number; strengths: string[]; improvements: string[]; disclaimer: string } }[] };

const nav = ["Overview", "Resumes", "Jobs", "Match", "Roadmap", "Practice", "Applications"] as const;
type View = (typeof nav)[number];

function errorText(payload: unknown) {
  return typeof payload === "object" && payload && "detail" in payload && typeof (payload as { detail: unknown }).detail === "string" ? (payload as { detail: string }).detail : "The requested operation could not be completed.";
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
  const [authMode, setAuthMode] = useState<"login" | "signup">("signup");
  const [jobDescription, setJobDescription] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [jobCompany, setJobCompany] = useState("");
  const [selectedResume, setSelectedResume] = useState("");
  const [selectedJob, setSelectedJob] = useState("");
  const [applicationCompany, setApplicationCompany] = useState("");
  const [applicationRole, setApplicationRole] = useState("");
  const [answer, setAnswer] = useState("");

  const api = getResumeApiBaseUrl();
  const hasApi = Boolean(api);

  const request = useCallback(async <T,>(path: string, init: RequestInit = {}, requiresAuth = true): Promise<T> => {
    if (!api) throw new Error("Set NEXT_PUBLIC_API_BASE_URL to connect the Copilot workspace to its FastAPI service.");
    const headers = new Headers(init.headers);
    if (requiresAuth && token) headers.set("Authorization", `Bearer ${token}`);
    if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
    const response = await fetch(`${api}${path}`, { ...init, headers });
    const body = await response.json().catch(() => null);
    if (!response.ok) throw new Error(errorText(body));
    return body as T;
  }, [api, token]);

  const refreshWorkspace = useCallback(async () => {
    if (!token) return;
    try {
      const [profile, resumeData, jobData, dashboardData, applicationData] = await Promise.all([
        request<User>("/auth/me"), request<Resume[]>("/resumes"), request<Job[]>("/jobs"), request<Dashboard>("/dashboard"), request<Application[]>("/applications"),
      ]);
      setUser(profile); setResumes(resumeData); setJobs(jobData); setDashboard(dashboardData); setApplications(applicationData);
      setSelectedResume((value) => value || resumeData[0]?.id || "");
      setSelectedJob((value) => value || jobData[0]?.id || "");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not refresh your workspace.");
      if (error instanceof Error && /token|authenticated|Authentication/i.test(error.message)) {
        localStorage.removeItem("career_copilot_token"); setToken(null); setUser(null);
      }
    }
  }, [request, token]);

  useEffect(() => { setToken(localStorage.getItem("career_copilot_token")); }, []);
  useEffect(() => { void refreshWorkspace(); }, [refreshWorkspace]);

  const login = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsBusy(true); setMessage(null);
    const form = new FormData(event.currentTarget);
    try {
      const path = authMode === "signup" ? "/auth/signup" : "/auth/login";
      const body = authMode === "signup" ? { email: form.get("email"), password: form.get("password"), display_name: form.get("display_name") } : { email: form.get("email"), password: form.get("password") };
      const result = await request<{ access_token: string; user: User }>(path, { method: "POST", body: JSON.stringify(body) }, false);
      localStorage.setItem("career_copilot_token", result.access_token); setToken(result.access_token); setUser(result.user); setMessage("Your private workspace is ready.");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Account access failed."); } finally { setIsBusy(false); }
  };

  const createJob = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setIsBusy(true); setMessage(null);
    try {
      await request<Job>("/jobs", { method: "POST", body: JSON.stringify({ title: jobTitle || null, company_name: jobCompany || null, description: jobDescription }) });
      setJobDescription(""); setJobTitle(""); setJobCompany(""); setMessage("Job requirements were parsed and saved to your workspace."); await refreshWorkspace(); setView("Match");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Job intake failed."); } finally { setIsBusy(false); }
  };

  const runMatch = async () => {
    if (!selectedResume || !selectedJob) return setMessage("Select both a resume and a job description before running an analysis.");
    setIsBusy(true); setMessage(null);
    try { const result = await request<Analysis>("/analyses/match", { method: "POST", body: JSON.stringify({ resume_id: selectedResume, job_id: selectedJob }) }); setAnalysis(result); setPlan(null); setMessage("The deterministic, source-linked match is ready to review."); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Match analysis failed."); } finally { setIsBusy(false); }
  };

  const createPlan = async () => {
    if (!analysis) return setMessage("Run a match before creating a roadmap.");
    setIsBusy(true); setMessage(null);
    try { const result = await request<Plan>(`/plans/${analysis.id}/generate`, { method: "POST" }); setPlan(result); setView("Roadmap"); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Roadmap generation failed."); } finally { setIsBusy(false); }
  };

  const beginPractice = async () => {
    setIsBusy(true); setMessage(null);
    try { const result = await request<Interview>("/interviews", { method: "POST", body: JSON.stringify({ resume_id: selectedResume || null, job_id: selectedJob || null, question_count: 4 }) }); setInterview(result); setAnswer(""); setView("Practice"); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Could not create an interview session."); } finally { setIsBusy(false); }
  };

  const saveAnswer = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); if (!interview) return; setIsBusy(true); setMessage(null);
    try { const result = await request<Interview>(`/interviews/${interview.id}/responses`, { method: "POST", body: JSON.stringify({ question_index: 0, answer }) }); setInterview(result); setMessage("Response saved with transparent structure feedback."); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Could not save the response."); } finally { setIsBusy(false); }
  };

  const addApplication = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setIsBusy(true); setMessage(null);
    try { await request<Application>("/applications", { method: "POST", body: JSON.stringify({ company_name: applicationCompany, role_title: applicationRole, job_id: selectedJob || null, status: "saved" }) }); setApplicationCompany(""); setApplicationRole(""); setMessage("Application added to your private tracker."); await refreshWorkspace(); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Application could not be saved."); } finally { setIsBusy(false); }
  };

  const selectedJobRecord = useMemo(() => jobs.find((job) => job.id === selectedJob), [jobs, selectedJob]);

  if (!hasApi) return <section className="service-boundary"><p className="eyebrow">Service boundary</p><h1>Connect the <em>career engine.</em></h1><p>Set <code>NEXT_PUBLIC_API_BASE_URL</code> to the FastAPI <code>/api/v1</code> address, then reload this static frontend. No account or resume data is stored in the browser.</p></section>;

  if (!token || !user) return <section className="auth-stage"><div className="auth-intro"><div className="auth-folio"><BrandMark /><span>Private file / 01</span><i aria-hidden="true" /></div><p className="eyebrow">Private career workspace</p><h1>Trace each move back to <em>evidence.</em></h1><p>Bring resumes, roles, deterministic gaps, practice answers, and application milestones into one owner-scoped record.</p><div className="direction-index"><span>Source evidence</span><i /><span>Clear next step</span></div><div className="auth-route" aria-hidden="true"><span>01</span><i /><span>Role signal</span></div></div><form className="auth-card" onSubmit={login}><p className="eyebrow">{authMode === "signup" ? "Create account" : "Sign in"}</p><h2>{authMode === "signup" ? "Start a private dossier." : "Return to your dossier."}</h2>{authMode === "signup" && <label>Display name<input name="display_name" required minLength={2} /></label>}<label>Email<input name="email" type="email" required /></label><label>Password<input name="password" type="password" required minLength={12} /></label>{authMode === "signup" && <p className="form-note">Use 12 or more characters. Passwords are hashed by the API; this frontend does not store them.</p>}<button className="signal-button" disabled={isBusy}>{isBusy ? "Working…" : authMode === "signup" ? "Create workspace" : "Sign in"}</button><button type="button" className="quiet-button" onClick={() => setAuthMode((mode) => mode === "signup" ? "login" : "signup")}>{authMode === "signup" ? "I already have an account" : "Create a new account"}</button>{message && <p className="upload-error" role="alert">{message}</p>}</form></section>;

  return <section className="copilot-shell"><aside className="workspace-rail"><button className="brand rail-brand" onClick={() => setView("Overview")}><span className="mark"><span className="mark-fallback" /></span><span><strong>AI Resume</strong><small>Career Copilot</small></span></button><p className="rail-label">Your evidence desk</p><nav aria-label="Career workspace">{nav.map((item, index) => <button key={item} onClick={() => setView(item)} className={view === item ? "active" : ""}><span>0{index + 1}</span>{item}</button>)}</nav><div className="rail-footer"><p>{user.display_name}</p><button className="quiet-button" onClick={() => { localStorage.removeItem("career_copilot_token"); setToken(null); setUser(null); }}>Sign out</button></div></aside><main className="workspace-main"><header className="workspace-header"><div><p className="eyebrow">{view} / Owner-scoped workspace</p><h1>{view === "Overview" ? <>Find the signal in <em>your evidence.</em></> : view}</h1></div><p className="header-status"><span /> Deterministic methods visible</p></header>{message && <p className="workspace-message" role="status">{message}</p>}{view === "Overview" && <Overview dashboard={dashboard} analysis={analysis} onJump={setView} />}{view === "Resumes" && <ResumeUploadPanel accessToken={token} onUploaded={() => void refreshWorkspace()} />}{view === "Jobs" && <section className="workspace-panel"><div className="panel-intro"><p className="eyebrow">Role signal</p><h2>Save the requirements before you compare.</h2><p>Paste an authentic job description. The API extracts only explicitly evidenced requirements and keeps its deterministic output attached to your account.</p></div><form className="stack-form" onSubmit={createJob}><label>Role title <input value={jobTitle} onChange={(event) => setJobTitle(event.target.value)} placeholder="Backend Engineer" /></label><label>Company <input value={jobCompany} onChange={(event) => setJobCompany(event.target.value)} placeholder="Company name" /></label><label>Job description <textarea value={jobDescription} onChange={(event) => setJobDescription(event.target.value)} required minLength={30} placeholder="Paste the job description and requirements…" /></label><button className="signal-button" disabled={isBusy}>{isBusy ? "Parsing…" : "Parse & save role"}</button></form><EvidenceList title="Saved roles" items={jobs.map((job) => <div key={job.id}><strong>{job.title}</strong><small>{job.company_name || "Company not detected"}</small><p>{job.parsed.required_skills.length ? `Required: ${job.parsed.required_skills.join(", ")}` : "No supported requirements detected yet."}</p></div>)} /></section>}{view === "Match" && <section className="workspace-panel match-surface"><div className="panel-intro"><p className="eyebrow">Explainable alignment</p><h2>Compare two source records.</h2><p>The score is a deterministic overlap measure with visible matched terms, gap priority, and ATS-style coverage notes. It is not a prediction of hiring outcomes.</p></div><div className="match-controls"><label>Resume<select value={selectedResume} onChange={(event) => setSelectedResume(event.target.value)}><option value="">Choose a resume</option>{resumes.map((resume) => <option key={resume.id} value={resume.id}>{resume.filename}</option>)}</select></label><label>Job description<select value={selectedJob} onChange={(event) => setSelectedJob(event.target.value)}><option value="">Choose a role</option>{jobs.map((job) => <option key={job.id} value={job.id}>{job.title}</option>)}</select></label><button className="signal-button" onClick={runMatch} disabled={isBusy || !selectedResume || !selectedJob}>{isBusy ? "Comparing…" : "Run source-linked match"}</button></div>{analysis && <AnalysisCard analysis={analysis} onPlan={createPlan} onPractice={beginPractice} isBusy={isBusy} />}</section>}{view === "Roadmap" && <section className="workspace-panel"><div className="panel-intro"><p className="eyebrow">Skill gap → proof</p><h2>Turn missing evidence into a sequence.</h2><p>Roadmaps and portfolio prompts follow the prioritized gaps in the last saved match. They are templates to adapt, not AI-generated claims about your readiness.</p></div>{plan ? <PlanCards plan={plan} /> : <div className="empty-evidence"><span>04</span><p>Run a match, then create its roadmap to see skill-specific steps and portfolio prompts here.</p></div>}</section>}{view === "Practice" && <section className="workspace-panel"><div className="panel-intro"><p className="eyebrow">Practice interview</p><h2>Rehearse with the role in view.</h2><p>Question sets use saved job skills. Feedback checks answer structure, stated skill reference, length, and measurable language; it does not claim to judge interview quality.</p></div>{!interview ? <button className="signal-button" onClick={beginPractice} disabled={isBusy}>{isBusy ? "Preparing…" : "Start role-focused practice"}</button> : <InterviewCard interview={interview} answer={answer} setAnswer={setAnswer} onSubmit={saveAnswer} isBusy={isBusy} />}</section>}{view === "Applications" && <section className="workspace-panel"><div className="panel-intro"><p className="eyebrow">Application ledger</p><h2>Keep the follow-through visible.</h2><p>Entries are user-scoped and support saved, applied, screening, interviewing, offer, rejected, and withdrawn stages.</p></div><form className="inline-form" onSubmit={addApplication}><input value={applicationCompany} onChange={(event) => setApplicationCompany(event.target.value)} placeholder="Company" required /><input value={applicationRole} onChange={(event) => setApplicationRole(event.target.value)} placeholder="Role title" required /><button className="signal-button" disabled={isBusy}>Add application</button></form><EvidenceList title="Current ledger" items={applications.map((item) => <div key={item.id} className="application-row"><strong>{item.role_title}</strong><span>{item.company_name}</span><b>{item.status}</b></div>)} /></section>}</main></section>;
}

function Overview({ dashboard, analysis, onJump }: { dashboard: Dashboard | null; analysis: Analysis | null; onJump: (view: View) => void }) { return <><section className="metric-ledger">{[["Resumes", dashboard?.resume_count || 0, "Resumes"], ["Saved roles", dashboard?.job_count || 0, "Jobs"], ["Applications", dashboard?.application_count || 0, "Applications"], ["Practice sessions", dashboard?.interviews_in_progress || 0, "Practice"]].map(([label, value, destination]) => <button key={String(label)} onClick={() => onJump(destination as View)}><span>{label}</span><b>{value}</b><i>→</i></button>)}</section><section className="overview-split"><div className="overview-narrative"><p className="eyebrow">Working principle</p><h2>Every recommendation should point back to a <em>record.</em></h2><p>Start with a resume and a genuine job description. The workspace retains the parsed source, makes scoring criteria visible, and keeps your next steps in one private place.</p><button className="signal-button" onClick={() => onJump("Resumes")}>Add resume evidence</button></div><div className="latest-signal"><p className="eyebrow">Latest alignment</p>{analysis ? <><div className="score-orbit"><b>{Math.round(analysis.match_score)}</b><span>match<br />score</span></div><p>{analysis.missing_skills.length ? `Next evidence to build: ${analysis.missing_skills.slice(0, 3).join(", ")}.` : "No missing supported skills were identified in the last comparison."}</p></> : <p>No match has been run yet. The first comparison will surface source-linked gaps here.</p>}<button className="quiet-button" onClick={() => onJump("Match")}>Review alignment →</button></div></section></> }
function EvidenceList({ title, items }: { title: string; items: ReactNode[] }) { return <div className="evidence-list"><p className="eyebrow">{title}</p>{items.length ? items : <p className="empty-field">Nothing saved yet.</p>}</div> }
function AnalysisCard({ analysis, onPlan, onPractice, isBusy }: { analysis: Analysis; onPlan: () => void; onPractice: () => void; isBusy: boolean }) { return <div className="analysis-card"><div className="score-orbit"><b>{Math.round(analysis.match_score)}</b><span>match<br />score</span></div><div><p className="eyebrow">Score breakdown</p><dl>{Object.entries(analysis.score_breakdown).map(([key, value]) => <div key={key}><dt>{key.replaceAll("_", " ")}</dt><dd>{Math.round(value)}%</dd></div>)}</dl></div><div><p className="eyebrow">Evidence found</p><p>{analysis.matched_skills.join(", ") || "No supported skills matched."}</p><p className="eyebrow">Priority gaps</p><p>{analysis.skill_gaps.map((gap) => `${gap.skill} (${gap.priority})`).join(", ") || "No gap items."}</p></div><div className="analysis-actions"><button className="signal-button" onClick={onPlan} disabled={isBusy}>Build roadmap</button><button className="quiet-button" onClick={onPractice} disabled={isBusy}>Practice role questions</button></div></div> }
function PlanCards({ plan }: { plan: Plan }) { return <div className="plan-grid"><div><p className="eyebrow">Learning sequence</p>{plan.roadmap.map((item) => <article key={item.skill}><span>0{item.sequence}</span><h3>{item.skill}</h3><b>{item.learning_stage} · {item.priority}</b><p>{item.practice_suggestion}</p></article>)}</div><div><p className="eyebrow">Portfolio proof</p>{plan.projects.map((item) => <article key={item.title}><h3>{item.title}</h3><b>{item.difficulty}</b><p>{item.purpose}</p><small>{item.portfolio_value}</small></article>)}</div></div> }
function InterviewCard({ interview, answer, setAnswer, onSubmit, isBusy }: { interview: Interview; answer: string; setAnswer: (value: string) => void; onSubmit: (event: FormEvent<HTMLFormElement>) => void; isBusy: boolean }) { const question = interview.questions[0]; const feedback = interview.responses.find((response) => response.question_index === 0)?.feedback; return <div className="practice-card"><p className="eyebrow">Question 01 / {question.category}</p><h3>{question.prompt}</h3><form className="stack-form" onSubmit={onSubmit}><textarea value={answer} onChange={(event) => setAnswer(event.target.value)} minLength={20} placeholder="Write your response using a truthful example…" required /><button className="signal-button" disabled={isBusy}>{isBusy ? "Checking structure…" : "Save response & view feedback"}</button></form>{feedback && <div className="feedback-card"><b>Structure score: {feedback.score}/100</b><p>{feedback.strengths.join(" ")}</p><p>{feedback.improvements.join(" ")}</p><small>{feedback.disclaimer}</small></div>}</div> }
