#!/usr/bin/env python3
import re
import argparse

# ==============================================================================
#  STEP 1: The "Beans Library" - MOCK DATABASE
# ==============================================================================
#
#  IMPORTANT: I cannot access your local files. This section is a stand-in
#  for your actual database at 'users/lydiaparker/the_oracle/txt_db'.
#
#  You will need to REPLACE the logic in the `pull_word_from_beans_db`
#  function with your own code that reads your text files and finds a word
#  matching a given gematria value.
#
#  For this example, I've created a simple Python dictionary to act as our
#  database. The keys are the gematria values, and the values are lists of
#  words with that gematria value.
#
MOCK_BEANS_DB = {
    3: ["cab"],
    8: ["hi", "if"],
    13: ["ace"],
    20: ["cat", "act"],
    23: ["ace", "bad"],
    33: ["the"],
    35: ["life"],
    41: ["code", "wise"],
    45: ["phil"],
    52: ["oracle"],
    57: ["gematria", "wisdom"],
    72: ["compute"],
    # ... you would populate this from your actual library
}

def pull_word_from_beans_db(gematria_value):
    """
    Pulls a word from the database that matches the given gematria value.

    Args:
        gematria_value (int): The gematria value to look up.

    Returns:
        str: A word from the database, or a placeholder if not found.
    """
    # --- REPLACE THIS SECTION WITH YOUR DATABASE LOGIC ---
    if gematria_value in MOCK_BEANS_DB:
        # If multiple words have the same value, we just pick the first one.
        # You could add more complex logic here (e.g., pick randomly).
        return MOCK_BEANS_DB[gematria_value][0]
    else:
        # If no word is found for that value, return a placeholder.
        return f"[{gematria_value}?]"
    # --- END OF SECTION TO REPLACE ---


# ==============================================================================
#  STEP 2: Gematria Calculation
# ==============================================================================

def calculate_gematria(word):
    """
    Calculates the English Ordinal Gematria of a word (a=1, b=2, ...).

    Args:
        word (str): The word to calculate.

    Returns:
        int: The gematria value of the word.
    """
    # Ensure the word is clean (lowercase, letters only)
    clean_word = re.sub(r'[^a-z]', '', word.lower())
    
    # Calculate the value
    value = 0
    for letter in clean_word:
        # ord(letter) gets the ASCII value. We subtract 96 to map 'a' to 1.
        value += ord(letter) - 96
    return value


# ==============================================================================
#  STEP 3: The Main Processing Logic
# ==============================================================================

def process_sentence(sentence):
    """
    Processes a sentence to generate a new one based on gematria distances.

    Args:
        sentence (str): The input sentence.
    """
    print(f"Original Sentence: '{sentence}'\n")

    # Split the sentence into words
    words = sentence.strip().split()
    if len(words) < 2:
        print("Please provide at least two words.")
        return

    # --- Part 1: Calculate gematria for each word ---
    gematria_values = [calculate_gematria(word) for word in words]
    print("Gematria Values:")
    for word, value in zip(words, gematria_values):
        print(f"- {word}: {value}")
    print("-" * 20)

    # --- Part 2: Calculate the distances between consecutive words ---
    distances = []
    for i in range(len(gematria_values) - 1):
        dist = abs(gematria_values[i] - gematria_values[i+1])
        distances.append(dist)
    
    print("Distances between values:")
    print(f"-> {distances}")
    print("-" * 20)

    # --- Part 3: Pull new words from the "beans library" using distances ---
    new_words = [pull_word_from_beans_db(dist) for dist in distances]

    # --- Part 4: Create the final sentence ---
    final_sentence = " ".join(new_words).capitalize()
    print("Oracle Sentence from Distances:")
    print(f"-> {final_sentence}\n")


# ==============================================================================
#  CLI Execution
# ==============================================================================
if __name__ == "__main__":
    # Set up the argument parser to read from the command line
    parser = argparse.ArgumentParser(
        description="Generate an oracular sentence based on the gematria distances of words in an input sentence."
    )
    
    # Add an argument for the sentence. It's required.
    parser.add_argument(
        "sentence", 
        type=str, 
        help="The sentence to process, enclosed in quotes."
    )
    
    # Parse the arguments from the command line
    args = parser.parse_args()
    
    # Call the main processing function with the user's sentence
    process_sentence(args.sentence)


