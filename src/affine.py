# affine encrypts each letter using a mathematical function E(x)=(ax+b) mod m
# x → position of the letter in the alphabet
# a → multiplicative key
# b → additive key (shift)
# m → size of alphabet

def mod_inverse(a, m):
    """
    compute modular inverse of a under modulo m.
    Returns None if inverse does not exist.
    """
    try:
        return pow(a, -1, m)
    except ValueError:
        return None


def affine_cipher(text, alphabet, a, b, mode="encrypt"):
    """
    :param text: input text
    :param alphabet: custom alphabet string
    :param a: multiplicative key
    :param b: additive key
    :param mode: "encrypt" or "decrypt"
    :return: encrypted/decrypted text
    """

    result = ""
    alphabet = alphabet.lower()
    m = len(alphabet)
    a_inv = mod_inverse(a, m)

    # Check if a is valid
    if a_inv is None:
        raise ValueError("Key 'a' is not coprime with alphabet size!")
    
    for char in text:
        lower_char = char.lower()

        if lower_char in alphabet:
            x = alphabet.index(lower_char)

            if mode == "encrypt":
                new_index = (a * x + b) % m
            else:
                new_index = (a_inv * (x - b)) % m

            new_char = alphabet[new_index]

            # preserve case
            if char.isupper():
                new_char = new_char.upper()

            result += new_char
        else:
            result += char

    return result

# import json
# from collections import Counter

# def crack_affine_frequency(ciphertext, alphabet, unigram_json_path, top_n=6):

#     alphabet = alphabet.lower()
#     m = len(alphabet)

#     # -------------------------
#     # Load language frequencies
#     # -------------------------
#     with open(unigram_json_path, "r", encoding="utf8") as f:
#         freq_table = json.load(f)

#     top_lang_letters = sorted(
#         freq_table,
#         key=freq_table.get,
#         reverse=True
#     )[:top_n]

#     # -------------------------
#     # Ciphertext frequencies
#     # -------------------------
#     letters = [c.lower() for c in ciphertext if c.lower() in alphabet]

#     cipher_freq = Counter(letters)

#     top_cipher_letters = [
#         l for l, _ in cipher_freq.most_common(top_n)
#     ]

#     candidates = []

#     # -------------------------
#     # Try pairs
#     # -------------------------
#     for c1 in top_cipher_letters:
#         for c2 in top_cipher_letters:

#             if c1 == c2:
#                 continue

#             for p1 in top_lang_letters:
#                 for p2 in top_lang_letters:

#                     if p1 == p2:
#                         continue

#                     y1 = alphabet.index(c1)
#                     y2 = alphabet.index(c2)

#                     x1 = alphabet.index(p1)
#                     x2 = alphabet.index(p2)

#                     denom = (x1 - x2) % m
#                     inv = mod_inverse(denom, m)

#                     if inv is None:
#                         continue

#                     a = ((y1 - y2) * inv) % m
#                     b = (y1 - a * x1) % m

#                     candidates.append((a, b))

#     # -------------------------
#     # Test candidates
#     # -------------------------
#     best = None
#     best_score = -1
#     best_plain = ciphertext

#     for a, b in candidates:

#         try:
#             plain = affine_cipher(ciphertext, alphabet, a, b, mode="decrypt")
#         except:
#             continue

#         score = sum(1 for c in plain if c in " etaoin")

#         if score > best_score:
#             best_score = score
#             best = (a, b)
#             best_plain = plain

#     print("Candidate keys:", len(candidates))
#     print("Best key:", best)

#     return best_plain, best

# alphabet = "abcdefghijklmnopqrstuvwxyz"

# plaintext = """
# affine cipher is a classical substitution cipher used in cryptography
# """

# cipher = affine_cipher(plaintext, alphabet, a=5, b=8)

# print("Ciphertext:\n", cipher)

# plaintext, key = crack_affine_frequency(
#     cipher,
#     alphabet,
#     "grams/english_1grams.json"
# )

# print("\nRecovered key:", key)
# print("\nDecrypted:\n", plaintext)




import json
import math
from collections import Counter

# -------------------------
# Scoring
# -------------------------

def extract_ngrams(text, alphabet, n):
    """
    Extract overlapping n-grams from alphabetic characters only.
    Non-alphabet characters (spaces, punctuation) are ignored,
    so bigrams span across word boundaries.

    Example (n=2): "the cat" -> ["th","he","ec","ca","at"]
    """
    clean = [c for c in text.lower() if c in alphabet]
    return ["".join(clean[i:i + n]) for i in range(len(clean) - n + 1)]


def log_likelihood_score(text, freq_table, alphabet, n):
    """
    Score decrypted text by how well its n-gram frequencies
    match the expected language distribution.
    Higher = better. Works for any alphabet and any n-gram size.
    """
    ngrams = extract_ngrams(text, alphabet, n)
    if not ngrams:
        return float('-inf')

    counts = Counter(ngrams)
    score = 0.0

    for gram, count in counts.items():
        prob = freq_table.get(gram, 1e-10)  # floor avoids log(0) for unseen n-grams
        score += count * math.log(prob)

    return score

# -------------------------
# Cracker
# -------------------------

def crack_affine_frequency(ciphertext, alphabet, unigram_json_path, n=1, top_n=6):
    """
    Crack an affine cipher using frequency analysis.

    Args:
        ciphertext:         The encrypted text.
        alphabet:           The alphabet used (e.g. 'abcdefghijklmnopqrstuvwxyz'
                            or Arabic letters string).
        unigram_json_path:  Path to a JSON file mapping each n-gram to its
                            frequency/probability in the target language.
        n:                  N-gram size for scoring:
                              1 = unigram (default)
                              2 = bigram
                              3 = trigram
                            The freq table keys must match this size.
        top_n:              How many top-frequency letters to use when
                            generating candidate keys.

    Returns:
        (plaintext, (a, b))  — best decryption and its key.
    """
    alphabet = alphabet.lower()
    m = len(alphabet)

    # -------------------------
    # Load language frequencies
    # -------------------------
    with open(unigram_json_path, "r", encoding="utf8") as f:
        freq_table = json.load(f)

    print(f"Loaded frequency table ({len(freq_table)} entries, n={n})")

    # -------------------------
    # Candidate generation always uses unigrams.
    # If n > 1, derive unigram freqs by marginalising the n-gram table.
    # -------------------------
    if n == 1:
        unigram_table = freq_table
    else:
        unigram_table = Counter()
        for gram, prob in freq_table.items():
            unigram_table[gram[0]] += prob
        total = sum(unigram_table.values())
        unigram_table = {k: v / total for k, v in unigram_table.items()}

    top_lang_letters = sorted(unigram_table, key=unigram_table.get, reverse=True)[:top_n]

    # -------------------------
    # Ciphertext letter frequencies
    # -------------------------
    letters = [c.lower() for c in ciphertext if c.lower() in alphabet]
    cipher_freq = Counter(letters)
    top_cipher_letters = [l for l, _ in cipher_freq.most_common(top_n)]

    # -------------------------
    # Generate + score candidates
    # (deduplicated: each (a, b) pair is decrypted exactly once)
    # -------------------------
    scored = {}

    for c1 in top_cipher_letters:
        for c2 in top_cipher_letters:
            if c1 == c2:
                continue

            for p1 in top_lang_letters:
                for p2 in top_lang_letters:
                    if p1 == p2:
                        continue

                    y1 = alphabet.index(c1)
                    y2 = alphabet.index(c2)
                    x1 = alphabet.index(p1)
                    x2 = alphabet.index(p2)

                    denom = (x1 - x2) % m
                    inv = mod_inverse(denom, m)
                    if inv is None:
                        continue

                    a = ((y1 - y2) * inv) % m
                    b = (y1 - a * x1) % m

                    if math.gcd(a, m) != 1:
                        continue
                    if (a, b) in scored:
                        continue

                    try:
                        plain = affine_cipher(ciphertext, alphabet, a, b, mode="decrypt")
                    except ValueError:
                        continue

                    scored[(a, b)] = (
                        log_likelihood_score(plain.lower(), freq_table, alphabet, n=n),
                        plain
                    )

    if not scored:
        print("No valid candidates found.")
        return ciphertext, None

    # -------------------------
    # Pick best key
    # -------------------------
    best = max(scored, key=lambda k: scored[k][0])
    best_score, best_plain = scored[best]

    print(f"Unique candidates evaluated : {len(scored)}")
    print(f"Best key                    : a={best[0]}, b={best[1]}")
    print(f"Log-likelihood score        : {best_score:.2f}")

    return best_plain, best


# -------------------------
# Example usage
# -------------------------

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

sample = (
    """
It can also be a fun way to surprise. You might choose to share a random sentence on social media just to see what type of reaction it garners from others. It's an unexpected move that might create more conversation than a typical post or tweet.
These are just a few ways that one might use the random sentence generator for their benefit. If you're not sure if it will help in the way you want, the best course of action is to try it and see. Have several random sentences generated and you'll soon be able to see if they can help with your project.
"""
)

a_key, b_key = 11, 17
encrypted = affine_cipher(sample, ALPHABET, a_key, b_key, mode="encrypt")
print(f"Encrypted : {encrypted}\n")

# Pass n to select scoring mode — just make sure the JSON keys match:
#   n=1  ->  keys like "e", "t", "a"       (english_1grams.json)
#   n=2  ->  keys like "th", "he", "in"    (english_2grams.json)
#   n=3  ->  keys like "the", "and", "ing" (english_3grams.json)

decrypted, key = crack_affine_frequency(encrypted, ALPHABET, "grams/english_2grams.json", n=2)
print(f"Found key : {key}")
print(f"\nDecrypted : {decrypted}")
