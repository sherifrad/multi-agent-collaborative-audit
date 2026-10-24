#!/usr/bin/env node
import { runRelay } from '../../shared_relay.mjs';

runRelay({
  skillName: 'claude-delegate',
  cliBinary: 'claude',
  useStdin: false,
  buildArgs: ({ briefText, readOnly }) =>
    readOnly
      ? ['-p', briefText, '--permission-mode', 'plan']
      : ['-p', briefText, '--permission-mode', 'acceptEdits']
});
