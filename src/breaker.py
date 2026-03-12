# -*- coding: utf-8 -*-
"""This module provides support for breaking substitution ciphers using n-grams.

This includes loading n-gram frequency data (1-gram through 4-gram),
scoring a plaintext and breaking substitution ciphers via hill climbing.
Supports both English and Arabic (or any alphabet ≤ 32 characters).
"""

import math
import json
import sys
import random
import time
import os


class BreakerInfo(object):
    """Class representing various information of the n-grams for a given language

    :ivar int n: the order of the n-gram (1, 2, 3, or 4)
    :ivar str alphabet: text representation of the alphabet
    :ivar int nbr_ngrams: the total number of n-gram occurrences in the corpus
    :ivar str most_frequent_ngram: the most often occurring n-gram
    :ivar float average_fitness: the expected fitness of a text if all characters are
        generated randomly with the same probability.
    :ivar float max_fitness: the fitness for the most frequent n-gram
    """

    def __init__(
        self,
        n=4,
        alphabet=None,
        nbr_ngrams=None,
        most_frequent_ngram=None,
        average_fitness=None,
        max_fitness=None,
    ):
        self.n = n
        self.alphabet = alphabet
        self.nbr_ngrams = nbr_ngrams
        self.most_frequent_ngram = most_frequent_ngram
        self.average_fitness = average_fitness
        self.max_fitness = max_fitness


class BreakerResult(object):
    """Class representing the result for breaking a substitution cipher

    :ivar str ciphertext: the original ciphertext
    :ivar str plaintext: the resulting plaintext using the found key
    :ivar str key: the best key found by the breaker
    :ivar str alphabet: the alphabet used to break the cipher
    :ivar float fitness: the fitness of the resulting plaintext
    :ivar int nbr_keys: the number of keys tried by the breaker
    :ivar nbr_rounds: the number of hill climbings performed
    :ivar float keys_per_second: the number of keys tried per second
    :ivar float seconds: the time in seconds used to break the cipher
    """

    def __init__(
        self,
        ciphertext=None,
        plaintext=None,
        key=None,
        alphabet=None,
        fitness=0,
        nbr_keys=0,
        nbr_rounds=0,
        keys_per_second=0,
        seconds=0,
    ):
        self.ciphertext = ciphertext
        self.plaintext = plaintext
        self.key = key
        self.alphabet = alphabet
        self.fitness = fitness
        self.nbr_keys = nbr_keys
        self.nbr_rounds = nbr_rounds
        self.keys_per_second = keys_per_second
        self.seconds = seconds

    def __str__(self):
        return "key = {}".format(self.key)


class Breaker(object):
    """Class to break substitution ciphers using n-gram frequency analysis.

    Supports 1-gram through 4-gram data loaded from dict-format JSON files
    (``{"th": 66858, "he": 63169, ...}``).  Works with any alphabet up to
    32 characters, including English and Arabic.

    :ivar info: a :class:`BreakerInfo` object
    :ivar key: a :class:`Key`-compatible string found when breaking a cipher
    :param ngram_path: path to a JSON file with n-gram counts in dict format.
    """

    def __init__(self, ngram_path):
        """Load n-gram data from a dict-format JSON file.

        The JSON file must be a mapping of n-gram strings to their counts,
        e.g. ``{"e": 278298, "t": 201219}`` for 1-grams or
        ``{"th": 66858, "he": 63169}`` for 2-grams.
        """
        with open(ngram_path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)

        if not raw:
            raise ValueError("n-gram JSON file is empty")

        # auto-detect n from the first key
        first_key = next(iter(raw))
        self._n = len(first_key)

        # auto-detect alphabet from all keys
        all_chars = set()
        for gram in raw:
            for ch in gram:
                all_chars.add(ch.lower())
        self._alphabet = "".join(sorted(all_chars))
        self._alphabet_len = len(self._alphabet)

        if self._alphabet_len > 32:
            raise ValueError("Alphabet must have 32 or fewer characters")

        # build the scored n-gram list using the same normalisation as the
        # original quadgram-based implementation
        size = 32 ** self._n
        ngrams = [0] * size

        for gram, count in raw.items():
            if len(gram) != self._n:
                continue
            idx = 0
            valid = True
            for ch in gram.lower():
                pos = self._alphabet.find(ch)
                if pos == -1:
                    valid = False
                    break
                idx = (idx << 5) + pos
            if valid:
                ngrams[idx] = count

        gram_sum = sum(ngrams)
        gram_min = min((v for v in ngrams if v), default=1)
        offset = math.log(gram_min / 10 / gram_sum)

        norm = 0
        for idx, val in enumerate(ngrams):
            if val:
                prop = val / gram_sum
                new_val = math.log(prop) - offset
                ngrams[idx] = new_val
                norm += prop * new_val

        if norm == 0:
            norm = 1  # avoid division by zero for degenerate data

        for idx in range(len(ngrams)):
            if ngrams[idx]:
                ngrams[idx] = round(ngrams[idx] / norm * 1000)

        self._ngrams = ngrams
        self._mask = (1 << (5 * (self._n - 1))) - 1

        # determine the most frequent n-gram
        max_idx = ngrams.index(max(ngrams))
        max_val = ngrams[max_idx]
        max_chars = []
        index = max_idx
        for _ in range(self._n):
            max_chars = [self._alphabet[index & 0x1F]] + max_chars
            index >>= 5
        most_frequent = "".join(max_chars)

        self.info = BreakerInfo(
            n=self._n,
            alphabet=self._alphabet,
            nbr_ngrams=gram_sum,
            most_frequent_ngram=most_frequent,
            average_fitness=sum(ngrams) / max(len(ngrams), 1) / 10,
            max_fitness=max_val / 10,
        )
        self.key = None

    # -----------------------------------------------------------------------
    # iterators
    # -----------------------------------------------------------------------

    @staticmethod
    def _text_iterator(txt, alphabet):
        """Yield numeric indices for each character of *txt* that is in *alphabet*."""
        trans = {val: key for key, val in enumerate(alphabet.lower())}
        for char in txt.lower():
            val = trans.get(char)
            if val is not None:
                yield val

    @staticmethod
    def _file_iterator(file_fh, alphabet):
        """Yield numeric indices for each character in file *file_fh* that is in *alphabet*."""
        trans = {val: key for key, val in enumerate(alphabet.lower())}
        for line in file_fh:
            line = line.lower()
            for char in line:
                val = trans.get(char)
                if val is not None:
                    yield val

    # -----------------------------------------------------------------------
    # fitness
    # -----------------------------------------------------------------------

    def _calc_fitness(self, iterator):
        """Calculate the fitness of text provided by *iterator*."""
        n = self._n
        mask = self._mask
        ngrams = self._ngrams

        try:
            ngram_val = 0
            for _ in range(n):
                ngram_val = (ngram_val << 5) + next(iterator)
        except StopIteration:
            raise ValueError(
                f"More than {n - 1} characters from the given alphabet are required"
            )

        fitness = ngrams[ngram_val]
        nbr = 1
        for numerical_char in iterator:
            ngram_val = ((ngram_val & mask) << 5) + numerical_char
            fitness += ngrams[ngram_val]
            nbr += 1

        if nbr == 0:
            raise ValueError(
                f"More than {n - 1} characters from the given alphabet are required"
            )
        return fitness / nbr / 10

    def calc_fitness(self, txt):
        """Calculate fitness for a text string."""
        return self._calc_fitness(Breaker._text_iterator(txt, self._alphabet))

    def calc_fitness_file(self, cleartext_fh=sys.stdin):
        """Calculate fitness from file contents."""
        return self._calc_fitness(Breaker._file_iterator(cleartext_fh, self._alphabet))

    # -----------------------------------------------------------------------
    # decode helper
    # -----------------------------------------------------------------------

    def _decode(self, text, key_str):
        """Decode *text* using substitution key *key_str*."""
        key = key_str.lower()
        alphabet = self._alphabet
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

    # -----------------------------------------------------------------------
    # hill climbing
    # -----------------------------------------------------------------------

    def _hill_climbing(self, key, cipher_bin, char_positions):
        """Basic hill climbing: swap character pairs, keep improvements."""
        plaintext = [key.index(idx) for idx in cipher_bin]
        ngrams = self._ngrams
        n = self._n
        mask = self._mask
        key_len = self._alphabet_len
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

                    # compute fitness with dynamic n
                    tmp_fitness = 0
                    quad_idx = 0
                    for i in range(n - 1):
                        quad_idx = (quad_idx << 5) + plaintext[i]
                    for char in plaintext[n - 1:]:
                        quad_idx = ((quad_idx & mask) << 5) + char
                        tmp_fitness += ngrams[quad_idx]

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

    # -----------------------------------------------------------------------
    # break_cipher
    # -----------------------------------------------------------------------

    def break_cipher(self, ciphertext, max_rounds=10000, consolidate=3):
        """Break a substitution cipher.

        :param str ciphertext: the ciphertext to break
        :param int max_rounds: maximum number of hill climbing rounds (1–10000)
        :param int consolidate: times the best local maximum must be hit before
            accepting it as the solution (1–30)
        :return: a :class:`BreakerResult`
        """
        if not (1 <= max_rounds <= 10000):
            raise ValueError("maximum number of rounds not in the valid range 1..10000")
        if not (1 <= consolidate <= 30):
            raise ValueError("consolidate parameter out of valid range 1..30")

        start_time = time.time()
        nbr_keys = 0
        n = self._n

        cipher_bin = list(Breaker._text_iterator(ciphertext, self._alphabet))
        if len(cipher_bin) < n:
            raise ValueError(f"ciphertext is too short, needs at least {n} characters")

        char_positions = []
        for idx in range(self._alphabet_len):
            char_positions.append([i for i, x in enumerate(cipher_bin) if x == idx])

        key_len = self._alphabet_len
        local_maximum, local_maximum_hit = 0, 1
        key = list(range(key_len))
        best_key = key.copy()
        round_cntr = 0

        for round_cntr in range(max_rounds):
            random.shuffle(key)
            fitness, tmp_nbr_keys = self._hill_climbing(key, cipher_bin, char_positions)
            nbr_keys += tmp_nbr_keys
            if fitness > local_maximum:
                local_maximum = fitness
                local_maximum_hit = 1
                best_key = key.copy()
            elif fitness == local_maximum:
                local_maximum_hit += 1
                if local_maximum_hit == consolidate:
                    break

        key_str = "".join([self._alphabet[x] for x in best_key])
        self.key = key_str
        seconds = time.time() - start_time

        return BreakerResult(
            ciphertext=ciphertext,
            plaintext=self._decode(ciphertext, key_str),
            key=key_str,
            alphabet=self._alphabet,
            fitness=local_maximum / max(len(cipher_bin) - n + 1, 1) / 10,
            nbr_keys=nbr_keys,
            nbr_rounds=round_cntr,
            keys_per_second=round(nbr_keys / seconds, 3) if seconds > 0 else 0,
            seconds=seconds,
        )


# ---------------------------------------------------------------------------
# Example: crack substitution ciphers using 1–4 gram data
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Resolve paths relative to this file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    grams_dir = os.path.join(base_dir, "grams")

    # ---- simple substitution helper (same as substitute.py) ----
    def _substitute(text, alphabet, key):
        """Encrypt text using a substitution cipher."""
        result = ""
        for char in text:
            lc = char.lower()
            if lc in alphabet:
                new = key[alphabet.index(lc)]
                result += new.upper() if char.isupper() else new
            else:
                result += char
        return result

    # ===================================================================
    #  English examples
    # ===================================================================
    eng_alphabet = "abcdefghijklmnopqrstuvwxyz"
    eng_key = "qwertyuiopasdfghjklzxcvbnm"
    eng_plaintext = "the quick brown fox jumps over the lazy dog"
    eng_ciphertext = _substitute(eng_plaintext, eng_alphabet, eng_key)

    print("=" * 60)
    print("ENGLISH EXAMPLES")
    print("=" * 60)
    print(f"Plaintext : {eng_plaintext}")
    print(f"Ciphertext: {eng_ciphertext}")
    print()

    for n in range(1, 5):
        gram_file = os.path.join(grams_dir, f"english_{n}grams.json")
        if not os.path.exists(gram_file):
            print(f"  [{n}-gram] file not found, skipping: {gram_file}")
            continue
        breaker = Breaker(gram_file)
        print(f"  [{n}-gram] alphabet={breaker.info.alphabet[:10]}... "
              f"most_frequent={breaker.info.most_frequent_ngram}")
        start = time.time()
        result = breaker.break_cipher(eng_ciphertext, max_rounds=1000, consolidate=3)
        elapsed = time.time() - start
        print(f"           plaintext = {result.plaintext}")
        print(f"           key       = {result.key}")
        print(f"           fitness   = {result.fitness:.2f}")
        print(f"           time      = {elapsed:.3f}s")
        print()

    # ===================================================================
    #  Arabic examples
    # ===================================================================
    arabic_alphabet = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
    shift = 3
    arabic_key = arabic_alphabet[shift:] + arabic_alphabet[:shift]
    arabic_plaintext = "النص العربي يستخدم هنا لاختبار خوارزمية التشفير بالاستبدال حيث يتم تغيير كل حرف بحرف آخر من الأبجدية مع الحفاظ على ترتيب النص."
    arabic_ciphertext = _substitute(arabic_plaintext, arabic_alphabet, arabic_key)

    print("=" * 60)
    print("ARABIC EXAMPLES")
    print("=" * 60)
    print(f"Plaintext : {arabic_plaintext}")
    print(f"Ciphertext: {arabic_ciphertext}")
    print()

    for n in range(1, 5):
        gram_file = os.path.join(grams_dir, f"arabic_{n}grams.json")
        if not os.path.exists(gram_file):
            print(f"  [{n}-gram] file not found, skipping: {gram_file}")
            continue
        breaker = Breaker(gram_file)
        print(f"  [{n}-gram] most_frequent={breaker.info.most_frequent_ngram}")
        start = time.time()
        result = breaker.break_cipher(arabic_ciphertext, max_rounds=1000, consolidate=3)
        elapsed = time.time() - start
        print(f"           plaintext = {result.plaintext}")
        print(f"           key       = {result.key}")
        print(f"           fitness   = {result.fitness:.2f}")
        print(f"           time      = {elapsed:.3f}s")
        print()
