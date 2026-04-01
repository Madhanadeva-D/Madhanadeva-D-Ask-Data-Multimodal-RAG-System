import re
import logging
from io import BytesIO

import pdfplumber
import pytesseract
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageFilter

logger = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; RAGBot/2.0)"}
_MAX_BYTES = 10 * 1024 * 1024  # 10 MB cap for URL responses


def from_url(url: str) -> str:
    resp = requests.get(url, headers=_HEADERS, timeout=15, stream=True)
    resp.raise_for_status()

    raw = b""
    for chunk in resp.iter_content(8192):
        raw += chunk
        if len(raw) > _MAX_BYTES:
            break

    soup = BeautifulSoup(raw, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    body = soup.find("main") or soup.find("article") or soup.body or soup
    text = " ".join(body.stripped_strings)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    logger.info(f"URL extracted {len(text):,} chars")
    return text


def from_pdf(stream: BytesIO) -> str:
    pages = []
    with pdfplumber.open(stream) as pdf:
        for page in pdf.pages:
            parts = []
            if page.extract_text():
                parts.append(page.extract_text().strip())
            for table in page.extract_tables():
                for row in table:
                    parts.append(" | ".join(cell or "" for cell in row))
            if parts:
                pages.append("\n".join(parts))

    text = "\n\n".join(pages).strip()
    logger.info(f"PDF extracted {len(text):,} chars from {len(pages)} pages")
    return text


def from_image(stream: BytesIO) -> str:
    img = Image.open(stream).convert("L")
    img = img.filter(ImageFilter.SHARPEN)
    img = img.point(lambda px: 255 if px > 128 else 0, "L")

    text = pytesseract.image_to_string(img, config="--oem 3 --psm 3").strip()
    logger.info(f"Image OCR extracted {len(text):,} chars")
    return text
