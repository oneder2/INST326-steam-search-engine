#!/usr/bin/env python3
"""
Steam Game Search Engine - Project Structure Display
显示项目结构的脚本

This script displays the current modular project structure.
"""

import os
from pathlib import Path

def display_tree(directory: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0):
    """
    显示目录树结构
    Display directory tree structure
    """
    if current_depth > max_depth:
        return
    
    items = sorted([item for item in directory.iterdir() 
                   if not item.name.startswith('.') and item.name != '__pycache__'])
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item.name}")
        
        if item.is_dir() and current_depth < max_depth:
            extension = "    " if is_last else "│   "
            display_tree(item, prefix + extension, max_depth, current_depth + 1)

def main():
    """主函数 / Main function"""
    print("🏗️  Steam Game Search Engine - Modular Architecture")
    print("=" * 60)
    print()
    
    # 获取项目根目录 / Get project root directory
    project_root = Path(__file__).parent.parent
    
    print("📁 Current Project Structure / 当前项目结构:")
    print()
    display_tree(project_root, max_depth=3)
    
    print()
    print("=" * 60)
    print("✅ Modular architecture successfully implemented!")
    print("✅ 模块化架构成功实现！")
    print()
    
    # 显示关键目录说明 / Show key directory descriptions
    print("📋 Key Directories / 关键目录说明:")
    print()
    print("├── app/                    # 应用核心代码 / Application core")
    print("│   ├── api/               # API层 / API layer")
    print("│   ├── core/              # 核心业务逻辑 / Core business logic")
    print("│   ├── data/              # 数据访问层 / Data access layer")
    print("│   ├── utils/             # 工具函数 / Utility functions")
    print("│   └── config/            # 配置管理 / Configuration")
    print("├── tests/                 # 测试代码 / Test code")
    print("├── docs/                  # 文档 / Documentation")
    print("├── scripts/               # 脚本工具 / Scripts")
    print("└── requirements/          # 依赖管理 / Dependencies")
    print()
    
    # 显示运行命令 / Show run commands
    print("🚀 How to Run / 如何运行:")
    print()
    print("# Start server / 启动服务器:")
    print("python3 main.py")
    print("# 或 / Or:")
    print("python3 -m app.main")
    print()
    print("# Run tests / 运行测试:")
    print("python3 tests/test_restructured_api.py")
    print()
    print("# Show this structure / 显示项目结构:")
    print("python3 scripts/show_structure.py")
    print()
    print("# Deploy to Render / 部署到Render:")
    print("# 1. Push to GitHub / 推送到GitHub")
    print("# 2. Connect repository in Render dashboard / 在Render控制台连接仓库")
    print("# 3. Use render.yaml configuration / 使用render.yaml配置")

if __name__ == "__main__":
    main()
