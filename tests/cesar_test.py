from src.substitute import substitution_cipher
from src.affine import affine_cipher
from src.cesar import cesar_cipher, frequency_analysis_caesar


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


eng = "abcdefghijklmnopqrstuvwxyz"

english_freq = {
    "e": 0.13, "t": 0.09, "a": 0.08, "o": 0.07, "i": 0.07,
    "n": 0.06, "s": 0.06, "h": 0.06, "r": 0.06, "d": 0.04,
    "l": 0.04, "c": 0.03, "u": 0.03, "m": 0.02, "w": 0.02,
    "f": 0.02, "g": 0.02, "y": 0.02, "p": 0.02, "b": 0.01,
    "v": 0.01, "k": 0.01, "j": 0.001, "x": 0.001, "q": 0.001, "z": 0.001
}

ciphertext = cesar_cipher("hello world this is a secret message", eng, 7)
print(frequency_analysis_caesar(ciphertext, eng, english_freq))
# → hello world this is a secret message