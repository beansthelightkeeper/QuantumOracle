import os
import re

def build_gematria_tables():
    simple = {}
    english = {}
    jewish = {}

    for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 1):
        simple[letter] = i
        english[letter] = i
        jewish_vals = [
            1, 2, 3, 4, 5, 6, 7, 8, 9,
            10, 20, 30, 40, 50, 60, 70, 80, 90,
            100, 200, 300, 400, 500, 600, 700, 800
        ]
        jewish[letter] = jewish_vals[i - 1]

    return simple, english, jewish

def get_gematria_values(word, simple, english, jewish):
    word = word.upper()
    return (
        sum(jewish.get(c, 0) for c in word),
        sum(english.get(c, 0) for c in word),
        sum(simple.get(c, 0) for c in word)
    )

def extract_words(directory):
    words = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    text = f.read()
                    words.update(re.findall(r"\b[a-zA-Z]{2,}\b", text))
    return sorted(words)

def main():
    input_dir = "/Users/lydiaparker/The_Oracle/txt_db"
    output_file = "/Users/lydiaparker/The_Oracle/wordsdb.txt"
    simple, english, jewish = build_gematria_tables()
    words = extract_words(input_dir)

    with open(output_file, 'w', encoding='utf-8') as out:
        for word in words:
            jewish_val, english_val, simple_val = get_gematria_values(word, simple, english, jewish)
            out.write(f"{word}:{jewish_val}:{english_val}:{simple_val}\n")

    print(f"✅ wordsdb.txt written with {len(words)} words, all gematria values included.")

if __name__ == "__main__":
    main()
