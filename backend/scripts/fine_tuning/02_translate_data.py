#!/usr/bin/env python3
"""
Script 2: Data Translation (NLLB-200)
======================================
Mục đích: Dịch dữ liệu CV/JD từ tiếng Anh sang tiếng Việt

Input:  backend/data/training_data/raw/cleaned_data.json
Output: backend/data/training_data/processed/translated_data.json

Model: facebook/nllb-200-distilled-600M

Chạy: python 02_translate_data.py [--batch-size 8] [--sample 100]
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Any
from datetime import datetime

import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
INPUT_FILE = PROJECT_ROOT / "backend" / "data" / "training_data" / "raw" / "cleaned_data.json"
OUTPUT_DIR = PROJECT_ROOT / "backend" / "data" / "training_data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "translated_data.json"

# Model config
MODEL_NAME = "facebook/nllb-200-distilled-600M"
SOURCE_LANG = "eng_Latn"  # English
TARGET_LANG = "vie_Latn"  # Vietnamese

# Translation settings
MAX_LENGTH = 512
DEFAULT_BATCH_SIZE = 4  # Adjust based on your GPU memory


# ==============================================================================
# TRANSLATION CLASS
# ==============================================================================

class NLLBTranslator:
    """Wrapper for NLLB-200 translation model."""
    
    def __init__(self, model_name: str = MODEL_NAME, device: str = None):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        print(f"📥 Loading model: {model_name}")
        print(f"   Device: {self.device}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        # Set source language
        self.tokenizer.src_lang = SOURCE_LANG
        
        print(f"✅ Model loaded successfully!")
        if self.device == "cuda":
            print(f"   GPU Memory: {torch.cuda.memory_allocated() / 1024**2:.0f} MB")
    
    def translate(self, text: str, max_length: int = MAX_LENGTH) -> str:
        """Translate a single text from English to Vietnamese."""
        if not text or not text.strip():
            return ""
        
        # Tokenize
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            max_length=max_length, 
            truncation=True,
            padding=True
        ).to(self.device)
        
        # Generate translation
        with torch.no_grad():
            generated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.lang_code_to_id[TARGET_LANG],
                max_length=max_length,
                num_beams=4,
                early_stopping=True
            )
        
        # Decode
        translation = self.tokenizer.batch_decode(
            generated_tokens, 
            skip_special_tokens=True
        )[0]
        
        return translation.strip()
    
    def translate_batch(self, texts: list[str], max_length: int = MAX_LENGTH) -> list[str]:
        """Translate a batch of texts."""
        if not texts:
            return []
        
        # Filter empty texts
        non_empty_indices = [i for i, t in enumerate(texts) if t and t.strip()]
        non_empty_texts = [texts[i] for i in non_empty_indices]
        
        if not non_empty_texts:
            return [""] * len(texts)
        
        # Tokenize batch
        inputs = self.tokenizer(
            non_empty_texts,
            return_tensors="pt",
            max_length=max_length,
            truncation=True,
            padding=True
        ).to(self.device)
        
        # Generate translations
        with torch.no_grad():
            generated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.lang_code_to_id[TARGET_LANG],
                max_length=max_length,
                num_beams=4,
                early_stopping=True
            )
        
        # Decode
        translations = self.tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True
        )
        
        # Reconstruct full result list
        result = [""] * len(texts)
        for i, idx in enumerate(non_empty_indices):
            result[idx] = translations[i].strip()
        
        return result
    
    def translate_list(self, items: list[str]) -> list[str]:
        """Translate a list of items (like skills)."""
        if not items:
            return []
        
        # Join items with separator, translate, then split
        # This is more efficient than translating each item separately
        translated = []
        for item in items:
            if item and item.strip():
                trans = self.translate(item, max_length=128)
                translated.append(trans if trans else item)
            else:
                translated.append("")
        
        return translated


# ==============================================================================
# DATA TRANSLATION FUNCTIONS
# ==============================================================================

def translate_cv(cv_data: dict, translator: NLLBTranslator) -> dict:
    """Translate CV data from English to Vietnamese."""
    translated = {
        "address": translator.translate(cv_data.get("address", "")),
        "career_objective": translator.translate(cv_data.get("career_objective", "")),
        "skills": cv_data.get("skills", []),  # Keep skills in English (technical terms)
        "skills_vi": translator.translate_list(cv_data.get("skills", [])[:10]),  # Also provide Vietnamese
        "education": {
            "institutions": cv_data.get("education", {}).get("institutions", []),
            "degrees": translator.translate_list(cv_data.get("education", {}).get("degrees", [])),
            "years": cv_data.get("education", {}).get("years", []),
            "fields": translator.translate_list(cv_data.get("education", {}).get("fields", [])),
            "results": cv_data.get("education", {}).get("results", []),
        },
        "experience": {
            "companies": cv_data.get("experience", {}).get("companies", []),
            "positions": translator.translate_list(cv_data.get("experience", {}).get("positions", [])),
            "start_dates": cv_data.get("experience", {}).get("start_dates", []),
            "end_dates": cv_data.get("experience", {}).get("end_dates", []),
            "skills_used": cv_data.get("experience", {}).get("skills_used", []),
            "locations": cv_data.get("experience", {}).get("locations", []),
        },
        "responsibilities": translator.translate_list(cv_data.get("responsibilities", [])[:5]),
        "languages": cv_data.get("languages", []),
        "certifications": cv_data.get("certifications", {}),
    }
    
    return translated


def translate_jd(jd_data: dict, translator: NLLBTranslator) -> dict:
    """Translate JD data from English to Vietnamese."""
    translated = {
        "job_title": translator.translate(jd_data.get("job_title", "")),
        "job_title_en": jd_data.get("job_title", ""),  # Keep original
        "education_requirement": translator.translate(jd_data.get("education_requirement", "")),
        "experience_requirement": translator.translate(jd_data.get("experience_requirement", "")),
        "experience_years": jd_data.get("experience_years"),
        "age_requirement": translator.translate(jd_data.get("age_requirement", "")),
        "responsibilities": translator.translate_list(jd_data.get("responsibilities", [])[:5]),
        "skills_required": jd_data.get("skills_required", []),  # Keep in English
        "skills_required_vi": translator.translate_list(jd_data.get("skills_required", [])[:10]),
    }
    
    return translated


def translate_record(record: dict, translator: NLLBTranslator) -> dict:
    """Translate a complete CV-JD record."""
    return {
        "id": record["id"],
        "cv_en": record["cv"],  # Keep original English
        "cv_vi": translate_cv(record["cv"], translator),
        "jd_en": record["jd"],  # Keep original English
        "jd_vi": translate_jd(record["jd"], translator),
        "matched_score": record["matched_score"],
        "match_level": record["match_level"],
    }


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(description="Translate CV/JD data to Vietnamese")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE,
                        help=f"Batch size for translation (default: {DEFAULT_BATCH_SIZE})")
    parser.add_argument("--sample", type=int, default=None,
                        help="Only process N samples (for testing)")
    parser.add_argument("--start-from", type=int, default=0,
                        help="Start from record index (for resuming)")
    parser.add_argument("--cpu", action="store_true",
                        help="Force CPU usage")
    return parser.parse_args()


def main():
    args = parse_args()
    
    print("=" * 60)
    print("SCRIPT 2: DATA TRANSLATION (NLLB-200)")
    print("=" * 60)
    
    # Check input file
    if not INPUT_FILE.exists():
        print(f"❌ Input file not found: {INPUT_FILE}")
        print("   Please run 01_preprocess_data.py first!")
        sys.exit(1)
    
    print(f"\n📂 Input file: {INPUT_FILE}")
    print(f"📂 Output file: {OUTPUT_FILE}")
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("\n📥 Loading preprocessed data...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    records = data["records"]
    total_records = len(records)
    print(f"   Loaded {total_records} records")
    
    # Apply sample limit if specified
    if args.sample:
        records = records[args.start_from:args.start_from + args.sample]
        print(f"   Processing sample: {len(records)} records (from index {args.start_from})")
    elif args.start_from > 0:
        records = records[args.start_from:]
        print(f"   Resuming from index {args.start_from}: {len(records)} records remaining")
    
    # Initialize translator
    print("\n🔧 Initializing translator...")
    device = "cpu" if args.cpu else None
    translator = NLLBTranslator(device=device)
    
    # Translate records
    print(f"\n🔄 Translating {len(records)} records...")
    translated_records = []
    start_time = datetime.now()
    
    for record in tqdm(records, desc="Translating"):
        try:
            translated = translate_record(record, translator)
            translated_records.append(translated)
        except Exception as e:
            print(f"\n⚠️  Error translating record {record['id']}: {e}")
            # Keep original record with empty translations
            translated_records.append({
                "id": record["id"],
                "cv_en": record["cv"],
                "cv_vi": record["cv"],  # Fallback to English
                "jd_en": record["jd"],
                "jd_vi": record["jd"],  # Fallback to English
                "matched_score": record["matched_score"],
                "match_level": record["match_level"],
                "translation_error": str(e),
            })
    
    # Calculate duration
    duration = datetime.now() - start_time
    
    # Save output
    print(f"\n💾 Saving translated data...")
    output_data = {
        "metadata": {
            "source": str(INPUT_FILE),
            "total_records": len(translated_records),
            "translation_model": MODEL_NAME,
            "source_language": SOURCE_LANG,
            "target_language": TARGET_LANG,
            "translation_time_seconds": duration.total_seconds(),
            "created_at": datetime.now().isoformat(),
        },
        "records": translated_records
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    # Statistics
    print("\n" + "=" * 60)
    print("📊 TRANSLATION COMPLETE")
    print("=" * 60)
    print(f"   ✅ Translated: {len(translated_records)} records")
    print(f"   ⏱️  Duration: {duration}")
    print(f"   📈 Speed: {len(translated_records) / duration.total_seconds():.2f} records/sec")
    print(f"   💾 Output: {OUTPUT_FILE}")
    print(f"   📦 File size: {OUTPUT_FILE.stat().st_size / 1024 / 1024:.1f} MB")
    
    # Show sample
    if translated_records:
        sample = translated_records[0]
        print("\n📝 Sample Translation:")
        print(f"   EN Job Title: {sample['jd_en'].get('job_title', 'N/A')}")
        print(f"   VI Job Title: {sample['jd_vi'].get('job_title', 'N/A')}")
        print(f"   EN Objective: {sample['cv_en'].get('career_objective', 'N/A')[:100]}...")
        print(f"   VI Objective: {sample['cv_vi'].get('career_objective', 'N/A')[:100]}...")


if __name__ == "__main__":
    main()
