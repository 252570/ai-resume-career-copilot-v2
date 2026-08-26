"use client";

/**
 * Quiet Signal Studio release note: a public paper-and-rail document using
 * existing ink-blue structure and vermilion only for verified evidence.
 */
import { BrandMark } from "./BrandMark";

type ReleaseUpdatePanelProps = {
  onBack: () => void;
  onStart: () => void;
};

const releaseItems = [
  ["01", "Secure sessions", "Browser sign-in now uses an HttpOnly, Secure, SameSite=Lax session cookie. Existing bearer API access remains compatible, while the browser avoids persisting tokens in local or session storage."],
  ["02", "Reviewable evidence", "Parsed resume evidence can be corrected before it is used, and saved resume versions remain visible to the account owner."],
  ["03", "Progress that persists", "Roadmap completion is stored per account. Duplicate jobs are protected, skills are normalized conservatively, and interview practice moves through a complete question set."],
];

const checks = [
  ["Build integrity", "Frontend type checking and static production build completed.", "Passed"],
  ["Backend regression", "73 backend tests completed successfully.", "Passed"],
  ["Browser session", "Public sign-in, protected workspace load, account controls, and sign-out were verified.", "Passed"],
  ["Public endpoints", "Frontend, readiness, robots, sitemap, protected export, and credentialed CORS were checked.", "Passed"],
];

export function ReleaseUpdatePanel({ onBack, onStart }: ReleaseUpdatePanelProps) {
  return <section className="release-update" aria-label="Product release update">
    <header className="release-header">
      <button className="brand release-brand" onClick={onBack} aria-label="Return to account access"><BrandMark /><span><strong>AI Resume</strong><small>Career Copilot</small></span></button>
      <div><span className="release-status"><i /> Release verified</span><button className="release-back" onClick={onBack}>Back to account access</button></div>
    </header>

    <main className="release-main">
      <section className="release-hero">
        <div className="release-copy">
          <p className="eyebrow">Product update / 2026</p>
          <h1>Release verified.<br /><em>Evidence attached.</em></h1>
          <p>A stronger private career workspace, checked from public sign-in through protected account actions. This note summarizes what is live without exposing any private setup details.</p>
          <div className="release-actions"><button className="signal-button" onClick={onStart}>Create or sign in</button><button className="release-text-link" onClick={() => document.getElementById("release-validation")?.scrollIntoView({ behavior: "smooth" })}>Read validation <span>→</span></button></div>
        </div>
        <div className="release-dossier" aria-hidden="true"><div className="dossier-tab">PUBLIC<br />NOTE</div><span>Release</span><b>02</b><i /><small>Build · validate · publish</small><div className="dossier-check">✓</div></div>
      </section>

      <section className="release-metrics" aria-label="Release verification summary">
        <div><b>73</b><span>backend tests passed</span></div><div><b>200</b><span>public readiness returned</span></div><div><b>401</b><span>unauthenticated export rejected</span></div><div><b>1h</b><span>secure cookie lifetime</span></div>
      </section>

      <section className="release-content" id="release-shipped">
        <aside className="release-rail"><p className="eyebrow">What shipped</p><span>01</span><i /><p>Focused upgrades to privacy, evidence quality, and follow-through.</p></aside>
        <div className="release-list"><div className="release-heading"><p className="eyebrow">Owner-scoped by design</p><h2>Three changes, <em>made accountable.</em></h2></div>{releaseItems.map(([number, title, copy]) => <article key={number}><span>{number}</span><div><h3>{title}</h3><p>{copy}</p></div><b>Verified</b></article>)}</div>
      </section>

      <section className="release-validation" id="release-validation">
        <div className="release-validation-title"><p className="eyebrow">Validation ledger</p><h2>Checked across<br />the <em>whole path.</em></h2><p>These are final production checks, not promises about future provider availability or configuration changes.</p></div>
        <div className="release-checks"><div className="release-check-head"><span>Check</span><span>Observation</span><span>Result</span></div>{checks.map(([name, observation, result]) => <div className="release-check-row" key={name}><strong>{name}</strong><p>{observation}</p><b>✓ {result}</b></div>)}</div>
      </section>

      <section className="release-scope">
        <div><p className="eyebrow">Scope note</p><h2>What remains<br /><em>outside</em> this release.</h2></div>
        <div className="release-scope-list"><article><span>01</span><h3>Custom domain</h3><p>Needs a purchased domain and DNS access before it can be connected.</p></article><article><span>02</span><h3>Email workflows</h3><p>Password reset and verification need a transactional email provider and verified sender.</p></article><article><span>03</span><h3>Hosting note</h3><p>Free-tier hosting may cold-start after inactivity; routine secret rotation remains recommended.</p></article></div>
      </section>

      <section className="release-close"><p className="eyebrow">Ready to inspect</p><h2>Private workspace.<br /><em>Visible evidence.</em></h2><p>Start with your own resume and a genuine job description to see source-linked next steps.</p><button className="signal-button" onClick={onStart}>Open Career Copilot</button></section>
    </main>
  </section>;
}
