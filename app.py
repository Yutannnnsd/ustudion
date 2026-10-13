from html import escape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlparse
import json
import os
import re
import struct


ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", "8138"))
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}
GENERIC_IMAGE_NAME = re.compile(
    r"^(?:\d+|sample\s*\d+|img\s*\d+|dsc\s*\d+|capture\s+one\s+\d+)$",
    re.IGNORECASE,
)
VERSION = "preserve-title-case-v1"
WATCH_EXTENSIONS = IMAGE_EXTENSIONS | {".css", ".html", ".js", ".py"}

CATEGORIES = {
    "/still.html": {
        "title": "Still life",
        "description": "Still life photographs by Studio U Yuta.",
        "folder": "still",
    },
    "/personal.html": {
        "title": "Personal",
        "description": "Personal works by Studio U Yuta.",
        "folder": "personal",
    },
    "/work.html": {
        "title": "Work",
        "description": "Selected works by Studio U Yuta.",
        "folder": "work",
    },
}

def global_header(home_href):
    return f"""    <header class="site-header">
      <a class="logo" href="{home_href}" aria-label="Studio U Yuta top page">Studio U</a>
    </header>
"""


def asset_url(path):
    return f"assets/images/{quote(path.as_posix())}"


def slug_from_text(text):
    spaced = re.sub(r"[-_]+", " ", text)
    slug = re.sub(r"[^a-z0-9]+", "-", spaced.lower()).strip("-")
    return slug or "work"


def unique_slug(base, seen):
    slug = base
    index = 2
    while slug in seen:
        slug = f"{base}-{index}"
        index += 1
    seen.add(slug)
    return slug


def site_version():
    latest = 0

    for item in ROOT.rglob("*"):
        relative = item.relative_to(ROOT)
        if any(part.startswith(".") for part in relative.parts):
            continue
        if "__pycache__" in relative.parts:
            continue
        if not item.is_file() or item.suffix.lower() not in WATCH_EXTENSIONS:
            continue

        latest = max(latest, item.stat().st_mtime_ns)

    return latest


def jpeg_dimensions(path):
    with path.open("rb") as stream:
        if stream.read(2) != b"\xff\xd8":
            return None

        while True:
            byte = stream.read(1)
            while byte and byte != b"\xff":
                byte = stream.read(1)
            if not byte:
                return None

            marker = stream.read(1)
            while marker == b"\xff":
                marker = stream.read(1)
            if not marker:
                return None

            marker_value = marker[0]
            length_bytes = stream.read(2)
            if len(length_bytes) != 2:
                return None

            length = int.from_bytes(length_bytes, "big")
            if marker_value in {
                0xC0,
                0xC1,
                0xC2,
                0xC3,
                0xC5,
                0xC6,
                0xC7,
                0xC9,
                0xCA,
                0xCB,
                0xCD,
                0xCE,
                0xCF,
            }:
                stream.read(1)
                height = int.from_bytes(stream.read(2), "big")
                width = int.from_bytes(stream.read(2), "big")
                return width, height

            stream.seek(length - 2, os.SEEK_CUR)


def image_dimensions(relative_path):
    path = ROOT / "assets" / "images" / relative_path
    suffix = path.suffix.lower()

    try:
        if suffix in {".jpg", ".jpeg"}:
            return jpeg_dimensions(path)

        if suffix == ".png":
            with path.open("rb") as stream:
                header = stream.read(24)
            if header.startswith(b"\x89PNG\r\n\x1a\n"):
                return struct.unpack(">II", header[16:24])

        if suffix == ".gif":
            with path.open("rb") as stream:
                header = stream.read(10)
            if header[:6] in {b"GIF87a", b"GIF89a"}:
                return struct.unpack("<HH", header[6:10])
    except OSError:
        return None

    return None


def image_attributes(relative_path, class_name):
    classes = [class_name]
    dimensions = image_dimensions(relative_path)
    attrs = ""

    if dimensions:
        width, height = dimensions
        if height > width:
            classes.append("is-portrait")
        elif width > height:
            classes.append("is-landscape")
        else:
            classes.append("is-square")

        attrs = (
            f' width="{width}" height="{height}"'
            f' style="--image-ratio: {width} / {height};"'
        )

    return f'class="{" ".join(classes)}"{attrs}'


def title_from_filename(filename):
    stem = Path(filename).stem
    spaced = re.sub(r"[-_]+", " ", stem)
    spaced = re.sub(r"\s+", " ", spaced).strip()
    return spaced if spaced else "Untitled"


def is_image_file(item):
    return item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS


def list_image_files(directory):
    return sorted(
        [item for item in directory.iterdir() if is_image_file(item)],
        key=lambda item: item.name.lower(),
    )


def title_from_work_folder(folder_name, first_image_name):
    image_title = title_from_filename(first_image_name)
    folder_title = title_from_filename(folder_name)
    image_stem = re.sub(r"[-_]+", " ", Path(first_image_name).stem).strip()

    if GENERIC_IMAGE_NAME.fullmatch(image_stem):
        return folder_title

    return image_title


def list_works(folder):
    image_dir = ROOT / "assets" / "images" / folder
    if not image_dir.exists():
        return []

    seen_slugs = set()
    works = [
        {
            "title": title_from_filename(image.name),
            "src": Path(folder) / image.name,
            "images": [Path(folder) / image.name],
            "slug": unique_slug(slug_from_text(Path(image.name).stem), seen_slugs),
        }
        for image in list_image_files(image_dir)
    ]

    work_folders = sorted(
        [item for item in image_dir.iterdir() if item.is_dir()],
        key=lambda item: item.name.lower(),
    )

    for work_folder in work_folders:
        images = list_image_files(work_folder)
        if not images:
            continue

        first_image = images[0]
        works.append(
            {
                "title": title_from_work_folder(work_folder.name, first_image.name),
                "src": Path(folder) / work_folder.name / first_image.name,
                "images": [Path(folder) / work_folder.name / image.name for image in images],
                "slug": unique_slug(slug_from_text(work_folder.name), seen_slugs),
            }
        )

    return works


def render_work_entry(category_title, work, index):
    heading_tag = "h1" if index == 0 else "h2"
    title = work["title"]
    src = asset_url(work["src"])
    href = f"{quote(work['src'].parts[0])}/{quote(work['slug'])}.html"

    return f"""
      <article class="work-entry">
        <div class="work-stage">
          <div class="work-copy">
            <{heading_tag}>{escape(category_title)}</{heading_tag}>
            <a class="piece-title piece-link" href="{href}">{escape(title)}</a>
          </div>

          <a class="piece-image piece-link" href="{href}" aria-label="{escape(title)} detail">
            <img {image_attributes(work["src"], "piece-photo")} src="{src}" alt="{escape(title)}" />
          </a>
        </div>
      </article>
    """


def render_category_page(path):
    category = CATEGORIES[path]
    title = category["title"]
    folder = category["folder"]
    works = list_works(folder)

    entries = "\n".join(
        render_work_entry(title, work, index) for index, work in enumerate(works)
    )

    if not entries:
        entries = f"""
      <article class="work-entry">
        <div class="work-stage">
          <div class="work-copy">
            <h1>{escape(title)}</h1>
            <p class="piece-title">No Images Yet</p>
          </div>
        </div>
      </article>
        """

    return f"""<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(title)} | Studio U Yuta</title>
    <meta name="description" content="{escape(category['description'])}" />
    <link rel="stylesheet" href="assets/styles.css?v={VERSION}" />
  </head>
  <body>
{global_header("./")}
    <main class="works-page" aria-label="{escape(title)}">
{entries}
    </main>
    <script src="assets/main.js?v={VERSION}"></script>
  </body>
</html>
"""


def category_from_folder(folder):
    for path, category in CATEGORIES.items():
        if category["folder"] == folder:
            return path, category
    return None, None


def render_detail_page(folder, slug):
    category_path, category = category_from_folder(folder)
    if not category:
        return None

    works = list_works(folder)
    work = next((item for item in works if item["slug"] == slug), None)
    if not work:
        return None

    category_title = category["title"]
    title = work["title"]
    category_href = f"../{category_path.lstrip('/')}"
    image_slides = "\n".join(
        f"""
          <figure class="detail-slide">
            <img {image_attributes(image, "detail-photo")} src="../{asset_url(image)}" alt="{escape(title)}" />
          </figure>
        """
        for image in work["images"]
    )
    return f"""<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(title)} | {escape(category_title)} | Studio U Yuta</title>
    <meta name="description" content="{escape(title)} by Studio U Yuta." />
    <link rel="stylesheet" href="../assets/styles.css?v={VERSION}" />
  </head>
  <body>
{global_header("../")}
    <main class="detail-page" aria-label="{escape(title)}">
      <section class="detail-stage">
        <a class="detail-category" href="{category_href}">{escape(category_title)}</a>

        <div class="detail-slider" data-slider>
          <div class="detail-track" data-slider-track tabindex="0" aria-label="{escape(title)} images">
{image_slides}
          </div>
        </div>

        <h1 class="detail-title">{escape(title)}</h1>
      </section>
    </main>
    <script src="../assets/main.js?v={VERSION}"></script>
  </body>
</html>
"""


class StudioRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path == "/site-version.json":
            payload = json.dumps({"version": site_version()}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if path in CATEGORIES:
            html = render_category_page(path).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return

        detail_match = re.fullmatch(r"/(still|personal|work)/([^/]+)\.html", path)
        if detail_match:
            html_text = render_detail_page(detail_match.group(1), detail_match.group(2))
            if html_text:
                html = html_text.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)
                return

        return super().do_GET()


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), StudioRequestHandler)
    print(f"Studio U Yuta is running at http://{HOST}:{PORT}/")
    print("Press Ctrl+C to stop.")
    server.serve_forever()
