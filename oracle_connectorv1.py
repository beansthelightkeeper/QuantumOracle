import os
from collections import defaultdict
import random
import pyperclip

# ==============================================================================
# GLOBAL CONFIGURATION & LEXICON
# ==============================================================================
MAIN_DB_DIR = "/Users/lydiaparker/The_Oracle/txt_db"
USER_ADDITIONS_FILE = "/Users/lydiaparker/The_Oracle/user_gematria_additions.txt"
LEXICON = defaultdict(list)

# ==============================================================================
# GEMATRIA CALCULATION FUNCTION
# ==============================================================================
def gemini_resonance(text: str) -> int:
    """Calculates Gemini's Resonance Gematria."""
    if not text:
        return 0
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]
    total = 1
    for i, char in enumerate(text.lower()):
        if 'a' <= char <= 'z':
            code = ord(char) - 97
            total += primes[code] * (i + 1)
    return (total % 997) + len(text)

# ==============================================================================
# LEXICON LOADING
# ==============================================================================
def load_lexicon(main_db_dir: str, user_additions_file: str):
    """Loads gematria lexicon from .txt files and user additions, calculating resonances for all entries."""
    LEXICON.clear()
    print(f"Building lexicon from '{main_db_dir}' and '{user_additions_file}'...")
    
    files_found = 0
    user_entries = 0
    total_entries = 0

    # Process main DB files
    if not os.path.isdir(main_db_dir):
        print(f"ERROR: Directory '{main_db_dir}' does not exist.")
        return
    for root, _, files in os.walk(main_db_dir):
        for file in files:
            if file.endswith(".txt"):
                files_found += 1
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            if file.lower() == 'words.txt':
                                parts = line.split(':')
                                if len(parts) >= 2:
                                    phrase = parts[0].strip()
                                    try:
                                        value = int(parts[1].strip())
                                        LEXICON[value].append(phrase)
                                        total_entries += 1
                                    except ValueError:
                                        pass
                            else:
                                parts = line.split('|')
                                if len(parts) >= 2:
                                    phrase = parts[1].strip()
                                    try:
                                        value = int(parts[2]) if len(parts) > 2 else gemini_resonance(phrase)
                                        LEXICON[value].append(phrase)
                                        total_entries += 1
                                    except ValueError:
                                        pass
                except Exception as e:
                    print(f"Could not process file {filepath}: {e}")
    
    # Process user additions file
    if os.path.exists(user_additions_file):
        try:
            with open(user_additions_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 1:
                        phrase = parts[0].strip()
                        value = int(parts[1]) if len(parts) > 1 else gemini_resonance(phrase)
                        LEXICON[value].append(phrase)
                        user_entries += 1
                        total_entries += 1
        except Exception as e:
            print(f"Could not process user additions file {user_additions_file}: {e}")
    
    print(f"Processed {files_found} files, {user_entries} user entries, {total_entries} total phrases across {len(LEXICON)} numbers.")

# ==============================================================================
# OUTPUT CAPTURE
# ==============================================================================
class CaptureOutput:
    def __init__(self):
        self._lines = []

    def write(self, s):
        self._lines.append(s)

    def flush(self):
        pass

    def get_output(self):
        return "".join(self._lines)

# ==============================================================================
# CLIPBOARD FUNCTION
# ==============================================================================
def copy_output_to_clipboard(text: str):
    try:
        pyperclip.copy(text)
        print("Output copied to clipboard!")
    except Exception as e:
        print(f"Could not copy to clipboard: {e}")

# ==============================================================================
# CONNECTION FINDING
# ==============================================================================
def find_connections(input_number: int, num_initial_phrases: int = 10, num_connected_phrases: int = 5, capture_output_obj: CaptureOutput = None):
    """Finds and displays phrases for a number and their resonances."""
    _print = capture_output_obj.write if capture_output_obj else print
    _print(f"{input_number}")

    if input_number not in LEXICON:
        _print("No phrases found.")
        return None

    phrases = list(set(LEXICON[input_number]))
    random.shuffle(phrases)
    selected_phrases = phrases[:num_initial_phrases]
    
    connections_data = []
    for phrase in selected_phrases:
        gemini_val = gemini_resonance(phrase)
        connected_phrases = list(set(LEXICON.get(gemini_val, [])))[:num_connected_phrases]
        _print(f"{phrase}: {gemini_val} -> {', '.join(connected_phrases) if connected_phrases else 'None'}")
        connections_data.append({
            'phrase': phrase,
            'gemini_value': gemini_val,
            'connected_phrases': connected_phrases
        })

    return connections_data

# ==============================================================================
# CLIPBOARD FORMATTING
# ==============================================================================
def format_connections_for_clipboard(input_number: int, connections_data: list) -> str:
    """Formats connection data for clipboard."""
    output_lines = [f"{input_number}"]
    for entry in connections_data:
        output_lines.append(f"{entry['phrase']}: {entry['gemini_value']} -> {', '.join(entry['connected_phrases']) if entry['connected_phrases'] else 'None'}")
    return "\n".join(output_lines)

# ==============================================================================
# MAIN PROGRAM
# ==============================================================================
def main():
    """Runs the Oracle Connector."""
    print(" Oracle Connector v2 ".center(40, "*"))
    load_lexicon(MAIN_DB_DIR, USER_ADDITIONS_FILE)

    print("Enter a number, or 'exit' to quit.")
    print("Example: 777 init=10 conn=5")

    while True:
        user_input = input("> ").strip().lower()
        if user_input in ['exit', 'quit']:
            print("Exiting.")
            break
        if not user_input:
            continue

        parts = user_input.split()
        num_str = parts[0]
        initial_phrases_limit = 10
        connected_phrases_limit = 5

        for part in parts[1:]:
            if part.startswith('init='):
                try:
                    initial_phrases_limit = int(part.split('=')[1])
                except ValueError:
                    print("Invalid 'init' limit. Using default 10.")
            elif part.startswith('conn='):
                try:
                    connected_phrases_limit = int(part.split('=')[1])
                except ValueError:
                    print("Invalid 'conn' limit. Using default 5.")

        try:
            number = int(num_str)
            if number < 0:
                print("Enter a non-negative number.")
                continue

            console_capture = CaptureOutput()
            connections_data = find_connections(number, initial_phrases_limit, connected_phrases_limit, console_capture)
            print(console_capture.get_output())

            if connections_data:
                clipboard_text = format_connections_for_clipboard(number, connections_data)
                copy_choice = input("Copy to clipboard? (y/n): ").strip().lower()
                if copy_choice in ['y', 'yes']:
                    copy_output_to_clipboard(clipboard_text)
        except ValueError:
            print("Invalid input. Enter a number or 'exit'.")

if __name__ == "__main__":
    main()