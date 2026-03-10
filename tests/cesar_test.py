from src.substitute import substitution_cipher
from src.affine import affine_cipher
from src.cesar import cesar_cipher, crack_caesar_frequency

def test_cesar_cipher():
    eng = "abcdefghijklmnopqrstuvwxyz"

    # 1. Basic encrypt/decrypt roundtrip
    assert cesar_cipher(cesar_cipher("hello", eng, 3), eng, 3, "decrypt") == "hello"

    # 2. Classic Caesar shift (a→d, b→e, c→f)
    assert cesar_cipher("abc", eng, 3) == "def"

    # 3. Wraps around alphabet (x→a, y→b, z→c)
    assert cesar_cipher("xyz", eng, 3) == "abc"

    # 4. Case preservation
    result = cesar_cipher("Hello World", eng, 3)
    assert result[0].isupper()
    assert result[6].isupper()

    # 5. Non-alphabet characters pass through unchanged
    assert cesar_cipher("hi!", eng, 3).endswith("!")

    # 6. Numbers and spaces pass through
    result = cesar_cipher("hi 123", eng, 3)
    assert "1" in result and "2" in result and "3" in result

    # 7. Shift of 0 → identity (no change)
    assert cesar_cipher("hello", eng, 0) == "hello"

    # 8. Full uppercase roundtrip
    assert cesar_cipher(cesar_cipher("HELLO", eng, 3), eng, 3, "decrypt") == "HELLO"

    # 9. Mixed case roundtrip
    assert cesar_cipher(cesar_cipher("HeLLo", eng, 3), eng, 3, "decrypt") == "HeLLo"

    # 10. Shift larger than alphabet size wraps correctly
    assert cesar_cipher("abc", eng, 29) == cesar_cipher("abc", eng, 3)  # 29 % 26 == 3

    # 11. Negative shift
    assert cesar_cipher(cesar_cipher("hello", eng, -3), eng, -3, "decrypt") == "hello"

    # 12. Arabic alphabet roundtrip
    arabic = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
    assert cesar_cipher(cesar_cipher("بحث", arabic, 3), arabic, 3, "decrypt") == "بحث"

    # 13. Affine with a=1 should match Caesar (since affine with a=1 is just a shift)
    assert cesar_cipher("hello", eng, 5) == affine_cipher("hello", eng, 1, 5)

    print("All tests passed!")

test_cesar_cipher()

alphabet = "abcdefghijklmnopqrstuvwxyz"

ciphertext = """
gura
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


# # ---- BIGRAM TEST ----
# plaintext2, shift2 = crack_caesar_frequency(
#     ciphertext=ciphertext,
#     alphabet=alphabet,
#     ngram_json_path="grams/english_2grams.json",
#     top_n=20
# )

# print("\n========== BIGRAM RESULT ==========")
# print("Shift:", shift2)
# print("Plaintext:\n", plaintext2)


# # ---- TRIGRAM TEST ----
# plaintext3, shift3 = crack_caesar_frequency(
#     ciphertext=ciphertext,
#     alphabet=alphabet,
#     ngram_json_path="grams/english_3grams.json",
#     top_n=50
# )

# print("\n========== TRIGRAM RESULT ==========")
# print("Shift:", shift3)
# print("Plaintext:\n", plaintext3)
