import fs from "node:fs/promises";
import path from "node:path";

export type JsonObject = Record<string, any>;

const DATA_ROOT = path.resolve(process.cwd(), "..", "combat-wiki", "data");

async function readDirSafe(dir: string): Promise<string[]> {
  try {
    return await fs.readdir(dir);
  } catch {
    return [];
  }
}

export async function loadJsonFile(filePath: string): Promise<JsonObject | null> {
  try {
    const raw = await fs.readFile(filePath, "utf8");
    return JSON.parse(raw) as JsonObject;
  } catch {
    return null;
  }
}

export async function loadCollection(game: string, sectionDir: string): Promise<JsonObject[]> {
  const directory = path.join(DATA_ROOT, game, sectionDir);
  const files = (await readDirSafe(directory))
    .filter((name) => name.endsWith(".json"))
    .filter((name) => name !== "index.json")
    .filter((name) => !path.basename(name).startsWith("_"))
    .sort();

  const rows = await Promise.all(
    files.map((fileName) => loadJsonFile(path.join(directory, fileName))),
  );

  return rows.filter((row): row is JsonObject => row !== null);
}

export async function loadIndexLike(game: string, sectionDir: string): Promise<JsonObject[]> {
  const directory = path.join(DATA_ROOT, game, sectionDir);
  const indexPath = path.join(directory, "index.json");
  const indexData = await loadJsonFile(indexPath);
  if (Array.isArray(indexData)) {
    return indexData as JsonObject[];
  }
  return loadCollection(game, sectionDir);
}

export async function loadDivergentUniverseVersion(version: string): Promise<JsonObject[]> {
  const directory = path.join(
    DATA_ROOT,
    "sr",
    "endgame",
    "divergentuniverse",
    version,
  );
  const files = (await readDirSafe(directory))
    .filter((name) => name.endsWith(".json"))
    .filter((name) => name !== "index.json")
    .filter((name) => !path.basename(name).startsWith("_"))
    .sort();

  const rows = await Promise.all(
    files.map((fileName) => loadJsonFile(path.join(directory, fileName))),
  );

  return rows.filter((row): row is JsonObject => row !== null);
}

export async function listDivergentUniverseVersions(): Promise<string[]> {
  const directory = path.join(DATA_ROOT, "sr", "endgame", "divergentuniverse");
  const entries = await readDirSafe(directory);
  return entries
    .filter((name) => !name.startsWith("."))
    .filter((name) => /^[0-9]+(\.[0-9]+)?$/.test(name))
    .sort((a, b) => Number.parseFloat(a) - Number.parseFloat(b));
}
