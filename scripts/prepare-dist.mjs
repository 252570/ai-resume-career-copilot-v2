/**
 * Deployment artifact contract:
 * package Next.js standalone output at the root-level `dist/` directory
 * expected by the managed runtime, with static and public files restored.
 */
import { access, cp, mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const repositoryRoot = path.resolve(scriptDirectory, "..");
const frontendDirectory = path.join(repositoryRoot, "frontend");
const nextDirectory = path.join(frontendDirectory, ".next");
const standaloneDirectory = path.join(nextDirectory, "standalone");
const standaloneApplicationDirectory = path.join(standaloneDirectory, "frontend");
const standaloneNodeModulesDirectory = path.join(standaloneDirectory, "node_modules");
const staticDirectory = path.join(nextDirectory, "static");
const publicDirectory = path.join(frontendDirectory, "public");
const distDirectory = path.join(repositoryRoot, "dist");
const deploymentConfigTemplate = path.join(repositoryRoot, "deploy", "project-config.template.json");
const deploymentConfigTargets = [".project-config.json", "project-config.json", "project-config.template.json"];

async function copyIfPresent(source, destination) {
  try {
    await access(source);
    await cp(source, destination, { recursive: true });
  } catch (error) {
    if (error?.code !== "ENOENT") {
      throw error;
    }
  }
}

async function prepareDeploymentArtifact() {
  await access(path.join(standaloneApplicationDirectory, "server.js"));
  await access(standaloneNodeModulesDirectory);
  await rm(distDirectory, { force: true, recursive: true });
  await mkdir(distDirectory, { recursive: true });

  await cp(standaloneApplicationDirectory, distDirectory, { recursive: true });
  await cp(standaloneNodeModulesDirectory, path.join(distDirectory, "node_modules"), { recursive: true });
  await mkdir(path.join(distDirectory, ".next"), { recursive: true });
  await copyIfPresent(staticDirectory, path.join(distDirectory, ".next", "static"));
  await copyIfPresent(publicDirectory, distDirectory);
  await Promise.all(
    deploymentConfigTargets.map((filename) => cp(deploymentConfigTemplate, path.join(distDirectory, filename))),
  );
  await writeFile(
    path.join(distDirectory, "index.js"),
    "// Compatibility entrypoint for managed static runtimes.\nrequire('./server.js');\n",
  );

  console.log("Prepared deployment artifact: dist/server.js, dist/index.js, and managed configuration aliases.");
}

prepareDeploymentArtifact().catch((error) => {
  console.error("Failed to prepare deployment artifact:", error);
  process.exitCode = 1;
});
