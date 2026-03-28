#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球数据自动化分析工具 v2.0
功能：
1. 从官方/可信接口获取最近500期开奖数据
2. 对红球、蓝球分别绘制号码走势图、出现频次统计图
3. 图表清晰带中文标注、网格线
4. 将所有图表自动排版生成PDF文件，支持中文正常显示
5. 每个图下都有文字说明
6. 完善的异常处理机制

依赖安装：
    pip install -r requirements.txt

运行方式：
    python main.py                    # 使用默认参数（500期）
    python main.py --count 300        # 分析300期
    python main.py --mock             # 使用模拟数据测试
    python main.py --no-pdf           # 只生成图表，不生成PDF

作者：AI Assistant
版本：2.0
日期：2024
"""
import sys
import os
import traceback
import argparse
import logging

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
    """
    检查依赖是否安装
    :return: 如果所有依赖都已安装返回True，否则返回False
    """
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
        print("=" * 60)
        print("错误：缺少以下依赖模块:")
        print("=" * 60)
        for mod in missing_modules:
            print(f"  - {mod}")
        print("\n请运行以下命令安装依赖:")
        print("  pip install -r requirements.txt")
        print("\n或手动安装:")
        print("  pip install requests matplotlib pandas reportlab numpy Pillow")
        print("=" * 60)
        return False
    return True


def print_usage():
    """打印使用说明"""
    print("""
====================================================================
                    双色球数据自动化分析工具 v2.0
====================================================================
功能说明：
  1. 自动获取最近500期双色球开奖数据
  2. 生成红球/蓝球出现频次统计图
  3. 生成红球/蓝球号码走势图（最近50期）
  4. 生成红球/蓝球遗漏统计图
  5. 自动排版生成PDF分析报告（支持中文）

使用参数：
  --count, -c    分析的期数数量，默认500期
  --output, -o   PDF报告输出路径，默认ssq_analysis_report.pdf
  --charts-dir   图表保存目录，默认charts
  --no-pdf       只生成图表，不生成PDF报告
  --mock         强制使用模拟数据（用于测试）
  --help, -h     显示帮助信息

示例：
  python main.py                    # 分析最近500期
  python main.py -c 300             # 分析最近300期
  python main.py --mock             # 使用模拟数据测试
  python main.py --no-pdf           # 只生成图表
====================================================================
""")


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description='双色球数据自动化分析工具 v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py              # 分析最近500期
  python main.py -c 300       # 分析最近300期
  python main.py --mock       # 使用模拟数据测试
        """
    )
    parser.add_argument('--count', '-c', type=int, default=500,
                       help='分析的期数数量，默认500期')
    parser.add_argument('--output', '-o', default='ssq_analysis_report.pdf',
                       help='PDF报告输出路径，默认ssq_analysis_report.pdf')
    parser.add_argument('--charts-dir', default='charts',
                       help='图表保存目录，默认charts')
    parser.add_argument('--no-pdf', action='store_true',
                       help='只生成图表，不生成PDF报告')
    parser.add_argument('--mock', action='store_true',
                       help='强制使用模拟数据（用于测试）')
    
    args = parser.parse_args()
    
    # 欢迎信息
    print("=" * 60)
    print("    双色球数据自动化分析工具 v2.0")
    print("=" * 60)
    
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
            logger.info("使用模拟数据模式")
            data = fetcher.generate_mock_data(args.count)
        else:
            try:
                data = fetcher.fetch_data(args.count)
            except Exception as e:
                logger.error(f"数据获取失败: {e}")
                print(f"\n警告: 数据获取失败，将使用模拟数据继续...")
                data = fetcher.generate_mock_data(args.count)
        
        if not data:
            logger.error("无法获取数据")
            print("错误：无法获取数据，请检查网络连接或稍后重试")
            sys.exit(1)
        
        print(f"成功获取 {len(data)} 期数据")
        print(f"数据范围: {data[-1]['date']} 至 {data[0]['date']}")
        
        # 2. 数据分析
        print("\n[2/5] 正在进行数据分析...")
        try:
            analyzer = SSQAnalyzer(data)
            summary = analyzer.get_summary()
            print("数据分析完成")
            
            # 打印冷热号
            print(f"\n热门红球: {summary['red_hot']}")
            print(f"冷门红球: {summary['red_cold']}")
            print(f"热门蓝球: {summary['blue_hot']}")
            print(f"冷门蓝球: {summary['blue_cold']}")
        except Exception as e:
            logger.error(f"数据分析失败: {e}")
            print(f"错误：数据分析失败 - {e}")
            sys.exit(1)
        
        # 3. 生成图表
        print("\n[3/5] 正在生成分析图表...")
        try:
            visualizer = SSQVisualizer(output_dir=args.charts_dir)
            issues = [item['issue'] for item in data]
            chart_files = visualizer.generate_all_charts(analyzer, issues)
            print(f"成功生成 {len(chart_files)} 个图表，保存在: {args.charts_dir}/")
            
            # 列出生成的图表
            for chart_name, chart_path in chart_files.items():
                print(f"  ✓ {chart_name}: {os.path.basename(chart_path)}")
        except Exception as e:
            logger.error(f"图表生成失败: {e}")
            print(f"错误：图表生成失败 - {e}")
            sys.exit(1)
        
        # 4. 生成PDF报告
        if not args.no_pdf:
            print("\n[4/5] 正在生成PDF分析报告...")
            try:
                pdf_generator = SSQPDFGenerator(output_path=args.output)
                pdf_generator.generate_report(summary, chart_files)
                print(f"PDF报告已生成: {args.output}")
            except Exception as e:
                logger.error(f"PDF生成失败: {e}")
                print(f"警告：PDF生成失败 - {e}")
                print("但图表文件已成功生成，您仍可以查看图表。")
        
        # 5. 完成
        print("\n" + "=" * 60)
        print("    分析完成!")
        print("=" * 60)
        print(f"\n统计期数: {summary['total_issues']} 期")
        print(f"日期范围: {summary['date_range'][0]} 至 {summary['date_range'][1]}")
        print(f"图表目录: {os.path.abspath(args.charts_dir)}")
        if not args.no_pdf and os.path.exists(args.output):
            print(f"PDF报告: {os.path.abspath(args.output)}")
        print(f"日志文件: {os.path.abspath('ssq_analyzer.log')}")
        print("\n" + "=" * 60)
        print("\n免责声明：本报告仅供娱乐和学习参考，不构成投注建议。")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}", exc_info=True)
        print("\n" + "=" * 60)
        print("    程序运行出错")
        print("=" * 60)
        print(f"\n错误信息: {str(e)}")
        print("\n详细错误信息:")
        traceback.print_exc()
        print("\n请查看日志文件获取更多信息: ssq_analyzer.log")
        print("\n如果问题持续存在，请尝试:")
        print("  1. 检查网络连接")
        print("  2. 使用 --mock 参数运行测试模式")
        print("  3. 重新安装依赖: pip install -r requirements.txt")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
