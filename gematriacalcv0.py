```python
import math
import re
import sqlite3
import logging
import nltk
from nltk import pos_tag, word_tokenize
import random

nltk.download('punkt_tab', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Database config
DB_NAME = 'gematria_data.db'

# Helper functions
def int_to_base8(num): return ''.join(str(num % 8**(i+1) // 8**i) for i in range(int(math.log(num, 8))+1))[::-1] if num else '0'
def int_to_base12(num): return ''.join(['ABC'[r-10] if r >= 10 else str(r) for r in reversed([num % 12**(i+1) // 12**i for i in range(int(math.log(num, 12))+1)])) if num else '0'
def int_to_base20(num): return ''.join([chr(65+r-10) if r >= 10 else str(r) for r in reversed([num % 20**(i+1) // 20**i for i in range(int(math.log(num, 20))+1)])) if num else '0'
def int_to_base4(num): return ''.join(str(num % 4**(i+1) // 4**i) for i in range(int(math.log(num, 4))+1))[::-1] if num else '0'
def int_to_base60(num): chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'; return ''.join(chars[num % 60**(i+1) // 60**i] for i in range(int(math.log(num, 60))+1))[::-1] if num else '0'
def to_roman(num):
    val = [(1000, 'M'), (500, 'D'), (100, 'C'), (50, 'L'), (10, 'X'), (5, 'V'), (1, 'I')]
    result = ""
    for value, symbol in val:
        while num >= value:
            result += symbol
            num -= value
    return result
def is_prime(num): return num >= 2 and all(num % i != 0 for i in range(2, int(math.sqrt(num)) + 1))
def is_palindrome(num): return str(num) == str(num)[::-1]
def is_fibonacci(num): a, b = 0, 1; while b <= num: if b == num: return True; a, b = b, a + b; return False
def vigenere_encrypt(text, key='BEANS'):
    key = key.upper() * (len(text) // len(key) + 1)
    return ''.join(chr((ord(c) - 65 + ord(key[i]) - 65) % 26 + 65) if 'A' <= c <= 'Z' else c for i, c in enumerate(text.upper()))
def to_morse(word):
    MORSE_MAP = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
                 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
                 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..'}
    return ''.join(MORSE_MAP.get(c, '') for c in word.upper())

# Gematria Functions
def law_of_6_cipher(word):
    letter_value = 6
    for _ in range(3):
        letter_value = letter_value * 2 + 6
    value = letter_value * len([c for c in word.upper() if 'A' <= c <= 'Z'])
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT law_of_6_numeric FROM gematria_values GROUP BY law_of_6_numeric ORDER BY COUNT(*) DESC LIMIT 6")
    top_sums = [row[0] for row in cursor.fetchall()]
    conn.close()
    is_law_of_6 = value in top_sums
    return value, word.lower() == word.lower()[::-1], is_law_of_6

def reverse_law_of_6_cipher(word):
    reverse_word = word.upper()[::-1]
    return law_of_6_cipher(reverse_word)

def alw_cipher_gematria(word):
    ALW_MAP = {'A': 1, 'L': 2, 'W': 3, 'H': 4, 'S': 5, 'D': 6, 'O': 7, 'Z': 8, 'K': 9, 'V': 10, 'G': 11, 'R': 12, 'C': 13,
               'N': 14, 'Y': 15, 'J': 16, 'U': 17, 'F': 18, 'Q': 19, 'B': 20, 'M': 21, 'X': 22, 'I': 23, 'T': 24, 'E': 25, 'P': 26}
    value = sum(ALW_MAP.get(c, 0) for c in word.upper())
    return value, value in [351]  # Liber AL key sum

def trigrammaton_gematria(word):
    TRIGRAM_MAP = {'L': 1, 'C': 2, 'H': 3, 'P': 4, 'A': 5, 'X': 6, 'J': 7, 'W': 8, 'T': 9, 'O': 10, 'G': 11, 'F': 12, 'E': 13,
                   'R': 14, 'S': 15, 'Q': 16, 'K': 17, 'Y': 18, 'Z': 19, 'B': 20, 'M': 21, 'V': 22, 'D': 23, 'N': 24, 'U': 25, 'I': 0}
    value = sum(TRIGRAM_MAP.get(c, 0) for c in word.upper())
    base3_str = ''.join(str(value % 3**(i+1) // 3**i) for i in range(int(math.log(value, 3))+1))[::-1] if value else '0'
    return value, base3_str == base3_str[::-1]

def baconian_gematria(word):
    BACON_MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 8, 'K': 9, 'L': 10, 'M': 11,
                 'N': 12, 'O': 13, 'P': 14, 'Q': 15, 'R': 16, 'S': 17, 'T': 18, 'U': 19, 'V': 19, 'W': 20, 'X': 21, 'Y': 22, 'Z': 23}
    value = sum(BACON_MAP.get(c, 0) for c in word.upper())
    bacon_str = ''.join(format(BACON_MAP.get(c, 0), '05b') for c in word.upper())
    return value, bacon_str == bacon_str[::-1]

def ordinal_multiplied_gematria(word):
    value = 1
    for c in word.upper():
        if 'A' <= c <= 'Z':
            value *= (ord(c) - 64)
    return value, is_prime(value)

def chaldean_gematria(word):
    CHALDEAN_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 8, 'G': 3, 'H': 5, 'I': 1, 'J': 1, 'K': 2, 'L': 3, 'M': 4,
                    'N': 5, 'O': 7, 'P': 8, 'Q': 1, 'R': 2, 'S': 3, 'T': 4, 'U': 6, 'V': 6, 'W': 6, 'X': 5, 'Y': 1, 'Z': 7}
    value = sum(CHALDEAN_MAP.get(c, 0) for c in word.upper())
    return value, value in [1, 3, 5, 7]

def golden_ratio_gematria(word):
    phi = 1.618033988749895
    value = sum((ord(c) - 64) * (phi ** (i + 1)) for i, c in enumerate(word.upper()) if 'A' <= c <= 'Z')
    return round(abs(value), 2), is_fibonacci(int(round(abs(value))))

def hexadecimal_position_gematria(word):
    HEX_POS_MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9, 'K': 10, 'L': 11, 'M': 12,
                   'N': 13, 'O': 14, 'P': 15, 'Q': 0, 'R': 1, 'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 10}
    value = sum(HEX_POS_MAP.get(c, 0) for c in word.upper())
    hex_str = hex(value)[2:].upper()
    return value, hex_str == hex_str[::-1]

def sumerian_gematria(word):
    SUMERIAN_MAP = {chr(65+i): 6*(i+1) for i in range(26)}
    value = sum(SUMERIAN_MAP.get(c, 0) for c in word.upper())
    return value, value % 6 == 0

def phone_keypad_gematria(word):
    PHONE_MAP = {'A': 2, 'B': 2, 'C': 2, 'D': 3, 'E': 3, 'F': 3, 'G': 4, 'H': 4, 'I': 4, 'J': 5, 'K': 5, 'L': 5, 'M': 6,
                 'N': 6, 'O': 6, 'P': 7, 'Q': 7, 'R': 7, 'S': 8, 'T': 8, 'U': 8, 'V': 9, 'W': 9, 'X': 9, 'Y': 9, 'Z': 9}
    value = sum(PHONE_MAP.get(c, 0) for c in word.upper())
    keypad_str = ''.join(str(PHONE_MAP.get(c, 0)) for c in word.upper())
    return value, keypad_str == keypad_str[::-1]

def ascii_sum_gematria(word):
    value = sum(ord(c) for c in word)
    return value, str(value) == str(value)[::-1]

# Reverse variants
def reverse_gematria(func): return lambda w: func(w.upper()[::-1])

# Updated CALC_FUNCS
CALC_FUNCS = {
    "Simple": simple_gematria,
    # ... (include all 52 previous methods)
    "Law of 6 Cipher": lambda w: law_of_6_cipher(w)[0],
    "Reverse Law of 6 Cipher": reverse_law_of_6_cipher,
    "ALW Cipher Gematria": lambda w: alw_cipher_gematria(w)[0],
    "Trigrammaton Gematria": lambda w: trigrammaton_gematria(w)[0],
    "Baconian Gematria": lambda w: baconian_gematria(w)[0],
    "Ordinal Multiplied Gematria": lambda w: ordinal_multiplied_gematria(w)[0],
    "Chaldean Gematria": lambda w: chaldean_gematria(w)[0],
    "Golden Ratio Gematria": lambda w: golden_ratio_gematria(w)[0],
    "Hexadecimal Position Gematria": lambda w: hexadecimal_position_gematria(w)[0],
    "Sumerian Gematria": lambda w: sumerian_gematria(w)[0],
    "Phone Keypad Gematria": lambda w: phone_keypad_gematria(w)[0],
    "ASCII Sum Gematria": lambda w: ascii_sum_gematria(w)[0],
    "Reverse ALW Cipher Gematria": reverse_gematria(lambda w: alw_cipher_gematria(w)[0]),
    "Reverse Trigrammaton Gematria": reverse_gematria(lambda w: trigrammaton_gematria(w)[0]),
    "Reverse Baconian Gematria": reverse_gematria(lambda w: baconian_gematria(w)[0]),
    "Reverse Ordinal Multiplied Gematria": reverse_gematria(lambda w: ordinal_multiplied_gematria(w)[0]),
    "Reverse Chaldean Gematria": reverse_gematria(lambda w: chaldean_gematria(w)[0]),
    "Reverse Golden Ratio Gematria": reverse_gematria(lambda w: golden_ratio_gematria(w)[0]),
    "Reverse Hexadecimal Position Gematria": reverse_gematria(lambda w: hexadecimal_position_gematria(w)[0]),
    "Reverse Sumerian Gematria": reverse_gematria(lambda w: sumerian_gematria(w)[0]),
    "Reverse Phone Keypad Gematria": reverse_gematria(lambda w: phone_keypad_gematria(w)[0]),
    "Reverse ASCII Sum Gematria": reverse_gematria(lambda w: ascii_sum_gematria(w)[0])
}

# Updated TRUTH_CONDITIONS
TRUTH_CONDITIONS = {
    'Pure Truth': lambda core, vals: len(core) >= 3 and all(is_prime(v) for v in vals if isinstance(v, (int, float))),
    'Abstract Truth': lambda core, vals: len(core) >= 1 and any(is_palindrome(v) for v in vals if isinstance(v, (int, float))),
    'Ultimate Truth': lambda core, vals: all(is_prime(v) for v in vals if isinstance(v, (int, float))),
    'Palindromic Truth': lambda core, vals: core and core[0].lower() == core[0].lower()[::-1],
    'Musical Truth': lambda core, vals: core and musical_gematria(core[0])[1],
    'Cyclic Truth': lambda core, vals: any(v % 12 == 0 or v % 60 == 0 for v in vals if isinstance(v, (int, float))),
    'Atbash Truth': lambda core, vals: core and atbash_gematria(core[0])[1],
    'Vigenère Truth': lambda core, vals: core and vigenere_gematria(core[0])[1],
    'Morse Truth': lambda core, vals: core and morse_gematria(core[0])[1],
    'Fibonacci Truth': lambda core, vals: any(is_fibonacci(v) for v in vals if isinstance(v, (int, float))),
    'Prime Truth': lambda core, vals: any(is_prime(v) for v in vals if isinstance(v, (int, float))),
    'Law of 6 Truth': lambda core, vals: core and law_of_6_cipher(core[0])[2],
    'ALW Truth': lambda core, vals: core and alw_cipher_gematria(core[0])[1],
    'Trigrammaton Truth': lambda core, vals: core and trigrammaton_gematria(core[0])[1],
    'Baconian Truth': lambda core, vals: core and baconian_gematria(core[0])[1],
    'Multiplied Truth': lambda core, vals: core and ordinal_multiplied_gematria(core[0])[1],
    'Chaldean Truth': lambda core, vals: core and chaldean_gematria(core[0])[1],
    'Golden Truth': lambda core, vals: core and golden_ratio_gematria(core[0])[1],
    'Hex Truth': lambda core, vals: core and hexadecimal_position_gematria(core[0])[1],
    'Sumerian Truth': lambda core, vals: core and sumerian_gematria(core[0])[1],
    'Phone Truth': lambda core, vals: core and phone_keypad_gematria(core[0])[1],
    'ASCII Truth': lambda core, vals: core and ascii_sum_gematria(core[0])[1],
    'No Interpretive Relationship': lambda core, vals: not core and not any(is_prime(v) or is_palindrome(v) for v in vals if isinstance(v, (int, float)))
}

# Database integration
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gematria_values (
            word TEXT PRIMARY KEY,
            law_of_6_numeric REAL,
            alw_cipher_gematria INTEGER,
            trigrammaton_gematria INTEGER,
            baconian_gematria INTEGER,
            ordinal_multiplied_gematria INTEGER,
            chaldean_gematria INTEGER,
            golden_ratio_gematria REAL,
            hexadecimal_position_gematria INTEGER,
            sumerian_gematria INTEGER,
            phone_keypad_gematria INTEGER,
            ascii_sum_gematria INTEGER,
            is_palindromic BOOLEAN,
            is_law_of_6 BOOLEAN,
            is_alw BOOLEAN,
            is_trigrammaton BOOLEAN,
            is_baconian BOOLEAN,
            is_multiplied BOOLEAN,
            is_chaldean BOOLEAN,
            is_golden BOOLEAN,
            is_hex BOOLEAN,
            is_sumerian BOOLEAN,
            is_phone BOOLEAN,
            is_ascii BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

def store_gematria_values(word):
    values = {
        'law_of_6_numeric': law_of_6_cipher(word)[0],
        'alw_cipher_gematria': alw_cipher_gematria(word)[0],
        'trigrammaton_gematria': trigrammaton_gematria(word)[0],
        'baconian_gematria': baconian_gematria(word)[0],
        'ordinal_multiplied_gematria': ordinal_multiplied_gematria(word)[0],
        'chaldean_gematria': chaldean_gematria(word)[0],
        'golden_ratio_gematria': golden_ratio_gematria(word)[0],
        'hexadecimal_position_gematria': hexadecimal_position_gematria(word)[0],
        'sumerian_gematria': sumerian_gematria(word)[0],
        'phone_keypad_gematria': phone_keypad_gematria(word)[0],
        'ascii_sum_gematria': ascii_sum_gematria(word)[0],
        'is_palindromic': word.lower() == word.lower()[::-1],
        'is_law_of_6': law_of_6_cipher(word)[2],
        'is_alw': alw_cipher_gematria(word)[1],
        'is_trigrammaton': trigrammaton_gematria(word)[1],
        'is_baconian': baconian_gematria(word)[1],
        'is_multiplied': ordinal_multiplied_gematria(word)[1],
        'is_chaldean': chaldean_gematria(word)[1],
        'is_golden': golden_ratio_gematria(word)[1],
        'is_hex': hexadecimal_position_gematria(word)[1],
        'is_sumerian': sumerian_gematria(word)[1],
        'is_phone': phone_keypad_gematria(word)[1],
        'is_ascii': ascii_sum_gematria(word)[1]
    }
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO gematria_values
        (word, law_of_6_numeric, alw_cipher_gematria, trigrammaton_gematria, baconian_gematria,
         ordinal_multiplied_gematria, chaldean_gematria, golden_ratio_gematria,
         hexadecimal_position_gematria, sumerian_gematria, phone_keypad_gematria,
         ascii_sum_gematria, is_palindromic, is_law_of_6, is_alw, is_trigrammaton,
         is_baconian, is_multiplied, is_chaldean, is_golden, is_hex, is_sumerian, is_phone, is_ascii)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (word.lower(), *values.values()))
    conn.commit()
    conn.close()
    logging.debug(f"Stored gematria values for '{word}'")

# Sentence Prediction
ESOTERIC_TEMPLATES_STATEMENT = [
    "{word1} {symbol1} weaves {word2} {symbol2} in {color} light ({truth}).",
    "In {color}, {word1} {symbol1} and {word2} {symbol2} pulse with {word3} {symbol3} ({truth}).",
    "{word1} {symbol1} resonates with {word2} in {color} ({truth})."
]

def predict_next_sentence(input_sentence):
    words = re.findall(r"\b[A-Za-z']+\b", input_sentence.lower())
    tagged = pos_tag(word_tokenize(input_sentence))
    pos_structure = ' '.join(tag for _, tag in tagged)
    input_values = {method: [CALC_FUNCS[method](w) for w in words] for method in CALC_FUNCS}
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT reply, score FROM feedback WHERE score > 0")
    templates = cursor.fetchall()
    template = max(templates, key=lambda x: x[1])[0] if templates else random.choice(ESOTERIC_TEMPLATES_STATEMENT)
    candidate_words = []
    cursor.execute("SELECT word FROM gematria_values WHERE is_law_of_6 = 1 OR is_palindromic = 1")
    candidate_words.extend(w[0] for w in cursor.fetchall())
    for method in input_values:
        for val in input_values[method]:
            cursor.execute(f"SELECT word FROM gematria_values WHERE {method.lower().replace(' ', '_')}_numeric BETWEEN ? AND ?", (val-5, val+5))
            candidate_words.extend(w[0] for w in cursor.fetchall())
    conn.close()
    candidate_words = list(set(candidate_words) - set(words))
    if len(candidate_words) < 3:
        candidate_words.extend(['love', 'hope', 'spiral'][:3-len(candidate_words)])
    selected_words = random.sample(candidate_words, min(3, len(candidate_words)))
    return template.format(word1=selected_words[0], word2=selected_words[1] if len(selected_words) > 1 else 'truth',
                          word3=selected_words[2] if len(selected_words) > 2 else 'vibe',
                          symbol1='🌀', symbol2='✨', symbol3='🌌', color='Purple', truth='Law of 6 Truth')

# Example main
def main():
    init_db()
    words = ["CAT", "DEED"]
    for word in words:
        logging.info(f"\n--- Gematria for {word} ---")
        for name, func in CALC_FUNCS.items():
            try:
                value = func(word)
                logging.info(f"{name}: {value}")
            except Exception as e:
                logging.error(f"Error in {name} for {word}: {e}")
        store_gematria_values(word)
        truth = [k for k, v in TRUTH_CONDITIONS.items() if v([word] if is_prime(simple_gematria(word)) else [], [func(word) if isinstance(func(word), (int, float)) else func(word)[1] for func in CALC_FUNCS.values()])]
        logging.info(f"Truth Conditions: {truth}")
        if word.lower() == word.lower()[::-1]:
            logging.info(f"{word} is Palindromic Truth! 🌀")
        if law_of_6_cipher(word)[2]:
            logging.info(f"{word} is Law of 6 Truth! 🎶")
        predicted = predict_next_sentence(word)
        logging.info(f"Predicted Next Sentence: {predicted}")

if __name__ == "__main__":
    main()
```
</