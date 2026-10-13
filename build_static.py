from pathlib import Path
import os
import shutil

import app


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / os.environ.get("SITE_OUTPUT_DIR", "docs")


def write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_assets():
    source = ROOT / "assets"
    destination = OUTPUT_DIR / "assets"
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"),
    )


def build():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir(parents=True)
    copy_assets()

    write_text(OUTPUT_DIR / ".nojekyll", "")
    write_text(OUTPUT_DIR / "index.html", (ROOT / "index.html").read_text(encoding="utf-8"))

    custom_domain = os.environ.get("CUSTOM_DOMAIN", "").strip()
    if custom_domain:
        write_text(OUTPUT_DIR / "CNAME", f"{custom_domain}\n")

    for route, category in app.CATEGORIES.items():
        write_text(OUTPUT_DIR / route.lstrip("/"), app.render_category_page(route))

        folder = category["folder"]
        for work in app.list_works(folder):
            detail = app.render_detail_page(folder, work["slug"])
            if detail:
                write_text(OUTPUT_DIR / folder / f"{work['slug']}.html", detail)


if __name__ == "__main__":
    build()
    print(f"Static site written to {OUTPUT_DIR}")
