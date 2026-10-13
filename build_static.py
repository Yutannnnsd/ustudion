from pathlib import Path
import shutil

import app


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


def write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_assets():
    source = ROOT / "assets"
    destination = DIST / "assets"
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"),
    )


def build():
    if DIST.exists():
        shutil.rmtree(DIST)

    DIST.mkdir(parents=True)
    copy_assets()

    write_text(DIST / "index.html", (ROOT / "index.html").read_text(encoding="utf-8"))

    for route, category in app.CATEGORIES.items():
        write_text(DIST / route.lstrip("/"), app.render_category_page(route))

        folder = category["folder"]
        for work in app.list_works(folder):
            detail = app.render_detail_page(folder, work["slug"])
            if detail:
                write_text(DIST / folder / f"{work['slug']}.html", detail)


if __name__ == "__main__":
    build()
    print(f"Static site written to {DIST}")
