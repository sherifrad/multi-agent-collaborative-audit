#!/usr/bin/env node
import { runRelay } from '../../shared_relay.mjs';

runRelay({
  skillName: 'codex-delegate',
  cliBinary: 'codex',
  useStdin: false,
  buildArgs: ({ briefText, readOnly }) =>
    readOnly
      ? ['exec', '--sandbox', 'read-only', briefText]
      : ['exec', '--sandbox', 'workspace-write', briefText]
});
