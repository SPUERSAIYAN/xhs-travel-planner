#!/usr/bin/env node

import { existsSync } from "node:fs";
import { cp, mkdir, rm } from "node:fs/promises";
import { homedir } from "node:os";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const skillName = "xhs-travel-planner";
const packageRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const skillEntries = ["SKILL.md", "agents", "assets", "references", "scripts"];

function includeInSkill(source) {
  return basename(source) !== "__pycache__" && !source.endsWith(".pyc");
}

function printHelp() {
  console.log(`xhs-travel-planner

Install the xhs-travel-planner Codex skill.

Usage:
  npx xhs-travel-planner install [--dest <skills-dir>] [--force]
  npx --package=github:SPUERSAIYAN/xhs-travel-planner xhs-travel-planner install [--dest <skills-dir>]

Options:
  --dest <dir>  Skills parent directory. Default: $CODEX_HOME/skills or ~/.codex/skills
  --force       Replace an existing xhs-travel-planner directory
  --help        Show this help

After installation, restart Codex to pick up new skills.`);
}

function parseArgs(args) {
  const result = { command: "install", dest: null, force: false, help: false };
  const input = [...args];
  if (input[0] && !input[0].startsWith("-")) {
    result.command = input.shift();
  }
  while (input.length) {
    const arg = input.shift();
    if (arg === "--help" || arg === "-h") {
      result.help = true;
    } else if (arg === "--force") {
      result.force = true;
    } else if (arg === "--dest") {
      if (!input.length) throw new Error("--dest requires a directory path");
      result.dest = input.shift();
    } else {
      throw new Error(`Unknown option: ${arg}`);
    }
  }
  return result;
}

function skillsDirectory(customDest) {
  if (customDest) return resolve(customDest);
  const codexHome = process.env.CODEX_HOME
    ? resolve(process.env.CODEX_HOME)
    : join(homedir(), ".codex");
  return join(codexHome, "skills");
}

async function install(options) {
  const skillsDir = skillsDirectory(options.dest);
  const destination = join(skillsDir, skillName);

  if (existsSync(destination)) {
    if (!options.force) {
      throw new Error(
        `Skill already exists at ${destination}. Re-run with --force to replace it.`
      );
    }
    await rm(destination, { recursive: true, force: true });
  }

  await mkdir(destination, { recursive: true });
  for (const entry of skillEntries) {
    await cp(join(packageRoot, entry), join(destination, basename(entry)), {
      recursive: true,
      filter: includeInSkill,
    });
  }

  console.log(`Installed ${skillName} to ${destination}`);
  console.log("Restart Codex to pick up new skills.");
}

async function main() {
  let options;
  try {
    options = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(`Error: ${error.message}`);
    printHelp();
    process.exitCode = 1;
    return;
  }

  if (options.help) {
    printHelp();
    return;
  }
  if (options.command !== "install") {
    console.error(`Error: unsupported command "${options.command}"`);
    printHelp();
    process.exitCode = 1;
    return;
  }

  try {
    await install(options);
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exitCode = 1;
  }
}

await main();
