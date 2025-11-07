#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import puppeteer from 'puppeteer';

process.env.PUPPETEER_DISABLE_CRASHPAD = 'true';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const userDataDir = path.resolve(__dirname, '.puppeteer-user');

async function resolveInputPath(input) {
    const inputIsUrl = /^https?:\/\//i.test(input);
    if (inputIsUrl) {
        return { inputIsUrl, inputFilePath: null, triedPaths: [] };
    }

    const triedPaths = [];

    if (path.isAbsolute(input)) {
        triedPaths.push(input);
    } else {
        triedPaths.push(
            path.resolve(process.cwd(), input),
            path.resolve(__dirname, input)
        );

        if (process.env.HOME) {
            triedPaths.push(path.resolve(process.env.HOME, 'Desktop', input));
        }
    }

    for (const candidate of triedPaths) {
        try {
            await fs.access(candidate);
            return { inputIsUrl, inputFilePath: candidate, triedPaths };
        } catch {
            // try next candidate
        }
    }

    return { inputIsUrl, inputFilePath: null, triedPaths };
}

export async function convertHtml({
    input,
    output,
    viewport = { width: 1200, height: 1600 },
    delayMs,
    fullPage = true
} = {}) {
    if (!input) {
        throw new Error('No input provided.');
    }

    await fs.mkdir(userDataDir, { recursive: true });

    const { inputIsUrl, inputFilePath, triedPaths } = await resolveInputPath(input);

    if (!inputIsUrl && !inputFilePath) {
        const details = triedPaths.map((candidate) => `  - ${candidate}`).join('\n');
        const error = new Error(`Input file not found.\nChecked paths:\n${details}`);
        error.code = 'INPUT_NOT_FOUND';
        throw error;
    }

    const defaultOutputDir = path.resolve(process.env.HOME ?? __dirname, 'Desktop', 'Donepng');
    const defaultOutputName = inputIsUrl
        ? `webpage-${Date.now()}.png`
        : `${path.basename(inputFilePath, path.extname(inputFilePath) || '.html')}.png`;
    const outputArg = output ?? path.join(defaultOutputDir, defaultOutputName);
    const outputPath = path.isAbsolute(outputArg)
        ? outputArg
        : path.resolve(process.cwd(), outputArg);

    await fs.mkdir(path.dirname(outputPath), { recursive: true });

    const effectiveDelay = typeof delayMs === 'number' && !Number.isNaN(delayMs)
        ? delayMs
        : Number.parseInt(process.env.SNAP_DELAY_MS ?? '', 10);
    const resolvedDelay = Number.isFinite(effectiveDelay) ? Math.max(0, effectiveDelay) : 500;

    const browser = await puppeteer.launch({
        headless: 'shell',
        defaultViewport: viewport,
        userDataDir,
        dumpio: true,
        ignoreDefaultArgs: ['--enable-crashpad'],
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--no-crashpad',
            '--disable-crash-reporter',
            '--disable-breakpad'
        ]
    });

    try {
        const page = await browser.newPage();

        const gotoOptions = { waitUntil: 'domcontentloaded', timeout: 60000 };

        if (inputIsUrl) {
            await page.goto(input, gotoOptions);
        } else {
            const htmlUrl = pathToFileURL(inputFilePath).href;
            await page.goto(htmlUrl, gotoOptions);
        }

        if (resolvedDelay > 0) {
            await new Promise((resolve) => setTimeout(resolve, resolvedDelay));
        }

        const lowerOutput = outputPath.toLowerCase();
        const screenshotType = lowerOutput.endsWith('.jpg') || lowerOutput.endsWith('.jpeg')
            ? 'jpeg'
            : 'png';

        await page.screenshot({
            path: outputPath,
            type: screenshotType,
            fullPage
        });

        return { outputPath, screenshotType };
    } finally {
        await browser.close();
    }
}

function parseArgs(argv) {
    const args = argv.slice(2);
    const parsed = {
        input: null,
        output: null,
        width: 1200,
        height: 1600,
        delay: null,
        fullPage: true,
        help: false,
        jpeg: false
    };

    for (let i = 0; i < args.length; i++) {
        const arg = args[i];

        if (arg === '-h' || arg === '--help') {
            parsed.help = true;
        } else if (arg === '-o' || arg === '--output') {
            parsed.output = args[++i];
        } else if (arg === '-w' || arg === '--width') {
            parsed.width = parseInt(args[++i], 10);
        } else if (arg === '-H' || arg === '--height') {
            parsed.height = parseInt(args[++i], 10);
        } else if (arg === '-d' || arg === '--delay') {
            parsed.delay = parseInt(args[++i], 10);
        } else if (arg === '--no-full-page') {
            parsed.fullPage = false;
        } else if (arg === '--jpeg' || arg === '--jpg') {
            parsed.jpeg = true;
        } else if (!arg.startsWith('-')) {
            if (!parsed.input) {
                parsed.input = arg;
            } else if (!parsed.output) {
                parsed.output = arg;
            }
        }
    }

    return parsed;
}

function printHelp(scriptName) {
    console.log(`
HTML to PNG/JPEG Screenshot Tool

USAGE:
  node ${scriptName} <input> [options]
  npm run snap -- <input> [options]

ARGUMENTS:
  <input>              HTML file path or URL to screenshot

OPTIONS:
  -o, --output <path>  Output file path (default: ~/Desktop/Donepng/<name>.png)
  -w, --width <px>     Viewport width in pixels (default: 1200)
  -H, --height <px>    Viewport height in pixels (default: 1600)
  -d, --delay <ms>     Delay before screenshot in milliseconds (default: 500)
  --no-full-page       Capture viewport only (not full page)
  --jpeg, --jpg        Save as JPEG instead of PNG
  -h, --help           Show this help message

EXAMPLES:
  # Screenshot a local HTML file
  node ${scriptName} index.html

  # Screenshot a URL
  node ${scriptName} https://example.com

  # Custom output location
  node ${scriptName} index.html -o screenshots/result.png

  # Custom viewport size with delay
  node ${scriptName} page.html -w 800 -H 600 -d 1000

  # JPEG format with no full page
  node ${scriptName} index.html --jpeg --no-full-page

  # Using npm script
  npm run snap -- index.html -o result.png
`);
}

export async function runSnap(argv = process.argv, options = {}) {
    const scriptName = options.scriptName ?? path.basename(argv[1] ?? 'snap.js');
    const args = parseArgs(argv);

    if (args.help) {
        printHelp(scriptName);
        return 0;
    }

    if (!args.input) {
        if (!options.quiet) {
            console.error('Error: No input provided.\n');
            printHelp(scriptName);
        }
        return 1;
    }

    // Auto-add extension if output specified without one
    let outputPath = args.output;
    if (outputPath && !outputPath.match(/\.(png|jpe?g)$/i)) {
        outputPath += args.jpeg ? '.jpg' : '.png';
    }

    try {
        const { outputPath: finalPath, screenshotType } = await convertHtml({
            input: args.input,
            output: outputPath,
            viewport: { width: args.width, height: args.height },
            delayMs: args.delay,
            fullPage: args.fullPage
        });

        if (!options.quiet) {
            console.log(`✓ Screenshot saved: ${finalPath}`);
            console.log(`  Type: ${screenshotType.toUpperCase()}`);
            console.log(`  Viewport: ${args.width}x${args.height}`);
            console.log(`  Full page: ${args.fullPage ? 'Yes' : 'No'}`);
        }

        return 0;
    } catch (error) {
        if (!options.quiet) {
            console.error(`✗ Error: ${error.message ?? error}`);
            if (error.code === 'INPUT_NOT_FOUND') {
                console.error('\nTip: Make sure the file path is correct or provide a full URL.');
            }
        }
        return error.code === 'INPUT_NOT_FOUND' ? 2 : 1;
    }
}

const executedDirectly = import.meta.url === pathToFileURL(process.argv[1] ?? '').href;

if (executedDirectly) {
    const exitCode = await runSnap(process.argv);
    process.exit(exitCode);
}
