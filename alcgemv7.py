import collections
import sys

# --- 1. Elemental Data ---
# Source: Data compiled from standard scientific sources.
# Atomic numbers and boiling points (in Kelvin) are provided.
# 'None' for boiling point indicates an unknown or inapplicable value.

ELEMENT_PROPERTIES = {
    # Symbol: (Atomic Number, Boiling Point in K)
    "H": (1, 20.271), "He": (2, 4.222), "Li": (3, 1603.0), "Be": (4, 2742.0), "B": (5, 4200.0),
    "C": (6, 4300.0), "N": (7, 77.355), "O": (8, 90.188), "F": (9, 85.03), "Ne": (10, 27.104),
    "Na": (11, 1156.09), "Mg": (12, 1363.0), "Al": (13, 2743.0), "Si": (14, 3173.0), "P": (15, 553.7),
    "S": (16, 717.8), "Cl": (17, 239.11), "Ar": (18, 87.302), "K": (19, 1032.0), "Ca": (20, 1757.0),
    "Sc": (21, 3109.0), "Ti": (22, 3560.0), "V": (23, 3680.0), "Cr": (24, 2944.0), "Mn": (25, 2334.0),
    "Fe": (26, 3134.0), "Co": (27, 3200.0), "Ni": (28, 3003.0), "Cu": (29, 2835.0), "Zn": (30, 1180.0),
    "Ga": (31, 2477.0), "Ge": (32, 3093.0), "As": (33, 887.0), "Se": (34, 958.0), "Br": (35, 332.0),
    "Kr": (36, 119.93), "Rb": (37, 961.0), "Sr": (38, 1650.0), "Y": (39, 3203.0), "Zr": (40, 4650.0),
    "Nb": (41, 5017.0), "Mo": (42, 4912.0), "Tc": (43, 4538.0), "Ru": (44, 4423.0), "Rh": (45, 3968.0),
    "Pd": (46, 3236.0), "Ag": (47, 2435.0), "Cd": (48, 1040.0), "In": (49, 2345.0), "Sn": (50, 2875.0),
    "Sb": (51, 1860.0), "Te": (52, 1261.0), "I": (53, 457.4), "Xe": (54, 165.05), "Cs": (55, 944.0),
    "Ba": (56, 2118.0), "La": (57, 3737.0), "Ce": (58, 3716.0), "Pr": (59, 3403.0), "Nd": (60, 3347.0),
    "Pm": (61, 3273.0), "Sm": (62, 2067.0), "Eu": (63, 1860.0), "Gd": (64, 3273.0), "Tb": (65, 3396.0),
    "Dy": (66, 2840.0), "Ho": (67, 2873.0), "Er": (68, 3141.0), "Tm": (69, 2223.0), "Yb": (70, 1469.0),
    "Lu": (71, 3675.0), "Hf": (72, 4876.0), "Ta": (73, 5731.0), "W": (74, 6203.0), "Re": (75, 5869.0),
    "Os": (76, 5285.0), "Ir": (77, 4701.0), "Pt": (78, 4098.0), "Au": (79, 3243.0), "Hg": (80, 629.88),
    "Tl": (81, 1746.0), "Pb": (82, 2022.0), "Bi": (83, 1837.0), "Po": (84, 1235.0), "At": (85, 610.0),
    "Rn": (86, 211.5), "Fr": (87, 950.0), "Ra": (88, 1413.0), "Ac": (89, 3471.0), "Th": (90, 5061.0),
    "Pa": (91, 4300.0), "U": (92, 4404.0), "Np": (93, 4273.0), "Pu": (94, 3505.0), "Am": (95, 2880.0),
    "Cm": (96, 3383.0), "Bk": (97, 2900.0), "Cf": (98, 1743.0), "Es": (99, 1269.0), "Fm": (100, None),
    "Md": (101, None), "No": (102, None), "Lr": (103, None), "Rf": (104, None), "Db": (105, None),
    "Sg": (106, None), "Bh": (107, None), "Hs": (108, None), "Mt": (109, None), "Ds": (110, None),
    "Rg": (111, None), "Cn": (112, None), "Nh": (113, None), "Fl": (114, None), "Mc": (115, None),
    "Lv": (116, None), "Ts": (117, None), "Og": (118, None)
}

# Pre-process elements for the search algorithm
ELEMENTS_FOR_SEARCH = []
for symbol in ELEMENT_PROPERTIES:
    ELEMENTS_FOR_SEARCH.append((symbol, collections.Counter(symbol.upper())))
ELEMENTS_FOR_SEARCH.sort(key=lambda x: (-len(x[0]), x[0]))

# --- 2. Core Logic ---

_memo = {}  # Memoization cache for the recursive search

def find_all_element_combinations(letters_counter):
    """
    Recursively finds ALL possible combinations of elements from a letter pool.
    Returns a list of lists of element symbols.
    """
    current_state = tuple(sorted(letters_counter.items()))
    if current_state in _memo:
        return _memo[current_state]

    all_combinations = [[]]
    for element_symbol, element_letters_counter in ELEMENTS_FOR_SEARCH:
        if all(letters_counter[char] >= count for char, count in element_letters_counter.items()):
            new_letters_counter = letters_counter.copy()
            new_letters_counter.subtract(element_letters_counter)
            sub_combinations = find_all_element_combinations(+new_letters_counter)
            for sub_combo in sub_combinations:
                all_combinations.append([element_symbol] + sub_combo)

    unique_combinations = {tuple(sorted(combo)) for combo in all_combinations}
    _memo[current_state] = [list(combo) for combo in unique_combinations]
    return _memo[current_state]

def analyze_combinations(text_input, analysis_mode='standard'):
    """
    Finds all element combinations and calculates their various alchemical properties.
    Can operate in 'standard' or 'bookend' mode.
    """
    normalized_input = ''.join(filter(str.isalpha, text_input)).upper()
    if not normalized_input:
        return {'error': "No alphabetic characters found in input."}

    first_letter, last_letter, core_letters = "", "", normalized_input
    if analysis_mode == 'bookend':
        if len(normalized_input) < 2:
            return {'error': "Bookend analysis requires at least 2 letters."}
        first_letter = normalized_input[0]
        last_letter = normalized_input[-1]
        core_letters = normalized_input[1:-1]

    initial_letters_pool = collections.Counter(core_letters)
    _memo.clear()
    all_combos = find_all_element_combinations(initial_letters_pool)

    results = []
    for combo in all_combos:
        if not combo and analysis_mode == 'standard':
            continue
        
        atomic_numbers = [ELEMENT_PROPERTIES[el][0] for el in combo]
        boiling_points = [ELEMENT_PROPERTIES[el][1] for el in combo if ELEMENT_PROPERTIES[el][1] is not None]
        base36_sum = sum(int(el, 36) for el in combo)
        avg_boiling_point = sum(boiling_points) / len(boiling_points) if boiling_points else None
        
        temp_pool = initial_letters_pool.copy()
        temp_pool.subtract(collections.Counter("".join(combo).upper()))
        remaining_str = "".join(sorted((+temp_pool).elements()))

        results.append({
            'elements': combo,
            'atomic_sum': sum(atomic_numbers),
            'avg_boiling_point': avg_boiling_point,
            'base36_sum': base36_sum,
            'letters_used': len("".join(combo)),
            'unmatched_letters': remaining_str,
            'bookends': (first_letter, last_letter) if analysis_mode == 'bookend' else None
        })

    if not any(res['avg_boiling_point'] is not None for res in results) and analysis_mode == 'standard':
         if not any(res['atomic_sum'] > 0 for res in results):
            return {'error': "No element combinations could be formed."}

    return {'results': results}

# --- 3. CLI Interface ---

def display_results(phrase, data, mode='best', perfect_only=False):
    """Formats and prints the results based on the selected mode and filters."""
    log_content = []
    
    if 'error' in data:
        print(f"\n--- Analysis for: '{phrase}' ---\n{data['error']}\n" + "-" * (len(phrase) + 22))
        return

    results = data.get('results', [])
    if not results:
        print(f"\n--- Analysis for: '{phrase}' ---\nNo valid combinations found.\n" + "-" * (len(phrase) + 22))
        return
        
    if perfect_only:
        results = [res for res in results if not res['unmatched_letters']]
        if not results:
            print(f"\n--- Analysis for: '{phrase}' ---\nNo 'perfect matches' could be found.\n" + "-" * (len(phrase) + 22))
            return

    results.sort(key=lambda x: (x['letters_used'], x.get('avg_boiling_point') or -1), reverse=True)

    # Determine if this is a bookend display
    is_bookend = results[0].get('bookends') is not None
    
    if mode == 'all':
        title_filter = " (Perfect Matches Only)" if perfect_only else ""
        analysis_type = "Bookend " if is_bookend else ""
        title = f"--- All {len(results)} {analysis_type}Possibilities for: '{phrase}'{title_filter} ---"
        print(f"\n{title}")
        log_content.append(f"{title}\n")

        for i, res in enumerate(results):
            bp_str = f"{res['avg_boiling_point']:.2f} K" if res['avg_boiling_point'] is not None else "N/A"
            elements_str = f"({', '.join(res['elements'])})" if res['elements'] else "()"
            
            if is_bookend:
                first, last = res['bookends']
                display_str = f"  {i+1}. Result: {first}{elements_str}{last}"
            else:
                display_str = f"  {i+1}. Elements: {', '.join(res['elements'])}"

            print(display_str)
            print(f"     - Avg Boiling Point: {bp_str}")
            print(f"     - Atomic Number Sum: {res['atomic_sum']}")
            print(f"     - Base-36 Symbol Sum: {res['base36_sum']}")
            print(f"     (Uses {res['letters_used']} letters from core. Unmatched: '{res['unmatched_letters']}')")
            log_content.extend([f"{display_str}\n", f"     - Avg Boiling Point: {bp_str}\n", f"     - Atomic Number Sum: {res['atomic_sum']}\n", f"     - Base-36 Symbol Sum: {res['base36_sum']}\n", f"     (Uses {res['letters_used']} letters from core. Unmatched: '{res['unmatched_letters']}')\n"])
        
        footer = "-" * len(title)
        print(footer)
        log_content.append(f"{footer}\n\n")

    else: # 'best' or 'lowest'
        top_tier_results = [res for res in results if res['letters_used'] == results[0]['letters_used']]
        
        if mode == 'best':
            final_result = max(top_tier_results, key=lambda x: x.get('avg_boiling_point') or -1)
            mode_title = "Highest Avg. Boiling Point"
        else: # 'lowest'
            final_result = min(top_tier_results, key=lambda x: x.get('avg_boiling_point') or float('inf'))
            mode_title = "Lowest Avg. Boiling Point"

        title_filter = " (Perfect Match)" if perfect_only and not final_result['unmatched_letters'] else ""
        analysis_type = "Bookend " if is_bookend else ""
        title = f"--- {mode_title} {analysis_type}Result for: '{phrase}'{title_filter} ---"
        
        bp_str = f"{final_result['avg_boiling_point']:.2f} K" if final_result['avg_boiling_point'] is not None else "N/A"
        elements_str = f"({', '.join(final_result['elements'])})" if final_result['elements'] else "()"

        print(f"\n{title}")
        if is_bookend:
            first, last = final_result['bookends']
            print(f"Result: {first}{elements_str}{last}")
        else:
            print(f"Elements: {', '.join(final_result['elements'])}")
        
        print(f"  - Avg Boiling Point: {bp_str}")
        print(f"  - Atomic Number Sum: {final_result['atomic_sum']}")
        print(f"  - Base-36 Symbol Sum: {final_result['base36_sum']}")
        print(f"Note: This result was chosen from combinations using {final_result['letters_used']} letters.")
        if final_result['unmatched_letters']:
            print(f"Unmatched letters from core: '{final_result['unmatched_letters']}'")
        
        footer = "-" * len(title)
        print(footer)
        # Logging logic would be here, similar to 'all' mode
        
    try:
        with open("alchemy_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write("".join(log_content))
        if log_content:
            print(f"Results for '{phrase}' also saved to alchemy_log.txt")
    except IOError as e:
        print(f"\n[Error] Could not write to alchemy_log.txt: {e}")

def main():
    """Main function for the CLI application."""
    print("Welcome to the Alchemical Properties Calculator!")

    while True:
        user_input = input("\nEnter word or phrase (or 'q' to quit): ").strip()
        if user_input.lower() == 'q':
            print("Exiting. Goodbye!")
            sys.exit(0)
        if not user_input:
            print("Input cannot be empty.")
            continue

        analysis_type = None
        while analysis_type not in ['1', '2']:
            analysis_type = input("Select analysis type:\n  1. Standard\n  2. Bookend (Preserve first and last letter)\nEnter choice (1-2): ").strip()

        mode_option = None
        mode_map = {'1': 'best', '2': 'lowest', '3': 'all'}
        while mode_option not in mode_map:
            mode_option = input("Select calculation mode (sorted by boiling point):\n  1. Highest (Default)\n  2. Lowest\n  3. Show All\nEnter choice (1-3): ").strip()
            if not mode_option: mode_option = '1'
        
        selected_mode = mode_map[mode_option]

        perfect_only_choice = input("Only show perfect matches (all core letters used)? (Y/N, default=N): ").strip().upper()
        perfect_only_flag = True if perfect_only_choice == 'Y' else False

        calculation_data = analyze_combinations(user_input, 'bookend' if analysis_type == '2' else 'standard')
        display_results(user_input, calculation_data, selected_mode, perfect_only_flag)

if __name__ == "__main__":
    main()

