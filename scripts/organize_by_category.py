#!/usr/bin/env python3
"""
将函数文档按分类组织到对应的文件夹

Usage: python3 organize_by_category.py
"""

import os
import re
import shutil
from pathlib import Path

# 目录配置
BACKEND_DIR = Path("docs/functions/backend")

# 分类映射
CATEGORY_MAPPING = {
    "API Endpoint": "api-endpoints",
    "Search Algorithm": "search-algorithms",
    "Data Access": "data-access",
    "Validation": "validation",
}

def get_category_from_file(file_path: Path) -> str:
    """从 markdown 文件中提取分类信息"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找 Category: 行
        match = re.search(r'\*\*Category:\*\*\s+(.+?)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        return None
    except Exception as e:
        print(f"  ❌ 读取文件失败 {file_path}: {e}")
        return None

def move_files_to_categories():
    """将文件移动到对应的分类文件夹"""
    print("=" * 60)
    print("按分类组织函数文档")
    print("=" * 60)
    
    # 统计
    moved_count = 0
    skipped_count = 0
    
    # 遍历所有 .md 文件
    for md_file in BACKEND_DIR.glob("*.md"):
        # 跳过 README.md
        if md_file.name == "README.md":
            print(f"\n⏭️  跳过: {md_file.name}")
            skipped_count += 1
            continue
        
        # 获取分类
        category = get_category_from_file(md_file)
        
        if not category:
            print(f"\n⚠️  未找到分类: {md_file.name}")
            skipped_count += 1
            continue
        
        # 获取目标文件夹
        target_folder = CATEGORY_MAPPING.get(category)
        
        if not target_folder:
            print(f"\n⚠️  未知分类 '{category}': {md_file.name}")
            skipped_count += 1
            continue
        
        # 创建目标目录
        target_dir = BACKEND_DIR / target_folder
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 移动文件
        target_path = target_dir / md_file.name
        
        print(f"\n📦 {md_file.name}")
        print(f"   分类: {category}")
        print(f"   目标: {target_folder}/")
        
        shutil.move(str(md_file), str(target_path))
        moved_count += 1
        print(f"   ✅ 已移动")
    
    print("\n" + "=" * 60)
    print(f"✅ 移动完成: {moved_count} 个文件")
    print(f"⏭️  跳过: {skipped_count} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    move_files_to_categories()

