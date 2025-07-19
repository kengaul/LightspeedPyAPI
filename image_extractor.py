import subprocess
import requests
from pathlib import Path
from typing import Iterable


def pdf_to_text(pdf_path: str | Path) -> str:
    """Return text extracted from ``pdf_path`` using ``pdftotext``."""
    result = subprocess.run([
        "pdftotext",
        str(pdf_path),
        "-",
    ], check=True, capture_output=True, text=True)
    return result.stdout


def extract_images(pdf_path: str | Path, output_dir: str | Path) -> None:
    """Extract images from ``pdf_path`` into ``output_dir`` using ``pdfimages``."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "pdfimages",
        "-j",
        str(pdf_path),
        str(output_dir / "image"),
    ], check=True)


def download_images(urls: Iterable[str], output_dir: str | Path) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for url in urls:
        filename = output_dir / Path(url).name
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(resp.content)
        except Exception:
            pass
