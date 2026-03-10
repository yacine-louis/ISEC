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



# -*- coding: utf-8 -*-
"""Functional version of the substitution cipher breaker.

This module replaces the class-based implementation from ``test.py`` with a set
of standalone functions.  The public API is intentionally simple:

* ``load_quadgrams(path)`` returns a dictionary containing the language data.
* ``generate_quadgrams(corpus_fh, quadgram_fh, alphabet)`` creates a quadgram
  file from a text corpus.
* ``decode(text, key, alphabet)`` / ``encode(text, key, alphabet)`` perform
  the substitution transform.
* ``calc_fitness(quadgram_data, text)`` and ``calc_fitness_file`` score texts.
* ``break_cipher(ciphertext, quadgram_data, max_rounds, consolidate)`` attempts
  to crack a substitution cipher using hill climbing.

Internally the data dictionary uses the same fields that were stored on the
``Breaker`` object in the original implementation, but there are no longer any
custom classes.  Results and info are returned as plain dictionaries.
"""



# ---------------------------------------------------------------------------
# helper utilities
# ---------------------------------------------------------------------------

def check_alphabet(alphabet=None):
    """Validate and normalise an alphabet string.

    ``alphabet`` is converted to lower case and a ``ValueError`` is raised if
    the characters are not unique.  If ``None`` is passed the default Arabic
    alphabet from the original module is returned.
    """
    if alphabet is None:
        alphabet = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
    alphabet = alphabet.lower()
    if len(set(alphabet)) != len(alphabet):
        raise ValueError("Alphabet must contain unique characters")
    return alphabet


def _file_iterator(file_fh, alphabet):
    trans = {val: key for key, val in enumerate(alphabet.lower())}
    for line in file_fh:
        line = line.lower()
        for char in line:
            val = trans.get(char)
            if val is not None:
                yield val


def _text_iterator(txt, alphabet):
    trans = {val: key for key, val in enumerate(alphabet.lower())}
    for char in txt.lower():
        val = trans.get(char)
        if val is not None:
            yield val


def decode(text, key_str, alphabet=None):
    """Decode ``text`` using ``key_str`` and ``alphabet`` (substitution).

    This mirrors the behaviour of ``Key.decode`` from the original module.
    """
    alphabet = check_alphabet(alphabet)
    key = key_str.lower()
    if len(key) != len(alphabet) or sorted(key) != sorted(alphabet):
        raise ValueError("Key must be a permutation of the alphabet")
    result = ""
    for char in text:
        lower_char = char.lower()
        if lower_char in key:
            new_char = alphabet[key.index(lower_char)]
            if char.isupper():
                new_char = new_char.upper()
            result += new_char
        else:
            result += char
    return result


def encode(text, key_str, alphabet=None):
    """Encode ``text`` using the supplied key/alphabet (reverse of ``decode``).
    """
    alphabet = check_alphabet(alphabet)
    key = key_str.lower()
    if len(key) != len(alphabet) or sorted(key) != sorted(alphabet):
        raise ValueError("Key must be a permutation of the alphabet")
    result = ""
    for char in text:
        lower_char = char.lower()
        if lower_char in alphabet:
            new_char = key[alphabet.index(lower_char)]
            if char.isupper():
                new_char = new_char.upper()
            result += new_char
        else:
            result += char
    return result


# ---------------------------------------------------------------------------
# quadgram loading / statistics
# ---------------------------------------------------------------------------

def load_quadgrams(quadgram_file_path):
    """Load a quadgram JSON file and return a dictionary of derived values.

    The returned mapping contains the keys ``n``, ``alphabet``, ``alphabet_len``,
    ``quadgrams``, ``mask`` and ``info``.  ``info`` itself is a dict with the
    same fields that were exposed by the original ``BreakerInfo`` class.
    """
    with open(quadgram_file_path, 'r', encoding='utf-8') as fh:
        obj = json.load(fh)

    if obj:
        first_key = next(iter(obj.keys()))
        n = len(first_key)
        all_chars = set()
        for gram in obj.keys():
            for ch in gram:
                all_chars.add(ch.lower())
        alphabet = ''.join(sorted(all_chars))
    else:
        n = 4
        alphabet = "abcdefghijklmnopqrstuvwxyz"
    alphabet_len = len(alphabet)

    # convert dict to list representation and normalise exactly as in the class
    ngrams = [0] * (32 ** n)
    for gram, count in obj.items():
        if len(gram) != n:
            continue
        idx = 0
        for ch in gram.lower():
            if ch in alphabet:
                idx = (idx << 5) + alphabet.index(ch)
            else:
                break
        else:
            ngrams[idx] = count

    gram_sum = sum(ngrams)
    gram_min = min((val for val in ngrams if val), default=1)
    offset = math.log(gram_min / 10 / gram_sum)

    norm = 0
    for idx, val in enumerate(ngrams):
        if val:
            prop = val / gram_sum
            new_val = math.log(prop) - offset
            ngrams[idx] = new_val
            norm += prop * new_val

    for idx, val in enumerate(ngrams):
        if val:
            ngrams[idx] = round(val / norm * 1000)

    mask = (1 << (5 * (n - 1))) - 1

    # determine most frequent quadgram for info
    max_idx = ngrams.index(max(ngrams))
    max_val = ngrams[max_idx]
    max_chars = []
    index = max_idx
    for _ in range(n):
        max_chars = [alphabet[index & 0x1F]] + max_chars
        index >>= 5
    most_frequent = ''.join(max_chars)

    info = {
        'alphabet': alphabet,
        'nbr_quadgrams': gram_sum,
        'most_frequent_quadgram': most_frequent,
        'average_fitness': sum(ngrams) / len(ngrams),
        'max_fitness': max_val,
    }

    return {
        'n': n,
        'alphabet': alphabet,
        'alphabet_len': alphabet_len,
        'quadgrams': ngrams,
        'mask': mask,
        'info': info,
    }


def generate_quadgrams(corpus_fh, quadgram_fh, alphabet=None):
    """Create a quadgram file from a text corpus.

    The implementation is copied verbatim from the static method of the
    original :class:`Breaker` class but rewritten as a standalone function.
    """
    alphabet = check_alphabet(alphabet)
    if len(alphabet) > 32:
        raise ValueError("Alphabet must have less or equal than 32 characters")
    iterator = _file_iterator(corpus_fh, alphabet)
    try:
        quadgram_val = next(iterator)
        quadgram_val = (quadgram_val << 5) + next(iterator)
        quadgram_val = (quadgram_val << 5) + next(iterator)
    except StopIteration:
        raise ValueError("corpus too short")
    quadgrams = [0 for _ in range(32 ** 4)]
    for numerical_char in iterator:
        quadgram_val = ((quadgram_val & 0x7FFF) << 5) + numerical_char
        quadgrams[quadgram_val] += 1

    quadgram_sum = sum(quadgrams)
    quadgram_min = min((val for val in quadgrams if val), default=1)
    offset = math.log(quadgram_min / 10 / quadgram_sum)

    norm = 0
    for idx, val in enumerate(quadgrams):
        if val:
            prop = val / quadgram_sum
            new_val = math.log(prop) - offset
            quadgrams[idx] = new_val
            norm += prop * new_val

    for idx, _ in enumerate(quadgrams):
        quadgrams[idx] = round(quadgrams[idx] / norm * 1000)

    max_idx = quadgrams.index(max(quadgrams))
    max_val = quadgrams[max_idx]
    max_chars = []
    index = max_idx
    for _ in range(4):
        max_chars = [alphabet[index & 0x1F]] + max_chars
        index >>= 5

    json.dump(
        {
            "alphabet": alphabet,
            "nbr_quadgrams": quadgram_sum,
            "most_frequent_quadgram": "".join(max_chars),
            "max_fitness": max_val,
            "average_fitness": sum(quadgrams) / (len(alphabet) ** 4),
            "quadgrams": quadgrams,
        },
        quadgram_fh,
        indent=0,
    )


# ---------------------------------------------------------------------------
# fitness and breaking routines
# ---------------------------------------------------------------------------

def _calc_fitness(iterator, quadgram_data):
    n = quadgram_data['n']
    mask = quadgram_data['mask']
    quadgrams = quadgram_data['quadgrams']
    try:
        quadgram_val = 0
        for _ in range(n):
            quadgram_val = (quadgram_val << 5) + next(iterator)
    except StopIteration:
        raise ValueError(f"More than {n - 1} characters from the given alphabet are required")

    fitness = 0
    nbr_quadgrams = 0
    fitness += quadgrams[quadgram_val]
    nbr_quadgrams += 1
    for numerical_char in iterator:
        quadgram_val = ((quadgram_val & mask) << 5) + numerical_char
        fitness += quadgrams[quadgram_val]
        nbr_quadgrams += 1
    if nbr_quadgrams == 0:
        raise ValueError(f"More than {n - 1} characters from the given alphabet are required")
    return fitness / nbr_quadgrams / 10


def calc_fitness_file(quadgram_data, cleartext_fh=sys.stdin):
    return _calc_fitness(_file_iterator(cleartext_fh, quadgram_data['alphabet']), quadgram_data)


def calc_fitness(quadgram_data, txt):
    return _calc_fitness(_text_iterator(txt, quadgram_data['alphabet']), quadgram_data)


def _hill_climbing(key, cipher_bin, char_positions, quadgram_data):
    quadgram = quadgram_data['quadgrams']
    n = quadgram_data['n']
    mask = quadgram_data['mask']
    key_len = quadgram_data['alphabet_len']

    plaintext = [key.index(idx) for idx in cipher_bin]
    nbr_keys = 0
    max_fitness = 0
    better_key = True
    while better_key:
        better_key = False
        for idx1 in range(key_len - 1):
            for idx2 in range(idx1 + 1, key_len):
                ch1 = key[idx1]
                ch2 = key[idx2]
                for idx in char_positions[ch1]:
                    plaintext[idx] = idx2
                for idx in char_positions[ch2]:
                    plaintext[idx] = idx1
                nbr_keys += 1
                tmp_fitness = 0
                quad_idx = 0
                for i in range(n - 1):
                    quad_idx = (quad_idx << 5) + plaintext[i]
                for char in plaintext[n - 1:]:
                    quad_idx = ((quad_idx & mask) << 5) + char
                    tmp_fitness += quadgram[quad_idx]
                if tmp_fitness > max_fitness:
                    max_fitness = tmp_fitness
                    better_key = True
                    key[idx1] = ch2
                    key[idx2] = ch1
                else:
                    for idx in char_positions[ch1]:
                        plaintext[idx] = idx1
                    for idx in char_positions[ch2]:
                        plaintext[idx] = idx2
    return max_fitness, nbr_keys


def break_cipher(ciphertext, quadgram_data, max_rounds=10000, consolidate=3):
    if not (1 <= max_rounds <= 10000):
        raise ValueError("maximum number of rounds not in the valid range 1..10000")
    if not (1 <= consolidate <= 30):
        raise ValueError("consolidate parameter out of valid range 1..30")
    start_time = time.time()
    nbr_keys = 0
    cipher_bin = [char for char in _text_iterator(ciphertext, quadgram_data['alphabet'])]
    n = quadgram_data['n']
    if len(cipher_bin) < n:
        raise ValueError(f"ciphertext is too short, needs at least {n} characters")

    char_positions = []
    for idx in range(quadgram_data['alphabet_len']):
        char_positions.append([i for i, x in enumerate(cipher_bin) if x == idx])

    key_len = quadgram_data['alphabet_len']
    local_maximum = 0
    local_maximum_hit = 1
    key = [idx for idx in range(key_len)]
    best_key = key.copy()
    for round_cntr in range(max_rounds):
        random.shuffle(key)
        fitness, tmp_keys = _hill_climbing(key, cipher_bin, char_positions, quadgram_data)
        nbr_keys += tmp_keys
        if fitness > local_maximum:
            local_maximum = fitness
            local_maximum_hit = 1
            best_key = key.copy()
        elif fitness == local_maximum:
            local_maximum_hit += 1
            if local_maximum_hit == consolidate:
                break
    key_str = ''.join([quadgram_data['alphabet'][x] for x in best_key])
    plaintext = decode(ciphertext, key_str, alphabet=quadgram_data['alphabet'])
    seconds = time.time() - start_time
    return {
        'ciphertext': ciphertext,
        'plaintext': plaintext,
        'key': key_str,
        'alphabet': quadgram_data['alphabet'],
        'fitness': local_maximum / (len(cipher_bin) - n + 1) / 10,
        'nbr_keys': nbr_keys,
        'nbr_rounds': round_cntr,
        'keys_per_second': round(nbr_keys / seconds, 3),
        'seconds': seconds,
    }


def crack_substitution_frequency(ciphertext, alphabet, quadgram_json_path, max_rounds=10000, consolidate=3):
    """
    Crack a substitution cipher using hill-climbing with quadgram frequencies.

    This uses the same approach as break_cipher, leveraging statistical
    frequencies of 4-grams for scoring during hill-climbing optimization.

    Args:
        ciphertext: The encrypted text.
        alphabet: The alphabet used (must match the quadgram file).
        quadgram_json_path: Path to a JSON file with quadgram data.
        max_rounds: Maximum number of hill-climbing rounds.
        consolidate: Number of rounds without improvement to stop.

    Returns:
        (plaintext, key_str) - the decrypted text and the key used.
    """
    quadgram_data = load_quadgrams(quadgram_json_path)
    if quadgram_data['alphabet'] != check_alphabet(alphabet):
        raise ValueError("Alphabet must match the quadgram file's alphabet")
    
    result = break_cipher(ciphertext, quadgram_data, max_rounds, consolidate)
    return result['plaintext'], result['key']
