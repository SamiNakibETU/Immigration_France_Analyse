/**
 * Copie le dossier site/ vers .vercel-output/ pour déploiement Vercel (site statique).
 */
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const src = path.join(root, "site");
const out = path.join(root, ".vercel-output");

if (!fs.existsSync(path.join(src, "index.html"))) {
  console.error("Absence de site/index.html");
  process.exit(1);
}

fs.rmSync(out, { recursive: true, force: true });
fs.cpSync(src, out, { recursive: true });
console.log("Copié site/ -> .vercel-output/");
