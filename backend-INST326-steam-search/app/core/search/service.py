"""
Steam Game Search Engine - Search Service
搜索服务类，处理所有搜索逻辑和算法

This module provides search functionality including mock BM25, semantic search,
and fusion ranking algorithms for demonstration purposes.
"""

import re
import random
import math
from typing import List, Dict, Tuple, Optional, Any
import logging

from ...data import GameInfo, SearchResult, GameRepository
from ...config.constants import (
    BM25_TITLE_WEIGHT, BM25_GENRE_WEIGHT, BM25_DESCRIPTION_WEIGHT,
    FUSION_BM25_WEIGHT, FUSION_SEMANTIC_WEIGHT, POPULAR_GENRES
)
from ...utils.text import tokenize_text, clean_search_query, extract_keywords
from ...utils.logging import log_performance_metric, PerformanceTimer

# 配置日志 / Configure logging
logger = logging.getLogger(__name__)


class SearchService:
    """
    搜索服务类，处理所有搜索逻辑
    Search service class handling all search logic and algorithms.
    
    这个类实现了模拟的BM25搜索、语义搜索和融合排序算法。
    This class implements mock BM25 search, semantic search, and fusion ranking algorithms.
    """
    
    def __init__(self, game_repository: GameRepository):
        """
        初始化搜索服务
        Initialize search service with game repository.
        
        Args:
            game_repository (GameRepository): 游戏仓库实例
        """
        self.game_repository = game_repository
        self.bm25_enabled = True
        self.semantic_enabled = True
        self.fusion_enabled = True
        
        # 搜索权重配置 / Search weight configuration
        self.bm25_weight = FUSION_BM25_WEIGHT
        self.semantic_weight = FUSION_SEMANTIC_WEIGHT
        self.title_boost = BM25_TITLE_WEIGHT
        self.genre_boost = BM25_GENRE_WEIGHT
        
        # 搜索统计 / Search statistics
        self.search_count = 0
        self.total_search_time = 0.0
        
        logger.info("SearchService initialized with mock algorithms")
    
    async def initialize(self):
        """
        异步初始化搜索服务
        Asynchronously initialize search service components.
        """
        try:
            # 预加载游戏数据用于搜索索引 / Preload game data for search indexing
            all_games = self.game_repository.get_all_games()
            logger.info(f"SearchService initialized with {len(all_games)} games")
            
        except Exception as e:
            logger.error(f"Failed to initialize SearchService: {str(e)}")
            raise
    
    async def search_games(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> List[SearchResult]:
        """
        执行游戏搜索
        Execute comprehensive game search with multiple algorithms.
        
        Args:
            query (str): 搜索查询字符串
            filters (Optional[Dict[str, Any]]): 过滤条件
            limit (int): 结果数量限制
            
        Returns:
            List[SearchResult]: 搜索结果列表
        """
        with PerformanceTimer("search_games_operation", auto_log=False) as timer:
            try:
                # 清理查询 / Clean query
                clean_query = clean_search_query(query)
                if not clean_query:
                    return []
                
                # 获取所有游戏 / Get all games
                all_games = self.game_repository.get_all_games()
                
                # 执行BM25搜索 / Execute BM25 search
                bm25_results = self._mock_bm25_search(clean_query, all_games)
                
                # 执行语义搜索 / Execute semantic search
                semantic_results = self._mock_semantic_search(clean_query, all_games)
                
                # 融合排序 / Fusion ranking
                fused_results = self._apply_fusion_ranking(bm25_results, semantic_results)
                
                # 应用过滤器 / Apply filters
                if filters:
                    fused_results = self._apply_filters(fused_results, filters)
                
                # 限制结果数量 / Limit results
                final_results = fused_results[:limit]
                
                # 更新统计 / Update statistics
                self.search_count += 1
                if timer.duration:
                    self.total_search_time += timer.duration
                    log_performance_metric("search_games", timer.duration, {
                        'query': clean_query,
                        'results_count': len(final_results),
                        'filters': filters
                    })
                
                logger.info(f"Search completed: query='{clean_query}', results={len(final_results)}")
                return final_results
                
            except Exception as e:
                logger.error(f"Search error: {str(e)}")
                return []
    
    def _mock_bm25_search(self, query: str, games: List[GameInfo]) -> List[Tuple[GameInfo, float]]:
        """
        模拟BM25搜索算法
        Mock BM25 search algorithm with field weighting.
        
        Args:
            query (str): 搜索查询
            games (List[GameInfo]): 游戏列表
            
        Returns:
            List[Tuple[GameInfo, float]]: 游戏和BM25分数的元组列表
        """
        query_tokens = tokenize_text(query)
        if not query_tokens:
            return []
        
        results = []
        
        for game in games:
            score = 0.0
            
            # 标题匹配 / Title matching
            title_tokens = tokenize_text(game.title)
            title_matches = sum(1 for token in query_tokens if token in title_tokens)
            if title_matches > 0:
                score += title_matches * self.title_boost
            
            # 类型匹配 / Genre matching
            genre_text = ' '.join(game.genres).lower()
            genre_matches = sum(1 for token in query_tokens if token in genre_text)
            if genre_matches > 0:
                score += genre_matches * self.genre_boost
            
            # 描述匹配 / Description matching
            description_tokens = tokenize_text(game.description)
            desc_matches = sum(1 for token in query_tokens if token in description_tokens)
            if desc_matches > 0:
                score += desc_matches * BM25_DESCRIPTION_WEIGHT
            
            # 添加随机性以模拟真实BM25 / Add randomness to simulate real BM25
            if score > 0:
                score *= (0.8 + random.random() * 0.4)  # 0.8-1.2倍随机因子
                results.append((game, score))
        
        # 按分数排序 / Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def _mock_semantic_search(self, query: str, games: List[GameInfo]) -> List[Tuple[GameInfo, float]]:
        """
        模拟语义搜索算法
        Mock semantic search algorithm based on genre and description similarity.
        
        Args:
            query (str): 搜索查询
            games (List[GameInfo]): 游戏列表
            
        Returns:
            List[Tuple[GameInfo, float]]: 游戏和语义分数的元组列表
        """
        query_lower = query.lower()
        results = []
        
        for game in games:
            score = 0.0
            
            # 类型语义匹配 / Genre semantic matching
            for genre in game.genres:
                if genre.lower() in query_lower or query_lower in genre.lower():
                    score += 2.0
                
                # 相关类型匹配 / Related genre matching
                related_genres = self._get_related_genres(genre)
                for related in related_genres:
                    if related.lower() in query_lower:
                        score += 1.0
            
            # 描述语义匹配 / Description semantic matching
            description_lower = game.description.lower()
            common_words = set(query_lower.split()) & set(description_lower.split())
            score += len(common_words) * 0.5
            
            # 开发者/发行商匹配 / Developer/Publisher matching
            if game.developer and game.developer.lower() in query_lower:
                score += 1.5
            if game.publisher and game.publisher.lower() in query_lower:
                score += 1.5
            
            # 添加随机性以模拟真实语义搜索 / Add randomness to simulate real semantic search
            if score > 0:
                score *= (0.7 + random.random() * 0.6)  # 0.7-1.3倍随机因子
                results.append((game, score))
        
        # 按分数排序 / Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def _get_related_genres(self, genre: str) -> List[str]:
        """获取相关类型 / Get related genres"""
        genre_relations = {
            'Action': ['Adventure', 'Shooter', 'Fighting'],
            'RPG': ['Adventure', 'Strategy', 'Indie'],
            'Strategy': ['Simulation', 'RPG', 'Turn-based Strategy'],
            'Indie': ['Action', 'Adventure', 'Platformer'],
            'Adventure': ['Action', 'RPG', 'Puzzle'],
            'Simulation': ['Strategy', 'Casual', 'Sports'],
            'Casual': ['Puzzle', 'Simulation', 'Family Friendly'],
            'Multiplayer': ['Action', 'Strategy', 'Sports'],
            'Platformer': ['Action', 'Indie', 'Adventure']
        }
        return genre_relations.get(genre, [])
    
    def _apply_fusion_ranking(
        self,
        bm25_results: List[Tuple[GameInfo, float]],
        semantic_results: List[Tuple[GameInfo, float]]
    ) -> List[SearchResult]:
        """
        应用融合排序算法
        Apply fusion ranking algorithm to combine BM25 and semantic results.
        
        Args:
            bm25_results: BM25搜索结果
            semantic_results: 语义搜索结果
            
        Returns:
            List[SearchResult]: 融合排序后的结果
        """
        # 创建分数字典 / Create score dictionaries
        bm25_scores = {game.game_id: score for game, score in bm25_results}
        semantic_scores = {game.game_id: score for game, score in semantic_results}
        
        # 获取所有游戏ID / Get all game IDs
        all_game_ids = set(bm25_scores.keys()) | set(semantic_scores.keys())
        
        # 计算融合分数 / Calculate fusion scores
        fusion_results = []
        for game_id in all_game_ids:
            bm25_score = bm25_scores.get(game_id, 0.0)
            semantic_score = semantic_scores.get(game_id, 0.0)
            
            # 融合分数计算 / Fusion score calculation
            fusion_score = (bm25_score * self.bm25_weight + 
                          semantic_score * self.semantic_weight)
            
            if fusion_score > 0:
                # 找到对应的游戏对象 / Find corresponding game object
                game = None
                for g, _ in bm25_results + semantic_results:
                    if g.game_id == game_id:
                        game = g
                        break
                
                if game:
                    # 质量加成 / Quality bonus
                    quality_bonus = self._calculate_quality_bonus(game)
                    final_score = fusion_score + quality_bonus
                    
                    search_result = SearchResult(
                        game=game,
                        score=final_score,
                        search_type="fusion"
                    )
                    fusion_results.append(search_result)
        
        # 按分数排序并设置排名 / Sort by score and set rankings
        fusion_results.sort(key=lambda x: x.score, reverse=True)
        for i, result in enumerate(fusion_results):
            result.rank = i + 1
        
        return fusion_results
    
    def _calculate_quality_bonus(self, game: GameInfo) -> float:
        """计算游戏质量加成 / Calculate game quality bonus"""
        bonus = 0.0
        
        # 评价状态加成 / Review status bonus
        review_bonuses = {
            'Overwhelmingly Positive': 2.0,
            'Very Positive': 1.5,
            'Positive': 1.0,
            'Mostly Positive': 0.5,
            'Mixed': 0.0,
            'Mostly Negative': -0.5,
            'Negative': -1.0,
            'Very Negative': -1.5
        }
        bonus += review_bonuses.get(game.review_status, 0.0)
        
        # Steam Deck兼容性加成 / Steam Deck compatibility bonus
        if game.deck_comp:
            bonus += 0.5
        
        # 价格合理性加成 / Price reasonableness bonus
        if game.price == 0.0:  # 免费游戏
            bonus += 0.3
        elif game.price <= 20.0:  # 低价游戏
            bonus += 0.2
        
        return bonus
    
    def _apply_filters(self, results: List[SearchResult], filters: Dict[str, Any]) -> List[SearchResult]:
        """应用搜索过滤器 / Apply search filters"""
        filtered_results = []
        
        for result in results:
            if result.game.matches_filters(filters):
                filtered_results.append(result)
        
        return filtered_results
    
    async def get_search_suggestions(self, prefix: str, limit: int = 10) -> List[str]:
        """
        获取搜索建议
        Get search suggestions based on input prefix.
        
        Args:
            prefix (str): 输入前缀
            limit (int): 建议数量限制
            
        Returns:
            List[str]: 搜索建议列表
        """
        try:
            suggestions = []
            prefix_lower = prefix.lower()
            
            # 获取所有游戏 / Get all games
            all_games = self.game_repository.get_all_games()
            
            # 游戏标题建议 / Game title suggestions
            for game in all_games:
                if prefix_lower in game.title.lower():
                    suggestions.append(game.title)
                    if len(suggestions) >= limit // 2:
                        break
            
            # 类型建议 / Genre suggestions
            for genre in POPULAR_GENRES:
                if prefix_lower in genre.lower() and genre not in suggestions:
                    suggestions.append(genre)
                    if len(suggestions) >= limit:
                        break
            
            # 开发者建议 / Developer suggestions
            developers = set()
            for game in all_games:
                if game.developer and prefix_lower in game.developer.lower():
                    developers.add(game.developer)
            
            for dev in list(developers)[:limit - len(suggestions)]:
                suggestions.append(dev)
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取搜索服务统计信息
        Get search service statistics.
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        avg_search_time = (self.total_search_time / self.search_count 
                          if self.search_count > 0 else 0.0)
        
        return {
            'search_count': self.search_count,
            'total_search_time': round(self.total_search_time, 4),
            'average_search_time': round(avg_search_time, 4),
            'bm25_enabled': self.bm25_enabled,
            'semantic_enabled': self.semantic_enabled,
            'fusion_enabled': self.fusion_enabled,
            'bm25_weight': self.bm25_weight,
            'semantic_weight': self.semantic_weight
        }
    
    async def shutdown(self):
        """关闭搜索服务 / Shutdown search service"""
        logger.info("SearchService shutdown completed")
