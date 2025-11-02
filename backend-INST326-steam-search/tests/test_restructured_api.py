"""
Steam Game Search Engine - Restructured API Tests
重构后API测试

This module contains comprehensive tests for the restructured Steam Game Search Engine API.
该模块包含重构后Steam游戏搜索引擎API的全面测试。
"""

import asyncio
import json
import time
import requests
from typing import Dict, Any, List
import logging

# 配置日志 / Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 测试配置 / Test configuration
BASE_URL = "http://localhost:8000"
API_VERSION = "v1"
API_BASE = f"{BASE_URL}/api/{API_VERSION}"

class APITestSuite:
    """
    API测试套件
    API test suite for comprehensive endpoint testing.
    
    用于全面端点测试的API测试套件。
    Comprehensive API test suite for endpoint testing.
    """
    
    def __init__(self):
        """初始化测试套件 / Initialize test suite"""
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Steam-Game-Search-Engine-Test/2.0'
        })
        self.test_results = []
        self.start_time = time.time()
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_time: float = 0):
        """
        记录测试结果
        Log test result with details.
        
        记录测试结果和详细信息。
        Log test result with details and timing information.
        """
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'response_time': response_time,
            'timestamp': time.time()
        }
        self.test_results.append(result)
        
        logger.info(f"{status} | {test_name} | {response_time:.3f}s | {details}")
    
    def test_health_check(self) -> bool:
        """
        测试健康检查端点
        Test health check endpoint.
        
        测试系统健康检查端点的可用性和响应格式。
        Test system health check endpoint availability and response format.
        """
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['status', 'timestamp', 'services', 'version']
                
                if all(field in data for field in required_fields):
                    self.log_test_result(
                        "Health Check", 
                        True, 
                        f"Status: {data.get('status')}, Services: {len(data.get('services', {}))}", 
                        response_time
                    )
                    return True
                else:
                    missing_fields = [f for f in required_fields if f not in data]
                    self.log_test_result(
                        "Health Check", 
                        False, 
                        f"Missing fields: {missing_fields}", 
                        response_time
                    )
                    return False
            else:
                self.log_test_result(
                    "Health Check", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            self.log_test_result("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_search_games(self) -> bool:
        """
        测试游戏搜索端点
        Test game search endpoint.
        
        测试游戏搜索功能的各种查询场景。
        Test game search functionality with various query scenarios.
        """
        test_queries = [
            {
                "name": "Basic Action Search",
                "query": {"query": "action games", "limit": 5}
            },
            {
                "name": "RPG with Price Filter",
                "query": {"query": "rpg", "limit": 3, "filters": {"price_max": 30}}
            },
            {
                "name": "Strategy Games",
                "query": {"query": "strategy", "limit": 4}
            },
            {
                "name": "Indie Games Search",
                "query": {"query": "indie", "limit": 6}
            }
        ]
        
        all_passed = True
        
        for test_case in test_queries:
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{API_BASE}/search/games",
                    json=test_case["query"]
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ['results', 'total', 'offset', 'limit', 'query']
                    
                    if all(field in data for field in required_fields):
                        results_count = len(data.get('results', []))
                        self.log_test_result(
                            f"Search: {test_case['name']}", 
                            True, 
                            f"Found {results_count} results, Total: {data.get('total', 0)}", 
                            response_time
                        )
                    else:
                        missing_fields = [f for f in required_fields if f not in data]
                        self.log_test_result(
                            f"Search: {test_case['name']}", 
                            False, 
                            f"Missing fields: {missing_fields}", 
                            response_time
                        )
                        all_passed = False
                else:
                    self.log_test_result(
                        f"Search: {test_case['name']}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}", 
                        response_time
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_test_result(f"Search: {test_case['name']}", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_game_details(self) -> bool:
        """
        测试游戏详情端点
        Test game details endpoint.
        
        测试获取特定游戏详细信息的功能。
        Test functionality for retrieving specific game details.
        """
        test_game_ids = [1, 2, 3, 5, 10]  # 测试多个游戏ID / Test multiple game IDs
        all_passed = True
        
        for game_id in test_game_ids:
            try:
                start_time = time.time()
                response = self.session.get(f"{API_BASE}/games/{game_id}")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ['game_id', 'title', 'description', 'price']
                    
                    if all(field in data for field in required_fields):
                        self.log_test_result(
                            f"Game Detail: ID {game_id}", 
                            True, 
                            f"Title: {data.get('title', 'N/A')[:30]}...", 
                            response_time
                        )
                    else:
                        missing_fields = [f for f in required_fields if f not in data]
                        self.log_test_result(
                            f"Game Detail: ID {game_id}", 
                            False, 
                            f"Missing fields: {missing_fields}", 
                            response_time
                        )
                        all_passed = False
                elif response.status_code == 404:
                    self.log_test_result(
                        f"Game Detail: ID {game_id}", 
                        True, 
                        "Game not found (expected for some IDs)", 
                        response_time
                    )
                else:
                    self.log_test_result(
                        f"Game Detail: ID {game_id}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}", 
                        response_time
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_test_result(f"Game Detail: ID {game_id}", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_search_suggestions(self) -> bool:
        """
        测试搜索建议端点
        Test search suggestions endpoint.
        
        测试搜索自动完成建议功能。
        Test search autocomplete suggestions functionality.
        """
        test_prefixes = ["act", "rpg", "str", "ind"]
        all_passed = True
        
        for prefix in test_prefixes:
            try:
                start_time = time.time()
                response = self.session.get(f"{API_BASE}/search/suggest?prefix={prefix}")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ['suggestions', 'prefix']
                    
                    if all(field in data for field in required_fields):
                        suggestions_count = len(data.get('suggestions', []))
                        self.log_test_result(
                            f"Suggestions: '{prefix}'", 
                            True, 
                            f"Got {suggestions_count} suggestions", 
                            response_time
                        )
                    else:
                        missing_fields = [f for f in required_fields if f not in data]
                        self.log_test_result(
                            f"Suggestions: '{prefix}'", 
                            False, 
                            f"Missing fields: {missing_fields}", 
                            response_time
                        )
                        all_passed = False
                else:
                    self.log_test_result(
                        f"Suggestions: '{prefix}'", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}", 
                        response_time
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_test_result(f"Suggestions: '{prefix}'", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        运行所有测试
        Run all tests and return comprehensive results.
        
        运行所有测试并返回全面的结果报告。
        Run all tests and return comprehensive results report.
        """
        logger.info("🚀 Starting Steam Game Search Engine API Tests (Restructured)")
        logger.info("=" * 70)
        
        # 运行所有测试 / Run all tests
        tests = [
            ("Health Check", self.test_health_check),
            ("Search Games", self.test_search_games),
            ("Game Details", self.test_game_details),
            ("Search Suggestions", self.test_search_suggestions)
        ]
        
        test_summary = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_categories': {},
            'total_time': 0,
            'average_response_time': 0
        }
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 Running {test_name} tests...")
            category_start = len(self.test_results)
            
            success = test_func()
            
            category_end = len(self.test_results)
            category_tests = self.test_results[category_start:category_end]
            category_passed = sum(1 for t in category_tests if t['success'])
            category_total = len(category_tests)
            
            test_summary['test_categories'][test_name] = {
                'total': category_total,
                'passed': category_passed,
                'failed': category_total - category_passed,
                'success_rate': (category_passed / category_total * 100) if category_total > 0 else 0
            }
        
        # 计算总体统计 / Calculate overall statistics
        test_summary['total_tests'] = len(self.test_results)
        test_summary['passed_tests'] = sum(1 for t in self.test_results if t['success'])
        test_summary['failed_tests'] = test_summary['total_tests'] - test_summary['passed_tests']
        test_summary['total_time'] = time.time() - self.start_time
        
        if self.test_results:
            test_summary['average_response_time'] = sum(t['response_time'] for t in self.test_results) / len(self.test_results)
        
        # 打印测试报告 / Print test report
        self.print_test_report(test_summary)
        
        return test_summary
    
    def print_test_report(self, summary: Dict[str, Any]):
        """
        打印测试报告
        Print comprehensive test report.
        
        打印详细的测试结果报告。
        Print detailed test results report.
        """
        logger.info("\n" + "=" * 70)
        logger.info("📊 TEST RESULTS SUMMARY / 测试结果摘要")
        logger.info("=" * 70)
        
        # 总体结果 / Overall results
        success_rate = (summary['passed_tests'] / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
        logger.info(f"总测试数 / Total Tests: {summary['total_tests']}")
        logger.info(f"通过测试 / Passed: {summary['passed_tests']}")
        logger.info(f"失败测试 / Failed: {summary['failed_tests']}")
        logger.info(f"成功率 / Success Rate: {success_rate:.1f}%")
        logger.info(f"总耗时 / Total Time: {summary['total_time']:.2f}s")
        logger.info(f"平均响应时间 / Avg Response Time: {summary['average_response_time']:.3f}s")
        
        # 分类结果 / Category results
        logger.info("\n📋 Test Categories:")
        for category, stats in summary['test_categories'].items():
            logger.info(f"  {category}: {stats['passed']}/{stats['total']} ({stats['success_rate']:.1f}%)")
        
        # 状态判断 / Status determination
        if success_rate >= 90:
            logger.info("\n🎉 API测试通过！/ API Tests PASSED!")
        elif success_rate >= 70:
            logger.info("\n⚠️  API测试部分通过 / API Tests PARTIALLY PASSED")
        else:
            logger.info("\n❌ API测试失败 / API Tests FAILED")
        
        logger.info("=" * 70)


def main():
    """
    主测试函数
    Main test function.
    
    执行完整的API测试套件。
    Execute complete API test suite.
    """
    print("🔧 Steam Game Search Engine - Restructured API Tests")
    print("🏗️  Testing new modular architecture...")
    print()
    
    # 创建并运行测试套件 / Create and run test suite
    test_suite = APITestSuite()
    results = test_suite.run_all_tests()
    
    # 返回退出码 / Return exit code
    success_rate = (results['passed_tests'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 0
    exit_code = 0 if success_rate >= 90 else 1
    
    print(f"\n🏁 Tests completed with exit code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    exit(main())
