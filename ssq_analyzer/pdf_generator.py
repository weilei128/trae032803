#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF生成模块
将图表自动排版生成PDF文件，支持中文显示
每个图表下方添加说明文字
"""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import sys
import logging
from typing import List, Dict, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SSQPDFGenerator:
    """双色球分析报告PDF生成器"""
    
    def __init__(self, output_path: str = 'ssq_analysis_report.pdf'):
        """
        初始化PDF生成器
        :param output_path: PDF输出路径
        """
        self.output_path = output_path
        self.story = []
        self.width, self.height = landscape(A4)
        
        self._register_chinese_font()
        self._create_styles()
    
    def _get_system_fonts(self) -> List[str]:
        """获取系统中文字体路径"""
        font_paths = [
            'C:/Windows/Fonts/simsun.ttc',
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/simhei.ttf',
            'C:/Windows/Fonts/msyhbd.ttc',
        ]
        
        linux_fonts = [
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        ]
        
        mac_fonts = [
            '/Library/Fonts/Songti.ttc',
            '/System/Library/Fonts/PingFang.ttc',
            '/Library/Fonts/Arial Unicode.ttf',
        ]
        
        if sys.platform.startswith('win'):
            search_paths = font_paths
        elif sys.platform.startswith('darwin'):
            search_paths = mac_fonts + font_paths
        else:
            search_paths = linux_fonts + font_paths + mac_fonts
        
        for path in search_paths:
            if os.path.exists(path):
                logger.info(f"找到中文字体: {path}")
                return [path]
        
        logger.warning("未找到中文字体")
        return []
    
    def _register_chinese_font(self):
        """注册中文字体"""
        font_files = self._get_system_fonts()
        
        if font_files:
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', font_files[0]))
                self.font_name = 'ChineseFont'
                logger.info(f"成功注册中文字体: {font_files[0]}")
            except Exception as e:
                logger.warning(f"注册中文字体失败: {e}，将使用默认字体")
                self.font_name = 'Helvetica'
        else:
            self.font_name = 'Helvetica'
            logger.warning("未找到中文字体，中文显示可能异常")
    
    def _create_styles(self):
        """创建文本样式"""
        self.styles = getSampleStyleSheet()
        
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Normal'],
            fontName=self.font_name,
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=HexColor('#2c3e50'),
            leading=30,
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Normal'],
            fontName=self.font_name,
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=15,
            textColor=HexColor('#34495e'),
            leading=22,
        )
        
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Normal'],
            fontName=self.font_name,
            fontSize=16,
            alignment=TA_LEFT,
            spaceBefore=15,
            spaceAfter=10,
            textColor=HexColor('#2c3e50'),
            leading=22,
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontName=self.font_name,
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=18,
            textColor=HexColor('#2c3e50'),
        )
        
        self.description_style = ParagraphStyle(
            'ChartDescription',
            parent=self.styles['Normal'],
            fontName=self.font_name,
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=15,
            spaceBefore=8,
            leading=16,
            textColor=HexColor('#34495e'),
            leftIndent=20,
            rightIndent=20,
        )
        
        self.table_header_style = ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontName=self.font_name,
            fontSize=11,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50'),
        )
        
        self.table_cell_style = ParagraphStyle(
            'TableCell',
            parent=self.styles['Normal'],
            fontName=self.font_name,
            fontSize=10,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50'),
        )
    
    def add_title(self, title: str):
        """添加标题"""
        self.story.append(Paragraph(title, self.title_style))
        self.story.append(Spacer(1, 0.5 * cm))
    
    def add_subtitle(self, subtitle: str):
        """添加副标题"""
        self.story.append(Paragraph(subtitle, self.subtitle_style))
        self.story.append(Spacer(1, 0.3 * cm))
    
    def add_section(self, section: str):
        """添加章节标题"""
        self.story.append(Paragraph(section, self.section_style))
        self.story.append(Spacer(1, 0.2 * cm))
    
    def add_paragraph(self, text: str):
        """添加段落"""
        self.story.append(Paragraph(text, self.body_style))
        self.story.append(Spacer(1, 0.2 * cm))
    
    def add_description(self, text: str):
        """添加图表说明文字"""
        self.story.append(Paragraph(text, self.description_style))
    
    def add_image(self, image_path: str, max_width_scale: float = 0.85, description: str = None):
        """添加图片和说明文字"""
        if not os.path.exists(image_path):
            logger.warning(f"图片不存在: {image_path}")
            return
        
        try:
            from PIL import Image as PILImage
            
            page_width = self.width
            page_height = self.height
            
            max_width = page_width * max_width_scale
            max_height = page_height * 0.55
            
            with PILImage.open(image_path) as pil_img:
                img_width, img_height = pil_img.size
            
            aspect = img_width / img_height
            
            width = max_width
            height = width / aspect
            
            if height > max_height:
                height = max_height
                width = height * aspect
            
            img = Image(image_path, width=width, height=height)
            
            self.story.append(img)
            self.story.append(Spacer(1, 0.3 * cm))
            
            if description:
                self.add_description(description)
        
        except Exception as e:
            logger.error(f"添加图片失败 {image_path}: {e}")
    
    def add_table(self, data: List[List], col_widths: List[float] = None):
        """添加表格"""
        if not data:
            return
        
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#bdc3c7')),
            ('BOX', (0, 0), (-1, -1), 1, HexColor('#2c3e50')),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#ecf0f1')),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 0), (-1, 0), self.font_name),
            ('ROWHEIGHT', (0, 0), (-1, -1), 25),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.5 * cm))
    
    def add_page_break(self):
        """添加分页"""
        self.story.append(PageBreak())
    
    def create_summary_table(self, summary: Dict) -> List[List]:
        """创建摘要表格"""
        data = [
            ['统计项', '内容'],
            ['统计期数', f"{summary['total_issues']} 期"],
            ['日期范围', f"{summary['date_range'][0]} 至 {summary['date_range'][1]}"],
            ['红球热门号码', ', '.join([f'{n:02d}' for n in summary['red_hot']])],
            ['红球冷门号码', ', '.join([f'{n:02d}' for n in summary['red_cold']])],
            ['蓝球热门号码', ', '.join([f'{n:02d}' for n in summary['blue_hot']])],
            ['蓝球冷门号码', ', '.join([f'{n:02d}' for n in summary['blue_cold']])],
            ['红球平均出现频次', f"{summary['red_avg_freq']:.1f} 次"],
            ['蓝球平均出现频次', f"{summary['blue_avg_freq']:.1f} 次"],
        ]
        return data
    
    def _get_chart_description(self, chart_type: str, summary: Dict) -> str:
        """获取图表说明文字"""
        descriptions = {
            'red_frequency': (
                f"【红球出现频次统计图说明】本图展示了统计期内所有红球号码（01-33）的出现次数。"
                f"红球每期开出6个，理论上每个号码出现概率相等。"
                f"统计期内红球平均出现{summary.get('red_avg_freq', 0):.1f}次。"
                f"热门号码（出现频次较高）: {', '.join([f'{n:02d}' for n in summary.get('red_hot', [])])}；"
                f"冷门号码（出现频次较低）: {', '.join([f'{n:02d}' for n in summary.get('red_cold', [])])}。"
                f"深色柱表示高于平均频次，浅色柱表示低于平均频次。"
            ),
            'blue_frequency': (
                f"【蓝球出现频次统计图说明】本图展示了统计期内所有蓝球号码（01-16）的出现次数。"
                f"蓝球每期开出1个，理论上每个号码出现概率相等。"
                f"统计期内蓝球平均出现{summary.get('blue_avg_freq', 0):.1f}次。"
                f"热门号码（出现频次较高）: {', '.join([f'{n:02d}' for n in summary.get('blue_hot', [])])}；"
                f"冷门号码（出现频次较低）: {', '.join([f'{n:02d}' for n in summary.get('blue_cold', [])])}。"
                f"深色柱表示高于平均频次，浅色柱表示低于平均频次。"
            ),
            'red_trend': (
                "【红球号码走势图说明】本图以热力图形式展示最近若干期红球号码的开出情况。"
                "横轴为期号（从旧到新），纵轴为红球号码01-33。"
                "红色圆点●表示该期开出了对应号码。"
                "通过此图可直观观察各号码的冷热分布、连续出现情况和遗漏期数。"
                "颜色越深表示该号码在统计期内出现频率越高。"
            ),
            'blue_trend': (
                "【蓝球号码走势图说明】本图以热力图形式展示最近若干期蓝球号码的开出情况。"
                "横轴为期号（从旧到新），纵轴为蓝球号码01-16。"
                "蓝色圆点●表示该期开出了对应号码。"
                "通过此图可观察蓝球号码的分布规律、连续出现情况和遗漏期数。"
                "颜色越深表示该号码在统计期内出现频率越高。"
            ),
            'red_missing': (
                "【红球遗漏统计图说明】遗漏期数指某号码距离上次开出到当前的期数。"
                "遗漏值越大，说明该号码越长时间未出现，可能存在回补的趋势。"
                "深色柱表示遗漏期数较高的号码，需要关注其回补可能性。"
                "浅色柱表示遗漏期数较低或刚出现过的号码。"
                "投资需谨慎，遗漏分析仅供参考。"
            ),
            'blue_missing': (
                "【蓝球遗漏统计图说明】遗漏期数指某号码距离上次开出到当前的期数。"
                "遗漏值越大，说明该号码越长时间未出现，可能存在回补的趋势。"
                "深色柱表示遗漏期数较高的号码，需要关注其回补可能性。"
                "浅色柱表示遗漏期数较低或刚出现过的号码。"
                "投资需谨慎，遗漏分析仅供参考。"
            ),
        }
        return descriptions.get(chart_type, "")
    
    def generate_report(self, summary: Dict, chart_files: Dict[str, str]):
        """
        生成完整的分析报告
        :param summary: 分析摘要
        :param chart_files: 图表文件路径
        """
        logger.info("开始生成PDF报告...")
        
        try:
            self.add_title("双色球开奖数据分析报告")
            
            gen_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.add_subtitle(f"数据范围: {summary['total_issues']} 期 ({summary['date_range'][0]} 至 {summary['date_range'][1]})")
            self.add_subtitle(f"报告生成时间: {gen_time}")
            
            self.add_paragraph(
                "本报告自动生成，包含号码走势分析、出现频率统计、遗漏分析等内容。"
                "数据来源于官方开奖记录，仅供参考，不构成任何投资建议。"
                "彩票有风险，投注需谨慎。"
            )
            
            self.add_section("一、数据摘要")
            summary_table = self.create_summary_table(summary)
            self.add_table(summary_table, col_widths=[5 * cm, 12 * cm])
            
            self.add_paragraph(
                f"【摘要说明】本报告统计了最近{summary['total_issues']}期双色球开奖数据。"
                f"热门号码指统计期内出现频次较高的号码，冷门号码指出现频次较低的号码。"
                f"红球号码范围01-33，每期开出6个；蓝球号码范围01-16，每期开出1个。"
            )
            
            self.add_page_break()
            self.add_section("二、红球号码分析")
            
            self.add_paragraph("2.1 红球出现频率统计")
            if 'red_frequency' in chart_files:
                desc = self._get_chart_description('red_frequency', summary)
                self.add_image(chart_files['red_frequency'], max_width_scale=0.85, description=desc)
            
            self.add_page_break()
            self.add_paragraph("2.2 红球号码走势图")
            if 'red_trend' in chart_files:
                desc = self._get_chart_description('red_trend', summary)
                self.add_image(chart_files['red_trend'], max_width_scale=0.85, description=desc)
            
            self.add_page_break()
            self.add_paragraph("2.3 红球遗漏统计")
            if 'red_missing' in chart_files:
                desc = self._get_chart_description('red_missing', summary)
                self.add_image(chart_files['red_missing'], max_width_scale=0.85, description=desc)
            
            self.add_page_break()
            self.add_section("三、蓝球号码分析")
            
            self.add_paragraph("3.1 蓝球出现频率统计")
            if 'blue_frequency' in chart_files:
                desc = self._get_chart_description('blue_frequency', summary)
                self.add_image(chart_files['blue_frequency'], max_width_scale=0.85, description=desc)
            
            self.add_page_break()
            self.add_paragraph("3.2 蓝球号码走势图")
            if 'blue_trend' in chart_files:
                desc = self._get_chart_description('blue_trend', summary)
                self.add_image(chart_files['blue_trend'], max_width_scale=0.85, description=desc)
            
            self.add_page_break()
            self.add_paragraph("3.3 蓝球遗漏统计")
            if 'blue_missing' in chart_files:
                desc = self._get_chart_description('blue_missing', summary)
                self.add_image(chart_files['blue_missing'], max_width_scale=0.85, description=desc)
            
            self.add_page_break()
            self.add_section("四、免责声明")
            
            self.add_paragraph(
                "1. 本报告所有数据均来源于官方公开开奖信息，数据真实可靠。"
            )
            self.add_paragraph(
                "2. 本报告的分析结果仅供娱乐参考，不构成任何投资建议。"
            )
            self.add_paragraph(
                "3. 彩票具有随机性，历史数据分析无法预测未来开奖结果。"
            )
            self.add_paragraph(
                "4. 请理性购彩，量力而行，切勿沉迷。"
            )
            self.add_paragraph(
                "5. 未满18周岁请勿购买彩票。"
            )
            
            self.add_paragraph("")
            self.add_paragraph(
                f"报告生成时间: {gen_time}"
            )
            self.add_paragraph(
                "工具版本: v2.0 (支持500期数据分析)"
            )
            
            doc = SimpleDocTemplate(
                self.output_path,
                pagesize=landscape(A4),
                rightMargin=1.5 * cm,
                leftMargin=1.5 * cm,
                topMargin=1.5 * cm,
                bottomMargin=1.5 * cm,
            )
            
            doc.build(self.story)
            logger.info(f"PDF报告已生成: {self.output_path}")
        
        except Exception as e:
            logger.error(f"生成PDF报告失败: {e}")
            raise


def main():
    """测试PDF生成"""
    pdf_gen = SSQPDFGenerator('test_report.pdf')
    
    summary = {
        'total_issues': 500,
        'date_range': ('2023-01-01', '2024-12-31'),
        'red_hot': [1, 2, 3, 4, 5],
        'red_cold': [29, 30, 31, 32, 33],
        'blue_hot': [1, 2, 3],
        'blue_cold': [14, 15, 16],
        'red_avg_freq': 90.9,
        'blue_avg_freq': 31.25,
    }
    
    chart_files = {
        'red_frequency': 'charts/red_frequency.png',
        'blue_frequency': 'charts/blue_frequency.png',
    }
    
    pdf_gen.generate_report(summary, chart_files)
    print("测试PDF生成完成")


if __name__ == '__main__':
    main()
