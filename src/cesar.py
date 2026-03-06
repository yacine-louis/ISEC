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



# https://raw.org/tool/caesar-cipher/#:~:text=Cracking%20it%20can%20be%20done,key%20more%20quickly%20and%20accurately.&text=In%20our%20cracking%20algorithm%2C%20we,and%20successfully%20decrypt%20the%20message.&text=By%20using%20the%20crack_caesar(),the%20decryption%20process%20in%20action.

def frequency_analysis_caesar(ciphertext, alphabet, language_freq):
    """
    Attempt to decrypt a Caesar cipher using frequency analysis.

    :param ciphertext: encrypted text
    :param alphabet: custom alphabet string
    :param language_freq: list of letters ordered by frequency in the language (most → least frequent)
    :return: best guess decrypted text
    """
    
    alphabet = alphabet.lower()
    m = len(alphabet)

    counts = {char: 0 for char in alphabet}
    for char in ciphertext.lower():
        if char in alphabet:
            counts[char] += 1

    total = sum(counts.values())

    best_shift = 0
    best_score = float("-inf")

    # try all possible shifts and score each one
    for shift in range(1, m):
        score = 0
        for char in alphabet:
            decrypted_char = alphabet[(alphabet.index(char) - shift) % m]
            expected_freq = language_freq.get(decrypted_char, 0)
            observed_freq = counts[char] / total if total > 0 else 0
            score += observed_freq * expected_freq  # dot product scoring

        if score > best_score:
            best_score = score
            best_shift = shift

    return cesar_cipher(ciphertext, alphabet, best_shift, mode="decrypt")
