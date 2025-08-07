"""
并行验证系统性能测试
对比串行验证和并行验证的性能差异
"""

import sys
import os
import time
import random
import statistics
from datetime import datetime
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.Logger import logger
from common.config import Config
from utils.parallel_validator import ParallelKeyValidator, get_parallel_validator

# 模拟原有的串行验证函数
def validate_gemini_key_serial(api_key: str) -> str:
    """模拟串行验证（原有方式）"""
    # 模拟网络延迟和处理时间
    time.sleep(random.uniform(0.8, 1.2))
    
    # 模拟验证结果（30%有效，10%限流，60%无效）
    rand = random.random()
    if rand < 0.3:
        return "ok"
    elif rand < 0.4:
        return "rate_limited"
    else:
        return "invalid"


def generate_test_keys(count: int) -> List[str]:
    """生成测试用的API密钥"""
    keys = []
    for i in range(count):
        # 生成符合格式的测试密钥
        key = f"AIzaSy{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_', k=33))}"
        keys.append(key)
    return keys


def test_serial_validation(keys: List[str]) -> Tuple[Dict[str, int], float]:
    """测试串行验证性能"""
    logger.info("🔄 开始串行验证测试...")
    start_time = time.time()
    
    results = {
        "ok": 0,
        "invalid": 0,
        "rate_limited": 0
    }
    
    for i, key in enumerate(keys):
        result = validate_gemini_key_serial(key)
        results[result] = results.get(result, 0) + 1
        
        # 显示进度
        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed
            logger.info(f"   进度: {i + 1}/{len(keys)} | 速率: {rate:.2f} keys/s")
    
    total_time = time.time() - start_time
    return results, total_time


def test_parallel_validation(keys: List[str], max_workers: int = 10) -> Tuple[Dict[str, int], float]:
    """测试并行验证性能"""
    logger.info(f"🚀 开始并行验证测试 (工作线程: {max_workers})...")
    
    # 创建验证器
    validator = ParallelKeyValidator(max_workers=max_workers)
    
    start_time = time.time()
    
    # 执行批量验证
    validation_results = validator.validate_batch(keys)
    
    # 统计结果
    results = {
        "ok": 0,
        "invalid": 0,
        "rate_limited": 0,
        "error": 0
    }
    
    for key, result in validation_results.items():
        if result.status == "ok":
            results["ok"] += 1
        elif result.status == "rate_limited":
            results["rate_limited"] += 1
        elif result.status == "invalid":
            results["invalid"] += 1
        else:
            results["error"] += 1
    
    total_time = time.time() - start_time
    
    # 获取统计信息
    stats = validator.get_stats()
    
    logger.info(f"   平均响应时间: {stats.avg_response_time:.2f}s")
    logger.info(f"   总吞吐量: {len(keys) / total_time:.2f} keys/s")
    
    validator.shutdown()
    
    return results, total_time


def run_performance_comparison(test_sizes: List[int] = None):
    """运行完整的性能对比测试"""
    if test_sizes is None:
        test_sizes = [10, 25, 50, 100]
    
    logger.info("=" * 80)
    logger.info("🏁 并行验证系统性能测试")
    logger.info("=" * 80)
    logger.info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"测试规模: {test_sizes}")
    logger.info("")
    
    # 存储测试结果
    test_results = []
    
    for size in test_sizes:
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 测试规模: {size} 个密钥")
        logger.info(f"{'='*60}")
        
        # 生成测试密钥
        test_keys = generate_test_keys(size)
        
        # 串行验证测试
        serial_results, serial_time = test_serial_validation(test_keys)
        serial_throughput = size / serial_time
        
        logger.info(f"\n📈 串行验证结果:")
        logger.info(f"   总耗时: {serial_time:.2f}秒")
        logger.info(f"   吞吐量: {serial_throughput:.2f} keys/s")
        logger.info(f"   结果分布: 有效={serial_results['ok']}, 无效={serial_results['invalid']}, 限流={serial_results['rate_limited']}")
        
        # 并行验证测试（不同工作线程数）
        parallel_results_list = []
        for workers in [5, 10, 20]:
            if workers > size:  # 工作线程数不应超过密钥数
                continue
                
            logger.info(f"\n🚀 并行验证 ({workers} 工作线程):")
            parallel_results, parallel_time = test_parallel_validation(test_keys, max_workers=workers)
            parallel_throughput = size / parallel_time
            
            logger.info(f"   总耗时: {parallel_time:.2f}秒")
            logger.info(f"   吞吐量: {parallel_throughput:.2f} keys/s")
            logger.info(f"   性能提升: {serial_time / parallel_time:.1f}x")
            logger.info(f"   时间节省: {serial_time - parallel_time:.2f}秒 ({(serial_time - parallel_time) / serial_time * 100:.1f}%)")
            
            parallel_results_list.append({
                "workers": workers,
                "time": parallel_time,
                "throughput": parallel_throughput,
                "speedup": serial_time / parallel_time
            })
        
        # 保存测试结果
        test_results.append({
            "size": size,
            "serial_time": serial_time,
            "serial_throughput": serial_throughput,
            "parallel_results": parallel_results_list
        })
    
    # 生成性能报告
    generate_performance_report(test_results)
    
    return test_results


def generate_performance_report(test_results: List[Dict]):
    """生成性能测试报告和图表"""
    logger.info("\n" + "=" * 80)
    logger.info("📊 性能测试总结报告")
    logger.info("=" * 80)
    
    # 创建图表
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('并行验证系统性能测试报告', fontsize=16, fontweight='bold')
    
    # 1. 吞吐量对比图
    sizes = [r["size"] for r in test_results]
    serial_throughputs = [r["serial_throughput"] for r in test_results]
    
    ax1.plot(sizes, serial_throughputs, 'r-o', label='串行验证', linewidth=2, markersize=8)
    
    # 添加不同工作线程数的并行验证结果
    worker_counts = set()
    for result in test_results:
        for p_result in result["parallel_results"]:
            worker_counts.add(p_result["workers"])
    
    colors = ['g', 'b', 'm', 'c', 'y']
    for i, workers in enumerate(sorted(worker_counts)):
        throughputs = []
        for result in test_results:
            for p_result in result["parallel_results"]:
                if p_result["workers"] == workers:
                    throughputs.append(p_result["throughput"])
                    break
            else:
                throughputs.append(None)
        
        # 过滤掉None值
        valid_sizes = [s for s, t in zip(sizes, throughputs) if t is not None]
        valid_throughputs = [t for t in throughputs if t is not None]
        
        ax1.plot(valid_sizes, valid_throughputs, f'{colors[i % len(colors)]}-o', 
                label=f'并行 ({workers} 线程)', linewidth=2, markersize=8)
    
    ax1.set_xlabel('密钥数量', fontsize=12)
    ax1.set_ylabel('吞吐量 (keys/秒)', fontsize=12)
    ax1.set_title('吞吐量对比', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 加速比图
    for result in test_results:
        size = result["size"]
        speedups = [p["speedup"] for p in result["parallel_results"]]
        workers = [p["workers"] for p in result["parallel_results"]]
        
        ax2.plot(workers, speedups, '-o', label=f'{size} keys', linewidth=2, markersize=8)
    
    ax2.set_xlabel('工作线程数', fontsize=12)
    ax2.set_ylabel('加速比 (倍数)', fontsize=12)
    ax2.set_title('加速比 vs 工作线程数', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=1, color='r', linestyle='--', alpha=0.5)
    
    # 3. 执行时间对比（柱状图）
    x = range(len(sizes))
    width = 0.2
    
    ax3.bar([i - width*1.5 for i in x], [r["serial_time"] for r in test_results], 
            width, label='串行', color='red', alpha=0.7)
    
    for j, workers in enumerate(sorted(worker_counts)):
        times = []
        for result in test_results:
            for p_result in result["parallel_results"]:
                if p_result["workers"] == workers:
                    times.append(p_result["time"])
                    break
            else:
                times.append(0)
        
        ax3.bar([i - width*0.5 + j*width for i in x], times, 
                width, label=f'并行-{workers}线程', alpha=0.7)
    
    ax3.set_xlabel('密钥数量', fontsize=12)
    ax3.set_ylabel('执行时间 (秒)', fontsize=12)
    ax3.set_title('执行时间对比', fontsize=14, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(sizes)
    ax3.legend()
    ax3.grid(True, axis='y', alpha=0.3)
    
    # 4. 效率提升百分比
    improvement_data = []
    labels = []
    
    for result in test_results:
        size = result["size"]
        serial_time = result["serial_time"]
        
        # 使用10线程的结果作为代表
        for p_result in result["parallel_results"]:
            if p_result["workers"] == 10:
                improvement = (serial_time - p_result["time"]) / serial_time * 100
                improvement_data.append(improvement)
                labels.append(f'{size} keys')
                break
    
    bars = ax4.bar(labels, improvement_data, color='green', alpha=0.7)
    ax4.set_ylabel('性能提升 (%)', fontsize=12)
    ax4.set_title('并行验证性能提升百分比 (10线程)', fontsize=14, fontweight='bold')
    ax4.grid(True, axis='y', alpha=0.3)
    
    # 在柱状图上添加数值
    for bar, value in zip(bars, improvement_data):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    
    # 保存图表
    report_path = 'performance_report.png'
    plt.savefig(report_path, dpi=300, bbox_inches='tight')
    logger.info(f"\n📈 性能报告图表已保存至: {report_path}")
    
    # 打印总结
    logger.info("\n🎯 关键发现:")
    
    # 计算平均加速比
    all_speedups = []
    for result in test_results:
        for p_result in result["parallel_results"]:
            if p_result["workers"] == 10:  # 使用10线程作为标准
                all_speedups.append(p_result["speedup"])
    
    if all_speedups:
        avg_speedup = statistics.mean(all_speedups)
        logger.info(f"   • 平均性能提升: {avg_speedup:.1f}x (使用10个工作线程)")
    
    # 找出最佳配置
    best_speedup = 0
    best_config = None
    for result in test_results:
        for p_result in result["parallel_results"]:
            if p_result["speedup"] > best_speedup:
                best_speedup = p_result["speedup"]
                best_config = (result["size"], p_result["workers"])
    
    if best_config:
        logger.info(f"   • 最佳性能提升: {best_speedup:.1f}x (处理{best_config[0]}个密钥，使用{best_config[1]}个工作线程)")
    
    # 吞吐量提升
    max_serial_throughput = max([r["serial_throughput"] for r in test_results])
    max_parallel_throughput = 0
    for result in test_results:
        for p_result in result["parallel_results"]:
            if p_result["throughput"] > max_parallel_throughput:
                max_parallel_throughput = p_result["throughput"]
    
    logger.info(f"   • 最大吞吐量提升: 从 {max_serial_throughput:.2f} 提升到 {max_parallel_throughput:.2f} keys/秒")
    
    logger.info("\n✅ 性能测试完成！")


def run_stress_test(duration_seconds: int = 60):
    """运行压力测试"""
    logger.info("\n" + "=" * 80)
    logger.info("🔥 压力测试模式")
    logger.info("=" * 80)
    logger.info(f"测试时长: {duration_seconds}秒")
    
    validator = ParallelKeyValidator(max_workers=20)
    
    start_time = time.time()
    total_validated = 0
    batch_times = []
    
    while time.time() - start_time < duration_seconds:
        # 生成随机批次大小的密钥
        batch_size = random.randint(20, 100)
        keys = generate_test_keys(batch_size)
        
        batch_start = time.time()
        results = validator.validate_batch(keys)
        batch_time = time.time() - batch_start
        
        batch_times.append(batch_time)
        total_validated += len(results)
        
        # 显示进度
        elapsed = time.time() - start_time
        rate = total_validated / elapsed
        logger.info(f"已验证: {total_validated} | 速率: {rate:.2f} keys/s | 批次时间: {batch_time:.2f}s")
    
    # 统计结果
    total_time = time.time() - start_time
    avg_batch_time = statistics.mean(batch_times)
    
    logger.info("\n📊 压力测试结果:")
    logger.info(f"   总验证数: {total_validated}")
    logger.info(f"   总时长: {total_time:.2f}秒")
    logger.info(f"   平均速率: {total_validated / total_time:.2f} keys/秒")
    logger.info(f"   平均批次时间: {avg_batch_time:.2f}秒")
    logger.info(f"   最快批次: {min(batch_times):.2f}秒")
    logger.info(f"   最慢批次: {max(batch_times):.2f}秒")
    
    validator.shutdown()


if __name__ == "__main__":
    # 运行性能对比测试
    logger.info("🚀 启动并行验证系统性能测试...")
    
    # 基础性能测试
    test_results = run_performance_comparison([10, 25, 50, 100, 200])
    
    # 可选：运行压力测试
    # run_stress_test(duration_seconds=30)
    
    logger.info("\n✨ 所有测试完成！")