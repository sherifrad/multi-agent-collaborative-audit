#!/usr/bin/env node
import { runRelay } from '../../shared_relay.mjs';

runRelay({
  skillName: 'agy-delegate',
  cliBinary: 'agy',
  useStdin: false,
  buildArgs: ({ briefText, readOnly, workDir }) =>
    readOnly
      ? ['--print', briefText, '--add-dir', workDir, '--sandbox']
      : ['--print', briefText, '--add-dir', workDir]
});
