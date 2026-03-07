import json
from collections import Counter


# cesar cipher each letter in the text is shifted by a fixed number of positions in the alphabet
def cesar_cipher(text, alphabet, shift, mode="encrypt"):
    """
    :param text: input text
    :param alphabet: custom alphabet string
    :param shift: shift value
    :param mode: "encrypt" or "decrypt"
    :return: encrypted/decrypted text
    """

    result = ""
    alphabet = alphabet.lower()
    alphabet_size = len(alphabet)

    # reverse shift for decoding
    if mode == "decrypt":
        shift = -shift

    for char in text:
        lower_char = char.lower()

        if lower_char in alphabet:
            index = alphabet.index(lower_char)
            new_index = (index + shift) % alphabet_size
            new_char = alphabet[new_index]

            # preserve character case
            if char.isupper():
                new_char = new_char.upper()

            result += new_char
        else:
            # keep others unchanged (spaces, numbers...)
            result += char

    return result


def crack_caesar_frequency(
    ciphertext,
    alphabet,
    ngram_json_path,
    top_n=10
):
    """
    Generic frequency attack for:
        - unigram
        - bigram
        - trigram
        - etc.

    It works by:
    1. Extracting n-grams from ciphertext
    2. Loading n-gram frequency table
    3. Pairing top cipher n-grams with top language n-grams
    4. Computing shift votes
    5. Picking majority shift
    """

    alphabet = alphabet.lower()
    n = len(alphabet)

    # -------------------------------
    # Load Frequency Table
    # -------------------------------
    with open(ngram_json_path, "r", encoding="utf8") as f:
        freq_table = json.load(f)

    top_language_ngrams = sorted(
        freq_table,
        key=freq_table.get,
        reverse=True
    )[:top_n]

    # -------------------------------
    # Extract Cipher n-grams
    # -------------------------------
    letters = [
        c.lower() for c in ciphertext
        if c.lower() in alphabet
    ]

    ngram_size = len(next(iter(top_language_ngrams)))  # auto-detect

    cipher_ngrams = [
        "".join(letters[i:i + ngram_size])
        for i in range(len(letters) - ngram_size + 1)
        if len(letters[i:i + ngram_size]) == ngram_size
    ]

    cipher_freq = Counter(cipher_ngrams)

    top_cipher_ngrams = [
        bg for bg, _ in cipher_freq.most_common(top_n)
    ]

    # -------------------------------
    # Voting
    # -------------------------------
    shift_votes = Counter()

    for cipher_ng in top_cipher_ngrams:
        for lang_ng in top_language_ngrams:

            shifts = []

            for i in range(ngram_size):
                shift = (
                    alphabet.index(cipher_ng[i])
                    - alphabet.index(lang_ng[i])
                ) % n
                shifts.append(shift)

            # Only vote if all letters agree on same shift
            if len(set(shifts)) == 1:
                shift_votes[shifts[0]] += 1

    if not shift_votes:
        return ciphertext, 0

    best_shift = shift_votes.most_common(1)[0][0]
    
    # -------------------------------
    # Decrypt
    # -------------------------------
    plaintext = cesar_cipher(ciphertext, alphabet, best_shift, mode="decrypt")

    print("Top cipher ngrams :", top_cipher_ngrams)
    print("Top language ngrams:", top_language_ngrams)
    print("Shift votes       :", shift_votes.most_common(5))
    print("Best shift        :", best_shift)

    return plaintext, best_shift

# ---------------------------
# Test Generic Frequency Attack
# ---------------------------

alphabet = "abcdefghijklmnopqrstuvwxyz"

ciphertext = """
Lw fdq dovr eh d ixq zdb wr vxusulvh rwkhuv. Brx pljkw fkrrvh wr vkduh d udqgrp vhqwhqfh rq vrfldo phgld mxvw wr vhh zkdw wbsh ri uhdfwlrq lw jduqhuv iurp rwkhuv.
"""

# ---- UNIGRAM TEST ----
plaintext1, shift1 = crack_caesar_frequency(
    ciphertext=ciphertext,
    alphabet=alphabet,
    ngram_json_path="grams/english_1grams.json",
    top_n=10
)

print("\n========== UNIGRAM RESULT ==========")
print("Shift:", shift1)
print("Plaintext:\n", plaintext1)


# ---- BIGRAM TEST ----
plaintext2, shift2 = crack_caesar_frequency(
    ciphertext=ciphertext,
    alphabet=alphabet,
    ngram_json_path="grams/english_2grams.json",
    top_n=20
)

print("\n========== BIGRAM RESULT ==========")
print("Shift:", shift2)
print("Plaintext:\n", plaintext2)


# ---- TRIGRAM TEST ----
plaintext3, shift3 = crack_caesar_frequency(
    ciphertext=ciphertext,
    alphabet=alphabet,
    ngram_json_path="grams/english_3grams.json",
    top_n=50
)

print("\n========== TRIGRAM RESULT ==========")
print("Shift:", shift3)
print("Plaintext:\n", plaintext3)
