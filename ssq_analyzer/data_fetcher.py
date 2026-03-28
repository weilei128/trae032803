#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球数据获取模块
从官方/可信接口获取最新开奖数据
支持获取最多500期历史数据
"""
import requests
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SSQDataFetcher:
    """双色球数据获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.cwl.gov.cn/ygkj/wqkjgg/ssq/',
        })
        self.max_retries = 3
        self.retry_delay = 2
    
    def _get_random_delay(self):
        """随机延迟，避免请求过于频繁"""
        time.sleep(random.uniform(0.5, 1.5))
    
    def _make_request(self, url: str, params: dict = None, timeout: int = 15) -> Optional[requests.Response]:
        """发送HTTP请求，带重试机制"""
        for attempt in range(self.max_retries):
            try:
                self._get_random_delay()
                response = self.session.get(url, params=params, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时，第 {attempt + 1} 次重试...")
                time.sleep(self.retry_delay)
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败: {e}，第 {attempt + 1} 次重试...")
                time.sleep(self.retry_delay)
        return None
    
    def fetch_from_official_api(self, count: int = 500) -> Optional[List[Dict]]:
        """
        从中国福利彩票官方API获取数据
        官方网站: https://www.cwl.gov.cn
        """
        try:
            url = "https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"
            
            all_data = []
            page_size = 100
            pages_needed = (count + page_size - 1) // page_size
            
            for page in range(1, pages_needed + 1):
                params = {
                    'name': 'ssq',
                    'issueCount': page_size,
                    'pageNo': page,
                    'pageSize': page_size,
                    'systemType': 'PC',
                }
                
                response = self._make_request(url, params)
                if not response:
                    continue
                
                data = response.json()
                
                if data.get('state') == 0 and 'result' in data:
                    for item in data['result']:
                        try:
                            red_balls = list(map(int, item['red'].split(',')))
                            blue_ball = int(item['blue'])
                            all_data.append({
                                'issue': item['code'],
                                'date': item['date'],
                                'red_balls': red_balls,
                                'blue_ball': blue_ball,
                            })
                        except (KeyError, ValueError) as e:
                            logger.warning(f"解析数据项失败: {e}")
                            continue
                
                if len(all_data) >= count:
                    break
            
            if all_data:
                logger.info(f"从官方接口获取到 {len(all_data)} 期数据")
                return all_data[:count]
        
        except Exception as e:
            logger.warning(f"官方接口获取失败: {e}")
        
        return None
    
    def fetch_from_opencai_api(self, count: int = 500) -> Optional[List[Dict]]:
        """
        从开奖网API获取数据
        备用接口
        """
        try:
            url = "https://www.opencai.com/lottery/ssq/"
            
            response = self._make_request(url, timeout=20)
            if not response:
                return None
            
            text = response.text
            
            import re
            json_match = re.search(r'var\s+historyData\s*=\s*(\[[\s\S]*?\]);', text)
            
            if json_match:
                data = json.loads(json_match.group(1))
                result_list = []
                for item in data[:count]:
                    try:
                        balls = item.get('red', '').split(',')
                        red_balls = [int(b.strip()) for b in balls if b.strip().isdigit()]
                        blue_ball = int(item.get('blue', 0))
                        
                        if len(red_balls) == 6 and 1 <= blue_ball <= 16:
                            result_list.append({
                                'issue': item.get('issue', ''),
                                'date': item.get('date', ''),
                                'red_balls': sorted(red_balls),
                                'blue_ball': blue_ball,
                            })
                    except (KeyError, ValueError) as e:
                        continue
                
                if result_list:
                    logger.info(f"从开奖网获取到 {len(result_list)} 期数据")
                    return result_list
        
        except Exception as e:
            logger.warning(f"开奖网接口获取失败: {e}")
        
        return None
    
    def fetch_from_zhcw_api(self, count: int = 500) -> Optional[List[Dict]]:
        """
        从中彩网API获取数据
        另一个备用接口
        """
        try:
            url = "https://data.zhcw.com/data/ssq/historyData.json"
            
            response = self._make_request(url, timeout=20)
            if not response:
                return None
            
            data = response.json()
            
            if isinstance(data, list):
                result_list = []
                for item in data[:count]:
                    try:
                        if isinstance(item, dict):
                            red_str = item.get('red', '') or item.get('redBall', '')
                            blue_str = item.get('blue', '') or item.get('blueBall', '')
                            
                            red_balls = [int(b.strip()) for b in red_str.split(',') if b.strip().isdigit()]
                            blue_ball = int(blue_str) if blue_str.isdigit() else 0
                            
                            if len(red_balls) == 6 and 1 <= blue_ball <= 16:
                                result_list.append({
                                    'issue': item.get('issue', '') or item.get('code', ''),
                                    'date': item.get('date', '') or item.get('openDate', ''),
                                    'red_balls': sorted(red_balls),
                                    'blue_ball': blue_ball,
                                })
                    except (KeyError, ValueError, AttributeError) as e:
                        continue
                
                if result_list:
                    logger.info(f"从中彩网获取到 {len(result_list)} 期数据")
                    return result_list
        
        except Exception as e:
            logger.warning(f"中彩网接口获取失败: {e}")
        
        return None
    
    def generate_mock_data(self, count: int = 500) -> List[Dict]:
        """
        生成模拟数据（用于演示和测试）
        当所有API都不可用时使用
        模拟真实开奖规律
        """
        logger.info(f"生成 {count} 期模拟数据用于演示")
        mock_data = []
        
        base_date = datetime.now()
        issue_num = 2024001
        
        for i in range(count):
            days_ago = (count - i) * 3
            issue_date = base_date - timedelta(days=days_ago)
            date_str = issue_date.strftime('%Y-%m-%d')
            
            year = issue_date.year
            issue_in_year = (count - i)
            issue_no = f"{year}{issue_in_year:03d}"
            
            red_balls = []
            while len(red_balls) < 6:
                ball = random.randint(1, 33)
                if ball not in red_balls:
                    red_balls.append(ball)
            red_balls.sort()
            
            blue_ball = random.randint(1, 16)
            
            mock_data.append({
                'issue': issue_no,
                'date': date_str,
                'red_balls': red_balls,
                'blue_ball': blue_ball,
            })
        
        logger.info(f"成功生成 {len(mock_data)} 期模拟数据")
        return mock_data
    
    def fetch_data(self, count: int = 500, use_mock_on_failure: bool = True) -> List[Dict]:
        """
        主数据获取方法，依次尝试各个接口
        
        Args:
            count: 需要获取的期数，默认500期
            use_mock_on_failure: API失败时是否使用模拟数据
        
        Returns:
            数据列表，按日期倒序排列（最新的在前）
        
        Raises:
            Exception: 当无法获取数据且不使用模拟数据时
        """
        if count <= 0:
            raise ValueError("获取期数必须大于0")
        
        if count > 500:
            logger.warning(f"请求期数 {count} 超过最大限制500，将获取500期数据")
            count = 500
        
        logger.info(f"开始获取最近 {count} 期双色球数据...")
        
        apis = [
            ("官方接口", self.fetch_from_official_api),
            ("开奖网", self.fetch_from_opencai_api),
            ("中彩网", self.fetch_from_zhcw_api),
        ]
        
        for api_name, api_func in apis:
            try:
                logger.info(f"尝试从 {api_name} 获取数据...")
                result = api_func(count)
                
                if result and len(result) > 0:
                    result = sorted(result, key=lambda x: x.get('date', ''), reverse=True)
                    unique_issues = {}
                    for item in result:
                        issue = item.get('issue', '')
                        if issue and issue not in unique_issues:
                            unique_issues[issue] = item
                    result = list(unique_issues.values())
                    
                    logger.info(f"成功从 {api_name} 获取 {len(result)} 期数据")
                    return result[:count]
            
            except Exception as e:
                logger.warning(f"{api_name} 获取失败: {e}")
                continue
        
        if use_mock_on_failure:
            logger.warning("所有API接口获取失败，将使用模拟数据")
            return self.generate_mock_data(count)
        
        raise Exception("无法获取双色球数据，请检查网络连接或稍后重试")


def main():
    """测试数据获取"""
    fetcher = SSQDataFetcher()
    
    print("=" * 60)
    print("    双色球数据获取测试")
    print("=" * 60)
    
    try:
        data = fetcher.fetch_data(500)
        
        print(f"\n成功获取 {len(data)} 期数据")
        print(f"\n最新5期开奖数据:")
        print("-" * 60)
        
        for item in data[:5]:
            red_str = ', '.join([f"{b:02d}" for b in item['red_balls']])
            print(f"期号: {item['issue']}  日期: {item['date']}")
            print(f"红球: {red_str}  蓝球: {item['blue_ball']:02d}")
            print("-" * 60)
        
        print(f"\n最早5期开奖数据:")
        print("-" * 60)
        
        for item in data[-5:]:
            red_str = ', '.join([f"{b:02d}" for b in item['red_balls']])
            print(f"期号: {item['issue']}  日期: {item['date']}")
            print(f"红球: {red_str}  蓝球: {item['blue_ball']:02d}")
            print("-" * 60)
    
    except Exception as e:
        print(f"错误: {e}")


if __name__ == '__main__':
    main()
