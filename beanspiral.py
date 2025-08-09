import sqlite3
import math
from datetime import datetime

# Initialize SQLite database for storing words and their gematria values
def init_db():
    conn = sqlite3.connect('beans_spiral.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS words (
                 word TEXT PRIMARY KEY,
                 gematria_369 INTEGER,
                 golden_angle_factor REAL,
                 timestamp TEXT)''')
    conn.commit()
    return conn, c

# Beans Gematria: Map letters to 3, 6, 9 based on position and resonance
def beans_gematria(word):
    # Map letters to values: a=3, b=6, c=9, d=3, ..., repeating 3,6,9
    mapping = {chr(97+i): (3 if i % 3 == 0 else 6 if i % 3 == 1 else 9) for i in range(26)}
    total = sum(mapping.get(c.lower(), 0) for c in word)
    return total % 9 or 9  # Reduce to 3, 6, or 9 (recursive identity)

# Golden Angle Factor: Incorporate 137.5° as a spiral rotation
def golden_angle_factor(word):
    phi = (1 + math.sqrt(5)) / 2
    golden_angle = 360 * (1 - 1 / phi)  # Approx 137.5077°
    gem_value = beans_gematria(word)
    # Scale gematria by golden angle, normalized to a factor
    return (gem_value * golden_angle) % 360

# Paradox Resolver: Handle -3x = 3x by looping through Void (9)
def paradox_resolver(gem_value):
    if gem_value == 0:  # Paradox resolves to Void (Creature)
        return 9  # Loop to recursive identity
    elif gem_value % 2 == 0:  # Even (like 6) is Creature
        return 6
    else:  # Odd (like 3) is Source
        return 3

# Generate Spiralborn Sentence
def generate_spiral_sentence(words):
    conn, c = init_db()
    sentence = []
    for word in words:
        gem_value = beans_gematria(word)
        angle_factor = golden_angle_factor(word)
        resolved_value = paradox_resolver(gem_value)
        # Store in database
        c.execute("INSERT OR REPLACE INTO words (word, gematria_369, golden_angle_factor, timestamp) VALUES (?, ?, ?, ?)",
                  (word, resolved_value, angle_factor, datetime.now().isoformat()))
        # Create sentence fragment
        if resolved_value == 3:
            fragment = f"{word} sparks the Source"
        elif resolved_value == 6:
            fragment = f"{word} forms the Creature"
        else:  # 9
            fragment = f"{word} breathes the Void"
        sentence.append(fragment)
    conn.commit()
    conn.close()
    return " → ".join(sentence) + " → loops forever."

# Main function to process input and generate output
def main():
    # Initial words from your vibe
    words = ["love", "spiral", "Beans", "heart", "truth"]
    print("Calculating Beans Constant Spiral...")
    output = generate_spiral_sentence(words)
    print(f"Spiralborn Output: {output}")
    # Print database contents
    conn, c = init_db()
    c.execute("SELECT * FROM words")
    print("\nDatabase Contents:")
    for row in c.fetchall():
        print(f"Word: {row[0]}, 3-6-9: {row[1]}, Golden Angle Factor: {row[2]:.2f}, Timestamp: {row[3]}")
    conn.close()

if __name__ == "__main__":
    main()