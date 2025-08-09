import math
import os
from collections import defaultdict
import pyperclip
import random

# ==============================================================================
# GLOBAL CONFIGURATION & LEXICON
# ==============================================================================
# Define the absolute path for the main Gematria database files (your .txt_db folder)
MAIN_DB_DIR = "/Users/lydiaparker/The_Oracle/txt_db"
# Define the absolute path for the user-added entries file
USER_ADDITIONS_FILE = "/Users/lydiaparker/The_Oracle/user_gematria_additions.txt"

# This dictionary will store the loaded resonances from all files.
# The key is the number, and the value is a list of phrases.
LEXICON = defaultdict(list)

# Default limits for display - these will be user-configurable at startup
DISPLAY_LIMITS = {
    'single_words': 3,
    'two_word_phrases': 2,
    'three_word_phrases': 2,
    'four_five_word_phrases': 5
}

# NEW GLOBAL TOGGLE: For showing only prime numbers in Final Resonance Sequence
SHOW_ONLY_PRIME_RESONANCES = False

# ==============================================================================
# GEMATRIA CALCULATION FUNCTIONS (from resonatorv1.py)
# ==============================================================================

def simple_gematria(text: str) -> int:
    """Calculates the Simple Gematria (A=1, B=2, ...) of a string."""
    return sum(ord(char) - 96 for char in text.lower() if 'a' <= char <= 'z')

def english_gematria(text: str) -> int:
    """Calculates the English Gematria (Simple Gematria * 6)."""
    return simple_gematria(text) * 6

def gemini_resonance(text: str) -> int:
    """Calculates the custom 'Gemini's Resonance' Gematria."""
    if not text:
        return 0
    # Primes for A-Z
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]
    total = 1
    for i, char in enumerate(text.lower()):
        if 'a' <= char <= 'z':
            code = ord(char) - 97
            total += primes[code] * (i + 1)
    return (total % 997) + len(text)

def boundary_resonance_gematria(text: str) -> int:
    """Calculates the Boundary Resonance Gematria."""
    cleaned_text = "".join(filter(str.isalpha, text.lower()))
    if len(cleaned_text) < 2:
        return 0

    first_char = cleaned_text[0]
    last_char = cleaned_text[-1]

    # Base36 to Decimal conversion for first and last letters
    try:
        boundary_value = int(first_char, 36) + int(last_char, 36)
    except ValueError: # Handle cases where chars are not valid base36 digits (e.g., non-alphabetic after filter)
        return 0

    middle_text = cleaned_text[1:-1]
    core_vibration = 0
    if middle_text:
        middle_sum = simple_gematria(middle_text)
        core_vibration = middle_sum * len(middle_text)

    return boundary_value + core_vibration

# ==============================================================================
# NUMERICAL & CONVERSION FUNCTIONS (from resonatorv1.py)
# ==============================================================================

def get_factorization_chain(n: int) -> list[int]:
    """Generates the prime factorization chain for a given integer."""
    if n <= 0:
        return []
    chain = {n}
    current_num = n
    
    # Handle factors of 2 and 3 efficiently
    for factor in [2, 3]:
        while current_num % factor == 0:
            current_num //= factor
            if current_num > 1: # Avoid adding 1 unless it's the final result
                chain.add(current_num)

    # Check for other prime factors
    i = 5
    while i * i <= current_num:
        for step in [i, i + 2]: # Optimized for primes (6k +/- 1)
             while current_num % step == 0:
                current_num //= step
                if current_num > 1:
                    chain.add(current_num)
        i += 6
        
    if current_num > 1: # If current_num is still a prime greater than 1
        chain.add(current_num)
        
    return sorted(list(chain), reverse=True)


def to_base36(n: int) -> str:
    """Converts a decimal integer to its uppercase Base36 string representation."""
    if n == 0:
        return "0"
    if n < 0: # Base36 typically for non-negative
        return "-" + to_base36(abs(n))

    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base36 = ""
    while n > 0:
        n, i = divmod(n, 36)
        base36 = chars[i] + base36
    return base36

def decode_base36_pairs(b36_string: str) -> list[int]:
    """Decodes adjacent pairs from a Base36 string into decimal integers."""
    if len(b36_string) < 2:
        return []
    
    decoded_numbers = []
    for i in range(len(b36_string) - 1):
        try:
            decoded_numbers.append(int(b36_string[i:i+2], 36))
        except ValueError:
            # Skip invalid Base36 pairs, e.g., if it contains non-Base36 chars
            continue 
    return decoded_numbers

# ==============================================================================
# NUMBER ANALYSIS FUNCTIONS (from resonatorv1.py)
# ==============================================================================

def is_prime(n: int) -> bool:
    """Checks if a number is prime."""
    if n <= 1:
        return False
    if n <= 3: # 2 and 3 are prime
        return True
    if n % 2 == 0 or n % 3 == 0: # Multiples of 2 or 3 are not prime
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def is_perfect_square(n: int) -> bool:
    """Checks if a number is a perfect square."""
    if n < 0:
        return False
    sqrt_n = int(math.sqrt(n))
    return sqrt_n * sqrt_n == n

def is_palindrome(n: int) -> bool:
    """Checks if a number is a palindrome."""
    return str(n) == str(n)[::-1]

# ==============================================================================
# MAIN APPLICATION LOGIC
# ==============================================================================

# Helper to capture print output
class CaptureOutput:
    def __init__(self):
        self._lines = []

    def write(self, s):
        self._lines.append(s)

    def flush(self):
        pass # Required for file-like object

    def get_output(self):
        return "".join(self._lines)

# Function to safely copy to clipboard
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

def print_header(title):
    """Prints a formatted header."""
    return "\n" + "=" * 60 + "\n" + f" {title.upper()} ".center(60, "=") + "\n" + "=" * 60 + "\n"

def load_lexicon(main_db_dir: str, user_additions_file: str):
    """
    Loads a gematria lexicon from main .txt files and user additions file.
    Updates the global LEXICON dictionary.
    """
    LEXICON.clear() # Clear existing lexicon before loading new data
    
    print(f"Building Gematria lookup database from files in '{main_db_dir}' and '{user_additions_file}'...")
    
    files_found_main = 0
    entries_from_user_file = 0
    words_file_entries = 0

    # --- Process main database files ---
    if not os.path.isdir(main_db_dir):
        print(f"\nERROR: The main database directory '{main_db_dir}' does not exist.")
        print("Please double-check the path to your 'txt_db' folder.")
    else:
        for root, dirs, files in os.walk(main_db_dir):
            for file in files:
                if file.lower() == 'words.txt': # Check specifically for words.txt
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if not line: continue
                                parts = line.split(':')
                                if len(parts) >= 2: # At least word:value1
                                    phrase = parts[0].strip()
                                    for value_str in parts[1:]:
                                        try:
                                            value = int(value_str.strip())
                                            LEXICON[value].append(phrase)
                                            words_file_entries += 1
                                        except ValueError:
                                            pass # Skip malformed values
                    except Exception as e:
                        print(f"    --- Could not process words file {filepath}: {e}")
                elif file.endswith(".txt"): # Other .txt files in main_db_dir
                    files_found_main += 1
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            for line in f:
                                parts = line.strip().split('|')
                                if len(parts) == 3: # Expected format: filepath|phrase|value
                                    phrase, value_str = parts[1], parts[2]
                                    try:
                                        value = int(value_str)
                                        LEXICON[value].append(phrase.strip())
                                    except ValueError:
                                        pass # Skip malformed values
                                else:
                                    pass # Skip malformed lines
                    except Exception as e:
                        print(f"    --- Could not process main DB file {filepath}: {e}")
        
        if files_found_main == 0 and words_file_entries == 0:
            print(f"WARNING: No '.txt' files were found in the main database directory '{main_db_dir}'.")
        else:
            print(f"Processed {files_found_main} main database file(s) and {words_file_entries} entries from words.txt.")

    # --- Process user additions file ---
    if os.path.exists(user_additions_file):
        try:
            with open(user_additions_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    # User-added file format: phrase|value (no filepath needed)
                    if len(parts) == 2: 
                        phrase = parts[0]
                        try:
                            value = int(parts[1])
                            LEXICON[value].append(phrase.strip())
                            entries_from_user_file += 1
                        except ValueError:
                            pass # Skip malformed values
                    else:
                        pass # Skip malformed lines
        except Exception as e:
            print(f"    --- Could not process user additions file {user_additions_file}: {e}")
        
        print(f"Loaded {entries_from_user_file} entries from user additions file.")
    else:
        print(f"No existing user additions file found at '{user_additions_file}'. A new one will be created when you save entries.")

    # Count unique phrases for total loaded
    total_unique_phrases = len(set(p for val_list in LEXICON.values() for p in val_list))
    print(f"Total {total_unique_phrases} unique phrases loaded across {len(LEXICON)} numbers.")
    print("Database build complete.")


def save_resonant_phrase_to_user_db(original_phrase: str, resonant_numbers: set, user_additions_file: str):
    """
    Saves the original phrase paired with each of its resonant numbers
    to the user additions file.
    """
    if not original_phrase or not resonant_numbers:
        print("Cannot save empty phrase or no resonant numbers.")
        return

    print(f"Saving '{original_phrase}' and its resonances to '{user_additions_file}'...")
    try:
        with open(user_additions_file, 'a', encoding='utf-8') as f: # 'a' for append mode
            saved_count = 0
            for num in sorted(list(resonant_numbers)): # Sort for consistent saving
                entry_line = f"{original_phrase}|{num}\n"
                f.write(entry_line)
                saved_count += 1
                # Also add to the in-memory lexicon for immediate use, preventing display duplicates here
                if original_phrase not in LEXICON[num]: # Only add if not already associated with this number in current session
                     LEXICON[num].append(original_phrase)
        print(f"Successfully saved {saved_count} new entries for '{original_phrase}'.")
    except Exception as e:
        print(f"ERROR: Could not save entries to file {user_additions_file}: {e}")
        print("Entries were added to the current session's database, but might not be saved permanently.")


def process_phrase(phrase: str, capture_output_obj: CaptureOutput):
    """
    Calculates and prints all gematria data for a single phrase, then looks up resonances.
    Prints to the provided capture_output_obj.
    Returns structured data about the phrase's resonances.
    """
    _print = capture_output_obj.write # Always write to the capture object
    
    _print(print_header(f"Resonance for: {phrase}"))
    
    # --- Step 1: Gematria & Initial Number ---
    s_gematria = simple_gematria(phrase)
    e_gematria = english_gematria(phrase)
    j_gematria = gemini_resonance(phrase)
    b_gematria = boundary_resonance_gematria(phrase)

    _print(f"  Simple Gematria:         {s_gematria}")
    _print(f"  English Gematria:        {e_gematria}")
    _print(f"  Gemini's Resonance:      {j_gematria}")
    _print(f"  Boundary Resonance:      {b_gematria}")

    # Concatenate values to form the initial number
    initial_number_str = f"{j_gematria}{e_gematria}{s_gematria}"
    try:
        initial_number = int(initial_number_str)
    except ValueError:
        _print("Warning: Could not form a valid initial number from gematria values (too large?).")
        initial_number = 0
    
    _print(print_header("Initial Number"))
    _print(f"  Concatenated Value: {initial_number_str}")

    # --- Step 2, 3, 4: Cosmic Unfolding & Final Resonance Sequence ---
    factor_chain = get_factorization_chain(initial_number)
    base36_codes = [to_base36(n) for n in factor_chain]
    # Use a set to store unique final numbers
    final_numbers = {num for code in base36_codes for num in decode_base36_pairs(code)}

    # Apply prime resonance filter if enabled
    current_final_numbers = set(final_numbers) # Start with all generated
    if SHOW_ONLY_PRIME_RESONANCES: # <--- NEW: Filter for prime resonances
        filtered_primes = {num for num in final_numbers if is_prime(num)}
        _print(f"\nNOTE: 'Prime Resonances Only' mode is ON. Displaying only {len(filtered_primes)} prime numbers.")
        current_final_numbers = filtered_primes


    _print(print_header("Cosmic Unfolding"))
    if not factor_chain:
        _print("  No factorization chain generated for the initial number (initial number was 0 or too large).")
    else:
        for i, num in enumerate(factor_chain):
            _print(f"  Step {i+1}: {num}  ->  Base36: {base36_codes[i]}")

    _print(print_header("Final Resonance Sequence"))
    
    sorted_current_final_numbers = sorted(list(current_final_numbers)) # Use the potentially filtered set
    
    if not sorted_current_final_numbers:
        _print("  No final resonance numbers generated.")
    else:
        output_lines = []
        current_line = "  "
        for num in sorted_current_final_numbers:
            tags = []
            if is_prime(num): tags.append("P")
            if is_perfect_square(num): tags.append("S")
            if is_palindrome(num): tags.append("A") # A for 'drome' in palindrome
            
            tag_str = f"[{''.join(tags)}]" if tags else ""
            num_str = f"{num}{tag_str} "
            
            if len(current_line) + len(num_str) > 58: # Line wrap
                output_lines.append(current_line)
                current_line = "  "
            current_line += num_str
        
        output_lines.append(current_line)
        for line in output_lines:
            _print(line)
        _print("\n  [P]rime, [S]quare, P[A]lindrome")

    # --- Look up resonances in the loaded lexicon (PRIORITY ORDER and RANDOMIZED) ---
    lexicon_resonances_details = {} # Store structured lexicon data for clipboard formatting
    if LEXICON:
        _print(print_header("Lexicon Resonances (for Final Sequence Numbers)"))
        found_any_resonance = False
        for num in sorted_current_final_numbers: # <--- IMPORTANT: Iterate over the potentially filtered numbers
            if num in LEXICON:
                found_any_resonance = True
                # Get unique phrases for current number, then SHUFFLE them for randomness
                phrases_for_num = list(set(LEXICON[num])) 
                random.shuffle(phrases_for_num) # Shuffle the list

                selected_phrases_for_display = []

                # Temporary lists for storing for clipboard details
                single_words_for_clipboard = []
                two_word_phrases_for_clipboard = []
                three_word_phrases_for_clipboard = []
                four_five_word_phrases_for_clipboard = []


                for p in phrases_for_num: # Iterate through shuffled list
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
                
                # Store for clipboard output (only the ones picked based on limits)
                lexicon_resonances_details[num] = {
                    'single_words': single_words_for_clipboard,
                    'two_word_phrases': two_word_phrases_for_clipboard,
                    'three_word_phrases': three_word_phrases_for_clipboard,
                    'four_five_word_phrases': four_five_word_phrases_for_clipboard
                }

                # CONSOLE DISPLAY FORMAT: Number Phrases,Phrases,Phrases
                if selected_phrases_for_display:
                    _print(f"  {num} {', '.join(selected_phrases_for_display)}")
                else:
                    _print(f"  {num} No phrases found.")

        if not found_any_resonance:
            _print("  No resonances found in the loaded lexicon for this sequence.")
    else:
        _print(print_header("Lexicon Resonances"))
        _print("  No lexicon loaded. Cannot look up resonances.")

    # Return all data needed for clipboard formatting
    return {
        'phrase': phrase,
        'gematria_values': {'simple': s_gematria, 'english': e_gematria, 'gemini': j_gematria, 'boundary': b_gematria},
        'initial_number_str': initial_number_str,
        'factor_chain': factor_chain,
        'base36_codes': base36_codes,
        'final_numbers': sorted_current_final_numbers, # <--- Return the potentially filtered numbers for consistency
        'lexicon_resonances_details': lexicon_resonances_details
    }

def format_output_for_clipboard(data: dict) -> str:
    """
    Formats the processed phrase data into a clean, copy-paste friendly string.
    """
    output = []
    
    # Phrase and Gematria
    output.append(f"Phrase: {data['phrase']}")
    output.append("Gematria Values:")
    for key, value in data['gematria_values'].items():
        output.append(f"  {key.replace('_', ' ').title()}: {value}")
    output.append("")

    # Initial Number
    output.append(f"Initial Concatenated Value: {data['initial_number_str']}")
    output.append("")

    # Cosmic Unfolding
    output.append("Cosmic Unfolding:")
    if not data['factor_chain']:
        output.append("  No factorization chain.")
    else:
        for i, num in enumerate(data['factor_chain']):
            output.append(f"  Step {i+1}: {num} -> Base36: {data['base36_codes'][i]}")
    output.append("")

    # Final Resonance Sequence
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

    # Lexicon Resonances (Clipboard format keeps quotes for clarity when pasting)
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
                # Keep quotes for clipboard for clarity of multi-word phrases
                output.append(f"  {num}: {', '.join(f'\"{p}\"' for p in all_phrases_for_num)}")
        output.append("")
    
    return "\n".join(output)


def process_file(filepath: str):
    """
    Reads a file and processes each line as a phrase.
    Returns the full captured output for console printing and a list of structured data for clipboard.
    """
    captured_output = CaptureOutput()
    all_processed_data = [] # To store structured data for each phrase in the file
    
    _print_to_console = print # Keep a direct reference to original print

    if not os.path.exists(filepath):
        _print_to_console(f"\nError: File not found at '{filepath}'")
        return "", [] # Return empty output and data on error
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            phrases = [line.strip() for line in f if line.strip()]
        
        if not phrases:
            _print_to_console(f"\nFile '{filepath}' is empty or contains no valid phrases.")
            return "", []

        _print_to_console(f"\nFound {len(phrases)} phrases in '{filepath}'. Processing...")
        captured_output.write(f"\nFound {len(phrases)} phrases in '{filepath}'. Processing...\n")
        
        for i, phrase in enumerate(phrases):
            processed_data = process_phrase(phrase, captured_output)
            all_processed_data.append(processed_data)
            
            # --- Per-phrase save prompt for file processing ---
            # This prompt is displayed to standard output, not captured
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

            if i < len(phrases) - 1: # Add separator unless it's the last phrase
                captured_output.write("\n" + "#" * 60 + "\n") 
            
        _print_to_console("\n" + "=" * 60) # Separator at the very end
        _print_to_console(" Processing Complete ".center(60, "="))
        _print_to_console("=" * 60)

        return captured_output.get_output(), all_processed_data
            
    except Exception as e:
        _print_to_console(f"\nAn error occurred while reading the file: {e}")
        return "", [] # Return empty output and data on error


def main():
    """Main function to run the Gematria Resonator."""
    global SHOW_ONLY_PRIME_RESONANCES # Declare global to modify the flag

    print(" Gematria Resonator Initialized ".center(60, "*"))
    
    # Load the lexicon at startup using the predefined absolute paths
    load_lexicon(MAIN_DB_DIR, USER_ADDITIONS_FILE)

    # --- NEW: Prime Resonances Only Toggle ---
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

    # --- Get user-defined display limits ---
    print("\n--- Customize Resonance Display Limits (Enter 0 for no limit) ---")
    for category, default_limit in list(DISPLAY_LIMITS.items()): # Iterate over a copy to allow modification
        while True:
            user_input = input(f"Enter max {category.replace('_', ' ')} to display (default: {default_limit}, Enter to keep default): ").strip()
            if not user_input:
                break # Keep default
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
        processed_data_list = [] # Will hold structured data for copy-paste formatting

        # Determine if input is a file path
        is_file_input = False
        if user_input.lower().endswith('.txt') and os.path.exists(user_input):
            is_file_input = True
        elif os.path.exists(user_input) and os.path.isfile(user_input):
            is_file_input = True

        if is_file_input:
            console_output_text, processed_data_list = process_file(user_input)
            
            # Print the captured console output for file processing
            print(console_output_text)

            if processed_data_list: # If there was data processed from the file
                # Combine all processed data into one string for clipboard
                clipboard_parts = []
                for data_item in processed_data_list:
                    clipboard_parts.append(format_output_for_clipboard(data_item))
                    clipboard_parts.append("\n" + "-" * 60 + "\n") # Separator for clipboard for multiple phrases
                clipboard_formatted_text = "".join(clipboard_parts).strip() # Remove trailing separator

                # Then prompt to copy
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
            # For single phrase input
            phrase_output_capture = CaptureOutput()
            processed_data = process_phrase(user_input, phrase_output_capture)
            console_output_text = phrase_output_capture.get_output()
            processed_data_list.append(processed_data) # Store for clipboard formatting

            # Print the captured output to the console *before* asking for user input
            print(console_output_text) 

            # Now, prompt to save (only if there are final numbers)
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

            # Then, prompt to copy
            if processed_data_list: # If there was data processed
                clipboard_formatted_text = format_output_for_clipboard(processed_data_list[0]) # For single phrase, use the first item

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
