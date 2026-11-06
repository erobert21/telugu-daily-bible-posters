# Bilingual Bible Poster update — installation

This update is prepared for `erobert21/telugu-daily-bible-posters`.

## Included
- `index.html`: modern bilingual 4:5 poster layout with complete Telugu and English verse text.
- `tools/build_bilingual_verses.py`: reads the existing `data/daily-references.json`, imports the official USFM archives, and generates `data/daily-verses.json`.
- `.github/workflows/build-bilingual-verses.yml`: manually run GitHub Action that builds and commits the bilingual dataset.
- `SCRIPTURE-LICENSES.md`: translation credits and licence notes.
- `sources/tel2017_usfm.zip`: Telugu IRV 2019 source.
- `sources/engwebp_usfm.zip`: English WEB source.

## Install on GitHub
1. Extract this update ZIP on your phone or computer.
2. Open your repository: https://github.com/erobert21/telugu-daily-bible-posters
3. Upload the extracted files and folders into the repository root. Keep the existing `data/daily-references.json`, `data/daily-reference-index.csv`, and `qr-maker.html`; do not delete them.
4. Confirm the uploaded paths are exactly:
   - `index.html`
   - `SCRIPTURE-LICENSES.md`
   - `tools/build_bilingual_verses.py`
   - `.github/workflows/build-bilingual-verses.yml`
   - `sources/tel2017_usfm.zip`
   - `sources/engwebp_usfm.zip`
5. Open the repository's **Actions** tab. The workflow requires repository Actions workflow permissions that allow `GITHUB_TOKEN` to write contents.
6. Select **Build bilingual Bible verses** and press **Run workflow**.
7. Wait for the workflow to finish. It will create `data/daily-verses.json` only if all references match in both source editions.
8. Open GitHub Pages and test the website. Existing monthly QR links using `?month=1` through `?month=12` remain unchanged.

## If the workflow fails
Open the failed workflow run and download the `bilingual-build-errors` artifact if one was created. A failed build does not publish incomplete verse data. The most likely issue is a reference code/book mismatch that needs review.

## Important
GitHub Actions needs repository **Contents: Read and write** permission. In repository settings, check Actions workflow permissions if the commit step is denied. The current connected GitHub integration previously returned HTTP 403 on a write, so this manual upload/workflow route is provided.
