import collections
import sys

# --- 1. Elemental Data (Full Periodic Table) ---
# Source: Standard Periodic Table atomic numbers
# Note: Symbol casing is standard (e.g., 'He', 'Fe', 'Og')
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

# Pre-process elements for efficient lookup during recursive search
# Store as (symbol, atomic_number, {char: count for symbol's letters})
ELEMENTS_FOR_SEARCH = []
for symbol, atomic_num in ELEMENTS_DATA.items():
    ELEMENTS_FOR_SEARCH.append((
        symbol,
        atomic_num,
        collections.Counter(symbol.upper()) # Use uppercase for matching
    ))

# Sort elements by length (longer first) then alphabetically for consistent greedy matching logic
# (though the recursive search handles different orders, this can sometimes prune branches faster)
ELEMENTS_FOR_SEARCH.sort(key=lambda x: (-len(x[0]), x[0]))

# --- 2. Core Gematria Logic ---

# Memoization cache for dynamic programming approach
_memo = {}

def find_best_element_combination(letters_counter):
    """
    Recursively finds the best combination of elements from a given letter counter.
    "Best" is defined as:
    1. Maximizes the number of letters consumed.
    2. Among those with max letters, maximizes the total atomic number.
    Returns (total_atomic_number, num_letters_consumed, list_of_elements_used)
    """
    # Convert Counter to a hashable tuple for memoization
    current_state = tuple(sorted(letters_counter.items()))
    if current_state in _memo:
        return _memo[current_state]

    best_score = 0
    best_letters_consumed = 0
    best_elements = []

    # Try to form single-letter elements first (if no two-letter match)
    # The sorted ELEMENTS_FOR_SEARCH (longer symbols first) helps prioritize.
    for element_symbol, atomic_num, element_letters_counter in ELEMENTS_FOR_SEARCH:
        # Check if the current element symbol can be formed from the remaining letters
        can_form = True
        for char, count in element_letters_counter.items():
            if letters_counter[char] < count:
                can_form = False
                break

        if can_form:
            # Create a new counter by consuming the letters
            new_letters_counter = letters_counter.copy()
            for char, count in element_letters_counter.items():
                new_letters_counter[char] -= count
            new_letters_counter = +new_letters_counter # Remove zero or negative counts

            # Recurse for the remaining letters
            sub_score, sub_letters_consumed, sub_elements = \
                find_best_element_combination(new_letters_counter)

            current_total_score = atomic_num + sub_score
            current_total_letters_consumed = sum(element_letters_counter.values()) + sub_letters_consumed
            current_elements_list = [element_symbol] + sub_elements

            # Update best combination
            if (current_total_letters_consumed > best_letters_consumed or
                (current_total_letters_consumed == best_letters_consumed and current_total_score > best_score)):
                best_score = current_total_score
                best_letters_consumed = current_total_letters_consumed
                best_elements = current_elements_list

    _memo[current_state] = (best_score, best_letters_consumed, best_elements)
    return best_score, best_letters_consumed, best_elements

def calculate_gematria(text_input):
    """
    Calculates the Alchemical Anagram Gematria for a given text input.
    """
    # Normalize input: uppercase and remove non-alphabetic characters for the pool
    normalized_input = ''.join(filter(str.isalpha, text_input)).upper()
    if not normalized_input:
        return 0, 0, [], "No alphabetic characters found in input."

    initial_letters_pool = collections.Counter(normalized_input)
    original_letters_count = len(normalized_input)

    # Clear memoization cache for each new calculation
    _memo.clear()

    total_gematria_value, letters_consumed, elements_used = \
        find_best_element_combination(initial_letters_pool)

    # Calculate remaining (unmatched) letters
    remaining_letters_count = original_letters_count - letters_consumed
    # Reconstruct remaining_letters_counter
    temp_pool = collections.Counter(normalized_input)
    for el_symbol in elements_used:
        for char in ELEMENTS_FOR_SEARCH_MAP[el_symbol]: # Use a temp map for symbol->letters
            temp_pool[char] -= 1
    remaining_letters_counter = +temp_pool # Remove zero or negative counts
    remaining_letters_str = "".join(sorted(remaining_letters_counter.elements()))


    status_message = ""
    if remaining_letters_count > 0:
        status_message = (f"Note: {remaining_letters_count} letters ({remaining_letters_str}) "
                          f"could not be matched to elements.")

    return total_gematria_value, letters_consumed, elements_used, status_message

# Create a map for quick lookup of element symbol to its letter Counter (for reconstructing remaining letters)
ELEMENTS_FOR_SEARCH_MAP = {sym: letters_c for sym, _, letters_c in ELEMENTS_FOR_SEARCH}

# --- 3. CLI Interface ---

def display_results(phrase, total_value, letters_used, elements, message):
    """Formats and prints the gematria results."""
    print(f"\n--- Result for: '{phrase}' ---")
    print(f"Alchemical Anagram Gematria Value: {total_value}")
    print(f"Elements Used: {', '.join(elements) if elements else 'None'}")
    if message:
        print(message)
    print("-" * (len(phrase) + 20))

def main():
    """Main function for the CLI application."""
    print("Welcome to Alchemical Anagram Gematria!")
    print("This system finds the highest value element combinations from your input letters.")
    print("Capitalization does not matter.")

    while True:
        user_input = input("\nEnter word or phrase (or 'q' to quit): ").strip()
        if user_input.lower() == 'q':
            print("Exiting Alchemical Anagram Gematria. Goodbye!")
            sys.exit(0)

        if not user_input:
            print("Input cannot be empty. Please try again.")
            continue

        process_option = None
        while process_option not in ['W', 'P']:
            process_option = input("Process by (W)ord or by (P)hrase? ").strip().upper()
            if process_option not in ['W', 'P']:
                print("Invalid option. Please enter 'W' or 'P'.")

        if process_option == 'W':
            words = user_input.split()
            for word in words:
                value, letters_consumed, elements, message = calculate_gematria(word)
                display_results(word, value, letters_consumed, elements, message)
        else: # process_option == 'P'
            value, letters_consumed, elements, message = calculate_gematria(user_input)
            display_results(user_input, value, letters_consumed, elements, message)

if __name__ == "__main__":
    main()
