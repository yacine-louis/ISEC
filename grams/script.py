import json

def txt_to_json(input_file, output_file):
    data = {}

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split()

            if len(parts) != 2:
                continue

            ngram = parts[0].lower()
            count = int(parts[1])

            data[ngram] = count

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Saved {len(data)} entries to {output_file}")


txt_to_json("data/test.txt", "online_english_4grams.json")