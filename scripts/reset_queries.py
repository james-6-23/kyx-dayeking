#!/usr/bin/env python3
"""
重置已处理的查询，允许程序重新扫描所有查询
"""

import json
import os
import sys
from datetime import datetime

def reset_queries(checkpoint_file="data/checkpoint.json"):
    """重置checkpoint中的已处理查询"""
    
    if not os.path.exists(checkpoint_file):
        print(f"❌ 检查点文件不存在: {checkpoint_file}")
        return False
    
    try:
        # 读取现有的checkpoint
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 备份原始数据
        backup_file = f"{checkpoint_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ 已创建备份: {backup_file}")
        
        # 统计信息
        old_queries_count = len(data.get('processed_queries', []))
        old_shas_count = len(data.get('scanned_shas', []))
        
        # 清空已处理的查询
        data['processed_queries'] = []
        
        # 可选：是否也清空已扫描的文件SHA
        if len(sys.argv) > 1 and sys.argv[1] == '--full':
            data['scanned_shas'] = []
            print("🔄 执行完全重置（包括已扫描的文件）")
        else:
            print("🔄 执行查询重置（保留已扫描的文件记录）")
        
        # 保存更新后的checkpoint
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 重置完成！")
        print(f"   - 清除了 {old_queries_count} 个已处理的查询")
        if len(sys.argv) > 1 and sys.argv[1] == '--full':
            print(f"   - 清除了 {old_shas_count} 个已扫描的文件SHA")
        else:
            print(f"   - 保留了 {old_shas_count} 个已扫描的文件SHA")
        
        return True
        
    except Exception as e:
        print(f"❌ 重置失败: {e}")
        return False

def main():
    print("=" * 50)
    print("🔄 Hajimi King 查询重置工具")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("使用方法:")
        print("  python reset_queries.py        # 只重置查询（推荐）")
        print("  python reset_queries.py --full # 完全重置（包括文件SHA）")
        print("")
        print("说明:")
        print("  - 默认模式：只清除已处理的查询，保留已扫描的文件记录")
        print("  - 完全模式：清除所有记录，程序将重新扫描所有内容")
        return
    
    # 检查data目录
    if not os.path.exists("data"):
        print("❌ data目录不存在，请在项目根目录运行此脚本")
        return
    
    reset_queries()
    print("\n✨ 现在可以重新运行 Hajimi King 来扫描所有查询了！")

if __name__ == "__main__":
    main()