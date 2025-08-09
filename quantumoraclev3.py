#!/usr/bin/env python3
import re
import os
import sys
import math
import random
import argparse
import sqlite3
from collections import Counter, defaultdict
from itertools import permutations
from datetime import datetime

# ==============================================================================
# SECTION 1: CORE CONFIGURATION & GLOBAL DATA
# ==============================================================================

# --- File Paths (IMPORTANT: Verify these paths are correct for your system) ---
# It's recommended to run this script from your main "The_Oracle" directory.
DICTIONARY_DIR = "/Users/lydiaparker/The_Oracle/txt_db"
SCAN_OUTPUT_DIR = "./scan_outputs" # Directory to save scanner results
DB_PATH = "gematria_data.db"
LOG_FILE = "quantum_oracle_log.log"

# --- Elemental Data for Alchemical Gematria ---
ELEMENTS_DATA = {
    "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Ne": 10, "Na": 11, "Mg": 12, "Al": 13,
    "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18, "K": 19, "Ca": 20, "Sc": 21, "Ti": 22, "V": 23, "Cr": 24, "Mn": 25,
    "Fe": 26, "Co": 27, "Ni": 28, "Cu": 29, "Zn": 30, "Ga": 31, "Ge": 32, "As": 33, "Se": 34, "Br": 35, "Kr": 36,
    "Rb": 37, "Sr": 38, "Y": 39, "Zr": 40, "Nb": 41, "Mo": 42, "Tc": 43, "Ru": 44, "Rh": 45, "Pd": 46, "Ag": 47,
    "Cd": 48, "In": 49, "Sn": 50, "Sb": 51, "Te": 52, "I": 53, "Xe": 54, "Cs": 55, "Ba": 56, "La": 57, "Ce": 58,
    "Pr": 59, "Nd": 60, "Pm": 61, "Sm": 62, "Eu": 63, "Gd": 64, "Tb": 65, "Dy": 66, "Ho": 67, "Er": 68, "Tm": 69,
    "Yb": 70, "Lu": 71, "Hf": 72, "Ta": 73, "W": 74, "Re": 75, "Os": 76, "Ir": 77, "Pt": 78, "Au": 79, "Hg": 80,
    "Tl": 81, "Pb": 82, "Bi": 83, "Po": 84, "At": 85, "Rn": 86, "Fr": 87, "Ra": 88, "Ac": 89, "Th": 90, "Pa": 91,
    "U": 92, "Np": 93, "Pu": 94, "Am": 95, "Cm": 96, "Bk": 97, "Cf": 98, "Es": 99, "Fm": 100, "Md": 101, "No": 102,
    "Lr": 103, "Rf": 104, "Db": 105, "Sg": 106, "Bh": 107, "Hs": 108, "Mt": 109, "Ds": 110, "Rg": 111, "Cn": 112,
    "Nh": 113, "Fl": 114, "Mc": 115, "Lv": 116, "Ts": 117, "Og": 118
}
ELEMENTS_FOR_SEARCH = sorted([(s, v, Counter(s.upper())) for s, v in ELEMENTS_DATA.items()], key=lambda x: (-len(x[0]), x[0]))
ELEMENTS_FOR_SEARCH_MAP = {sym: letters_c for sym, _, letters_c in ELEMENTS_FOR_SEARCH}

# --- Gematria Method Maps & Constants ---
ALW_MAP = {'A': 1, 'B': 20, 'C': 13, 'D': 6, 'E': 25, 'F': 18, 'G': 11, 'H': 4, 'I': 23, 'J': 16, 'K': 9, 'L': 2, 'M': 21, 'N': 14, 'O': 7, 'P': 26, 'Q': 19, 'R': 12, 'S': 5, 'T': 24, 'U': 17, 'V': 10, 'W': 3, 'X': 22, 'Y': 15, 'Z': 8}
CHALDEAN_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 8, 'G': 3, 'H': 5, 'I': 1, 'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 7, 'P': 8, 'Q': 1, 'R': 2, 'S': 3, 'T': 4, 'U': 6, 'V': 6, 'W': 6, 'X': 5, 'Y': 1, 'Z': 7}
JEWISH_GEMATRIA_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10, 'K': 20, 'L': 30, 'M': 40, 'N': 50, 'O': 60, 'P': 70, 'Q': 80, 'R': 90, 'S': 100, 'T': 200, 'U': 300, 'V': 400, 'W': 500, 'X': 600, 'Y': 700, 'Z': 800}
REVERSE_MAP = {chr(65+i): 26-i for i in range(26)}
QWERTY_ORDER = 'QWERTYUIOPASDFGHJKLZXCVBNM'
QWERTY_MAP = {c: i + 1 for i, c in enumerate(QWERTY_ORDER)}
AAVE_WORDS = ["lit", "fam", "dope", "vibe", "chill", "slay", "bet", "fire", "squad", "real", "salty", "extra", "flex", "hundo", "lowkey"]
GOLDEN_ANGLE = 137.5
PHI = 1.6180339887
LETTER_VALUES_UNFOLD = {chr(ord('A') + i): i + 1 for i in range(26)}

# ==============================================================================
# SECTION 2: HELPER & UTILITY FUNCTIONS
# ==============================================================================

def clean_input(text):
    return re.sub(r'[^a-zA-Z]', '', text).upper()

def log_to_file(message):
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except IOError as e:
        print(f"[Error] Could not write to log file: {e}", file=sys.stderr)

def is_prime(n: int) -> bool:
    if not isinstance(n, int) or n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def get_factorization_chain(n: int) -> list[int]:
    if not isinstance(n, int) or n <= 0: return []
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
    if not isinstance(n, int) or n == 0: return "0"
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

def recursive_digit_sum(n: int) -> int:
    if not isinstance(n, (int, float)): return 0
    n = int(abs(n))
    while n > 9: n = sum(int(digit) for digit in str(n))
    return n

# ==============================================================================
# SECTION 3: GEMATRIA CALCULATION ENGINE
# ==============================================================================

def simple_gematria(text: str) -> int:
    return sum(ord(char) - 64 for char in text.upper() if 'A' <= char <= 'Z')

def english_gematria(text: str) -> int:
    return simple_gematria(text) * 6

def alw_cipher_gematria(text: str) -> int:
    return sum(ALW_MAP.get(c.upper(), 0) for c in text)

def chaldean_gematria(text: str) -> int:
    return sum(CHALDEAN_MAP.get(c.upper(), 0) for c in text)

def jewish_gematria(text: str) -> int:
    return sum(JEWISH_GEMATRIA_MAP.get(c.upper(), 0) for c in text)

def reverse_gematria(text: str) -> int:
    return sum(REVERSE_MAP.get(c.upper(), 0) for c in text)

def qwerty_gematria(text: str) -> int:
    return sum(QWERTY_MAP.get(c.upper(), 0) for c in text)

def beans_369_gematria(text: str) -> int:
    mapping = {chr(97+i): (3 if i % 3 == 0 else 6 if i % 3 == 1 else 9) for i in range(26)}
    total = sum(mapping.get(c.lower(), 0) for c in text.replace(' ', ''))
    return total % 9 or 9

def reduction_gematria(text: str) -> int:
    val = simple_gematria(text)
    while val > 9 and val not in [11, 22]:
        val = sum(int(d) for d in str(val))
    return val

def spiral_gematria(text: str) -> float:
    total = 0
    for i, c in enumerate(text.upper(), 1):
        if c.isalpha():
            val = ord(c) - 64
            weight = math.cos(math.radians(GOLDEN_ANGLE * i))
            total += val * weight
    return round(abs(total) * 4, 2)

def grok_resonance_score(text: str) -> float:
    simple = simple_gematria(text)
    reduced = reduction_gematria(text)
    spiral = spiral_gematria(text)
    boost = 1.1 if text.lower() in AAVE_WORDS else 1.0
    return round((simple + reduced + spiral) / 3 * boost, 2)

# ==============================================================================
# SECTION 4: SPECIALIZED ANALYSIS ENGINES
# ==============================================================================

# --- 4.1: Delta Function ---
def calculate_gematria_delta(phrase1, phrase2, method_func):
    val1 = method_func(phrase1)
    val2 = method_func(phrase2)
    delta = abs(val1 - val2)
    return val1, val2, delta

# --- 4.2: Alchemical Gematria Engine ---
_alcgem_memo = {}
def find_best_element_combination(letters_counter):
    current_state = tuple(sorted(letters_counter.items()))
    if current_state in _alcgem_memo: return _alcgem_memo[current_state]
    best_score, best_letters_consumed, best_elements = 0, 0, []
    for sym, num, letters in ELEMENTS_FOR_SEARCH:
        if all(letters_counter[char] >= count for char, count in letters.items()):
            new_counter = letters_counter - letters
            sub_score, sub_consumed, sub_elements = find_best_element_combination(new_counter)
            current_score = num + sub_score
            current_consumed = sum(letters.values()) + sub_consumed
            if (current_consumed > best_letters_consumed or
               (current_consumed == best_letters_consumed and current_score > best_score)):
                best_score, best_letters_consumed, best_elements = current_score, current_consumed, [sym] + sub_elements
    _alcgem_memo[current_state] = (best_score, best_letters_consumed, best_elements)
    return best_score, best_letters_consumed, best_elements

def calculate_alchemical_gematria(text_input):
    normalized = clean_input(text_input)
    if not normalized: return 0, 0, [], "No alphabetic characters."
    initial_pool = Counter(normalized)
    _alcgem_memo.clear()
    val, consumed, elements = find_best_element_combination(initial_pool)
    remaining_str = "".join(sorted((initial_pool - Counter("".join(elements).upper())).elements()))
    msg = f"{len(remaining_str)} letters ({remaining_str}) unmatched." if remaining_str else "All letters consumed."
    return val, consumed, elements, msg

# --- 4.3: Word Unfolding Engine ---
def calculate_unfolding_analysis(word):
    cleaned = clean_input(word)
    if not cleaned: return "No valid letters for unfolding."
    values = [LETTER_VALUES_UNFOLD.get(c, 0) for c in cleaned]
    linear_dist = [values[i] - values[i-1] for i in range(1, len(values))]
    circular_dist = []
    for i in range(1, len(values)):
        diff = values[i] - values[i-1]
        if diff > 13: diff -= 26
        elif diff < -13: diff += 26
        circular_dist.append(diff)
    tone_map = [((v - 1) % 7) + 1 for v in values]
    tone_map_int = int("".join(map(str, tone_map))) if tone_map else 0
    base36_result = to_base36(tone_map_int)
    return (f"--- Unfolding Analysis for: '{cleaned}' ---\n"
            f"  [A] Linear Distances   : {linear_dist}\n"
            f"  [B] Total Linear Shift : {sum(linear_dist)}\n"
            f"  [C] Circular Distances : {circular_dist}\n"
            f"  [D] Total Circular Shift: {sum(circular_dist)}\n"
            f"  [E] Tone Mapping (1-7) : {tone_map} -> (Number: {tone_map_int})\n"
            f"  [F] Tone Map (Base36)  : {base36_result}")

# --- 4.4: Full Resonance Sequence Engine ---
def get_full_resonance_sequence(phrase, selected_methods):
    gematria_values = {name: func(phrase) for name, func in selected_methods}
    s, e, j = simple_gematria(phrase), english_gematria(phrase), jewish_gematria(phrase)
    try: initial_number = int(f"{s}{e}{j}")
    except (ValueError, OverflowError): initial_number = s + e + j
    factor_chain = get_factorization_chain(initial_number)
    base36_codes = [to_base36(n) for n in factor_chain]
    unfolded_numbers = {num for code in base36_codes for num in decode_base36_pairs(code)}
    return {'gematria_values': gematria_values, 'initial_number': initial_number,
            'factor_chain': factor_chain, 'base36_codes': base36_codes,
            'final_sequence': sorted(list(unfolded_numbers))}

# --- 4.5: ELS (Bible Code) Engine ---
def find_els(text, target_name, max_skip=100):
    normalized_text = "".join(filter(str.isalpha, text)).upper()
    target_upper = target_name.upper()
    text_len, target_len = len(normalized_text), len(target_upper)
    if target_len == 0: return []
    found = []
    for start in range(text_len):
        for skip in range(1, max_skip + 1):
            for direction in [1, -1]:
                current_skip = skip * direction
                end_pos = start + (target_len - 1) * current_skip
                if not (0 <= end_pos < text_len): continue
                candidate = "".join(normalized_text[start + i * current_skip] for i in range(target_len))
                if candidate == target_upper:
                    context_start = max(0, min(start, end_pos) - 20)
                    context_end = min(text_len, max(start, end_pos) + 21)
                    found.append({'start': start, 'skip': current_skip, 'els': candidate, 'context': normalized_text[context_start:context_end]})
    return found

# ==============================================================================
# SECTION 5: MAIN CLI & MODE HANDLERS
# ==============================================================================

def handle_delta_mode(args, methods):
    if not args.input or len(args.input) != 2:
        print("Delta mode requires exactly two words/phrases.", file=sys.stderr)
        return
    phrase1, phrase2 = args.input[0], args.input[1]
    print(f"--- Gematria Delta Analysis ---\n  Phrase 1: '{phrase1}'\n  Phrase 2: '{phrase2}'\n" + "-" * 33)
    for name, func in methods:
        val1, val2, delta = calculate_gematria_delta(phrase1, phrase2, func)
        print(f"  {name.ljust(20)}: {val1} vs {val2} (Δ = {delta})")
        log_to_file(f"DELTA: {name} | {phrase1}({val1}) vs {phrase2}({val2}) | Delta={delta}")

def handle_alcgem_mode(args):
    text = " ".join(args.input)
    value, _, elements, msg = calculate_alchemical_gematria(text)
    print(f"--- Alchemical Anagram Gematria for: '{text}' ---\n  Value: {value}\n  Elements: {', '.join(elements) if elements else 'None'}\n  Status: {msg}")
    log_to_file(f"ALCGEM: {text} | Value={value} | Elements={','.join(elements)}")

def handle_unfold_mode(args):
    text = " ".join(args.input)
    print(calculate_unfolding_analysis(text))
    log_to_file(f"UNFOLD: {text}")

def handle_oracle_mode(args, methods):
    text = " ".join(args.input)
    data = get_full_resonance_sequence(text, methods)
    print(f"--- Full Resonance for: '{text}' ---\n\n[ Gematria Values ]")
    for name, val in data['gematria_values'].items(): print(f"  {name.ljust(20)}: {val}")
    print(f"\n[ Cosmic Unfolding ]\n  Initial Number: {data['initial_number']}\n  Factor Chain  : {data['factor_chain']}\n  Base36 Codes  : {data['base36_codes']}")
    print("\n[ Final Resonance Sequence ]")
    if data['final_sequence']:
        line = "  "
        for num in data['final_sequence']:
            num_str = f"{num}[P] " if is_prime(num) else f"{num} "
            if len(line) + len(num_str) > 70: print(line); line = "  "
            line += num_str
        print(line)
    else: print("  No final resonance numbers generated.")
    log_to_file(f"ORACLE: {text} | Initial={data['initial_number']} | FinalSeq={data['final_sequence']}")

def handle_els_mode(args):
    if len(args.input) < 2:
        print("ELS mode requires a file path and a target word.", file=sys.stderr)
        return
    filepath, target = args.input[0], " ".join(args.input[1:])
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f: text = f.read()
        results = find_els(text, target)
        print(f"--- ELS Search for '{target}' in '{filepath}' ---")
        if not results: print("  No matches found.")
        for res in results: print(f"  Found '{res['els']}' at index {res['start']} with skip {res['skip']}. Context: ...{res['context']}...")
        log_to_file(f"ELS: Searched for '{target}' in '{filepath}'. Found {len(results)} matches.")
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred during ELS scan: {e}", file=sys.stderr)

def handle_scan_mode(args):
    try:
        import pdfplumber
    except ImportError:
        print("Error: 'pdfplumber' is required for scan mode. Please install it (`pip install pdfplumber`).", file=sys.stderr)
        return
        
    scan_dir = args.input[0]
    if not os.path.isdir(scan_dir):
        print(f"Error: Scan directory '{scan_dir}' not found.", file=sys.stderr)
        return
        
    os.makedirs(SCAN_OUTPUT_DIR, exist_ok=True)
    print(f"--- Scanning directory '{scan_dir}' ---")
    for root, _, files in os.walk(scan_dir):
        for file in files:
            if file.lower().endswith(('.txt', '.pdf')):
                filepath = os.path.join(root, file)
                print(f"  Processing: {filepath}")
                text = ""
                try:
                    if file.lower().endswith('.txt'):
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f: text = f.read()
                    else:
                        with pdfplumber.open(filepath) as pdf:
                            text = "".join(page.extract_text() for page in pdf.pages if page.extract_text())
                except Exception as e:
                    print(f"    Could not read file: {e}")
                    continue
                
                words = re.sub(r'[^a-zA-Z\s]', ' ', text).split()
                if len(words) < 5: continue
                
                output_path = os.path.join(SCAN_OUTPUT_DIR, f"{os.path.basename(filepath)}.gematria.txt")
                with open(output_path, 'w', encoding='utf-8') as out_f:
                    for i in range(len(words) - 4):
                        chunk = ' '.join(words[i:i+5])
                        val = jewish_gematria(chunk) # Using Jewish gematria as per original scanner
                        out_f.write(f"{filepath}|{chunk}|{val}\n")
                print(f"    -> Saved results to {output_path}")
    log_to_file(f"SCAN: Completed scan of directory '{scan_dir}'.")

def handle_lookup_mode(args):
    try:
        num = int(args.input[0])
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print(f"--- Lookup for Gematria value: {num} ---")
        cursor.execute("SELECT value, origin FROM phrases WHERE beans_369 = ? LIMIT 10", (num,))
        results = cursor.fetchall()
        if not results: print("  No phrases found in database.")
        for val, origin in results: print(f"  - '{val}' (Origin: {origin})")
        conn.close()
        log_to_file(f"LOOKUP: Searched for {num}. Found {len(results)} results.")
    except ValueError:
        print("Lookup mode requires a valid integer.", file=sys.stderr)
    except sqlite3.Error as e:
        print(f"Database error during lookup: {e}. Has the DB been built with 'build-db' mode?", file=sys.stderr)

def handle_build_db_mode(args):
    print("--- Building Gematria Database ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS phrases (value TEXT PRIMARY KEY, origin TEXT, beans_369 INTEGER)''')
    core_phrases = ['spiralborn love', 'recursive truth', 'Beans constant', 'golden spiral', 'love loop']
    for phrase in core_phrases:
        val = beans_369_gematria(phrase)
        cursor.execute("INSERT OR REPLACE INTO phrases (value, origin, beans_369) VALUES (?, ?, ?)", (phrase.lower(), 'Beans', val))
    conn.commit()
    conn.close()
    print(f"Database '{DB_PATH}' built/updated with {len(core_phrases)} core phrases.")
    log_to_file("BUILD-DB: Database built/updated.")
    
def main():
    parser = argparse.ArgumentParser(description="Quantum Oracle v2: A unified tool for esoteric text analysis.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('mode', choices=['oracle', 'delta', 'alcgem', 'unfold', 'els', 'scan', 'lookup', 'build-db'], help="The operational mode.")
    parser.add_argument('input', nargs='*', help="Input: phrase(s), file paths, or numbers depending on the mode.")
    parser.add_argument('-m', '--methods', nargs='+', default=['simple', 'jewish', 'alw'], help="Gematria methods to use.")
    args = parser.parse_args()

    available_methods = {'simple': simple_gematria, 'english': english_gematria, 'alw': alw_cipher_gematria, 'chaldean': chaldean_gematria, 'jewish': jewish_gematria, 'reverse': reverse_gematria, 'qwerty': qwerty_gematria, 'beans369': beans_369_gematria, 'reduction': reduction_gematria, 'spiral': spiral_gematria, 'grok': grok_resonance_score}
    selected_methods = []
    for key in args.methods:
        if key.lower() in available_methods:
            name = ' '.join(word.capitalize() for word in key.split('_'))
            selected_methods.append((name, available_methods[key.lower()]))
        else:
            print(f"Warning: Unknown method '{key}' ignored.", file=sys.stderr)

    if not selected_methods and args.mode in ['oracle', 'delta']:
        print("Error: No valid methods selected for a mode that requires them. Exiting.", file=sys.stderr); sys.exit(1)

    print("🔮 Quantum Oracle v2 Initialized 🔮")
    log_to_file(f"MODE: {args.mode} | INPUT: {' '.join(args.input)} | METHODS: {args.methods}")

    mode_map = {
        'delta': handle_delta_mode, 'alcgem': handle_alcgem_mode, 'unfold': handle_unfold_mode,
        'oracle': handle_oracle_mode, 'els': handle_els_mode, 'scan': handle_scan_mode,
        'lookup': handle_lookup_mode, 'build-db': handle_build_db_mode
    }
    
    # Modes that don't need methods passed
    if args.mode in ['alcgem', 'unfold', 'els', 'scan', 'lookup', 'build-db']:
        mode_map[args.mode](args)
    # Modes that do need methods
    else:
        mode_map[args.mode](args, selected_methods)

    print("\n🔮 Oracle processing complete. 🔮")

if __name__ == "__main__":
    main()

