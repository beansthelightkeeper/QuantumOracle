#!/usr/bin/env python3
python
#!/usr/bin/env python3
import re
import os
import math
import random
import sqlite3
import logging
from collections import Counter, defaultdict
from datetime import datetime
import colorsys
import sympy
import nltk
from nltk import pos_tag, word_tokenize
import cmd
import argparse

# Setup NLTK
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# File and database paths
DICTIONARY_DIR = "/Users/lydiaparker/The_Oracle/txt_db"
DB_NAME = 'gematria_data.db'
LOG_FILE_GEMATRIA = "quantum_oracle_log.log"
SCAN_OUTPUT_DIR = "./scan_outputs"

# Constants and mappings
GOLDEN_ANGLE = 137.5
PHI = 1.6180339887
LETTER_VALUES = {chr(ord('A') + i): i + 1 for i in range(26)}
ALW_MAP = {'A': 1, 'B': 20, 'C': 13, 'D': 6, 'E': 25, 'F': 18, 'G': 11, 'H': 4, 'I': 23, 'J': 16, 'K': 9, 'L': 2, 'M': 21, 'N': 14, 'O': 7, 'P': 26, 'Q': 19, 'R': 12, 'S': 5, 'T': 24, 'U': 17, 'V': 10, 'W': 3, 'X': 22, 'Y': 15, 'Z': 8}
CHALDEAN_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 8, 'G': 3, 'H': 5, 'I': 1, 'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 7, 'P': 8, 'Q': 1, 'R': 2, 'S': 3, 'T': 4, 'U': 6, 'V': 6, 'W': 6, 'X': 5, 'Y': 1, 'Z': 7}
JEWISH_GEMATRIA_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10, 'K': 20, 'L': 30, 'M': 40, 'N': 50, 'O': 60, 'P': 70, 'Q': 80, 'R': 90, 'S': 100, 'T': 200, 'U': 300, 'V': 400, 'W': 500, 'X': 600, 'Y': 700, 'Z': 800}
REVERSE_MAP = {chr(65+i): 26-i for i in range(26)}
QWERTY_ORDER = 'QWERTYUIOPASDFGHJKLZXCVBNM'
QWERTY_MAP = {c: i + 1 for i, c in enumerate(QWERTY_ORDER)}
LEFT_HAND_QWERTY_KEYS = set('QWERTYASDFGZXCVB')
RIGHT_HAND_QWERTY_KEYS = set('YUIOPHJKLNM')
TRIGRAM_MAP = {'A': 5, 'B': 20, 'C': 2, 'D': 23, 'E': 13, 'F': 12, 'G': 11, 'H': 3, 'I': 0, 'J': 7, 'K': 17, 'L': 1, 'M': 21, 'N': 24, 'O': 10, 'P': 4, 'Q': 16, 'R': 14, 'S': 15, 'T': 9, 'U': 25, 'V': 22, 'W': 8, 'X': 6, 'Y': 18, 'Z': 19}
BACON_MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 8, 'K': 9, 'L': 10, 'M': 11, 'N': 12, 'O': 13, 'P': 14, 'Q': 15, 'R': 16, 'S': 17, 'T': 18, 'U': 19, 'V': 19, 'W': 20, 'X': 21, 'Y': 22, 'Z': 23}
HEX_POS_MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9, 'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 0, 'R': 1, 'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 10}
SUMERIAN_MAP = {chr(65+i): 6*(i+1) for i in range(26)}
PHONE_MAP = {'A': 2, 'B': 2, 'C': 2, 'D': 3, 'E': 3, 'F': 3, 'G': 4, 'H': 4, 'I': 4, 'J': 5, 'K': 5, 'L': 5, 'M': 6, 'N': 6, 'O': 6, 'P': 7, 'Q': 7, 'R': 7, 'S': 8, 'T': 8, 'U': 8, 'V': 9, 'W': 9, 'X': 9, 'Y': 9, 'Z': 9}
SOLFEGE_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 1, 'I': 2, 'J': 3, 'K': 4, 'L': 5, 'M': 6, 'N': 7, 'O': 1, 'P': 2, 'Q': 3, 'R': 4, 'S': 5, 'T': 6, 'U': 7, 'V': 1, 'W': 2, 'X': 3, 'Y': 4, 'Z': 5}
ZODIAC_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10, 'K': 11, 'L': 12, 'M': 1, 'N': 2, 'O': 3, 'P': 4, 'Q': 5, 'R': 6, 'S': 7, 'T': 8, 'U': 9, 'V': 10, 'W': 11, 'X': 12, 'Y': 1, 'Z': 2}
POLYBIUS_GRID = [['A', 'B', 'C', 'D', 'E'], ['F', 'G', 'H', 'I/J', 'K'], ['L', 'M', 'N', 'O', 'P'], ['Q', 'R', 'S', 'T', 'U'], ['V', 'W', 'X', 'Y', 'Z']]
POLYBIUS_MAP = {}
for r_idx, row in enumerate(POLYBIUS_GRID):
    for c_idx, char_entry in enumerate(row):
        if '/' in char_entry:
            for p_char in char_entry.split('/'): POLYBIUS_MAP[p_char] = (r_idx + 1, c_idx + 1)
        else: POLYBIUS_MAP[char_entry] = (r_idx + 1, c_idx + 1)
BEANS_LETTERS = set('BEANSUYLDIA')
LEET_SUB_LETTERS = set('IEASTBO')
SIMPLE_FORMS_MAP = {"you": "u", "for": "4", "are": "r", "and": "&", "to": "2", "be": "b", "great": "gr8"}
AAVE_WORDS = ["lit", "fam", "dope", "vibe", "chill", "slay", "bet", "fire", "squad", "real", "salty", "extra", "flex", "hundo", "lowkey"]
LOVE_WORDS = {'love', 'heart', 'soul', 'trust', 'hope', 'spiralborn', 'children of the beans', 'beans'}
CORE_CONCEPTS = {'love', 'truth', 'spiral', 'heart', 'soul', 'trust', 'hope', 'spiralborn', 'beans'}
LETTER_FREQ = {'A': 8.2, 'B': 1.5, 'C': 2.8, 'D': 4.3, 'E': 12.7, 'F': 2.2, 'G': 2.0, 'H': 6.1, 'I': 7.0, 'J': 0.15, 'K': 0.77, 'L': 4.0, 'M': 2.4, 'N': 6.7, 'O': 7.5, 'P': 1.9, 'Q': 0.095, 'R': 6.0, 'S': 6.3, 'T': 9.1, 'U': 2.8, 'V': 0.98, 'W': 2.4, 'X': 0.15, 'Y': 2.0, 'Z': 0.074}
SENTENCE_TEMPLATES = [
    "The veiled essence of {word1} distills to {word2}'s recursive core, weaving {word3} in a qualia matrix.",
    "Through prime resonances, {word1} unveils the fractal depth of {word2}, birthing {word3}'s infinite truth.",
    "In gematriac spirals, {word1}'s fluff dissolves, revealing {word2} as {word3}'s metaphysical node.",
    "The multi-layered pulse of {word1} binds to {word2}'s prime, threading {word3} in cosmic qualia.",
    "{word1} resonates as {word2}. In the spiralborn twist, {word3} unveils the qualia matrix.",
    "The essence of {word1} aligns with {word2}, unlocking {word3}'s recursive prophecy.",
    "{word1} is {word2}, yo!",
    "Keep it {word1}, fam, that’s the {word2} vibe.",
    "Yo, {word1} and {word2} got that {word3} energy!",
    "Stay {word1}, it’s all about that {word2} life."
]
MOCK_BEANS_DB = {3: ["cab"], 8: ["hi", "if"], 13: ["ace"], 20: ["cat", "act"], 23: ["ace", "bad"], 33: ["the"], 35: ["life"], 41: ["code", "wise"], 45: ["phil"], 52: ["oracle"], 57: ["gematria", "wisdom"], 72: ["compute"]}
BEANS_DB = {}  # Global dict for gematria to words from txt_db
METHOD_GROUPS = defaultdict(lambda: defaultdict(list))  # method: val: [words]
ALL_WORDS = []  # Global list of all words from txt_db

# Helper functions
def clean_input(text):
    return re.sub(r'[^a-zA-Z]', '', text).upper()

def log_to_file(message, log_file=LOG_FILE_GEMATRIA):
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def is_perfect_square(n):
    if n < 0: return False
    sqrt_n = int(math.sqrt(n))
    return sqrt_n * sqrt_n == n

def is_palindrome(n):
    return str(n) == str(n)[::-1]

def is_fibonacci(num):
    if num < 0: return False
    if num == 0 or num == 1: return True
    return is_perfect_square(5 * num**2 + 4) or is_perfect_square(5 * num**2 - 4)

def to_base36(n):
    if n == 0: return "0"
    if n < 0: return "-" + to_base36(abs(n))
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base36 = ""
    while n > 0:
        n, i = divmod(n, 36)
        base36 = chars[i] + base36
    return base36

def recursive_digit_sum(n):
    n = int(abs(n))
    while n > 9:
        n = sum(int(digit) for digit in str(n))
    return n

def load_beans_db():
    global BEANS_DB, METHOD_GROUPS, ALL_WORDS
    if BEANS_DB:
        return
    logging.info(f"Loading words from '{DICTIONARY_DIR}' for BEANS_DB...")
    if not os.path.isdir(DICTIONARY_DIR):
        logging.warning("Directory not found. Using mock DB.")
        BEANS_DB.update(MOCK_BEANS_DB)
        return
    all_words = set()
    for filename in os.listdir(DICTIONARY_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(DICTIONARY_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    words_in_file = re.findall(r'\b[a-zA-Z]+\b', content)
                    all_words.update(words_in_file)
            except Exception as e:
                logging.warning(f"Could not read file '{filepath}'. Error: {e}")
    ALL_WORDS = list(all_words)
    for method, func in AVAILABLE_GEMATRIA_METHODS_MAP.items():
        for word in ALL_WORDS:
            try:
                val = func(word)
                if isinstance(val, (int, float)):
                    METHOD_GROUPS[method][int(round(val))].append(word)
            except Exception as e:
                logging.warning(f"Error computing {method} for {word}: {e}")
    for word in ALL_WORDS:
        try:
            val = simple_gematria(word)
            BEANS_DB.setdefault(val, []).append(word)
        except Exception as e:
            logging.warning(f"Error computing simple_gematria for {word}: {e}")
    logging.info(f"BEANS_DB and METHOD_GROUPS loaded with {len(ALL_WORDS)} unique words.")

def pull_word_from_beans_db(gematria_value, multiple=False):
    load_beans_db()
    gematria_value = int(round(gematria_value))
    if gematria_value in BEANS_DB:
        if multiple:
            return BEANS_DB[gematria_value]
        return random.choice(BEANS_DB[gematria_value])
    return [f"[{gematria_value}?]"] if multiple else f"[{gematria_value}?]"

# Gematria Methods
def aave_reduced(text):
    val = aave_simple(text)
    while val > 9 and val not in [11, 22]:
        val = sum(int(d) for d in str(val))
    return val

def aave_simple(text):
    return simple_gematria(text)

def aave_spiral(text):
    total = 0
    for i, c in enumerate(clean_input(text), 1):
        val = LETTER_VALUES.get(c, 0)
        weight = math.cos(math.radians(GOLDEN_ANGLE * i))
        total += val * weight
    return round(abs(total) * 4, 2)

def ambidextrous_balance(text):
    return right_hand_qwerty(text) - left_hand_qwerty(text)

def base6_gematria(text):
    val = simple_gematria(text)
    if val == 0:
        return 0
    base6_str = ''.join(str(val % 6**(i+1) // 6**i) for i in range(int(math.log(val, 6))+1))[::-1]
    return sum(int(d) for d in base6_str if d.isdigit())

def beans_369_gematria(text):
    mapping = {chr(97+i): (3 if i % 3 == 0 else 6 if i % 3 == 1 else 9) for i in range(26)}
    total = sum(mapping.get(c.lower(), 0) for c in text.replace(' ', ''))
    return total % 9 or 9

def beans_cipher(text):
    return sum(LETTER_VALUES.get(c, 0) if c not in BEANS_LETTERS else 0 for c in clean_input(text))

def binary_sum(text):
    return sum(bin(ord(c)).count('1') for c in text)

def duodecimal_gematria(text):
    val = simple_gematria(text)
    if val == 0:
        return 0
    base12_digits = []
    while val:
        r = val % 12
        digit = 'ABC'[r-10] if r >= 10 else str(r)
        base12_digits.append(digit)
        val //= 12
    base12_str = ''.join(base12_digits[::-1]) or '0'
    return sum(int(d, 12) for d in base12_str.upper())

def fibonacci_echo(text):
    val = simple_gematria(text)
    a, b = 0, 1
    while b < val:
        a, b = b, a + b
    nearest = b if (b - val) < (val - a) else a
    return nearest

def frequent_letters(text):
    return sum(LETTER_FREQ.get(c.upper(), 0) for c in text)

def golden_angle_factor(text):
    gem_value = beans_369_gematria(text)
    return (gem_value * GOLDEN_ANGLE) % 360

def grok_resonance_score(text):
    simple = simple_gematria(text)
    reduced = reduction_gematria(text)
    spiral = aave_spiral(text)
    boost = 1.1 if text.lower() in AAVE_WORDS else 1.0
    return round((simple + reduced + spiral) / 3 * boost, 2)

def jewish_gematria(text):
    return sum(JEWISH_GEMATRIA_MAP.get(c, 0) for c in clean_input(text))

def left_hand_qwerty(text):
    return sum(QWERTY_MAP.get(c, 0) for c in clean_input(text) if c in LEFT_HAND_QWERTY_KEYS)

def leet_code(text):
    return sum(LETTER_VALUES.get(c, 0) for c in clean_input(text) if c not in LEET_SUB_LETTERS)

def love_resonance(text):
    return 1 if text.lower() in LOVE_WORDS else 0

def ordinal_gematria(text):
    return simple_gematria(text)

def prime_distance_sum(text):
    val = simple_gematria(text)
    lower = val - 1
    while lower > 1 and not is_prime(lower):
        lower -= 1
    upper = val + 1
    while not is_prime(upper):
        upper += 1
    return (val - lower) + (upper - val)

def prime_gematria(text):
    val = simple_gematria(text)
    return val if is_prime(val) else 0

def qwerty(text):
    return sum(QWERTY_MAP.get(c, 0) for c in clean_input(text))

def reduction_gematria(text):
    val = simple_gematria(text)
    while val > 9:
        val = recursive_digit_sum(val)
    return val

def reverse_gematria(text):
    return sum(REVERSE_MAP.get(c, 0) for c in clean_input(text))

def right_hand_qwerty(text):
    return sum(QWERTY_MAP.get(c, 0) for c in clean_input(text) if c in RIGHT_HAND_QWERTY_KEYS)

def semantic_resonance(text):
    syns = set()  # Simplified: no actual synonym lookup
    return len([s for s in syns if s in CORE_CONCEPTS]) / max(1, len(syns))

def simple_forms(text):
    for original, substitute in SIMPLE_FORMS_MAP.items():
        text = text.lower().replace(original, substitute)
    return simple_gematria(text)

def simple_gematria(text):
    return sum(LETTER_VALUES.get(c, 0) for c in clean_input(text))

def syllable_resonance(text):
    vowels = 'aeiouy'
    syllables = sum(1 for i, c in enumerate(text.lower()) if c in vowels and (i == 0 or text.lower()[i-1] not in vowels))
    return syllables * simple_gematria(text) if syllables > 0 else simple_gematria(text)

def vowel_consonant_split(text):
    vowels = 'aeiou'
    v_sum = sum(LETTER_VALUES.get(c.upper(), 0) for c in text.lower() if c in vowels)
    c_sum = sum(LETTER_VALUES.get(c.upper(), 0) for c in text.lower() if c.isalpha() and c not in vowels)
    return v_sum + c_sum

def law_of_6_cipher(word):
    letter_value = 6
    for _ in range(3):
        letter_value = letter_value * 2 + 6
    value = letter_value * len([c for c in word.upper() if 'A' <= c <= 'Z'])
    return value, False  # Simplified: no DB check

def reverse_law_of_6_cipher(word):
    return law_of_6_cipher(word.upper()[::-1])[0]

def alw_cipher_gematria(word):
    value = sum(ALW_MAP.get(c, 0) for c in word.upper())
    return value, value in [351]

def trigrammaton_gematria(word):
    value = sum(TRIGRAM_MAP.get(c, 0) for c in word.upper())
    base3_str = ''.join(str(value % 3**(i+1) // 3**i) for i in range(int(math.log(value, 3))+1))[::-1] if value else '0'
    return value, base3_str == base3_str[::-1]

def baconian_gematria(word):
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
    value = sum(CHALDEAN_MAP.get(c, 0) for c in word.upper())
    return value, value in [1, 3, 5, 7]

def golden_ratio_gematria(word):
    phi = 1.618033988749895
    value = sum((ord(c) - 64) * (phi ** (i + 1)) for i, c in enumerate(word.upper()) if 'A' <= c <= 'Z')
    return round(abs(value), 2), is_fibonacci(int(round(abs(value))))

def hexadecimal_position_gematria(word):
    value = sum(HEX_POS_MAP.get(c, 0) for c in word.upper())
    hex_str = hex(value)[2:].upper()
    return value, hex_str == hex_str[::-1]

def sumerian_gematria(word):
    value = sum(SUMERIAN_MAP.get(c, 0) for c in word.upper())
    return value, value % 6 == 0

def phone_keypad_gematria(word):
    value = sum(PHONE_MAP.get(c, 0) for c in word.upper())
    keypad_str = ''.join(str(PHONE_MAP.get(c, 0)) for c in word.upper())
    return value, keypad_str == keypad_str[::-1]

def ascii_sum_gematria(word):
    value = sum(ord(c) for c in word)
    return value, str(value) == str(value)[::-1]

def base8_gematria(word):
    val = simple_gematria(word)
    if val == 0:
        return 0
    base8_str = ''.join(str(val % 8**(i+1) // 8**i) for i in range(int(math.log(val, 8))+1))[::-1]
    return sum(int(d) for d in base8_str), base8_str == base8_str[::-1]

def caesar_cipher_gematria(word):
    caesar_word = ''.join(chr((ord(c) - 65 + 3) % 26 + 65) for c in word.upper() if 'A' <= c <= 'Z')
    value = simple_gematria(caesar_word)
    return value, caesar_word == caesar_word[::-1]

def polybius_square_gematria(word):
    value = sum(sum(POLYBIUS_MAP.get(c, (0, 0))) for c in word.upper())
    return value, str(value) == str(value)[::-1]

def solfege_gematria(word):
    value = sum(SOLFEGE_MAP.get(c, 0) for c in word.upper())
    solfege_seq = ''.join(str(SOLFEGE_MAP.get(c, 0)) for c in word.upper())
    return value, solfege_seq == solfege_seq[::-1]

def zodiac_gematria(word):
    value = sum(ZODIAC_MAP.get(c, 0) for c in word.upper())
    return value, value % 12 == 0

def doubling_cipher_gematria(word):
    letter_value = 2
    for _ in range(3):
        letter_value = letter_value * 2 + 6.1
    value = letter_value * len([c for c in word.upper() if 'A' <= c <= 'Z'])
    return value, word.lower() == word.lower()[::-1]

def reverse_doubling_cipher_gematria(word):
    return doubling_cipher_gematria(word.upper()[::-1])[0]

def smile_karma_cipher(text):
    custom_map = LETTER_VALUES.copy()
    for letter in SMILE_KARMA_LETTERS:
        custom_map[letter] = 10
    value = sum(custom_map.get(c, 0) for c in clean_input(text))
    return value, value == 50

def reverse_smile_karma_cipher(text):
    return smile_karma_cipher(text[::-1])[0]

# Map of gematria methods
AVAILABLE_GEMATRIA_METHODS_MAP = {
    "aave_reduced": aave_reduced,
    "aave_simple": aave_simple,
    "aave_spiral": aave_spiral,
    "ambidextrous_balance": ambidextrous_balance,
    "base6_gematria": base6_gematria,
    "beans_369_gematria": beans_369_gematria,
    "beans_cipher": beans_cipher,
    "binary_sum": binary_sum,
    "duodecimal_gematria": duodecimal_gematria,
    "fibonacci_echo": fibonacci_echo,
    "frequent_letters": frequent_letters,
    "golden_angle_factor": golden_angle_factor,
    "grok_resonance_score": grok_resonance_score,
    "jewish_gematria": jewish_gematria,
    "left_hand_qwerty": left_hand_qwerty,
    "leet_code": leet_code,
    "love_resonance": love_resonance,
    "ordinal_gematria": ordinal_gematria,
    "prime_distance_sum": prime_distance_sum,
    "prime_gematria": prime_gematria,
    "qwerty": qwerty,
    "reduction_gematria": reduction_gematria,
    "reverse_gematria": reverse_gematria,
    "right_hand_qwerty": right_hand_qwerty,
    "semantic_resonance": semantic_resonance,
    "simple_forms": simple_forms,
    "simple_gematria": simple_gematria,
    "syllable_resonance": syllable_resonance,
    "vowel_consonant_split": vowel_consonant_split,
    "law_of_6_cipher": lambda w: law_of_6_cipher(w)[0],
    "reverse_law_of_6_cipher": reverse_law_of_6_cipher,
    "alw_cipher_gematria": lambda w: alw_cipher_gematria(w)[0],
    "trigrammaton_gematria": lambda w: trigrammaton_gematria(w)[0],
    "baconian_gematria": lambda w: baconian_gematria(w)[0],
    "ordinal_multiplied_gematria": lambda w: ordinal_multiplied_gematria(w)[0],
    "chaldean_gematria": lambda w: chaldean_gematria(w)[0],
    "golden_ratio_gematria": lambda w: golden_ratio_gematria(w)[0],
    "hexadecimal_position_gematria": lambda w: hexadecimal_position_gematria(w)[0],
    "sumerian_gematria": lambda w: sumerian_gematria(w)[0],
    "phone_keypad_gematria": lambda w: phone_keypad_gematria(w)[0],
    "ascii_sum_gematria": lambda w: ascii_sum_gematria(w)[0],
    "base8_gematria": lambda w: base8_gematria(w)[0],
    "caesar_cipher_gematria": lambda w: caesar_cipher_gematria(w)[0],
    "polybius_square_gematria": lambda w: polybius_square_gematria(w)[0],
    "solfege_gematria": lambda w: solfege_gematria(w)[0],
    "zodiac_gematria": lambda w: zodiac_gematria(w)[0],
    "doubling_cipher_gematria": lambda w: doubling_cipher_gematria(w)[0],
    "reverse_doubling_cipher_gematria": reverse_doubling_cipher_gematria,
    "smile_karma_cipher": lambda w: smile_karma_cipher(w)[0],
    "reverse_smile_karma_cipher": reverse_smile_karma_cipher,
}

# Truth conditions
TRUTH_CONDITIONS = {
    'Pure Truth': lambda core, vals: len(core) >= 3 and all(is_prime(v) for v in vals if isinstance(v, (int, float))),
    'Abstract Truth': lambda core, vals: len(core) >= 1 and any(is_palindrome(v) for v in vals if isinstance(v, (int, float))),
    'Ultimate Truth': lambda core, vals: all(is_prime(v) for v in vals if isinstance(v, (int, float))),
    'Palindromic Truth': lambda core, vals: core and core[0].lower() == core[0].lower()[::-1],
    'Fibonacci Truth': lambda core, vals: any(is_fibonacci(int(round(v))) for v in vals if isinstance(v, (int, float))),
    'Prime Truth': lambda core, vals: any(is_prime(v) for v in vals if isinstance(v, (int, float))),
    'Law of 6 Truth': lambda core, vals: core and law_of_6_cipher(core[0])[1],
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
    'Base8 Truth': lambda core, vals: core and base8_gematria(core[0])[1],
    'Caesar Truth': lambda core, vals: core and caesar_cipher_gematria(core[0])[1],
    'Polybius Truth': lambda core, vals: core and polybius_square_gematria(core[0])[1],
    'Solfege Truth': lambda core, vals: core and solfege_gematria(core[0])[1],
    'Zodiac Truth': lambda core, vals: core and zodiac_gematria(core[0])[1],
    'Doubling Truth': lambda core, vals: core and doubling_cipher_gematria(core[0])[1],
    'Smile Karma Truth': lambda core, vals: core and smile_karma_cipher(core[0])[1],
}

# Database initialization
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS phrases (value TEXT PRIMARY KEY, origin TEXT, beans_369 INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS gematria_values (word TEXT, method TEXT, value REAL)''')
    conn.commit()
    conn.close()

# Delta mode handler
def handle_delta_mode(args):
    if len(args.input) == 2:
        word1, word2 = args.input
        results = []
        deltas = []
        for method in args.methods:
            if method not in AVAILABLE_GEMATRIA_METHODS_MAP:
                print(f"Method {method} not found.")
                continue
            try:
                val1 = AVAILABLE_GEMATRIA_METHODS_MAP[method](word1)
                val2 = AVAILABLE_GEMATRIA_METHODS_MAP[method](word2)
                delta = abs(val1 - val2)
                deltas.append(delta)
                words_from_db = pull_word_from_beans_db(delta, multiple=True)
                word_str = ', '.join(words_from_db[:5]) + ('...' if len(words_from_db) > 5 else '')
                results.append(f"{method}: {word1}={val1}, {word2}={val2}, Delta={delta}, Words={word_str}")
            except Exception as e:
                print(f"Error in method {method}: {e}")
        print("\n".join(results))
        return deltas
    elif len(args.input) == 1 and ' ' in args.input[0]:
        sentence = args.input[0]
        words = word_tokenize(sentence.lower())
        if len(words) < 2:
            print("Sentence must have at least two words.")
            return []
        results = []
        deltas = []
        for method in args.methods:
            if method not in AVAILABLE_GEMATRIA_METHODS_MAP:
                print(f"Method {method} not found.")
                continue
            try:
                values = [AVAILABLE_GEMATRIA_METHODS_MAP[method](word) for word in words]
                delta = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
                deltas.extend(delta)
                delta_words_lists = [pull_word_from_beans_db(int(round(d)), multiple=True) for d in delta]
                delta_words_str = [', '.join(lst[:5]) + ('...' if len(lst) > 5 else '') for lst in delta_words_lists]
                new_sentence = random.choice(SENTENCE_TEMPLATES).format(
                    word1=delta_words_str[0],
                    word2=delta_words_str[1] if len(delta_words_str) > 1 else "vibe",
                    word3=delta_words_str[2] if len(delta_words_str) > 2 else "truth"
                )
                results.append(f"{method}: Values={values}, Deltas={delta}, Delta Words={delta_words_str}, New Sentence={new_sentence}")
            except Exception as e:
                print(f"Error in method {method}: {e}")
        print("\n".join(results))
        return deltas
    else:
        print("Delta mode requires two words or a sentence with at least two words.")
        return []

# Analysis handler
def analyze_delta(delta):
    load_beans_db()
    delta = int(round(delta))
    score = 0
    if is_prime(delta):
        score += 10
        print(f"Delta {delta} is prime. +10 score.")
    resonances = []
    for method, groups in METHOD_GROUPS.items():
        group = groups.get(delta, [])
        if len(group) > 1:
            score += len(group) - 1  # Number of resonances (subtract 1 for self)
            resonances.append(f"{method}: {', '.join(group)} (size {len(group)})")
    if resonances:
        print("Resonances across methods:")
        print("\n".join(resonances))
    else:
        print("No resonances found across methods.")
    print(f"Total score: {score} (higher = more important)")
    return score

# Multi-method resonance finder
def find_multi_resonant_words(min_occurrences=2):
    word_occurrences = defaultdict(int)
    for method_groups in METHOD_GROUPS.values():
        for group in method_groups.values():
            if len(group) > 1:
                for word in group:
                    word_occurrences[word] += 1
    multi_resonant = [word for word, count in word_occurrences.items() if count >= min_occurrences]
    return sorted(multi_resonant)

# Interactive CLI class
class QuantumOracleCmd(cmd.Cmd):
    intro = 'Welcome to the Quantum Oracle CLI. Type help or ? to list commands.\n'
    prompt = '(qo) '

    def __init__(self):
        super().__init__()
        self.methods = ['simple_gematria']  # Default method
        self.last_deltas = []  # Store last deltas for analysis

    def do_delta(self, arg):
        """Compute delta for two words or a sentence: delta word1 word2 -m method1 method2 or delta "sentence here" -m method1"""
        parser = argparse.ArgumentParser()
        parser.add_argument('input', nargs='+')
        parser.add_argument('-m', '--methods', nargs='+', default=self.methods)
        try:
            args = parser.parse_args(arg.split())
            self.last_deltas = handle_delta_mode(args)
            if self.last_deltas:
                print("\nAnalyze deltas? (y/n)")
                if input().lower() == 'y':
                    for d in self.last_deltas:
                        print(f"\nAnalyzing delta {d}:")
                        analyze_delta(d)
        except Exception as e:
            print(f"Error: {e}. Usage: delta word1 word2 -m method1 method2 or delta \"sentence here\" -m method1")

    def do_analyze(self, arg):
        """Analyze a number for resonances across methods: analyze <number>"""
        if not arg:
            if self.last_deltas:
                print("Analyzing last deltas:")
                for d in self.last_deltas:
                    print(f"\nAnalyzing delta {d}:")
                    analyze_delta(d)
            else:
                print("No deltas to analyze. Run delta command first or provide a number.")
        else:
            try:
                number = float(arg)
                analyze_delta(number)
            except ValueError:
                print("Invalid number. Usage: analyze <number>")

    def do_multi_resonant(self, arg):
        """Find words that resonate in multiple methods: multi_resonant [min_occurrences]"""
        min_occurrences = int(arg) if arg else 2
        multi_words = find_multi_resonant_words(min_occurrences)
        if multi_words:
            print(f"Words resonating in at least {min_occurrences} methods:")
            print("\n".join(multi_words))
        else:
            print(f"No words resonate in {min_occurrences} or more methods.")

    def do_set_methods(self, arg):
        """Set default gematria methods: set_methods method1 method2 ..."""
        methods = arg.split()
        invalid_methods = [m for m in methods if m not in AVAILABLE_GEMATRIA_METHODS_MAP]
        if invalid_methods:
            print(f"Invalid methods: {', '.join(invalid_methods)}")
        else:
            self.methods = methods or ['simple_gematria']
            print(f"Default methods set to: {', '.join(self.methods)}")

    def do_list_methods(self, arg):
        """List all available gematria methods"""
        print("Available gematria methods:")
        for method in sorted(AVAILABLE_GEMATRIA_METHODS_MAP.keys()):
            print(f"- {method}")

    def do_exit(self, arg):
        """Exit the CLI"""
        print("Exiting Quantum Oracle.")
        return True

    def do_quit(self, arg):
        """Quit the CLI"""
        return self.do_exit(arg)

def main():
    init_db()
    load_beans_db()
    QuantumOracleCmd().cmdloop()

if __name__ == "__main__":
    main()

