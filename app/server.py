"""
app/server.py
Flask REST API for CipherX — connects the frontend SPA to the Python cipher backend.
"""

import sys
import os

# Ensure the project root is on the path so `src` is importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from flask import Flask, render_template, request, jsonify
from src.cesar import cesar_cipher, frequency_analysis_caesar
from src.affine import affine_cipher, frequency_analysis_affine
from src.substitute import substitution_cipher, frequency_analysis_substitution
from src.languages import ALPHABETS, FREQ_TABLES, list_languages, get_alphabet, get_freq_table
from src.auto_detect import detect_language, detect_and_decrypt

app = Flask(__name__, template_folder="templates", static_folder="static")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get_language_data(language: str):
    """Return (alphabet, freq_table) for the requested language."""
    lang = language.lower()
    if lang not in ALPHABETS:
        raise ValueError(f"Unknown language: {language}")
    return ALPHABETS[lang], FREQ_TABLES[lang]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/languages", methods=["GET"])
def api_languages():
    """Return available languages with their alphabets."""
    data = {
        lang: {"alphabet": ALPHABETS[lang], "size": len(ALPHABETS[lang])}
        for lang in list_languages()
    }
    return jsonify({"languages": data})


@app.route("/api/encrypt", methods=["POST"])
def api_encrypt():
    """
    Encrypt text with the specified cipher.

    Expected JSON body:
    {
      "text": str,
      "cipher": "caesar" | "affine" | "substitution",
      "language": str,
      "shift": int,          # Caesar only
      "a": int,              # Affine only
      "b": int,              # Affine only
      "key": str             # Substitution only
    }
    """
    data = request.get_json(force=True)
    text    = data.get("text", "")
    cipher  = data.get("cipher", "caesar").lower()
    language= data.get("language", "english").lower()

    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    try:
        alphabet, _ = _get_language_data(language)

        if cipher == "caesar":
            shift = int(data.get("shift", 3))
            result = cesar_cipher(text, alphabet, shift, mode="encrypt")
            meta = {"shift": shift}

        elif cipher == "affine":
            a = int(data.get("a", 5))
            b = int(data.get("b", 8))
            result = affine_cipher(text, alphabet, a, b, mode="encrypt")
            meta = {"a": a, "b": b}

        elif cipher == "substitution":
            key = data.get("key", "")
            if not key:
                return jsonify({"error": "Substitution key required"}), 400
            result = substitution_cipher(text, alphabet, key, mode="encrypt")
            meta = {"key": key}

        else:
            return jsonify({"error": f"Unknown cipher: {cipher}"}), 400

        return jsonify({
            "result": result,
            "cipher": cipher,
            "language": language,
            "meta": meta,
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500


@app.route("/api/decrypt", methods=["POST"])
def api_decrypt():
    """
    Decrypt text with the specified cipher and optional keys, or via frequency analysis.

    Expected JSON body:
    {
      "text": str,
      "cipher": "caesar" | "affine" | "substitution" | "auto",
      "language": str | "auto",
      "method": "key" | "frequency",   # default: key
      "shift": int,
      "a": int,
      "b": int,
      "key": str
    }
    """
    data = request.get_json(force=True)
    text    = data.get("text", "")
    cipher  = data.get("cipher", "auto").lower()
    language= data.get("language", "auto").lower()
    method  = data.get("method", "frequency").lower()

    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    try:
        # Auto mode — frequency analysis across all ciphers
        if cipher == "auto" or method == "frequency":
            out = detect_and_decrypt(text, language if language != "auto" else None, cipher if cipher != "auto" else None)
            return jsonify({
                "result": out["decrypted_text"],
                "detected_language": out["detected_language"],
                "detected_cipher": out["detected_cipher"],
                "score": out["score"],
                "method": "frequency",
            })

        # Manual key-based decryption
        alphabet, freq_table = _get_language_data(language if language != "auto" else detect_language(text))

        if cipher == "caesar":
            if method == "key":
                shift = int(data.get("shift", 0))
                result = cesar_cipher(text, alphabet, shift, mode="decrypt")
                meta = {"shift": shift}
            else:
                result = frequency_analysis_caesar(text, alphabet, freq_table)
                meta = {}

        elif cipher == "affine":
            if method == "key":
                a = int(data.get("a", 5))
                b = int(data.get("b", 8))
                result = affine_cipher(text, alphabet, a, b, mode="decrypt")
                meta = {"a": a, "b": b}
            else:
                result = frequency_analysis_affine(text, alphabet, freq_table)
                meta = {}

        elif cipher == "substitution":
            if method == "key":
                key = data.get("key", "")
                if not key:
                    return jsonify({"error": "Substitution key required"}), 400
                result = substitution_cipher(text, alphabet, key, mode="decrypt")
                meta = {"key": key}
            else:
                result = frequency_analysis_substitution(text, alphabet, freq_table)
                meta = {}

        else:
            return jsonify({"error": f"Unknown cipher: {cipher}"}), 400

        return jsonify({
            "result": result,
            "cipher": cipher,
            "language": language,
            "method": method,
            "meta": meta,
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500


@app.route("/api/frequency", methods=["POST"])
def api_frequency():
    """
    Compute and return letter frequency counts for the given text.

    Expected JSON body:
    {
      "text": str,
      "language": str
    }
    """
    data = request.get_json(force=True)
    text     = data.get("text", "")
    language = data.get("language", "english").lower()

    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    try:
        alphabet, freq_table = _get_language_data(language)

        counts = {ch: 0 for ch in alphabet}
        for ch in text.lower():
            if ch in counts:
                counts[ch] += 1

        total = sum(counts.values())
        observed = {ch: round(cnt / total, 6) if total > 0 else 0 for ch, cnt in counts.items()}

        # Reference frequencies (normalised to same scale)
        ref_total = sum(freq_table.values())
        reference = {ch: round(freq_table.get(ch, 0) / ref_total, 6) for ch in alphabet}

        return jsonify({
            "observed": observed,
            "reference": reference,
            "alphabet": list(alphabet),
            "language": language,
            "total_chars": total,
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/detect-language", methods=["POST"])
def api_detect_language():
    """Auto-detect language from input text."""
    data = request.get_json(force=True)
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    lang = detect_language(text)
    return jsonify({"language": lang, "alphabet": ALPHABETS[lang]})
