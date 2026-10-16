"""
captcha_solver.py
-----------------
High-accuracy CAPTCHA solver for PARIVESH KYA.
Primary: ddddocr (Zero-DLL, pure-Python / onnxruntime, trained on alphanumeric CAPTCHAs).
Fallback: Custom ONNX CNN model (captcha_model.onnx).

Usage:
    from captcha_solver import solve_captcha_from_png, solve_captcha_from_bytes
"""

from __future__ import annotations

import io
import base64
import logging
import os
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

logger = logging.getLogger(__name__)

# Character vocabulary (for ONNX fallback)
CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
assert len(CHARS) == 62

MODEL_H = 60
MODEL_W = 160
CHAR_W  = MODEL_W // 5

ONNX_PATH = Path(__file__).parent / "captcha_model.onnx"


# ── ddddocr Engine (Primary) ──────────────────────────────────────────────────
_ddddocr_instance = None

def _get_ddddocr():
    global _ddddocr_instance
    if _ddddocr_instance is None:
        try:
            import ddddocr
            _ddddocr_instance = ddddocr.DdddOcr(beta=True, show_ad=False)
            logger.info("ddddocr (beta model) initialized successfully.")
        except Exception as e:
            logger.warning("ddddocr beta initialization failed, trying standard: %s", e)
            try:
                import ddddocr
                _ddddocr_instance = ddddocr.DdddOcr(show_ad=False)
            except Exception as e2:
                logger.warning("ddddocr initialization failed: %s", e2)
    return _ddddocr_instance


# ── Session (ONNX Fallback) ───────────────────────────────────────────────────
_session = None

def _get_session():
    global _session
    if _session is None:
        import onnxruntime as ort
        if not ONNX_PATH.exists():
            raise FileNotFoundError(
                f"captcha_model.onnx not found at {ONNX_PATH}. "
                "Run convert_to_onnx.py first."
            )
        _session = ort.InferenceSession(
            str(ONNX_PATH),
            providers=["CPUExecutionProvider"],
        )
        logger.info("ONNX fallback session loaded: %s", ONNX_PATH)
    return _session


# ── Image preprocessing (ONNX Fallback) ───────────────────────────────────────
def _preprocess_strip(img: Image.Image) -> np.ndarray:
    gray = img.convert("L")
    gray = gray.resize((MODEL_W, MODEL_H), Image.LANCZOS)
    gray = gray.filter(ImageFilter.GaussianBlur(radius=0.5))
    arr = np.array(gray, dtype=np.float32) / 255.0
    return arr[np.newaxis, np.newaxis, :, :]


def _preprocess_full(img: Image.Image) -> np.ndarray:
    gray = img.convert("L")
    gray = gray.resize((MODEL_W, MODEL_H), Image.LANCZOS)
    arr = np.array(gray, dtype=np.float32) / 255.0
    return arr[np.newaxis, np.newaxis, :, :]


def _infer_char(arr: np.ndarray) -> tuple[str, float]:
    sess = _get_session()
    logits = sess.run(["output"], {"input": arr})[0][0]
    probs  = _softmax(logits)
    idx    = int(np.argmax(probs))
    return CHARS[idx], float(probs[idx])


def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())
    return e / e.sum()


def _segment_captcha(img: Image.Image, n_chars: int = 5) -> list[Image.Image]:
    w, h = img.size
    strip_w = w // n_chars
    strips = []
    for i in range(n_chars):
        left  = i * strip_w
        right = left + strip_w if i < n_chars - 1 else w
        strips.append(img.crop((left, 0, right, h)))
    return strips


# ── Public API ────────────────────────────────────────────────────────────────
def solve_captcha_from_image(img: Image.Image, n_chars: int = 5,
                             min_confidence: float = 0.30) -> tuple[str, float]:
    """
    Solves a CAPTCHA image using ddddocr (primary), falling back to ONNX CNN.

    Parameters
    ----------
    img            : PIL Image
    n_chars        : Expected number of characters (default 5)
    min_confidence : Per-character confidence threshold for fallback

    Returns
    -------
    (text, confidence)
    """
    # 1. Primary: ddddocr
    ocr = _get_ddddocr()
    if ocr is not None:
        try:
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            pred = ocr.classification(buf.getvalue()).strip()
            if pred and len(pred) >= 4:
                logger.info("ddddocr solved CAPTCHA: '%s'", pred)
                return pred, 0.95
        except Exception as err:
            logger.warning("ddddocr error: %s, falling back to ONNX", err)

    # 2. Fallback: ONNX CNN strip segmentation
    try:
        strips = _segment_captcha(img, n_chars=n_chars)
        chars, confs = [], []
        for strip in strips:
            arr = _preprocess_strip(strip)
            char, conf = _infer_char(arr)
            chars.append(char)
            confs.append(conf)

        mean_conf = float(np.mean(confs))
        text = "".join(chars)
        return text, mean_conf
    except Exception as e:
        logger.error("ONNX fallback error: %s", e)
        return "", 0.0


def solve_captcha_from_png(path: str | Path, n_chars: int = 5,
                            min_confidence: float = 0.30) -> tuple[str, float]:
    """Loads a PNG file and calls solve_captcha_from_image."""
    img = Image.open(path)
    return solve_captcha_from_image(img, n_chars=n_chars, min_confidence=min_confidence)


def solve_captcha_from_b64(b64_data: str, n_chars: int = 5,
                            min_confidence: float = 0.30) -> tuple[str, float]:
    """Decodes a base64 string (with or without data-URI prefix) and solves it."""
    if "," in b64_data:
        b64_data = b64_data.split(",", 1)[1]
    raw = base64.b64decode(b64_data)
    img = Image.open(io.BytesIO(raw))
    return solve_captcha_from_image(img, n_chars=n_chars, min_confidence=min_confidence)


def solve_captcha_from_bytes(data: bytes, n_chars: int = 5,
                              min_confidence: float = 0.30) -> tuple[str, float]:
    """Wraps raw bytes (PNG/JPEG) into a PIL Image and solves."""
    img = Image.open(io.BytesIO(data))
    return solve_captcha_from_image(img, n_chars=n_chars, min_confidence=min_confidence)
