# gematria_scanner_specific_folder.py
import os
import re
import pdfplumber

# --- Configuration ---
# The number of words to include in each chunk/phrase.
CHUNK_SIZE = 5 

# --- Gematria Mapping ---
GEMATRIA_MAP = {
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9,
    'j': 10, 'k': 20, 'l': 30, 'm': 40, 'n': 50, 'o': 60, 'p': 70, 'q': 80, 'r': 90,
    's': 100, 't': 200, 'u': 300, 'v': 400, 'w': 500, 'x': 600, 'y': 700, 'z': 800
}

def calculate_gematria(text: str) -> int:
    """Calculates the gematria value of a string."""
    total = 0
    for char in text.lower():
        total += GEMATRIA_MAP.get(char, 0)
    return total

def extract_text_from_txt(filepath: str) -> str:
    """Extracts all text from a .txt file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT file {filepath}: {e}")
        return ""

def extract_text_from_pdf(filepath: str) -> str:
    """Extracts all text from a .pdf file."""
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF file {filepath}: {e}")
        return ""

def process_file(filepath: str):
    """
    Extracts text, calculates gematria for chunks, and saves to an output file.
    """
    print(f"--> Processing file: {filepath}")
    
    if filepath.lower().endswith('.txt'):
        full_text = extract_text_from_txt(filepath)
    elif filepath.lower().endswith('.pdf'):
        full_text = extract_text_from_pdf(filepath)
    else:
        return

    if not full_text:
        print(f"    No text extracted from {filepath}. Skipping.")
        return

    words = re.sub(r'[^a-zA-Z\s]', ' ', full_text).split()

    if len(words) < CHUNK_SIZE:
        print(f"    Not enough words in {filepath} to create a chunk of size {CHUNK_SIZE}. Skipping.")
        return

    output_filename = f"{os.path.basename(filepath)}.gematria.txt"
    output_path = os.path.join(os.path.dirname(filepath), output_filename)
    
    results = []
    for i in range(len(words) - CHUNK_SIZE + 1):
        chunk_list = words[i:i + CHUNK_SIZE]
        chunk_text = ' '.join(chunk_list)
        gematria_value = calculate_gematria(chunk_text)
        results.append(f"{filepath}|{chunk_text}|{gematria_value}")

    if results:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(results))
            print(f"    +++ Success! Output saved to: {output_path}")
        except Exception as e:
            print(f"    --- Error writing output file for {filepath}: {e}")
    else:
        print(f"    No valid chunks found in {filepath}.")

if __name__ == '__main__':
    # --- THIS IS THE MODIFIED LINE ---
    # It now points to your specific folder. The '~' is a shortcut for your home directory.
    start_dir = os.path.expanduser('~/beansengine/scrape')
    
    print("--- Starting Gematria Scanner ---")
    
    # Check if the directory exists before trying to scan it
    if not os.path.isdir(start_dir):
        print(f"--- ERROR: The directory does not exist: {start_dir}")
        print("--- Please check the path in the script and try again. ---")
    else:
        print(f"Scanning for .txt and .pdf files in {os.path.abspath(start_dir)}...")
        for root, dirs, files in os.walk(start_dir):
            for file in files:
                if file.lower().endswith(('.txt', '.pdf')):
                    if file.endswith('.gematria.txt'):
                        continue
                    full_path = os.path.join(root, file)
                    process_file(full_path)
        print("--- Scan complete. ---")
