#!/usr/bin/env node
import { runRelay } from '../../shared_relay.mjs';

runRelay({
  skillName: 'opencode-delegate',
  cliBinary: 'opencode',
  useStdin: false,
  buildArgs: ({ briefText, readOnly, model }) => {
    const args = ['run'];
    if (readOnly) args.push('--agent', 'plan');
    if (model) args.push('--model', model);
    args.push(briefText);
    return args;
  }
});
