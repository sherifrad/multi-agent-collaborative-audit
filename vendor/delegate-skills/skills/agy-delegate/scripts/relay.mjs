#!/usr/bin/env node
import { runRelay } from '../../shared_relay.mjs';

runRelay({
  skillName: 'agy-delegate',
  cliBinary: 'agy',
  useStdin: false,
  buildArgs: ({ briefText, readOnly, model, workDir }) => {
    // --model before --print: agy reads the token after -p/--print as the prompt (the default model's quota can be exhausted while others still work)
    const args = model ? ['--model', model] : [];
    args.push('--print', briefText, '--add-dir', workDir);
    // owner-approved 2026-10-31: a writing lane auto-accepts edits (narrowest mode; NOT --dangerously-skip-permissions). Scope is still enforced by the pipeline allow-list.
    if (readOnly) args.push('--sandbox'); else args.push('--mode', 'accept-edits');
    return args;
  }
});
