#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球可视化模块
绘制号码走势图、出现频次统计图
支持中文标注、网格线，每个图表下方添加说明文字
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from typing import List, Dict, Tuple, Optional
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mpl.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Zen Hei', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False
mpl.rcParams['font.size'] = 10


class SSQVisualizer:
    """双色球可视化器"""
    
    def __init__(self, output_dir: str = 'charts'):
        """
        初始化可视化器
        :param output_dir: 图表输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.red_color = '#e74c3c'
        self.blue_color = '#3498db'
        self.grid_color = '#bdc3c7'
        self.bg_color = '#f8f9fa'
        self.text_color = '#2c3e50'
    
    def _add_chart_description(self, ax: plt.Axes, fig: plt.Figure, description: str, 
                                y_offset: float = -0.12):
        """
        在图表下方添加说明文字
        :param ax: 坐标轴对象
        :param fig: 图形对象
        :param description: 说明文字
        :param y_offset: Y轴偏移量
        """
        fig.text(0.5, y_offset, description, 
                ha='center', va='top', fontsize=10, 
                color=self.text_color, style='italic',
                wrap=True)
    
    def _save_and_close(self, fig: plt.Figure, filename: str) -> str:
        """保存并关闭图片"""
        filepath = os.path.join(self.output_dir, filename)
        fig.tight_layout()
        fig.subplots_adjust(bottom=0.15)
        fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor=self.bg_color)
        plt.close(fig)
        logger.info(f"图表已保存: {filepath}")
        return filepath
    
    def plot_red_frequency(self, freq_data: Dict[int, int], 
                           title: str = '红球出现频次统计图',
                           description: Optional[str] = None) -> str:
        """
        绘制红球出现频次统计图
        :param freq_data: 频次数据字典
        :param title: 图表标题
        :param description: 图表说明文字
        """
        nums = list(freq_data.keys())
        freqs = list(freq_data.values())
        avg_freq = sum(freqs) / len(freqs) if freqs else 0
        max_freq = max(freqs) if freqs else 0
        min_freq = min(freqs) if freqs else 0
        
        fig, ax = plt.subplots(figsize=(16, 9), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        colors = [self.red_color if f >= avg_freq else '#f5b7b1' for f in freqs]
        bars = ax.bar(nums, freqs, color=colors, alpha=0.85, width=0.7, edgecolor='white', linewidth=0.5)
        
        ax.axhline(y=avg_freq, color='#2c3e50', linestyle='--', linewidth=2, alpha=0.7, 
                  label=f'平均频次: {avg_freq:.1f}次')
        
        for bar, freq in zip(bars, freqs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(freq)}',
                    ha='center', va='bottom', fontsize=8, fontweight='bold',
                    color=self.text_color)
        
        ax.set_title(title, fontsize=18, pad=20, fontweight='bold', color=self.text_color)
        ax.set_xlabel('红球号码 (01-33)', fontsize=13, labelpad=10)
        ax.set_ylabel('出现次数', fontsize=13, labelpad=10)
        ax.set_xticks(nums)
        ax.set_xticklabels([f'{n:02d}' for n in nums], rotation=0, fontsize=9)
        
        ax.grid(True, axis='y', linestyle='--', alpha=0.6, color=self.grid_color, linewidth=0.8)
        ax.grid(True, axis='x', linestyle=':', alpha=0.3, color=self.grid_color, linewidth=0.5)
        
        ax.set_ylim(0, max(freqs) * 1.15 if max(freqs) > 0 else 10)
        ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.grid_color)
        ax.spines['bottom'].set_color(self.grid_color)
        
        if description is None:
            hot_nums = sorted(freq_data.items(), key=lambda x: x[1], reverse=True)[:5]
            cold_nums = sorted(freq_data.items(), key=lambda x: x[1])[:5]
            description = (f"【图表说明】红球号码范围01-33，每期开出6个红球。"
                          f"统计期内，红球平均出现{avg_freq:.1f}次。"
                          f"热门号码: {', '.join([f'{n[0]:02d}({n[1]}次)' for n in hot_nums])}；"
                          f"冷门号码: {', '.join([f'{n[0]:02d}({n[1]}次)' for n in cold_nums])}。"
                          f"深色柱表示高于平均频次，浅色柱表示低于平均频次。")
        
        self._add_chart_description(ax, fig, description, y_offset=-0.10)
        
        return self._save_and_close(fig, 'red_frequency.png')
    
    def plot_blue_frequency(self, freq_data: Dict[int, int], 
                            title: str = '蓝球出现频次统计图',
                            description: Optional[str] = None) -> str:
        """
        绘制蓝球出现频次统计图
        :param freq_data: 频次数据字典
        :param title: 图表标题
        :param description: 图表说明文字
        """
        nums = list(freq_data.keys())
        freqs = list(freq_data.values())
        avg_freq = sum(freqs) / len(freqs) if freqs else 0
        
        fig, ax = plt.subplots(figsize=(14, 7), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        colors = [self.blue_color if f >= avg_freq else '#aed6f1' for f in freqs]
        bars = ax.bar(nums, freqs, color=colors, alpha=0.85, width=0.6, edgecolor='white', linewidth=0.5)
        
        ax.axhline(y=avg_freq, color='#2c3e50', linestyle='--', linewidth=2, alpha=0.7,
                  label=f'平均频次: {avg_freq:.1f}次')
        
        for bar, freq in zip(bars, freqs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                    f'{int(freq)}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold',
                    color=self.text_color)
        
        ax.set_title(title, fontsize=18, pad=20, fontweight='bold', color=self.text_color)
        ax.set_xlabel('蓝球号码 (01-16)', fontsize=13, labelpad=10)
        ax.set_ylabel('出现次数', fontsize=13, labelpad=10)
        ax.set_xticks(nums)
        ax.set_xticklabels([f'{n:02d}' for n in nums], rotation=0, fontsize=11)
        
        ax.grid(True, axis='y', linestyle='--', alpha=0.6, color=self.grid_color, linewidth=0.8)
        ax.grid(True, axis='x', linestyle=':', alpha=0.3, color=self.grid_color, linewidth=0.5)
        
        ax.set_ylim(0, max(freqs) * 1.18 if max(freqs) > 0 else 10)
        ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.grid_color)
        ax.spines['bottom'].set_color(self.grid_color)
        
        if description is None:
            hot_nums = sorted(freq_data.items(), key=lambda x: x[1], reverse=True)[:3]
            cold_nums = sorted(freq_data.items(), key=lambda x: x[1])[:3]
            description = (f"【图表说明】蓝球号码范围01-16，每期开出1个蓝球。"
                          f"统计期内，蓝球平均出现{avg_freq:.1f}次。"
                          f"热门号码: {', '.join([f'{n[0]:02d}({n[1]}次)' for n in hot_nums])}；"
                          f"冷门号码: {', '.join([f'{n[0]:02d}({n[1]}次)' for n in cold_nums])}。"
                          f"深色柱表示高于平均频次，浅色柱表示低于平均频次。")
        
        self._add_chart_description(ax, fig, description, y_offset=-0.12)
        
        return self._save_and_close(fig, 'blue_frequency.png')
    
    def plot_red_trend(self, trend_data: Dict[int, List[int]], issues: List[str], 
                       title: str = '红球号码走势图',
                       description: Optional[str] = None) -> str:
        """
        绘制红球号码走势图
        :param trend_data: 走势数据字典
        :param issues: 期号列表
        :param title: 图表标题
        :param description: 图表说明文字
        """
        num_count = 33
        period_count = min(len(issues), 60)
        
        matrix = np.zeros((num_count, period_count))
        for num in range(1, 34):
            values = trend_data[num][-period_count:] if len(trend_data[num]) >= period_count else trend_data[num]
            if len(values) < period_count:
                values = [0] * (period_count - len(values)) + values
            matrix[num-1] = values
        
        display_issues = issues[:period_count]
        display_issues_reversed = display_issues[::-1]
        
        fig, ax = plt.subplots(figsize=(18, 12), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        cmap = plt.cm.Reds
        im = ax.imshow(matrix, aspect='auto', cmap=cmap, vmin=0, vmax=1, alpha=0.9)
        
        ax.set_yticks(np.arange(num_count))
        ax.set_yticklabels([f'{n:02d}' for n in range(1, 34)], fontsize=9)
        ax.set_xticks(np.arange(period_count))
        ax.set_xticklabels([issue[-4:] for issue in display_issues_reversed],
                          rotation=90, fontsize=7)
        
        for i in range(num_count):
            for j in range(period_count):
                if matrix[i, j] == 1:
                    ax.text(j, i, '●', ha='center', va='center', color='white', fontsize=7, fontweight='bold')
        
        ax.set_title(title, fontsize=18, pad=20, fontweight='bold', color=self.text_color)
        ax.set_xlabel('期号 (从左到右：旧 → 新)', fontsize=13, labelpad=10)
        ax.set_ylabel('红球号码', fontsize=13, labelpad=10)
        
        ax.set_xticks(np.arange(period_count + 1) - 0.5, minor=True)
        ax.set_yticks(np.arange(num_count + 1) - 0.5, minor=True)
        ax.grid(which='minor', color='white', linestyle='-', linewidth=0.8)
        ax.tick_params(which='minor', bottom=False, left=False)
        
        cbar = plt.colorbar(im, ax=ax, shrink=0.6, aspect=30)
        cbar.set_label('出现状态', fontsize=11)
        cbar.set_ticks([0, 1])
        cbar.set_ticklabels(['未出现', '出现'])
        
        if description is None:
            description = (f"【图表说明】红球走势图展示最近{period_count}期各红球号码的开出情况。"
                          f"横轴为期号（从旧到新），纵轴为红球号码01-33。"
                          f"红色圆点●表示该期开出了对应号码，颜色越深表示出现频率越高。"
                          f"通过此图可直观观察各号码的冷热分布和连续出现情况。")
        
        self._add_chart_description(ax, fig, description, y_offset=-0.08)
        
        return self._save_and_close(fig, 'red_trend.png')
    
    def plot_blue_trend(self, trend_data: Dict[int, List[int]], issues: List[str],
                        title: str = '蓝球号码走势图',
                        description: Optional[str] = None) -> str:
        """
        绘制蓝球号码走势图
        :param trend_data: 走势数据字典
        :param issues: 期号列表
        :param title: 图表标题
        :param description: 图表说明文字
        """
        num_count = 16
        period_count = min(len(issues), 60)
        
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
        
        cmap = plt.cm.Blues
        im = ax.imshow(matrix, aspect='auto', cmap=cmap, vmin=0, vmax=1, alpha=0.9)
        
        ax.set_yticks(np.arange(num_count))
        ax.set_yticklabels([f'{n:02d}' for n in range(1, 17)], fontsize=11)
        ax.set_xticks(np.arange(period_count))
        ax.set_xticklabels([issue[-4:] for issue in display_issues_reversed],
                          rotation=90, fontsize=7)
        
        for i in range(num_count):
            for j in range(period_count):
                if matrix[i, j] == 1:
                    ax.text(j, i, '●', ha='center', va='center', color='white', fontsize=9, fontweight='bold')
        
        ax.set_title(title, fontsize=18, pad=20, fontweight='bold', color=self.text_color)
        ax.set_xlabel('期号 (从左到右：旧 → 新)', fontsize=13, labelpad=10)
        ax.set_ylabel('蓝球号码', fontsize=13, labelpad=10)
        
        ax.set_xticks(np.arange(period_count + 1) - 0.5, minor=True)
        ax.set_yticks(np.arange(num_count + 1) - 0.5, minor=True)
        ax.grid(which='minor', color='white', linestyle='-', linewidth=0.8)
        ax.tick_params(which='minor', bottom=False, left=False)
        
        cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=20)
        cbar.set_label('出现状态', fontsize=11)
        cbar.set_ticks([0, 1])
        cbar.set_ticklabels(['未出现', '出现'])
        
        if description is None:
            description = (f"【图表说明】蓝球走势图展示最近{period_count}期各蓝球号码的开出情况。"
                          f"横轴为期号（从旧到新），纵轴为蓝球号码01-16。"
                          f"蓝色圆点●表示该期开出了对应号码，颜色越深表示出现频率越高。"
                          f"通过此图可观察蓝球号码的分布规律和遗漏情况。")
        
        self._add_chart_description(ax, fig, description, y_offset=-0.12)
        
        return self._save_and_close(fig, 'blue_trend.png')
    
    def plot_red_missing(self, missing_data: Dict[int, int], 
                         title: str = '红球遗漏统计图',
                         description: Optional[str] = None) -> str:
        """
        绘制红球遗漏统计图
        :param missing_data: 遗漏数据字典
        :param title: 图表标题
        :param description: 图表说明文字
        """
        nums = list(missing_data.keys())
        missing = list(missing_data.values())
        avg_missing = sum(missing) / len(missing) if missing else 0
        
        fig, ax = plt.subplots(figsize=(16, 9), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        colors = ['#e67e22' if m >= avg_missing else '#f5cba7' for m in missing]
        bars = ax.bar(nums, missing, color=colors, alpha=0.85, width=0.7, edgecolor='white', linewidth=0.5)
        
        ax.axhline(y=avg_missing, color='#2c3e50', linestyle='--', linewidth=2, alpha=0.7,
                  label=f'平均遗漏: {avg_missing:.1f}期')
        
        for bar, miss in zip(bars, missing):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                    f'{int(miss)}',
                    ha='center', va='bottom', fontsize=8, fontweight='bold',
                    color=self.text_color)
        
        ax.set_title(title, fontsize=18, pad=20, fontweight='bold', color=self.text_color)
        ax.set_xlabel('红球号码 (01-33)', fontsize=13, labelpad=10)
        ax.set_ylabel('遗漏期数', fontsize=13, labelpad=10)
        ax.set_xticks(nums)
        ax.set_xticklabels([f'{n:02d}' for n in nums], rotation=0, fontsize=9)
        
        ax.grid(True, axis='y', linestyle='--', alpha=0.6, color=self.grid_color, linewidth=0.8)
        ax.grid(True, axis='x', linestyle=':', alpha=0.3, color=self.grid_color, linewidth=0.5)
        
        ax.set_ylim(0, max(missing) * 1.18 if max(missing) > 0 else 10)
        ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.grid_color)
        ax.spines['bottom'].set_color(self.grid_color)
        
        if description is None:
            high_missing = sorted(missing_data.items(), key=lambda x: x[1], reverse=True)[:5]
            low_missing = sorted(missing_data.items(), key=lambda x: x[1])[:5]
            description = (f"【图表说明】遗漏期数指某号码距离上次开出到当前的期数。"
                          f"红球平均遗漏{avg_missing:.1f}期。"
                          f"高遗漏号码: {', '.join([f'{n[0]:02d}({n[1]}期)' for n in high_missing])}；"
                          f"低遗漏号码: {', '.join([f'{n[0]:02d}({n[1]}期)' for n in low_missing])}。"
                          f"深色柱表示遗漏期数较高，需关注回补可能性。")
        
        self._add_chart_description(ax, fig, description, y_offset=-0.10)
        
        return self._save_and_close(fig, 'red_missing.png')
    
    def plot_blue_missing(self, missing_data: Dict[int, int], 
                          title: str = '蓝球遗漏统计图',
                          description: Optional[str] = None) -> str:
        """
        绘制蓝球遗漏统计图
        :param missing_data: 遗漏数据字典
        :param title: 图表标题
        :param description: 图表说明文字
        """
        nums = list(missing_data.keys())
        missing = list(missing_data.values())
        avg_missing = sum(missing) / len(missing) if missing else 0
        
        fig, ax = plt.subplots(figsize=(14, 7), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        colors = ['#9b59b6' if m >= avg_missing else '#d7bde2' for m in missing]
        bars = ax.bar(nums, missing, color=colors, alpha=0.85, width=0.6, edgecolor='white', linewidth=0.5)
        
        ax.axhline(y=avg_missing, color='#2c3e50', linestyle='--', linewidth=2, alpha=0.7,
                  label=f'平均遗漏: {avg_missing:.1f}期')
        
        for bar, miss in zip(bars, missing):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                    f'{int(miss)}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold',
                    color=self.text_color)
        
        ax.set_title(title, fontsize=18, pad=20, fontweight='bold', color=self.text_color)
        ax.set_xlabel('蓝球号码 (01-16)', fontsize=13, labelpad=10)
        ax.set_ylabel('遗漏期数', fontsize=13, labelpad=10)
        ax.set_xticks(nums)
        ax.set_xticklabels([f'{n:02d}' for n in nums], rotation=0, fontsize=11)
        
        ax.grid(True, axis='y', linestyle='--', alpha=0.6, color=self.grid_color, linewidth=0.8)
        ax.grid(True, axis='x', linestyle=':', alpha=0.3, color=self.grid_color, linewidth=0.5)
        
        ax.set_ylim(0, max(missing) * 1.18 if max(missing) > 0 else 10)
        ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.grid_color)
        ax.spines['bottom'].set_color(self.grid_color)
        
        if description is None:
            high_missing = sorted(missing_data.items(), key=lambda x: x[1], reverse=True)[:3]
            low_missing = sorted(missing_data.items(), key=lambda x: x[1])[:3]
            description = (f"【图表说明】遗漏期数指某号码距离上次开出到当前的期数。"
                          f"蓝球平均遗漏{avg_missing:.1f}期。"
                          f"高遗漏号码: {', '.join([f'{n[0]:02d}({n[1]}期)' for n in high_missing])}；"
                          f"低遗漏号码: {', '.join([f'{n[0]:02d}({n[1]}期)' for n in low_missing])}。"
                          f"深色柱表示遗漏期数较高，需关注回补可能性。")
        
        self._add_chart_description(ax, fig, description, y_offset=-0.12)
        
        return self._save_and_close(fig, 'blue_missing.png')
    
    def generate_all_charts(self, analyzer, issues: List[str]) -> Dict[str, str]:
        """
        生成所有图表
        :param analyzer: SSQAnalyzer实例
        :param issues: 期号列表
        :return: 图表文件路径字典
        """
        logger.info("开始生成图表...")
        
        try:
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
        
        except Exception as e:
            logger.error(f"生成图表失败: {e}")
            raise


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
