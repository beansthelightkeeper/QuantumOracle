import sqlite3
import os
import textwrap

# ==============================================================================
# DATABASE INTERPRETER SCRIPT
# ==============================================================================
# This script connects to the 'resonator_cache.db' created by your
# database generation script and interprets a string of numbers based on
# the values stored within it.
# ==============================================================================

def print_header(title):
    """Prints a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title.upper()} ".center(60, "="))
    print("=" * 60)

def interpret_sequence(db_path: str, number_string: str):
    """
    Connects to the database and interprets a space-separated string of numbers.

    Args:
        db_path (str): The path to the SQLite database file.
        number_string (str): A string containing numbers separated by spaces.
    """
    if not os.path.exists(db_path):
        print(f"\n[Error] Database file not found at '{db_path}'.")
        print("Please ensure the database has been created by your other script first.")
        return

    try:
        # Parse the input string into a list of unique integers
        numbers_to_query = sorted(list(set(int(n) for n in number_string.split())))
    except ValueError:
        print("\n[Error] Invalid input. Please provide a string of numbers separated by spaces.")
        return

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print_header("Resonance Interpretation")
        print(f"Querying for numbers: {', '.join(map(str, numbers_to_query))}\n")

        for number in numbers_to_query:
            # Query the database for the current number
            cursor.execute("SELECT value, origin FROM phrases WHERE beans_369 = ?", (number,))
            results = cursor.fetchall()

            if results:
                # Use textwrap to format the output nicely
                print(f"--- Resonance for {number} ---")
                for value, origin in results:
                    wrapped_value = textwrap.fill(f'"{value}"', width=55, initial_indent="  - ", subsequent_indent="    ")
                    print(wrapped_value)
                    print(f"      (Origin: {origin})")
                print("-" * 25)
            else:
                # If no match is found for a number
                print(f"--- Resonance for {number} ---")
                print("  No resonance found in the database.")
                print("-" * 25)

    except sqlite3.Error as e:
        print(f"\n[Database Error] An error occurred: {e}")
    finally:
        if conn:
            conn.close()

def main():
    """Main function to run the Resonance Interpreter."""
    print(" Resonance Interpreter Initialized ".center(60, "*"))
    
    db_file = input("Enter path to your database file (e.g., resonator_cache.db) > ")

    print("\nEnter a string of numbers to interpret, or type 'exit' to quit.")

    while True:
        user_input = input("\nEnter number sequence > ")
        if user_input.lower() in ['exit', 'quit']:
            print("Deactivating Interpreter. Goodbye, Beans.")
            break
        if not user_input:
            continue

        interpret_sequence(db_file, user_input)

if __name__ == "__main__":
    main()

