#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球数据分析模块
对红球、蓝球进行统计分析
"""
import pandas as pd
import numpy as np
from collections import Counter
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SSQAnalyzer:
    """双色球数据分析器"""
    
    def __init__(self, data: List[Dict]):
        """
        初始化分析器
        :param data: 数据列表，每个元素包含 issue, date, red_balls, blue_ball
        """
        if not data:
            raise ValueError("数据不能为空")
        
        self.data = data
        self.df = self._to_dataframe()
        logger.info(f"分析器初始化完成，共 {len(data)} 期数据")
    
    def _to_dataframe(self) -> pd.DataFrame:
        """将数据转换为DataFrame格式"""
        try:
            rows = []
            for item in self.data:
                row = {
                    'issue': item['issue'],
                    'date': item['date'],
                    'blue_ball': item['blue_ball'],
                }
                # 添加红球列
                for i, ball in enumerate(item['red_balls'], 1):
                    row[f'red_{i}'] = ball
                rows.append(row)
            
            df = pd.DataFrame(rows)
            df['date'] = pd.to_datetime(df['date'])
            return df
        except Exception as e:
            logger.error(f"数据转换失败: {e}")
            raise
    
    def get_red_frequency(self) -> Dict[int, int]:
        """
        统计红球出现频率
        :return: 字典，键为号码(1-33)，值为出现次数
        """
        try:
            red_balls = []
            for item in self.data:
                red_balls.extend(item['red_balls'])
            
            counter = Counter(red_balls)
            # 确保所有号码都有统计（1-33）
            for num in range(1, 34):
                if num not in counter:
                    counter[num] = 0
            
            return dict(sorted(counter.items()))
        except Exception as e:
            logger.error(f"红球频率统计失败: {e}")
            raise
    
    def get_blue_frequency(self) -> Dict[int, int]:
        """
        统计蓝球出现频率
        :return: 字典，键为号码(1-16)，值为出现次数
        """
        try:
            blue_balls = [item['blue_ball'] for item in self.data]
            counter = Counter(blue_balls)
            # 确保所有号码都有统计（1-16）
            for num in range(1, 17):
                if num not in counter:
                    counter[num] = 0
            
            return dict(sorted(counter.items()))
        except Exception as e:
            logger.error(f"蓝球频率统计失败: {e}")
            raise
    
    def get_red_trend(self) -> Dict[int, List[int]]:
        """
        获取红球走势数据（每期的红球位置）
        :return: 字典，键为号码，值为每期是否出现的列表（1表示出现，0表示未出现）
        """
        try:
            trend = {}
            for num in range(1, 34):
                trend[num] = []
            
            for item in reversed(self.data):  # 逆序，最早的在前
                balls_present = set(item['red_balls'])
                for num in range(1, 34):
                    # 1表示出现，0表示未出现
                    trend[num].append(1 if num in balls_present else 0)
            
            return trend
        except Exception as e:
            logger.error(f"红球走势分析失败: {e}")
            raise
    
    def get_blue_trend(self) -> Dict[int, List[int]]:
        """
        获取蓝球走势数据
        :return: 字典，键为号码，值为每期是否出现的列表
        """
        try:
            trend = {}
            for num in range(1, 17):
                trend[num] = []
            
            for item in reversed(self.data):
                blue = item['blue_ball']
                for num in range(1, 17):
                    trend[num].append(1 if num == blue else 0)
            
            return trend
        except Exception as e:
            logger.error(f"蓝球走势分析失败: {e}")
            raise
    
    def get_missing_stats(self) -> Tuple[Dict[int, int], Dict[int, int]]:
        """
        获取遗漏统计（每个号码距上次出现的间隔）
        :return: (红球遗漏字典, 蓝球遗漏字典)
        """
        try:
            red_missing = {num: 0 for num in range(1, 34)}
            blue_missing = {num: 0 for num in range(1, 17)}
            
            # 追踪红球遗漏
            red_seen = {num: False for num in range(1, 34)}
            for item in self.data:
                balls = set(item['red_balls'])
                for num in range(1, 34):
                    if not red_seen[num]:
                        if num in balls:
                            red_seen[num] = True
                        else:
                            red_missing[num] += 1
            
            # 追踪蓝球遗漏
            blue_seen = {num: False for num in range(1, 17)}
            for item in self.data:
                blue = item['blue_ball']
                for num in range(1, 17):
                    if not blue_seen[num]:
                        if num == blue:
                            blue_seen[num] = True
                        else:
                            blue_missing[num] += 1
            
            return red_missing, blue_missing
        except Exception as e:
            logger.error(f"遗漏统计失败: {e}")
            raise
    
    def get_hot_cold_numbers(self, top_n: int = 5) -> Tuple[List[int], List[int], List[int], List[int]]:
        """
        获取冷热号
        :param top_n: 热门/冷门号码数量
        :return: (红球热门, 红球冷门, 蓝球热门, 蓝球冷门)
        """
        try:
            red_freq = self.get_red_frequency()
            blue_freq = self.get_blue_frequency()
            
            # 红球冷热
            red_sorted = sorted(red_freq.items(), key=lambda x: x[1], reverse=True)
            red_hot = [num for num, _ in red_sorted[:top_n]]
            red_cold = [num for num, _ in red_sorted[-top_n:]]
            
            # 蓝球冷热
            blue_sorted = sorted(blue_freq.items(), key=lambda x: x[1], reverse=True)
            blue_hot = [num for num, _ in blue_sorted[:top_n]]
            blue_cold = [num for num, _ in blue_sorted[-top_n:]]
            
            return red_hot, red_cold, blue_hot, blue_cold
        except Exception as e:
            logger.error(f"冷热号分析失败: {e}")
            raise
    
    def get_consecutive_stats(self) -> Dict[str, List[int]]:
        """
        获取连号统计
        :return: 连号统计字典
        """
        try:
            stats = {
                '2连号': [],
                '3连号': [],
                '4连号及以上': [],
            }
            
            for item in self.data:
                balls = sorted(item['red_balls'])
                consecutive_count = 1
                max_consecutive = 1
                
                for i in range(1, len(balls)):
                    if balls[i] == balls[i-1] + 1:
                        consecutive_count += 1
                        max_consecutive = max(max_consecutive, consecutive_count)
                    else:
                        consecutive_count = 1
                
                if max_consecutive >= 4:
                    stats['4连号及以上'].append(1)
                elif max_consecutive == 3:
                    stats['3连号'].append(1)
                elif max_consecutive == 2:
                    stats['2连号'].append(1)
            
            return stats
        except Exception as e:
            logger.error(f"连号统计失败: {e}")
            raise
    
    def get_summary(self) -> Dict:
        """
        获取数据摘要
        :return: 包含各项统计数据的字典
        """
        try:
            red_freq = self.get_red_frequency()
            blue_freq = self.get_blue_frequency()
            red_missing, blue_missing = self.get_missing_stats()
            red_hot, red_cold, blue_hot, blue_cold = self.get_hot_cold_numbers()
            
            return {
                'total_issues': len(self.data),
                'date_range': (self.df['date'].min().strftime('%Y-%m-%d'), 
                              self.df['date'].max().strftime('%Y-%m-%d')),
                'red_freq': red_freq,
                'blue_freq': blue_freq,
                'red_missing': red_missing,
                'blue_missing': blue_missing,
                'red_hot': red_hot,
                'red_cold': red_cold,
                'blue_hot': blue_hot,
                'blue_cold': blue_cold,
                'red_avg_freq': sum(red_freq.values()) / 33,
                'blue_avg_freq': sum(blue_freq.values()) / 16,
            }
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            raise

def main():
    """测试分析器"""
    from data_fetcher import SSQDataFetcher
    
    try:
        fetcher = SSQDataFetcher()
        data = fetcher.fetch_data(50)
        
        analyzer = SSQAnalyzer(data)
        summary = analyzer.get_summary()
        
        print(f"统计期数: {summary['total_issues']}")
        print(f"日期范围: {summary['date_range']}")
        print(f"热门红球: {summary['red_hot']}")
        print(f"冷门红球: {summary['red_cold']}")
        print(f"热门蓝球: {summary['blue_hot']}")
        print(f"冷门蓝球: {summary['blue_cold']}")
    except Exception as e:
        logger.error(f"测试失败: {e}")

if __name__ == '__main__':
    main()
