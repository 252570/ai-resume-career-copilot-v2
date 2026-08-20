# AI Resume & Career Copilot — Design Direction

## Three possible approaches

| Theme Name | Very Brief Intro | Probability |
| --- | --- | ---: |
| Quiet Signal Studio | A warm editorial workspace where career progress feels evidence-based and calm rather than algorithmic. The interface uses tactile materials and strong information hierarchy. | 0.07 |
| Precision Terminal | A restrained high-contrast system inspired by aviation instruments and technical manuals, focused on exactness and confident utility. | 0.04 |
| Field Notes Atlas | A career-planning space styled as an annotated personal research journal, with mapped paths and collected evidence. | 0.09 |

## Chosen approach: Quiet Signal Studio

### Design Movement

The interface follows **contemporary editorial minimalism** combined with the material clarity of an architectural practice. It should feel like a well-made career dossier, not a generic AI dashboard.

### Core Principles

1. **Evidence before decoration:** Data, milestones, and decisions use precise hierarchy, captions, and meaningful labels.
2. **Calm asymmetry:** Layouts use an offset reading column, a supporting rail, and generous negative space rather than repeated centered cards.
3. **Tactile intelligence:** Paper-like surfaces, hairline rules, quiet shadows, and restrained material contrasts make the platform approachable.
4. **Progress with accountability:** Directional lines, index labels, and explicit phase markers make it clear what exists now and what is planned later.

### Color Philosophy

Chalk white and warm parchment create a neutral thinking surface. **Ink blue** provides editorial authority and trustworthy contrast, while a single vermilion-orange accent marks agency, forward movement, and important decisions. The accent is reserved for actions, progress markers, and brand direction rather than used as a decorative wash.

### Layout Paradigm

The product uses a **document-and-rail composition**: a broad primary canvas holds the active career work, while a narrow vertical rail carries phase state, architecture cues, and contextual status. On small screens, the rail becomes a compact status block above the document canvas.

### Signature Elements

1. A thin vermilion **career line** that connects status, actions, and milestone cards.
2. Offset **folio labels** such as `01 / FOUNDATION` and compact metadata captions.
3. A geometric **compass-document mark** repeated at meaningful moments, never as generic decoration.

### Interaction Philosophy

Controls should respond like carefully placed drafting tools: clear, compact, and immediate. Interactive elements communicate unavailable future modules directly rather than implying functionality that is not yet implemented.

### Animation

Small transitions use `opacity` and `transform` only, with 160–240ms custom ease-out timing. The career line may subtly draw into view on initial load, while cards lift by 2px on hover. All non-essential movement respects `prefers-reduced-motion`.

### Typography System

**DM Serif Display** is used only for high-value editorial headings to provide a considered, human voice. **Manrope** is the working sans for navigation, metadata, UI controls, and body text. Headings are generous but never oversized; labels use tracked uppercase caps for an archival, documented tone.

### Brand Essence

**AI Resume & Career Copilot turns a candidate’s existing evidence into a practical, explainable route toward a specific role.**

The personality is **methodical, candid, and forward-looking**.

### Brand Voice

Headlines are specific, calm, and action-oriented. CTAs explain the immediate outcome, while microcopy names limits plainly.

> “Turn your existing experience into a clearer next move.”

> “Phase 1 establishes the workspace. Intelligence modules follow in sequence.”

### Wordmark & Logo

The mark is a folded document corner that becomes a compass pointer. The wordmark, where present, uses a tightly set Manrope label paired with an editorial serif product name—not a default-font treatment.

### Signature Brand Color

**Signal Vermilion — `#DF4D34`** is reserved for career direction, important markers, and primary actions.

## Style Decisions

- The folded document/compass mark appears as the primary brand device and as a recurring directional motif, never as a generic app icon.
- Vermilion `#DF4D34` is reserved only for active state, directional movement, primary action, key numerals, and evidence-to-decision connections.
- Imagery is framed as an annotated career dossier with layered papers, structured evidence fragments, route lines, captions, and compass-document geometry rather than generic SaaS illustration.
