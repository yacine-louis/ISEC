# substitution cipher replaces each letter with a corresponding letter from a shuffled key alphabet
# each letter in the alphabet maps 1-to-1 to a letter in the key
# key must be a permutation of the alphabet (same letters, different order)

from collections import Counter
import json
import math
import random


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



# -------------------------
# Scoring
# -------------------------

def extract_ngrams(text, alphabet, n):
    clean = [c for c in text.lower() if c in alphabet]
    return ["".join(clean[i:i + n]) for i in range(len(clean) - n + 1)]


def log_likelihood_score(text, freq_table, alphabet, n):
    ngrams = extract_ngrams(text, alphabet, n)
    if not ngrams:
        return float('-inf')
    counts = Counter(ngrams)
    return sum(count * math.log(freq_table.get(gram, 1e-10))
               for gram, count in counts.items())


# -------------------------
# Cracker
# -------------------------

def crack_substitution(ciphertext, alphabet, freq_json_path, n=4,
                        restarts=10, max_no_improve=1000):
    """
    Crack a substitution cipher using frequency seeding + hill climbing.

    Args:
        ciphertext:       The encrypted text.
        alphabet:         The alphabet string used for encryption.
        freq_json_path:   Path to a JSON n-gram frequency table.
        n:                N-gram size for scoring.
                          4 (quadgrams) is the recommended default —
                          captures word fragments far better than bi/trigrams.
        restarts:         How many independent hill climbs to run.
                          More restarts = better chance of escaping local optima.
        max_no_improve:   How many consecutive failed swaps before a restart
                          is triggered.

    Returns:
        (plaintext, key)
    """
    alphabet = alphabet.lower()
    alpha_len = len(alphabet)

    with open(freq_json_path, "r", encoding="utf8") as f:
        freq_table = json.load(f)

    print(f"Loaded frequency table ({len(freq_table)} entries, n={n})")

    # -------------------------
    # Derive unigram ranks for frequency seeding
    # (works regardless of n-gram size in the table)
    # -------------------------
    if n == 1:
        unigram_table = freq_table
    else:
        unigram_table = Counter()
        for gram, prob in freq_table.items():
            unigram_table[gram[0]] += prob
        total = sum(unigram_table.values())
        unigram_table = {k: v / total for k, v in unigram_table.items()}

    lang_ranked = sorted(unigram_table, key=unigram_table.get, reverse=True)

    letters = [c.lower() for c in ciphertext if c.lower() in alphabet]
    cipher_ranked = [l for l, _ in Counter(letters).most_common()]

    # seed_key[i] = what alphabet[i] decrypts to
    # cipher_ranked[i] should decrypt to lang_ranked[i]
    seed_decrypt = {}
    for i, c in enumerate(cipher_ranked):
        if i < len(lang_ranked):
            seed_decrypt[c] = lang_ranked[i]

    # Fill unmapped letters randomly
    unmapped = [l for l in alphabet if l not in seed_decrypt.values()]
    random.shuffle(unmapped)
    fill = iter(unmapped)
    for c in alphabet:
        if c not in seed_decrypt:
            seed_decrypt[c] = next(fill)

    # Convert decrypt mapping -> key string
    # substitution_cipher(decrypt): src=key, dst=alphabet
    # so key[alphabet.index(plain)] = cipher  (i.e. inverse of decrypt map)
    def mapping_to_key(decrypt_map):
        inv = {v: k for k, v in decrypt_map.items()}
        return "".join(inv.get(c, c) for c in alphabet)

    def swap_key(key, i, j):
        k = list(key)
        k[i], k[j] = k[j], k[i]
        return "".join(k)

    # Score the full plaintext — precompute once per key
    def score_key(key):
        plain = substitution_cipher(ciphertext, alphabet, key, mode="decrypt")
        return log_likelihood_score(plain.lower(), freq_table, alphabet, n), plain

    best_overall_score = float('-inf')
    best_overall_plain = ciphertext
    best_overall_key = None

    for restart in range(restarts):

        # Restart 0: frequency-seeded key
        # Restart 1+: randomly perturb the best key found so far
        if restart == 0:
            current_key = mapping_to_key(seed_decrypt)
        else:
            key_list = list(best_overall_key)
            indices = random.sample(range(alpha_len), k=random.randint(2, alpha_len // 2))
            vals = [key_list[i] for i in indices]
            random.shuffle(vals)
            for idx, val in zip(indices, vals):
                key_list[idx] = val
            current_key = "".join(key_list)

        current_score, current_plain = score_key(current_key)
        no_improve_count = 0

        # -------------------------
        # Hill climb: greedy — accept the FIRST swap that improves score.
        # Much faster than exhaustive-pass approaches since we move immediately
        # instead of waiting to evaluate all 325 swaps before stepping.
        # -------------------------
        while no_improve_count < max_no_improve:
            i, j = random.sample(range(alpha_len), 2)
            candidate_key = swap_key(current_key, i, j)
            candidate_score, candidate_plain = score_key(candidate_key)

            if candidate_score > current_score:
                current_key = candidate_key
                current_plain = candidate_plain
                current_score = candidate_score
                no_improve_count = 0
            else:
                no_improve_count += 1

        if current_score > best_overall_score:
            best_overall_score = current_score
            best_overall_plain = current_plain
            best_overall_key = current_key

        print(f"Restart {restart + 1}/{restarts}  "
              f"score: {current_score:.2f}  best: {best_overall_score:.2f}")

    print(f"\nBest key   : {best_overall_key}")
    print(f"Best score : {best_overall_score:.2f}")

    return best_overall_plain, best_overall_key


# -------------------------
# Example usage
# -------------------------

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

sample = (
"""
You might choose to share a random sentence on social media just to see what type of reaction it garners from others. It's an unexpected move that might create more conversation than a typical post or tweet.
These are just a few ways that one might use the random sentence generator for their benefit. If you're not sure if it will help in the way you want, the best course of action is to try it and see. Have several random sentences generated and you will soon be able to see if they can help with your project.
"""
)

key = "tuxpjykabwsefdhizvlgnocqrm"  # reverse alphabet

encrypted = (
    "Pm ol ohk hufaopun jvumpkluaphs av zhf, ol dyval pa pu jpwoly, " 
    "aoha pz, if zv johunpun aol vykly vm aol slaalyz vm aol hswohila, "
    "aoha uva h dvyk jvbsk il thkl vba."
)
print(f"Encrypted:\n{encrypted}\n")

# Swap in your quadgram JSON and run:
decrypted, found_key = crack_substitution(
    encrypted, ALPHABET, "grams/english_4grams.json", n=4, restarts=100
)
print(f"\nDecrypted:\n{decrypted}")









# https://gitlab.com/guballa/SubstitutionBreaker

# This is a proper substitution cipher breaker using hill climbing + quadgrams 
# — significantly more powerful than your current frequency analysis approach. Here's how it works:
# Quadgrams instead of single letter frequencies
# Rather than counting individual letter frequencies, 
# it scores sequences of 4 letters (quadgrams) against a prebuilt corpus. tion, the, ther etc. score high in English 
# — this captures language patterns far better than single letter counts.

# there is test for it in substitute.py