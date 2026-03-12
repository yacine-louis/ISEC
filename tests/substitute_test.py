import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.substitute import substitution_cipher, crack_substitution_frequency
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

    print("All tests passed!")

test_substitution_cipher()


def test_crack_substitution_frequency():
    eng = "abcdefghijklmnopqrstuvwxyz"
    key = "qwertyuiopasdfghjklzxcvbnm"  # QWERTY mapping

    # Longer plaintext for reliable statistical cracking
    plaintext = (
        "the quick brown fox jumps over the lazy dog and then runs back again "
        "through the forest where the birds are singing their beautiful songs "
        "while the sun is setting behind the mountains creating a wonderful "
        "display of colors in the evening sky above the peaceful valley below"
    )

    # Encrypt
    ciphertext = substitution_cipher(plaintext, eng, key)

    # Crack using the function
    quadgram_path = "grams/english_4grams.json"
    cracked_plaintext, cracked_key = crack_substitution_frequency(
        ciphertext, eng, quadgram_path, max_rounds=10000, consolidate=3
    )

    # Check if the cracked plaintext matches the original (case-insensitive)
    assert cracked_plaintext.lower() == plaintext.lower(), f"Expected: {plaintext}, Got: {cracked_plaintext}"

    print("Crack test passed!")

test_crack_substitution_frequency()



def test_arabic_substitution_crack():
    arabic_alphabet = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
    
    # Longer Arabic text for reliable statistical cracking
    plaintext = (
        "في هذا النص نستخدم اللغة العربية لاختبار قدرة الخوارزمية على كسر شفرة الاستبدال "
        "حيث يتم استبدال كل حرف بحرف مختلف من نفس الابجدية وهذه الطريقة تعتمد على تحليل "
        "تكرار الحروف والمقاطع في النصوص العربية وكلما كان النص اطول كلما زادت دقة التحليل "
        "ونجحت الخوارزمية في استعادة النص الاصلي بشكل صحيح وكامل"
    )
    
    # Create a simple substitution key (shift by 3 positions)
    shift = 3
    key = arabic_alphabet[shift:] + arabic_alphabet[:shift]
    
    # Encrypt the text
    ciphertext = substitution_cipher(plaintext, arabic_alphabet, key)
    
    # Crack using frequency analysis
    quadgram_path = "grams/arabic_4grams.json"
    cracked_plaintext, cracked_key = crack_substitution_frequency(
        ciphertext, arabic_alphabet, quadgram_path, max_rounds=10000, consolidate=3
    )
    
    # Check if the cracked plaintext matches the original
    assert cracked_plaintext == plaintext, f"Expected: {plaintext}, Got: {cracked_plaintext}"
    
    print("Arabic crack test passed!")

test_arabic_substitution_crack()
