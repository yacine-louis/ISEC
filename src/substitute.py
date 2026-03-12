# substitution cipher replaces each letter with a corresponding letter from a shuffled key alphabet
# each letter in the alphabet maps 1-to-1 to a letter in the key
# key must be a permutation of the alphabet (same letters, different order)

from collections import Counter
import json
import math
import random
import sys
import time

def substitution_cipher(text, alphabet, key, mode="encrypt"):
    """
    :param text: input text
    :param alphabet: custom alphabet string
    :param key: permutation of the alphabet used as substitution map
    :param mode: "encrypt" or "decrypt"
    :return: encrypted/decrypted text
    """

    alphabet = alphabet.lower()
    key = key.lower()

    # validate key
    if len(key) != len(alphabet):
        raise ValueError("Key length must match alphabet length!")
    if sorted(key) != sorted(alphabet):
        raise ValueError("Key must be a permutation of the alphabet!")

    # swap mapping direction for decryption
    if mode == "encrypt":
        src, dst = alphabet, key
    else:
        src, dst = key, alphabet

    result = ""

    for char in text:
        lower_char = char.lower()

        if lower_char in src:
            new_char = dst[src.index(lower_char)]

            # preserve case
            if char.isupper():
                new_char = new_char.upper()

            result += new_char
        else:
            result += char

    return result

def crack_substitution_frequency(ciphertext, alphabet, ngram_json_path, max_rounds=None, consolidate=None):
    """
    Crack a substitution cipher using hill-climbing with n-gram frequencies.

    Supports 1-gram through 4-gram JSON files in dict format
    (e.g. ``{"th": 66858, "he": 63169, ...}``).
    Works with any alphabet (English, Arabic, etc.).

    Args:
        ciphertext: The encrypted text.
        alphabet: The alphabet used (must match the n-gram file).
        ngram_json_path: Path to a JSON file with n-gram counts.
        max_rounds: Maximum number of hill-climbing rounds.
        consolidate: Number of rounds without improvement to stop.

    Returns:
        (plaintext, key_str) - the decrypted text and the key used.
    """
    from src.breaker import Breaker

    # Accept either a file-like object or a path to the n-gram JSON file
    if hasattr(ngram_json_path, "read"):
        breaker = Breaker(ngram_json_path)
    else:
        with open(ngram_json_path, encoding="utf-8") as fh:
            breaker = Breaker(fh)
    # Auto-tune rounds by text length for better performance
    len_text = len([c for c in ciphertext if c in alphabet])
    default_rounds = max(500, min(3000, len_text // 10))  # Scale: short=fast, long=thorough
    rounds = max_rounds or default_rounds
    cons = consolidate or 3
    result = breaker.break_cipher(ciphertext, rounds, cons)
    return result.plaintext, result.key
