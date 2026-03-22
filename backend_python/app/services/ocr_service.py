import base64
import os
from dataclasses import dataclass


@dataclass
class OCRResult:
    status: str
    text: str
    engine: str
    detail: str | None = None


def _extract_text_plain(file_path: str) -> OCRResult:
    try:
        with open(file_path, "rb") as fh:
            raw = fh.read()
        text = raw.decode("utf-8", errors="ignore").strip()
        if not text:
            return OCRResult(status="no_text", text="", engine="plain_text")
        return OCRResult(status="ok", text=text, engine="plain_text")
    except Exception as exc:
        return OCRResult(status="error", text="", engine="plain_text", detail=str(exc))


def _extract_pdf_text(file_path: str) -> OCRResult:
    try:
        from pypdf import PdfReader
    except Exception:
        return OCRResult(
            status="unsupported",
            text="",
            engine="pypdf",
            detail="Dependência pypdf não instalada.",
        )
    try:
        reader = PdfReader(file_path)
        chunks: list[str] = []
        for page in reader.pages[:8]:
            chunks.append((page.extract_text() or "").strip())
        text = "\n".join([c for c in chunks if c]).strip()
        if not text:
            return OCRResult(status="no_text", text="", engine="pypdf")
        return OCRResult(status="ok", text=text, engine="pypdf")
    except Exception as exc:
        return OCRResult(status="error", text="", engine="pypdf", detail=str(exc))


def _extract_image_text_tesseract(file_path: str) -> OCRResult:
    try:
        from PIL import Image
        import pytesseract
    except Exception:
        return OCRResult(
            status="unsupported",
            text="",
            engine="tesseract",
            detail="Dependências Pillow/pytesseract não instaladas.",
        )
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang=os.getenv("OCR_TESSERACT_LANG", "por+eng")).strip()
        if not text:
            return OCRResult(status="no_text", text="", engine="tesseract")
        return OCRResult(status="ok", text=text, engine="tesseract")
    except Exception as exc:
        return OCRResult(status="error", text="", engine="tesseract", detail=str(exc))


def _extract_image_text_openai(file_path: str) -> OCRResult:
    if os.getenv("TEST_ENV", "0") == "1":
        return OCRResult(status="unsupported", text="", engine="openai_vision", detail="test_env")

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return OCRResult(status="unsupported", text="", engine="openai_vision", detail="OPENAI_API_KEY ausente")

    try:
        from openai import OpenAI
    except Exception:
        return OCRResult(status="unsupported", text="", engine="openai_vision", detail="SDK OpenAI indisponível")

    try:
        with open(file_path, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{b64}"
        client = OpenAI(api_key=api_key)
        model = os.getenv("OCR_OPENAI_MODEL", "gpt-4o-mini")
        response = client.chat.completions.create(
            model=model,
            temperature=0.0,
            messages=[
                {
                    "role": "system",
                    "content": "Extraia o texto visível da imagem. Responda somente com o texto extraído em português.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Realize OCR desta imagem."},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
        )
        text = (response.choices[0].message.content or "").strip()
        if not text:
            return OCRResult(status="no_text", text="", engine="openai_vision")
        return OCRResult(status="ok", text=text, engine="openai_vision")
    except Exception as exc:
        return OCRResult(status="error", text="", engine="openai_vision", detail=str(exc))


def _is_text_file(ext: str) -> bool:
    return ext in {".txt", ".csv", ".json", ".md", ".log"}


def _is_image_file(ext: str) -> bool:
    return ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}


def extract_text_from_file(file_path: str, filename: str | None = None) -> OCRResult:
    name = (filename or file_path).lower()
    _, ext = os.path.splitext(name)
    if _is_text_file(ext):
        return _extract_text_plain(file_path)
    if ext == ".pdf":
        return _extract_pdf_text(file_path)
    if _is_image_file(ext):
        primary = _extract_image_text_tesseract(file_path)
        if primary.status == "ok":
            return primary
        fallback = _extract_image_text_openai(file_path)
        if fallback.status == "ok":
            return fallback
        if primary.status != "unsupported":
            return primary
        return fallback
    return OCRResult(status="unsupported", text="", engine="none", detail=f"Extensão não suportada: {ext or 'n/a'}")
