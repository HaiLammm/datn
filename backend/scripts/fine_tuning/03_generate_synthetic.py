#!/usr/bin/env python3
"""
Script 3: Synthetic CV Generation (Ollama)
===========================================
Mục đích: Tạo thêm CV tiếng Việt synthetic để đa dạng hóa dataset

Input:  backend/data/training_data/processed/translated_data.json
Output: backend/data/training_data/processed/synthetic_data.json

Model: Ollama (llama3.1:8b hoặc llama3:8b)

Chạy: python 03_generate_synthetic.py [--count 200] [--model llama3.1:8b]
"""

import os
import sys
import json
import random
import argparse
from pathlib import Path
from datetime import datetime
from typing import Any

import httpx
from tqdm import tqdm

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
INPUT_FILE = PROJECT_ROOT / "backend" / "data" / "training_data" / "processed" / "translated_data.json"
# Fallback to raw if translated not exists
INPUT_FILE_RAW = PROJECT_ROOT / "backend" / "data" / "training_data" / "raw" / "cleaned_data.json"
OUTPUT_DIR = PROJECT_ROOT / "backend" / "data" / "training_data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "synthetic_data.json"

# Ollama config
OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.1:8b"
REQUEST_TIMEOUT = 120.0

# Generation settings
DEFAULT_COUNT = 200


# ==============================================================================
# VIETNAMESE CV TEMPLATES
# ==============================================================================

# Common Vietnamese job titles
JOB_TITLES_VI = [
    "Kỹ sư Phần mềm",
    "Lập trình viên Full Stack",
    "Chuyên viên Phân tích Dữ liệu",
    "Kỹ sư Machine Learning",
    "Quản lý Dự án CNTT",
    "Kỹ sư DevOps",
    "Lập trình viên Backend",
    "Lập trình viên Frontend",
    "Kỹ sư AI",
    "Chuyên viên QA/QC",
    "Kỹ sư Hệ thống",
    "Lập trình viên Mobile",
    "Kỹ sư Cloud",
    "Chuyên viên An ninh Mạng",
    "Data Scientist",
    "Kỹ sư Cơ khí",
    "Kế toán viên",
    "Chuyên viên Nhân sự",
    "Marketing Executive",
    "Business Analyst",
]

# Common Vietnamese universities
UNIVERSITIES_VI = [
    "Đại học Bách khoa Hà Nội",
    "Đại học Công nghệ - ĐHQGHN",
    "Đại học FPT",
    "Đại học Bách khoa TP.HCM",
    "Đại học Khoa học Tự nhiên TP.HCM",
    "Đại học Công nghệ Thông tin - ĐHQG TP.HCM",
    "Học viện Công nghệ Bưu chính Viễn thông",
    "Đại học Sư phạm Kỹ thuật TP.HCM",
    "Đại học Kinh tế Quốc dân",
    "Đại học Ngoại thương",
]

# Common Vietnamese companies
COMPANIES_VI = [
    "FPT Software",
    "VNG Corporation",
    "Viettel",
    "VNPT",
    "Tiki",
    "Shopee Việt Nam",
    "Grab Việt Nam",
    "MoMo",
    "ZaloPay",
    "VinAI",
    "VinBigdata",
    "CMC Corporation",
    "TMA Solutions",
    "KMS Technology",
    "NashTech",
]

# Skill categories
SKILL_CATEGORIES = {
    "programming": ["Python", "Java", "JavaScript", "C++", "Go", "Rust", "TypeScript", "PHP", "Ruby", "C#"],
    "frontend": ["React", "Vue.js", "Angular", "HTML/CSS", "Tailwind CSS", "Bootstrap", "Next.js", "Redux"],
    "backend": ["Node.js", "Django", "FastAPI", "Spring Boot", "Express.js", "Flask", "Laravel", "ASP.NET"],
    "database": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Oracle", "SQL Server"],
    "cloud": ["AWS", "Google Cloud", "Azure", "Docker", "Kubernetes", "Terraform", "CI/CD"],
    "ml_ai": ["TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Keras", "NLP", "Computer Vision"],
    "tools": ["Git", "Jira", "Confluence", "VS Code", "IntelliJ", "Postman", "Figma"],
}


# ==============================================================================
# OLLAMA CLIENT
# ==============================================================================

class OllamaClient:
    """Client for Ollama API."""
    
    def __init__(self, base_url: str = OLLAMA_URL, model: str = DEFAULT_MODEL):
        self.base_url = base_url
        self.model = model
        self.client = httpx.Client(timeout=REQUEST_TIMEOUT)
    
    def check_connection(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False
    
    def generate(self, prompt: str, system: str = None) -> str:
        """Generate text using Ollama."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.text}")
        
        return response.json()["message"]["content"]
    
    def generate_json(self, prompt: str, system: str = None) -> dict:
        """Generate JSON response from Ollama."""
        full_prompt = f"{prompt}\n\nTrả lời CHÍNH XÁC bằng JSON format, không có text thừa."
        
        response = self.generate(full_prompt, system)
        
        # Extract JSON from response
        try:
            # Try to find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return None


# ==============================================================================
# SYNTHETIC DATA GENERATION
# ==============================================================================

def generate_cv_prompt(job_title: str, experience_years: int, skill_focus: str) -> str:
    """Generate prompt for creating a Vietnamese CV."""
    skills = random.sample(SKILL_CATEGORIES.get(skill_focus, SKILL_CATEGORIES["programming"]), 5)
    skills_str = ", ".join(skills)
    
    return f"""Tạo một CV tiếng Việt cho vị trí {job_title} với {experience_years} năm kinh nghiệm.

Yêu cầu:
- CV phải hoàn toàn bằng tiếng Việt (trừ tên kỹ năng kỹ thuật)
- Thông tin phải thực tế và phù hợp với thị trường Việt Nam
- Kỹ năng chính: {skills_str}

Trả về JSON với format sau:
{{
    "career_objective": "Mục tiêu nghề nghiệp (2-3 câu)",
    "skills": ["skill1", "skill2", ...],
    "education": {{
        "institution": "Tên trường đại học",
        "degree": "Bằng cấp",
        "field": "Chuyên ngành",
        "year": "Năm tốt nghiệp"
    }},
    "experience": [
        {{
            "company": "Tên công ty",
            "position": "Vị trí",
            "duration": "Thời gian làm việc",
            "responsibilities": ["Trách nhiệm 1", "Trách nhiệm 2"]
        }}
    ],
    "certifications": ["Chứng chỉ nếu có"]
}}"""


def generate_jd_prompt(job_title: str, experience_years: int) -> str:
    """Generate prompt for creating a Vietnamese JD."""
    return f"""Tạo một Job Description (JD) tiếng Việt cho vị trí {job_title}.

Yêu cầu:
- JD phải hoàn toàn bằng tiếng Việt (trừ tên kỹ năng kỹ thuật)
- Yêu cầu {experience_years} năm kinh nghiệm
- Thông tin phải thực tế và phù hợp với thị trường Việt Nam

Trả về JSON với format sau:
{{
    "job_title": "Tên vị trí",
    "education_requirement": "Yêu cầu học vấn",
    "experience_requirement": "Yêu cầu kinh nghiệm",
    "skills_required": ["Kỹ năng 1", "Kỹ năng 2", ...],
    "responsibilities": ["Trách nhiệm 1", "Trách nhiệm 2", ...],
    "benefits": ["Quyền lợi 1", "Quyền lợi 2"]
}}"""


def calculate_match_score(cv: dict, jd: dict) -> float:
    """Calculate a synthetic match score based on skills overlap."""
    cv_skills = set(s.lower() for s in cv.get("skills", []))
    jd_skills = set(s.lower() for s in jd.get("skills_required", []))
    
    if not jd_skills:
        return random.uniform(0.5, 0.8)
    
    overlap = len(cv_skills.intersection(jd_skills))
    base_score = overlap / len(jd_skills) if jd_skills else 0.5
    
    # Add some randomness
    noise = random.uniform(-0.1, 0.1)
    score = max(0.0, min(1.0, base_score + noise))
    
    return round(score, 2)


def generate_synthetic_pair(ollama: OllamaClient, index: int) -> dict | None:
    """Generate a synthetic CV-JD pair."""
    # Randomly select parameters
    job_title = random.choice(JOB_TITLES_VI)
    experience_years = random.randint(1, 10)
    skill_focus = random.choice(list(SKILL_CATEGORIES.keys()))
    
    system_prompt = """Bạn là chuyên gia tạo dữ liệu huấn luyện cho hệ thống matching CV-JD.
Nhiệm vụ: Tạo dữ liệu CV và JD thực tế, đa dạng, bằng tiếng Việt.
Luôn trả lời bằng JSON format chính xác."""
    
    try:
        # Generate CV
        cv_prompt = generate_cv_prompt(job_title, experience_years, skill_focus)
        cv_data = ollama.generate_json(cv_prompt, system_prompt)
        
        if not cv_data:
            return None
        
        # Generate JD (may be same or different job)
        jd_experience = random.randint(max(1, experience_years - 2), experience_years + 3)
        jd_prompt = generate_jd_prompt(job_title, jd_experience)
        jd_data = ollama.generate_json(jd_prompt, system_prompt)
        
        if not jd_data:
            return None
        
        # Calculate match score
        match_score = calculate_match_score(cv_data, jd_data)
        
        # Determine match level
        if match_score >= 0.8:
            match_level = "excellent"
        elif match_score >= 0.6:
            match_level = "good"
        elif match_score >= 0.4:
            match_level = "fair"
        else:
            match_level = "poor"
        
        return {
            "id": f"synthetic_{index}",
            "cv_vi": cv_data,
            "jd_vi": jd_data,
            "matched_score": match_score,
            "match_level": match_level,
            "is_synthetic": True,
            "generation_params": {
                "job_title": job_title,
                "experience_years": experience_years,
                "skill_focus": skill_focus,
            }
        }
        
    except Exception as e:
        print(f"\n⚠️  Error generating pair {index}: {e}")
        return None


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(description="Generate synthetic Vietnamese CV-JD pairs")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT,
                        help=f"Number of synthetic pairs to generate (default: {DEFAULT_COUNT})")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                        help=f"Ollama model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--append", action="store_true",
                        help="Append to existing output file")
    return parser.parse_args()


def main():
    args = parse_args()
    
    print("=" * 60)
    print("SCRIPT 3: SYNTHETIC CV GENERATION (OLLAMA)")
    print("=" * 60)
    
    print(f"\n📋 Configuration:")
    print(f"   Model: {args.model}")
    print(f"   Count: {args.count}")
    print(f"   Output: {OUTPUT_FILE}")
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize Ollama client
    print("\n🔧 Connecting to Ollama...")
    ollama = OllamaClient(model=args.model)
    
    if not ollama.check_connection():
        print("❌ Cannot connect to Ollama!")
        print(f"   Please make sure Ollama is running at {OLLAMA_URL}")
        print("   Start with: ollama serve")
        sys.exit(1)
    
    print(f"✅ Connected to Ollama ({args.model})")
    
    # Load existing data if appending
    existing_records = []
    if args.append and OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            existing_records = existing_data.get("records", [])
        print(f"   Loaded {len(existing_records)} existing records")
    
    # Generate synthetic pairs
    print(f"\n🔄 Generating {args.count} synthetic CV-JD pairs...")
    generated_records = []
    failed_count = 0
    start_time = datetime.now()
    
    for i in tqdm(range(args.count), desc="Generating"):
        record = generate_synthetic_pair(ollama, len(existing_records) + i)
        if record:
            generated_records.append(record)
        else:
            failed_count += 1
    
    # Calculate duration
    duration = datetime.now() - start_time
    
    # Combine with existing
    all_records = existing_records + generated_records
    
    # Save output
    print(f"\n💾 Saving synthetic data...")
    output_data = {
        "metadata": {
            "total_records": len(all_records),
            "new_records": len(generated_records),
            "failed_generations": failed_count,
            "model": args.model,
            "generation_time_seconds": duration.total_seconds(),
            "created_at": datetime.now().isoformat(),
        },
        "records": all_records
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    # Statistics
    print("\n" + "=" * 60)
    print("📊 GENERATION COMPLETE")
    print("=" * 60)
    print(f"   ✅ Generated: {len(generated_records)} records")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   📦 Total in file: {len(all_records)}")
    print(f"   ⏱️  Duration: {duration}")
    print(f"   💾 Output: {OUTPUT_FILE}")
    
    # Show sample
    if generated_records:
        sample = generated_records[0]
        print("\n📝 Sample Synthetic Record:")
        print(f"   Job Title: {sample['jd_vi'].get('job_title', 'N/A')}")
        print(f"   Skills: {sample['cv_vi'].get('skills', [])[:5]}")
        print(f"   Match Score: {sample['matched_score']}")


if __name__ == "__main__":
    main()
