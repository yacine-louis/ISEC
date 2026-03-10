"""
src/__init__.py
Public API for the ISEC cipher library.
"""

from .cesar import cesar_cipher, crack_caesar_frequency
from .affine import affine_cipher, crack_affine_frequency
from .substitute import substitution_cipher, crack_substitution_frequency

__all__ = [
    "cesar_cipher",
    "crack_caesar_frequency",
    "affine_cipher",
    "crack_affine_frequency",
    "substitution_cipher",
    "crack_substitution_frequency",
]
