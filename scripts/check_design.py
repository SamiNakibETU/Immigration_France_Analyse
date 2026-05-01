import re

from playwright.sync_api import sync_playwright

BAD_SUB_TOKENS = ["Eurostat", "ONS", "INSEE", "Istat", "Statistics", "CNMIGRATRT", "migr_", "Home Office"]
MIN_LABEL_GAP = 16
MIN_EVENT_STROKE = 0.9
MIN_EVENT_OPACITY = 0.72

failures = []
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": 1200, "height": 1000})
    page.goto("http://localhost:8787/", wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(1000)
    data = page.evaluate("""() => [...document.querySelectorAll('article.figure')].map((art, index) => {
      const slug = art.getAttribute('data-export-slug') || `idx-${index}`;
      const sub = art.querySelector('.figure-sub')?.textContent?.trim() || '';
      const paths = [...art.querySelectorAll('.end-label-lines path')];
      const texts = [...art.querySelectorAll('.end-label-texts text')];
      const labelChecks = paths.map((p, i) => {
        const pb = p.getBBox();
        const tb = texts[i]?.getBBox();
        return tb ? {i, gap: tb.x - (pb.x + pb.width), text: texts[i].textContent} : null;
      }).filter(Boolean);
      const callouts = [...art.querySelectorAll('line.ann-callout-line')].map((l) => ({
        strokeWidth: parseFloat(l.getAttribute('stroke-width') || getComputedStyle(l).strokeWidth || '0'),
        opacity: parseFloat(l.getAttribute('opacity') || getComputedStyle(l).opacity || '1'),
      }));
      return {index, slug, sub, labelChecks, callouts};
    })""")
    browser.close()

def sub_has_token(sub: str, token: str) -> bool:
    s = sub.lower()
    t = token.lower()
    if t.endswith("_"):
        return t in s
    return re.search(rf"(?<![A-Za-z]){re.escape(t)}(?![A-Za-z])", s) is not None


for fig in data:
    for token in BAD_SUB_TOKENS:
        if sub_has_token(fig["sub"], token):
            failures.append(f"{fig['slug']}: sous-titre contient source/code '{token}' -> {fig['sub']}")
            break
    for chk in fig['labelChecks']:
        if chk['gap'] < MIN_LABEL_GAP:
            failures.append(f"{fig['slug']}: gap trait-label trop faible ({chk['gap']:.1f}px) pour {chk['text']}")
    for c in fig['callouts']:
        if c['strokeWidth'] < MIN_EVENT_STROKE or c['opacity'] < MIN_EVENT_OPACITY:
            failures.append(f"{fig['slug']}: tiret evenement trop faible stroke={c['strokeWidth']} opacity={c['opacity']}")
            break

if failures:
    print("FAIL")
    for f in failures[:80]:
        print("-", f)
    raise SystemExit(1)
print("PASS")
