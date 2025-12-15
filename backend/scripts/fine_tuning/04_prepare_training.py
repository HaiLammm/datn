#!/usr/bin/env python3
"""
Script 4: Prepare Training Data
================================
Mục đích: Chuẩn bị dữ liệu final cho fine-tuning Llama 3

Input:  
  - backend/data/training_data/processed/translated_data.json
  - backend/data/training_data/processed/synthetic_data.json (optional)

Output: 
  - backend/data/training_data/splits/train.jsonl
  - backend/data/training_data/splits/val.jsonl
  - backend/data/training_data/splits/test.jsonl

Chạy: python 04_prepare_training.py [--train-ratio 0.8] [--val-ratio 0.1]
"""

import os
import sys
import json
import random
import argparse
from pathlib import Path
from datetime import datetime
from typing import Any

from sklearn.model_selection import train_test_split

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "backend" / "data" / "training_data"
TRANSLATED_FILE = DATA_DIR / "processed" / "translated_data.json"
SYNTHETIC_FILE = DATA_DIR / "processed" / "synthetic_data.json"
RAW_FILE = DATA_DIR / "raw" / "cleaned_data.json"
OUTPUT_DIR = DATA_DIR / "splits"

# Default ratios
DEFAULT_TRAIN_RATIO = 0.8
DEFAULT_VAL_RATIO = 0.1
# Test ratio = 1 - train - val

# Random seed for reproducibility
RANDOM_SEED = 42


# ==============================================================================
# PROMPT TEMPLATES
# ==============================================================================

SYSTEM_PROMPT = """Bạn là chuyên gia đánh giá và so khớp CV với Job Description (JD). 
Nhiệm vụ của bạn là phân tích mức độ phù hợp giữa CV của ứng viên và yêu cầu công việc.
Bạn sẽ đưa ra điểm số, nhận xét chi tiết và gợi ý cải thiện.
Luôn trả lời bằng JSON format."""

USER_PROMPT_TEMPLATE = """Phân tích mức độ phù hợp giữa CV và JD sau:

## CV Ứng viên:
{cv_content}

## Yêu cầu Công việc (JD):
{jd_content}

Hãy đánh giá và trả lời bằng JSON với format sau:
{{
    "match_score": <số từ 0.0 đến 1.0>,
    "match_level": "<excellent|good|fair|poor>",
    "summary": "<tóm tắt đánh giá 1-2 câu>",
    "skill_analysis": {{
        "matched_skills": ["skill1", "skill2"],
        "missing_skills": ["skill1", "skill2"],
        "extra_skills": ["skill1", "skill2"],
        "skill_match_rate": <số từ 0.0 đến 1.0>
    }},
    "experience_analysis": {{
        "required_years": <số>,
        "candidate_years": <số hoặc null>,
        "experience_match": "<nhận xét>",
        "relevant_experience": <true|false>
    }},
    "education_analysis": {{
        "required": "<yêu cầu học vấn>",
        "candidate": "<học vấn ứng viên>",
        "education_match": <true|false>
    }},
    "detailed_feedback": [
        "<điểm mạnh/yếu 1>",
        "<điểm mạnh/yếu 2>",
        "<điểm mạnh/yếu 3>"
    ],
    "improvement_suggestions": [
        "<gợi ý cải thiện 1>",
        "<gợi ý cải thiện 2>"
    ],
    "recommendation": "<STRONGLY_RECOMMEND|RECOMMEND|RECOMMEND_WITH_TRAINING|NOT_RECOMMEND>"
}}"""


# ==============================================================================
# DATA FORMATTING FUNCTIONS
# ==============================================================================

def format_cv_content(cv: dict, language: str = "vi") -> str:
    """Format CV data into readable text."""
    lines = []
    
    # Career objective
    objective = cv.get("career_objective", "")
    if objective:
        lines.append(f"**Mục tiêu nghề nghiệp:** {objective}")
    
    # Skills
    skills = cv.get("skills", [])
    if skills:
        skills_str = ", ".join(skills[:15])  # Limit to 15 skills
        lines.append(f"**Kỹ năng:** {skills_str}")
    
    # Education
    edu = cv.get("education", {})
    if edu:
        institutions = edu.get("institutions", [])
        degrees = edu.get("degrees", [])
        fields = edu.get("fields", [])
        
        if institutions:
            inst = institutions[0] if isinstance(institutions, list) else institutions
            degree = degrees[0] if degrees and isinstance(degrees, list) else ""
            field = fields[0] if fields and isinstance(fields, list) else ""
            lines.append(f"**Học vấn:** {degree} - {field} tại {inst}")
    
    # Experience
    exp = cv.get("experience", {})
    if exp:
        companies = exp.get("companies", [])
        positions = exp.get("positions", [])
        
        if companies and positions:
            exp_items = []
            for i in range(min(3, len(companies))):  # Limit to 3 experiences
                company = companies[i] if i < len(companies) else ""
                position = positions[i] if i < len(positions) else ""
                if company and position:
                    exp_items.append(f"{position} tại {company}")
            
            if exp_items:
                lines.append(f"**Kinh nghiệm:** {'; '.join(exp_items)}")
    
    # Responsibilities
    responsibilities = cv.get("responsibilities", [])
    if responsibilities:
        resp_str = "; ".join(responsibilities[:5])
        lines.append(f"**Trách nhiệm:** {resp_str}")
    
    # Certifications
    certs = cv.get("certifications", {})
    if certs and certs.get("skills"):
        cert_skills = certs.get("skills", [])
        if cert_skills:
            lines.append(f"**Chứng chỉ:** {', '.join(cert_skills[:5])}")
    
    return "\n".join(lines) if lines else "Không có thông tin CV"


def format_jd_content(jd: dict, language: str = "vi") -> str:
    """Format JD data into readable text."""
    lines = []
    
    # Job title
    title = jd.get("job_title", "")
    if title:
        lines.append(f"**Vị trí:** {title}")
    
    # Education requirement
    edu_req = jd.get("education_requirement", "")
    if edu_req:
        lines.append(f"**Yêu cầu học vấn:** {edu_req}")
    
    # Experience requirement
    exp_req = jd.get("experience_requirement", "")
    if exp_req:
        lines.append(f"**Yêu cầu kinh nghiệm:** {exp_req}")
    
    # Skills required
    skills = jd.get("skills_required", [])
    if skills:
        skills_str = ", ".join(skills[:10])
        lines.append(f"**Kỹ năng yêu cầu:** {skills_str}")
    
    # Responsibilities
    responsibilities = jd.get("responsibilities", [])
    if responsibilities:
        resp_str = "; ".join(responsibilities[:5])
        lines.append(f"**Trách nhiệm công việc:** {resp_str}")
    
    # Age requirement
    age_req = jd.get("age_requirement", "")
    if age_req:
        lines.append(f"**Yêu cầu độ tuổi:** {age_req}")
    
    return "\n".join(lines) if lines else "Không có thông tin JD"


def generate_expected_output(record: dict) -> dict:
    """Generate expected model output based on record data."""
    cv = record.get("cv_vi", record.get("cv", {}))
    jd = record.get("jd_vi", record.get("jd", {}))
    score = record.get("matched_score", 0.5)
    level = record.get("match_level", "fair")
    
    # Extract skills
    cv_skills = set(s.lower() for s in cv.get("skills", []))
    jd_skills = set(s.lower() for s in jd.get("skills_required", []))
    
    matched_skills = list(cv_skills.intersection(jd_skills))[:5]
    missing_skills = list(jd_skills - cv_skills)[:5]
    extra_skills = list(cv_skills - jd_skills)[:5]
    
    skill_match_rate = len(matched_skills) / len(jd_skills) if jd_skills else 0.5
    
    # Determine recommendation
    if score >= 0.8:
        recommendation = "STRONGLY_RECOMMEND"
        summary = "Ứng viên rất phù hợp với vị trí. Kỹ năng và kinh nghiệm đáp ứng tốt yêu cầu."
    elif score >= 0.6:
        recommendation = "RECOMMEND"
        summary = "Ứng viên phù hợp với vị trí. Có thể cần bổ sung một số kỹ năng."
    elif score >= 0.4:
        recommendation = "RECOMMEND_WITH_TRAINING"
        summary = "Ứng viên có tiềm năng nhưng cần đào tạo thêm để đáp ứng yêu cầu."
    else:
        recommendation = "NOT_RECOMMEND"
        summary = "Ứng viên chưa đáp ứng được yêu cầu cơ bản của vị trí."
    
    # Generate feedback
    feedback = []
    if matched_skills:
        feedback.append(f"Ứng viên có các kỹ năng phù hợp: {', '.join(matched_skills[:3])}")
    if missing_skills:
        feedback.append(f"Thiếu một số kỹ năng quan trọng: {', '.join(missing_skills[:3])}")
    if extra_skills:
        feedback.append(f"Có thêm các kỹ năng: {', '.join(extra_skills[:3])}")
    
    # Generate suggestions
    suggestions = []
    if missing_skills:
        suggestions.append(f"Bổ sung kỹ năng: {', '.join(missing_skills[:2])}")
    if score < 0.6:
        suggestions.append("Cân nhắc các khóa đào tạo chuyên sâu")
    if not cv.get("certifications", {}).get("skills"):
        suggestions.append("Bổ sung các chứng chỉ chuyên môn")
    
    return {
        "match_score": score,
        "match_level": level,
        "summary": summary,
        "skill_analysis": {
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "extra_skills": extra_skills,
            "skill_match_rate": round(skill_match_rate, 2)
        },
        "experience_analysis": {
            "required_years": jd.get("experience_years"),
            "candidate_years": None,  # Would need parsing
            "experience_match": "Cần đánh giá chi tiết",
            "relevant_experience": score >= 0.5
        },
        "education_analysis": {
            "required": jd.get("education_requirement", "Không xác định"),
            "candidate": cv.get("education", {}).get("degrees", ["Không xác định"])[0] if cv.get("education", {}).get("degrees") else "Không xác định",
            "education_match": score >= 0.5
        },
        "detailed_feedback": feedback if feedback else ["Không có thông tin chi tiết"],
        "improvement_suggestions": suggestions if suggestions else ["Tiếp tục phát triển kỹ năng chuyên môn"],
        "recommendation": recommendation
    }


def create_training_example(record: dict) -> dict:
    """Create a single training example in chat format."""
    # Get CV and JD (prefer Vietnamese if available)
    cv = record.get("cv_vi", record.get("cv", {}))
    jd = record.get("jd_vi", record.get("jd", {}))
    
    # Format content
    cv_content = format_cv_content(cv)
    jd_content = format_jd_content(jd)
    
    # Create user prompt
    user_prompt = USER_PROMPT_TEMPLATE.format(
        cv_content=cv_content,
        jd_content=jd_content
    )
    
    # Generate expected output
    expected_output = generate_expected_output(record)
    
    # Format as chat messages
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": json.dumps(expected_output, ensure_ascii=False, indent=2)}
        ],
        "metadata": {
            "id": record.get("id"),
            "match_score": record.get("matched_score"),
            "match_level": record.get("match_level"),
            "is_synthetic": record.get("is_synthetic", False)
        }
    }


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(description="Prepare training data for fine-tuning")
    parser.add_argument("--train-ratio", type=float, default=DEFAULT_TRAIN_RATIO,
                        help=f"Training set ratio (default: {DEFAULT_TRAIN_RATIO})")
    parser.add_argument("--val-ratio", type=float, default=DEFAULT_VAL_RATIO,
                        help=f"Validation set ratio (default: {DEFAULT_VAL_RATIO})")
    parser.add_argument("--include-synthetic", action="store_true",
                        help="Include synthetic data if available")
    parser.add_argument("--max-samples", type=int, default=None,
                        help="Maximum number of samples to use")
    parser.add_argument("--use-raw", action="store_true",
                        help="Use raw data instead of translated (English only)")
    return parser.parse_args()


def load_data(args) -> list:
    """Load all available data sources."""
    all_records = []
    
    # Try translated data first
    if not args.use_raw and TRANSLATED_FILE.exists():
        print(f"📥 Loading translated data: {TRANSLATED_FILE}")
        with open(TRANSLATED_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            records = data.get("records", [])
            all_records.extend(records)
            print(f"   Loaded {len(records)} translated records")
    
    # Fallback to raw data
    elif RAW_FILE.exists():
        print(f"📥 Loading raw data: {RAW_FILE}")
        with open(RAW_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            records = data.get("records", [])
            # Mark as not having Vietnamese
            for r in records:
                r["cv_vi"] = r.get("cv", {})
                r["jd_vi"] = r.get("jd", {})
            all_records.extend(records)
            print(f"   Loaded {len(records)} raw records")
    
    # Add synthetic data if requested
    if args.include_synthetic and SYNTHETIC_FILE.exists():
        print(f"📥 Loading synthetic data: {SYNTHETIC_FILE}")
        with open(SYNTHETIC_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            records = data.get("records", [])
            all_records.extend(records)
            print(f"   Loaded {len(records)} synthetic records")
    
    return all_records


def save_jsonl(data: list, filepath: Path):
    """Save data as JSONL file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def main():
    args = parse_args()
    
    print("=" * 60)
    print("SCRIPT 4: PREPARE TRAINING DATA")
    print("=" * 60)
    
    print(f"\n📋 Configuration:")
    print(f"   Train ratio: {args.train_ratio}")
    print(f"   Val ratio: {args.val_ratio}")
    print(f"   Test ratio: {1 - args.train_ratio - args.val_ratio:.2f}")
    print(f"   Include synthetic: {args.include_synthetic}")
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("\n📥 Loading data...")
    all_records = load_data(args)
    
    if not all_records:
        print("❌ No data found! Please run previous scripts first.")
        sys.exit(1)
    
    print(f"   Total records: {len(all_records)}")
    
    # Apply max samples limit
    if args.max_samples and len(all_records) > args.max_samples:
        random.seed(RANDOM_SEED)
        all_records = random.sample(all_records, args.max_samples)
        print(f"   Sampled to: {len(all_records)} records")
    
    # Create training examples
    print("\n⚙️  Creating training examples...")
    training_examples = []
    failed = 0
    
    for record in all_records:
        try:
            example = create_training_example(record)
            training_examples.append(example)
        except Exception as e:
            failed += 1
            if failed <= 3:
                print(f"   ⚠️  Error: {e}")
    
    print(f"   Created {len(training_examples)} examples")
    if failed:
        print(f"   Failed: {failed}")
    
    # Split data
    print("\n📊 Splitting data...")
    random.seed(RANDOM_SEED)
    
    # First split: train vs (val + test)
    train_data, temp_data = train_test_split(
        training_examples,
        train_size=args.train_ratio,
        random_state=RANDOM_SEED
    )
    
    # Second split: val vs test
    val_ratio_adjusted = args.val_ratio / (1 - args.train_ratio)
    val_data, test_data = train_test_split(
        temp_data,
        train_size=val_ratio_adjusted,
        random_state=RANDOM_SEED
    )
    
    print(f"   Train: {len(train_data)} ({len(train_data)/len(training_examples)*100:.1f}%)")
    print(f"   Val:   {len(val_data)} ({len(val_data)/len(training_examples)*100:.1f}%)")
    print(f"   Test:  {len(test_data)} ({len(test_data)/len(training_examples)*100:.1f}%)")
    
    # Save splits
    print("\n💾 Saving splits...")
    
    train_file = OUTPUT_DIR / "train.jsonl"
    val_file = OUTPUT_DIR / "val.jsonl"
    test_file = OUTPUT_DIR / "test.jsonl"
    
    save_jsonl(train_data, train_file)
    save_jsonl(val_data, val_file)
    save_jsonl(test_data, test_file)
    
    print(f"   ✅ Train: {train_file} ({train_file.stat().st_size / 1024:.1f} KB)")
    print(f"   ✅ Val:   {val_file} ({val_file.stat().st_size / 1024:.1f} KB)")
    print(f"   ✅ Test:  {test_file} ({test_file.stat().st_size / 1024:.1f} KB)")
    
    # Also save a combined file for reference
    combined_file = OUTPUT_DIR / "all_data.jsonl"
    save_jsonl(training_examples, combined_file)
    print(f"   ✅ All:   {combined_file} ({combined_file.stat().st_size / 1024:.1f} KB)")
    
    # Statistics
    print("\n" + "=" * 60)
    print("📊 DATA PREPARATION COMPLETE")
    print("=" * 60)
    
    # Score distribution in train set
    scores = [ex["metadata"]["match_score"] for ex in train_data]
    print(f"\n📈 Training Set Statistics:")
    print(f"   Total examples: {len(train_data)}")
    print(f"   Score range: {min(scores):.2f} - {max(scores):.2f}")
    print(f"   Score mean: {sum(scores)/len(scores):.2f}")
    
    # Level distribution
    levels = {}
    for ex in train_data:
        level = ex["metadata"]["match_level"]
        levels[level] = levels.get(level, 0) + 1
    
    print(f"\n📊 Match Level Distribution (Train):")
    for level, count in sorted(levels.items()):
        print(f"   {level}: {count} ({count/len(train_data)*100:.1f}%)")
    
    # Show sample
    print("\n📝 Sample Training Example:")
    sample = train_data[0]
    print(f"   User prompt length: {len(sample['messages'][1]['content'])} chars")
    print(f"   Assistant response length: {len(sample['messages'][2]['content'])} chars")
    print(f"   Match score: {sample['metadata']['match_score']}")
    
    print("\n✅ Ready for fine-tuning!")
    print(f"   Training file: {train_file}")


if __name__ == "__main__":
    main()
