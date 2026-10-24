#!/usr/bin/env node
/**
 * ============================================================================
 * Vendored Delegate-Skills Universal Relay Core (delegate-relay.result.v1)
 * Based on https://github.com/amElnagdy/delegate-skills
 * Node built-ins only. Zero external npm dependencies. Never commits.
 * ============================================================================
 */

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

export function runRelay(config) {
  const args = process.argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`Usage: node relay.mjs --brief <file|text> --cd <repo_dir> [--read-only] [--model <id>] [--out-dir <dir>] [--self-test]`);
    process.exit(0);
  }

  if (args.includes('--self-test')) {
    const sample = {
      schema: 'delegate-relay.result.v1',
      skill: config.skillName,
      cli: config.cliBinary,
      selfTestStatus: 'PASS',
      readOnlySupported: true,
      neverCommits: true
    };
    console.log(JSON.stringify(sample, null, 2));
    process.exit(0);
  }

  const getArg = (flag) => {
    const idx = args.indexOf(flag);
    return idx !== -1 && idx + 1 < args.length ? args[idx + 1] : null;
  };

  const briefArg = getArg('--brief');
  const cdArg = getArg('--cd') || process.cwd();
  const modelArg = getArg('--model') || config.defaultModel || '';
  const outDirArg = getArg('--out-dir') || path.join(cdArg, '.agents', 'relay-runs', config.skillName);
  const readOnly = args.includes('--read-only');

  if (!briefArg) {
    console.error(JSON.stringify({
      status: 'MACA_SCRIPT_ERROR — STOP_AND_FIX',
      error_code: 'MISSING_BRIEF',
      skill: config.skillName,
      message: 'Missing required --brief <path_or_text> argument.',
      remediation: 'Pass --brief <path_to_brief.md> and --cd <target_repo_dir>.'
    }, null, 2));
    process.exit(2);
  }

  const workDir = path.resolve(cdArg);
  if (!fs.existsSync(workDir)) {
    console.error(JSON.stringify({
      status: 'MACA_SCRIPT_ERROR — STOP_AND_FIX',
      error_code: 'INVALID_WORKDIR',
      skill: config.skillName,
      message: `Target repository directory does not exist: ${workDir}`,
      remediation: 'Provide a valid existing directory path to --cd.'
    }, null, 2));
    process.exit(2);
  }

  const briefText = fs.existsSync(path.resolve(briefArg))
    ? fs.readFileSync(path.resolve(briefArg), 'utf8')
    : briefArg;

  const envPath = `${process.env.PATH || ''}:/opt/homebrew/bin:/usr/local/bin`;
  const whichRes = spawnSync('which', [config.cliBinary], { env: { ...process.env, PATH: envPath }, encoding: 'utf8' });
  const cliPath = whichRes.status === 0 ? whichRes.stdout.trim() : null;

  const getGitStatusFiles = () => {
    const gitRes = spawnSync('git', ['-C', workDir, 'status', '--porcelain'], { env: { ...process.env, PATH: envPath }, encoding: 'utf8' });
    if (gitRes.status !== 0) return [];
    return gitRes.stdout
      .split('\n')
      .map((l) => l.trim())
      .filter(Boolean)
      .map((l) => l.slice(3).trim());
  };

  const beforeFiles = new Set(getGitStatusFiles());

  fs.mkdirSync(outDirArg, { recursive: true });
  const resultPath = path.join(outDirArg, 'result.json');

  if (!cliPath) {
    const unavailableResult = {
      schema: 'delegate-relay.result.v1',
      skill: config.skillName,
      cli: config.cliBinary,
      status: `${config.cliBinary}_unavailable`,
      exitCode: 127,
      readOnly,
      readOnlyViolation: false,
      touchedFiles: [],
      finalMessage: `CLI '${config.cliBinary}' is not installed in PATH. Cascade to next available tier.`,
      timestamp: new Date().toISOString()
    };
    fs.writeFileSync(resultPath, JSON.stringify(unavailableResult, null, 2), 'utf8');
    console.log(JSON.stringify(unavailableResult, null, 2));
    process.exit(127);
  }

  const cliArgs = config.buildArgs({ briefText, readOnly, model: modelArg, workDir });
  const runRes = spawnSync(cliPath, cliArgs, {
    cwd: workDir,
    env: { ...process.env, PATH: envPath },
    input: config.useStdin ? briefText : undefined,
    encoding: 'utf8',
    timeout: 300000
  });

  const afterFiles = getGitStatusFiles();
  const touchedFiles = afterFiles.filter((f) => !beforeFiles.has(f));
  const readOnlyViolation = readOnly && touchedFiles.length > 0;

  const result = {
    schema: 'delegate-relay.result.v1',
    skill: config.skillName,
    cli: config.cliBinary,
    status: runRes.status === 0 && !readOnlyViolation ? 'completed' : 'failed',
    exitCode: runRes.status ?? 1,
    signal: runRes.signal || null,
    readOnly,
    readOnlyViolation,
    touchedFiles,
    finalMessage: (runRes.stdout || '').trim().slice(-4000),
    stderrTail: (runRes.stderr || '').trim().slice(-1000),
    resultPath,
    timestamp: new Date().toISOString()
  };

  fs.writeFileSync(resultPath, JSON.stringify(result, null, 2), 'utf8');
  console.log(JSON.stringify(result, null, 2));
  process.exit(result.status === 'completed' ? 0 : (result.exitCode || 1));
}
