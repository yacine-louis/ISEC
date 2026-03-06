from src.substitute import substitution_cipher
from src.affine import affine_cipher
from src.cesar import cesar_cipher

def test_substitution_cipher():
    eng = "abcdefghijklmnopqrstuvwxyz"
    key = "qwertyuiopasdfghjklzxcvbnm"  # classic QWERTY mapping

    # 1. Basic encrypt/decrypt roundtrip
    assert substitution_cipher(substitution_cipher("hello", eng, key), eng, key, "decrypt") == "hello"

    # 2. Known mapping (a→q, b→w, c→e)
    assert substitution_cipher("abc", eng, key) == "qwe"

    # 3. Case preservation
    result = substitution_cipher("Hello World", eng, key)
    assert result[0].isupper()
    assert result[6].isupper()

    # 4. Non-alphabet characters pass through unchanged
    assert substitution_cipher("hi!", eng, key).endswith("!")

    # 5. Numbers and spaces pass through
    result = substitution_cipher("hi 123", eng, key)
    assert "1" in result and "2" in result and "3" in result

    # 6. Full uppercase roundtrip
    assert substitution_cipher(substitution_cipher("HELLO", eng, key), eng, key, "decrypt") == "HELLO"

    # 7. Mixed case roundtrip
    assert substitution_cipher(substitution_cipher("HeLLo", eng, key), eng, key, "decrypt") == "HeLLo"

    # 8. Identity key (alphabet maps to itself) → no change
    assert substitution_cipher("hello", eng, eng) == "hello"

    # 9. Wrong key length raises error
    try:
        substitution_cipher("hello", eng, "abc")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # 10. Key with wrong characters raises error
    try:
        substitution_cipher("hello", eng, "qwertyuiopasdfghjklzxcvbn1")  # '1' instead of a letter
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # 11. Key with duplicate characters raises error
    try:
        substitution_cipher("hello", eng, "qqertyuiopasdfghjklzxcvbnm")  # 'q' twice, no 'w'
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # 12. Arabic alphabet roundtrip
    arabic = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
    arabic_key = "بتثجحخدذرزسشصضطظعغفقكلمنهويا"  # shifted by one
    assert substitution_cipher(substitution_cipher("بحث", arabic, arabic_key), arabic, arabic_key, "decrypt") == "بحث"

    # 13. Caesar shift of 3 should match substitution with equivalent key
    caesar_as_key = eng[3:] + eng[:3]  # "defghijklmnopqrstuvwxyzabc"
    assert substitution_cipher("hello", eng, caesar_as_key) == cesar_cipher("hello", eng, 3)

    print("All tests passed!")

test_substitution_cipher()

from subbreaker import Breaker
import subbreaker
import os

library_path = os.path.dirname(subbreaker.__file__)
english_json = os.path.join(library_path, "quadgram", "EN.json")

with open(english_json) as f:
    breaker = Breaker(f)

key = "qwertyuiopasdfghjklzxcvbnm"
plaintext = (
    "the quick brown fox jumps over the lazy dog and then the dog jumped back over the fox "
    "while the brown fox was still jumping quickly over every single lazy dog in the entire area "
    "the weather was nice and the sun was shining brightly over the hills and the trees were green"
)
ciphertext = substitution_cipher(plaintext, "abcdefghijklmnopqrstuvwxyz", key)

result = breaker.break_cipher(ciphertext, max_rounds=100, consolidate=3)
print(f"result: {result.plaintext}")
print(result.key)
print(f"fitness: {result.fitness}")
print(f"keys tried: {result.nbr_keys}")
print(f"rounds: {result.nbr_rounds}")