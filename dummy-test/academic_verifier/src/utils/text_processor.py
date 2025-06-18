"""
Text Processor Module

This module provides utilities for processing and analyzing text from academic papers.
"""

import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


def extract_sections(text: str) -> Dict[str, str]:
    """
    Extract sections from a paper's text.
    
    Args:
        text: Paper text
        
    Returns:
        Dictionary mapping section names to section content
    """
    if not text:
        return {}
    
    # Common section headers in academic papers
    section_patterns = [
        r"(?i)abstract",
        r"(?i)introduction",
        r"(?i)background",
        r"(?i)related\s+work",
        r"(?i)methodology|methods",
        r"(?i)experimental\s+setup|experiment",
        r"(?i)results",
        r"(?i)discussion",
        r"(?i)conclusion",
        r"(?i)references|bibliography"
    ]
    
    # Combine patterns into a single regex
    combined_pattern = r"(?:^|\n)(" + "|".join(section_patterns) + r")(?:\s*\n|\s*:)"
    
    # Find all section headers
    matches = list(re.finditer(combined_pattern, text, re.MULTILINE))
    
    # If no sections found, treat the entire text as a single section
    if not matches:
        return {"content": text}
    
    sections = {}
    
    # Extract content for each section
    for i, match in enumerate(matches):
        section_name = match.group(1).strip().lower()
        start_pos = match.end()
        
        # End position is the start of the next section or the end of the text
        end_pos = matches[i + 1].start() if i < len(matches) - 1 else len(text)
        
        # Extract section content
        section_content = text[start_pos:end_pos].strip()
        
        # Normalize section name
        normalized_name = normalize_section_name(section_name)
        
        sections[normalized_name] = section_content
    
    # If abstract is not found but the text starts before the first section,
    # treat that as the abstract
    if "abstract" not in sections and matches[0].start() > 0:
        abstract_content = text[:matches[0].start()].strip()
        if abstract_content:
            sections["abstract"] = abstract_content
    
    return sections


def normalize_section_name(section_name: str) -> str:
    """
    Normalize a section name.
    
    Args:
        section_name: Section name
        
    Returns:
        Normalized section name
    """
    section_name = section_name.lower().strip()
    
    # Remove punctuation and extra whitespace
    section_name = re.sub(r"[^\w\s]", "", section_name)
    section_name = re.sub(r"\s+", " ", section_name).strip()
    
    # Map similar section names to standard names
    mapping = {
        "abstract": "abstract",
        "introduction": "introduction",
        "background": "background",
        "related work": "related_work",
        "methodology": "methodology",
        "methods": "methodology",
        "experimental setup": "methodology",
        "experiment": "methodology",
        "results": "results",
        "discussion": "discussion",
        "conclusion": "conclusion",
        "conclusions": "conclusion",
        "references": "references",
        "bibliography": "references"
    }
    
    # Return mapped name or original if not in mapping
    return mapping.get(section_name, section_name)


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace, special characters, etc.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Replace multiple whitespace with a single space
    text = re.sub(r"\s+", " ", text)
    
    # Remove non-printable characters
    text = re.sub(r"[^\x20-\x7E\n]", "", text)
    
    # Remove URLs
    text = re.sub(r"https?://\S+", "[URL]", text)
    
    # Remove email addresses
    text = re.sub(r"\S+@\S+", "[EMAIL]", text)
    
    return text.strip()


def extract_citations(text: str) -> List[str]:
    """
    Extract citations from text.
    
    Args:
        text: Text to extract citations from
        
    Returns:
        List of extracted citations
    """
    citations = []
    
    # Match citations in various formats
    
    # Harvard style: (Author, Year)
    harvard_pattern = r"\(([A-Za-z\s]+(?:et al\.)?),\s*(\d{4}[a-z]?)\)"
    harvard_matches = re.finditer(harvard_pattern, text)
    for match in harvard_matches:
        citations.append(match.group(0))
    
    # IEEE style: [1], [2-5]
    ieee_pattern = r"\[(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)\]"
    ieee_matches = re.finditer(ieee_pattern, text)
    for match in ieee_matches:
        citations.append(match.group(0))
    
    # APA style: (Author et al., Year)
    apa_pattern = r"\(([A-Za-z\s]+(?:et al\.)?),\s*(\d{4}[a-z]?)\)"
    apa_matches = re.finditer(apa_pattern, text)
    for match in apa_matches:
        citations.append(match.group(0))
    
    return citations


def count_words(text: str) -> int:
    """
    Count the number of words in text.
    
    Args:
        text: Text to count words in
        
    Returns:
        Word count
    """
    if not text:
        return 0
    
    # Split by whitespace and count non-empty words
    words = [word for word in re.split(r"\s+", text) if word]
    return len(words)


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract potential keywords from text.
    
    This is a simple implementation that counts word frequencies.
    A more sophisticated approach would use NLP techniques.
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text)
    
    # Split into words
    words = re.split(r"\s+", text)
    
    # Remove common stop words
    stop_words = {
        "a", "an", "the", "and", "or", "but", "if", "then", "else", "when",
        "at", "from", "by", "for", "with", "about", "against", "between",
        "into", "through", "during", "before", "after", "above", "below",
        "to", "of", "in", "on", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "having", "do", "does", "did", "doing",
        "this", "that", "these", "those", "it", "its", "we", "they", "them",
        "their", "what", "which", "who", "whom", "whose", "where", "when",
        "why", "how", "all", "any", "both", "each", "few", "more", "most",
        "other", "some", "such", "no", "nor", "not", "only", "own", "same",
        "so", "than", "too", "very", "can", "will", "just", "should", "now"
    }
    
    filtered_words = [word for word in words if word and word not in stop_words and len(word) > 2]
    
    # Count word frequencies
    word_counts = {}
    for word in filtered_words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Return top keywords
    return [word for word, count in sorted_words[:max_keywords]]


def calculate_readability_score(text: str) -> float:
    """
    Calculate a simple readability score for text.
    
    This implements a simplified version of the Flesch Reading Ease score.
    
    Args:
        text: Text to calculate score for
        
    Returns:
        Readability score (higher is more readable)
    """
    if not text:
        return 0.0
    
    # Count sentences
    sentences = re.split(r"[.!?]+", text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    # Count words
    word_count = count_words(text)
    
    # Count syllables (simplified)
    syllable_count = 0
    for word in re.split(r"\s+", text.lower()):
        if not word:
            continue
        
        # Count vowel groups as syllables
        syllable_count += len(re.findall(r"[aeiouy]+", word))
        
        # Words ending with 'e' often have a silent e
        if word.endswith("e"):
            syllable_count -= 1
        
        # Every word has at least one syllable
        if syllable_count <= 0:
            syllable_count = 1
    
    # Avoid division by zero
    if sentence_count == 0 or word_count == 0:
        return 0.0
    
    # Calculate Flesch Reading Ease score
    words_per_sentence = word_count / sentence_count
    syllables_per_word = syllable_count / word_count
    
    score = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
    
    # Clamp score to 0-100 range
    return max(0.0, min(100.0, score))