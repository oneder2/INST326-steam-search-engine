"""
Steam Game Search Engine - Search Algorithms Module
搜索算法模块，实现BM25关键词搜索和Faiss语义搜索

This module implements the core search functionality including BM25 keyword search,
Faiss semantic search, and fusion ranking algorithms.
"""

import os
import json
import pickle
import numpy as np
import faiss
from typing import List, Dict, Tuple, Optional, Any
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import logging
import re
from config import get_settings
from database import GameInfo

# 配置日志 / Configure logging
logger = logging.getLogger(__name__)
settings = get_settings()

# 全局变量用于存储加载的索引 / Global variables for loaded indices
bm25_index: Optional[BM25Okapi] = None
game_corpus: Optional[List[Dict]] = None
faiss_index: Optional[faiss.Index] = None
game_id_mapping: Optional[Dict[int, int]] = None
embedding_model: Optional[SentenceTransformer] = None


def validate_search_query(query: str) -> str:
    """
    验证和清理搜索查询
    Validate and sanitize search query input to prevent malicious patterns.
    
    Args:
        query (str): 原始搜索查询
        
    Returns:
        str: 清理后的查询字符串
        
    Raises:
        ValueError: 如果查询无效
    """
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")
    
    # 移除多余空格 / Remove extra whitespace
    clean_query = re.sub(r'\s+', ' ', query.strip())
    
    # 检查查询长度 / Check query length
    if len(clean_query) > 200:
        raise ValueError("Search query too long (max 200 characters)")
    
    # 检查恶意模式 / Check for malicious patterns
    malicious_patterns = [
        r'<script.*?>.*?</script>',  # XSS scripts
        r'javascript:',              # JavaScript URLs
        r'data:text/html',          # Data URLs
        r'vbscript:',               # VBScript
    ]
    
    for pattern in malicious_patterns:
        if re.search(pattern, clean_query, re.IGNORECASE):
            raise ValueError("Invalid characters in search query")
    
    logger.info(f"Validated search query: '{clean_query}'")
    return clean_query


def tokenize_text(text: str) -> List[str]:
    """
    文本分词函数
    Tokenize text for BM25 indexing with proper preprocessing.
    
    Args:
        text (str): 要分词的文本
        
    Returns:
        List[str]: 分词结果列表
    """
    if not text:
        return []
    
    # 转换为小写并移除特殊字符 / Convert to lowercase and remove special characters
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # 分词并过滤空字符串 / Split and filter empty strings
    tokens = [token for token in text.split() if token and len(token) > 1]
    
    return tokens


def load_bm25_index() -> Tuple[BM25Okapi, List[Dict]]:
    """
    加载BM25搜索索引
    Load and initialize the BM25 search index from preprocessed game data.
    
    Returns:
        Tuple[BM25Okapi, List[Dict]]: BM25索引和游戏语料库
        
    Raises:
        FileNotFoundError: 如果索引文件不存在
        Exception: 如果加载失败
    """
    global bm25_index, game_corpus
    
    try:
        # 尝试加载预构建的索引 / Try to load pre-built index
        if os.path.exists(settings.bm25_index_path):
            logger.info("Loading pre-built BM25 index...")
            with open(settings.bm25_index_path, 'rb') as f:
                index_data = pickle.load(f)
                bm25_index = index_data['index']
                game_corpus = index_data['corpus']
                logger.info(f"BM25 index loaded with {len(game_corpus)} documents")
                return bm25_index, game_corpus
        
        # 如果没有预构建索引，从数据库构建 / Build from database if no pre-built index
        logger.warning("No pre-built BM25 index found. This would normally build from database.")
        logger.warning("For now, returning empty index. TODO: Implement database-based index building.")
        
        # TODO: 实现从数据库构建索引的逻辑
        # TODO: Implement database-based index building logic
        bm25_index = BM25Okapi([])  # Empty index for now
        game_corpus = []
        
        return bm25_index, game_corpus
        
    except Exception as e:
        logger.error(f"Failed to load BM25 index: {str(e)}")
        raise


def load_faiss_index() -> Tuple[faiss.Index, Dict[int, int], SentenceTransformer]:
    """
    加载Faiss向量搜索索引
    Load the Faiss vector similarity search index and associated game ID mappings.
    
    Returns:
        Tuple[faiss.Index, Dict[int, int], SentenceTransformer]: Faiss索引、游戏ID映射和嵌入模型
        
    Raises:
        FileNotFoundError: 如果索引文件不存在
        Exception: 如果加载失败
    """
    global faiss_index, game_id_mapping, embedding_model
    
    try:
        # 加载Faiss索引 / Load Faiss index
        if not os.path.exists(settings.faiss_index_path):
            logger.warning(f"Faiss index not found at {settings.faiss_index_path}")
            logger.warning("Creating empty index. TODO: Implement index building.")
            
            # TODO: 创建空索引用于开发 / TODO: Create empty index for development
            dimension = 384  # all-MiniLM-L6-v2 embedding dimension
            faiss_index = faiss.IndexFlatIP(dimension)  # Inner product index
            game_id_mapping = {}
        else:
            logger.info("Loading Faiss index...")
            faiss_index = faiss.read_index(settings.faiss_index_path)
            
            # 加载游戏ID映射 / Load game ID mapping
            mapping_path = settings.game_id_mapping_path
            if os.path.exists(mapping_path):
                with open(mapping_path, 'r') as f:
                    raw_mapping = json.load(f)
                    # 转换字符串键为整数 / Convert string keys to integers
                    game_id_mapping = {int(k): v for k, v in raw_mapping.items()}
            else:
                logger.warning(f"Game ID mapping not found at {mapping_path}")
                game_id_mapping = {}
        
        # 加载嵌入模型 / Load embedding model
        logger.info("Loading sentence transformer model...")
        embedding_model = SentenceTransformer(settings.embedding_model)
        
        # 验证索引完整性 / Verify index integrity
        _verify_faiss_index(faiss_index, game_id_mapping)
        
        logger.info(f"Faiss index loaded: {faiss_index.ntotal} vectors, dimension {faiss_index.d}")
        
        return faiss_index, game_id_mapping, embedding_model
        
    except Exception as e:
        logger.error(f"Failed to load Faiss index: {str(e)}")
        raise


def _verify_faiss_index(index: faiss.Index, mapping: Dict[int, int]) -> None:
    """
    验证Faiss索引完整性
    Verify Faiss index integrity and functionality.
    
    Args:
        index (faiss.Index): Faiss索引
        mapping (Dict[int, int]): 游戏ID映射
        
    Raises:
        ValueError: 如果索引验证失败
    """
    try:
        # 检查索引是否已训练（对于IVF索引） / Check if index is trained (for IVF indices)
        if hasattr(index, 'is_trained') and not index.is_trained:
            raise ValueError("Faiss index is not trained")
        
        # 验证映射大小 / Verify mapping size
        if len(mapping) != index.ntotal and index.ntotal > 0:
            logger.warning(
                f"Mapping size ({len(mapping)}) doesn't match index size ({index.ntotal})"
            )
        
        # 测试搜索功能 / Test search functionality
        if index.ntotal > 0:
            test_vector = np.random.random((1, index.d)).astype(np.float32)
            distances, indices = index.search(test_vector, min(5, index.ntotal))
            
            if len(indices[0]) == 0:
                raise ValueError("Faiss index search returned no results")
        
        logger.info("Faiss index verification passed")
        
    except Exception as e:
        logger.error(f"Faiss index verification failed: {str(e)}")
        raise


async def search_bm25_index(query: str, limit: int = 50) -> List[Tuple[int, float]]:
    """
    使用BM25算法进行关键词搜索
    Perform BM25 keyword search on the game corpus.
    
    Args:
        query (str): 搜索查询
        limit (int): 结果数量限制
        
    Returns:
        List[Tuple[int, float]]: (游戏ID, BM25分数) 的列表
    """
    global bm25_index, game_corpus
    
    if not bm25_index or not game_corpus:
        logger.warning("BM25 index not loaded")
        return []
    
    try:
        # 分词查询 / Tokenize query
        query_tokens = tokenize_text(query)
        if not query_tokens:
            return []
        
        # 获取BM25分数 / Get BM25 scores
        scores = bm25_index.get_scores(query_tokens)
        
        # 创建(游戏ID, 分数)对并排序 / Create (game_id, score) pairs and sort
        game_scores = []
        for i, score in enumerate(scores):
            if i < len(game_corpus) and score > 0:
                game_id = game_corpus[i].get('game_id', 0)
                game_scores.append((game_id, float(score)))
        
        # 按分数降序排序 / Sort by score descending
        game_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前N个结果 / Return top N results
        results = game_scores[:limit]
        logger.info(f"BM25 search returned {len(results)} results for query: '{query}'")
        
        return results
        
    except Exception as e:
        logger.error(f"BM25 search error: {str(e)}")
        return []


async def search_faiss_index(query: str, limit: int = 50) -> List[Tuple[int, float]]:
    """
    使用Faiss进行语义搜索
    Perform semantic search using Faiss vector similarity.
    
    Args:
        query (str): 搜索查询
        limit (int): 结果数量限制
        
    Returns:
        List[Tuple[int, float]]: (游戏ID, 相似度分数) 的列表
    """
    global faiss_index, game_id_mapping, embedding_model
    
    if not faiss_index or not embedding_model:
        logger.warning("Faiss index or embedding model not loaded")
        return []
    
    if faiss_index.ntotal == 0:
        logger.warning("Faiss index is empty")
        return []
    
    try:
        # 生成查询嵌入 / Generate query embedding
        query_embedding = embedding_model.encode([query])
        query_vector = query_embedding.astype(np.float32)
        
        # 执行相似度搜索 / Perform similarity search
        distances, indices = faiss_index.search(query_vector, min(limit, faiss_index.ntotal))
        
        # 转换结果为(游戏ID, 分数)格式 / Convert results to (game_id, score) format
        results = []
        for i, (distance, index) in enumerate(zip(distances[0], indices[0])):
            if index != -1 and index in game_id_mapping:
                game_id = game_id_mapping[index]
                # 转换距离为相似度分数 / Convert distance to similarity score
                similarity_score = float(distance)  # For inner product, higher is better
                results.append((game_id, similarity_score))
        
        logger.info(f"Faiss search returned {len(results)} results for query: '{query}'")
        
        return results
        
    except Exception as e:
        logger.error(f"Faiss search error: {str(e)}")
        return []


def merge_search_results(
    bm25_results: List[Tuple[int, float]],
    faiss_results: List[Tuple[int, float]]
) -> List[Tuple[int, float, str]]:
    """
    合并来自多个搜索算法的结果
    Merge results from multiple search algorithms
    """
    try:
        # 标准化分数到0-1范围 / Normalize scores to 0-1 range
        normalized_bm25 = _normalize_scores(bm25_results, "bm25")
        normalized_faiss = _normalize_scores(faiss_results, "faiss")

        # 创建统一结果字典 / Create unified result dictionary
        merged_results = {}

        # 添加BM25结果 / Add BM25 results
        for game_id, score in normalized_bm25:
            merged_results[game_id] = {
                'bm25_score': score,
                'faiss_score': 0.0,
                'sources': ['bm25']
            }

        # 添加Faiss结果 / Add Faiss results
        for game_id, score in normalized_faiss:
            if game_id in merged_results:
                merged_results[game_id]['faiss_score'] = score
                merged_results[game_id]['sources'].append('faiss')
            else:
                merged_results[game_id] = {
                    'bm25_score': 0.0,
                    'faiss_score': score,
                    'sources': ['faiss']
                }

        # 转换为输出格式 / Convert to output format
        final_results = []
        for game_id, data in merged_results.items():
            # 计算初始组合分数 / Calculate initial combined score
            combined_score = _calculate_initial_combined_score(
                data['bm25_score'],
                data['faiss_score']
            )

            source_info = '+'.join(data['sources'])
            final_results.append((game_id, combined_score, source_info))

        # 按组合分数排序 / Sort by combined score
        final_results.sort(key=lambda x: x[1], reverse=True)

        logger.debug(f"Merged {len(bm25_results)} BM25 + {len(faiss_results)} Faiss results "
                    f"into {len(final_results)} unique results")

        return final_results

    except Exception as e:
        logger.error(f"Error merging search results: {str(e)}")
        return []

def apply_fusion_ranking(
    bm25_results: List[Tuple[int, float]],
    faiss_results: List[Tuple[int, float]],
    bm25_weight: float = 0.4,
    faiss_weight: float = 0.6
) -> List[Tuple[int, float]]:
    """
    应用融合排序算法
    Apply fusion ranking algorithm to combine BM25 and Faiss search results.
    
    Args:
        bm25_results (List[Tuple[int, float]]): BM25搜索结果
        faiss_results (List[Tuple[int, float]]): Faiss搜索结果
        bm25_weight (float): BM25权重
        faiss_weight (float): Faiss权重
        
    Returns:
        List[Tuple[int, float]]: 融合排序后的结果
    """
    try:
        # 归一化分数 / Normalize scores
        def normalize_scores(results: List[Tuple[int, float]]) -> Dict[int, float]:
            if not results:
                return {}
            
            scores = [score for _, score in results]
            max_score = max(scores) if scores else 1.0
            min_score = min(scores) if scores else 0.0
            score_range = max_score - min_score if max_score != min_score else 1.0
            
            normalized = {}
            for game_id, score in results:
                normalized_score = (score - min_score) / score_range
                normalized[game_id] = normalized_score
            
            return normalized
        
        # 归一化两个结果集 / Normalize both result sets
        bm25_normalized = normalize_scores(bm25_results)
        faiss_normalized = normalize_scores(faiss_results)
        
        # 合并分数 / Combine scores
        combined_scores = {}
        all_game_ids = set(bm25_normalized.keys()) | set(faiss_normalized.keys())
        
        for game_id in all_game_ids:
            bm25_score = bm25_normalized.get(game_id, 0.0)
            faiss_score = faiss_normalized.get(game_id, 0.0)
            
            # 计算加权融合分数 / Calculate weighted fusion score
            fusion_score = (bm25_weight * bm25_score) + (faiss_weight * faiss_score)
            combined_scores[game_id] = fusion_score
        
        # 按融合分数排序 / Sort by fusion score
        sorted_results = sorted(
            combined_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        logger.info(f"Fusion ranking combined {len(sorted_results)} unique games")
        
        return sorted_results
        
    except Exception as e:
        logger.error(f"Fusion ranking error: {str(e)}")
        # 如果融合失败，返回BM25结果作为后备 / Return BM25 results as fallback
        return bm25_results


def _normalize_scores(results: List[Tuple[int, float]], algorithm: str) -> List[Tuple[int, float]]:
    """
    标准化分数到0-1范围以便公平比较
    Normalize scores to 0-1 range for fair comparison
    """
    if not results:
        return []

    scores = [score for _, score in results]

    if algorithm == "bm25":
        # BM25分数通常是0-∞，使用对数标准化 / BM25 scores are typically 0-∞, use log normalization
        max_score = max(scores)
        if max_score > 0:
            normalized = [
                (game_id, math.log(score + 1) / math.log(max_score + 1))
                for game_id, score in results
            ]
        else:
            normalized = [(game_id, 0.0) for game_id, _ in results]

    elif algorithm == "faiss":
        # Faiss相似度分数通常是0-1，但可能需要反转 / Faiss similarity scores are typically 0-1
        max_score = max(scores)
        min_score = min(scores)

        if max_score > min_score:
            # 标准化到0-1范围 / Normalize to 0-1 range
            normalized = [
                (game_id, (score - min_score) / (max_score - min_score))
                for game_id, score in results
            ]
        else:
            normalized = [(game_id, 1.0) for game_id, _ in results]

    else:
        # 默认最小-最大标准化 / Default min-max normalization
        max_score = max(scores)
        min_score = min(scores)

        if max_score > min_score:
            normalized = [
                (game_id, (score - min_score) / (max_score - min_score))
                for game_id, score in results
            ]
        else:
            normalized = [(game_id, 1.0) for game_id, _ in results]

    return normalized


def _calculate_initial_combined_score(bm25_score: float, faiss_score: float) -> float:
    """
    计算融合排序前的初始组合分数
    Calculate initial combined score before fusion ranking
    """
    # 简单加权平均作为初始组合 / Simple weighted average as initial combination
    bm25_weight = 0.4
    faiss_weight = 0.6

    combined = (bm25_score * bm25_weight) + (faiss_score * faiss_weight)

    # 为两个算法都找到的结果提供共识奖励 / Boost scores for results found by both algorithms
    if bm25_score > 0 and faiss_score > 0:
        # 应用共识奖励 / Apply consensus bonus
        consensus_bonus = 0.1 * min(bm25_score, faiss_score)
        combined += consensus_bonus

    return min(combined, 1.0)  # 确保分数不超过1.0 / Ensure score doesn't exceed 1.0


def check_bm25_index_health() -> bool:
    """
    检查BM25索引健康状态
    Check BM25 index health status.
    
    Returns:
        bool: 索引是否健康
    """
    global bm25_index, game_corpus
    
    try:
        if not bm25_index or not game_corpus:
            return False
        
        # 测试搜索功能 / Test search functionality
        test_query = ["test"]
        scores = bm25_index.get_scores(test_query)
        
        return len(scores) == len(game_corpus)
        
    except Exception:
        return False


def check_faiss_index_health() -> bool:
    """
    检查Faiss索引健康状态
    Check Faiss index health status.
    
    Returns:
        bool: 索引是否健康
    """
    global faiss_index, game_id_mapping
    
    try:
        if not faiss_index or not game_id_mapping:
            return False
        
        # 快速搜索测试 / Quick search test
        if faiss_index.ntotal > 0:
            test_vector = np.random.random((1, faiss_index.d)).astype(np.float32)
            distances, indices = faiss_index.search(test_vector, 1)
            
            return len(indices[0]) > 0 and indices[0][0] != -1
        
        return True  # Empty index is considered healthy
        
    except Exception:
        return False
