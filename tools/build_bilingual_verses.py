#!/usr/bin/env python3
"""Build the 365-day bilingual verse dataset from the official USFM source archives."""
import json, re, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
DATA = ROOT / "data"
TEL_ZIP = SOURCES / "tel2017_usfm.zip"
ENG_ZIP = SOURCES / "engwebp_usfm.zip"
REFS = DATA / "daily-references.json"
OUT = DATA / "daily-verses.json"
ERRORS = DATA / "bilingual-build-errors.txt"

def clean_usfm_text(text):
    # Footnotes and cross-references are editorial apparatus, not verse wording.
    text = re.sub(r"\\f\b.*?\\f\*", " ", text, flags=re.S)
    text = re.sub(r"\\x\b.*?\\x\*", " ", text, flags=re.S)

    # Unwrap USFM word markup while discarding Strong's/lemma/morphology attributes.
    def unwrap(match):
        inner = match.group(1)
        inner = re.sub(r'(?:\||\s+)(?:strong|lemma|morph|x-strong|x-lemma)="[^"]*"', "", inner)
        return inner.strip()

    text = re.sub(r"\\\+?w\s+(.*?)\\\+?w\*", unwrap, text, flags=re.S)
    # Remove remaining USFM markers; retain their readable text.
    text = re.sub(r"\\\+?[a-zA-Z0-9-]+\*?", " ", text)
    text = re.sub(r'(?:\||\s+)(?:strong|lemma|morph|x-strong|x-lemma)="[^"]*"', "", text)
    text = text.replace("|", " ").replace("~", " ").replace("¶", " ")
    return re.sub(r"\s+", " ", text).strip()

def parse_archive(path, suffix):
    books = {}
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.endswith(".usfm") or name.startswith("00-"):
                continue
            match = re.match(r"\d+-(.+?)" + re.escape(suffix) + r"\.usfm$", name)
            if not match:
                continue
            book = match.group(1)
            raw = archive.read(name).decode("utf-8-sig")
            verses = {}
            chapters = re.finditer(r"\\c\s+(\d+)(.*?)(?=\\c\s+\d+|\\id\s|$)", raw, flags=re.S)
            for chapter_match in chapters:
                chapter = int(chapter_match.group(1))
                body = chapter_match.group(2)
                verse_matches = re.finditer(
                    r"\\v\s+(\d+)(?:-[\d]+)?(?:/[a-z])?\s+(.*?)(?=\\v\s+\d+(?:-[\d]+)?(?:/[a-z])?\s+|$)",
                    body, flags=re.S
                )
                for verse_match in verse_matches:
                    verse = int(verse_match.group(1))
                    wording = clean_usfm_text(verse_match.group(2))
                    if wording:
                        verses[(chapter, verse)] = wording
            books[book] = verses
    return books

def main():
    for required in (TEL_ZIP, ENG_ZIP, REFS):
        if not required.exists():
            raise SystemExit(f"Missing required file: {required.relative_to(ROOT)}")

    telugu = parse_archive(TEL_ZIP, "tel2017")
    english = parse_archive(ENG_ZIP, "engwebp")
    references = json.loads(REFS.read_text(encoding="utf-8"))
    if ERRORS.exists():
        ERRORS.unlink()
    if len(references) != 365:
        raise SystemExit(f"Expected 365 daily references, found {len(references)}. Check data/daily-references.json.")
    output, missing = [], []

    for item in references:
        match = re.fullmatch(r"([A-Z0-9]+)\s+(\d+):(\d+)(?:-(\d+))?", item["reference_code"].strip())
        if not match:
            missing.append((item.get("month"), item.get("day"), item.get("reference_code"), "invalid reference format"))
            continue
        book, chapter, first, last = match.group(1), int(match.group(2)), int(match.group(3)), int(match.group(4) or match.group(3))
        tel_parts, eng_parts = [], []
        for verse_num in range(first, last + 1):
            t = telugu.get(book, {}).get((chapter, verse_num))
            e = english.get(book, {}).get((chapter, verse_num))
            if not t or not e:
                missing.append((item.get("month"), item.get("day"), item["reference_code"], f"missing verse {book} {chapter}:{verse_num}"))
                break
            tel_parts.append(t)
            eng_parts.append(e)
        else:
            row = dict(item)
            row["verse_te"] = " ".join(tel_parts)
            row["verse_en"] = " ".join(eng_parts)
            row["translation_te"] = "IRV Telugu 2019"
            row["translation_en"] = "World English Bible"
            output.append(row)

    if missing:
        ERRORS.write_text("\n".join(map(str, missing)), encoding="utf-8")
        raise SystemExit(f"Build stopped: {len(missing)} reference(s) could not be matched. See data/bilingual-build-errors.txt in the workflow artifact/logs. No incomplete daily-verses.json was written.")

    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Success: generated {len(output)} bilingual daily verses at {OUT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
