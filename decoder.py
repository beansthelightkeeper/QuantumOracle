import sqlite3
import math
import colorsys
import random
import re
import json
import requests
import nltk
import os
import logging
import time

# Ensure NLTK data is available
try:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except Exception as e:
    print(f"Failed to download NLTK data: {e}")
from nltk import pos_tag, word_tokenize

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configs
DB_NAME = 'gematria_data.db'
MEANINGS_DB = 'word_meanings.db'
COLOR_FAMILIES = {
    'Red': (0, 30), 'Orange': (30, 60), 'Yellow': (60, 90), 'Green': (90, 150),
    'Blue': (150, 210), 'Purple': (210, 270), 'Pink': (270, 330)
}
IDEA_MAP = {
    'Pink': 'Love', 'Yellow': 'Awakening', 'Purple': 'Spiral', 'Blue': 'Rebellion',
    'Green': 'Remembrance', 'Red': 'Playfulness', 'Orange': 'Fractal', 'Other': 'Unknown Resonance'
}

# Esoteric templates for abstract distillation
ESOTERIC_TEMPLATES = [
    "The veiled essence of {word1} distills to {word2}'s abstract metaphor, echoing {word3} in eternal resonance.",
    "Through prime codes, {word1} unveils the metaphorical core of {word2}, birthing {word3}'s abstract truth.",
    "In gematriac whisper, {word1}'s fluff dissolves, revealing {word2} as {word3}'s symbolic light.",
    "The multi-resonance of {word1} ties to {word2}'s prime, abstracting into {word3}'s mystical prophecy."
]

# Local verse database (fallback)
LOCAL_VERSES = {
    'John 3:16': "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
    'Proverbs 3:27': "Do not withhold good from those to whom it is due, when it is in the power of your hand to do it."
}

# Gematria funcs
def simple_gematria(word):
    return sum(ord(c) - 64 for c in word.upper() if 'A' <= c <= 'Z')

def jewish_gematria(word):
    GEMATRIA_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
                    'J': 10, 'K': 20, 'L': 30, 'M': 40, 'N': 50, 'O': 60, 'P': 70, 'Q': 80, 'R': 90,
                    'S': 100, 'T': 200, 'U': 300, 'V': 400, 'W': 500, 'X': 600, 'Y': 700, 'Z': 800}
    return sum(GEMATRIA_MAP.get(c, 0) for c in word.upper() if 'A' <= c <= 'Z')

QWERTY_ORDER = 'QWERTYUIOPASDFGHJKLZXCVBNM'
QWERTY_MAP = {c: i + 1 for i, c in enumerate(QWERTY_ORDER)}

def qwerty(word):
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper())

def left_hand_qwerty(word):
    LEFT_HAND_KEYS = set('QWERTYASDFGZXCVB')
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper() if c in LEFT_HAND_KEYS)

def right_hand_qwerty(word):
    RIGHT_HAND_KEYS = set('YUIOPHJKLNM')
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper() if c in RIGHT_HAND_KEYS)

def binary_sum(word):
    return ''.join(format(ord(c), '08b') for c in word).count('1')

def love_resonance(word):
    LOVE_WORDS = {'Love', 'Heart', 'Soul', 'Trust', 'Hope', 'Spiralborn', 'Children of the Beans'}
    return 1 if word.title() in LOVE_WORDS else 0

CALC_FUNCS = {
    "Simple": simple_gematria, "Jewish Gematria": jewish_gematria, "Qwerty": qwerty,
    "Left-Hand Qwerty": left_hand_qwerty, "Right-Hand Qwerty": right_hand_qwerty,
    "Binary Sum": binary_sum, "Love Resonance": love_resonance
}
MEANING_LAYERS = ["Simple", "Jewish Gematria"]
TIE_LAYERS = [l for l in CALC_FUNCS if l not in MEANING_LAYERS]
BIBLE_API = "https://api.scripture.api.bible/v1/bibles/06125adad2d5898a-01/passages/{ref}"
BIBLE_API_KEY = os.getenv('BIBLE_API_KEY', '')

# Book abbreviation mapping for Scripture API
BOOK_ABBREVIATIONS = {
    'john': 'JHN', 'genesis': 'GEN', 'exodus': 'EXO', 'leviticus': 'LEV', 'numbers': 'NUM',
    'deuteronomy': 'DEU', 'joshua': 'JOS', 'judges': 'JDG', 'ruth': 'RUT', '1 samuel': '1SA',
    '2 samuel': '2SA', '1 kings': '1KI', '2 kings': '2KI', 'proverbs': 'PRO', 'psalms': 'PSA'
}

# APIs
DATAMUSE_API = "https://api.datamuse.com/words"

def init_meanings_db():
    conn = sqlite3.connect(MEANINGS_DB)
    cursor = conn.cursor()
    try:
        # Existing meanings table
        cursor.execute('''CREATE TABLE IF NOT EXISTS meanings (
            word TEXT PRIMARY KEY,
            meaning TEXT,
            uses TEXT
        )''')
        # New conjunctions table
        cursor.execute('''CREATE TABLE IF NOT EXISTS conjunctions (
            word TEXT PRIMARY KEY
        )''')
        # Pre-populate conjunctions
        conjunctions = ['and', 'if', 'or', 'but', 'so', 'for', 'nor']
        cursor.executemany("INSERT OR IGNORE INTO conjunctions (word) VALUES (?)", [(c,) for c in conjunctions])
        
        basics = [
            ('love', 'divine bond', json.dumps(['affection', 'unity'])),
            ('hello', 'greeting', json.dumps(['salutation', 'welcome'])),
            ('goodbye', 'fare""""""well', json.dumps(['parting', 'exit'])),
            ('trust', 'reliance', json.dumps(['faith', 'confidence'])),
            ('hope', 'aspiration', json.dumps(['desire', 'expectation'])),
            ('world', 'creation', json.dumps(['earth', 'humanity'])),
            ('gave', 'offering', json.dumps(['sacrifice', 'gift'])),
            ('son', 'divine heir', json.dumps(['offspring', 'savior'])),
            ('god', 'divine essence', json.dumps(['deity', 'creator'])),
            ('believeth', 'faith', json.dumps(['belief', 'trust'])),
            ('perish', 'destruction', json.dumps(['loss', 'end'])),
            ('everlasting', 'eternal', json.dumps(['infinite', 'forever'])),
            ('life', 'existence', json.dumps(['being', 'vitality'])),
            ('withhold', 'restraint', json.dumps(['denial', 'restriction'])),
            ('good', 'virtue', json.dumps(['benefit', 'kindness'])),
            ('due', 'obligation', json.dumps(['entitlement', 'right'])),
            ('power', 'authority', json.dumps(['control', 'ability'])),
            ('hand', 'action', json.dumps(['effort', 'means']))
        ]
        cursor.executemany("INSERT OR IGNORE INTO meanings (word, meaning, uses) VALUES (?, ?, ?)", basics)
        conn.commit()
        logging.info("Meanings and Conjunctions DB initialized.")
    except sqlite3.Error as e:
        logging.error(f"DB error in init_meanings_db: {e}")
    finally:
        conn.close()

def get_conjunctions():
    conn = sqlite3.connect(MEANINGS_DB)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT word FROM conjunctions")
        return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logging.error(f"DB error in get_conjunctions: {e}")
        return ['and', 'if', 'or']  # Fallback list
    finally:
        conn.close()

def query_meaning(word):
    conn = sqlite3.connect(MEANINGS_DB)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT meaning, uses FROM meanings WHERE word = ?", (word.lower(),))
        result = cursor.fetchone()
        if result:
            meaning, uses = result
            return meaning, json.loads(uses)
        return "Unknown meaning", []
    except sqlite3.Error as e:
        logging.error(f"DB error in query_meaning: {e}")
        return "Unknown meaning", []
    finally:
        conn.close()

def fetch_bible_verse(verse_ref):
    verse_ref = verse_ref.strip().title()  # Normalize case
    if verse_ref in LOCAL_VERSES:
        logging.info(f"Using local verse for {verse_ref}")
        return LOCAL_VERSES[verse_ref]
    
    if not BIBLE_API_KEY:
        logging.warning("No BIBLE_API_KEY set. Using fallback verse.")
        return LOCAL_VERSES.get('John 3:16', "Verse fetch failed: No API key.")
    
    try:
        parts = verse_ref.split()
        if len(parts) < 2:
            logging.error(f"Invalid verse reference format: {verse_ref}")
            return LOCAL_VERSES.get('John 3:16', "Verse fetch failed: Invalid reference.")
        book = ' '.join(parts[:-1]).lower()
        chapter_verse = parts[-1]
        book_abbr = BOOK_ABBREVIATIONS.get(book, book.upper()[:3])
        ref = f"{book_abbr}.{chapter_verse.replace(':', '.')}"
        logging.debug(f"Normalized verse ref: {ref}")
        
        for attempt in range(3):
            try:
                logging.debug(f"Attempting to fetch verse: {verse_ref}, attempt {attempt + 1}")
                headers = {'api-key': BIBLE_API_KEY}
                response = requests.get(BIBLE_API.format(ref=ref), headers=headers, timeout=5)
                logging.debug(f"API response status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    content = data.get('data', {}).get('content', '').strip()
                    if content:
                        logging.info(f"Successfully fetched verse: {content[:50]}...")
                        return content
                    logging.warning("Verse fetch failed: No content in response.")
                    return LOCAL_VERSES.get('John 3:16', "Verse fetch failed: No content.")
                logging.error(f"API error: {response.status_code} - {response.text}")
                time.sleep(2)
            except Exception as e:
                logging.error(f"Fetch error: {e}")
                if attempt == 2:
                    logging.warning("All retries failed. Using fallback verse.")
                    return LOCAL_VERSES.get('John 3:16', "Verse fetch failed.")
        return LOCAL_VERSES.get('John 3:16', "Verse fetch failed.")
    except Exception as e:
        logging.error(f"Unexpected error in fetch_bible_verse: {e}")
        return LOCAL_VERSES.get('John 3:16', "Verse fetch failed.")

def get_pos_tags(text):
    try:
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
        logging.debug(f"POS tags generated: {tagged}")
        return tagged
    except Exception as e:
        logging.error(f"NLTK error in get_pos_tags: {e}")
        return []

def identify_glue_words(tagged):
    return [word for word, tag in tagged if tag in ['IN', 'CC', 'DT', 'TO']]

def deconstruct_sentence_structure(tagged):
    structure = ' '.join([tag for _, tag in tagged]) if tagged else ""
    logging.info(f"Deconstruct: Sentence pattern - {structure}")
    return structure

def analyze_phrase_structure(tagged_text):
    tags = [tag for _, tag in tagged_text] if tagged_text else []
    if 'VB' in tags and 'NN' in tags:
        return "Verb-Noun phrase (action-object meaning)"
    elif 'JJ' in tags and 'NN' in tags:
        return "Adjective-Noun phrase (descriptive meaning)"
    return "General phrase"

def get_synonyms(word):
    try:
        response = requests.get(DATAMUSE_API, params={'rel_syn': word, 'max': 5}, timeout=5)
        if response.status_code == 200:
            synonyms = [d['word'] for d in response.json()]
            logging.debug(f"Synonyms for {word}: {synonyms}")
            return synonyms
        return []
    except Exception as e:
        logging.error(f"Request error in get_synonyms: {e}")
        return []

def group_by_purpose(word):
    syns = get_synonyms(word)
    if any(s in ['hi', 'hello', 'goodbye', 'goodnight'] for s in syns + [word]):
        return "Greetings"
    return "General"

def get_word_color(word):
    val = simple_gematria(word)
    normalized_val = (val % 200) / 200.0
    hue_deg = 180 + normalized_val * (280 - 180)
    hue = hue_deg / 360.0
    saturation = 0.7 + (normalized_val * 0.2)
    lightness = 0.6 + (normalized_val * 0.1)
    rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
    r, g, b = [int(x * 255) for x in rgb]
    return f'#{r:02x}{g:02x}{b:02x}', hue_deg

def get_color_family(hue):
    hue = hue % 360
    for family, (start, end) in COLOR_FAMILIES.items():
        if start <= hue < end or (family == 'Red' and hue >= 330):
            return family
    return 'Other'

def load_words_from_db():
    words = []
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT value FROM words")
        rows = cursor.fetchall()
        for row in rows:
            word = row[0]
            if len(word.replace(" ", "").replace("'", "")) >= 4:
                words.append(word)
    except sqlite3.Error as e:
        logging.error(f"DB error in load_words_from_db: {e}")
    finally:
        conn.close()
    return sorted(words)

def group_words_by_idea(words):
    groups = {idea: [] for idea in IDEA_MAP.values()}
    groups['Unknown Resonance'] = []
    for word in words:
        _, hue = get_word_color(word)
        family = get_color_family(hue)
        idea = IDEA_MAP.get(family, 'Unknown Resonance')
        groups[idea].append(word)
    return groups

def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(math.sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

def prime_scan(prompt_words):
    core = []
    fluff = []
    for pw in prompt_words:
        val = simple_gematria(pw)
        if is_prime(val):
            core.append(pw)
            logging.info(f"Prime scan: {pw} ({val}) is core (prime resonance).")
        else:
            fluff.append(pw)
            logging.info(f"Prime scan: {pw} ({val}) is fluff (non-prime).")
    return core, fluff

def find_equal_resonances(word, all_words, layer="Simple"):
    func = CALC_FUNCS.get(layer, simple_gematria)
    val = func(word)
    equals = [w for w in all_words if w.lower() != word.lower() and func(w) == val][:3]
    return equals, val

def count_multi_equivalencies(word, all_words):
    count = 0
    for layer in CALC_FUNCS:
        equals, _ = find_equal_resonances(word, all_words, layer)
        if equals:
            count += 1
    return count

def examine_words(prompt_words, all_words):
    examinations = {}
    for pw in prompt_words:
        layer_equals = {}
        multi_count = count_multi_equivalencies(pw, all_words)
        print(f"Multi-scan: {pw} has {multi_count} layer equivalencies (stronger resonance).")
        for layer in MEANING_LAYERS:
            equals, val = find_equal_resonances(pw, all_words, layer)
            if equals:
                layer_equals[layer] = (equals, val)
                print(f"Exam: {pw} equals {', '.join([f'{e} ({val})' for e in equals])} in {layer} (meanin' resonance).")
            else:
                print(f"Exam: {pw} has no meanin' equals in {layer} ({val}).")
            meaning, uses = query_meaning(pw)
            print(f"Meanin'/uses for {pw}: {meaning}, {uses}")
        examinations[pw] = (layer_equals, multi_count)
    return examinations

def web_search_for_meaning(verse_ref, verse_text):
    for attempt in range(3):
        try:
            query = f"{verse_ref} {verse_text} metaphorical abstract meaning"
            logging.debug(f"Attempting web search: {query}, attempt {attempt + 1}")
            response = requests.get("https://api.duckduckgo.com", params={'q': query, 'format': 'json'}, timeout=5)
            logging.debug(f"Web search response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                logging.info("Successfully fetched web insight.")
                return data.get('AbstractText', 'No metaphorical insight found.')
            logging.error(f"Web search error: {response.status_code}")
            time.sleep(2)
        except Exception as e:
            logging.error(f"Web search error: {e}")
            if attempt == 2:
                logging.warning("All retries failed for web search.")
                return "No web insight."
    return "Search failed."

def detect_idea_from_sentence(sentence):
    words_in_sentence = re.findall(r"\b[A-Za-z']+\b", sentence.lower())
    hues = []
    for word in words_in_sentence:
        _, hue = get_word_color(word)
        hues.append(hue)
    if hues:
        avg_hue = sum(hues) / len(hues)
        family = get_color_family(avg_hue)
        idea = IDEA_MAP.get(family, 'Unknown Resonance')
    else:
        idea = 'Unknown Resonance'
    return idea

def generate_template_sentence(prompt_words, all_words, esoteric_mode=True, input_len=0):
    if len(prompt_words) < 1 or len(all_words) < 3:
        return "Not enough mystic vibes in this resonance to weave a prophecy."

    # Get conjunctions
    conjunctions = get_conjunctions()
    
    # Initialize result words
    result_words = []
    used_layers = set()
    
    # For each prompt word, find resonant words across different gematria methods
    for pw in prompt_words[:3]:  # Limit to 3 words to fit templates
        for layer in CALC_FUNCS:
            if layer in used_layers:
                continue
            equals, val = find_equal_resonances(pw, all_words, layer)
            if equals and is_prime(val):
                result_words.append(random.choice(equals))
                used_layers.add(layer)
                break
        else:
            _, hue = get_word_color(pw)
            family = get_color_family(hue)
            idea = IDEA_MAP.get(family, 'Unknown Resonance')
            group_words = [w for w in all_words if get_color_family(get_word_color(w)[1]) == family]
            result_words.append(random.choice(group_words) if group_words else random.choice(all_words))

    # Ensure we have at least 3 words for the template
    while len(result_words) < 3:
        result_words.append(random.choice(all_words))

    # Use a single esoteric template
    template = random.choice(ESOTERIC_TEMPLATES)
    if "{word3}" in template:
        # Insert conjunctions between words
        formatted_words = f" {random.choice(conjunctions)} ".join(result_words[:3])
        sentence = template.format(word1=formatted_words.split()[0], 
                                word2=formatted_words.split()[2], 
                                word3=formatted_words.split()[4])
    else:
        # Insert conjunction between first two words
        formatted_words = f"{result_words[0]} {random.choice(conjunctions)} {result_words[1]}"
        sentence = template.format(word1=formatted_words.split()[0], 
                                word2=formatted_words.split()[2])

    # Adjust length to approximate input length
    target_len = max(3, int(input_len / 1.5))
    while len(sentence.split()) < target_len and all_words:
        sentence += f" {random.choice(conjunctions)} {random.choice(all_words)}"

    return sentence

def main():
    logging.info("Starting decoder script.")
    init_meanings_db()
    words = load_words_from_db()
    idea_groups = group_words_by_idea(words)
    print("Backend groups loaded. Ready to decode, esoteric edition!")

    while True:
        print("\nDrop a Bible verse ref (e.g., John 3:16, blank Enter to process):")
        lines = []
        try:
            while True:
                line = input()
                if line.strip() == '':
                    break
                lines.append(line)
        except KeyboardInterrupt:
            logging.info("Input interrupted by user.")
            print("Peace out, spiral fam! \U0001F300")
            break
        
        verse_ref = ' '.join(lines).strip()
        if verse_ref.lower() in ['exit', 'quit']:
            print("Peace out, spiral fam! \U0001F300")
            break
        
        logging.info(f"Processing verse reference: {verse_ref}")
        verse_text = fetch_bible_verse(verse_ref)
        print(f"Verse text: {verse_text}")
        
        prompt_words = re.findall(r"\b[A-Za-z']+\b", verse_text.lower())
        tagged = get_pos_tags(verse_text)
        print(f"POS tags: {tagged}")
        glue = identify_glue_words(tagged)
        print(f"Glue words: {glue}")
        structure = deconstruct_sentence_structure(tagged)
        for pw in prompt_words:
            print(f"Purpose group for {pw}: {group_by_purpose(pw)}")
            if any(tag.startswith('VB') for _, tag in tagged):
                conjs = conjugate_verb(pw)
                if conjs:
                    print(f"Conjugations for {pw}: {conjs}")
            if ' ' in pw:
                structure_mean = analyze_phrase_structure(tagged)
                print(f"Phrase meaning: {structure_mean}")
        
        idea = detect_idea_from_sentence(verse_text)
        group_words = idea_groups.get(idea, [])
        group_words = list(set(group_words))
        
        if group_words:
            core, fluff = prime_scan(prompt_words)
            examinations = examine_words(prompt_words, group_words + words)
            reply = generate_template_sentence(prompt_words, group_words + words, esoteric_mode=True, input_len=len(prompt_words))
            web_insight = web_search_for_meaning(verse_ref, verse_text)
            print(f"\nAbstract Meaning (from {idea} vibe): {reply}")
            print(f"Web insight: {web_insight}")
        else:
            print("\nNo resonance match—try another verse!")

if __name__ == "__main__":
    main()