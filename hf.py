# from datasets import load_dataset

# dataset = load_dataset("wikimedia/wikipedia", "20231101.ar")

# with open("arabic_wikipedia.txt", "w", encoding="utf8") as f:
#     for article in dataset["train"]:
#         f.write(article["text"] + "\n")

# # Cut a large text file to a target size in MB
# input_file = "arabic_wikipedia.txt"   # your original 2.8GB file
# output_file = "arabic_wikipedia_10mb.txt"
# limit_mb = 100

# limit_bytes = limit_mb * 1024 * 1024
# size = 0

# with open(input_file, "r", encoding="utf8") as fin, open(output_file, "w", encoding="utf8") as fout:
#     for line in fin:
#         encoded = line.encode("utf8")
#         if size + len(encoded) > limit_bytes:
#             break
#         fout.write(line)
#         size += len(encoded)

# print(f"Done! Output file size: {size / (1024*1024):.2f} MB")


# import re

# def clean_arabic_text(text):
#     # Remove Wikipedia tables / templates {{...}} and {|...|}
#     text = re.sub(r'\{\{.*?\}\}', ' ', text, flags=re.DOTALL)
#     text = re.sub(r'\{\|.*?\|\}', ' ', text, flags=re.DOTALL)

#     # Remove HTML tags <...>
#     text = re.sub(r'<.*?>', ' ', text)

#     # Remove Wikipedia links [[...]]
#     text = re.sub(r'\[\[.*?\]\]', ' ', text)

#     # Remove non-Arabic letters (keep only Arabic letters and spaces)
#     text = re.sub(r'[^\u0600-\u06FF\s]', ' ', text)

#     # Normalize spaces
#     text = re.sub(r'\s+', ' ', text)

#     # Remove Arabic diacritics
#     arabic_diacritics = re.compile(r'[\u064B-\u065F\u0670\u06D6-\u06ED]')
#     text = re.sub(arabic_diacritics, '', text)

#     return text.strip()

# input_file = "arabic_wikipedia_10mb.txt"
# output_file = "arabic_wikipedia_10mb_clean.txt"

# with open(input_file, "r", encoding="utf8") as fin, open(output_file, "w", encoding="utf8") as fout:
#     for line in fin:
#         clean_line = clean_arabic_text(line)
#         if clean_line:
#             fout.write(clean_line + "\n")

# print("Cleaning done! File ready for n-grams.")


# import re

# # Input and output files
# input_file = "arabic_wikipedia_10mb_clean.txt"
# output_file = "arabic_wikipedia_10mb_clean_no_tashkeel.txt"

# # Function to remove Arabic diacritics (tashkeel)
# def remove_tashkeel(text):
#     arabic_diacritics = re.compile(r'[\u064B-\u065F\u0670\u06D6-\u06ED]')
#     return re.sub(arabic_diacritics, '', text)

# # Read original file and write cleaned file
# with open(input_file, "r", encoding="utf8") as fin, open(output_file, "w", encoding="utf8") as fout:
#     for line in fin:
#         clean_line = remove_tashkeel(line)
#         fout.write(clean_line)

# print(f"Done! File without tashkeel saved as {output_file}")






# import json
# from collections import Counter
# import re

# # Input & output files
# input_file = "arabic_wikipedia_10mb_clean_no_tashkeel.txt"
# output_file = "arabic_unigrams_28letters_sorted.json"

# # Standard 28 Arabic letters
# arabic_letters = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"

# # Read the text
# with open(input_file, "r", encoding="utf8") as f:
#     text = f.read()

# # Remove spaces and any non-Arabic 28 letters (extra safety)
# text = re.sub(f"[^{arabic_letters}]", "", text)

# # Count unigrams
# unigram_counts = Counter(text)

# # Sort by frequency (descending)
# sorted_unigrams = dict(sorted(unigram_counts.items(), key=lambda item: item[1], reverse=True))

# # Save to JSON
# with open(output_file, "w", encoding="utf8") as f:
#     json.dump(sorted_unigrams, f, ensure_ascii=False, indent=2)

# print(f"Done! Unigrams saved and sorted in {output_file}")



# import json
# from collections import Counter
# import re

# # Input & output files
# input_file = "arabic_wikipedia_10mb_clean_no_tashkeel.txt"
# output_file = "arabic_bigrams.json"

# # Standard 28 Arabic letters
# arabic_letters = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"

# # Read the text
# with open(input_file, "r", encoding="utf8") as f:
#     text = f.read()

# # Keep only the 28 letters
# text = re.sub(f"[^{arabic_letters}]", "", text)

# # Generate bigrams
# bigrams = [text[i:i+2] for i in range(len(text)-1)]

# # Count bigram frequencies
# bigram_counts = Counter(bigrams)

# # Sort by frequency descending
# sorted_bigrams = dict(sorted(bigram_counts.items(), key=lambda item: item[1], reverse=True))

# # Save to JSON
# with open(output_file, "w", encoding="utf8") as f:
#     json.dump(sorted_bigrams, f, ensure_ascii=False, indent=2)

# print(f"Done! Bigrams saved and sorted in {output_file}")

# import json
# from collections import Counter
# import re

# # Input & output files
# input_file = "arabic_wikipedia_10mb_clean_no_tashkeel.txt"
# output_file = "arabic_trigrams.json"

# # Standard 28 Arabic letters
# arabic_letters = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"

# # Read the text
# with open(input_file, "r", encoding="utf8") as f:
#     text = f.read()

# # Keep only the 28 letters
# text = re.sub(f"[^{arabic_letters}]", "", text)

# # Generate trigrams
# trigrams = [text[i:i+3] for i in range(len(text)-2)]

# # Count trigram frequencies
# trigram_counts = Counter(trigrams)

# # Sort by frequency descending
# sorted_trigrams = dict(sorted(trigram_counts.items(), key=lambda item: item[1], reverse=True))

# # Save to JSON
# with open(output_file, "w", encoding="utf8") as f:
#     json.dump(sorted_trigrams, f, ensure_ascii=False, indent=2)

# print(f"Done! Trigrams saved and sorted in {output_file}")


# import json
# from collections import Counter
# import re

# # Input/output files
# input_file = "arabic_wikipedia_10mb_clean_no_tashkeel.txt"
# output_file = "arabic_quadgrams_sorted_correct.json"

# # Standard 28 Arabic letters
# arabic_letters = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"

# # Read and clean text
# with open(input_file, "r", encoding="utf8") as f:
#     text = f.read()

# # Keep only the 28 Arabic letters in one continuous string
# text = re.sub(f"[^{arabic_letters}]", "", text)

# # Generate quadgrams (exact consecutive letters)
# quadgrams = [text[i:i+4] for i in range(len(text)-3)]

# # Count frequencies
# quadgram_counts = Counter(quadgrams)

# # Sort descending by frequency
# sorted_quadgrams = dict(sorted(quadgram_counts.items(), key=lambda x: x[1], reverse=True))

# # Save JSON
# with open(output_file, "w", encoding="utf8") as f:
#     json.dump(sorted_quadgrams, f, ensure_ascii=False, indent=2)

# print(f"Done! Correct quadgrams saved in {output_file}")