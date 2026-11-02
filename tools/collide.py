"""Overlap check for the Payout Timing prototype (DESIGN.md, section 5, item 4).

Measures every visible label, chip, tick and footer item inside the day strips
and lists any pair whose boxes intersect. Runs at 1000, 1100 and 1280px:
the overview at rest, the overview while each payment dot is hovered,
and each payment page at rest.

Text is measured by its rendered glyph boxes (a Range over each text node),
not by its container, so a wide block that holds a short label doesn't count
as an overlap.

Usage:
    pip install playwright && playwright install chromium
    python3 -m http.server 8000 &          # from the repo root
    python3 tools/collide.py http://localhost:8000/

Exit code is 0 when no overlaps are found, 1 otherwise.
"""
import asyncio
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/"
WIDTHS = (1000, 1100, 1280)
TOLERANCE = 1.0  # px; boxes that only touch (or share a line-box edge) are not overlaps
LAUNCH = {}  # e.g. {"executable_path": "/usr/bin/google-chrome"}

# Layers that cross-fade in the same spot by design: only the visible one is measured
# (opacity is checked through all ancestors), so they never collide with each other.

MEASURE = r"""
(rootSel) => {
  const roots = [...document.querySelectorAll(rootSel)].filter(r => r.offsetParent !== null);
  const items = [];
  const shown = el => {
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) < 0.05) return false;
    }
    return true;
  };
  const name = el => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    if (el.classList.length) s += '.' + [...el.classList].slice(0, 2).join('.');
    return s;
  };
  // stacking level inside the strip: z-index of the nearest ancestor that sets one
  const zOf = el => {
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const z = getComputedStyle(n).zIndex;
      if (z !== 'auto') return parseInt(z, 10);
    }
    return 0;
  };
  // does an ancestor (up to its chip) paint an opaque background behind this text?
  const backed = el => {
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const bg = getComputedStyle(n).backgroundColor;
      const m = bg.match(/rgba?\(([^)]+)\)/);
      if (m) { const a = m[1].split(',').map(Number); if (a.length === 3 || a[3] === 1) return true; }
      if (n.classList.contains('oc-chip') || n.classList.contains('pl-b')) break;
    }
    return false;
  };
  const push = (kind, el, r, label) => {
    if (r.width < 1 || r.height < 1) return;
    items.push({kind, el: name(el), label: (label || '').trim().slice(0, 40),
                x: r.left, y: r.top, w: r.width, h: r.height, id: items.length,
                z: zOf(el), backed: kind === 'text' && backed(el)});
  };
  for (const root of roots) {
    // 1. text: tight glyph boxes for every non-empty text node
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let t;
    while ((t = walker.nextNode())) {
      if (!t.textContent.trim()) continue;
      const el = t.parentElement;
      if (!shown(el) || el.closest('.op-tip')) continue;  // a tooltip is measured as one box below
      const range = document.createRange();
      range.selectNodeContents(t);
      for (const r of range.getClientRects()) push('text', el, r, t.textContent);
    }
    // 2. chips, dots and ticks (non-text marks)
    // a container only counts as a mark if something of it is painted
    const painted = el => {
      const cs = getComputedStyle(el);
      return (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || cs.backgroundImage !== 'none' ||
              cs.boxShadow !== 'none' || parseFloat(cs.borderTopWidth) > 0 || parseFloat(cs.borderLeftWidth) > 0);
    };
    root.querySelectorAll('.oc-chip, .pl-b, .pl-pay .pin, .op-dot > i, .op-tip, .run-tick, .op-tick').forEach(el => {
      if (shown(el) && painted(el)) push('mark', el, el.getBoundingClientRect(), el.textContent);
    });
    // reference lines: they may cross marks, but never text (DESIGN.md section 4)
    root.querySelectorAll('.os-line, .dg-dead').forEach(el => {
      if (shown(el)) push('line', el, el.getBoundingClientRect(), '');
    });
  }
  return items;
}
"""


def overlaps(items):
    found = []
    for i, a in enumerate(items):
        for b in items[i + 1:]:
            if a["el"] == b["el"] and a["kind"] == b["kind"] == "text" and abs(a["y"] - b["y"]) < 1:
                continue  # two line-boxes of the same wrapped label
            ix = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
            iy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
            tol = 0 if "line" in (a["kind"], b["kind"]) else TOLERANCE  # a 1px line crossing text counts
            if ix <= tol or iy <= tol:
                continue
            kinds = {a["kind"], b["kind"]}
            if "line" in kinds and "text" not in kinds:
                continue  # a line may pass behind a chip or dot
            if kinds == {"line", "text"}:
                line, txt = (a, b) if a["kind"] == "line" else (b, a)
                if txt["z"] > line["z"] and txt["backed"]:
                    continue  # the line runs behind an opaque chip, so it never shows across the text
            # text sitting inside its own chip is not an overlap
            if kinds == {"text", "mark"}:
                txt, mark = (a, b) if a["kind"] == "text" else (b, a)
                inside = (txt["x"] >= mark["x"] - TOLERANCE and txt["y"] >= mark["y"] - TOLERANCE and
                          txt["x"] + txt["w"] <= mark["x"] + mark["w"] + TOLERANCE and
                          txt["y"] + txt["h"] <= mark["y"] + mark["h"] + TOLERANCE)
                if inside and txt["label"] and txt["label"] in mark["label"]:
                    continue
            found.append((a, b, round(ix, 1), round(iy, 1)))
    return found


def fmt(it):
    return f'{it["el"]} "{it["label"]}"'


async def check(page, state, root_sel, report):
    await page.wait_for_timeout(450)  # let transitions settle
    items = await page.evaluate(MEASURE, root_sel)
    hits = overlaps(items)
    report.append((state, len(items), hits))


async def main():
    report = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(**LAUNCH)
        for w in WIDTHS:
            page = await browser.new_page(viewport={"width": w, "height": 1000})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            await page.goto(URL, wait_until="load")
            await page.wait_for_timeout(600)

            await check(page, f"{w}px overview, at rest", "#moneyBar", report)
            dots = await page.query_selector_all("#moneyBar .op-dot")
            for i in range(len(dots)):
                dots = await page.query_selector_all("#moneyBar .op-dot")
                await dots[i].hover()
                await check(page, f"{w}px overview, payment {i + 1} hovered", "#moneyBar", report)
            await page.mouse.move(0, 0)

            rows = await page.query_selector_all(".pay-row")
            for i in range(len(rows)):
                rows = await page.query_selector_all(".pay-row")
                await rows[i].click()
                await page.wait_for_timeout(700)
                await check(page, f"{w}px payment page {i + 1}, at rest", "#viewDetail .act, #viewDetail .pd-head", report)
                # with a plan applied: every movable payout pulled as early as it goes
                movable = await page.query_selector_all("#viewDetail .act .pl-fund.mv")
                for k in range(len(movable)):
                    movable = await page.query_selector_all("#viewDetail .act .pl-fund.mv")
                    await movable[k].focus()
                    for _ in range(20):
                        await page.keyboard.press("ArrowLeft")
                if movable:
                    await page.wait_for_timeout(500)
                    await check(page, f"{w}px payment page {i + 1}, plan applied", "#viewDetail .act, #viewDetail .pd-head", report)
                    reset = await page.query_selector("#viewDetail .pl-reset")
                    if reset:
                        await reset.click()
                await page.click("#backBtn")
                await page.wait_for_timeout(500)

            if errors:
                report.append((f"{w}px script errors", 0, [({"el": e, "label": "", "kind": ""}, {"el": "", "label": "", "kind": ""}, 0, 0) for e in errors]))
            await page.close()
        await browser.close()

    total = 0
    for state, n, hits in report:
        total += len(hits)
        mark = "ok " if not hits else "!! "
        print(f"{mark}{state}: {n} items measured, {len(hits)} overlaps")
        for a, b, ix, iy in hits:
            print(f"     {fmt(a)}  x  {fmt(b)}  ({ix}×{iy}px)")
    print(f"\n{total} overlap(s) in {len(report)} states")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    asyncio.run(main())
