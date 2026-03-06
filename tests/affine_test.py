from src.substitute import substitution_cipher
from src.affine import affine_cipher, frequency_analysis_affine
from src.cesar import cesar_cipher


def test_affine_cipher():
    # Standard English alphabet
    eng = "abcdefghijklmnopqrstuvwxyz"

    # 1. Basic encrypt/decrypt roundtrip
    assert affine_cipher(affine_cipher("hello", eng, 5, 8), eng, 5, 8, "decrypt") == "hello"

    # 2. Case preservation
    result = affine_cipher("Hello World", eng, 5, 8)
    assert result[0].isupper()
    assert result[6].isupper()

    # 3. Non-alphabet characters pass through unchanged
    assert affine_cipher("hi!", eng, 5, 8).endswith("!")

    # 4. Invalid key raises error
    try:
        affine_cipher("hello", eng, 13, 5)  # gcd(13, 26) != 1
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # 5. Full uppercase roundtrip
    assert affine_cipher(affine_cipher("HELLO", eng, 5, 8), eng, 5, 8, "decrypt") == "HELLO"

    # 6. Mixed case roundtrip
    assert affine_cipher(affine_cipher("HeLLo", eng, 5, 8), eng, 5, 8, "decrypt") == "HeLLo"

    # 7. Arabic alphabet roundtrip
    arabic = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
    assert affine_cipher(affine_cipher("بحث", arabic, 3, 5), arabic, 3, 5, "decrypt") == "بحث"

    # 8. a=1 behaves like Caesar cipher (just a shift)
    assert affine_cipher("abc", eng, 1, 3) == cesar_cipher("abc", eng, 3)

    # 9. b=0, a=1 → identity (no change)
    assert affine_cipher("hello", eng, 1, 0) == "hello"

    # 10. Numbers and spaces pass through
    result = affine_cipher("hi 123", eng, 5, 8)
    assert "1" in result and "2" in result and "3" in result

    print("All tests passed!")

test_affine_cipher()


def test_frequency_analysis_affine():
    eng = "abcdefghijklmnopqrstuvwxyz"
    english_freq = {
        "e": 0.13, "t": 0.09, "a": 0.08, "o": 0.07, "i": 0.07,
        "n": 0.06, "s": 0.06, "h": 0.06, "r": 0.06, "d": 0.04,
        "l": 0.04, "c": 0.03, "u": 0.03, "m": 0.02, "w": 0.02,
        "f": 0.02, "g": 0.02, "y": 0.02, "p": 0.02, "b": 0.01,
        "v": 0.01, "k": 0.01, "j": 0.001, "x": 0.001, "q": 0.001, "z": 0.001
    }

    # long enough text for reliable frequency analysis
    plaintext = (
        "the quick brown fox jumps over the lazy dog and then the dog jumped back over the fox "
        "while the brown fox was still jumping quickly over every single lazy dog in the entire area"
    )

    # 1. Recovers plaintext with typical keys
    for a, b in [(3, 5), (5, 8), (7, 3), (11, 2)]:
        ciphertext = affine_cipher(plaintext, eng, a, b)
        result = frequency_analysis_affine(ciphertext, eng, english_freq)
        assert result == plaintext, f"Failed for a={a}, b={b}"

    # 2. Non-alphabet characters are preserved
    ciphertext = affine_cipher("hello, world! 123", eng, 5, 8)
    result = frequency_analysis_affine(ciphertext, eng, english_freq)
    assert "," in result and "!" in result and "123" in result

    # 3. Result should differ from ciphertext (actually decrypted something)
    ciphertext = affine_cipher(plaintext, eng, 5, 8)
    result = frequency_analysis_affine(ciphertext, eng, english_freq)
    assert result != ciphertext

    # 4. Identity case (a=1, b=0) is excluded — result should not be the ciphertext itself
    ciphertext = affine_cipher(plaintext, eng, 3, 5)
    result = frequency_analysis_affine(ciphertext, eng, english_freq)
    assert result != ciphertext

    # 5. Should match direct decryption with known key
    a, b = 7, 11
    ciphertext = affine_cipher(plaintext, eng, a, b)
    expected = affine_cipher(ciphertext, eng, a, b, mode="decrypt")
    result = frequency_analysis_affine(ciphertext, eng, english_freq)
    assert result == expected, "Frequency analysis result should match direct decryption"

    print("All tests passed!")

test_frequency_analysis_affine()


eng = "abcdefghijklmnopqrstuvwxyz"

english_freq = {
    "e": 0.13, "t": 0.09, "a": 0.08, "o": 0.07, "i": 0.07,
    "n": 0.06, "s": 0.06, "h": 0.06, "r": 0.06, "d": 0.04,
    "l": 0.04, "c": 0.03, "u": 0.03, "m": 0.02, "w": 0.02,
    "f": 0.02, "g": 0.02, "y": 0.02, "p": 0.02, "b": 0.01,
    "v": 0.01, "k": 0.01, "j": 0.001, "x": 0.001, "q": 0.001, "z": 0.001
}

plaintext = "the quick brown fox jumps over the lazy dog and then the dog jumped back over the fox"

ciphertext = affine_cipher(plaintext, eng, 5, 8)
print(frequency_analysis_affine(ciphertext, eng, english_freq))
# → the quick brown fox jumps over the lazy dog and then the dog jumped back over the fox
