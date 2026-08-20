/*
 * Quiet Signal Studio: a document-and-rail layout that makes the current
 * project phase explicit. Vermilion marks direction; later features are
 * named transparently but never presented as available controls.
 */
import { BrandMark } from "./components/BrandMark";

const modules = [
  {
    index: "01",
    title: "Foundation",
    description: "Standalone frontend and API boundaries, tested health contract, and environment conventions.",
    status: "Active now",
  },
  {
    index: "02",
    title: "Career evidence",
    description: "Resume capture, parsing, and structured experience extraction will be introduced only in later phases.",
    status: "Deferred",
  },
  {
    index: "03",
    title: "Decision support",
    description: "Job alignment, ATS gaps, learning paths, and recommendations will build on verified resume evidence.",
    status: "Deferred",
  },
];

function CompassMark() {
  return <BrandMark />;
}

export default function Home() {
  return (
    <main>
      <header className="site-header">
        <a className="brand" href="#overview" aria-label="AI Resume and Career Copilot home">
          <CompassMark />
          <span>
            <strong>AI Resume</strong>
            <small>Career Copilot</small>
          </span>
        </a>
        <p className="header-status"><span /> Phase 01 / Architecture</p>
      </header>

      <section className="hero" id="overview">
        <div className="hero-copy">
          <p className="eyebrow">A career intelligence platform, assembled deliberately</p>
          <h1>Make your next career move <em>legible.</em></h1>
          <p className="lede">
            AI Resume &amp; Career Copilot will turn resume evidence and job requirements into an explainable path forward. The first layer is now in place.
          </p>
          <div className="hero-note">
            <span className="note-line" />
            <p><strong>Phase 1 complete in scope.</strong> The current workspace contains only the architecture, app shells, configuration boundaries, and starter tests needed to proceed responsibly.</p>
          </div>
          <div className="direction-index" aria-label="Evidence becomes a career decision">
            <span>Source evidence</span><i aria-hidden="true" /><span>Career decision</span>
          </div>
        </div>
        <div className="hero-image" role="img" aria-label="Career planning materials arranged in a quiet studio">
          <div className="dossier-sheet sheet-one" aria-hidden="true"><span>Evidence file</span><b>01</b><i /></div>
          <div className="dossier-sheet sheet-two" aria-hidden="true"><span>Role signal</span><b>→</b><i /></div>
          <div className="compass-stamp" aria-hidden="true"><CompassMark /></div>
          <div className="image-caption"><span>Career evidence</span><span>→</span><span>clear direction</span></div>
        </div>
      </section>

      <section className="content-grid" aria-label="Phase 1 architecture overview">
        <aside className="phase-rail">
          <p className="eyebrow">Project index</p>
          <div className="rail-line" aria-hidden="true"><span /></div>
          <div className="phase-number">01</div>
          <h2>Foundation<br />established.</h2>
          <p>Two independently runnable applications, one clean system boundary.</p>
          <dl>
            <div><dt>Web</dt><dd>Next.js / TypeScript</dd></div>
            <div><dt>API</dt><dd>FastAPI / Pydantic</dd></div>
            <div><dt>Data</dt><dd>PostgreSQL in Phase 2</dd></div>
          </dl>
        </aside>

        <div className="modules">
          <div className="section-heading">
            <div>
              <p className="eyebrow">System map</p>
              <h2>Each capability begins with a clear boundary.</h2>
            </div>
            <p className="section-caption">No future feature is represented as currently available.</p>
          </div>

          <div className="module-list">
            {modules.map((module) => (
              <article className={`module ${module.index === "01" ? "current" : ""}`} key={module.index}>
                <span className="module-index">{module.index}</span>
                <div>
                  <h3>{module.title}</h3>
                  <p>{module.description}</p>
                </div>
                <span className="module-status">{module.status}</span>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="architecture-strip">
        <div className="architecture-copy">
          <p className="eyebrow">The operating principle</p>
          <h2>Good career advice must be <em>traceable</em> to real evidence.</h2>
          <p>Future analyses will keep the path from source resume and job criteria to match score, gap, and recommendation visible by design.</p>
          <div className="strip-direction"><span>Resume fragments</span><i aria-hidden="true" /><span>Accountable next step</span></div>
        </div>
        <div className="signal-image" role="img" aria-label="Abstract skill mapping materials arranged as a career dossier">
          <span className="signal-label top">Experience</span><span className="signal-label bottom">Skill proof</span><span className="signal-route" aria-hidden="true" />
        </div>
      </section>

      <footer>
        <div className="footer-brand"><CompassMark /><span>AI Resume &amp; Career Copilot</span></div>
        <p>Phase 1 — architecture &amp; setup only</p>
      </footer>
    </main>
  );
}
