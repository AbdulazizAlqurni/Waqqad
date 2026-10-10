// PNG and MP4 exports of the final symbol.
//   node export.js        (needs Playwright with Chromium, and ffmpeg on PATH)
// Reads final/symbol/*.svg, writes final/symbol/png/ and final/symbol/video/.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const DIR = path.join(__dirname, "final", "symbol");
const read = f => fs.readFileSync(path.join(DIR, f), "utf8");

const PNGS = [
  ["waqqad-app-icon.svg", "png/waqqad-app-icon-1024.png", 1024],
  ["waqqad-app-icon.svg", "png/waqqad-app-icon-512.png", 512],
  ["waqqad-app-icon.svg", "png/waqqad-app-icon-180.png", 180],
  ["waqqad-app-icon.svg", "png/favicon-32.png", 32],
  ["waqqad-app-icon.svg", "png/favicon-16.png", 16],
  ["waqqad-symbol.svg", "png/waqqad-symbol-1024.png", 1024],
  ["waqqad-symbol-on-dark.svg", "png/waqqad-symbol-on-dark-1024.png", 1024],
];

(async () => {
  const browser = await chromium.launch();
  fs.mkdirSync(path.join(DIR, "png"), { recursive: true });
  fs.mkdirSync(path.join(DIR, "video"), { recursive: true });

  for (const [src, out, px] of PNGS) {
    const page = await browser.newPage({ viewport: { width: px, height: px } });
    const svg = read(src).replace(/width="[^"]*" height="[^"]*"/, `width="${px}" height="${px}" preserveAspectRatio="xMidYMid meet"`);
    await page.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    await page.screenshot({ path: path.join(DIR, out), omitBackground: true, clip: { x: 0, y: 0, width: px, height: px } });
    await page.close();
  }

  // the intro, frame by frame at 30 fps: SMIL time is set exactly, so no dropped frames
  const W = 1920, H = 1080, FPS = 30, SECONDS = 5.5;
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  const intro = read("motion/waqqad-symbol-intro-navy.svg").replace(/width="[^"]*" height="[^"]*"/, 'width="760" height="760"');
  await page.setContent(`<html><body style="margin:0;background:#0B1F3A;display:grid;place-items:center;width:${W}px;height:${H}px;overflow:hidden">${intro}</body></html>`);
  const tmp = fs.mkdtempSync(path.join(require("os").tmpdir(), "wq-frames-"));
  await page.evaluate(() => document.querySelector("svg").pauseAnimations());
  const total = Math.round(FPS * SECONDS);
  for (let i = 0; i < total; i++) {
    await page.evaluate(t => document.querySelector("svg").setCurrentTime(t), Math.min(i / FPS, 5));
    await page.screenshot({ path: path.join(tmp, `f${String(i).padStart(4, "0")}.png`) });
  }
  await browser.close();
  execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-framerate", String(FPS), "-i", path.join(tmp, "f%04d.png"),
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-movflags", "+faststart",
    path.join(DIR, "video", "waqqad-symbol-intro-1080p.mp4")]);
  // WebM copy for browsers without H.264
  execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-i", path.join(DIR, "video", "waqqad-symbol-intro-1080p.mp4"),
    "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "30", "-row-mt", "1", path.join(DIR, "video", "waqqad-symbol-intro-1080p.webm")]);
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log("exported", PNGS.length, "PNGs and the 1080p intro");
})();
