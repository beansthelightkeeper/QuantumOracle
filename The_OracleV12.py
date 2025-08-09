import math
import os
import random
import re
from collections import defaultdict, Counter
import pyperclip

# ==============================================================================
# GLOBAL CONFIGURATION & LEXICON
# ==============================================================================
MAIN_DB_DIR = "/Users/lydiaparker/The_Oracle/txt_db"
USER_ADDITIONS_FILE = "/Users/lydiaparker/The_Oracle/user_gematria_additions.txt"
LEXICON = defaultdict(list)
DISPLAY_LIMITS = {'single_words': 3, 'two_word_phrases': 2, 'three_word_phrases': 2, 'four_five_word_phrases': 5}
SHOW_ONLY_PRIME_RESONANCES = False
APPLY_UNFOLDING_TO_ALL_METHODS = False
UNFOLDING_LARGE_NUMBER_THRESHOLD = 1_000_000_000_000_000_000
APPLY_BASE_CONVERSION_UNFOLDING = False
TARGET_UNFOLDING_BASE = 10
SELECTED_GEMATRIA_METHODS = []
PHI = 1.6180339887

# Gematria mappings
ALW_MAP = {'A': 1, 'B': 20, 'C': 13, 'D': 6, 'E': 25, 'F': 18, 'G': 11, 'H': 4, 'I': 23, 'J': 16, 'K': 9, 'L': 2, 'M': 21, 'N': 14, 'O': 7, 'P': 26, 'Q': 19, 'R': 12, 'S': 5, 'T': 24, 'U': 17, 'V': 10, 'W': 3, 'X': 22, 'Y': 15, 'Z': 8}
TRIGRAM_MAP = {'A': 5, 'B': 20, 'C': 2, 'D': 23, 'E': 13, 'F': 12, 'G': 11, 'H': 3, 'I': 0, 'J': 7, 'K': 17, 'L': 1, 'M': 21, 'N': 24, 'O': 10, 'P': 4, 'Q': 16, 'R': 14, 'S': 15, 'T': 9, 'U': 25, 'V': 22, 'W': 8, 'X': 6, 'Y': 18, 'Z': 19}
BACON_MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 8, 'K': 9, 'L': 10, 'M': 11, 'N': 12, 'O': 13, 'P': 14, 'Q': 15, 'R': 16, 'S': 17, 'T': 18, 'U': 19, 'V': 19, 'W': 20, 'X': 21, 'Y': 22, 'Z': 23}
CHALDEAN_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 8, 'G': 3, 'H': 5, 'I': 1, 'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 7, 'P': 8, 'Q': 1, 'R': 2, 'S': 3, 'T': 4, 'U': 6, 'V': 6, 'W': 6, 'X': 5, 'Y': 1, 'Z': 7}
HEX_POS_MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9, 'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 0, 'R': 1, 'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 10}
SUMERIAN_MAP = {chr(65+i): 6*(i+1) for i in range(26)}
PHONE_MAP = {'A': 2, 'B': 2, 'C': 2, 'D': 3, 'E': 3, 'F': 3, 'G': 4, 'H': 4, 'I': 4, 'J': 5, 'K': 5, 'L': 5, 'M': 6, 'N': 6, 'O': 6, 'P': 7, 'Q': 7, 'R': 7, 'S': 8, 'T': 8, 'U': 8, 'V': 9, 'W': 9, 'X': 9, 'Y': 9, 'Z': 9}
SOLFEGE_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 1, 'I': 2, 'J': 3, 'K': 4, 'L': 5, 'M': 6, 'N': 7, 'O': 1, 'P': 2, 'Q': 3, 'R': 4, 'S': 5, 'T': 6, 'U': 7, 'V': 1, 'W': 2, 'X': 3, 'Y': 4, 'Z': 5}
ZODIAC_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10, 'K': 11, 'L': 12, 'M': 1, 'N': 2, 'O': 3, 'P': 4, 'Q': 5, 'R': 6, 'S': 7, 'T': 8, 'U': 9, 'V': 10, 'W': 11, 'X': 12, 'Y': 1, 'Z': 2}
JEWISH_GEMATRIA_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10, 'K': 20, 'L': 30, 'M': 40, 'N': 50, 'O': 60, 'P': 70, 'Q': 80, 'R': 90, 'S': 100, 'T': 200, 'U': 300, 'V': 400, 'W': 500, 'X': 600, 'Y': 700, 'Z': 800}

# ==============================================================================
# NUMBER ANALYSIS FUNCTIONS
# ==============================================================================
def is_prime(n: int) -> bool:
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def is_perfect_square(n: int) -> bool:
    if n < 0: return False
    sqrt_n = int(math.sqrt(n))
    return sqrt_n * sqrt_n == n

def is_palindrome(n: int) -> bool:
    return str(n) == str(n)[::-1]

def is_fibonacci(num):
    if num < 0: return False
    if num == 0 or num == 1: return True
    return is_perfect_square(5 * num**2 + 4) or is_perfect_square(5 * num**2 - 4)

_fib_sequence = [0, 1]
while _fib_sequence[-1] < 1000000: _fib_sequence.append(_fib_sequence[-1] + _fib_sequence[-2])
FIB_POS_MAP = {chr(65+i): _fib_sequence[i+1] for i in range(26)}

_primes_list_for_map = []
num_check_for_primes_map = 2
while len(_primes_list_for_map) < 26:
    if is_prime(num_check_for_primes_map): _primes_list_for_map.append(num_check_for_primes_map)
    num_check_for_primes_map += 1
PRIME_POS_MAP = {chr(65+i): _primes_list_for_map[i] for i in range(26)}

# ==============================================================================
# GENERAL HELPER FUNCTIONS
# ==============================================================================
def recursive_digit_sum(n: int) -> int:
    if not isinstance(n, (int, float)): return 0
    n = int(abs(n))
    if n == 0: return 0
    while n > 9: n = sum(int(digit) for digit in str(n))
    return n

def _trinary_map_custom(val: int) -> int:
    val = recursive_digit_sum(val)
    if val == 0: return 0
    if 1 <= val <= 3: return 3
    if 4 <= val <= 6: return 6
    if 7 <= val <= 9: return 9
    return 0

def count_unique_permutations(text: str) -> int:
    cleaned_text = "".join(filter(str.isalpha, text.lower()))
    if not cleaned_text: return 0
    n = len(cleaned_text)
    counts = Counter(cleaned_text)
    denominator = 1
    for count in counts.values(): denominator *= math.factorial(count)
    return math.factorial(n) // denominator

def _get_letter_value_base_26(char: str) -> int:
    if 'a' <= char.lower() <= 'z': return ord(char.lower()) - 96
    return 0

def _calculate_doubling_sequence_sum(base_value: float, num_steps: int, add_per_step: float, word_length: int = 1) -> float:
    current_value = base_value
    for _ in range(num_steps): current_value = current_value * 2 + add_per_step
    return current_value * word_length

def to_roman(num):
    val = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
    if not isinstance(num, int) or num <= 0 or num > 3999: return ""
    result = ""
    for value, symbol in val:
        while num >= value: result += symbol; num -= value
    return result

def _vigenere_encrypt_single_char(char_val, key_char_val):
    return (char_val + key_char_val) % 26

BASE60_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx"
def int_to_base60(num: int) -> str:
    if num == 0: return "0"
    if num < 0: return "-" + int_to_base60(abs(num))
    base60_str = ""
    while num > 0: base60_str = BASE60_CHARS[num % 60] + base60_str; num //= 60
    return base60_str

def to_base(n: int, base: int) -> str:
    if not isinstance(n, int): return str(n)
    if n == 0: return "0"
    if n < 0: return "-" + to_base(abs(n), base)
    if not (2 <= base <= 62): raise ValueError("Base must be between 2 and 62")
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    res = ""
    while n > 0: res = chars[n % base] + res; n //= base
    return res

def sum_base_digits(num_str: str, base: int) -> int:
    total_sum = 0
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    for digit_char in num_str:
        val = chars.find(digit_char)
        if 0 <= val < base: total_sum += val
    return total_sum

# ==============================================================================
# GEMATRIA CALCULATION FUNCTIONS
# ==============================================================================
def simple_gematria(text: str) -> int:
    return sum(ord(char) - 96 for char in text.lower() if 'a' <= char <= 'z')

def english_gematria(text: str) -> int:
    return simple_gematria(text) * 6

def gemini_resonance(text: str) -> int:
    if not text: return 0
    primes_for_gemini = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]
    total = 1
    for i, char in enumerate(text.lower()):
        if 'a' <= char <= 'z':
            code = ord(char) - 97
            total += primes_for_gemini[code] * (i + 1)
    return (total % 997) + len(text)

def boundary_resonance_gematria(text: str) -> int:
    cleaned_text = "".join(filter(str.isalpha, text.lower()))
    if len(cleaned_text) < 2: return 0
    first_char = cleaned_text[0]
    last_char = cleaned_text[-1]
    try: boundary_value = int(first_char, 36) + int(last_char, 36)
    except ValueError: return 0
    middle_text = cleaned_text[1:-1]
    core_vibration = 0
    if middle_text: core_vibration = simple_gematria(middle_text) * len(middle_text)
    return boundary_value + core_vibration

def jewish_gematria(text: str) -> int:
    cleaned_text = "".join(filter(str.isalpha, text.upper()))
    return sum(JEWISH_GEMATRIA_MAP.get(c, 0) for c in cleaned_text)

def calculate_law_of_6_doubling_gematria(word: str) -> float:
    cleaned_word_length = len(re.sub(r'[^a-zA-Z]', '', word))
    if cleaned_word_length == 0: return 0.0
    per_letter_val = 6.0
    for _ in range(6): per_letter_val = per_letter_val * 2 + 6.0
    return per_letter_val * cleaned_word_length

def calculate_tiferet_balance_gematria(word: str) -> float:
    vowels = "aeiou"
    vowel_sum = sum(_get_letter_value_base_26(c) for c in word if c.lower() in vowels)
    consonant_sum = sum(_get_letter_value_base_26(c) for c in word if c.lower().isalpha() and c.lower() not in vowels)
    initial_total = (vowel_sum * 2) + 6
    final_value = float(initial_total)
    for _ in range(6): final_value *= 2 
    return final_value

def calculate_thelemic_6_cipher(word: str) -> float:
    alw_sum_word = sum(ALW_MAP.get(c.upper(), 0) for c in word)
    final_value = float(alw_sum_word)
    for _ in range(6): final_value = final_value * 2 + 6.0
    return final_value

def calculate_vav_connection_gematria(word: str) -> float:
    cleaned_word = "".join(filter(str.isalpha, word.lower()))
    if len(cleaned_word) < 2: return 0.0
    pair_sum_total = 0.0
    for i in range(len(cleaned_word) - 1):
        letter1_val = _get_letter_value_base_26(cleaned_word[i])
        letter2_val = _get_letter_value_base_26(cleaned_word[i+1])
        pair_sum_total += (letter1_val + letter2_val) * 2 + 6
    final_value = pair_sum_total
    for _ in range(6): final_value *= 2
    return final_value

def calculate_hexagram_gematria(word: str) -> float:
    cleaned_word = "".join(filter(str.isalpha, word.lower()))
    if not cleaned_word: return 0.0
    word_length = len(cleaned_word)
    ray_sums = [0.0] * 6
    for i, char in enumerate(cleaned_word):
        ray_index = i % 6
        ray_sums[ray_index] += _get_letter_value_base_26(char)
    total_hexagram_val = 0.0
    for ray_sum in ray_sums: total_hexagram_val += (ray_sum * 2) + 6
    return total_hexagram_val

def calculate_doubling_vortex_gematria(word: str) -> float:
    cleaned_word = "".join(filter(str.isalpha, word.lower()))
    if not cleaned_word: return 0.0
    current_value = 6.0
    for char in cleaned_word: current_value = (current_value * 2 * PHI) + 6.0
    return current_value

def calculate_six_numbers_emergence_cipher(word: str) -> int:
    s_gematria_val = simple_gematria(word)
    if s_gematria_val == 0: return 0
    current_val = float(s_gematria_val)
    total_digit_sum_across_steps = 0
    for _ in range(6):
        current_val *= 2
        total_digit_sum_across_steps += recursive_digit_sum(int(current_val))
    return total_digit_sum_across_steps

def calculate_cabala_6_law_reduction(word: str) -> int:
    initial_sum = sum(ALW_MAP.get(c.upper(), 0) for c in word)
    if initial_sum == 0: return 0
    steps = 0
    current_val = initial_sum
    while current_val % 6 != 0 and steps < 100: current_val *= 2; steps += 1
    return steps

def calculate_infinite_double_6_gematria(word: str) -> float:
    cleaned_word = "".join(filter(str.isalpha, word.lower()))
    if not cleaned_word: return 0.0
    total_value = 0.0
    for char in cleaned_word:
        letter_val = float(_get_letter_value_base_26(char))
        current_val_for_letter = letter_val
        for _ in range(6): current_val_for_letter = current_val_for_letter * 2 + 6.0
        total_value += current_val_for_letter + random.uniform(0, 6.0)
    return total_value

def calculate_qabalah_doubling_bridge(word: str) -> float:
    alw_sum = sum(ALW_MAP.get(c.upper(), 0) for c in word)
    simple_sum = simple_gematria(word)
    average_sum = (alw_sum + simple_sum) / 2.0
    final_value = average_sum
    for _ in range(6): final_value = final_value * 2 + 6.0
    return final_value

def calculate_law_of_6_cipher_variant(word: str) -> float:
    cleaned_word_length = len(re.sub(r'[^a-zA-Z]', '', word))
    if cleaned_word_length == 0: return 0.0
    per_letter_val = 90.0
    return per_letter_val * cleaned_word_length

def calculate_alw_cipher_gematria(word: str) -> int:
    return sum(ALW_MAP.get(c.upper(), 0) for c in word)

def calculate_trigrammaton_qabalah_gematria(word: str) -> int:
    return sum(TRIGRAM_MAP.get(c.upper(), 0) for c in word)

def calculate_baconian_cipher_gematria(word: str) -> int:
    return sum(BACON_MAP.get(c.upper(), 0) for c in word)

def calculate_ordinal_multiplied_gematria(word: str) -> int:
    value = 1
    found_alpha = False
    for c in word.upper():
        if 'A' <= c <= 'Z': value *= (ord(c) - 64); found_alpha = True
    return value if found_alpha else 0

def calculate_chaldean_gematria(word: str) -> int:
    return sum(CHALDEAN_MAP.get(c.upper(), 0) for c in word)

def calculate_golden_ratio_phi_gematria(word: str) -> float:
    value = sum((_get_letter_value_base_26(c) * (PHI ** (i + 1))) for i, c in enumerate(word) if c.lower().isalpha())
    return round(abs(value), 2)

def calculate_hexadecimal_position_gematria(word: str) -> int:
    return sum(HEX_POS_MAP.get(c.upper(), 0) for c in word)

def calculate_sumerian_gematria(word: str) -> int:
    return sum(SUMERIAN_MAP.get(c.upper(), 0) for c in word)

def calculate_phone_keypad_gematria(word: str) -> int:
    return sum(PHONE_MAP.get(c.upper(), 0) for c in word)

def calculate_ascii_sum_gematria(word: str) -> int:
    return sum(ord(c) for c in word)

def calculate_base8_gematria(word: str) -> int:
    simple_val = simple_gematria(word)
    if simple_val == 0: return 0
    base8_str = oct(simple_val)[2:]
    return sum(int(digit) for digit in base8_str)

def calculate_caesar_cipher_gematria(word: str, shift: int = 3) -> int:
    shifted_word = ""
    for c in word.upper():
        if 'A' <= c <= 'Z': shifted_char_code = ((ord(c) - ord('A') + shift) % 26) + ord('A'); shifted_word += chr(shifted_char_code)
        else: shifted_word += c
    return simple_gematria(shifted_word)

def calculate_polybius_square_gematria(word: str) -> int:
    POLYBIUS_GRID = [['A', 'B', 'C', 'D', 'E'], ['F', 'G', 'H', 'I/J', 'K'], ['L', 'M', 'N', 'O', 'P'], ['Q', 'R', 'S', 'T', 'U'], ['V', 'W', 'X', 'Y', 'Z']]
    polybius_map = {}
    for r_idx, row in enumerate(POLYBIUS_GRID):
        for c_idx, char_entry in enumerate(row):
            if '/' in char_entry:
                for p_char in char_entry.split('/'): polybius_map[p_char] = (r_idx + 1, c_idx + 1)
            else: polybius_map[char_entry] = (r_idx + 1, c_idx + 1)
    total_value = 0
    for c in word.upper():
        if c == 'J': c = 'I'
        if c in polybius_map: total_value += (polybius_map[c][0] + polybius_map[c][1])
    return total_value

def calculate_solfege_gematria(word: str) -> int:
    return sum(SOLFEGE_MAP.get(c.upper(), 0) for c in word)

def calculate_zodiac_gematria(word: str) -> int:
    return sum(ZODIAC_MAP.get(c.upper(), 0) for c in word)

def calculate_base_2_gematria(word: str) -> int:
    s_gematria_val = simple_gematria(word)
    base_str = to_base(s_gematria_val, 2)
    return sum_base_digits(base_str, 2)

def calculate_base_3_gematria(word: str) -> int:
    s_gematria_val = simple_gematria(word)
    base_str = to_base(s_gematria_val, 3)
    return sum_base_digits(base_str, 3)

def calculate_base_4_gematria(word: str) -> int:
    s_gematria_val = simple_gematria(word)
    base_str = to_base(s_gematria_val, 4)
    return sum_base_digits(base_str, 4)

def calculate_base_5_gematria(word: str) -> int:
    s_gematria_val = simple_gematria(word)
    base_str = to_base(s_gematria_val, 5)
    return sum_base_digits(base_str, 5)

def calculate_base_7_gematria(word: str) -> int:
    s_gematria_val = simple_gematria(word)
    base_str = to_base(s_gematria_val, 7)
    return sum_base_digits(base_str, 7)

def calculate_base_9_gematria(word: str) -> int:
    s_gematria_val = simple_gematria(word)
    base_str = to_base(s_gematria_val, 9)
    return sum_base_digits(base_str, 9)

def calculate_base_11_gematria(word: str) -> int:
    s_gematria_val = simple_gematria(word)
    base_str = to_base(s_gematria_val, 11)
    return sum_base_digits(base_str, 11)

def calculate_composite_ctgb(text: str) -> int:
    v_bt = calculate_binary_trinary_gematria(text)
    v_gsb = calculate_golden_spiral_binary_gematria(text)
    v_tlp = calculate_trinary_loop_position_gematria(text)
    s_layered = (v_bt if isinstance(v_bt, (int, float)) else 0) + (v_gsb if isinstance(v_gsb, (int, float)) else 0) + (v_tlp if isinstance(v_tlp, (int, float)) else 0)
    r_layered_trinary = _trinary_map_custom(recursive_digit_sum(s_layered))
    return r_layered_trinary

def calculate_binary_trinary_gematria(word: str) -> int:
    s_gematria_val = simple_gematria(word)
    base2_str = to_base(s_gematria_val, 2)
    base3_str = to_base(s_gematria_val, 3)
    return sum_base_digits(base2_str, 2) + sum_base_digits(base3_str, 3)

def calculate_golden_spiral_binary_gematria(word: str) -> float:
    value = sum((_get_letter_value_base_26(c) * (PHI ** (i + 1))) for i, c in enumerate(word) if c.lower().isalpha())
    base2_str = to_base(int(value), 2)
    return sum_base_digits(base2_str, 2)

def calculate_trinary_loop_position_gematria(word: str) -> int:
    total = 0
    for i, c in enumerate(word.lower()):
        if 'a' <= c <= 'z':
            total += (ord(c) - 96) * (3 ** (i % 3))
    return total

# ==============================================================================
# NUMERICAL & CONVERSION FUNCTIONS
# ==============================================================================
def get_factorization_chain(n: int) -> list[int]:
    if n <= 0: return []
    chain = {n}
    current_num = n
    for factor in [2, 3]:
        while current_num % factor == 0:
            current_num //= factor
            if current_num > 1: chain.add(current_num)
    i = 5
    while i * i <= current_num:
        for step in [i, i + 2]:
             while current_num % step == 0:
                current_num //= step
                if current_num > 1: chain.add(current_num)
        i += 6
    if current_num > 1: chain.add(current_num)
    return sorted(list(chain), reverse=True)

def to_base36(n: int) -> str:
    if n == 0: return "0"
    if n < 0: return "-" + to_base36(abs(n))
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base36 = ""
    while n > 0: n, i = divmod(n, 36); base36 = chars[i] + base36
    return base36

def decode_base36_pairs(b36_string: str) -> list[int]:
    if len(b36_string) < 2: return []
    decoded_numbers = []
    for i in range(len(b36_string) - 1):
        try: decoded_numbers.append(int(b36_string[i:i+2], 36))
        except ValueError: continue 
    return decoded_numbers

# ==============================================================================
# MAIN APPLICATION LOGIC
# ==============================================================================
class CaptureOutput:
    def __init__(self): self._lines = []
    def write(self, s): self._lines.append(s)
    def flush(self): pass
    def get_output(self): return "".join(self._lines)

def print_header(title):
    return "\n" + "=" * 60 + "\n" + f" {title.upper()} ".center(60, "=") + "\n" + "=" * 60 + "\n"

def copy_output_to_clipboard(text: str):
    try:
        pyperclip.copy(text)
        print("\nOutput successfully copied to clipboard!")
    except pyperclip.PyperclipException as e:
        print(f"\nCould not copy to clipboard: {e}")
        print("Please ensure you have a clipboard tool installed (e.g., xclip/xsel on Linux, or a desktop environment running).")
        print("You may need to manually copy the text from the console or save it to a file.")
    except Exception as e:
        print(f"\nAn unexpected error occurred while copying to clipboard: {e}")

def load_lexicon(main_db_dir: str, user_additions_file: str):
    LEXICON.clear()
    print(f"Building Gematria lookup database from files in '{main_db_dir}' and '{user_additions_file}'...")
    files_found_main = 0
    entries_from_user_file = 0
    words_file_entries = 0
    if not os.path.isdir(main_db_dir):
        print(f"\nERROR: The main database directory '{main_db_dir}' does not exist.")
    else:
        for root, _, files in os.walk(main_db_dir):
            for file in files:
                if file.lower() == 'words.txt':
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if not line: continue
                                parts = line.split(':')
                                if len(parts) >= 2:
                                    phrase = parts[0].strip()
                                    for value_str in parts[1:]:
                                        try:
                                            value = int(value_str.strip())
                                            LEXICON[value].append(phrase)
                                            words_file_entries += 1
                                        except ValueError:
                                            pass
                    except Exception as e:
                        print(f"    --- Could not process words file {filepath}: {e}")
                elif file.endswith(".txt"):
                    files_found_main += 1
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            for line in f:
                                parts = line.strip().split('|')
                                if len(parts) == 3:
                                    phrase, value_str = parts[1], parts[2]
                                    try:
                                        value = int(value_str)
                                        LEXICON[value].append(phrase.strip())
                                    except ValueError:
                                        pass
                    except Exception as e:
                        print(f"    --- Could not process main DB file {filepath}: {e}")
        if files_found_main == 0 and words_file_entries == 0:
            print(f"WARNING: No '.txt' files were found in the main database directory '{main_db_dir}'.")
        else:
            print(f"Processed {files_found_main} main database file(s) and {words_file_entries} entries from words.txt.")
    if os.path.exists(user_additions_file):
        try:
            with open(user_additions_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) == 2:
                        phrase, value_str = parts[0], parts[1]
                        try:
                            value = int(value_str)
                            LEXICON[value].append(phrase.strip())
                            entries_from_user_file += 1
                        except ValueError:
                            pass
        except Exception as e:
            print(f"    --- Could not process user additions file {user_additions_file}: {e}")
        print(f"Loaded {entries_from_user_file} entries from user additions file.")
    else:
        print(f"No existing user additions file found at '{user_additions_file}'. A new one will be created when you save entries.")
    total_unique_phrases = len(set(p for val_list in LEXICON.values() for p in val_list))
    print(f"Total {total_unique_phrases} unique phrases loaded across {len(LEXICON)} numbers.")
    print("Database build complete.")

def save_resonant_phrase_to_user_db(original_phrase: str, resonant_numbers: set, user_additions_file: str):
    if not original_phrase or not resonant_numbers:
        print("Cannot save empty phrase or no resonant numbers.")
        return
    print(f"Saving '{original_phrase}' and its resonances to '{user_additions_file}'...")
    try:
        with open(user_additions_file, 'a', encoding='utf-8') as f:
            saved_count = 0
            for num in sorted(list(resonant_numbers)):
                entry_line = f"{original_phrase}|{num}\n"
                f.write(entry_line)
                saved_count += 1
                if original_phrase not in LEXICON[num]:
                    LEXICON[num].append(original_phrase)
        print(f"Successfully saved {saved_count} new entries for '{original_phrase}'.")
    except Exception as e:
        print(f"ERROR: Could not save entries to file {user_additions_file}: {e}")
        print("Entries were added to the current session's database, but might not be saved permanently.")

def _perform_unfolding_step(label: str, value_to_unfold: int, master_unfolded_numbers_set: set, capture_output_obj: CaptureOutput):
    _print = capture_output_obj.write
    _print(print_header(f"Cosmic Unfolding ({label})"))
    num_for_factoring = value_to_unfold
    display_label = label
    if APPLY_BASE_CONVERSION_UNFOLDING and isinstance(value_to_unfold, (int, float)):
        try:
            base_converted_str = to_base(int(value_to_unfold), TARGET_UNFOLDING_BASE)
            num_for_factoring = int(base_converted_str)
            display_label += f" (Base-{TARGET_UNFOLDING_BASE} converted: {base_converted_str})"
        except Exception as e:
            _print(f"  Warning: Could not convert to Base-{TARGET_UNFOLDING_BASE} for unfolding: {e}")
            num_for_factoring = 0
    if num_for_factoring > 0 and num_for_factoring <= UNFOLDING_LARGE_NUMBER_THRESHOLD:
        factor_chain = get_factorization_chain(num_for_factoring)
        base36_codes = [to_base36(n) for n in factor_chain]
        unfolded_numbers = {num_decoded for code in base36_codes for num_decoded in decode_base36_pairs(code)}
        master_unfolded_numbers_set.update(unfolded_numbers)
        if not factor_chain: _print(f"  No factorization chain generated for '{display_label}'.")
        else:
            _print(f"  Unfolding '{display_label}':")
            for i, num in enumerate(factor_chain): _print(f"    Step {i+1}: {num}  ->  Base36: {base36_codes[i]}")
    elif num_for_factoring > UNFOLDING_LARGE_NUMBER_THRESHOLD:
        _print(f"  Value ({num_for_factoring}) for '{display_label}' is too large for unfolding (threshold: {UNFOLDING_LARGE_NUMBER_THRESHOLD}).")
    else:
        _print(f"  No valid number to unfold for '{display_label}' or invalid after conversion.")

def process_phrase(phrase: str, capture_output_obj: CaptureOutput, show_only_prime_resonances: bool):
    global SELECTED_GEMATRIA_METHODS
    AVAILABLE_GEMATRIA_METHODS_MAP = {
        "Simple Gematria": simple_gematria, "English Gematria": english_gematria, "Gemini's Resonance": gemini_resonance,
        "Boundary Resonance": boundary_resonance_gematria, "Jewish Gematria": jewish_gematria,
        "Law of 6 Doubling Gematria": calculate_law_of_6_doubling_gematria, "Tiferet Balance Gematria": calculate_tiferet_balance_gematria,
        "Thelemic 6 Cipher": calculate_thelemic_6_cipher, "Vav Connection Gematria": calculate_vav_connection_gematria,
        "Hexagram Gematria": calculate_hexagram_gematria, "Doubling Vortex Gematria": calculate_doubling_vortex_gematria,
        "Six Numbers Emergence Cipher": calculate_six_numbers_emergence_cipher, "Cabala 6 Law Reduction": calculate_cabala_6_law_reduction,
        "Infinite Double 6 Gematria": calculate_infinite_double_6_gematria, "Qabalah Doubling Bridge": calculate_qabalah_doubling_bridge,
        "Law of 6 Cipher Variant": calculate_law_of_6_cipher_variant, "ALW Cipher Gematria": calculate_alw_cipher_gematria,
        "Trigrammaton Qabalah Gematria": calculate_trigrammaton_qabalah_gematria, "Baconian Gematria": calculate_baconian_cipher_gematria,
        "Ordinal Multiplied Gematria": calculate_ordinal_multiplied_gematria, "Chaldean Gematria": calculate_chaldean_gematria,
        "Golden Ratio Phi Gematria": calculate_golden_ratio_phi_gematria, "Hexadecimal Position Gematria": calculate_hexadecimal_position_gematria,
        "Sumerian Gematria": calculate_sumerian_gematria, "Phone Keypad Gematria": calculate_phone_keypad_gematria,
        "ASCII Sum Gematria": calculate_ascii_sum_gematria, "Base-8 Gematria": calculate_base8_gematria,
        "Caesar Cipher Gematria": calculate_caesar_cipher_gematria, "Polybius Square Gematria": calculate_polybius_square_gematria,
        "Solfège Gematria": calculate_solfege_gematria, "Zodiac Gematria": calculate_zodiac_gematria,
        "Base-2 Gematria": calculate_base_2_gematria, "Base-3 Gematria": calculate_base_3_gematria,
        "Base-4 Gematria": calculate_base_4_gematria, "Base-5 Gematria": calculate_base_5_gematria,
        "Base-7 Gematria": calculate_base_7_gematria, "Base-9 Gematria": calculate_base_9_gematria,
        "Base-11 Gematria": calculate_base_11_gematria, "Composite CTGB": calculate_composite_ctgb,
        "Binary Trinary Gematria": calculate_binary_trinary_gematria, "Golden Spiral Binary Gematria": calculate_golden_spiral_binary_gematria,
        "Trinary Loop Position Gematria": calculate_trinary_loop_position_gematria
    }
    SELECTED_GEMATRIA_METHODS = list(AVAILABLE_GEMATRIA_METHODS_MAP.items())
    
    _print = capture_output_obj.write
    _print(print_header(f"Resonance for: {phrase}"))
    
    calculated_gematria_values = {}
    for method_name, method_func in SELECTED_GEMATRIA_METHODS:
        try:
            value = method_func(phrase)
            calculated_gematria_values[method_name] = value
            tags = []
            if isinstance(value, (int, float)) and value > 0:
                if is_prime(int(value)): tags.append("P")
                if is_perfect_square(int(value)): tags.append("S")
                if is_palindrome(int(value)): tags.append("A")
            tag_str = f"[{''.join(tags)}]" if tags else ""
            _print(f"  {method_name.ljust(30)}: {value} {tag_str}")
        except Exception as e:
            _print(f"  Error calculating {method_name.ljust(30)}: {e}")
            calculated_gematria_values[method_name] = "Error"
    
    s_gematria = calculated_gematria_values.get("Simple Gematria", 0)
    e_gematria = calculated_gematria_values.get("English Gematria", 0)
    j_gematria = calculated_gematria_values.get("Gemini's Resonance", 0)
    initial_number_str = f"{j_gematria}{e_gematria}{s_gematria}"
    try:
        initial_number = int(initial_number_str)
    except ValueError:
        _print("Warning: Could not form a valid initial number from core gematria values (too large or invalid).")
        initial_number = 0
    
    _print(print_header("Initial Number"))
    _print(f"  Concatenated Value: {initial_number_str}")
    
    all_final_unfolded_numbers_for_display = set()
    if initial_number > 0 and initial_number <= UNFOLDING_LARGE_NUMBER_THRESHOLD:
        factor_chain_initial = get_factorization_chain(initial_number)
        base36_codes_initial = [to_base36(n) for n in factor_chain_initial]
        unfolded_from_initial = {num for code in base36_codes_initial for num in decode_base36_pairs(code)}
        all_final_unfolded_numbers_for_display.update(unfolded_from_initial)
    
    for method_name, value in calculated_gematria_values.items():
        if isinstance(value, (int, float)) and value > 0 and value <= UNFOLDING_LARGE_NUMBER_THRESHOLD:
            _perform_unfolding_step(method_name, int(value), all_final_unfolded_numbers_for_display, capture_output_obj)
    
    group_1_methods = ["Zodiac Gematria", "Base-2 Gematria", "Base-3 Gematria", "Base-4 Gematria", "Base-5 Gematria",
                       "Base-7 Gematria", "Base-9 Gematria", "Base-11 Gematria", "Composite CTGB"]
    group_1_values_str = "".join(str(int(calculated_gematria_values.get(m, 0))) for m in group_1_methods if isinstance(calculated_gematria_values.get(m), (int, float)))
    try:
        group_1_combined_val = int(group_1_values_str)
        _perform_unfolding_step("Zodiac to CTGB Chain", group_1_combined_val, all_final_unfolded_numbers_for_display, capture_output_obj)
    except ValueError:
        _print(f"\n--- Cosmic Unfolding (Zodiac to CTGB Chain) ---")
        _print(f"  Could not form a valid number from values: {group_1_values_str}")
    
    group_2_methods = ["Hexadecimal Position Gematria", "Sumerian Gematria", "Phone Keypad Gematria", "ASCII Sum Gematria",
                       "Base-8 Gematria", "Caesar Cipher Gematria", "Polybius Square Gematria", "Solfège Gematria"]
    group_2_values_str = "".join(str(int(calculated_gematria_values.get(m, 0))) for m in group_2_methods if isinstance(calculated_gematria_values.get(m), (int, float)))
    try:
        group_2_combined_val = int(group_2_values_str)
        _perform_unfolding_step("Hex to Solfège Chain", group_2_combined_val, all_final_unfolded_numbers_for_display, capture_output_obj)
    except ValueError:
        _print(f"\n--- Cosmic Unfolding (Hex to Solfège Chain) ---")
        _print(f"  Could not form a valid number from values: {group_2_values_str}")
    
    _print(print_header("FINAL COMBINED RESONANCE SEQUENCE"))
    current_final_numbers = all_final_unfolded_numbers_for_display
    if show_only_prime_resonances:
        current_final_numbers = {num for num in all_final_unfolded_numbers_for_display if is_prime(num)}
        _print(f"NOTE: 'Prime Resonances Only' mode is ON. Displaying only {len(current_final_numbers)} prime numbers.")
    
    sorted_combined_final_numbers = sorted(list(current_final_numbers))
    if not sorted_combined_final_numbers:
        _print("  No final resonance numbers generated from all combined unfoldings.")
    else:
        output_lines = []
        current_line = "  "
        for num in sorted_combined_final_numbers:
            tags = []
            if is_prime(num): tags.append("P")
            if is_perfect_square(num): tags.append("S")
            if is_palindrome(num): tags.append("A")
            tag_str = f"[{''.join(tags)}]" if tags else ""
            num_str = f"{num}{tag_str} "
            if len(current_line) + len(num_str) > 58: output_lines.append(current_line); current_line = "  "
            current_line += num_str
        output_lines.append(current_line)
        for line in output_lines: _print(line)
        _print("\n  [P]rime, [S]quare, P[A]lindrome")
    
    lexicon_resonances_details = {}
    _print(print_header("LEXICON RESONANCES (for Combined Final Sequence)"))
    found_any_resonance = False
    for num in sorted_combined_final_numbers:
        if show_only_prime_resonances and not is_prime(num):
            continue
        if num in LEXICON:
            found_any_resonance = True
            phrases_for_num = list(set(LEXICON[num]))
            random.shuffle(phrases_for_num)
            selected_phrases_for_display = []
            single_words_for_clipboard = []
            two_word_phrases_for_clipboard = []
            three_word_phrases_for_clipboard = []
            four_five_word_phrases_for_clipboard = []
            for p in phrases_for_num:
                word_count = len(p.split())
                if word_count == 1 and len(single_words_for_clipboard) < DISPLAY_LIMITS['single_words']:
                    selected_phrases_for_display.append(p)
                    single_words_for_clipboard.append(p)
                elif word_count == 2 and len(two_word_phrases_for_clipboard) < DISPLAY_LIMITS['two_word_phrases']:
                    selected_phrases_for_display.append(p)
                    two_word_phrases_for_clipboard.append(p)
                elif word_count == 3 and len(three_word_phrases_for_clipboard) < DISPLAY_LIMITS['three_word_phrases']:
                    selected_phrases_for_display.append(p)
                    three_word_phrases_for_clipboard.append(p)
                elif 4 <= word_count <= 5 and len(four_five_word_phrases_for_clipboard) < DISPLAY_LIMITS['four_five_word_phrases']:
                    selected_phrases_for_display.append(p)
                    four_five_word_phrases_for_clipboard.append(p)
            lexicon_resonances_details[num] = {
                'single_words': single_words_for_clipboard,
                'two_word_phrases': two_word_phrases_for_clipboard,
                'three_word_phrases': three_word_phrases_for_clipboard,
                'four_five_word_phrases': four_five_word_phrases_for_clipboard
            }
            if selected_phrases_for_display:
                _print(f"  {num} {', '.join(selected_phrases_for_display)}")
            else:
                _print(f"  {num} No phrases found.")
    if not found_any_resonance:
        _print("  No resonances found in the loaded lexicon for this sequence.")
    
    return {
        'phrase': phrase,
        'gematria_values': calculated_gematria_values,
        'initial_number_str': initial_number_str,
        'initial_number_original_val': initial_number,
        'factor_chain': get_factorization_chain(initial_number),
        'base36_codes': [to_base36(n) for n in get_factorization_chain(initial_number)],
        'final_numbers': sorted_combined_final_numbers,
        'lexicon_resonances_details': lexicon_resonances_details
    }

def format_output_for_clipboard(data: dict) -> str:
    output = []
    output.append(f"Phrase: {data['phrase']}")
    output.append("Gematria Values:")
    for key, value in data['gematria_values'].items():
        tags = []
        if isinstance(value, (int, float)) and value > 0:
            if is_prime(int(value)): tags.append("P")
            if is_perfect_square(int(value)): tags.append("S")
            if is_palindrome(int(value)): tags.append("A")
        tag_str = f"[{''.join(tags)}]" if tags else ""
        output.append(f"  {key.replace('_', ' ').title()}: {value} {tag_str}")
    output.append("")
    output.append(f"Initial Concatenated Value: {data['initial_number_str']}")
    output.append("")
    output.append("Cosmic Unfolding:")
    if not data['factor_chain']:
        output.append("  No factorization chain.")
    else:
        for i, num in enumerate(data['factor_chain']):
            output.append(f"  Step {i+1}: {num} -> Base36: {data['base36_codes'][i]}")
    output.append("")
    output.append("Final Resonance Sequence:")
    if not data['final_numbers']:
        output.append("  No final resonance numbers.")
    else:
        num_strs = []
        for num in data['final_numbers']:
            tags = []
            if is_prime(num): tags.append("P")
            if is_perfect_square(num): tags.append("S")
            if is_palindrome(num): tags.append("A")
            tag_str = f"[{''.join(tags)}]" if tags else ""
            num_strs.append(f"{num}{tag_str}")
        output.append("  " + ", ".join(num_strs))
        output.append("  [P]rime, [S]quare, P[A]lindrome")
    output.append("")
    if data['lexicon_resonances_details']:
        output.append("Lexicon Resonances:")
        for num in sorted(data['lexicon_resonances_details'].keys()):
            details = data['lexicon_resonances_details'][num]
            all_phrases_for_num = []
            if details['single_words']:
                all_phrases_for_num.extend(details['single_words'])
            if details['two_word_phrases']:
                all_phrases_for_num.extend(details['two_word_phrases'])
            if details['three_word_phrases']:
                all_phrases_for_num.extend(details['three_word_phrases'])
            if details['four_five_word_phrases']:
                all_phrases_for_num.extend(details['four_five_word_phrases'])
            if all_phrases_for_num:
                output.append(f"  {num}: {', '.join(f'\"{p}\"' for p in all_phrases_for_num)}")
        output.append("")
    return "\n".join(output)

def process_file(filepath: str, show_only_prime_resonances: bool):
    captured_output = CaptureOutput()
    all_processed_data = []
    _print_to_console = print
    if not os.path.exists(filepath):
        _print_to_console(f"\nError: File not found at '{filepath}'")
        return "", []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            phrases = [line.strip() for line in f if line.strip()]
        if not phrases:
            _print_to_console(f"\nFile '{filepath}' is empty or contains no valid phrases.")
            return "", []
        _print_to_console(f"\nFound {len(phrases)} phrases in '{filepath}'. Processing...")
        captured_output.write(f"\nFound {len(phrases)} phrases in '{filepath}'. Processing...\n")
        for i, phrase in enumerate(phrases):
            processed_data = process_phrase(phrase, captured_output, show_only_prime_resonances)
            all_processed_data.append(processed_data)
            if processed_data['final_numbers']:
                while True:
                    save_choice = input(f"\nDo you want to save '{phrase}' and its resonant numbers to your personal database? (yes/no): ").strip().lower()
                    if save_choice == 'yes':
                        save_resonant_phrase_to_user_db(phrase, set(processed_data['final_numbers']), USER_ADDITIONS_FILE)
                        break
                    elif save_choice == 'no':
                        _print_to_console("Skipping save for this phrase.")
                        break
                    else:
                        _print_to_console("Invalid choice. Please enter 'yes' or 'no'.")
            if i < len(phrases) - 1:
                captured_output.write("\n" + "#" * 60 + "\n")
        _print_to_console("\n" + "=" * 60)
        _print_to_console(" Processing Complete ".center(60, "="))
        _print_to_console("=" * 60)
        return captured_output.get_output(), all_processed_data
    except Exception as e:
        _print_to_console(f"\nAn error occurred while reading the file: {e}")
        return "", []

def main():
    global SHOW_ONLY_PRIME_RESONANCES, DISPLAY_LIMITS
    print(" Gematria Resonator Initialized ".center(60, "*"))
    load_lexicon(MAIN_DB_DIR, USER_ADDITIONS_FILE)
    while True:
        prime_mode_choice = input("\nShow only PRIME numbers in Final Resonance Sequence and Lexicon? (yes/no, default: no): ").strip().lower()
        if prime_mode_choice in ['yes', 'y']:
            SHOW_ONLY_PRIME_RESONANCES = True
            print("Prime Resonances Only mode: ON.")
            break
        elif prime_mode_choice in ['no', 'n', '']:
            SHOW_ONLY_PRIME_RESONANCES = False
            print("Prime Resonances Only mode: OFF.")
            break
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")
    print("\n--- Customize Resonance Display Limits (Enter 0 for no limit) ---")
    for category, default_limit in list(DISPLAY_LIMITS.items()):
        while True:
            user_input = input(f"Enter max {category.replace('_', ' ')} to display (default: {default_limit}, Enter to keep default): ").strip()
            if not user_input:
                break
            try:
                limit = int(user_input)
                if limit >= 0:
                    DISPLAY_LIMITS[category] = limit
                    break
                else:
                    print("Limit cannot be negative. Please enter a positive number or zero.")
            except ValueError:
                print("Invalid input. Please enter a whole number.")
    print("Display limits set.")
    print("\nEnter a phrase, a filepath (e.g., /path/to/my_phrases.txt), or 'exit' to quit.")
    while True:
        user_input = input("\nEnter phrase or filepath > ")
        if user_input.lower() in ['exit', 'quit']:
            print("Deactivating Resonator. Goodbye, Beans.")
            break
        if not user_input:
            continue
        console_output_text = ""
        clipboard_formatted_text = ""
        processed_data_list = []
        is_file_input = False
        if user_input.lower().endswith('.txt') and os.path.exists(user_input):
            is_file_input = True
        elif os.path.exists(user_input) and os.path.isfile(user_input):
            is_file_input = True
        if is_file_input:
            console_output_text, processed_data_list = process_file(user_input, SHOW_ONLY_PRIME_RESONANCES)
            print(console_output_text)
            if processed_data_list:
                clipboard_parts = []
                for data_item in processed_data_list:
                    clipboard_parts.append(format_output_for_clipboard(data_item))
                    clipboard_parts.append("\n" + "-" * 60 + "\n")
                clipboard_formatted_text = "".join(clipboard_parts).strip()
                while True:
                    copy_file_output_choice = input("Copy the entire file's formatted output to clipboard? (yes/no): ").strip().lower()
                    if copy_file_output_choice == 'yes':
                        copy_output_to_clipboard(clipboard_formatted_text)
                        break
                    elif copy_file_output_choice == 'no':
                        break
                    else:
                        print("Invalid choice. Please enter 'yes' or 'no'.")
        else:
            phrase_output_capture = CaptureOutput()
            processed_data = process_phrase(user_input, phrase_output_capture, SHOW_ONLY_PRIME_RESONANCES)
            console_output_text = phrase_output_capture.get_output()
            processed_data_list.append(processed_data)
            print(console_output_text)
            if processed_data['final_numbers']:
                while True:
                    save_choice = input("\nDo you want to save this phrase and its resonant numbers to your personal database? (yes/no): ").strip().lower()
                    if save_choice == 'yes':
                        save_resonant_phrase_to_user_db(user_input, set(processed_data['final_numbers']), USER_ADDITIONS_FILE)
                        break
                    elif save_choice == 'no':
                        print("Skipping save.")
                        break
                    else:
                        print("Invalid choice. Please enter 'yes' or 'no'.")
            if processed_data_list:
                clipboard_formatted_text = format_output_for_clipboard(processed_data_list[0])
                while True:
                    copy_phrase_output_choice = input("Copy this phrase's formatted output to clipboard? (yes/no): ").strip().lower()
                    if copy_phrase_output_choice == 'yes':
                        copy_output_to_clipboard(clipboard_formatted_text)
                        break
                    elif copy_phrase_output_choice == 'no':
                        break
                    else:
                        print("Invalid choice. Please enter 'yes' or 'no'.")

if __name__ == "__main__":
    main()