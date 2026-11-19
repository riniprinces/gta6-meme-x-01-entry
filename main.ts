// gta6-meme-x-01 entry: hand POST.json (the X post's address) to the gate.
//
// Node 22, standard library only. The post itself is the entry -- the
// judge reads it from X -- so all this program does is copy POST.json
// from the repository into the output directory, byte for byte. It also
// refuses to copy a file that is not a JSON object naming a url, so a
// broken POST.json fails loudly here instead of at the gate.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const src = join(BOT_DIR, 'POST.json');
const dst = join(OUTPUT_DIR, 'POST.json');

let bytes: Buffer;
try {
  bytes = readFileSync(src);
} catch (err) {
  console.error(`POST.json could not be read from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}

let post: unknown;
try {
  post = JSON.parse(bytes.toString('utf8'));
} catch {
  console.error('POST.json is not valid JSON');
  process.exit(1);
}
if (typeof post !== 'object' || post === null || typeof (post as { url?: unknown }).url !== 'string') {
  console.error('POST.json must be a JSON object with a string url field');
  process.exit(1);
}
if ((post as { url: string }).url.includes('<handle>')) {
  console.error('warning: POST.json still holds the placeholder address; replace it with the real post URL before submitting');
}

mkdirSync(OUTPUT_DIR, { recursive: true });
writeFileSync(dst, bytes);
