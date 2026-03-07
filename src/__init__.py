"""
src/__init__.py
Public API for the ISEC cipher library.
"""

from .cesar import cesar_cipher, frequency_analysis_caesar
from .affine import affine_cipher, frequency_analysis_affine, mod_inverse
from .substitute import substitution_cipher, frequency_analysis_substitution
from .languages import (
    ALPHABETS,
    FREQ_TABLES,
    get_alphabet,
    get_freq_table,
    list_languages,
)
from .auto_detect import detect_language, detect_and_decrypt

__all__ = [
    # Caesar
    "cesar_cipher",
    "frequency_analysis_caesar",
    # Affine
    "affine_cipher",
    "frequency_analysis_affine",
    "mod_inverse",
    # Substitution
    "substitution_cipher",
    "frequency_analysis_substitution",
    # Languages
    "ALPHABETS",
    "FREQ_TABLES",
    "get_alphabet",
    "get_freq_table",
    "list_languages",
    # Auto-detection
    "detect_language",
    "detect_and_decrypt",
]
