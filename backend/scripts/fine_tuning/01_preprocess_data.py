#!/usr/bin/env python3
"""
Script 1: Data Preprocessing
=============================
Mục đích: Clean và chuẩn hóa dữ liệu từ resume_data.csv

Input:  cv/resume_data.csv
Output: backend/data/training_data/raw/cleaned_data.json

Chạy: python 01_preprocess_data.py
"""

import os
import sys
import json
import re
import ast
from pathlib import Path
from typing import Any

import pandas as pd
import numpy as np
from tqdm import tqdm

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # /home/.../datn
INPUT_FILE = PROJECT_ROOT / "cv" / "resume_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "backend" / "data" / "training_data" / "raw"
OUTPUT_FILE = OUTPUT_DIR / "cleaned_data.json"

# Minimum requirements for a valid record
MIN_SKILLS_COUNT = 1
MIN_SCORE = 0.0
MAX_SCORE = 1.0


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def safe_parse_list(value: Any) -> list:
    """Safely parse a string representation of a list."""
    if pd.isna(value) or value is None:
        return []
    
    if isinstance(value, list):
        return value
    
    if isinstance(value, str):
        value = value.strip()
        if not value or value.lower() in ['n/a', 'none', 'null', '[]']:
            return []
        
        try:
            # Try to parse as Python literal
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if item]
            return [str(parsed).strip()] if parsed else []
        except (ValueError, SyntaxError):
            # If parsing fails, try splitting by common delimiters
            if ',' in value:
                return [item.strip() for item in value.split(',') if item.strip()]
            return [value.strip()] if value.strip() else []
    
    return []


def clean_text(text: Any) -> str:
    """Clean and normalize text content."""
    if pd.isna(text) or text is None:
        return ""
    
    text = str(text).strip()
    
    if text.lower() in ['n/a', 'none', 'null', 'nan']:
        return ""
    
    # Remove excessive whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = text.replace('\ufeff', '')  # BOM
    text = text.replace('ï¼', ':')  # Fix encoding issues
    
    return text.strip()


def normalize_score(score: Any) -> float | None:
    """Normalize the matched_score to [0, 1] range."""
    if pd.isna(score) or score is None:
        return None
    
    try:
        score = float(score)
        if MIN_SCORE <= score <= MAX_SCORE:
            return round(score, 4)
        elif score > 1:
            # Might be percentage, convert to decimal
            return round(score / 100, 4) if score <= 100 else None
        return None
    except (ValueError, TypeError):
        return None


def extract_years_experience(exp_req: str) -> int | None:
    """Extract years of experience from requirement string."""
    if not exp_req:
        return None
    
    # Patterns like "At least 3 years", "3 to 5 years", "1 year"
    patterns = [
        r'at least (\d+)',
        r'(\d+)\s*to\s*\d+',
        r'(\d+)\s*-\s*\d+',
        r'(\d+)\s*year',
        r'(\d+)\s*\+',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, exp_req.lower())
        if match:
            return int(match.group(1))
    
    return None


def parse_responsibilities(resp: Any) -> list[str]:
    """Parse responsibilities into a list of items."""
    if pd.isna(resp) or resp is None:
        return []
    
    text = str(resp).strip()
    if not text or text.lower() in ['n/a', 'none', 'null']:
        return []
    
    # Split by newlines
    items = text.split('\n')
    
    # Clean each item
    cleaned = []
    for item in items:
        item = item.strip()
        # Remove leading bullets or numbers
        item = re.sub(r'^[\d\.\)\-\*\•]+\s*', '', item)
        if item and len(item) > 2:
            cleaned.append(item)
    
    return cleaned


# ==============================================================================
# DATA PROCESSING
# ==============================================================================

def process_cv_data(row: pd.Series) -> dict | None:
    """Process a single CV record."""
    cv_data = {
        "address": clean_text(row.get("address", "")),
        "career_objective": clean_text(row.get("career_objective", "")),
        "skills": safe_parse_list(row.get("skills", [])),
        "education": {
            "institutions": safe_parse_list(row.get("educational_institution_name", [])),
            "degrees": safe_parse_list(row.get("degree_names", [])),
            "years": safe_parse_list(row.get("passing_years", [])),
            "fields": safe_parse_list(row.get("major_field_of_studies", [])),
            "results": safe_parse_list(row.get("educational_results", [])),
        },
        "experience": {
            "companies": safe_parse_list(row.get("professional_company_names", [])),
            "positions": safe_parse_list(row.get("positions", [])),
            "start_dates": safe_parse_list(row.get("start_dates", [])),
            "end_dates": safe_parse_list(row.get("end_dates", [])),
            "skills_used": safe_parse_list(row.get("related_skils_in_job", [])),
            "locations": safe_parse_list(row.get("locations", [])),
        },
        "responsibilities": parse_responsibilities(row.get("responsibilities", "")),
        "languages": safe_parse_list(row.get("languages", [])),
        "certifications": {
            "providers": safe_parse_list(row.get("certification_providers", [])),
            "skills": safe_parse_list(row.get("certification_skills", [])),
        },
        "extra_curricular": {
            "types": safe_parse_list(row.get("extra_curricular_activity_types", [])),
            "organizations": safe_parse_list(row.get("extra_curricular_organization_names", [])),
        },
    }
    
    # Validate CV has minimum required data
    if len(cv_data["skills"]) < MIN_SKILLS_COUNT:
        return None
    
    return cv_data


def process_jd_data(row: pd.Series) -> dict | None:
    """Process a single JD record."""
    jd_data = {
        "job_title": clean_text(row.get("﻿job_position_name", row.get("job_position_name", ""))),
        "education_requirement": clean_text(row.get("educationaL_requirements", row.get("educational_requirements", ""))),
        "experience_requirement": clean_text(row.get("experiencere_requirement", row.get("experience_requirement", ""))),
        "experience_years": extract_years_experience(
            clean_text(row.get("experiencere_requirement", row.get("experience_requirement", "")))
        ),
        "age_requirement": clean_text(row.get("age_requirement", "")),
        "responsibilities": parse_responsibilities(row.get("responsibilities.1", "")),
        "skills_required": safe_parse_list(row.get("skills_required", [])),
    }
    
    # Also try parsing skills_required from text if it's a string with newlines
    if not jd_data["skills_required"]:
        skills_text = str(row.get("skills_required", ""))
        if '\n' in skills_text:
            jd_data["skills_required"] = [
                s.strip() for s in skills_text.split('\n') 
                if s.strip() and s.strip().lower() not in ['n/a', 'none']
            ]
    
    # Validate JD has minimum required data
    if not jd_data["job_title"]:
        return None
    
    return jd_data


def process_record(row: pd.Series, idx: int) -> dict | None:
    """Process a complete CV-JD pair."""
    # Get match score
    score = normalize_score(row.get("matched_score"))
    if score is None:
        return None
    
    # Process CV
    cv_data = process_cv_data(row)
    if cv_data is None:
        return None
    
    # Process JD
    jd_data = process_jd_data(row)
    if jd_data is None:
        return None
    
    return {
        "id": idx,
        "cv": cv_data,
        "jd": jd_data,
        "matched_score": score,
        "match_level": categorize_score(score),
    }


def categorize_score(score: float) -> str:
    """Categorize match score into levels."""
    if score >= 0.8:
        return "excellent"
    elif score >= 0.6:
        return "good"
    elif score >= 0.4:
        return "fair"
    else:
        return "poor"


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    print("=" * 60)
    print("SCRIPT 1: DATA PREPROCESSING")
    print("=" * 60)
    
    # Check input file exists
    if not INPUT_FILE.exists():
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        sys.exit(1)
    
    print(f"\n📂 Input file: {INPUT_FILE}")
    print(f"📂 Output file: {OUTPUT_FILE}")
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("\n📥 Loading data...")
    df = pd.read_csv(INPUT_FILE, encoding='utf-8', on_bad_lines='skip')
    print(f"   Loaded {len(df)} records")
    print(f"   Columns: {len(df.columns)}")
    
    # Display column names for debugging
    print("\n📋 Columns found:")
    for i, col in enumerate(df.columns):
        print(f"   {i+1}. {col}")
    
    # Process records
    print("\n⚙️  Processing records...")
    processed_records = []
    failed_records = 0
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing"):
        try:
            record = process_record(row, idx)
            if record:
                processed_records.append(record)
            else:
                failed_records += 1
        except Exception as e:
            failed_records += 1
            if failed_records <= 5:  # Only show first 5 errors
                print(f"\n   ⚠️  Error at row {idx}: {e}")
    
    # Statistics
    print("\n📊 Processing Statistics:")
    print(f"   ✅ Successfully processed: {len(processed_records)}")
    print(f"   ❌ Failed/Skipped: {failed_records}")
    print(f"   📈 Success rate: {len(processed_records)/len(df)*100:.1f}%")
    
    # Score distribution
    scores = [r["matched_score"] for r in processed_records]
    print("\n📈 Score Distribution:")
    print(f"   Min: {min(scores):.2f}")
    print(f"   Max: {max(scores):.2f}")
    print(f"   Mean: {np.mean(scores):.2f}")
    print(f"   Median: {np.median(scores):.2f}")
    
    # Level distribution
    levels = {}
    for r in processed_records:
        level = r["match_level"]
        levels[level] = levels.get(level, 0) + 1
    
    print("\n📊 Match Level Distribution:")
    for level, count in sorted(levels.items()):
        print(f"   {level}: {count} ({count/len(processed_records)*100:.1f}%)")
    
    # Save output
    print(f"\n💾 Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "source": str(INPUT_FILE),
                "total_records": len(processed_records),
                "failed_records": failed_records,
                "score_stats": {
                    "min": min(scores),
                    "max": max(scores),
                    "mean": float(np.mean(scores)),
                    "median": float(np.median(scores)),
                },
                "level_distribution": levels,
            },
            "records": processed_records
        }, f, ensure_ascii=False, indent=2)
    
    print("\n✅ Preprocessing complete!")
    print(f"   Output saved to: {OUTPUT_FILE}")
    print(f"   File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
    
    # Show sample record
    print("\n📝 Sample Record (first):")
    sample = processed_records[0]
    print(json.dumps({
        "id": sample["id"],
        "cv_skills": sample["cv"]["skills"][:5],
        "jd_title": sample["jd"]["job_title"],
        "jd_skills": sample["jd"]["skills_required"][:5] if sample["jd"]["skills_required"] else [],
        "matched_score": sample["matched_score"],
        "match_level": sample["match_level"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
