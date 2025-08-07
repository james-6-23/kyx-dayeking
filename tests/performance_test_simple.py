"""
并行验证系统性能测试（简化版）
不依赖外部绘图库，专注于性能数据展示
"""

import sys
import os
import time
import random
from datetime import datetime
from typing import List, Dict, Tuple

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.Logger import logger
from utils.parallel_validator import ParallelKeyValidator


class PerformanceTest:
    """性能测试类"""
    
    def __init__(self):
        self.test_results = []
    
    def generate_test_keys(self, count: int) -> List[str]:
        """生成测试用的API密钥"""
        keys = []
        for i in range(count):
            # 生成符合格式的测试密钥
            key = f"AIzaSy{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_', k=33))}"
            keys.append(key)
        return keys
    
    def simulate_serial_validation(self, keys: List[str]) -> Tuple[Dict[str, int], float]:
        """模拟串行验证（原有方式）"""
        logger.info("🔄 开始串行验证测试...")
        start_time = time.time()
        
        results = {
            "ok": 0,
            "invalid": 0,
            "rate_limited": 0
        }
        
        for i, key in enumerate(keys):
            # 模拟网络延迟和处理时间
            time.sleep(random.uniform(0.8, 1.2))
            
            # 模拟验证结果（30%有效，10%限流，60%无效）
            rand = random.random()
            if rand < 0.3:
                results["ok"] += 1
            elif rand < 0.4:
                results["rate_limited"] += 1
            else:
                results["invalid"] += 1
            
            # 显示进度
            if (i + 1) % 10 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                logger.info(f"   进度: {i + 1}/{len(keys)} | 速率: {rate:.2f} keys/s")
        
        total_time = time.time() - start_time
        return results, total_time
    
    def test_parallel_validation(self, keys: List[str], max_workers: int = 10) -> Tuple[Dict[str, int], float, Dict]:
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
        
        response_times = []
        
        for key, result in validation_results.items():
            if result.status == "ok":
                results["ok"] += 1
            elif result.status == "rate_limited":
                results["rate_limited"] += 1
            elif result.status == "invalid":
                results["invalid"] += 1
            else:
                results["error"] += 1
            
            if result.response_time:
                response_times.append(result.response_time)
        
        total_time = time.time() - start_time
        
        # 获取统计信息
        stats = validator.get_stats()
        proxy_stats = validator.get_proxy_stats()
        
        # 计算额外统计
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        validator.shutdown()
        
        return results, total_time, {
            "avg_response_time": avg_response_time,
            "stats": stats,
            "proxy_stats": proxy_stats
        }
    
    def print_comparison_table(self, size: int, serial_time: float, parallel_results: List[Dict]):
        """打印对比表格"""
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 性能对比表 - {size} 个密钥")
        logger.info(f"{'='*80}")
        logger.info(f"{'验证方式':<20} {'耗时(秒)':<15} {'吞吐量(keys/s)':<20} {'加速比':<15}")
        logger.info(f"{'-'*80}")
        
        # 串行结果
        serial_throughput = size / serial_time
        logger.info(f"{'串行验证':<20} {serial_time:<15.2f} {serial_throughput:<20.2f} {'1.0x':<15}")
        
        # 并行结果
        for result in parallel_results:
            name = f"并行({result['workers']}线程)"
            speedup = f"{result['speedup']:.1f}x"
            logger.info(f"{name:<20} {result['time']:<15.2f} {result['throughput']:<20.2f} {speedup:<15}")
        
        logger.info(f"{'-'*80}")
    
    def run_comparison(self, test_sizes: List[int] = None):
        """运行完整的性能对比测试"""
        if test_sizes is None:
            test_sizes = [10, 25, 50]
        
        logger.info("\n" + "="*100)
        logger.info("🏁 并行验证系统性能测试")
        logger.info("="*100)
        logger.info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"测试规模: {test_sizes}")
        
        all_results = []
        
        for size in test_sizes:
            logger.info(f"\n\n{'#'*100}")
            logger.info(f"### 测试规模: {size} 个密钥")
            logger.info(f"{'#'*100}")
            
            # 生成测试密钥
            test_keys = self.generate_test_keys(size)
            
            # 串行验证测试
            serial_results, serial_time = self.simulate_serial_validation(test_keys)
            serial_throughput = size / serial_time
            
            logger.info(f"\n📈 串行验证结果:")
            logger.info(f"   总耗时: {serial_time:.2f}秒")
            logger.info(f"   吞吐量: {serial_throughput:.2f} keys/s")
            logger.info(f"   结果分布: 有效={serial_results['ok']}, 无效={serial_results['invalid']}, 限流={serial_results['rate_limited']}")
            
            # 并行验证测试
            parallel_results_list = []
            
            # 测试不同的工作线程数
            worker_counts = [5, 10, 20] if size >= 20 else [5, 10]
            
            for workers in worker_counts:
                if workers > size:
                    continue
                
                logger.info(f"\n🚀 并行验证测试 ({workers} 工作线程):")
                parallel_results, parallel_time, extra_stats = self.test_parallel_validation(test_keys, max_workers=workers)
                parallel_throughput = size / parallel_time
                speedup = serial_time / parallel_time
                
                logger.info(f"   总耗时: {parallel_time:.2f}秒")
                logger.info(f"   吞吐量: {parallel_throughput:.2f} keys/s")
                logger.info(f"   性能提升: {speedup:.1f}x")
                logger.info(f"   时间节省: {serial_time - parallel_time:.2f}秒 ({(serial_time - parallel_time) / serial_time * 100:.1f}%)")
                logger.info(f"   平均响应时间: {extra_stats['avg_response_time']:.2f}秒")
                
                # 显示代理统计
                if extra_stats['proxy_stats']:
                    logger.info("   代理性能:")
                    for proxy_url, pstats in extra_stats['proxy_stats'].items():
                        logger.info(f"     {proxy_url}: 成功率 {pstats['success_rate']:.1%} ({pstats['success']}/{pstats['total']})")
                
                parallel_results_list.append({
                    "workers": workers,
                    "time": parallel_time,
                    "throughput": parallel_throughput,
                    "speedup": speedup,
                    "time_saved": serial_time - parallel_time,
                    "time_saved_percent": (serial_time - parallel_time) / serial_time * 100
                })
            
            # 打印对比表格
            self.print_comparison_table(size, serial_time, parallel_results_list)
            
            # 保存结果
            all_results.append({
                "size": size,
                "serial_time": serial_time,
                "serial_throughput": serial_throughput,
                "parallel_results": parallel_results_list
            })
        
        # 打印总结报告
        self.print_summary_report(all_results)
        
        return all_results
    
    def print_summary_report(self, all_results: List[Dict]):
        """打印总结报告"""
        logger.info("\n\n" + "="*100)
        logger.info("📊 性能测试总结报告")
        logger.info("="*100)
        
        # 计算平均性能提升
        all_speedups = []
        best_speedup = 0
        best_config = None
        
        for result in all_results:
            for p_result in result["parallel_results"]:
                speedup = p_result["speedup"]
                all_speedups.append(speedup)
                
                if speedup > best_speedup:
                    best_speedup = speedup
                    best_config = {
                        "size": result["size"],
                        "workers": p_result["workers"],
                        "speedup": speedup,
                        "time_saved_percent": p_result["time_saved_percent"]
                    }
        
        avg_speedup = sum(all_speedups) / len(all_speedups) if all_speedups else 0
        
        logger.info("\n🎯 关键发现:")
        logger.info(f"   • 平均性能提升: {avg_speedup:.1f}x")
        
        if best_config:
            logger.info(f"   • 最佳性能提升: {best_config['speedup']:.1f}x")
            logger.info(f"     - 配置: {best_config['size']}个密钥，{best_config['workers']}个工作线程")
            logger.info(f"     - 时间节省: {best_config['time_saved_percent']:.1f}%")
        
        # 吞吐量对比
        logger.info("\n📈 吞吐量提升:")
        for result in all_results:
            size = result["size"]
            serial_tp = result["serial_throughput"]
            
            # 找出该规模下的最佳并行吞吐量
            best_parallel_tp = max([p["throughput"] for p in result["parallel_results"]])
            improvement = (best_parallel_tp - serial_tp) / serial_tp * 100
            
            logger.info(f"   • {size}个密钥: {serial_tp:.2f} → {best_parallel_tp:.2f} keys/s (+{improvement:.1f}%)")
        
        # 建议
        logger.info("\n💡 优化建议:")
        logger.info("   1. 对于小批量（<20个密钥），使用5-10个工作线程")
        logger.info("   2. 对于大批量（>50个密钥），使用10-20个工作线程")
        logger.info("   3. 配置足够的代理以避免限流")
        logger.info("   4. 根据系统CPU核心数调整工作线程数（建议：CPU核心数 × 2）")
        
        logger.info("\n✅ 性能测试完成！")


def run_quick_demo():
    """运行快速演示"""
    logger.info("\n🚀 快速性能演示")
    logger.info("="*60)
    
    # 生成20个测试密钥
    test_keys = []
    for i in range(20):
        key = f"AIzaSy{''.join(random.choices('0123456789ABCDEF', k=33))}"
        test_keys.append(key)
    
    # 模拟串行验证
    logger.info("\n1️⃣ 模拟串行验证（原方式）...")
    serial_start = time.time()
    for i, key in enumerate(test_keys):
        time.sleep(1)  # 模拟验证延迟
        if (i + 1) % 5 == 0:
            logger.info(f"   已验证: {i + 1}/20")
    serial_time = time.time() - serial_start
    
    logger.info(f"   串行验证完成！耗时: {serial_time:.2f}秒")
    
    # 并行验证
    logger.info("\n2️⃣ 并行验证（新方式）...")
    validator = ParallelKeyValidator(max_workers=10)
    
    parallel_start = time.time()
    results = validator.validate_batch(test_keys)
    parallel_time = time.time() - parallel_start
    
    logger.info(f"   并行验证完成！耗时: {parallel_time:.2f}秒")
    
    # 显示结果
    speedup = serial_time / parallel_time
    logger.info(f"\n🎉 性能提升: {speedup:.1f}倍！")
    logger.info(f"   时间节省: {serial_time - parallel_time:.1f}秒")
    
    validator.shutdown()


if __name__ == "__main__":
    logger.info("🏁 启动并行验证系统性能测试...")
    
    # 选择测试模式
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # 快速演示模式
        run_quick_demo()
    else:
        # 完整测试模式
        tester = PerformanceTest()
        
        # 可以自定义测试规模
        # test_sizes = [10, 25, 50, 100]  # 更大规模测试
        test_sizes = [10, 25, 50]  # 标准测试
        
        results = tester.run_comparison(test_sizes)
        
        logger.info("\n✨ 所有测试完成！")
        logger.info("\n提示：运行 'python performance_test_simple.py quick' 可以查看快速演示")