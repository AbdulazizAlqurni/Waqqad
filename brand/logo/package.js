// PNGs and the guidelines PDF for brand/waqqad-logo/.
//   python3 package.py && node package.js     (Playwright with Chromium)
// Every SVG in svg/ becomes a PNG in png/ (lockups 2400 px wide, the symbol and
// the name 1024 px wide), the app icon and favicons go to icons/png/, and
// guidelines.html is printed to waqqad-logo-guidelines.pdf.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const PKG = path.join(__dirname, "..", "waqqad-logo");

function svgSize(svg) {
  const m = svg.match(/viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"/);
  return { w: +m[3], h: +m[4] };
}

async function rasterise(browser, svg, out, width, height) {
  const { w, h } = svgSize(svg);
  const W = width || Math.round(height * w / h), H = height || Math.round(width * h / w);
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  const sized = svg.replace(/^(<svg[^>]*?) width="[^"]*" height="[^"]*"/, `$1 width="${W}" height="${H}"`);
  await page.setContent(`<html><body style="margin:0;background:transparent">${sized}</body></html>`);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  await page.screenshot({ path: out, omitBackground: true, clip: { x: 0, y: 0, width: W, height: H } });
  await page.close();
}

(async () => {
  const browser = await chromium.launch();
  let count = 0;
  for (const group of ["stacked", "horizontal", "symbol", "name"]) {
    const dir = path.join(PKG, "svg", group);
    for (const fn of fs.readdirSync(dir).filter(f => f.endsWith(".svg"))) {
      const svg = fs.readFileSync(path.join(dir, fn), "utf8");
      const width = group === "stacked" || group === "horizontal" ? 2400 : 1024;
      await rasterise(browser, svg, path.join(PKG, "png", group, fn.replace(/\.svg$/, ".png")), width);
      count++;
    }
  }
  const icon = fs.readFileSync(path.join(PKG, "icons", "waqqad-app-icon.svg"), "utf8");
  for (const [name, px] of [["waqqad-app-icon-1024", 1024], ["waqqad-app-icon-512", 512], ["waqqad-app-icon-180", 180],
                            ["favicon-48", 48], ["favicon-32", 32], ["favicon-16", 16]]) {
    await rasterise(browser, icon, path.join(PKG, "icons", "png", name + ".png"), px, px);
    count++;
  }

  const page = await browser.newPage();
  await page.goto("file://" + path.join(__dirname, "guidelines.html"), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);
  await page.pdf({ path: path.join(PKG, "waqqad-logo-guidelines.pdf"), width: "297mm", height: "210mm", printBackground: true, preferCSSPageSize: true });
  await browser.close();
  console.log(`exported ${count} PNGs and the guidelines PDF`);
})();
