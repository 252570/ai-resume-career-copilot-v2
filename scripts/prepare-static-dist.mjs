import { cp, mkdir, rm } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const repositoryRoot = path.resolve(scriptDirectory, "..");
const frontendOutput = path.join(repositoryRoot, "frontend", "out");
const distDirectory = path.join(repositoryRoot, "dist");
const publicDirectory = path.join(distDirectory, "public");

await rm(distDirectory, { force: true, recursive: true });
await mkdir(publicDirectory, { recursive: true });
await cp(frontendOutput, publicDirectory, { recursive: true });
console.log("Prepared managed static artifact at dist/public.");
