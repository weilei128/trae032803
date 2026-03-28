#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球数据自动化分析工具 v2.0
主程序入口
支持获取最近500期开奖数据，生成分析图表和PDF报告

功能特点:
- 从官方/可信接口获取最近500期开奖数据
- 对红球、蓝球分别绘制号码走势图、出现频次统计图
- 图表清晰带中文标注、网格线
- 每个图表下方添加文字说明
- 自动生成PDF报告，支持中文正常显示
- 完善的异常处理机制

依赖说明:
- requests>=2.31.0: HTTP请求库，用于获取开奖数据
- matplotlib>=3.7.0: 绑图库，用于生成图表
- pandas>=2.0.0: 数据处理库
- reportlab>=4.0.0: PDF生成库
- numpy>=1.24.0: 数值计算库
- Pillow>=10.0.0: 图像处理库

运行方式:
    python main.py                    # 获取500期数据，生成PDF报告
    python main.py --count 200        # 获取200期数据
    python main.py --mock             # 使用模拟数据测试
    python main.py --no-pdf           # 只生成图表，不生成PDF
    python main.py -h                 # 查看帮助信息
"""
import sys
import os
import traceback
import argparse
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ssq_analyzer.log', encoding='utf-8', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """检查依赖是否安装"""
    required_modules = {
        'requests': 'requests',
        'matplotlib': 'matplotlib',
        'pandas': 'pandas',
        'reportlab': 'reportlab',
        'numpy': 'numpy',
        'PIL': 'Pillow',
    }
    
    missing_modules = []
    for import_name, package_name in required_modules.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_modules.append(package_name)
    
    if missing_modules:
        print("=" * 60)
        print("    错误：缺少以下依赖模块")
        print("=" * 60)
        for mod in missing_modules:
            print(f"  - {mod}")
        print("\n请运行以下命令安装依赖:")
        print("  pip install -r requirements.txt")
        print("=" * 60)
        return False
    return True


def print_banner():
    """打印欢迎信息"""
    print("\n" + "=" * 60)
    print("    双色球数据自动化分析工具 v2.0")
    print("    支持获取最近500期开奖数据")
    print("=" * 60)


def print_result(summary: dict, args):
    """打印分析结果"""
    print("\n" + "=" * 60)
    print("    分析完成!")
    print("=" * 60)
    print(f"\n统计期数: {summary['total_issues']} 期")
    print(f"日期范围: {summary['date_range'][0]} 至 {summary['date_range'][1]}")
    print(f"\n红球热门号码: {', '.join([f'{n:02d}' for n in summary['red_hot']])}")
    print(f"红球冷门号码: {', '.join([f'{n:02d}' for n in summary['red_cold']])}")
    print(f"蓝球热门号码: {', '.join([f'{n:02d}' for n in summary['blue_hot']])}")
    print(f"蓝球冷门号码: {', '.join([f'{n:02d}' for n in summary['blue_cold']])}")
    print(f"\n图表目录: {os.path.abspath(args.charts_dir)}")
    if not args.no_pdf:
        print(f"PDF报告: {os.path.abspath(args.output)}")
    print(f"日志文件: {os.path.abspath('ssq_analyzer.log')}")
    print("\n" + "=" * 60)


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description='双色球数据自动化分析工具 v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                    获取500期数据，生成PDF报告
  python main.py --count 200        获取200期数据
  python main.py --mock             使用模拟数据测试
  python main.py --no-pdf           只生成图表，不生成PDF
        """
    )
    parser.add_argument('--count', '-c', type=int, default=500,
                       help='分析的期数数量，默认500期（最大500期）')
    parser.add_argument('--output', '-o', default='ssq_analysis_report.pdf',
                       help='PDF报告输出路径，默认ssq_analysis_report.pdf')
    parser.add_argument('--charts-dir', default='charts',
                       help='图表保存目录，默认charts')
    parser.add_argument('--no-pdf', action='store_true',
                       help='只生成图表，不生成PDF报告')
    parser.add_argument('--mock', action='store_true',
                       help='强制使用模拟数据（用于测试）')
    
    args = parser.parse_args()
    
    print_banner()
    
    if not check_dependencies():
        sys.exit(1)
    
    start_time = datetime.now()
    
    try:
        from ssq_analyzer.data_fetcher import SSQDataFetcher
        from ssq_analyzer.analyzer import SSQAnalyzer
        from ssq_analyzer.visualizer import SSQVisualizer
        from ssq_analyzer.pdf_generator import SSQPDFGenerator
        
        print(f"\n[1/5] 正在获取最近 {args.count} 期开奖数据...")
        fetcher = SSQDataFetcher()
        
        try:
            if args.mock:
                print("      (使用模拟数据模式)")
                data = fetcher.generate_mock_data(args.count)
            else:
                data = fetcher.fetch_data(args.count)
        except Exception as e:
            logger.error(f"获取数据失败: {e}")
            print(f"\n警告: 获取数据失败 ({e})")
            print("正在使用模拟数据继续分析...")
            data = fetcher.generate_mock_data(args.count)
        
        if not data:
            logger.error("无法获取数据")
            print("错误：无法获取数据，请检查网络连接或稍后重试")
            sys.exit(1)
        
        print(f"      成功获取 {len(data)} 期数据")
        print(f"      数据范围: {data[-1]['date']} 至 {data[0]['date']}")
        
        print("\n[2/5] 正在进行数据分析...")
        try:
            analyzer = SSQAnalyzer(data)
            summary = analyzer.get_summary()
            print("      数据分析完成")
        except Exception as e:
            logger.error(f"数据分析失败: {e}")
            print(f"错误：数据分析失败: {e}")
            sys.exit(1)
        
        print("\n[3/5] 正在生成分析图表...")
        try:
            visualizer = SSQVisualizer(output_dir=args.charts_dir)
            issues = [item['issue'] for item in data]
            chart_files = visualizer.generate_all_charts(analyzer, issues)
            print(f"      成功生成 {len(chart_files)} 个图表")
        except Exception as e:
            logger.error(f"生成图表失败: {e}")
            print(f"错误：生成图表失败: {e}")
            sys.exit(1)
        
        if not args.no_pdf:
            print("\n[4/5] 正在生成PDF分析报告...")
            try:
                pdf_generator = SSQPDFGenerator(output_path=args.output)
                pdf_generator.generate_report(summary, chart_files)
                print(f"      PDF报告已生成: {args.output}")
            except Exception as e:
                logger.error(f"生成PDF失败: {e}")
                print(f"错误：生成PDF失败: {e}")
                print("      请检查图表文件是否存在")
                sys.exit(1)
        else:
            print("\n[4/5] 跳过PDF生成 (--no-pdf)")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n[5/5] 分析完成!")
        print_result(summary, args)
        
        print(f"\n总耗时: {duration:.1f} 秒")
        print(f"完成时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        logger.info(f"分析完成，耗时 {duration:.1f} 秒")
    
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
        logger.info("用户中断操作")
        sys.exit(1)
    
    except ImportError as e:
        logger.error(f"导入模块失败: {e}")
        print("\n" + "=" * 60)
        print("    错误：导入模块失败")
        print("=" * 60)
        print(f"\n错误信息: {e}")
        print("\n请确保已安装所有依赖:")
        print("  pip install -r requirements.txt")
        print("=" * 60)
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
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
