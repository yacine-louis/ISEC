# substitution cipher replaces each letter with a corresponding letter from a shuffled key alphabet
# each letter in the alphabet maps 1-to-1 to a letter in the key
# key must be a permutation of the alphabet (same letters, different order)

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

# # The key difference from Caesar and affine is that there is no key to solve for mathematically 
# # — instead you build a mapping directly by ranking both the ciphertext letters and 
# # the language letters by frequency and pairing them up position by position.
# # This is also why substitution frequency analysis is the least reliable of the three — 
# # Caesar and affine crack exactly given enough text, 
# # but substitution produces a best guess that almost always needs manual tweaking.
# def frequency_analysis_substitution(ciphertext, alphabet, language_freq):
#     """
#     Attempt to decrypt a substitution cipher using frequency analysis.

#     :param ciphertext: encrypted text
#     :param alphabet: custom alphabet string
#     :param language_freq: dict of {letter: frequency} e.g {"e": 0.13, "t": 0.09, ...}
#     :return: best guess decrypted text
#     """

#     alphabet = alphabet.lower()

#     # count letter frequencies in ciphertext
#     counts = {char: 0 for char in alphabet}
#     for char in ciphertext.lower():
#         if char in alphabet:
#             counts[char] += 1

#     # sort ciphertext letters by frequency (most → least frequent)
#     sorted_ciphertext_letters = sorted(counts, key=counts.get, reverse=True)

#     # sort language letters by frequency (most → least frequent)
#     sorted_language_letters = sorted(language_freq, key=language_freq.get, reverse=True)

#     # map most frequent ciphertext letter → most frequent language letter, and so on
#     guessed_key = {
#         cipher_char: lang_char
#         for cipher_char, lang_char in zip(sorted_ciphertext_letters, sorted_language_letters)
#     }

#     result = ""
#     for char in ciphertext:
#         lower_char = char.lower()
#         if lower_char in guessed_key:
#             new_char = guessed_key[lower_char]
#             if char.isupper():
#                 new_char = new_char.upper()
#             result += new_char
#         else:
#             result += char

#     return result








# https://gitlab.com/guballa/SubstitutionBreaker

# This is a proper substitution cipher breaker using hill climbing + quadgrams 
# — significantly more powerful than your current frequency analysis approach. Here's how it works:
# Quadgrams instead of single letter frequencies
# Rather than counting individual letter frequencies, 
# it scores sequences of 4 letters (quadgrams) against a prebuilt corpus. tion, the, ther etc. score high in English 
# — this captures language patterns far better than single letter counts.

# there is test for it in substitute.py