#!/usr/bin/env python3
"""
Script to index job/CV data from CSV into ChromaDB for RAG enhancement.

This script reads data from cv/data_cv.csv and indexes:
1. Job descriptions (position name, responsibilities, requirements, skills)
2. Career objectives and candidate skills as reference data

Usage:
    cd backend
    python -m scripts.index_csv_to_chromadb
"""

import csv
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.modules.ai.vector_store import vector_store
from app.modules.ai.embeddings import embedding_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Collection names
COLLECTION_JOB_DATA = "job_reference_data"  # For job descriptions from CSV

# ChromaDB max batch size (actual limit is 5461, we use smaller for safety)
CHROMA_MAX_BATCH_SIZE = 5000


def clean_text(text: Optional[str]) -> str:
    """Clean and normalize text content."""
    if not text or text == "None" or text.strip() == "":
        return ""
    # Remove extra whitespace and normalize newlines
    return " ".join(text.strip().split())


def parse_csv_row(row: Dict[str, str]) -> Dict[str, Any]:
    """Parse a CSV row into structured data."""
    return {
        # Career/CV data (English)
        "career_objective": clean_text(row.get("career_objective", "")),
        "skills": clean_text(row.get("skills", "")),
        "positions": clean_text(row.get("positions", "")),
        
        # Career/CV data (Vietnamese)
        "career_objective_vi": clean_text(row.get("career_object_vi", "")),
        
        # Job description data
        "job_position_name": clean_text(row.get("\ufeffjob_position_name", "") or row.get("job_position_name", "")),
        "responsibilities": clean_text(row.get("responsibilities", "")),
        "responsibilities_vi": clean_text(row.get("responsibilites_vi", "")),
        "educational_requirements": clean_text(row.get("educationaL_requirements", "")),
        "experience_requirement": clean_text(row.get("experiencere_requirement", "")),
        "skills_required": clean_text(row.get("skills_required", "")),
        "matched_score": clean_text(row.get("matched_score", "")),
        
        # Related skills
        "related_skills_in_job": clean_text(row.get("related_skils_in_job", "")),
    }


def create_job_document(data: Dict[str, Any], doc_id: str, lang: str = "en") -> tuple[str, str, Dict[str, Any]]:
    """
    Create a document for job description indexing.
    
    Returns:
        Tuple of (doc_id, content, metadata)
    """
    job_name = data.get("job_position_name", "Unknown Position")
    
    if lang == "vi":
        responsibilities = data.get("responsibilities_vi", "") or data.get("responsibilities", "")
    else:
        responsibilities = data.get("responsibilities", "")
    
    # Build comprehensive job description content
    content_parts = []
    
    if job_name:
        content_parts.append(f"Job Position: {job_name}")
    
    if responsibilities:
        content_parts.append(f"Responsibilities: {responsibilities}")
    
    if data.get("educational_requirements"):
        content_parts.append(f"Education Requirements: {data['educational_requirements']}")
    
    if data.get("experience_requirement"):
        content_parts.append(f"Experience Required: {data['experience_requirement']}")
    
    if data.get("skills_required"):
        content_parts.append(f"Required Skills: {data['skills_required']}")
    
    content = "\n\n".join(content_parts)
    
    metadata = {
        "doc_type": "job_description",
        "job_position": job_name[:200] if job_name else "",
        "language": lang,
        "source": "data_cv.csv"
    }
    
    return f"{doc_id}_{lang}", content, metadata


def create_career_document(data: Dict[str, Any], doc_id: str, lang: str = "en") -> tuple[str, str, Dict[str, Any]]:
    """
    Create a document for career objective/skills indexing.
    
    Returns:
        Tuple of (doc_id, content, metadata)
    """
    if lang == "vi":
        career_obj = data.get("career_objective_vi", "") or data.get("career_objective", "")
    else:
        career_obj = data.get("career_objective", "")
    
    skills = data.get("skills", "")
    positions = data.get("positions", "")
    
    # Build career profile content
    content_parts = []
    
    if career_obj:
        content_parts.append(f"Career Objective: {career_obj}")
    
    if skills:
        content_parts.append(f"Skills: {skills}")
    
    if positions:
        content_parts.append(f"Target Positions: {positions}")
    
    if data.get("matched_score"):
        content_parts.append(f"Match Score: {data['matched_score']}")
    
    content = "\n\n".join(content_parts)
    
    metadata = {
        "doc_type": "career_profile",
        "language": lang,
        "source": "data_cv.csv"
    }
    
    if positions:
        metadata["positions"] = positions[:200]
    
    return f"career_{doc_id}_{lang}", content, metadata


def load_csv_data(csv_path: Path, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Load and parse CSV data."""
    logger.info(f"Loading CSV data from: {csv_path}")
    
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    data = []
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = parse_csv_row(row)
            # Only include rows with meaningful content
            if parsed.get("job_position_name") or parsed.get("career_objective"):
                data.append(parsed)
                if limit and len(data) >= limit:
                    break
    
    logger.info(f"Loaded {len(data)} valid records from CSV")
    return data


def index_batch_to_chromadb(
    collection_name: str,
    doc_ids: List[str],
    contents: List[str],
    embeddings: List[List[float]],
    metadatas: List[Dict[str, Any]],
    doc_type: str = "documents"
) -> int:
    """
    Index documents to ChromaDB in batches to avoid max batch size limit.
    
    Returns:
        Number of successfully indexed documents
    """
    total_docs = len(doc_ids)
    indexed_count = 0
    
    # Process in chunks
    for start_idx in range(0, total_docs, CHROMA_MAX_BATCH_SIZE):
        end_idx = min(start_idx + CHROMA_MAX_BATCH_SIZE, total_docs)
        batch_num = (start_idx // CHROMA_MAX_BATCH_SIZE) + 1
        total_batches = (total_docs + CHROMA_MAX_BATCH_SIZE - 1) // CHROMA_MAX_BATCH_SIZE
        
        logger.info(f"Indexing batch {batch_num}/{total_batches} ({start_idx}-{end_idx} of {total_docs} {doc_type})...")
        
        success = vector_store.index_documents_batch(
            collection_name=collection_name,
            doc_ids=doc_ids[start_idx:end_idx],
            contents=contents[start_idx:end_idx],
            embeddings=embeddings[start_idx:end_idx],
            metadatas=metadatas[start_idx:end_idx]
        )
        
        if success:
            batch_size = end_idx - start_idx
            indexed_count += batch_size
            logger.info(f"Batch {batch_num} indexed successfully ({batch_size} documents)")
        else:
            logger.error(f"Batch {batch_num} failed to index")
    
    return indexed_count


def index_job_documents(data: List[Dict[str, Any]]) -> int:
    """Index job description documents."""
    logger.info("Indexing job description documents...")
    
    doc_ids = []
    contents = []
    metadatas = []
    
    for i, record in enumerate(data):
        # Skip if no job position name
        if not record.get("job_position_name"):
            continue
        
        # Create English document
        doc_id_en, content_en, meta_en = create_job_document(record, f"job_{i}", "en")
        if content_en and len(content_en.strip()) > 20:
            doc_ids.append(doc_id_en)
            contents.append(content_en)
            metadatas.append(meta_en)
        
        # Create Vietnamese document if available
        if record.get("responsibilities_vi"):
            doc_id_vi, content_vi, meta_vi = create_job_document(record, f"job_{i}", "vi")
            if content_vi and len(content_vi.strip()) > 20:
                doc_ids.append(doc_id_vi)
                contents.append(content_vi)
                metadatas.append(meta_vi)
    
    if not doc_ids:
        logger.warning("No job documents to index")
        return 0
    
    logger.info(f"Generating embeddings for {len(doc_ids)} job documents...")
    embeddings = embedding_service.generate_embeddings_batch(contents)
    
    # Filter out failed embeddings
    valid_indices = [i for i in range(len(doc_ids)) if embeddings[i] is not None]
    
    if not valid_indices:
        logger.error("All embeddings failed")
        return 0
    
    valid_doc_ids = [doc_ids[i] for i in valid_indices]
    valid_contents = [contents[i] for i in valid_indices]
    valid_embeddings = [embeddings[i] for i in valid_indices]
    valid_metadatas = [metadatas[i] for i in valid_indices]
    
    logger.info(f"Indexing {len(valid_doc_ids)} job documents to ChromaDB (in batches of {CHROMA_MAX_BATCH_SIZE})...")
    indexed = index_batch_to_chromadb(
        collection_name=COLLECTION_JOB_DATA,
        doc_ids=valid_doc_ids,
        contents=valid_contents,
        embeddings=valid_embeddings,
        metadatas=valid_metadatas,
        doc_type="job documents"
    )
    
    logger.info(f"Successfully indexed {indexed}/{len(valid_doc_ids)} job documents")
    return indexed


def index_career_documents(data: List[Dict[str, Any]]) -> int:
    """Index career objective/profile documents."""
    logger.info("Indexing career profile documents...")
    
    doc_ids = []
    contents = []
    metadatas = []
    
    for i, record in enumerate(data):
        # Skip if no career objective
        if not record.get("career_objective"):
            continue
        
        # Create English document
        doc_id_en, content_en, meta_en = create_career_document(record, f"{i}", "en")
        if content_en and len(content_en.strip()) > 20:
            doc_ids.append(doc_id_en)
            contents.append(content_en)
            metadatas.append(meta_en)
        
        # Create Vietnamese document if available
        if record.get("career_objective_vi"):
            doc_id_vi, content_vi, meta_vi = create_career_document(record, f"{i}", "vi")
            if content_vi and len(content_vi.strip()) > 20:
                doc_ids.append(doc_id_vi)
                contents.append(content_vi)
                metadatas.append(meta_vi)
    
    if not doc_ids:
        logger.warning("No career documents to index")
        return 0
    
    logger.info(f"Generating embeddings for {len(doc_ids)} career documents...")
    embeddings = embedding_service.generate_embeddings_batch(contents)
    
    # Filter out failed embeddings
    valid_indices = [i for i in range(len(doc_ids)) if embeddings[i] is not None]
    
    if not valid_indices:
        logger.error("All embeddings failed")
        return 0
    
    valid_doc_ids = [doc_ids[i] for i in valid_indices]
    valid_contents = [contents[i] for i in valid_indices]
    valid_embeddings = [embeddings[i] for i in valid_indices]
    valid_metadatas = [metadatas[i] for i in valid_indices]
    
    # Index to the reference collection (same as other reference docs)
    logger.info(f"Indexing {len(valid_doc_ids)} career documents to ChromaDB (in batches of {CHROMA_MAX_BATCH_SIZE})...")
    indexed = index_batch_to_chromadb(
        collection_name=settings.CHROMA_COLLECTION_REFERENCE,
        doc_ids=valid_doc_ids,
        contents=valid_contents,
        embeddings=valid_embeddings,
        metadatas=valid_metadatas,
        doc_type="career documents"
    )
    
    logger.info(f"Successfully indexed {indexed}/{len(valid_doc_ids)} career documents")
    return indexed


def get_stats() -> Dict[str, int]:
    """Get current collection statistics."""
    return {
        "job_reference_data": vector_store.get_collection_count(COLLECTION_JOB_DATA),
        "job_descriptions": vector_store.get_collection_count(settings.CHROMA_COLLECTION_JOBS),
        "reference_docs": vector_store.get_collection_count(settings.CHROMA_COLLECTION_REFERENCE),
    }


def main():
    """Main function to run the indexing process."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Index CSV data to ChromaDB")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records to process")
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Starting CSV data indexing to ChromaDB")
    logger.info("=" * 60)
    
    # Check services availability
    if not vector_store.is_available:
        logger.error("ChromaDB is not available. Please check configuration.")
        sys.exit(1)
    
    if not embedding_service.is_available:
        logger.error("Embedding service is not available. Please check model.")
        sys.exit(1)
    
    # Get initial stats
    logger.info("Initial collection stats:")
    initial_stats = get_stats()
    for name, count in initial_stats.items():
        logger.info(f"  {name}: {count} documents")
    
    # Load CSV data
    csv_path = Path(__file__).parent.parent.parent / "cv" / "data_cv.csv"
    try:
        data = load_csv_data(csv_path, limit=args.limit)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    
    # Index documents
    job_count = index_job_documents(data)
    career_count = index_career_documents(data)
    
    # Get final stats
    logger.info("Final collection stats:")
    final_stats = get_stats()
    for name, count in final_stats.items():
        logger.info(f"  {name}: {count} documents")
    
    logger.info("=" * 60)
    logger.info(f"Indexing completed!")
    logger.info(f"  Job documents indexed: {job_count}")
    logger.info(f"  Career documents indexed: {career_count}")
    logger.info(f"  Total documents indexed: {job_count + career_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
