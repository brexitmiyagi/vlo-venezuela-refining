"""Compare each version of Treasury's Venezuela general licences 46, 50 and 52 with the one before.

Downloads the Federal Register text of each notice (federalregister.gov API), cuts out each licence,
and prints a word-level diff. The current versions (46E, 50C, 52C) are on OFAC's site as PDFs:
https://ofac.treasury.gov/sanctions-programs-and-country-information/venezuela-related-sanctions
My reading of every change is in data/ofac_licence_history.csv.
"""
import re, json, difflib, urllib.request

DOCS = ["2026-09092", "2026-09090", "2026-18572", "2026-20006", "2026-20008", "2026-20009"]
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode()
texts = {}
for d in DOCS:
    meta = json.loads(get(f"https://www.federalregister.gov/api/v1/documents/{d}.json?fields[]=raw_text_url"))
    t = re.sub(r"\s+", " ", get(meta["raw_text_url"]))
    t = re.sub(r"<a [^>]*>.*?</a>", "[email]", t)   # obfuscated email links in the raw text
    hits = [(m.start(), m.group(1) + m.group(2)) for m in re.finditer(r"GENERAL LICENSE NO\. (46|50|52)([A-E]?)\b", t)]
    for i, (s, name) in enumerate(hits):
        e = hits[i + 1][0] if i + 1 < len(hits) else s + 8000
        body = t[s:e]
        cut = re.search(r"Bradley T\. Smith|Director,? Office of Foreign Assets Control", body)
        body = body[:cut.start()] if cut else body
        if len(body) > len(texts.get(name, "")):
            texts[name] = body
chains = [["46", "46A", "46B", "46C", "46D"], ["50", "50A", "50B", "50C"], ["52", "52A", "52B"]]
for chain in chains:
    for a, b in zip(chain, chain[1:]):
        if a not in texts or b not in texts:
            print(a, "->", b, ": text not found"); continue
        A, B = texts[a].split(), texts[b].split()
        print(f"\n=== {a} -> {b}")
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
            if op != "equal":
                print(f"  - {' '.join(A[i1:i2])[:300]}\n  + {' '.join(B[j1:j2])[:300]}")
