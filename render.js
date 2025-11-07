#!/usr/bin/env node
import { runSnap } from './snap.js';

const exitCode = await runSnap(process.argv, { scriptName: 'render.js' });
process.exit(exitCode);
