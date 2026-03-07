#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script for the Breaker class using custom quadgram."""

import sys
import os
import random
import importlib.util

# Load the breaker module
spec = importlib.util.spec_from_file_location("breaker", os.path.join(os.path.dirname(__file__), 'something', 'test.py'))
breaker_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(breaker_module)

Breaker = breaker_module.Breaker
Key = breaker_module.Key

def main():
    # Path to the English ngram file (change to test different n)
    quadgram_path = os.path.join(os.path.dirname(__file__), 'grams', 'arabic_4grams.json')

    # Initialize the Breaker with the quadgram
    breaker = Breaker(quadgram_path)

    print("Breaker info:")
    print("Alphabet:", breaker.info.alphabet)
    print("Most frequent quadgram:", breaker.info.most_frequent_quadgram)
    print("Number of quadgrams:", breaker.info.nbr_quadgrams)

    # Create a sample plaintext (shorter for faster testing)
    plaintext = ("""
                 كان الطقس جميلًا في ذلك الصباح، فخرج أحمد يتمشى في الحديقة القريبة من منزله. كانت الأشجار خضراء والهواء منعشًا، وكان الناس يجلسون على المقاعد يتحدثون ويستمتعون بالهدوء. جلس أحمد قليلًا يقرأ كتابه المفضل، ثم عاد إلى المنزل وهو يشعر بالراحة والنشاط لبقية يومه.
                 """)

    # Create a random key for encryption
    alphabet = breaker.info.alphabet
    key_list = list(alphabet)
    random.shuffle(key_list)
    key_str = ''.join(key_list)
    key = Key(key_str, alphabet=alphabet)

    # Encrypt the plaintext
    ciphertext = key.decode(plaintext)  # Wait, decode is decrypt, need encrypt
    # Since Key.decode decrypts, to encrypt, I need to reverse
    # Actually, for substitution, encrypt is replace with key
    # Let's define encrypt
    def encrypt(text, key_obj):
        result = ""
        for char in text:
            lower_char = char.lower()
            if lower_char in key_obj.alphabet:
                new_char = key_obj.key[key_obj.alphabet.index(lower_char)]
                if char.isupper():
                    new_char = new_char.upper()
                result += new_char
            else:
                result += char
        return result

    ciphertext = encrypt(plaintext, key)

    print("\nOriginal plaintext:", plaintext)
    print("Ciphertext:", ciphertext)
    print("Key used:", key_str)

    # Now break the cipher (fewer rounds for faster testing)
    result = breaker.break_cipher(ciphertext, max_rounds=1000, consolidate=3)

    print("\nBreaking result:")
    print("Recovered plaintext:", result.plaintext)
    print("Recovered key:", result.key)
    print("Fitness:", result.fitness)
    print("Keys tried:", result.nbr_keys)
    print("Rounds:", result.nbr_rounds)
    print("Keys per second:", result.keys_per_second)
    print("Time taken:", result.seconds, "seconds")

    # Check if correct
    if result.plaintext.lower() == plaintext.lower():
        print("SUCCESS: Cipher broken correctly!")
    else:
        print("PARTIAL: Plaintext not fully recovered.")


main()