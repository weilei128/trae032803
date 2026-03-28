#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球数据自动化分析工具 v2.0
支持500期大数据分析，图表自动带说明，PDF支持中文显示
"""
import sys
import os
import traceback
import argparse
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ssq_analyzer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """检查依赖是否安装"""
    required_modules = [
        'requests',
        'matplotlib',
        'pandas',
        'reportlab',
        'numpy',
    ]
    
    # PIL的导入名称是Pillow
    try:
        from PIL import Image
    except ImportError:
        required_modules.append('Pillow')
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("错误：缺少以下依赖模块:")
        for mod in missing_modules:
            print(f"  - {mod}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    return True

def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description='双色球数据自动化分析工具 v2.0')
    parser.add_argument('--count', '-c', type=int, default=500,
                       help='分析的期数数量，默认500期（最大值500）')
    parser.add_argument('--output', '-o', default='ssq_analysis_report.pdf',
                       help='PDF报告输出路径，默认ssq_analysis_report.pdf')
    parser.add_argument('--charts-dir', default='charts',
                       help='图表保存目录，默认charts')
    parser.add_argument('--no-pdf', action='store_true',
                       help='只生成图表，不生成PDF报告')
    parser.add_argument('--mock', action='store_true',
                       help='强制使用模拟数据（用于测试）')
    parser.add_argument('--no-caption', action='store_true',
                       help='不生成图表说明文字（仅图表）')
    
    args = parser.parse_args()
    
    # 欢迎信息
    print("=" * 70)
    print("    双色球数据自动化分析工具 v2.0")
    print("    支持500期大数据分析 | 图表自动带说明 | PDF中文显示")
    print("=" * 70)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # 导入内部模块
        from ssq_analyzer.data_fetcher import SSQDataFetcher
        from ssq_analyzer.analyzer import SSQAnalyzer
        from ssq_analyzer.visualizer import SSQVisualizer
        from ssq_analyzer.pdf_generator import SSQPDFGenerator
        
        # 1. 获取数据
        print(f"\n[1/5] 正在获取最近 {args.count} 期开奖数据...")
        fetcher = SSQDataFetcher()
        
        if args.mock:
            data = fetcher.generate_mock_data(args.count)
        else:
            data = fetcher.fetch_data(args.count)
        
        if not data:
            logger.error("无法获取数据")
            print("错误：无法获取数据，请检查网络连接或稍后重试")
            print("提示：可使用 --mock 参数使用模拟数据进行测试")
            sys.exit(1)
        
        print(f"成功获取 {len(data)} 期有效数据")
        print(f"数据范围: {data[-1]['date']} 至 {data[0]['date']}")
        
        # 2. 数据分析
        print("\n[2/5] 正在进行数据分析...")
        analyzer = SSQAnalyzer(data)
        summary = analyzer.get_summary()
        # 添加生成时间
        summary['generate_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("数据分析完成")
        
        # 打印冷热号
        print(f"\n热门红球 (前5): {summary['red_hot']}")
        print(f"冷门红球 (后5): {summary['red_cold']}")
        print(f"热门蓝球 (前5): {summary['blue_hot']}")
        print(f"冷门蓝球 (后5): {summary['blue_cold']}")
        print(f"红球平均出现频次: {summary['red_avg_freq']:.1f} 次")
        print(f"蓝球平均出现频次: {summary['blue_avg_freq']:.1f} 次")
        
        # 3. 生成图表
        print("\n[3/5] 正在生成分析图表...")
        visualizer = SSQVisualizer(output_dir=args.charts_dir)
        issues = [item['issue'] for item in data]
        chart_files = visualizer.generate_all_charts(analyzer, issues)
        
        # 获取图表说明文字
        chart_descriptions = None
        if not args.no_caption:
            chart_descriptions = visualizer.get_chart_descriptions(summary)
        
        print(f"成功生成 {len(chart_files)} 个图表，保存在: {args.charts_dir}/")
        for name, path in chart_files.items():
            print(f"  - {name}: {os.path.basename(path)}")
        
        # 4. 生成PDF报告
        if not args.no_pdf:
            print("\n[4/5] 正在生成PDF分析报告...")
            pdf_generator = SSQPDFGenerator(output_path=args.output)
            pdf_generator.generate_report(summary, chart_files, chart_descriptions)
            print(f"PDF报告已生成: {args.output}")
        
        # 5. 完成
        print("\n" + "=" * 70)
        print("    分析完成!")
        print("=" * 70)
        print(f"\n统计期数: {summary['total_issues']} 期")
        print(f"日期范围: {summary['date_range'][0]} 至 {summary['date_range'][1]}")
        print(f"图表目录: {os.path.abspath(args.charts_dir)}")
        if not args.no_pdf:
            print(f"PDF报告: {os.path.abspath(args.output)}")
        print(f"日志文件: {os.path.abspath('ssq_analyzer.log')}")
        print(f"报告生成时间: {summary['generate_time']}")
        print("\n" + "=" * 70)
        print("\n【温馨提示】彩票有风险，投资需谨慎。本分析仅作统计参考！")
        
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}", exc_info=True)
        print("\n" + "=" * 70)
        print("    程序运行出错")
        print("=" * 70)
        print(f"\n错误信息: {str(e)}")
        print("\n详细错误信息:")
        traceback.print_exc()
        print("\n请查看日志文件获取更多信息: ssq_analyzer.log")
        print("\n排障建议:")
        print("1. 网络问题: 检查网络连接或使用 --mock 参数使用模拟数据")
        print("2. 依赖问题: 运行 pip install -r requirements.txt 安装依赖")
        print("3. 字体问题: 确保系统安装了中文字体（微软雅黑/文泉驿等）")
        sys.exit(1)

if __name__ == '__main__':
    main()
