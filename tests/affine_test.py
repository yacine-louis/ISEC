from src.substitute import substitution_cipher
from src.affine import affine_cipher, crack_affine_frequency
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

