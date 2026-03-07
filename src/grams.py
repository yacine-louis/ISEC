import re
import json
import string
from collections import Counter
from pathlib import Path

books = [ "data/book1.txt", "data/book2.txt", "data/book3.txt", "data/book4.txt", "data/book5.txt" ]
english_alphabet = "abcdefghijklmnopqrstuvwxyz"

def cumulative_ngrams_to_json(
    text_files,
    json_file_path,
    n=1,
    alphabet=string.ascii_lowercase
):
    """
    text_files : list of text file paths
    json_file_path : output json
    n : n-gram size (1,2,3,...)
    alphabet : allowed characters (language dependent)
    """

    cumulative_freq = Counter()

    for file_path in text_files:
        with open(file_path, encoding="utf8") as f:
            text = f.read().lower()

        # Keep only characters from the given alphabet
        pattern = f"[^{''.join(alphabet)}]"
        text = re.sub(pattern, '', text)

        # Generate n-grams
        ngrams = [text[i:i+n] for i in range(len(text) - n + 1)]
        cumulative_freq.update(ngrams)

    # Only keep n-grams that actually appeared in the text
    result = dict(cumulative_freq)

    # Sort by frequency (descending)
    sorted_result = dict(
        sorted(result.items(), key=lambda x: x[1], reverse=True)
    )

    # Create folder if needed
    Path(json_file_path).parent.mkdir(parents=True, exist_ok=True)

    with open(json_file_path, "w", encoding="utf8") as f:
        json.dump(sorted_result, f, ensure_ascii=False, indent=2)

    print(f"Saved {n}-gram frequencies → {json_file_path}")

# Example usage:

# 1-gram
cumulative_ngrams_to_json(
    books,
    "grams/english_1grams.json",
    n=1,
    alphabet=english_alphabet
)

# 2-gram
cumulative_ngrams_to_json(
    books,
    "grams/english_2grams.json",
    n=2,
    alphabet=english_alphabet
)

# 3-gram
cumulative_ngrams_to_json(
    books,
    "grams/english_3grams.json",
    n=3,
    alphabet=english_alphabet
)

# 4-gram
cumulative_ngrams_to_json(
    books,
    "grams/english_4grams.json",
    n=4,
    alphabet=english_alphabet
)