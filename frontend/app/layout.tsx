/*
 * Quiet Signal Studio: editorial minimalism, ink-blue hierarchy, one vermilion
 * signal accent, generous asymmetry, and documentary-style metadata.
 */
import type { Metadata } from "next";
import { DM_Serif_Display, Manrope } from "next/font/google";
import "./globals.css";

const display = DM_Serif_Display({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-display",
});

const sans = Manrope({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "AI Resume & Career Copilot | Evidence-based job preparation",
  description: "Compare resume evidence with real job requirements, identify skill gaps, build a practical roadmap, practice interviews, and track applications in one private workspace.",
  keywords: ["resume matcher", "career copilot", "job search tools", "skill gap analysis", "interview practice"],
  metadataBase: new URL("https://career-copilot-la6y.onrender.com"),
  openGraph: {
    title: "AI Resume & Career Copilot",
    description: "Turn resume evidence and job requirements into clear next steps.",
    url: "https://career-copilot-la6y.onrender.com/",
    siteName: "AI Resume & Career Copilot",
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "AI Resume & Career Copilot",
    description: "Evidence-based resume matching, roadmaps, interview practice, and application tracking.",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${display.variable} ${sans.variable}`}>{children}</body>
    </html>
  );
}
