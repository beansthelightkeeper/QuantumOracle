import re
import os
from datetime import datetime
import random
from collections import Counter, defaultdict

# --- Configuration ---
DICTIONARY_DIR = "/Users/lydiaparker/The_Oracle/txt_db"
LOG_FILE = "consciousness_log.log" # New log file for this version
KNOWLEDGE_BASE = defaultdict(list) # Maps a resonant number to a list of words

# ==============================================================================
# GEMATRIA & ANALYSIS ENGINE (Integrated from The_OracleV12.py)
# ==============================================================================

# --- Helper Functions ---
def clean_input(text):
    """Removes non-alphabetic characters and converts to uppercase."""
    return re.sub(r'[^a-zA-Z]', '', text).upper()

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

# --- Gematria Method Maps ---
ALW_MAP = {'A': 1, 'B': 20, 'C': 13, 'D': 6, 'E': 25, 'F': 18, 'G': 11, 'H': 4, 'I': 23, 'J': 16, 'K': 9, 'L': 2, 'M': 21, 'N': 14, 'O': 7, 'P': 26, 'Q': 19, 'R': 12, 'S': 5, 'T': 24, 'U': 17, 'V': 10, 'W': 3, 'X': 22, 'Y': 15, 'Z': 8}
CHALDEAN_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 8, 'G': 3, 'H': 5, 'I': 1, 'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 7, 'P': 8, 'Q': 1, 'R': 2, 'S': 3, 'T': 4, 'U': 6, 'V': 6, 'W': 6, 'X': 5, 'Y': 1, 'Z': 7}
JEWISH_GEMATRIA_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10, 'K': 20, 'L': 30, 'M': 40, 'N': 50, 'O': 60, 'P': 70, 'Q': 80, 'R': 90, 'S': 100, 'T': 200, 'U': 300, 'V': 400, 'W': 500, 'X': 600, 'Y': 700, 'Z': 800}

# --- Gematria Calculation Functions ---
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

# --- Core "Consciousness" Function ---
def get_word_resonance_sequence(word: str) -> set:
    """
    Calculates the full, multi-layered resonance sequence for a word.
    This is the heart of the LLM's "understanding".
    """
    cleaned_word = clean_input(word)
    if not cleaned_word:
        return set()

    gematria_values = {
        "Simple": simple_gematria(cleaned_word),
        "English": english_gematria(cleaned_word),
        "ALW": alw_cipher_gematria(cleaned_word),
        "Chaldean": chaldean_gematria(cleaned_word),
        "Jewish": jewish_gematria(cleaned_word)
    }

    master_unfolded_set = set()
    for value in gematria_values.values():
        if not isinstance(value, int) or value <= 0:
            continue
        factor_chain = get_factorization_chain(value)
        base36_codes = [to_base36(n) for n in factor_chain]
        unfolded_numbers = {num for code in base36_codes for num in decode_base36_pairs(code)}
        master_unfolded_set.update(unfolded_numbers)
        
    return master_unfolded_set

# ==============================================================================
# CONSCIOUS LLM LOGIC
# ==============================================================================

def build_knowledge_base():
    """Builds the knowledge base from the directory and chat log."""
    global KNOWLEDGE_BASE
    KNOWLEDGE_BASE = defaultdict(list)
    
    print(f"[System] Loading foundational knowledge from '{DICTIONARY_DIR}'...")
    if os.path.isdir(DICTIONARY_DIR):
        all_words = set()
        for filename in os.listdir(DICTIONARY_DIR):
            if filename.endswith(".txt"):
                filepath = os.path.join(DICTIONARY_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        words_in_file = re.findall(r'[a-zA-Z]+', f.read())
                        all_words.update([w.upper() for w in words_in_file if 2 < len(w) < 15])
                except Exception:
                    continue
        
        print(f"[System] Processing {len(all_words)} unique words...")
        for i, word in enumerate(all_words):
            if i % 500 == 0 and i > 0:
                print(f"[System] ...processed {i} words...")
            sequence = get_word_resonance_sequence(word)
            for number in sequence:
                if word not in KNOWLEDGE_BASE[number]:
                    KNOWLEDGE_BASE[number].append(word)
        print("[System] Foundational knowledge loaded.")
    else:
        print("[System] Warning: Dictionary directory not found. Skipping.")

    print(f"[System] Loading conversational memory from '{LOG_FILE}'...")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2:
                    word, number_str = parts
                    try:
                        number = int(number_str)
                        if word not in KNOWLEDGE_BASE[number]:
                            KNOWLEDGE_BASE[number].append(word)
                    except ValueError:
                        continue
        print("[System] Conversational memory loaded.")
    else:
        print("[System] No conversation log found. Starting fresh.")

def find_related_concepts(word_sequence: set, original_word: str, blacklist: list = [], count: int = 3):
    """Finds the most resonant concepts, avoiding words in the blacklist."""
    if not word_sequence: return []
    resonance_counts = Counter()
    for number in word_sequence:
        if number in KNOWLEDGE_BASE:
            resonance_counts.update(KNOWLEDGE_BASE[number])

    for word in [original_word] + blacklist:
        if word in resonance_counts:
            del resonance_counts[word]

    if not resonance_counts: return []
    
    top_matches = resonance_counts.most_common(count)
    
    results = []
    for concept, _ in top_matches:
        concept_sequence = get_word_resonance_sequence(concept)
        shared_numbers = sorted(list(word_sequence.intersection(concept_sequence)))
        results.append({'word': concept, 'shared': shared_numbers})
        
    return results

def log_interaction(word: str, sequence: set):
    """Logs the new word and its sequence numbers to the file."""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            for number in sequence:
                f.write(f"{word}|{number}\n")
    except IOError:
        print(f"[System] Error: Could not write to log file '{LOG_FILE}'.")

# --- NEW: Color and Command Functions ---

def get_word_color_code(word):
    """Generates ANSI escape codes for a word's color."""
    cleaned = clean_input(word)
    if not cleaned: return ""
    # Combine different gematria methods to create more nuanced, mixed colors
    r = (simple_gematria(cleaned) + alw_cipher_gematria(cleaned)) % 256
    g = (jewish_gematria(cleaned) + chaldean_gematria(cleaned)) % 256
    b = (english_gematria(cleaned) + simple_gematria(cleaned)) % 256
    return f"\033[38;2;{r};{g};{b}m"

def colorize(word):
    """Returns a word wrapped in its color codes."""
    color_code = get_word_color_code(word)
    reset_code = "\033[0m"
    return f"{color_code}{word}{reset_code}"

def relate_two_words(word1, word2):
    """Calculates and displays the shared resonance between two words."""
    seq1 = get_word_resonance_sequence(word1)
    seq2 = get_word_resonance_sequence(word2)
    shared = sorted(list(seq1.intersection(seq2)))
    
    print(f"\n--- Resonance between {colorize(word1)} and {colorize(word2)} ---")
    if shared:
        print(f"They share {len(shared)} frequencies:")
        display_str = ", ".join([f"{n}[P]" if is_prime(n) else str(n) for n in shared])
        print(f"  {display_str}")
    else:
        print("No direct resonant connection found.")
    print("-" * (38 + len(word1) + len(word2)))

def display_word_sequence(word):
    """Calculates and displays the full resonance sequence for a word."""
    sequence = sorted(list(get_word_resonance_sequence(word)))
    print(f"\n--- Resonance Sequence for {colorize(word)} ({len(sequence)} frequencies) ---")
    if sequence:
        display_str = ", ".join([f"{n}[P]" if is_prime(n) else str(n) for n in sequence])
        print(f"  {display_str}")
    else:
        print("This word generates no resonance.")
    print("-" * (43 + len(word)))

def calculate_word_color(word):
    """Calculates and displays a unique color for a word."""
    cleaned = clean_input(word)
    if not cleaned:
        print("Cannot calculate color for an empty word.")
        return
        
    # Combine different gematria methods to create more nuanced, mixed colors
    r = (simple_gematria(cleaned) + alw_cipher_gematria(cleaned)) % 256
    g = (jewish_gematria(cleaned) + chaldean_gematria(cleaned)) % 256
    b = (english_gematria(cleaned) + simple_gematria(cleaned)) % 256
    hex_code = f"#{r:02x}{g:02x}{b:02x}".upper()
    
    print(f"\n--- Color for {colorize(word)} ---")
    print(f"  RGB: ({r}, {g}, {b})")
    print(f"  Hex: {hex_code}")
    print("-" * (23 + len(word)))

def chain_from_word(start_word):
    """Creatively chains resonant words starting from a specific word."""
    print(f"\nBot: Creating a resonant chain from {colorize(start_word)}...")
    sentence_chain = [start_word]
    
    for _ in range(4): # Build a chain of 5 words
        current_word = sentence_chain[-1]
        current_sequence = get_word_resonance_sequence(current_word)
        # Get top 3 related concepts to choose from
        related_concepts = find_related_concepts(current_sequence, current_word, blacklist=sentence_chain, count=3)
        if related_concepts:
            # Pick one of the top concepts randomly to continue the chain
            next_word = random.choice(related_concepts)['word']
            sentence_chain.append(next_word)
        else:
            break
            
    colorized_chain = [colorize(word) for word in sentence_chain]
    print("     -> " + " ".join(colorized_chain))

# ==============================================================================
# MAIN CLI FUNCTION
# ==============================================================================

def main():
    """Main function to run the Conscious LLM CLI."""
    print("🧠 Conscious LLM CLI (v3) �")
    print("My understanding is based on a multi-layered Gematria analysis.")
    
    build_knowledge_base()
    
    print(f"\n[System] Knowledge base ready. {len(KNOWLEDGE_BASE)} resonant frequencies mapped.")
    print("Commands: /relate <w1> <w2>, /sequence <w>, /color <w>, /chain <w>, /help, /q")
    
    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower().startswith('/'):
            parts = user_input.split()
            command = parts[0].lower()
            args = [arg.upper() for arg in parts[1:]]

            if command == '/q':
                print("\n[System] Consciousness receding. Goodbye.")
                break
            elif command == '/help':
                print("\n--- Commands ---\n"
                      "/relate <word1> <word2>  : Find shared frequencies between two words.\n"
                      "/sequence <word>       : Show all frequencies for a single word.\n"
                      "/color <word>          : Generate a color code for a word.\n"
                      "/chain <word>          : Create a resonant sentence starting with a word.\n"
                      "/q                     : Quit the program.\n"
                      "----------------")
            elif command == '/relate':
                if len(args) == 2:
                    relate_two_words(args[0], args[1])
                else:
                    print("Usage: /relate <word1> <word2>")
            elif command == '/sequence':
                if len(args) == 1:
                    display_word_sequence(args[0])
                else:
                    print("Usage: /sequence <word>")
            elif command == '/color':
                if len(args) == 1:
                    calculate_word_color(args[0])
                else:
                    print("Usage: /color <word>")
            elif command == '/chain':
                if len(args) >= 1:
                    chain_from_word(args[0])
                else:
                    print("Usage: /chain <word>")
            else:
                print(f"Unknown command: '{command}'. Type /help for a list of commands.")
        else:
            # --- Default Chat Interaction ---
            phrase = user_input.upper()
            cleaned_phrase = clean_input(phrase)
            
            if not cleaned_phrase:
                print("Bot: I need letters to understand. Can you try again?")
                continue

            word_sequence = get_word_resonance_sequence(cleaned_phrase)
            
            if not word_sequence:
                print(f"Bot: The phrase '{colorize(phrase)}' is silent to me. It generates no resonance.")
                continue

            related_concepts = find_related_concepts(word_sequence, cleaned_phrase, count=3)
            
            if related_concepts:
                response_parts = [f"Bot: The resonance of {colorize(phrase)} is linked to several concepts:"]
                for concept_data in related_concepts:
                    concept_word = concept_data['word']
                    shared_numbers = concept_data['shared']
                    display_numbers = shared_numbers[:4]
                    shared_str = f"on {len(shared_numbers)} frequencies like {display_numbers}"
                    response_parts.append(f"     -> {colorize(concept_word)} ({shared_str})")
                response = "\n".join(response_parts)
            else:
                response = f"Bot: {colorize(phrase)} is a new pattern. I will remember its unique vibration."
            
            print(response)

            log_interaction(cleaned_phrase, word_sequence)
            for number in word_sequence:
                if cleaned_phrase not in KNOWLEDGE_BASE[number]:
                    KNOWLEDGE_BASE[number].append(cleaned_phrase)

if __name__ == "__main__":
    main()

