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


def test_affine_crack_english_ngrams():
    eng = "abcdefghijklmnopqrstuvwxyz"
    a, b = 5, 8

    plaintext = (
        "the quick brown fox jumps over the lazy dog and then runs back again "
        "through the forest where the birds are singing their beautiful songs "
        "while the sun is setting behind the mountains creating a wonderful "
        "display of colors in the evening sky above the peaceful valley below"
    )

    ciphertext = affine_cipher(plaintext, eng, a, b)

    for ngram_path in ("grams/english_3grams.json", "grams/english_4grams.json"):
        cracked_plaintext, (cracked_a, cracked_b) = crack_affine_frequency(
            ciphertext, eng, ngram_path
        )
        assert cracked_plaintext.lower() == plaintext.lower()
        assert cracked_a == a and cracked_b == b

    print("English affine crack tests (3-grams & 4-grams) passed!")


def test_affine_crack_arabic_ngrams():
    arabic_alphabet = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
    a, b = 5, 7

    plaintext = (
        "في هذا النص نستخدم اللغة العربية لاختبار قدرة الخوارزمية على كسر شفرة الاستبدال "
        "حيث يتم استبدال كل حرف بحرف مختلف من نفس الابجدية وهذه الطريقة تعتمد على تحليل "
        "تكرار الحروف والمقاطع في النصوص العربية وكلما كان النص اطول كلما زادت دقة التحليل "
        "ونجحت الخوارزمية في استعادة النص الاصلي بشكل صحيح وكامل"
    )

    ciphertext = affine_cipher(plaintext, arabic_alphabet, a, b)

    for ngram_path in ("grams/arabic_3grams.json", "grams/arabic_4grams.json"):
        cracked_plaintext, (cracked_a, cracked_b) = crack_affine_frequency(
            ciphertext, arabic_alphabet, ngram_path
        )
        assert cracked_plaintext == plaintext
        assert cracked_a == a and cracked_b == b

    print("Arabic affine crack tests (3-grams & 4-grams) passed!")


test_affine_crack_english_ngrams()
test_affine_crack_arabic_ngrams()


def test_affine_crack_specific_arabic_4gram_text():
    """
    Regression-style test: ensure cracking this specific Arabic ciphertext with
    4-gram statistics does not crash and returns a string result.
    """
    arabic_alphabet = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
    ciphertext = (
        """حادث خواظ وخ دبتغريذب حاخو ختاث ببتنظوة دث رهخظ شخدة دبدثغدث
ودبنتب حدبدسرجدض لظخي دبثسدش حتث خغن وخ لبذ دبنبت خسض زتظة سجضج
حوخ ثجدخة دبخحت ندض دبى تثعبج حجح خفنظ ذدبظكد حدبدتب وخ هض دوكب
"""
    )
    ngram_path = "grams/arabic_1grams.json"

    plaintext, best = crack_affine_frequency(ciphertext, arabic_alphabet, ngram_path)

    print(plaintext)

test_affine_crack_specific_arabic_4gram_text()

