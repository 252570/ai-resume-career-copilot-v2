/* Quiet Signal Studio: a concise, calm recovery page matching the primary document aesthetic. */
import Link from "next/link";

export default function NotFound() {
  return (
    <main style={{ alignItems: "center", display: "flex", justifyContent: "center", minHeight: "100vh", padding: "2rem" }}>
      <section style={{ borderTop: "3px solid #df4d34", maxWidth: "34rem", paddingTop: "1.5rem" }}>
        <p style={{ color: "#df4d34", fontSize: ".7rem", fontWeight: 800, letterSpacing: ".14em", textTransform: "uppercase" }}>Route unavailable</p>
        <h1 style={{ fontFamily: "var(--font-display), Georgia, serif", fontSize: "clamp(3rem, 8vw, 5.5rem)", fontWeight: 400, letterSpacing: "-.05em", lineHeight: ".95", margin: "1rem 0" }}>This page is not in the current dossier.</h1>
        <Link href="/" style={{ color: "#142b45", fontSize: ".8rem", fontWeight: 800, letterSpacing: ".1em", textTransform: "uppercase" }}>Return to the foundation →</Link>
      </section>
    </main>
  );
}
