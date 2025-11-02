"""
Steam Game Search Engine - Text Processing Utilities
文本处理工具模块

This module provides text processing and normalization utilities.
该模块提供文本处理和标准化工具。
"""

import re
import unicodedata
from typing import List, Optional


def normalize_text(text: str, lowercase: bool = True, remove_accents: bool = False) -> str:
    """
    标准化文本以确保一致的处理
    Normalize text for consistent processing and comparison
    
    Args:
        text: 要标准化的文本
        lowercase: 是否转换为小写
        remove_accents: 是否移除重音符号
        
    Returns:
        str: 标准化的文本字符串
    """
    if not text:
        return ""
    
    # Unicode标准化（NFC形式）/ Unicode normalization (NFC form)
    normalized = unicodedata.normalize('NFC', text)
    
    # 如果需要，转换为小写 / Convert to lowercase if requested
    if lowercase:
        normalized = normalized.lower()
    
    # 如果需要，移除重音符号 / Remove accent marks if requested
    if remove_accents:
        normalized = _remove_accent_marks(normalized)
    
    # 标准化空白字符 / Normalize whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # 移除前导/尾随空白字符 / Remove leading/trailing whitespace
    normalized = normalized.strip()
    
    return normalized


def tokenize_text(text: str, language: str = "english", min_length: int = 2) -> List[str]:
    """
    将文本分词为标记列表
    Tokenize text into a list of tokens for search indexing
    
    Args:
        text: 要分词的文本
        language: 语言（用于词干提取）
        min_length: 最小词长度
        
    Returns:
        List[str]: 分词后的标记列表
    """
    if not text:
        return []
    
    # 标准化文本 / Normalize text
    normalized = normalize_text(text, lowercase=True)
    
    # 使用正则表达式分词 / Tokenize using regex
    tokens = re.findall(r'\b[a-zA-Z]+\b', normalized)
    
    # 过滤短词和停用词 / Filter short words and stop words
    filtered_tokens = []
    stop_words = _get_stop_words(language)
    
    for token in tokens:
        if len(token) >= min_length and token not in stop_words:
            # 简单词干提取 / Simple stemming
            stemmed = _stem_word(token, language)
            filtered_tokens.append(stemmed)
    
    return filtered_tokens


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    从文本中提取关键词
    Extract keywords from text for search suggestions
    
    Args:
        text: 输入文本
        max_keywords: 最大关键词数量
        
    Returns:
        List[str]: 关键词列表
    """
    if not text:
        return []
    
    # 分词 / Tokenize
    tokens = tokenize_text(text)
    
    # 计算词频 / Calculate word frequency
    word_freq = {}
    for token in tokens:
        word_freq[token] = word_freq.get(token, 0) + 1
    
    # 按频率排序并返回前N个 / Sort by frequency and return top N
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, freq in sorted_words[:max_keywords]]
    
    return keywords


def clean_search_query(query: str) -> str:
    """
    清理搜索查询字符串
    Clean search query string for processing
    
    Args:
        query: 原始搜索查询
        
    Returns:
        str: 清理后的查询字符串
    """
    if not query:
        return ""
    
    # 标准化文本 / Normalize text
    cleaned = normalize_text(query, lowercase=True)
    
    # 移除特殊字符但保留空格和连字符 / Remove special chars but keep spaces and hyphens
    cleaned = re.sub(r'[^\w\s\-]', ' ', cleaned)
    
    # 标准化空白字符 / Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()


def highlight_matches(text: str, query: str, highlight_tag: str = "mark") -> str:
    """
    在文本中高亮匹配的查询词
    Highlight matching query terms in text
    
    Args:
        text: 要高亮的文本
        query: 搜索查询
        highlight_tag: HTML标签名称
        
    Returns:
        str: 带高亮标记的文本
    """
    if not text or not query:
        return text
    
    # 分词查询 / Tokenize query
    query_tokens = tokenize_text(query)
    
    highlighted = text
    for token in query_tokens:
        if len(token) >= 2:  # 只高亮长度>=2的词
            pattern = re.compile(re.escape(token), re.IGNORECASE)
            highlighted = pattern.sub(
                f'<{highlight_tag}>\\g<0></{highlight_tag}>', 
                highlighted
            )
    
    return highlighted


def _remove_accent_marks(text: str) -> str:
    """移除重音符号的内部函数 / Internal function to remove accent marks"""
    return ''.join(
        char for char in unicodedata.normalize('NFD', text)
        if unicodedata.category(char) != 'Mn'
    )


def _get_stop_words(language: str) -> set:
    """获取停用词列表 / Get stop words list"""
    if language == "english":
        return {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'you', 'your', 'this', 'but', 'they',
            'have', 'had', 'what', 'said', 'each', 'which', 'their', 'time',
            'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some',
            'her', 'would', 'make', 'like', 'into', 'him', 'has', 'two',
            'more', 'very', 'after', 'words', 'long', 'than', 'first', 'been',
            'call', 'who', 'oil', 'sit', 'now', 'find', 'down', 'day', 'did',
            'get', 'come', 'made', 'may', 'part'
        }
    return set()


def _stem_word(word: str, language: str) -> str:
    """常见后缀的简单词干提取 / Simple stemming for common suffixes"""
    if language == "english":
        # 移除常见后缀 / Remove common suffixes
        suffixes = ['ing', 'ed', 'er', 'est', 'ly', 's']
        for suffix in suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
    return word
