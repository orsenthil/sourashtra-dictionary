#!/usr/bin/env python3
"""
Convert Sourashtra Dictionary to Dictpress Format
This tool converts the 9-field Sourashtra dictionary CSV files to the 11-field dictpress format.

Usage: python3 convert_to_dictpress.py [--input-dir INPUT_DIR] [--output-dir OUTPUT_DIR] [--dry-run]
"""

import argparse
import csv
import json
import os
import re
import sys
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import unicodedata

try:
    import nltk
    from nltk.corpus import wordnet
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("Warning: NLTK not available. Some enhancement features will be limited.")

# Definition type mappings
DEFINITION_TYPES = {
    'abbr': "Abbreviation",
    'adj': "Adjective", 
    'adv': "Adverb",
    'auxv': "Auxiliary verb",
    'conj': "Conjugation",
    'idm': "Idiom",
    'interj': "Interjection",
    'noun': "Noun",
    'pfx': "Prefix",
    'ph': "Phrase",
    'phrv': "Phrasal verb",
    'prep': "Preposition",
    'pron': "Pronoun",
    'propn': "Proper Noun",
    'sfx': "Suffix",
    'verb': "Verb"
}

# Category mappings based on file names
CATEGORY_MAPPINGS = {
    'adjectives': {'type': 'adj', 'tags': 'descriptive|quality', 'category': 'adjective'},
    'adverbs': {'type': 'adv', 'tags': 'manner|degree', 'category': 'adverb'},
    'age-and-growth-stages': {'type': 'noun', 'tags': 'time|period|stage|life', 'category': 'noun'},
    'animals': {'type': 'noun', 'tags': 'animal|creature|living', 'category': 'noun'},
    'birds': {'type': 'noun', 'tags': 'bird|animal|flying', 'category': 'noun'},
    'body-parts': {'type': 'noun', 'tags': 'anatomy|body|physical', 'category': 'noun'},
    'ceremonies': {'type': 'noun', 'tags': 'ritual|ceremony|religious', 'category': 'noun'},
    'colors': {'type': 'adj', 'tags': 'color|visual|appearance', 'category': 'adjective'},
    'compound-verbs': {'type': 'verb', 'tags': 'action|compound', 'category': 'verb'},
    'concepts': {'type': 'noun', 'tags': 'abstract|concept|idea', 'category': 'noun'},
    'creatures-and-insects': {'type': 'noun', 'tags': 'creature|insect|small|animal', 'category': 'noun'},
    'defective-verbs': {'type': 'verb', 'tags': 'action|irregular', 'category': 'verb'},
    'directions': {'type': 'noun', 'tags': 'direction|spatial|location', 'category': 'noun'},
    'dress-and-ornaments': {'type': 'noun', 'tags': 'clothing|ornament|decoration', 'category': 'noun'},
    'earth-and-related-words': {'type': 'noun', 'tags': 'earth|nature|geography', 'category': 'noun'},
    'education': {'type': 'noun', 'tags': 'education|learning|knowledge', 'category': 'noun'},
    'festivals': {'type': 'noun', 'tags': 'festival|celebration|cultural', 'category': 'noun'},
    'food': {'type': 'noun', 'tags': 'food|nourishment|eating', 'category': 'noun'},
    'fruits': {'type': 'noun', 'tags': 'fruit|food|plant', 'category': 'noun'},
    'function-verbs': {'type': 'verb', 'tags': 'action|function|activity', 'category': 'verb'},
    'games': {'type': 'noun', 'tags': 'game|play|entertainment', 'category': 'noun'},
    'grammar': {'type': 'noun', 'tags': 'grammar|language|linguistic', 'category': 'noun'},
    'health': {'type': 'noun', 'tags': 'health|medical|wellness', 'category': 'noun'},
    'house-articles': {'type': 'noun', 'tags': 'household|object|domestic', 'category': 'noun'},
    'house-parts': {'type': 'noun', 'tags': 'house|building|structure', 'category': 'noun'},
    'interrogative-words': {'type': 'pron', 'tags': 'question|interrogative', 'category': 'pronoun'},
    'kinship': {'type': 'noun', 'tags': 'family|relationship|social', 'category': 'noun'},
    'kitchen': {'type': 'noun', 'tags': 'kitchen|cooking|food', 'category': 'noun'},
    'law-and-order': {'type': 'noun', 'tags': 'law|legal|order', 'category': 'noun'},
    'literature': {'type': 'noun', 'tags': 'literature|writing|cultural', 'category': 'noun'},
    'measurements': {'type': 'noun', 'tags': 'measurement|quantity|size', 'category': 'noun'},
    'metals': {'type': 'noun', 'tags': 'metal|material|substance', 'category': 'noun'},
    'months': {'type': 'noun', 'tags': 'time|month|calendar', 'category': 'noun'},
    'music': {'type': 'noun', 'tags': 'music|art|cultural', 'category': 'noun'},
    'numerals': {'type': 'noun', 'tags': 'number|quantity|counting', 'category': 'noun'},
    'physique': {'type': 'noun', 'tags': 'physical|body|appearance', 'category': 'noun'},
    'plants': {'type': 'noun', 'tags': 'plant|nature|botanical', 'category': 'noun'},
    'politics': {'type': 'noun', 'tags': 'politics|government|social', 'category': 'noun'},
    'profession': {'type': 'noun', 'tags': 'profession|work|occupation', 'category': 'noun'},
    'pronouns': {'type': 'pron', 'tags': 'pronoun|reference', 'category': 'pronoun'},
    'provisions': {'type': 'noun', 'tags': 'provision|supply|material', 'category': 'noun'},
    'religious-institutions': {'type': 'noun', 'tags': 'religious|institution|spiritual', 'category': 'noun'},
    'seasons': {'type': 'noun', 'tags': 'season|time|weather', 'category': 'noun'},
    'simple-verbs': {'type': 'verb', 'tags': 'action|simple', 'category': 'verb'},
    'sizes-and-shapes': {'type': 'adj', 'tags': 'size|shape|physical', 'category': 'adjective'},
    'sky': {'type': 'noun', 'tags': 'sky|celestial|nature', 'category': 'noun'},
    'time': {'type': 'noun', 'tags': 'time|temporal|duration', 'category': 'noun'},
    'trade': {'type': 'noun', 'tags': 'trade|commerce|business', 'category': 'noun'},
    'transport': {'type': 'noun', 'tags': 'transport|vehicle|movement', 'category': 'noun'},
    'tree': {'type': 'noun', 'tags': 'tree|plant|nature', 'category': 'noun'},
    'vegetables': {'type': 'noun', 'tags': 'vegetable|food|plant', 'category': 'noun'},
    'water-animals': {'type': 'noun', 'tags': 'animal|water|aquatic', 'category': 'noun'},
}

class ConceptNetAPI:
    """Interface to ConceptNet API for semantic enhancement"""
    
    BASE_URL = "http://api.conceptnet.io"
    
    @staticmethod
    def get_related_concepts(word: str, language: str = 'en', limit: int = 5) -> List[str]:
        """Get related concepts from ConceptNet"""
        try:
            url = f"{ConceptNetAPI.BASE_URL}/query"
            params = {
                'node': f'/c/{language}/{word.lower()}',
                'limit': limit
            }
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                related = []
                for edge in data.get('edges', []):
                    if 'end' in edge:
                        concept = edge['end'].get('label', '')
                        if concept and concept != word and len(concept.split()) <= 2:
                            related.append(concept.lower())
                return list(set(related))[:limit]
        except Exception as e:
            print(f"ConceptNet API error for '{word}': {e}")
        return []

class NLTKEnhancer:
    """NLTK-based text enhancement"""
    
    @staticmethod
    def initialize():
        """Initialize NLTK data if available"""
        if not NLTK_AVAILABLE:
            return False
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/wordnet')
            return True
        except LookupError:
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('wordnet', quiet=True)
                nltk.download('omw-1.4', quiet=True)  # For lemmatizer
                return True
            except Exception:
                return False
    
    @staticmethod
    def get_synonyms(word: str) -> List[str]:
        """Get synonyms using WordNet"""
        if not NLTK_AVAILABLE:
            return []
        
        try:
            synonyms = set()
            for synset in wordnet.synsets(word):
                for lemma in synset.lemmas():
                    synonym = lemma.name().replace('_', ' ')
                    if synonym != word:
                        synonyms.add(synonym.lower())
            return list(synonyms)[:5]
        except Exception:
            return []
    
    @staticmethod
    def get_definition(word: str) -> str:
        """Get definition using WordNet"""
        if not NLTK_AVAILABLE:
            return ""
        
        try:
            synsets = wordnet.synsets(word)
            if synsets:
                return synsets[0].definition()
        except Exception:
            pass
        return ""

class DictpressConverter:
    """Main converter class"""
    
    def __init__(self):
        self.nltk_enhancer = NLTKEnhancer()
        self.conceptnet_api = ConceptNetAPI()
        
        # Initialize NLTK if available
        if NLTK_AVAILABLE:
            self.nltk_enhancer.initialize()
    
    def get_first_character(self, text: str) -> str:
        """Get the first character for the initial field"""
        if not text:
            return ""
        return text[0]
    
    def get_category_info(self, filename: str) -> Dict[str, str]:
        """Get category information based on filename"""
        # Extract category from filename (remove .csv extension and convert to lowercase)
        category = filename.lower().replace('.csv', '').replace('_', '-')
        return CATEGORY_MAPPINGS.get(category, {
            'type': 'noun', 
            'tags': 'general', 
            'category': 'noun'
        })
    
    def detect_definition_type(self, english_meaning: str, category_info: Dict[str, str]) -> str:
        """Detect definition type from English meaning and category"""
        meaning_lower = english_meaning.lower()
        
        # Use category info first
        if category_info.get('type'):
            return category_info['type']
        
        # Pattern-based detection
        if any(word in meaning_lower for word in ['action', 'to ', 'doing']):
            return 'verb'
        elif any(word in meaning_lower for word in ['quality', 'describing', 'characteristic']):
            return 'adj'
        elif any(word in meaning_lower for word in ['manner', 'way', 'how']):
            return 'adv'
        elif any(word in meaning_lower for word in ['person', 'place', 'thing', 'object']):
            return 'noun'
        else:
            return 'noun'  # Default
    
    def create_enhanced_notes(self, word: str, meaning: str, category: str) -> str:
        """Create enhanced notes using NLTK and ConceptNet"""
        notes_parts = []
        
        # Add basic description
        if category in ['noun', 'verb', 'adj', 'adv']:
            notes_parts.append(f"Sourashtra word meaning {meaning}")
        
        # Add synonyms from NLTK
        synonyms = self.nltk_enhancer.get_synonyms(meaning.split()[0] if meaning else word)
        if synonyms:
            notes_parts.append(f"Related terms: {', '.join(synonyms[:3])}")
        
        # Add definition from NLTK
        definition = self.nltk_enhancer.get_definition(meaning.split()[0] if meaning else word)
        if definition and len(definition) < 100:
            notes_parts.append(definition)
        
        return "; ".join(notes_parts) if notes_parts else f"Sourashtra word meaning {meaning}"
    
    def create_tsvector_tokens(self, sourashtra_word: str, pronunciations: List[str], 
                             english_meaning: str, tamil_meaning: str = None, related_concepts: List[str] = None) -> str:
        """Create tsvector tokens for search optimization - PostgreSQL TSVector format"""
        token_weights = {}  # Use dict to ensure uniqueness and track weights
        weight = 1
        
        def clean_token(token: str) -> str:
            """Clean token for tsvector format - alphanumeric chars including Unicode letters"""
            # Remove punctuation but keep Unicode letters and numbers
            cleaned = re.sub(r'[^\w]', '', token.strip())
            # Convert to lowercase
            cleaned = cleaned.lower()
            # For Tamil and other Unicode scripts, keep all Unicode letters and numbers
            # Remove only ASCII punctuation and symbols, but keep Unicode letters
            cleaned = re.sub(r'[^\w\u0B80-\u0BFF\u0900-\u097F\uA800-\uA82F]', '', cleaned)
            return cleaned if len(cleaned) > 1 else ''  # Only keep tokens longer than 1 char
        
        def add_token(token: str, current_weight: int) -> int:
            """Add token with weight if not already present"""
            clean_tok = clean_token(token)
            if clean_tok and clean_tok not in token_weights:
                token_weights[clean_tok] = current_weight
                return current_weight + 1
            return current_weight
        
        # Add Sourashtra word (weight 1)
        if sourashtra_word:
            weight = add_token(sourashtra_word, weight)
        
        # Add pronunciations (weight 2-6)
        for pron in pronunciations:
            if pron and pron.strip():
                weight = add_token(pron, weight)
        
        # Add English meaning words (weight 7+)
        if english_meaning:
            meaning_words = re.findall(r'\b\w+\b', english_meaning.lower())
            for word in meaning_words:
                if len(word) > 2:  # Skip very short words
                    weight = add_token(word, weight)
        
        # Add lemmatized English meaning words using NLTK
        if english_meaning and NLTK_AVAILABLE:
            try:
                lemmatizer = WordNetLemmatizer()
                meaning_words = re.findall(r'\b\w+\b', english_meaning.lower())
                for word in meaning_words:
                    if len(word) > 2:
                        # Try different POS tags for better lemmatization
                        for pos in ['n', 'v', 'a', 'r']:  # noun, verb, adjective, adverb
                            lemma = lemmatizer.lemmatize(word, pos=pos)
                            if lemma != word:  # Only add if lemmatization changed the word
                                weight = add_token(lemma, weight)
            except Exception:
                pass  # Silently continue if lemmatization fails
        
        # Add Tamil meaning words for search capability
        if tamil_meaning:
            # Extract Tamil words - handle both Tamil script and romanized Tamil
            tamil_words = re.findall(r'\b\w+\b', tamil_meaning.lower())
            for word in tamil_words:
                if len(word) > 1:  # Keep even 2-character Tamil words as they can be meaningful
                    weight = add_token(word, weight)
        
        # Add related concepts (if provided)
        if related_concepts:
            for concept in related_concepts[:3]:
                if concept:
                    # Handle multi-word concepts by splitting them
                    concept_words = concept.split()
                    for concept_word in concept_words:
                        weight = add_token(concept_word, weight)
        
        # Convert to PostgreSQL tsvector format
        if not token_weights:
            return ''
        
        # Sort by weight to maintain consistent output
        sorted_tokens = sorted(token_weights.items(), key=lambda x: x[1])
        formatted_tokens = [f"'{token}':{weight}" for token, weight in sorted_tokens]
        
        return ' '.join(formatted_tokens)
    
    def create_semantic_tags(self, category_info: Dict[str, str], 
                           english_meaning: str, related_concepts: List[str] = None) -> str:
        """Create semantic tags"""
        tags = set()
        
        # Add category tags
        if category_info.get('tags'):
            tags.update(category_info['tags'].split('|'))
        
        # Add meaning-based tags
        meaning_lower = english_meaning.lower()
        if 'time' in meaning_lower or 'period' in meaning_lower:
            tags.add('temporal')
        if 'person' in meaning_lower or 'people' in meaning_lower:
            tags.add('person')
        if 'place' in meaning_lower or 'location' in meaning_lower:
            tags.add('location')
        
        # Add related concept tags
        if related_concepts:
            tags.update(related_concepts[:2])
        
        return '|'.join(sorted(tags))
    
    def create_metadata_json(self, category_info: Dict[str, str], 
                           english_meaning: str, etymology: str = None) -> str:
        """Create JSON metadata with proper escaping"""
        metadata = {
            "script": "sourashtra",
            "category": category_info.get('category', 'noun'),
            "type": "concrete" if any(word in english_meaning.lower() 
                                   for word in ['object', 'thing', 'person', 'place']) else "abstract"
        }
        
        if etymology:
            metadata["etymology"] = etymology
        
        # Convert to JSON and escape quotes for CSV
        json_str = json.dumps(metadata, ensure_ascii=False, separators=(',', ':'))
        return json_str.replace('"', '""')  # Escape quotes for CSV
    
    def combine_pronunciations(self, hindi_pron: str, tamil_pron: str, 
                             roman_readable: str, harvard_kyoto: str, 
                             iast: str, ipa: str) -> str:
        """Combine all pronunciations with | separator"""
        pronunciations = []
        for pron in [hindi_pron, tamil_pron, roman_readable, harvard_kyoto, iast, ipa]:
            if pron and pron.strip():
                pronunciations.append(pron.strip())
        return '|'.join(pronunciations)
    
    def convert_row(self, row: List[str], filename: str) -> List[List[str]]:
        """Convert a single CSV row to dictpress format (returns 3 rows)"""
        if len(row) < 9:
            print(f"Warning: Row has {len(row)} fields, expected 9: {row}")
            return []
        
        # Parse input fields
        sourashtra_word = row[0].strip()
        hindi_pron = row[1].strip()
        tamil_pron = row[2].strip()
        roman_readable = row[3].strip()
        harvard_kyoto = row[4].strip()
        iast = row[5].strip()
        ipa = row[6].strip()
        english_meaning = row[7].strip()
        tamil_meaning = row[8].strip()
        
        if not sourashtra_word or not english_meaning:
            return []
        
        # Get category information
        category_info = self.get_category_info(filename)
        
        # Get enhanced information
        # TODO (orsenthil) - This is not used as it conceptnet can divulge.
        related_concepts = self.conceptnet_api.get_related_concepts(english_meaning.split()[0])
        
        # Create components
        initial = self.get_first_character(sourashtra_word)
        definition_type = self.detect_definition_type(english_meaning, category_info)
        enhanced_notes = self.create_enhanced_notes(sourashtra_word, english_meaning, category_info['category'])
        tsvector_tokens = self.create_tsvector_tokens(sourashtra_word, 
                                                    [roman_readable, harvard_kyoto, iast], 
                                                    english_meaning, tamil_meaning)
        semantic_tags = self.create_semantic_tags(category_info, english_meaning)
        phones = self.combine_pronunciations(hindi_pron, tamil_pron, roman_readable, 
                                           harvard_kyoto, iast, ipa)
        metadata = self.create_metadata_json(category_info, english_meaning)
        
        # Create the three output rows
        output_rows = []
        
        # Row 1: Main Sourashtra entry (type -)
        main_row = [
            '-',  # type
            initial,  # initial
            sourashtra_word,  # content
            'sourashtra',  # language
            '',  # notes (optional)
            '',  # tsvector_language (empty for Sourashtra)
            tsvector_tokens,  # tsvector_tokens
            semantic_tags,  # tags
            phones,  # phones
            '',  # definition_type (empty for main entry)
            metadata  # meta
        ]
        output_rows.append(main_row)
        
        # Row 2: English definition (type ^)
        english_notes = self.nltk_enhancer.get_definition(english_meaning.split()[0]) or f"Primary definition: {english_meaning}"
        english_row = [
            '^',  # type
            '',  # initial
            english_meaning,  # content
            'english',  # language
            '',  # notes (optional)
            'english',  # tsvector_language
            '',  # tsvector_tokens (auto-generated by Postgres)
            semantic_tags,  # tags
            '',  # phones
            definition_type,  # definition_type
            ''  # meta
        ]
        output_rows.append(english_row)
        
        # Row 3: Tamil definition (type ^)
        tamil_tokens = self.create_tsvector_tokens('', [tamil_meaning], english_meaning, tamil_meaning)
        tamil_row = [
            '^',  # type
            '',  # initial
            tamil_meaning,  # content
            'tamil',  # language
            '',  # notes (optional)
            'tamil',  # tsvector_language
            tamil_tokens,  # tsvector_tokens
            semantic_tags,  # tags
            tamil_pron if tamil_pron else '',  # phones
            definition_type,  # definition_type (Tamil equivalent)
            ''  # meta
        ]
        output_rows.append(tamil_row)
        
        return output_rows
    
    def convert_file(self, input_file: Path, output_file: Path, dry_run: bool = False) -> Tuple[bool, str, int, int]:
        """Convert a single CSV file"""
        try:
            total_rows = 0
            output_rows = 0
            all_output_rows = []
            
            with open(input_file, 'r', encoding='utf-8') as infile:
                csv_reader = csv.reader(infile)
                header = next(csv_reader, None)  # Skip header
                
                if not header:
                    return False, "Empty file or no header found", 0, 0
                
                for row_num, row in enumerate(csv_reader, 2):  # Start from 2 (after header)
                    total_rows += 1
                    
                    if not row or all(field.strip() == '' for field in row):
                        continue
                    
                    converted_rows = self.convert_row(row, input_file.name)
                    if converted_rows:
                        all_output_rows.extend(converted_rows)
                        output_rows += len(converted_rows)
            
            if not dry_run and all_output_rows:
                # Write output file
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                    csv_writer = csv.writer(outfile, lineterminator='\n')
                    
                    # Write only data rows (no header line)
                    for output_row in all_output_rows:
                        csv_writer.writerow(output_row)
            
            return True, None, total_rows, output_rows
            
        except Exception as e:
            return False, f"Error processing file: {str(e)}", 0, 0

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Convert Sourashtra dictionary to dictpress format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 convert_to_dictpress.py                           # Convert all files from words/ to dictpress/
  python3 convert_to_dictpress.py --input-dir processed/    # Convert from processed/ directory
  python3 convert_to_dictpress.py --output-dir output/      # Output to output/ directory
  python3 convert_to_dictpress.py --dry-run                 # Preview without writing files
        '''
    )
    
    parser.add_argument('--input-dir', '-i',
                       default='words',
                       help='Input directory containing CSV files (default: words)')
    parser.add_argument('--output-dir', '-o',
                       default='dictpress',
                       help='Output directory for dictpress files (default: dictpress)')
    parser.add_argument('--dry-run',
                       action='store_true',
                       help='Preview conversion without writing files')
    parser.add_argument('--file-pattern',
                       default='*.csv',
                       help='File pattern to match (default: *.csv)')
    
    args = parser.parse_args()
    
    # Convert to Path objects
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)
    
    if not input_dir.is_dir():
        print(f"Error: Input path is not a directory: {input_dir}")
        sys.exit(1)
    
    # Get CSV files
    csv_files = sorted(input_dir.glob(args.file_pattern))
    
    if not csv_files:
        print(f"No CSV files found in {input_dir}")
        return
    
    print(f"Converting {len(csv_files)} files from {input_dir} to {output_dir}")
    if args.dry_run:
        print("DRY RUN MODE - No files will be written")
    print("=" * 80)
    
    # Initialize converter
    converter = DictpressConverter()
    
    total_input_rows = 0
    total_output_rows = 0
    successful_files = 0
    failed_files = 0
    
    for csv_file in csv_files:
        print(f"\nProcessing: {csv_file.name}")
        
        output_file = output_dir / csv_file.name
        success, error_msg, input_rows, output_rows = converter.convert_file(
            csv_file, output_file, args.dry_run
        )
        
        if success:
            print(f"  ✓ Converted {input_rows} input rows to {output_rows} output rows")
            if not args.dry_run:
                print(f"  → {output_file}")
            successful_files += 1
            total_input_rows += input_rows
            total_output_rows += output_rows
        else:
            print(f"  ✗ Failed: {error_msg}")
            failed_files += 1
    
    # Print summary
    print("\n" + "=" * 80)
    print("CONVERSION SUMMARY")
    print("=" * 80)
    print(f"Files processed: {len(csv_files)}")
    print(f"Successful: {successful_files}")
    print(f"Failed: {failed_files}")
    print(f"Total input rows: {total_input_rows}")
    print(f"Total output rows: {total_output_rows}")
    
    if args.dry_run:
        print("\nDRY RUN completed - no files were written")
    else:
        print(f"\nOutput written to: {output_dir}")
    
    if failed_files > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
