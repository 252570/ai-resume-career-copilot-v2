/*
 * Quiet Signal Studio: the public entry uses an editorial header and passes
 * into the owner-scoped workspace. Vermilion marks next actions; all methods
 * are labelled as deterministic unless an actual provider is configured.
 */
import { CopilotWorkspace } from "./components/CopilotWorkspace";

export default function Home() {
  return <CopilotWorkspace />;
}
