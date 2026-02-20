#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

let babelCore = null;
let templateLiteralPlugin = null;
try {
  babelCore = await import("@babel/core");
  templateLiteralPlugin = await import("@babel/plugin-transform-template-literals");
} catch {
  console.warn("[compat-transpile] babel template-literal plugin not installed; skipping JS transpile.");
  process.exit(0);
}

function parseArgs(argv) {
  let webRoot = "./web";
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === "--web" && i + 1 < argv.length) {
      webRoot = argv[i + 1];
      i += 1;
    }
  }
  return { webRoot: path.resolve(webRoot) };
}

async function walk(dir) {
  const out = [];
  const items = await fs.readdir(dir, { withFileTypes: true });
  for (const item of items) {
    const full = path.join(dir, item.name);
    if (item.isDirectory()) {
      out.push(...(await walk(full)));
      continue;
    }
    out.push(full);
  }
  return out;
}

function shouldTranspile(filePath, webRoot) {
  const rel = path.relative(webRoot, filePath).replaceAll(path.sep, "/");
  if (rel.startsWith("javascripts/") && rel.endsWith(".js")) return true;
  if (rel === "data/New.js") return true;
  return false;
}

async function main() {
  const { webRoot } = parseArgs(process.argv);
  const stat = await fs.stat(webRoot).catch(() => null);
  if (!stat || !stat.isDirectory()) {
    throw new Error(`web root not found: ${webRoot}`);
  }

  const files = await walk(webRoot);
  let transpiled = 0;
  for (const file of files) {
    if (!shouldTranspile(file, webRoot)) continue;
    const code = await fs.readFile(file, "utf8");
    if (!code.includes("`")) continue;
    const result = babelCore.transformSync(code, {
      filename: file,
      configFile: false,
      babelrc: false,
      comments: true,
      compact: false,
      plugins: [templateLiteralPlugin.default],
    });
    if (!result || typeof result.code !== "string") continue;
    await fs.writeFile(file, result.code, "utf8");
    transpiled += 1;
  }
  console.log(`[compat-transpile] transpiled ${transpiled} file(s) for ES5/WebKit compatibility.`);
}

main().catch((err) => {
  console.error(`[compat-transpile] failed: ${String(err)}`);
  process.exit(1);
});
