import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Entrypoint: hand the rendered broadsheet to the grader, byte for byte.
// The art lives in entry.png next to this file; the grader reads it from
// the output directory (MAKEFUN_OUTPUT_DIR, or /output by default).
const root = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(join(root, "entry.png"), join(outDir, "entry.png"));
