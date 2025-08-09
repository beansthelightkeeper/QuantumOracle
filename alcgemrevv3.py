import collections
import sys
import os
import re # Import regular expressions
from itertools import permutations

# --- 0. Setup: Dictionary Directory ---
# IMPORTANT: YOU MUST CHANGE THIS PATH TO YOUR ACTUAL DIRECTORY!
# Example: DICTIONARY_DIR = "C:\\Users\\lydiaparker\\The_Oracle\\txt_db" (Windows)
# Example: DICTIONARY_DIR = "/home/youruser/The_Oracle/txt_db" (Linux)
DICTIONARY_DIR = "/Users/lydiaparker/The_Oracle/txt_db" # <--- CHANGE THIS LINE!

# --- 1. Elemental Data (Full Periodic Table) ---
ELEMENTS_DATA = {
    "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Ne": 10,
    "Na": 11, "Mg": 12, "Al": 13, "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18, "K": 19, "Ca": 20,
    "Sc": 21, "Ti": 22, "V": 23, "Cr": 24, "Mn": 25, "Fe": 26, "Co": 27, "Ni": 28, "Cu": 29, "Zn": 30,
    "Ga": 31, "Ge": 32, "As": 33, "Se": 34, "Br": 35, "Kr": 36, "Rb": 37, "Sr": 38, "Y": 39, "Zr": 40,
    "Nb": 41, "Mo": 42, "Tc": 43, "Ru": 44, "Rh": 45, "Pd": 46, "Ag": 47, "Cd": 48, "In": 49, "Sn": 50,
    "Sb": 51, "Te": 52, "I": 53, "Xe": 54, "Cs": 55, "Ba": 56, "La": 57, "Ce": 58, "Pr": 59, "Nd": 60,
    "Pm": 61, "Sm": 62, "Eu": 63, "Gd": 64, "Tb": 65, "Dy": 66, "Ho": 67, "Er": 68, "Tm": 69, "Yb": 70,
    "Lu": 71, "Hf": 72, "Ta": 73, "W": 74, "Re": 75, "Os": 76, "Ir": 77, "Pt": 78, "Au": 79, "Hg": 80,
    "Tl": 81, "Pb": 82, "Bi": 83, "Po": 84, "At": 85, "Rn": 86, "Fr": 87, "Ra": 88, "Ac": 89, "Th": 90,
    "Pa": 91, "U": 92, "Np": 93, "Pu": 94, "Am": 95, "Cm": 96, "Bk": 97, "Cf": 98, "Es": 99, "Fm": 100,
    "Md": 101, "No": 102, "Lr": 103, "Rf": 104, "Db": 105, "Sg": 106, "Bh": 107, "Hs": 108, "Mt": 109, "Ds": 110,
    "Rg": 111, "Cn": 112, "Nh": 113, "Fl": 114, "Mc": 115, "Lv": 116, "Ts": 117, "Og": 118
}

# Invert for quick lookup by value and symbol properties
ELEMENTS_BY_VALUE = collections.defaultdict(list)
# Store as (symbol, atomic_number, {char: count for symbol's letters})
ELEMENTS_FOR_SEARCH = []
for symbol, atomic_num in ELEMENTS_DATA.items():
    ELEMENTS_BY_VALUE[atomic_num].append((symbol, collections.Counter(symbol.upper())))
    ELEMENTS_FOR_SEARCH.append((symbol, atomic_num, collections.Counter(symbol.upper())))

# Sort elements by atomic number for combination search (ascending)
ELEMENTS_FOR_SEARCH.sort(key=lambda x: x[1])

# --- 2. Load Dictionary (From User's Choice) ---
VALID_WORDS = set()
MIN_WORD_LENGTH = 2 # Minimum length for a word to be considered valid
MAX_WORD_LENGTH = 20 # Maximum length for a word to be considered valid

def load_dictionary_from_dir(directory_path):
    """Loads words from all .txt files in a directory."""
    print(f"Loading dictionary from directory '{directory_path}'...")
    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found or is not a directory.")
        print("Please ensure the path in the script is correct and the directory exists.")
        sys.exit(1)

    total_files_processed = 0
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory_path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        words_in_line = re.findall(r'[a-zA-Z]+', line)
                        for word in words_in_line:
                            word_upper = word.upper()
                            if MIN_WORD_LENGTH <= len(word_upper) <= MAX_WORD_LENGTH:
                                VALID_WORDS.add(word_upper)
                total_files_processed += 1
            except Exception as e:
                print(f"Warning: Could not read file '{filepath}'. Error: {e}")
    
    print(f"Processed {total_files_processed} .txt files.")
    print(f"Loaded {len(VALID_WORDS)} unique words into the dictionary.")

def load_gematria_log_words(log_filepath="gematria_log.txt"):
    """Loads words from a gematria_log.txt file into the VALID_WORDS set."""
    print(f"Loading dictionary from log file '{log_filepath}'...")
    if not os.path.isfile(log_filepath):
        print(f"Error: Log file '{log_filepath}' not found.")
        print("Please run the other script first to generate a log, or choose another dictionary source.")
        sys.exit(1)

    # Regex to find the phrases/words from the log file format
    # Example line: --- Result for: 'Quantum Physics' ---
    log_entry_regex = re.compile(r"--- Result for: '(.+?)' ---")

    try:
        with open(log_filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Find all logged phrases
            logged_items = log_entry_regex.findall(content)

            for item in logged_items:
                # Split phrases into individual words and clean them
                words_in_item = re.findall(r'[a-zA-Z]+', item)
                for word in words_in_item:
                    word_upper = word.upper()
                    if MIN_WORD_LENGTH <= len(word_upper) <= MAX_WORD_LENGTH:
                        VALID_WORDS.add(word_upper)

    except Exception as e:
        print(f"Warning: Could not read or parse file '{log_filepath}'. Error: {e}")

    if not VALID_WORDS:
        print(f"Warning: No valid words were loaded from '{log_filepath}'. Anagram search may not work.")
    else:
        print(f"Loaded {len(VALID_WORDS)} unique words from the log file.")

# --- 3. Core Reverse Gematria Logic ---

def find_element_combinations(target_sum, max_elements=5):
    """
    Finds combinations of element symbols whose atomic numbers sum to the target.
    Uses a recursive backtracking approach.
    Returns a list of lists of element symbols.
    """
    results = []
    found_combinations_set = set()
    memo_combinations = {}

    def backtrack(current_sum, current_combination, start_index, num_elements_used):
        current_combo_tuple = tuple(sorted(current_combination))
        state_tuple = (current_sum, start_index, num_elements_used, current_combo_tuple)

        if state_tuple in memo_combinations:
            return

        if current_sum == target_sum:
            if current_combo_tuple not in found_combinations_set:
                results.append(list(current_combination))
                found_combinations_set.add(current_combo_tuple)
            memo_combinations[state_tuple] = True
            return

        if current_sum > target_sum or num_elements_used >= max_elements:
            memo_combinations[state_tuple] = True
            return

        for i in range(start_index, len(ELEMENTS_FOR_SEARCH)):
            sym, val, _ = ELEMENTS_FOR_SEARCH[i]
            current_combination.append(sym)
            backtrack(current_sum + val, current_combination, i, num_elements_used + 1)
            current_combination.pop()

        memo_combinations[state_tuple] = True

    backtrack(0, [], 0, 0)
    return results

def get_anagrams(letters_counter):
    """
    Finds valid English words that can be formed using all letters in the letters_counter.
    """
    num_letters = sum(letters_counter.values())
    if num_letters > 10:
        print(f"  (Skipping anagram search for {num_letters} letters due to performance. Max ~10 letters for practical anagram search.)")
        return []

    found_anagrams = set()
    all_possible_letters_list = list(letters_counter.elements())
    
    for perm_tuple in permutations(all_possible_letters_list):
        perm_word = "".join(perm_tuple)
        if perm_word in VALID_WORDS:
            found_anagrams.add(perm_word)
    return sorted(list(found_anagrams))

# --- 4. CLI Interface ---

def main():
    print("Welcome to Reverse Alchemical Anagram Gematria!")
    print("Enter a target number, and I'll try to find element combinations that sum to it,")
    print("then list possible English words (anagrams) from their combined letters.")

    # --- NEW: Dictionary Source Selection ---
    while True:
        source_choice = input("\nChoose a dictionary source:\n  1. Directory of .txt files (Large Dictionary)\n  2. gematria_log.txt (Words from previous calculations)\nEnter your choice (1 or 2): ").strip()
        if source_choice == '1':
            load_dictionary_from_dir(DICTIONARY_DIR)
            break
        elif source_choice == '2':
            load_gematria_log_words() # Assumes default filename "gematria_log.txt"
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")
    # --- END NEW SECTION ---

    while True:
        try:
            target_str = input("\nEnter target Gematria value (integer, or 'q' to quit): ").strip()
            if target_str.lower() == 'q':
                print("Exiting Reverse Alchemical Anagram Gematria. Goodbye!")
                sys.exit(0)

            target_number = int(target_str)
            if target_number <= 0:
                print("Please enter a positive integer.")
                continue

            max_elements_str = input(f"Max number of elements in a combination (e.g., 5, default=5, 'all' for no limit): ").strip().lower()
            max_elements = 5 # Default
            if max_elements_str == 'all':
                max_elements = float('inf') # No practical limit
            elif max_elements_str.isdigit():
                max_elements = int(max_elements_str)
                if max_elements <= 0:
                    print("Max elements must be a positive integer or 'all'. Using default (5).")
                    max_elements = 5
            elif max_elements_str:
                print("Invalid input for max elements. Using default (5).")
                max_elements = 5


            print(f"\nSearching for element combinations that sum to {target_number} (max elements: {max_elements if max_elements != float('inf') else 'no limit'})...")
            
            combinations_found = find_element_combinations(target_number, max_elements)

            if not combinations_found:
                print(f"No combinations of elements found that sum to {target_number} with {max_elements if max_elements != float('inf') else 'no limit'} elements.")
            else:
                print(f"Found {len(combinations_found)} element combination(s):")
                combinations_found.sort(key=lambda x: (len(x), " ".join(sorted(x))))

                for i, combo in enumerate(combinations_found):
                    all_letters_counter = collections.Counter()
                    display_symbols = []
                    for el_symbol in combo:
                        display_symbols.append(el_symbol)
                        for s, _, letters_c in ELEMENTS_FOR_SEARCH:
                            if s == el_symbol:
                                all_letters_counter.update(letters_c)
                                break
                    
                    combined_letters_str = "".join(sorted(all_letters_counter.elements()))
                    
                    print(f"\n--- Combination {i+1} ---")
                    print(f"  Elements: {', '.join(display_symbols)}")
                    print(f"  Total Letters: {len(combined_letters_str)} ('{combined_letters_str}')")

                    anagrams = get_anagrams(all_letters_counter)
                    if anagrams:
                        print(f"  Possible Anagrams: {', '.join(anagrams)}")
                    else:
                        if len(combined_letters_str) <= 10:
                             print("  No exact word anagrams found for these letters.")
                        else:
                            pass

        except ValueError:
            print("Invalid input. Please enter an integer number.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
