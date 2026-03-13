"""
app/server.py
Flask REST API for CipherX — connects the frontend SPA to the Python cipher backend.
"""

import sys
import os
import json
import time

# Ensure the project root is on the path so `src` is importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from flask import Flask, render_template, request, jsonify  # type: ignore
from src.cesar import cesar_cipher, crack_caesar_frequency
from src.affine import affine_cipher, crack_affine_frequency
from src.substitute import substitution_cipher, crack_substitution_frequency

app = Flask(__name__, template_folder="templates", static_folder="static")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALPHABETS = {
    "english": "abcdefghijklmnopqrstuvwxyz",
    "arabic": "ابتثجحخدذرزسشصضطظعغفقكلمنهوي",
    "french": "abcdefghijklmnopqrstuvwxyzéèêàâîïôûçœùëü",
    "kabyle": "abcdefghijklmnqrstuwxyzɣɛḍḥṭẓčǧ",
}

FREQ_PATHS = {
    "english": {
        1: os.path.join(ROOT, "grams", "english_1grams.json"),
        2: os.path.join(ROOT, "grams", "english_2grams.json"),
        3: os.path.join(ROOT, "grams", "english_3grams.json"),
        4: os.path.join(ROOT, "grams", "english_4grams.json"),
    },
    "arabic": {
        1: os.path.join(ROOT, "grams", "arabic_1grams.json"),
        2: os.path.join(ROOT, "grams", "arabic_2grams.json"),
        3: os.path.join(ROOT, "grams", "arabic_3grams.json"),
        4: os.path.join(ROOT, "grams", "arabic_4grams.json"),
    },
    "french": {
        1: os.path.join(ROOT, "grams", "french_1grams.json"),
        2: os.path.join(ROOT, "grams", "french_2grams.json"),
        3: os.path.join(ROOT, "grams", "french_3grams.json"),
        4: os.path.join(ROOT, "grams", "french_4grams.json"),
    },
    "kabyle": {
        1: os.path.join(ROOT, "grams", "kabyle_1grams.json"),
        2: os.path.join(ROOT, "grams", "kabyle_2grams.json"),
        3: os.path.join(ROOT, "grams", "kabyle_3grams.json"),
        4: os.path.join(ROOT, "grams", "kabyle_4grams.json"),
    },
}

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get_alphabet(language: str):
    """Return alphabet for the requested language."""
    lang = language.lower()
    if lang not in ALPHABETS:
        raise ValueError(f"Unknown language: {language}")
    return ALPHABETS[lang]

def _get_language_data(language: str, ngram_size: int = 4):
    """Return (alphabet, freq_path) for the requested language and ngram size."""
    lang = language.lower()
    if lang not in ALPHABETS:
        raise ValueError(f"Unknown language: {language}")
    if ngram_size not in FREQ_PATHS[lang]:
        raise ValueError(f"No frequency data for ngram size {ngram_size} in {language}")
    return ALPHABETS[lang], FREQ_PATHS[lang][ngram_size]


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
        for lang in ALPHABETS
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
        start_time = time.perf_counter()
        alphabet = _get_alphabet(language)

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

        end_time = time.perf_counter()
        return jsonify({
            "result": result,
            "cipher": cipher,
            "language": language,
            "meta": meta,
            "execution_time_ms": round((end_time - start_time) * 1000, 2),
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500


@app.route("/api/decrypt", methods=["POST"])
def api_decrypt():
    """
    Decrypt text with the specified cipher and keys, or via frequency analysis.

    Expected JSON body:
    {
      "text": str,
      "cipher": "caesar" | "affine" | "substitution",
      "language": str,
      "method": "key" | "frequency",
      "shift": int,          # Caesar key only
      "a": int,              # Affine key only
      "b": int,              # Affine key only
      "key": str,            # Substitution key only
      "ngram_size": int,     # Frequency only, 1-4
      "top_n": int           # Frequency only for caesar/affine
    }
    """
    data = request.get_json(force=True)
    text    = data.get("text", "")
    cipher  = data.get("cipher", "caesar").lower()
    language= data.get("language", "english").lower()
    method  = data.get("method", "key").lower()

    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    try:
        start_time = time.perf_counter()
        if method == "frequency":
            ngram_size = int(data.get("ngram_size", 4))
            top_n = int(data.get("top_n", 10))  # default for caesar

            if cipher == "caesar":
                alphabet, freq_path = _get_language_data(language, ngram_size)
                result, best_shift = crack_caesar_frequency(text, alphabet, freq_path, top_n=top_n)
                meta = {"shift": best_shift}

            elif cipher == "affine":
                alphabet, freq_path = _get_language_data(language, ngram_size)
                result, best = crack_affine_frequency(text, alphabet, freq_path, top_n=top_n)
                # crack_affine_frequency returns (ciphertext, None) if no suitable key is found
                if best is None:
                    meta = {
                        "a": None,
                        "b": None,
                        "warning": (
                            "No reliable affine key found with current settings; "
                            "showing ciphertext unchanged."
                        ),
                    }
                else:
                    meta = {"a": best[0], "b": best[1]}

            elif cipher == "substitution":
                alphabet, freq_path = _get_language_data(language, 4)
                result, key_str = crack_substitution_frequency(text, alphabet, freq_path)
                meta = {"key": key_str}

            else:
                return jsonify({"error": f"Unknown cipher: {cipher}"}), 400

        else:  # method == "key"
            alphabet = _get_alphabet(language)

            if cipher == "caesar":
                shift = int(data.get("shift", 0))
                result = cesar_cipher(text, alphabet, shift, mode="decrypt")
                meta = {"shift": shift}

            elif cipher == "affine":
                a = int(data.get("a", 5))
                b = int(data.get("b", 8))
                result = affine_cipher(text, alphabet, a, b, mode="decrypt")
                meta = {"a": a, "b": b}

            elif cipher == "substitution":
                key = data.get("key", "")
                if not key:
                    return jsonify({"error": "Substitution key required"}), 400
                result = substitution_cipher(text, alphabet, key, mode="decrypt")
                meta = {"key": key}

            else:
                return jsonify({"error": f"Unknown cipher: {cipher}"}), 400

        end_time = time.perf_counter()
        return jsonify({
            "result": result,
            "cipher": cipher,
            "language": language,
            "method": method,
            "meta": meta,
            "execution_time_ms": round((end_time - start_time) * 1000, 2),
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    # except Exception as e:
    #     return jsonify({"error": f"Unexpected error: {e}"}), 500


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
        alphabet = _get_alphabet(language)
        freq_path = FREQ_PATHS[language][1]  # use 1-grams for reference

        counts = {ch: 0 for ch in alphabet}
        for ch in text.lower():
            if ch in counts:
                counts[ch] += 1

        total = sum(counts.values())
        observed = {ch: round(cnt / total, 6) if total > 0 else 0 for ch, cnt in counts.items()}

        # Reference frequencies (normalised to same scale)
        with open(freq_path, "r", encoding="utf8") as f:
            ref_freq = json.load(f)
        ref_total = sum(ref_freq.values())
        reference = {ch: round(ref_freq.get(ch, 0) / ref_total, 6) for ch in alphabet}

        return jsonify({
            "observed": observed,
            "reference": reference,
            "alphabet": list(alphabet),
            "language": language,
            "total_chars": total,
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500
