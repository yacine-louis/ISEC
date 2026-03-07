"""
languages.py
Alphabets and letter-frequency tables for each supported language.
Frequencies are approximate relative values (not probabilities) — higher = more common.
"""

# ---------------------------------------------------------------------------
# Alphabets
# ---------------------------------------------------------------------------

ALPHABETS = {
    "english": "abcdefghijklmnopqrstuvwxyz",
    "french":  "abcdefghijklmnopqrstuvwxyz",   # same Latin letters, different freq
    "kabyle":  "abcdefghijklmnopqrstuvwxyz",   # Kabyle uses Latin; subset differs in freq
    "arabic":  "ابتثجحخدذرزسشصضطظعغفقكلمنهوي",
}

# ---------------------------------------------------------------------------
# Frequency tables  {letter: relative_frequency}
# ---------------------------------------------------------------------------

# English — from Cornell / standard corpora
FREQ_ENGLISH = {
    'e': 0.1202, 't': 0.0910, 'a': 0.0812, 'o': 0.0768, 'i': 0.0731,
    'n': 0.0695, 's': 0.0628, 'r': 0.0602, 'h': 0.0592, 'd': 0.0432,
    'l': 0.0398, 'u': 0.0288, 'c': 0.0271, 'm': 0.0261, 'f': 0.0230,
    'y': 0.0211, 'w': 0.0209, 'g': 0.0203, 'p': 0.0182, 'b': 0.0149,
    'v': 0.0111, 'k': 0.0069, 'x': 0.0017, 'q': 0.0011, 'j': 0.0010,
    'z': 0.0007,
}

# French — from Becker & al. corpora
FREQ_FRENCH = {
    'e': 0.1474, 'a': 0.0844, 's': 0.0790, 'i': 0.0763, 't': 0.0724,
    'n': 0.0709, 'r': 0.0643, 'u': 0.0637, 'l': 0.0546, 'o': 0.0540,
    'd': 0.0341, 'c': 0.0323, 'p': 0.0302, 'm': 0.0262, 'é': 0.0171,
    'v': 0.0164, 'q': 0.0099, 'f': 0.0096, 'b': 0.0089, 'g': 0.0087,
    'h': 0.0074, 'j': 0.0061, 'à': 0.0054, 'x': 0.0042, 'y': 0.0030,
    'z': 0.0013, 'k': 0.0002, 'w': 0.0001,
}

# Kabyle (Tamazight written in Latin) — approximate from Tamazight texts
FREQ_KABYLE = {
    'a': 0.1650, 'i': 0.1100, 'n': 0.0920, 'e': 0.0850, 't': 0.0820,
    'r': 0.0780, 'l': 0.0720, 'u': 0.0680, 's': 0.0640, 'γ': 0.0550,
    'k': 0.0490, 'd': 0.0460, 'g': 0.0440, 'w': 0.0410, 'm': 0.0370,
    'b': 0.0310, 'c': 0.0280, 'z': 0.0250, 'y': 0.0230, 'f': 0.0210,
    'h': 0.0190, 'q': 0.0170, 'x': 0.0120, 'v': 0.0040, 'j': 0.0030,
    'p': 0.0010,
}

# Arabic — frequencies from standard Arabic text corpora
FREQ_ARABIC = {
    'ا': 0.1273, 'ل': 0.0897, 'ن': 0.0632, 'م': 0.0606, 'ي': 0.0570,
    'و': 0.0566, 'ه': 0.0474, 'ر': 0.0446, 'ع': 0.0396, 'ت': 0.0385,
    'ب': 0.0368, 'ف': 0.0269, 'س': 0.0268, 'ق': 0.0249, 'ك': 0.0225,
    'د': 0.0206, 'ج': 0.0197, 'أ': 0.0176, 'ح': 0.0174, 'ذ': 0.0168,
    'خ': 0.0145, 'ش': 0.0141, 'ص': 0.0141, 'ز': 0.0100, 'ط': 0.0086,
    'ث': 0.0072, 'غ': 0.0058, 'ض': 0.0055, 'ظ': 0.0037,
}

_ARABIC_BASE = {
    'ا': 0.1273, 'ل': 0.0897, 'ن': 0.0632, 'م': 0.0606, 'ي': 0.0570,
    'و': 0.0566, 'ه': 0.0474, 'ر': 0.0446, 'ع': 0.0396, 'ت': 0.0385,
    'ب': 0.0368, 'ف': 0.0269, 'س': 0.0268, 'ق': 0.0249, 'ك': 0.0225,
    'د': 0.0206, 'ج': 0.0197, 'ح': 0.0174, 'ذ': 0.0168, 'خ': 0.0145,
    'ش': 0.0141, 'ص': 0.0141, 'ز': 0.0100, 'ط': 0.0086, 'ث': 0.0072,
    'غ': 0.0058, 'ض': 0.0055, 'ظ': 0.0037,
}

# Map language name → freq table
FREQ_TABLES = {
    "english": FREQ_ENGLISH,
    "french":  FREQ_FRENCH,
    "kabyle":  FREQ_KABYLE,
    "arabic":  _ARABIC_BASE,
}


def get_alphabet(language: str) -> str:
    """Return the alphabet string for the given language (lowercase name)."""
    lang = language.lower()
    if lang not in ALPHABETS:
        raise ValueError(f"Unsupported language: {language}. Choose from: {list(ALPHABETS.keys())}")
    return ALPHABETS[lang]


def get_freq_table(language: str) -> dict:
    """Return the frequency dict for the given language."""
    lang = language.lower()
    if lang not in FREQ_TABLES:
        raise ValueError(f"Unsupported language: {language}. Choose from: {list(FREQ_TABLES.keys())}")
    return FREQ_TABLES[lang]


def list_languages() -> list:
    """Return list of supported language names."""
    return list(ALPHABETS.keys())
