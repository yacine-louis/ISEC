#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script to verify English still works."""

import sys
import os
import random
import importlib.util

spec = importlib.util.spec_from_file_location("breaker", os.path.join(os.path.dirname(__file__), 'something', 'test.py'))
breaker_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(breaker_module)

Breaker = breaker_module.Breaker
Key = breaker_module.Key

def main():
    # Test with English
    quadgram_path = os.path.join(os.path.dirname(__file__), 'grams', 'english_3grams.json')
    breaker = Breaker(quadgram_path)

    print('Breaker info:')
    print('Alphabet:', breaker.info.alphabet)
    print('Most frequent quadgram:', breaker.info.most_frequent_quadgram)

    plaintext = 'This website includes information about Project Gutenberg, including how to make donations to the Project Gutenberg Literary Archive Foundation, how to help produce our new eBooks, and how to subscribe to our email newsletter to hear about new eBooks.'

    alphabet = breaker.info.alphabet
    key_list = list(alphabet)
    random.shuffle(key_list)
    key_str = ''.join(key_list)
    key = Key(key_str, alphabet=alphabet)

    def encrypt(text, key_obj):
        result = ''
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

    print('Plaintext:', plaintext)
    print('Ciphertext:', ciphertext)

    result = breaker.break_cipher(ciphertext, max_rounds=10000, consolidate=5)
    print('Recovered plaintext:', result.plaintext)
    print('Match:', result.plaintext.lower() == plaintext.lower())
    print('Fitness:', result.fitness)
    print('Keys tried:', result.nbr_keys)
    print('Time taken:', result.seconds, 'seconds')

if __name__ == '__main__':
    main()
