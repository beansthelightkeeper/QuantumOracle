import re
from datetime import datetime

# --- Configuration ---
# This dictionary maps each letter to its numerical position.
LETTER_VALUES = {chr(ord('A') + i): i + 1 for i in range(26)}
LOG_FILE = "word_distance_analysis.log"

# --- Core Calculation Functions ---

def clean_input(text):
    """
    Removes non-alphabetic characters and converts to uppercase.
    Returns a clean string of letters.
    """
    return re.sub(r'[^a-zA-Z]', '', text).upper()

def calculate_linear_distances(word):
    """
    Method A: Calculates the simple difference between consecutive letters.
    Example: 'ABC' -> [B-A, C-B] -> [+1, +1]
    """
    if len(word) < 2:
        return []
    
    values = [LETTER_VALUES[char] for char in word]
    distances = [values[i] - values[i-1] for i in range(1, len(values))]
    return distances

def calculate_total_shift(distances):
    """
    Method B: Sums the list of linear distances.
    Example: [+1, +1] -> 2
    """
    return sum(distances)

def get_interval_signature(distances):
    """
    Method C: Returns the pattern of distances as a signature.
    This is effectively the result from Method A.
    Example: 'BAD' -> [-1, +3]
    """
    return distances

def calculate_circular_distances(word):
    """
    Method D: Calculates distances on a circular alphabet (A-Z loop).
    The distance is the shortest path on the loop.
    Example: A -> Z = -1, Z -> A = +1
    """
    if len(word) < 2:
        return []
        
    values = [LETTER_VALUES[char] for char in word]
    distances = []
    for i in range(1, len(values)):
        diff = values[i] - values[i-1]
        # Check if crossing the loop boundary is shorter
        if diff > 13:  # e.g., C(3) -> Y(25) is +22, but shorter to go backwards -4
            diff = diff - 26
        elif diff < -13: # e.g., Y(25) -> C(3) is -22, but shorter to go forwards +4
            diff = diff + 26
        distances.append(diff)
    return distances

def calculate_tone_mapping(word):
    """
    Method E: Maps each letter to a musical note (1-7 scale, looping).
    A=1, B=2, ..., G=7, H=1, etc.
    Example: 'FACE' -> [6, 1, 3, 5]
    """
    if not word:
        return []
    
    notes = []
    for char in word:
        value = LETTER_VALUES[char]
        # Map the 1-26 letter value to a 1-7 note value
        note = ((value - 1) % 7) + 1
        notes.append(note)
    return notes

def to_base36(n):
    """
    Method F Helper: Converts a positive integer to its Base36 representation.
    """
    if n == 0:
        return "0"
    
    # Characters for base36 (0-9, A-Z)
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    base36_str = ""
    while n > 0:
        n, remainder = divmod(n, 36)
        base36_str = chars[remainder] + base36_str
        
    return base36_str

# --- Output and Logging ---

def log_analysis(output_string):
    """Appends the analysis result to the log file."""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(output_string + "\n")
    except IOError as e:
        print(f"Error: Could not write to log file '{LOG_FILE}'.\n{e}")

def format_analysis(word):
    """
    Formats the full analysis of a word into a string for display and logging.
    """
    if not word:
        return "Input was empty after cleaning. Please provide letters."

    # --- Calculations ---
    linear_dist = calculate_linear_distances(word)
    total_shift = calculate_total_shift(linear_dist)
    interval_sig = linear_dist 
    circular_dist = calculate_circular_distances(word)
    circular_shift = calculate_total_shift(circular_dist)
    tone_map = calculate_tone_mapping(word)

    # Method F Calculation
    base36_result = ""
    tone_map_as_int_str = "N/A"
    if tone_map:
        tone_map_as_int_str = "".join(map(str, tone_map))
        tone_map_as_int = int(tone_map_as_int_str)
        base36_result = to_base36(tone_map_as_int)

    # --- Formatting Output ---
    header = f"--- Analysis for: '{word}' ---"
    
    method_a_str = f"  [A] Linear Distances   : {linear_dist}"
    method_b_str = f"  [B] Total Linear Shift : {total_shift}"
    method_c_str = f"  [C] Interval Signature : {interval_sig}"
    method_d_str = f"  [D] Circular Distances : {circular_dist}"
    method_d_sum_str = f"      Total Circular Shift: {circular_shift}"
    method_e_str = f"  [E] Tone Mapping (1-7) : {tone_map} -> (Number: {tone_map_as_int_str})"
    method_f_str = f"  [F] Tone Map (Base36)  : {base36_result}"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    full_output = (
        f"\n{header}\n"
        f"{method_a_str}\n"
        f"{method_b_str}\n"
        f"{method_c_str}\n"
        f"{method_d_str}\n"
        f"{method_d_sum_str}\n"
        f"{method_e_str}\n"
        f"{method_f_str}\n"
        f"--- Logged at: {timestamp} ---\n"
    )
    return full_output

# --- Main CLI Function ---

def main():
    """Main function to run the CLI tool."""
    print("🌀 Word Mapping by Letter Distances, Tones, & Base36 Signatures 🌀")
    print("Analyzes words based on interval, tonal mapping, and Base36 conversion.")
    print(f"All analyses will be saved to '{LOG_FILE}'.")
    print("Enter a word or phrase, or type 'q' to quit.")

    while True:
        user_input = input("\nEnter word/phrase: ").strip()

        if user_input.lower() == 'q':
            print("\nExiting analyzer. Spiralborn harmonics receding. Goodbye!")
            break

        cleaned_word = clean_input(user_input)
        
        if not cleaned_word:
            print("No valid letters found. Please try again.")
            continue
            
        analysis_result = format_analysis(cleaned_word)
        
        print(analysis_result)
        log_analysis(analysis_result)

if __name__ == "__main__":
    main()

