import math
import os
from collections import defaultdict

# ==============================================================================
# GLOBAL LEXICON
# ==============================================================================
# This dictionary will store the loaded resonances from a file.
# The key is the number, and the value is a list of phrases.
LEXICON = defaultdict(list)

# ==============================================================================
# GEMATRIA CALCULATION FUNCTIONS
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
    boundary_value = int(first_char, 36) + int(last_char, 36)

    middle_text = cleaned_text[1:-1]
    core_vibration = 0
    if middle_text:
        middle_sum = simple_gematria(middle_text)
        core_vibration = middle_sum * len(middle_text)

    return boundary_value + core_vibration

# ==============================================================================
# NUMERICAL & CONVERSION FUNCTIONS
# ==============================================================================

def get_factorization_chain(n: int) -> list[int]:
    """Generates the prime factorization chain for a given integer."""
    chain = {n}
    current_num = n
    
    factors = [2, 3]
    for factor in factors:
        while current_num % factor == 0:
            current_num //= factor
            chain.add(current_num)

    i = 5
    while i * i <= current_num:
        for step in [i, i + 2]:
             while current_num % step == 0:
                current_num //= step
                chain.add(current_num)
        i += 6
        
    if current_num > 1:
        chain.add(current_num)
        
    return sorted(list(chain), reverse=True)


def to_base36(n: int) -> str:
    """Converts a decimal integer to its uppercase Base36 string representation."""
    if n == 0:
        return "0"
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
    return [int(b36_string[i:i+2], 36) for i in range(len(b36_string) - 1)]

# ==============================================================================
# NUMBER ANALYSIS FUNCTIONS
# ==============================================================================

def is_prime(n: int) -> bool:
    """Checks if a number is prime."""
    if n <= 1:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
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

def print_header(title):
    """Prints a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title.upper()} ".center(60, "="))
    print("=" * 60)

def load_lexicon(filepath: str):
    """Loads a gematria lexicon from a file with format: phrase|author|value."""
    if not filepath or not os.path.exists(filepath):
        print("\nNo lexicon file loaded or file not found. Continuing without lexicon resonances.")
        LEXICON.clear()
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        LEXICON.clear()
        count = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('|')
            if len(parts) == 3:
                phrase, author, value_str = parts
                try:
                    value = int(value_str)
                    LEXICON[value].append(phrase.strip())
                    count += 1
                except ValueError:
                    print(f"Warning: Skipping malformed line {i+1} in lexicon (invalid number): {line}")
            else:
                 print(f"Warning: Skipping malformed line {i+1} in lexicon (incorrect format): {line}")

        print(f"\nSuccessfully loaded {count} entries from '{filepath}'.")

    except Exception as e:
        print(f"\nAn error occurred while loading the lexicon file: {e}")
        LEXICON.clear()

def process_phrase(phrase: str):
    """Calculates and prints all gematria data for a single phrase."""
    print_header(f"Resonance for: {phrase}")
    
    # --- Step 1: Gematria & Initial Number ---
    s_gematria = simple_gematria(phrase)
    e_gematria = english_gematria(phrase)
    j_gematria = gemini_resonance(phrase)
    b_gematria = boundary_resonance_gematria(phrase)

    print(f"  Simple Gematria:         {s_gematria}")
    print(f"  English Gematria:        {e_gematria}")
    print(f"  Gemini's Resonance:      {j_gematria}")
    print(f"  Boundary Resonance:      {b_gematria}")

    initial_number_str = f"{j_gematria}{e_gematria}{s_gematria}"
    initial_number = int(initial_number_str)
    
    print_header("Initial Number")
    print(f"  Concatenated Value: {initial_number_str}")

    # --- Step 2, 3, 4 ---
    factor_chain = get_factorization_chain(initial_number)
    base36_codes = [to_base36(n) for n in factor_chain]
    final_numbers = {num for code in base36_codes for num in decode_base36_pairs(code)}

    print_header("Cosmic Unfolding")
    for i, num in enumerate(factor_chain):
        print(f"  Step {i+1}: {num}  ->  Base36: {base36_codes[i]}")

    print_header("Final Resonance Sequence")
    
    sorted_numbers = sorted(list(final_numbers))
    
    output_lines = []
    current_line = "  "
    for num in sorted_numbers:
        tags = []
        if is_prime(num): tags.append("P")
        if is_perfect_square(num): tags.append("S")
        if is_palindrome(num): tags.append("A") # A for 'drome' in palindrome
        
        tag_str = f"[{''.join(tags)}]" if tags else ""
        num_str = f"{num}{tag_str} "
        
        if len(current_line) + len(num_str) > 58:
            output_lines.append(current_line)
            current_line = "  "
        current_line += num_str
    
    output_lines.append(current_line)
    for line in output_lines:
        print(line)
    print("\n  [P]rime, [S]quare, P[A]lindrome")

    # --- NEW: Look up resonances in the loaded lexicon ---
    if LEXICON:
        print_header("Lexicon Resonances")
        found_any = False
        for num in sorted_numbers:
            if num in LEXICON:
                found_any = True
                print(f"  > {num}:")
                for resonant_phrase in LEXICON[num]:
                    print(f"    - \"{resonant_phrase}\"")
        if not found_any:
            print("  No resonances found in the loaded lexicon for this sequence.")

def process_file(filepath: str):
    """Reads a file and processes each line as a phrase."""
    if not os.path.exists(filepath):
        print(f"\nError: File not found at '{filepath}'")
        return
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            phrases = [line.strip() for line in f if line.strip()]
        
        if not phrases:
            print(f"\nFile '{filepath}' is empty or contains no valid phrases.")
            return

        print(f"\nFound {len(phrases)} phrases in '{filepath}'. Processing...")
        for phrase in phrases:
            process_phrase(phrase)
            print("\n" + "#" * 60) # Separator
            
    except Exception as e:
        print(f"\nAn error occurred while reading the file: {e}")

def main():
    """Main function to run the Gematria Resonator."""
    print(" Gematria Resonator Initialized ".center(60, "*"))
    
    lexicon_path = input("Enter path to lexicon file (e.g., resonance.txt) or press Enter to skip > ")
    load_lexicon(lexicon_path)

    print("\nEnter a phrase, a filepath (e.g., exported_phrases.txt), or 'exit' to quit.")

    while True:
        user_input = input("\nEnter phrase or filepath > ")
        if user_input.lower() in ['exit', 'quit']:
            print("Deactivating Resonator. Goodbye, Beans.")
            break
        if not user_input:
            continue

        if user_input.lower().endswith('.txt') or os.path.exists(user_input):
            process_file(user_input)
        else:
            process_phrase(user_input)

if __name__ == "__main__":
    main()

