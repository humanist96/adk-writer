"""
Diff utilities for comparing draft and final documents
"""

import difflib
from typing import List, Dict, Tuple, Any
import re
import streamlit as st


def create_diff_html(text1: str, text2: str, label1: str = "초안", label2: str = "최종") -> str:
    """
    Create HTML diff visualization with color coding
    
    Args:
        text1: Original text (draft)
        text2: Modified text (final)
        label1: Label for first text
        label2: Label for second text
    
    Returns:
        HTML string with colored diff
    """
    # Split texts into lines
    lines1 = text1.splitlines(keepends=True)
    lines2 = text2.splitlines(keepends=True)
    
    # Create diff
    diff = difflib.unified_diff(lines1, lines2, fromfile=label1, tofile=label2, lineterm='')
    
    html_lines = []
    html_lines.append('<div style="font-family: monospace; background: #f8f9fa; padding: 1rem; border-radius: 8px;">')
    
    for line in diff:
        if line.startswith('+++'):
            html_lines.append(f'<div style="color: #28a745; font-weight: bold;">📝 {label2}</div>')
        elif line.startswith('---'):
            html_lines.append(f'<div style="color: #dc3545; font-weight: bold;">📄 {label1}</div>')
        elif line.startswith('@@'):
            html_lines.append(f'<div style="color: #6c757d; margin: 0.5rem 0;">{"="*50}</div>')
        elif line.startswith('+'):
            # Added line
            html_lines.append(f'<div style="background: #d4edda; color: #155724; padding: 2px 4px; margin: 1px 0; border-left: 3px solid #28a745;">+ {line[1:]}</div>')
        elif line.startswith('-'):
            # Removed line
            html_lines.append(f'<div style="background: #f8d7da; color: #721c24; padding: 2px 4px; margin: 1px 0; border-left: 3px solid #dc3545;">- {line[1:]}</div>')
        else:
            # Context line
            html_lines.append(f'<div style="color: #495057; padding: 2px 4px; margin: 1px 0;">{line}</div>')
    
    html_lines.append('</div>')
    return ''.join(html_lines)


def create_word_diff(text1: str, text2: str) -> Tuple[str, Dict[str, int]]:
    """
    Create word-level diff with statistics
    
    Returns:
        Tuple of (html_diff, statistics)
    """
    words1 = text1.split()
    words2 = text2.split()
    
    diff = difflib.ndiff(words1, words2)
    
    html_parts = []
    added_count = 0
    removed_count = 0
    changed_count = 0
    
    for item in diff:
        if item.startswith('+ '):
            html_parts.append(f'<span style="background: #d4edda; color: #155724; padding: 2px 4px; border-radius: 3px;">{item[2:]}</span>')
            added_count += 1
        elif item.startswith('- '):
            html_parts.append(f'<span style="background: #f8d7da; color: #721c24; padding: 2px 4px; border-radius: 3px; text-decoration: line-through;">{item[2:]}</span>')
            removed_count += 1
        elif item.startswith('? '):
            continue  # Skip marker lines
        else:
            html_parts.append(item[2:])
    
    stats = {
        'added': added_count,
        'removed': removed_count,
        'total_changes': added_count + removed_count
    }
    
    return ' '.join(html_parts), stats


def extract_modifications(critique: str) -> List[Dict[str, str]]:
    """
    Extract modification reasons from critique
    
    Args:
        critique: Critique text from LoopAgent
    
    Returns:
        List of modifications with reasons
    """
    modifications = []
    
    # Common patterns for critique points
    patterns = [
        r'(?:개선|수정|변경|추가|삭제)(?:사항|점|내용)?\s*[:：]\s*([^.!?]+[.!?])',
        r'(?:Issue|문제점|Problem)\s*[:：]\s*([^.!?]+[.!?])',
        r'(?:Suggestion|제안|추천)\s*[:：]\s*([^.!?]+[.!?])',
        r'\d+\.\s*([^.!?]+[.!?])',  # Numbered list items
        r'[-•]\s*([^.!?]+[.!?])',    # Bullet points
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, critique, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            modification = match.group(1).strip()
            if len(modification) > 10:  # Filter out very short matches
                modifications.append({
                    'type': determine_modification_type(modification),
                    'description': modification,
                    'severity': determine_severity(modification)
                })
    
    # Remove duplicates
    seen = set()
    unique_mods = []
    for mod in modifications:
        if mod['description'] not in seen:
            seen.add(mod['description'])
            unique_mods.append(mod)
    
    return unique_mods


def determine_modification_type(text: str) -> str:
    """Determine the type of modification from text"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['추가', 'add', '포함', 'include']):
        return '추가'
    elif any(word in text_lower for word in ['삭제', 'remove', 'delete', '제거']):
        return '삭제'
    elif any(word in text_lower for word in ['수정', 'modify', 'change', '변경']):
        return '수정'
    elif any(word in text_lower for word in ['개선', 'improve', 'enhance', '향상']):
        return '개선'
    elif any(word in text_lower for word in ['형식', 'format', '구조', 'structure']):
        return '형식'
    else:
        return '기타'


def determine_severity(text: str) -> str:
    """Determine the severity of the modification"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['critical', '중요', '필수', 'must', '반드시']):
        return 'high'
    elif any(word in text_lower for word in ['should', '권장', 'recommend', '추천']):
        return 'medium'
    else:
        return 'low'


def get_modification_icon(mod_type: str) -> str:
    """Get icon for modification type"""
    icons = {
        '추가': '➕',
        '삭제': '➖',
        '수정': '✏️',
        '개선': '⚡',
        '형식': '📐',
        '기타': '📝'
    }
    return icons.get(mod_type, '📝')


def get_severity_color(severity: str) -> str:
    """Get color for severity level"""
    colors = {
        'high': '#dc3545',
        'medium': '#ffc107',
        'low': '#28a745'
    }
    return colors.get(severity, '#6c757d')


def create_modification_summary(modifications: List[Dict[str, str]]) -> str:
    """Create HTML summary of modifications"""
    if not modifications:
        return "<p>수정 사항이 감지되지 않았습니다.</p>"
    
    html = ['<div style="background: white; padding: 1rem; border-radius: 8px; margin: 1rem 0;">']
    html.append('<h4 style="margin-bottom: 1rem;">📋 수정 사항 요약</h4>')
    
    # Group by type
    by_type = {}
    for mod in modifications:
        mod_type = mod['type']
        if mod_type not in by_type:
            by_type[mod_type] = []
        by_type[mod_type].append(mod)
    
    for mod_type, mods in by_type.items():
        icon = get_modification_icon(mod_type)
        html.append(f'<div style="margin: 0.5rem 0;">')
        html.append(f'<strong>{icon} {mod_type} ({len(mods)}건)</strong>')
        html.append('<ul style="margin: 0.25rem 0 0.5rem 1.5rem;">')
        
        for mod in mods[:3]:  # Show max 3 items per type
            color = get_severity_color(mod['severity'])
            html.append(f'<li style="color: {color}; margin: 0.25rem 0;">{mod["description"][:100]}...</li>')
        
        if len(mods) > 3:
            html.append(f'<li style="color: #6c757d; font-style: italic;">... 외 {len(mods) - 3}건</li>')
        
        html.append('</ul>')
        html.append('</div>')
    
    html.append('</div>')
    return ''.join(html)


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two texts"""
    return difflib.SequenceMatcher(None, text1, text2).ratio()


def get_change_statistics(text1: str, text2: str) -> Dict[str, Any]:
    """Get comprehensive statistics about changes"""
    words1 = text1.split()
    words2 = text2.split()
    
    stats = {
        'original_length': len(text1),
        'final_length': len(text2),
        'length_change': len(text2) - len(text1),
        'length_change_percent': ((len(text2) - len(text1)) / len(text1) * 100) if len(text1) > 0 else 0,
        'original_words': len(words1),
        'final_words': len(words2),
        'word_change': len(words2) - len(words1),
        'similarity': calculate_similarity(text1, text2) * 100,
        'sentences_original': len(re.findall(r'[.!?]+', text1)),
        'sentences_final': len(re.findall(r'[.!?]+', text2))
    }
    
    return stats