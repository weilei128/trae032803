#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球可视化模块
绘制号码走势图、出现频次统计图
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from typing import List, Dict, Tuple
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置中文显示
mpl.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'WenQuanYi Zen Hei', 'Microsoft YaHei']
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
        
        # 颜色配置
        self.red_color = '#e74c3c'
        self.blue_color = '#3498db'
        self.grid_color = '#bdc3c7'
        self.bg_color = '#f8f9fa'
    
    def _save_and_close(self, fig, filename: str):
        """保存并关闭图片"""
        filepath = os.path.join(self.output_dir, filename)
        fig.tight_layout()
        fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor=self.bg_color)
        plt.close(fig)
        logger.info(f"图表已保存: {filepath}")
        return filepath
    
    def plot_red_frequency(self, freq_data: Dict[int, int], title: str = '红球出现频次统计') -> str:
        """
        绘制红球出现频次统计图
        文字说明：展示1-33号红球在统计期数内的出现次数，红色柱子表示各号码出现频次，虚线表示平均出现频次
        """
        nums = list(freq_data.keys())
        freqs = list(freq_data.values())
        avg_freq = sum(freqs) / len(freqs)
        
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        # 绘制柱状图
        bars = ax.bar(nums, freqs, color=self.red_color, alpha=0.8, width=0.7)
        
        # 添加平均线
        ax.axhline(y=avg_freq, color='#2c3e50', linestyle='--', alpha=0.6, 
                  label=f'平均频次 ({avg_freq:.1f})')
        
        # 在柱子上标注数值
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=8)
        
        ax.set_title(title, fontsize=16, pad=20, fontweight='bold')
        ax.set_xlabel('红球号码', fontsize=12)
        ax.set_ylabel('出现次数', fontsize=12)
        ax.set_xticks(nums)
        ax.set_xticklabels([str(n) for n in nums], rotation=0)
        ax.grid(True, axis='y', linestyle='--', alpha=0.6, color=self.grid_color)
        ax.legend()
        
        # 设置y轴范围
        ax.set_ylim(0, max(freqs) * 1.1)
        
        # 添加文字说明
        description = f"""图表说明：
- 统计范围：最近500期开奖数据
- 横轴：红球号码（01-33）
- 纵轴：各号码出现次数
- 黑色虚线：平均出现频次（{avg_freq:.1f}次）
- 柱子高度越高，表示该号码出现频率越高"""
        fig.text(0.5, -0.02, description, ha='center', va='top', fontsize=9, 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        return self._save_and_close(fig, 'red_frequency.png')
    
    def plot_blue_frequency(self, freq_data: Dict[int, int], title: str = '蓝球出现频次统计') -> str:
        """
        绘制蓝球出现频次统计图
        文字说明：展示1-16号蓝球在统计期数内的出现次数，蓝色柱子表示各号码出现频次
        """
        nums = list(freq_data.keys())
        freqs = list(freq_data.values())
        avg_freq = sum(freqs) / len(freqs)
        
        fig, ax = plt.subplots(figsize=(12, 6), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        bars = ax.bar(nums, freqs, color=self.blue_color, alpha=0.8, width=0.6)
        
        ax.axhline(y=avg_freq, color='#2c3e50', linestyle='--', alpha=0.6,
                  label=f'平均频次 ({avg_freq:.1f})')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9)
        
        ax.set_title(title, fontsize=16, pad=20, fontweight='bold')
        ax.set_xlabel('蓝球号码', fontsize=12)
        ax.set_ylabel('出现次数', fontsize=12)
        ax.set_xticks(nums)
        ax.grid(True, axis='y', linestyle='--', alpha=0.6, color=self.grid_color)
        ax.legend()
        ax.set_ylim(0, max(freqs) * 1.15)
        
        # 添加文字说明
        description = f"""图表说明：
- 统计范围：最近500期开奖数据
- 横轴：蓝球号码（01-16）
- 纵轴：各号码出现次数
- 黑色虚线：平均出现频次（{avg_freq:.1f}次）
- 柱子高度越高，表示该号码出现频率越高"""
        fig.text(0.5, -0.02, description, ha='center', va='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
        
        return self._save_and_close(fig, 'blue_frequency.png')
    
    def plot_red_trend(self, trend_data: Dict[int, List[int]], issues: List[str], 
                       title: str = '红球号码走势图') -> str:
        """
        绘制红球号码走势图
        文字说明：热力图形式展示最近50期各红球号码的出现情况，白色圆点表示该期该号码出现
        """
        num_count = 33  # 红球号码数量
        period_count = min(len(issues), 50)  # 显示最近50期
        
        # 准备数据矩阵
        matrix = np.zeros((num_count, period_count))
        for num in range(1, 34):
            # 取最新的period_count期数据（trend_data是从旧到新）
            values = trend_data[num][-period_count:] if len(trend_data[num]) >= period_count else trend_data[num]
            # 如果数据不足，填充
            if len(values) < period_count:
                values = [0] * (period_count - len(values)) + values
            matrix[num-1] = values
        
        # 准备显示的期号（最新的在前）
        display_issues = issues[:period_count]
        display_issues_reversed = display_issues[::-1]  # 反转，旧到新
        
        fig, ax = plt.subplots(figsize=(16, 10), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        # 使用热力图显示
        im = ax.imshow(matrix, aspect='auto', cmap='Reds', vmin=0, vmax=1, alpha=0.9)
        
        # 设置标签
        ax.set_yticks(np.arange(num_count))
        ax.set_yticklabels([str(n) for n in range(1, 34)], fontsize=8)
        ax.set_xticks(np.arange(period_count))
        ax.set_xticklabels([issue[-4:] for issue in display_issues_reversed],  # 只显示期号后4位
                          rotation=90, fontsize=7)
        
        # 在每个格子中标记是否出现
        for i in range(num_count):
            for j in range(period_count):
                if matrix[i, j] == 1:
                    ax.text(j, i, '●', ha='center', va='center', color='white', fontsize=6)
        
        ax.set_title(title, fontsize=16, pad=20, fontweight='bold')
        ax.set_xlabel('期号 (从左到右：旧 -> 新)', fontsize=12)
        ax.set_ylabel('红球号码', fontsize=12)
        
        # 添加网格线
        ax.set_xticks(np.arange(period_count + 1) - 0.5, minor=True)
        ax.set_yticks(np.arange(num_count + 1) - 0.5, minor=True)
        ax.grid(which='minor', color='white', linestyle='-', linewidth=0.5)
        ax.tick_params(which='minor', bottom=False, left=False)
        
        # 添加文字说明
        description = """图表说明：
- 显示范围：最近50期开奖数据
- 横轴：期号（从左到右，由旧到新）
- 纵轴：红球号码（01-33）
- 红色格子：该号码在该期出现
- 深色格子：该号码在该期未出现
- 白色圆点：标记出现位置"""
        fig.text(0.5, -0.02, description, ha='center', va='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        return self._save_and_close(fig, 'red_trend.png')
    
    def plot_blue_trend(self, trend_data: Dict[int, List[int]], issues: List[str],
                        title: str = '蓝球号码走势图') -> str:
        """
        绘制蓝球号码走势图
        文字说明：热力图形式展示最近50期各蓝球号码的出现情况
        """
        num_count = 16  # 蓝球号码数量
        period_count = min(len(issues), 50)
        
        matrix = np.zeros((num_count, period_count))
        for num in range(1, 17):
            values = trend_data[num][-period_count:] if len(trend_data[num]) >= period_count else trend_data[num]
            if len(values) < period_count:
                values = [0] * (period_count - len(values)) + values
            matrix[num-1] = values
        
        display_issues = issues[:period_count]
        display_issues_reversed = display_issues[::-1]
        
        fig, ax = plt.subplots(figsize=(16, 7), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        im = ax.imshow(matrix, aspect='auto', cmap='Blues', vmin=0, vmax=1, alpha=0.9)
        
        ax.set_yticks(np.arange(num_count))
        ax.set_yticklabels([str(n) for n in range(1, 17)], fontsize=10)
        ax.set_xticks(np.arange(period_count))
        ax.set_xticklabels([issue[-4:] for issue in display_issues_reversed],
                          rotation=90, fontsize=7)
        
        # 在每个格子中标记是否出现
        for i in range(num_count):
            for j in range(period_count):
                if matrix[i, j] == 1:
                    ax.text(j, i, '●', ha='center', va='center', color='white', fontsize=8)
        
        ax.set_title(title, fontsize=16, pad=20, fontweight='bold')
        ax.set_xlabel('期号 (从左到右：旧 -> 新)', fontsize=12)
        ax.set_ylabel('蓝球号码', fontsize=12)
        
        ax.set_xticks(np.arange(period_count + 1) - 0.5, minor=True)
        ax.set_yticks(np.arange(num_count + 1) - 0.5, minor=True)
        ax.grid(which='minor', color='white', linestyle='-', linewidth=0.5)
        ax.tick_params(which='minor', bottom=False, left=False)
        
        # 添加文字说明
        description = """图表说明：
- 显示范围：最近50期开奖数据
- 横轴：期号（从左到右，由旧到新）
- 纵轴：蓝球号码（01-16）
- 蓝色格子：该号码在该期出现
- 深色格子：该号码在该期未出现
- 白色圆点：标记出现位置"""
        fig.text(0.5, -0.02, description, ha='center', va='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
        
        return self._save_and_close(fig, 'blue_trend.png')
    
    def plot_red_missing(self, missing_data: Dict[int, int], title: str = '红球遗漏统计图') -> str:
        """
        绘制红球遗漏统计图
        文字说明：展示各红球号码距离上次出现的期数间隔，数值越大表示遗漏越久
        """
        nums = list(missing_data.keys())
        missing = list(missing_data.values())
        
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        bars = ax.bar(nums, missing, color='#e67e22', alpha=0.7, width=0.7)
        
        # 标注遗漏值
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        ax.set_title(title, fontsize=16, pad=20, fontweight='bold')
        ax.set_xlabel('红球号码', fontsize=12)
        ax.set_ylabel('遗漏期数', fontsize=12)
        ax.set_xticks(nums)
        ax.grid(True, axis='y', linestyle='--', alpha=0.6, color=self.grid_color)
        ax.set_ylim(0, max(missing) * 1.15 if max(missing) > 0 else 10)
        
        # 添加文字说明
        max_missing = max(missing) if missing else 0
        avg_missing = sum(missing) / len(missing) if missing else 0
        description = f"""图表说明：
- 统计范围：最近500期开奖数据
- 横轴：红球号码（01-33）
- 纵轴：遗漏期数（距离上次出现的期数间隔）
- 最大遗漏：{max_missing}期
- 平均遗漏：{avg_missing:.1f}期
- 遗漏值越大，表示该号码越久未出现"""
        fig.text(0.5, -0.02, description, ha='center', va='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        return self._save_and_close(fig, 'red_missing.png')
    
    def plot_blue_missing(self, missing_data: Dict[int, int], title: str = '蓝球遗漏统计图') -> str:
        """
        绘制蓝球遗漏统计图
        文字说明：展示各蓝球号码距离上次出现的期数间隔
        """
        nums = list(missing_data.keys())
        missing = list(missing_data.values())
        
        fig, ax = plt.subplots(figsize=(12, 6), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        bars = ax.bar(nums, missing, color='#9b59b6', alpha=0.7, width=0.6)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_title(title, fontsize=16, pad=20, fontweight='bold')
        ax.set_xlabel('蓝球号码', fontsize=12)
        ax.set_ylabel('遗漏期数', fontsize=12)
        ax.set_xticks(nums)
        ax.grid(True, axis='y', linestyle='--', alpha=0.6, color=self.grid_color)
        ax.set_ylim(0, max(missing) * 1.15 if max(missing) > 0 else 10)
        
        # 添加文字说明
        max_missing = max(missing) if missing else 0
        avg_missing = sum(missing) / len(missing) if missing else 0
        description = f"""图表说明：
- 统计范围：最近500期开奖数据
- 横轴：蓝球号码（01-16）
- 纵轴：遗漏期数（距离上次出现的期数间隔）
- 最大遗漏：{max_missing}期
- 平均遗漏：{avg_missing:.1f}期
- 遗漏值越大，表示该号码越久未出现"""
        fig.text(0.5, -0.02, description, ha='center', va='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='plum', alpha=0.3))
        
        return self._save_and_close(fig, 'blue_missing.png')
    
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
    visualizer = SSQVisualizer()
    
    # 测试频率图
    test_freq = {i: np.random.randint(5, 20) for i in range(1, 34)}
    visualizer.plot_red_frequency(test_freq)
    
    test_blue_freq = {i: np.random.randint(10, 40) for i in range(1, 17)}
    visualizer.plot_blue_frequency(test_blue_freq)
    
    print("测试图表生成完成")

if __name__ == '__main__':
    main()
