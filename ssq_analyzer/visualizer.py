#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球可视化模块
绘制号码走势图、出现频次统计图
支持500期大数据分析可视化
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from typing import List, Dict, Tuple, Optional
import os
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置中文显示 - 增强多系统支持
def configure_matplotlib_font():
    """配置matplotlib中文显示"""
    # 尝试多种中文字体，按优先级排列
    font_preferences = [
        'Microsoft YaHei',    # Windows
        'SimHei',              # Windows 黑体
        'WenQuanYi Zen Hei',   # Linux
        'Noto Sans CJK SC',     # Linux
        'Source Han Sans CN',   # macOS
        'Arial Unicode MS',    # macOS
        'DejaVu Sans',         #  fallback
    ]
    
    # 检查系统平台
    if sys.platform.startswith('win'):
        font_preferences = ['Microsoft YaHei', 'SimHei', 'SimSun', 'NSimSun'] + font_preferences
    elif sys.platform.startswith('darwin'):
        font_preferences = ['PingFang HK', 'PingFang SC', 'Arial Unicode MS'] + font_preferences
    
    # 设置字体
    mpl.rcParams['font.sans-serif'] = font_preferences + mpl.rcParams['font.sans-serif']
    mpl.rcParams['axes.unicode_minus'] = False
    mpl.rcParams['font.size'] = 10
    mpl.rcParams['figure.dpi'] = 100
    mpl.rcParams['savefig.dpi'] = 300
    mpl.rcParams['savefig.bbox'] = 'tight'

# 初始化字体配置
configure_matplotlib_font()

class SSQVisualizer:
    """双色球可视化器"""
    
    def __init__(self, output_dir: str = 'charts'):
        """
        初始化可视化器
        :param output_dir: 图表输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 颜色配置 - 专业配色方案
        self.red_color = '#dc2626'        # 红球主色
        self.red_light = '#fca5a5'
        self.red_dark = '#991b1b'
        self.blue_color = '#2563eb'      # 蓝球主色
        self.blue_light = '#93c5fd'
        self.blue_dark = '#1e40af'
        self.grid_color = '#e5e7eb'
        self.grid_dark = '#9ca3af'
        self.bg_color = '#fafafa'
        self.text_color = '#1f2937'
        self.accent_color = '#059669'
    
    def _save_and_close(self, fig, filename: str):
        """保存并关闭图片"""
        filepath = os.path.join(self.output_dir, filename)
        fig.tight_layout(pad=2.0)
        fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor=self.bg_color)
        plt.close(fig)
        logger.info(f"图表已保存: {filepath}")
        return filepath
    
    def _add_value_labels(self, ax, bars, fontsize=8):
        """为柱状图添加数值标签"""
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=fontsize,
                    fontweight='bold', color=self.text_color)
    
    def plot_red_frequency(self, freq_data: Dict[int, int], title: str = '红球出现频次统计') -> str:
        """
        绘制红球出现频次统计图
        支持500期大数据可视化
        """
        nums = list(freq_data.keys())
        freqs = list(freq_data.values())
        avg_freq = sum(freqs) / len(freqs)
        max_freq = max(freqs)
        min_freq = min(freqs)
        
        fig, ax = plt.subplots(figsize=(16, 9), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        # 根据频率值设置渐变颜色
        colors = [self.red_color if freq >= avg_freq else self.red_light for freq in freqs]
        
        # 绘制柱状图
        bars = ax.bar(nums, freqs, color=colors, alpha=0.9, width=0.75,
                     edgecolor=self.red_dark, linewidth=0.5)
        
        # 添加平均线
        ax.axhline(y=avg_freq, color=self.accent_color, linestyle='-', linewidth=2,
                  label=f'平均频次 ({avg_freq:.1f}')
        
        # 添加最大值和最小值线
        ax.axhline(y=max_freq, color=self.red_dark, linestyle=':', linewidth=1.5,
                  alpha=0.8, label=f'最高频次 ({max_freq})')
        ax.axhline(y=min_freq, color='#6b7280', linestyle=':', linewidth=1.5,
                  alpha=0.8, label=f'最低频次 ({min_freq})')
        
        # 添加数值标签
        self._add_value_labels(ax, bars, fontsize=7)
        
        # 图表标题和标签
        ax.set_title(title, fontsize=18, pad=25, fontweight='bold', color=self.text_color)
        ax.set_xlabel('红球号码 (1-33)', fontsize=13, labelpad=15)
        ax.set_ylabel('出现次数', fontsize=13, labelpad=15)
        ax.set_xticks(nums)
        ax.set_xticklabels([str(n) for n in nums], fontsize=10)
        ax.tick_params(axis='both', colors=self.text_color)
        
        # 增强网格线
        ax.grid(True, axis='y', linestyle='-', alpha=0.4, color=self.grid_color, linewidth=1)
        ax.grid(True, axis='x', linestyle=':', alpha=0.3, color=self.grid_color, linewidth=0.5)
        ax.set_axisbelow(True)  # 网格线在柱状图下方
        
        # 设置边框
        ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
        ax.set_ylim(0, max_freq * 1.12)
        
        return self._save_and_close(fig, 'red_frequency.png')
    
    def plot_blue_frequency(self, freq_data: Dict[int, int], title: str = '蓝球出现频次统计') -> str:
        """
        绘制蓝球出现频次统计图
        支持500期大数据可视化
        """
        nums = list(freq_data.keys())
        freqs = list(freq_data.values())
        avg_freq = sum(freqs) / len(freqs)
        max_freq = max(freqs)
        min_freq = min(freqs)
        
        fig, ax = plt.subplots(figsize=(14, 7), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        # 根据频率值设置渐变颜色
        colors = [self.blue_color if freq >= avg_freq else self.blue_light for freq in freqs]
        
        bars = ax.bar(nums, freqs, color=colors, alpha=0.9, width=0.65,
                     edgecolor=self.blue_dark, linewidth=0.5)
        
        ax.axhline(y=avg_freq, color=self.accent_color, linestyle='-', linewidth=2,
                  label=f'平均频次 ({avg_freq:.1f})')
        ax.axhline(y=max_freq, color=self.blue_dark, linestyle=':', linewidth=1.5,
                  alpha=0.8, label=f'最高频次 ({max_freq})')
        ax.axhline(y=min_freq, color='#6b7280', linestyle=':', linewidth=1.5,
                  alpha=0.8, label=f'最低频次 ({min_freq})')
        
        # 添加数值标签
        self._add_value_labels(ax, bars, fontsize=9)
        
        ax.set_title(title, fontsize=18, pad=25, fontweight='bold', color=self.text_color)
        ax.set_xlabel('蓝球号码 (1-16)', fontsize=13, labelpad=15)
        ax.set_ylabel('出现次数', fontsize=13, labelpad=15)
        ax.set_xticks(nums)
        ax.set_xticklabels([str(n) for n in nums], fontsize=11)
        ax.tick_params(axis='both', colors=self.text_color)
        
        # 增强网格线
        ax.grid(True, axis='y', linestyle='-', alpha=0.4, color=self.grid_color, linewidth=1)
        ax.grid(True, axis='x', linestyle=':', alpha=0.3, color=self.grid_color, linewidth=0.5)
        ax.set_axisbelow(True)
        
        ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
        ax.set_ylim(0, max_freq * 1.15)
        
        return self._save_and_close(fig, 'blue_frequency.png')
    
    def plot_red_trend(self, trend_data: Dict[int, List[int]], issues: List[str], 
                       title: str = '红球号码走势图 (最近30期)') -> str:
        """
        绘制红球号码走势图
        增强可视化效果，优化网格线
        """
        num_count = 33  # 红球号码数量
        period_count = min(len(issues), 30)  # 显示最近30期，优化性能
        
        # 准备数据矩阵
        matrix = np.zeros((num_count, period_count))
        for num in range(1, 34):
            values = trend_data[num][-period_count:] if len(trend_data[num]) >= period_count else trend_data[num]
            if len(values) < period_count:
                values = [0] * (period_count - len(values)) + values
            matrix[num-1] = values
        
        display_issues = issues[:period_count]
        display_issues_reversed = display_issues[::-1]  # 反转，旧到新
        
        fig, ax = plt.subplots(figsize=(18, 11), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        # 使用自定义颜色映射
        from matplotlib.colors import ListedColormap
        cmap = ListedColormap(['#f3f4f6', self.red_color])
        im = ax.imshow(matrix, aspect='auto', cmap=cmap, vmin=0, vmax=1)
        
        # 设置标签
        ax.set_yticks(np.arange(num_count))
        ax.set_yticklabels([f'{n:2d}' for n in range(1, 34)], fontsize=9, fontweight='medium')
        ax.set_xticks(np.arange(period_count))
        ax.set_xticklabels([issue[-4:] for issue in display_issues_reversed],
                          rotation=90, fontsize=7)
        
        # 只标记开出的号码，优化性能
        for i in range(num_count):
            for j in range(period_count):
                if matrix[i, j] == 1:
                    ax.text(j, i, '●', ha='center', va='center', color='white', 
                           fontsize=8, fontweight='bold')
        
        ax.set_title(title, fontsize=18, pad=25, fontweight='bold', color=self.text_color)
        ax.set_xlabel('期号 (从左到右：旧 → 新)', fontsize=13, labelpad=15)
        ax.set_ylabel('红球号码', fontsize=13, labelpad=15)
        ax.tick_params(axis='both', colors=self.text_color)
        
        # 增强网格线
        ax.set_xticks(np.arange(period_count + 1) - 0.5, minor=True)
        ax.set_yticks(np.arange(num_count + 1) - 0.5, minor=True)
        ax.grid(which='minor', color='white', linestyle='-', linewidth=1.2)
        ax.grid(which='major', visible=False)
        ax.tick_params(which='minor', bottom=False, left=False)
        
        # 设置边框
        for spine in ax.spines.values():
            spine.set_color(self.grid_dark)
            spine.set_linewidth(1)
        
        return self._save_and_close(fig, 'red_trend.png')
    
    def plot_blue_trend(self, trend_data: Dict[int, List[int]], issues: List[str],
                        title: str = '蓝球号码走势图 (最近30期)') -> str:
        """
        绘制蓝球号码走势图
        增强可视化效果，优化网格线
        """
        num_count = 16  # 蓝球号码数量
        period_count = min(len(issues), 30)  # 显示最近30期，优化性能
        
        matrix = np.zeros((num_count, period_count))
        for num in range(1, 17):
            values = trend_data[num][-period_count:] if len(trend_data[num]) >= period_count else trend_data[num]
            if len(values) < period_count:
                values = [0] * (period_count - len(values)) + values
            matrix[num-1] = values
        
        display_issues = issues[:period_count]
        display_issues_reversed = display_issues[::-1]
        
        fig, ax = plt.subplots(figsize=(18, 8), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        from matplotlib.colors import ListedColormap
        cmap = ListedColormap(['#f3f4f6', self.blue_color])
        im = ax.imshow(matrix, aspect='auto', cmap=cmap, vmin=0, vmax=1)
        
        ax.set_yticks(np.arange(num_count))
        ax.set_yticklabels([f'{n:2d}' for n in range(1, 17)], fontsize=10, fontweight='medium')
        ax.set_xticks(np.arange(period_count))
        ax.set_xticklabels([issue[-4:] for issue in display_issues_reversed],
                          rotation=90, fontsize=7)
        
        # 只标记开出的号码，优化性能
        for i in range(num_count):
            for j in range(period_count):
                if matrix[i, j] == 1:
                    ax.text(j, i, '●', ha='center', va='center', color='white', 
                           fontsize=9, fontweight='bold')
        
        ax.set_title(title, fontsize=18, pad=25, fontweight='bold', color=self.text_color)
        ax.set_xlabel('期号 (从左到右：旧 → 新)', fontsize=13, labelpad=15)
        ax.set_ylabel('蓝球号码', fontsize=13, labelpad=15)
        ax.tick_params(axis='both', colors=self.text_color)
        
        # 增强网格线
        ax.set_xticks(np.arange(period_count + 1) - 0.5, minor=True)
        ax.set_yticks(np.arange(num_count + 1) - 0.5, minor=True)
        ax.grid(which='minor', color='white', linestyle='-', linewidth=1.2)
        ax.grid(which='major', visible=False)
        ax.tick_params(which='minor', bottom=False, left=False)
        
        for spine in ax.spines.values():
            spine.set_color(self.grid_dark)
            spine.set_linewidth(1)
        
        return self._save_and_close(fig, 'blue_trend.png')
    
    def plot_red_missing(self, missing_data: Dict[int, int], title: str = '红球遗漏统计图') -> str:
        """
        绘制红球遗漏统计图
        遗漏期数：距离当前最后一期该号码未出现的期数
        """
        nums = list(missing_data.keys())
        missing = list(missing_data.values())
        avg_missing = sum(missing) / len(missing) if missing else 0
        max_missing = max(missing) if missing else 0
        
        fig, ax = plt.subplots(figsize=(16, 9), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        # 根据遗漏值设置颜色（遗漏越久颜色越深）
        colors = []
        for m in missing:
            if m <= 5:
                colors.append('#f59e0b')    # 近期出现
            elif m <= 15:
                colors.append('#d97706')    # 中等遗漏
            else:
                colors.append('#b45309')    # 冷号
        
        bars = ax.bar(nums, missing, color=colors, alpha=0.85, width=0.75,
                     edgecolor='#92400e', linewidth=0.5)
        
        ax.axhline(y=avg_missing, color=self.accent_color, linestyle='-', linewidth=2,
                  label=f'平均遗漏期数 ({avg_missing:.1f})')
        if max_missing > 0:
            ax.axhline(y=max_missing, color='#7c2d12', linestyle=':', linewidth=1.5,
                      alpha=0.8, label=f'最大遗漏期数 ({max_missing})')
        
        # 标注遗漏值
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=8, fontweight='bold',
                    color=self.text_color)
        
        ax.set_title(title, fontsize=18, pad=25, fontweight='bold', color=self.text_color)
        ax.set_xlabel('红球号码 (1-33)', fontsize=13, labelpad=15)
        ax.set_ylabel('遗漏期数', fontsize=13, labelpad=15)
        ax.set_xticks(nums)
        ax.set_xticklabels([str(n) for n in nums], fontsize=10)
        ax.tick_params(axis='both', colors=self.text_color)
        
        # 增强网格线
        ax.grid(True, axis='y', linestyle='-', alpha=0.4, color=self.grid_color, linewidth=1)
        ax.grid(True, axis='x', linestyle=':', alpha=0.3, color=self.grid_color, linewidth=0.5)
        ax.set_axisbelow(True)
        
        ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
        ax.set_ylim(0, max_missing * 1.15 if max_missing > 0 else 10)
        
        return self._save_and_close(fig, 'red_missing.png')
    
    def plot_blue_missing(self, missing_data: Dict[int, int], title: str = '蓝球遗漏统计图') -> str:
        """
        绘制蓝球遗漏统计图
        遗漏期数：距离当前最后一期该号码未出现的期数
        """
        nums = list(missing_data.keys())
        missing = list(missing_data.values())
        avg_missing = sum(missing) / len(missing) if missing else 0
        max_missing = max(missing) if missing else 0
        
        fig, ax = plt.subplots(figsize=(14, 7), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        # 根据遗漏值设置颜色
        colors = []
        for m in missing:
            if m <= 3:
                colors.append('#8b5cf6')    # 近期出现
            elif m <= 8:
                colors.append('#7c3aed')    # 中等遗漏
            else:
                colors.append('#5b21b6')    # 冷号
        
        bars = ax.bar(nums, missing, color=colors, alpha=0.85, width=0.65,
                     edgecolor='#4c1d95', linewidth=0.5)
        
        ax.axhline(y=avg_missing, color=self.accent_color, linestyle='-', linewidth=2,
                  label=f'平均遗漏期数 ({avg_missing:.1f})')
        if max_missing > 0:
            ax.axhline(y=max_missing, color='#4c1d95', linestyle=':', linewidth=1.5,
                      alpha=0.8, label=f'最大遗漏期数 ({max_missing})')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold',
                    color=self.text_color)
        
        ax.set_title(title, fontsize=18, pad=25, fontweight='bold', color=self.text_color)
        ax.set_xlabel('蓝球号码 (1-16)', fontsize=13, labelpad=15)
        ax.set_ylabel('遗漏期数', fontsize=13, labelpad=15)
        ax.set_xticks(nums)
        ax.set_xticklabels([str(n) for n in nums], fontsize=11)
        ax.tick_params(axis='both', colors=self.text_color)
        
        ax.grid(True, axis='y', linestyle='-', alpha=0.4, color=self.grid_color, linewidth=1)
        ax.grid(True, axis='x', linestyle=':', alpha=0.3, color=self.grid_color, linewidth=0.5)
        ax.set_axisbelow(True)
        
        ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
        ax.set_ylim(0, max_missing * 1.15 if max_missing > 0 else 10)
        
        return self._save_and_close(fig, 'blue_missing.png')
    
    def get_chart_descriptions(self, summary: Dict) -> Dict[str, str]:
        """
        生成每个图表的分析说明文字
        :param summary: 分析摘要数据
        :return: 各图表说明文字字典
        """
        total_issues = summary['total_issues']
        red_freq = summary['red_freq']
        blue_freq = summary['blue_freq']
        
        descriptions = {}
        
        # 红球频率说明
        red_avg = summary['red_avg_freq']
        red_hot = summary['red_hot']
        red_cold = summary['red_cold']
        descriptions['red_frequency'] = (
            f"【图表说明】基于 {total_issues} 期开奖数据统计分析：\n"
            f"• 红球平均出现频次为 {red_avg:.1f} 次\n"
            f"• 最热门的前5个红球号码为：{', '.join(map(str, red_hot))}\n"
            f"• 最冷门的前5个红球号码为：{', '.join(map(str, red_cold))}\n"
            f"• 红色柱子表示高于平均值，浅红色表示低于平均值\n"
            f"• 理论上每个红球出现概率约为 {(6/33*100):.1f}%"
        )
        
        # 蓝球频率说明
        blue_avg = summary['blue_avg_freq']
        blue_hot = summary['blue_hot']
        blue_cold = summary['blue_cold']
        descriptions['blue_frequency'] = (
            f"【图表说明】基于 {total_issues} 期开奖数据统计分析：\n"
            f"• 蓝球平均出现频次为 {blue_avg:.1f} 次\n"
            f"• 最热门的前5个蓝球号码为：{', '.join(map(str, blue_hot))}\n"
            f"• 最冷门的前5个蓝球号码为：{', '.join(map(str, blue_cold))}\n"
            f"• 深蓝色柱子表示高于平均值，浅蓝色表示低于平均值\n"
            f"• 理论上每个蓝球出现概率约为 {(1/16*100):.1f}%"
        )
        
        # 红球走势说明
        descriptions['red_trend'] = (
            f"【图表说明】最近50期红球号码出现走势：\n"
            f"• 红色圆点表示该号码在对应期数中开出\n"
            f"• 灰色点表示该号码当期未开出\n"
            f"• 可观察号码的连出、间隔、冷热趋势\n"
            f"• 横向看每期开奖结果，纵向看单个号码走势"
        )
        
        # 蓝球走势说明
        descriptions['blue_trend'] = (
            f"【图表说明】最近50期蓝球号码出现走势：\n"
            f"• 蓝色圆点表示该号码在对应期数中开出\n"
            f"• 灰色点表示该号码当期未开出\n"
            f"• 蓝球走势相对独立，可关注奇偶、大小分布规律\n"
            f"• 蓝球共16个号码，理论上每16期应轮循一次"
        )
        
        # 红球遗漏说明
        red_missing = summary['red_missing']
        max_red_missing = max(red_missing.values())
        hot_missing_red = [k for k, v in sorted(red_missing.items(), key=lambda x: x[1])[:3]]
        cold_missing_red = [k for k, v in sorted(red_missing.items(), key=lambda x: x[1], reverse=True)[:3]]
        descriptions['red_missing'] = (
            f"【图表说明】红球当前遗漏期数统计（截至最后一期）：\n"
            f"• 目前遗漏期数最多的红球是：{cold_missing_red[0]} 号（已遗漏 {max_red_missing} 期）\n"
            f"• 近期刚开出的热门红球：{', '.join(map(str, hot_missing_red))}\n"
            f"• 颜色越深表示遗漏期数越长，可关注回补机会\n"
            f"• 历史最大遗漏通常不超过50期（仅供参考）"
        )
        
        # 蓝球遗漏说明
        blue_missing = summary['blue_missing']
        max_blue_missing = max(blue_missing.values())
        hot_missing_blue = [k for k, v in sorted(blue_missing.items(), key=lambda x: x[1])[:3]]
        cold_missing_blue = [k for k, v in sorted(blue_missing.items(), key=lambda x: x[1], reverse=True)[:3]]
        descriptions['blue_missing'] = (
            f"【图表说明】蓝球当前遗漏期数统计（截至最后一期）：\n"
            f"• 目前遗漏期数最多的蓝球是：{cold_missing_blue[0]} 号（已遗漏 {max_blue_missing} 期）\n"
            f"• 近期刚开出的热门蓝球：{', '.join(map(str, hot_missing_blue))}\n"
            f"• 颜色越深表示遗漏期数越长\n"
            f"• 蓝球历史最大遗漏通常不超过30-40期"
        )
        
        return descriptions
    
    def generate_all_charts(self, analyzer, issues: List[str]) -> Dict[str, str]:
        """
        生成所有图表
        :param analyzer: SSQAnalyzer实例
        :param issues: 期号列表
        :return: 图表文件路径字典
        """
        logger.info("开始生成图表...")
        
        red_freq = analyzer.get_red_frequency()
        blue_freq = analyzer.get_blue_frequency()
        red_trend = analyzer.get_red_trend()
        blue_trend = analyzer.get_blue_trend()
        red_missing, blue_missing = analyzer.get_missing_stats()
        
        chart_files = {
            'red_frequency': self.plot_red_frequency(red_freq),
            'blue_frequency': self.plot_blue_frequency(blue_freq),
            'red_trend': self.plot_red_trend(red_trend, issues),
            'blue_trend': self.plot_blue_trend(blue_trend, issues),
            'red_missing': self.plot_red_missing(red_missing),
            'blue_missing': self.plot_blue_missing(blue_missing),
        }
        
        logger.info(f"成功生成 {len(chart_files)} 个图表")
        return chart_files

def main():
    """测试可视化"""
    from data_fetcher import SSQDataFetcher
    from analyzer import SSQAnalyzer
    
    fetcher = SSQDataFetcher()
    data = fetcher.fetch_data(100)
    
    analyzer = SSQAnalyzer(data)
    issues = [item['issue'] for item in data]
    
    visualizer = SSQVisualizer()
    charts = visualizer.generate_all_charts(analyzer, issues)
    
    print("生成的图表文件:")
    for name, path in charts.items():
        print(f"  {name}: {path}")

if __name__ == '__main__':
    main()
