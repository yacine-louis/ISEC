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

# The main difference from Caesar frequency analysis is the nested loop 
# — Caesar only searches m shifts, while affine searches all valid (a, b) pairs, 
# which is roughly φ(m) × m combinations (φ(m) being the count of valid a values coprime with m). 
# For English that's 12 × 26 = 312 combinations vs Caesar's 25.

def frequency_analysis_affine(ciphertext, alphabet, language_freq):
    """
    Attempt to decrypt an affine cipher using frequency analysis.

    :param ciphertext: encrypted text
    :param alphabet: custom alphabet string
    :param language_freq: dict of {letter: frequency} e.g {"e": 0.13, "t": 0.09, ...}
    :return: best guess decrypted text
    """

    alphabet = alphabet.lower()
    m = len(alphabet)

    # count letter frequencies in ciphertext
    counts = {char: 0 for char in alphabet}
    for char in ciphertext.lower():
        if char in alphabet:
            counts[char] += 1

    total = sum(counts.values())

    best_a, best_b = None, None
    best_score = float("-inf")

    for a in range(1, m):
        a_inv = mod_inverse(a, m)
        if mod_inverse(a, m) is None:
            continue  # skip invalid a values

        for b in range(m):
            # exclude identity case
            if a == 1 and b == 0:
                continue

            score = 0
            for char in alphabet:
                x = alphabet.index(char)
                decrypted_char = alphabet[(a_inv * (x - b)) % m]
                expected_freq = language_freq.get(decrypted_char, 0)
                observed_freq = counts[char] / total if total > 0 else 0
                score += observed_freq * expected_freq

            if score > best_score:
                best_score = score
                best_a, best_b = a, b

    return affine_cipher(ciphertext, alphabet, best_a, best_b, mode="decrypt")