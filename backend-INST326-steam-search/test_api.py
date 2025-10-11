#!/usr/bin/env python3
"""
Steam Game Search Engine - API测试脚本
API Testing Script for the FastAPI backend

This script tests the main API endpoints to ensure they work correctly.
用于测试主要API端点以确保其正常工作
"""

import asyncio
import httpx
import json
import sys
from typing import Dict, Any


class APITester:
    """API测试类 / API Testing Class"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化API测试器
        Initialize API tester with base URL.
        
        Args:
            base_url (str): API基础URL
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.client.aclose()
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """
        记录测试结果
        Log test result.
        
        Args:
            test_name (str): 测试名称
            success (bool): 是否成功
            details (str): 详细信息
        """
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    async def test_health_check(self):
        """测试健康检查端点 / Test health check endpoint"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/health")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                services = data.get("services", {})
                
                self.log_test(
                    "Health Check", 
                    True, 
                    f"Status: {status}, Services: {len(services)}"
                )
                return True
            else:
                self.log_test(
                    "Health Check", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False
    
    async def test_search_games(self):
        """测试游戏搜索端点 / Test game search endpoint"""
        try:
            search_data = {
                "query": "action games",
                "limit": 5,
                "offset": 0
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/search/games",
                json=search_data
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                total = data.get("total", 0)
                
                self.log_test(
                    "Search Games", 
                    True, 
                    f"Found {len(results)} results (total: {total})"
                )
                return True
            else:
                self.log_test(
                    "Search Games", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Search Games", False, f"Exception: {str(e)}")
            return False
    
    async def test_search_suggestions(self):
        """测试搜索建议端点 / Test search suggestions endpoint"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/search/suggest?prefix=action"
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get("suggestions", [])
                prefix = data.get("prefix", "")
                
                self.log_test(
                    "Search Suggestions", 
                    True, 
                    f"Generated {len(suggestions)} suggestions for '{prefix}'"
                )
                return True
            else:
                self.log_test(
                    "Search Suggestions", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Search Suggestions", False, f"Exception: {str(e)}")
            return False
    
    async def test_game_details(self):
        """测试游戏详情端点 / Test game details endpoint"""
        try:
            # 测试一个可能存在的游戏ID / Test a potentially existing game ID
            game_id = 1
            response = await self.client.get(
                f"{self.base_url}/api/v1/games/{game_id}"
            )
            
            if response.status_code == 200:
                data = response.json()
                title = data.get("title", "Unknown")
                
                self.log_test(
                    "Game Details", 
                    True, 
                    f"Retrieved details for game: {title}"
                )
                return True
            elif response.status_code == 404:
                self.log_test(
                    "Game Details", 
                    True, 
                    "Game not found (expected for test ID)"
                )
                return True
            else:
                self.log_test(
                    "Game Details", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Game Details", False, f"Exception: {str(e)}")
            return False
    
    async def test_root_endpoint(self):
        """测试根端点 / Test root endpoint"""
        try:
            response = await self.client.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                self.log_test(
                    "Root Endpoint", 
                    True, 
                    f"Message: {message}"
                )
                return True
            else:
                self.log_test(
                    "Root Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """
        运行所有测试
        Run all API tests.
        
        Returns:
            bool: 所有测试是否通过
        """
        print(f"🧪 Starting API tests for {self.base_url}")
        print("=" * 50)
        
        # 运行所有测试 / Run all tests
        tests = [
            self.test_root_endpoint(),
            self.test_health_check(),
            self.test_search_games(),
            self.test_search_suggestions(),
            self.test_game_details()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # 统计结果 / Count results
        passed = sum(1 for result in results if result is True)
        total = len(results)
        
        print("=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed. Check the details above.")
            return False
    
    def print_summary(self):
        """打印测试摘要 / Print test summary"""
        print("\n📋 Test Summary:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}")


async def main():
    """主函数 / Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Steam Game Search API")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    async with APITester(args.url) as tester:
        success = await tester.run_all_tests()
        tester.print_summary()
        
        # 退出码 / Exit code
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
