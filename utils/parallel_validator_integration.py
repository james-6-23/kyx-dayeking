"""
并行验证器集成示例
展示如何在 hajimi_king.py 中集成并行验证系统
"""

import time
from typing import List, Dict, Tuple
from datetime import datetime

from common.Logger import logger
from utils.parallel_validator import ParallelKeyValidator, ValidationResult, get_parallel_validator


def integrate_parallel_validation(keys: List[str]) -> Tuple[List[str], List[str], Dict[str, ValidationResult]]:
    """
    集成并行验证到现有流程
    
    Args:
        keys: 待验证的密钥列表
        
    Returns:
        Tuple[valid_keys, rate_limited_keys, all_results]
    """
    if not keys:
        return [], [], {}
    
    logger.info(f"🚀 Starting parallel validation for {len(keys)} keys...")
    start_time = time.time()
    
    # 获取并行验证器实例
    validator = get_parallel_validator(max_workers=10)
    
    # 执行批量验证
    results = validator.validate_batch(keys)
    
    # 分类结果
    valid_keys = []
    rate_limited_keys = []
    
    for key, result in results.items():
        if result.status == "ok":
            valid_keys.append(key)
            logger.info(f"✅ VALID: {key[:10]}... (response time: {result.response_time:.2f}s)")
        elif result.status == "rate_limited":
            rate_limited_keys.append(key)
            logger.warning(f"⚠️ RATE LIMITED: {key[:10]}... (proxy: {result.proxy_used})")
        elif result.status == "invalid":
            logger.info(f"❌ INVALID: {key[:10]}...")
        else:
            logger.error(f"💥 ERROR: {key[:10]}... - {result.error_message}")
    
    # 计算统计信息
    elapsed_time = time.time() - start_time
    stats = validator.get_stats()
    
    logger.info(f"📊 Parallel validation completed in {elapsed_time:.2f}s")
    logger.info(f"   Total: {len(keys)}, Valid: {len(valid_keys)}, Rate Limited: {len(rate_limited_keys)}")
    logger.info(f"   Average response time: {stats.avg_response_time:.2f}s")
    logger.info(f"   Throughput: {len(keys) / elapsed_time:.2f} keys/second")
    
    # 显示代理统计
    proxy_stats = validator.get_proxy_stats()
    if proxy_stats:
        logger.info("🌐 Proxy performance:")
        for proxy_url, stats in proxy_stats.items():
            logger.info(f"   {proxy_url}: Success rate {stats['success_rate']:.1%} ({stats['success']}/{stats['total']})")
    
    return valid_keys, rate_limited_keys, results


def process_item_with_parallel_validation(item: Dict[str, Any], content: str) -> Tuple[int, int]:
    """
    使用并行验证处理单个文件（替代原有的 process_item 函数）
    
    这个函数展示了如何修改现有的 process_item 函数以使用并行验证
    """
    import re
    from utils.file_manager import file_manager
    
    # 提取密钥
    pattern = r'(AIzaSy[A-Za-z0-9\-_]{33})'
    keys = re.findall(pattern, content)
    
    # 过滤占位符密钥
    filtered_keys = []
    for key in keys:
        context_index = content.find(key)
        if context_index != -1:
            snippet = content[context_index:context_index + 45]
            if "..." in snippet or "YOUR_" in snippet.upper():
                continue
        filtered_keys.append(key)
    
    # 去重
    keys = list(set(filtered_keys))
    
    if not keys:
        return 0, 0
    
    logger.info(f"🔑 Found {len(keys)} suspected key(s), starting parallel validation...")
    
    # 使用并行验证
    valid_keys, rate_limited_keys, results = integrate_parallel_validation(keys)
    
    # 保存结果
    repo_name = item["repository"]["full_name"]
    file_path = item["path"]
    file_url = item["html_url"]
    
    if valid_keys:
        file_manager.save_valid_keys(repo_name, file_path, file_url, valid_keys)
        logger.info(f"💾 Saved {len(valid_keys)} valid key(s)")
    
    if rate_limited_keys:
        file_manager.save_rate_limited_keys(repo_name, file_path, file_url, rate_limited_keys)
        logger.info(f"💾 Saved {len(rate_limited_keys)} rate limited key(s)")
    
    return len(valid_keys), len(rate_limited_keys)


# 异步版本示例
async def process_items_async(items: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    异步处理多个文件的示例
    """
    import asyncio
    from utils.github_client import GitHubClient
    
    all_keys = []
    item_key_map = {}  # 记录每个key来自哪个item
    
    # 收集所有密钥
    for item in items:
        content = GitHubClient.get_file_content(item)
        if not content:
            continue
        
        # 提取密钥
        pattern = r'(AIzaSy[A-Za-z0-9\-_]{33})'
        keys = re.findall(pattern, content)
        
        for key in keys:
            all_keys.append(key)
            if key not in item_key_map:
                item_key_map[key] = []
            item_key_map[key].append(item)
    
    # 去重
    unique_keys = list(set(all_keys))
    
    if not unique_keys:
        return {"valid": [], "rate_limited": []}
    
    logger.info(f"🔑 Found {len(unique_keys)} unique keys from {len(items)} items")
    
    # 创建验证器并异步验证
    validator = ParallelKeyValidator(max_workers=20)  # 更多工作线程
    results = await validator.validate_batch_async(unique_keys)
    
    # 分类结果
    valid_keys = []
    rate_limited_keys = []
    
    for key, result in results.items():
        if result.status == "ok":
            valid_keys.append(key)
        elif result.status == "rate_limited":
            rate_limited_keys.append(key)
    
    # 关闭验证器
    validator.shutdown()
    
    return {
        "valid": valid_keys,
        "rate_limited": rate_limited_keys,
        "results": results,
        "item_map": item_key_map
    }


# 性能对比示例
def performance_comparison_demo():
    """
    展示并行验证与串行验证的性能对比
    """
    import random
    
    # 生成测试密钥
    test_keys = []
    for i in range(50):
        # 混合有效和无效的密钥格式
        if i % 3 == 0:
            key = f"AIzaSy{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_', k=33))}"
        else:
            key = f"AIzaSyINVALID{''.join(random.choices('0123456789', k=27))}"
        test_keys.append(key)
    
    logger.info("=" * 60)
    logger.info("🏁 Performance Comparison: Serial vs Parallel Validation")
    logger.info("=" * 60)
    
    # 串行验证（模拟原有方式）
    logger.info("\n📊 Serial Validation:")
    start_time = time.time()
    serial_results = []
    
    for i, key in enumerate(test_keys):
        # 模拟原有的验证延迟
        time.sleep(random.uniform(0.5, 1.5))
        serial_results.append("ok" if i % 3 == 0 else "invalid")
        if (i + 1) % 10 == 0:
            logger.info(f"   Progress: {i + 1}/{len(test_keys)}")
    
    serial_time = time.time() - start_time
    logger.info(f"   Total time: {serial_time:.2f}s")
    logger.info(f"   Throughput: {len(test_keys) / serial_time:.2f} keys/second")
    
    # 并行验证
    logger.info("\n🚀 Parallel Validation:")
    validator = ParallelKeyValidator(max_workers=10)
    start_time = time.time()
    
    parallel_results = validator.validate_batch(test_keys)
    
    parallel_time = time.time() - start_time
    stats = validator.get_stats()
    
    logger.info(f"   Total time: {parallel_time:.2f}s")
    logger.info(f"   Throughput: {len(test_keys) / parallel_time:.2f} keys/second")
    logger.info(f"   Average response time: {stats.avg_response_time:.2f}s")
    
    # 性能提升
    speedup = serial_time / parallel_time
    logger.info(f"\n🎯 Performance improvement: {speedup:.1f}x faster!")
    logger.info(f"   Time saved: {serial_time - parallel_time:.2f}s")
    
    validator.shutdown()


if __name__ == "__main__":
    # 运行性能对比演示
    performance_comparison_demo()