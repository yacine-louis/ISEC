"""
auto_detect.py
Automatic language and cipher detection using letter frequency analysis.
"""

from .languages import ALPHABETS, FREQ_TABLES
from .cesar import frequency_analysis_caesar, cesar_cipher
from .affine import frequency_analysis_affine, affine_cipher


def _score_text(text: str, freq_table: dict) -> float:
    """
    Compute how well 'text' matches a language's frequency table.
    Uses dot-product scoring: sum of (observed_freq * expected_freq).
    Higher = better match.
    """
    text_lower = text.lower()
    alphabet = "".join(freq_table.keys())
    counts = {}
    total = 0
    for ch in text_lower:
        if ch in freq_table:
            counts[ch] = counts.get(ch, 0) + 1
            total += 1

    if total == 0:
        return 0.0

    score = 0.0
    for ch, cnt in counts.items():
        observed = cnt / total
        expected = freq_table.get(ch, 0)
        score += observed * expected
    return score


def detect_language(text: str) -> str:
    """
    Detect the most likely language of 'text' by matching its letter
    frequencies against each language's reference table.

    Returns the language name string (e.g. "english", "arabic").
    """
    best_lang = "english"
    best_score = -1.0

    for lang, freq_table in FREQ_TABLES.items():
        score = _score_text(text, freq_table)
        if score > best_score:
            best_score = score
            best_lang = lang

    return best_lang


def detect_and_decrypt(
    ciphertext: str,
    language: str | None = None,
    cipher: str | None = None,
) -> dict:
    """
    Attempt to auto-decrypt ciphertext.

    Parameters
    ----------
    ciphertext : str
        The encrypted text.
    language : str or None
        Language name; if None, auto-detected.
    cipher : str or None
        'caesar', 'affine', 'substitution', or None (try all).

    Returns
    -------
    dict with keys:
        detected_language, detected_cipher, decrypted_text, score
    """
    from .substitute import frequency_analysis_substitution

    # Step 1 — determine language
    if language is None or language.lower() == "auto":
        detected_language = detect_language(ciphertext)
    else:
        detected_language = language.lower()

    alphabet = ALPHABETS[detected_language]
    freq_table = FREQ_TABLES[detected_language]

    ciphers_to_try = []
    if cipher is None or cipher.lower() == "auto":
        ciphers_to_try = ["caesar", "affine", "substitution"]
    else:
        ciphers_to_try = [cipher.lower()]

    results = []
    for c in ciphers_to_try:
        try:
            if c == "caesar":
                decrypted = frequency_analysis_caesar(ciphertext, alphabet, freq_table)
            elif c == "affine":
                decrypted = frequency_analysis_affine(ciphertext, alphabet, freq_table)
            elif c == "substitution":
                decrypted = frequency_analysis_substitution(ciphertext, alphabet, freq_table)
            else:
                continue
            score = _score_text(decrypted, freq_table)
            results.append((c, decrypted, score))
        except Exception:
            continue

    if not results:
        return {
            "detected_language": detected_language,
            "detected_cipher": "unknown",
            "decrypted_text": ciphertext,
            "score": 0.0,
        }

    # Pick best result by score
    best_cipher, best_text, best_score = max(results, key=lambda x: x[2])

    return {
        "detected_language": detected_language,
        "detected_cipher": best_cipher,
        "decrypted_text": best_text,
        "score": best_score,
    }
