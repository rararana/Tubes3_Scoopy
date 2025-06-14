import re
import time
from collections import Counter
from typing import List, Tuple, Dict, Any

from algorithms.boyer_moore import boyer_moore_search
from algorithms.kmp import kmp_search
from algorithms.ahocorasick import aho_corasick_search
from services.database_service import get_applicant_name_by_cv

def _levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def _fuzzy_search(text: str, keyword: str, max_distance: int = 1) -> Dict[str, int]:
    words = re.findall(r'\b\w+\b', text.lower())
    keyword_lower = keyword.lower()
    found_words_counter = Counter()
    for word in words:
        if _levenshtein_distance(word, keyword_lower) <= max_distance:
            found_words_counter[word] += 1
    return dict(found_words_counter)

def _search_with_algorithm(text: str, keyword: str, algorithm: str = 'kmp') -> list:
    if algorithm == 'kmp':
        return kmp_search(text, keyword)
    elif algorithm in ['boyer-moore', 'bm']:
        return boyer_moore_search(text, keyword)
    elif algorithm in ['ahocorasick', 'ac']:
        matches = aho_corasick_search(text, [keyword])
        return [start for pattern, start, end in matches if pattern == keyword]
    return []

def search_keywords(
    keywords_input: str,
    algorithm: str,
    max_results_count: int,
    pattern_files: List[Tuple[str, str]]
) -> Dict[str, Any]:
    if not pattern_files:
        return {"results": [], "exact_time_ms": 0, "fuzzy_time_ms": 0, "cv_count": 0}

    keywords = [kw.strip().lower() for kw in keywords_input.split(',') if kw.strip()]
    if not keywords:
        return {"results": [], "exact_time_ms": 0, "fuzzy_time_ms": 0, "cv_count": len(pattern_files)}

    results = []
    found_keywords_exact = set()

    exact_start_time = time.time()
    for filename, text in pattern_files:
        text_lower = text.lower()
        keyword_results = {}
        total_matches = 0
        for keyword in keywords:
            positions = _search_with_algorithm(text_lower, keyword, algorithm)
            if positions:
                found_keywords_exact.add(keyword)
                if keyword not in keyword_results:
                    keyword_results[keyword] = {'count': 0, 'type': 'exact'}
                keyword_results[keyword]['count'] += len(positions)
                total_matches += len(positions)
        if keyword_results:
            name, role = get_applicant_name_by_cv(filename)
            results.append({"name": name, "role": role, "filename": filename, "total_matches": total_matches, "keyword_details": keyword_results, "match_type": "exact"})
    exact_time_ms = int((time.time() - exact_start_time) * 1000)

    keywords_for_fuzzy = [kw for kw in keywords if kw not in found_keywords_exact]
    fuzzy_time_ms = 0

    if keywords_for_fuzzy:
        fuzzy_start_time = time.time()
        for filename, text in pattern_files:
            text_lower = text.lower()
            all_fuzzy_matches_for_cv = {}
            total_fuzzy_matches_for_cv = 0
            for keyword in keywords_for_fuzzy:
                found_matches = _fuzzy_search(text_lower, keyword)
                if found_matches:
                    for found_word, count in found_matches.items():
                        if found_word == keyword: continue
                        if found_word not in all_fuzzy_matches_for_cv:
                            all_fuzzy_matches_for_cv[found_word] = {'count': 0, 'type': 'fuzzy'}
                        all_fuzzy_matches_for_cv[found_word]['count'] += count
                        total_fuzzy_matches_for_cv += count
            if all_fuzzy_matches_for_cv:
                existing_result = next((r for r in results if r['filename'] == filename), None)
                if existing_result:
                    for word, details in all_fuzzy_matches_for_cv.items():
                        if word in existing_result['keyword_details']:
                            existing_result['keyword_details'][word]['count'] += details['count']
                        else:
                            existing_result['keyword_details'][word] = details
                    existing_result['total_matches'] += total_fuzzy_matches_for_cv
                    existing_result['match_type'] = 'mixed'
                else:
                    name, role = get_applicant_name_by_cv(filename)
                    results.append({"name": name, "role": role, "filename": filename, "total_matches": total_fuzzy_matches_for_cv, "keyword_details": all_fuzzy_matches_for_cv, "match_type": "fuzzy"})
        fuzzy_time_ms = int((time.time() - fuzzy_start_time) * 1000)

    results.sort(key=lambda x: x["total_matches"], reverse=True)
    if max_results_count > 0:
        results = results[:max_results_count]

    return {"results": results, "exact_time_ms": exact_time_ms, "fuzzy_time_ms": fuzzy_time_ms, "cv_count": len(pattern_files)}