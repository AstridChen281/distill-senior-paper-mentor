#!/usr/bin/env python3
"""Import user-provided papers locally. No network calls or model inference."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


SUPPORTED = {".pdf", ".txt", ".md", ".html", ".htm"}
ROOT = Path(__file__).resolve().parent.parent


def extract(source):
    suffix = source.suffix.lower()
    if suffix == ".pdf":
        if not shutil.which("pdftotext"):
            raise ValueError("PDF import requires pdftotext")
        if not source.read_bytes().startswith(b"%PDF-"):
            raise ValueError("File is not a PDF")
        result = subprocess.run(["pdftotext", "-layout", str(source), "-"],
                                capture_output=True, check=True, timeout=120)
        text = result.stdout.decode("utf-8", errors="strict")
    else:
        text = source.read_text(encoding="utf-8")
        if suffix in {".html", ".htm"}:
            try:
                from bs4 import BeautifulSoup
            except ImportError as error:
                raise ValueError("HTML import requires beautifulsoup4") from error
            soup = BeautifulSoup(text, "html.parser")
            for node in soup.select("script, style, nav"):
                node.decompose()
            article = soup.select_one("article") or soup.select_one("main") or soup
            text = article.get_text("\n", strip=True)
    if len(text.strip()) < 80:
        raise ValueError("Too little extractable text; scanned PDFs need OCR")
    if "\ufffd" in text or "\x00" in text:
        raise ValueError("Damaged text extraction; inspect the original")
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "library",
                        help="Local library directory, defaults to this skill's ignored library/")
    args = parser.parse_args()
    files, failures = [], []
    for path in args.paths:
        if path.is_dir():
            files += sorted(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED)
        elif path.is_file() and path.suffix.lower() in SUPPORTED:
            files.append(path)
        else:
            failures.append({"file": str(path), "error": "Missing file or unsupported format"})
    library = args.output.resolve()
    library.mkdir(parents=True, exist_ok=True)
    index_path = library / "index.json"
    now = datetime.now(timezone.utc).isoformat()
    data = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {
        "schema_version": 1, "created_at": now, "papers": [],
    }
    existing = {p["sha256"] for p in data["papers"]}
    imported, duplicates = 0, 0
    for source in files:
        try:
            content = source.read_bytes()
            digest = hashlib.sha256(content).hexdigest()
            if digest in existing:
                duplicates += 1
                continue
            text = extract(source)
            identifier = "paper-" + digest[:16]
            original = library / "sources" / (identifier + source.suffix.lower())
            extracted = library / "text" / (identifier + ".txt")
            original.parent.mkdir(parents=True, exist_ok=True)
            extracted.parent.mkdir(parents=True, exist_ok=True)
            original.write_bytes(content)
            extracted.write_text(text, encoding="utf-8")
            data["papers"].append({
                "id": identifier, "filename": source.name, "sha256": digest,
                "source_path": original.relative_to(library).as_posix(),
                "text_path": extracted.relative_to(library).as_posix(),
                "imported_at": now, "reading_level": "extracted", "read_sections": [],
                "card_path": None, "characters": len(text),
            })
            existing.add(digest)
            imported += 1
        except (OSError, ValueError, UnicodeError, subprocess.SubprocessError) as error:
            failures.append({"file": str(source), "error": str(error)})
    data["updated_at"] = now
    index_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"imported": imported, "duplicates": duplicates,
                      "total": len(data["papers"]), "index": str(index_path),
                      "reading_level": "extracted; distillation still requires reading",
                      "failures": failures}, ensure_ascii=False))
    return int(bool(failures) or not data["papers"])


if __name__ == "__main__":
    sys.exit(main())
