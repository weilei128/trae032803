#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF生成模块
将图表自动排版生成PDF文件，支持中文显示，每个图表下方带有分析说明
"""
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, Color
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import sys
import logging
from typing import List, Dict, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SSQPDFGenerator:
    """双色球分析报告PDF生成器 - 简化版"""
    
    # 颜色配置
    COLORS = {
        'primary': '#dc2626',      # 主色调红色
        'secondary': '#2563eb',    # 次要色调蓝色
        'accent': '#059669',       # 强调色绿色
        'text': '#1f2937',         # 文本色
        'text_light': '#6b7280',   # 浅色文本
    }
    
    def __init__(self, output_path: str = 'ssq_analysis_report.pdf'):
        """
        初始化PDF生成器
        :param output_path: PDF输出路径
        """
        self.output_path = output_path
        self.story = []
        self.page_width, self.page_height = portrait(A4)  # 竖向A4
        
        # 可用页面尺寸（减去边距）
        self.margin = 1.5 * cm
        self.usable_width = self.page_width - 2 * self.margin
        self.usable_height = self.page_height - 2 * self.margin
        
        # 注册中文字体
        self.chinese_font_name = self._register_chinese_font()
        
        # 创建样式
        self._create_styles()
    
    def _get_system_fonts(self) -> List[str]:
        """获取系统中文字体路径 - 增强搜索"""
        # Windows字体路径（按优先级排序）
        win_fonts = [
            'C:/Windows/Fonts/msyh.ttc',        # 微软雅黑（优先）
            'C:/Windows/Fonts/msyhbd.ttc',      # 微软雅黑粗体
            'C:/Windows/Fonts/simhei.ttf',      # 黑体
            'C:/Windows/Fonts/simsun.ttc',      # 宋体
            'C:/Windows/Fonts/msyhl.ttc',       # 微软雅黑Light
            'C:/Windows/Fonts/kaiu.ttf',        # 楷体
        ]
        
        # Linux字体路径
        linux_fonts = [
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
            '/usr/share/fonts/TTF/NotoSansCJK-Regular.ttf',
            '/usr/share/fonts/TTF/DejaVuSans.ttf',
        ]
        
        # macOS字体路径
        mac_fonts = [
            '/Library/Fonts/PingFang.ttc',
            '/Library/Fonts/PingFangSC.ttf',
            '/Library/Fonts/Hiragino Sans GB.ttc',
            '/Library/Fonts/Songti.ttc',
            '/Library/Fonts/Arial Unicode.ttf',
        ]
        
        # 其他可能的字体位置
        other_fonts = [
            '/usr/local/share/fonts/simsun.ttc',
            '/opt/local/share/fonts/simsun.ttc',
        ]
        
        # 根据平台确定搜索顺序
        if sys.platform.startswith('win'):
            search_paths = win_fonts + linux_fonts + mac_fonts + other_fonts
        elif sys.platform.startswith('darwin'):
            search_paths = mac_fonts + win_fonts + linux_fonts + other_fonts
        else:
            search_paths = linux_fonts + win_fonts + mac_fonts + other_fonts
        
        # 查找存在的字体文件
        found_fonts = []
        for path in search_paths:
            if os.path.exists(path):
                found_fonts.append(path)
                logger.debug(f"找到字体: {path}")
        
        return found_fonts
    
    def _register_chinese_font(self) -> str:
        """注册中文字体 - 增强版"""
        font_files = self._get_system_fonts()
        default_font = 'Helvetica'
        
        if font_files:
            for font_path in font_files[:3]:  # 尝试前3个字体
                try:
                    # 注册字体
                    font_name = 'ChineseFont'
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    
                    # 尝试注册粗体（如果可用）
                    try:
                        bold_path = font_path.replace('.ttf', 'bd.ttf').replace('.ttc', 'bd.ttc')
                        if os.path.exists(bold_path):
                            pdfmetrics.registerFont(TTFont('ChineseFont-Bold', bold_path))
                            registerFontFamily('ChineseFont', 
                                              normal='ChineseFont',
                                              bold='ChineseFont-Bold')
                    except:
                        pass
                    
                    logger.info(f"成功注册中文字体: {font_path}")
                    return font_name
                except Exception as e:
                    logger.warning(f"注册字体失败 {font_path}: {e}")
                    continue
        
        logger.warning("未能找到合适的中文字体，中文显示可能异常，建议安装微软雅黑或文泉驿字体")
        return default_font
    
    def _create_styles(self):
        """创建文本样式 - 增强版"""
        self.styles = getSampleStyleSheet()
        base_font = self.chinese_font_name
        bold_font = 'ChineseFont-Bold' if 'ChineseFont-Bold' in pdfmetrics.getRegisteredFontNames() else base_font
        
        # 标题样式（封面）
        self.title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Normal'],
            fontName=bold_font,
            fontSize=28,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=HexColor(self.COLORS['primary']),
            leading=36,
        )
        
        # 大标题样式（章节）
        self.heading1_style = ParagraphStyle(
            'Heading1',
            parent=self.styles['Normal'],
            fontName=bold_font,
            fontSize=18,
            alignment=TA_LEFT,
            spaceAfter=15,
            spaceBefore=20,
            textColor=HexColor(self.COLORS['text']),
            leading=24,
        )
        
        # 中标题样式（子章节）
        self.heading2_style = ParagraphStyle(
            'Heading2',
            parent=self.styles['Normal'],
            fontName=bold_font,
            fontSize=14,
            alignment=TA_LEFT,
            spaceAfter=10,
            spaceBefore=15,
            textColor=HexColor(self.COLORS['secondary']),
            leading=20,
        )
        
        # 副标题样式
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontName=base_font,
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=15,
            textColor=HexColor(self.COLORS['text_light']),
            leading=18,
        )
        
        # 正文样式
        self.body_style = ParagraphStyle(
            'Body',
            parent=self.styles['Normal'],
            fontName=base_font,
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=18,
            textColor=HexColor(self.COLORS['text']),
            firstLineIndent=22,  # 首行缩进
        )
        
        # 图表说明样式
        self.caption_style = ParagraphStyle(
            'Caption',
            parent=self.styles['Normal'],
            fontName=base_font,
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=12,
            spaceBefore=8,
            leading=16,
            textColor=HexColor(self.COLORS['text_light']),
            leftIndent=10,
            rightIndent=10,
        )
        
        # 表格内容样式
        self.table_content_style = ParagraphStyle(
            'TableContent',
            parent=self.styles['Normal'],
            fontName=base_font,
            fontSize=10,
            alignment=TA_CENTER,
            leading=14,
            textColor=HexColor(self.COLORS['text']),
        )
        
        # 页脚样式
        self.footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontName=base_font,
            fontSize=9,
            alignment=TA_CENTER,
            textColor=HexColor(self.COLORS['text_light']),
        )
    
    def add_title(self, title: str):
        """添加大标题（封面）"""
        self.story.append(Paragraph(title, self.title_style))
        self.story.append(Spacer(1, 1.0 * cm))
    
    def add_heading1(self, text: str):
        """添加一级标题"""
        self.story.append(Paragraph(f"◆ {text}", self.heading1_style))
        self.story.append(Spacer(1, 0.3 * cm))
    
    def add_heading2(self, text: str):
        """添加二级标题"""
        self.story.append(Paragraph(f"◇ {text}", self.heading2_style))
        self.story.append(Spacer(1, 0.2 * cm))
    
    def add_subtitle(self, subtitle: str):
        """添加副标题"""
        self.story.append(Paragraph(subtitle, self.subtitle_style))
        self.story.append(Spacer(1, 0.5 * cm))
    
    def add_paragraph(self, text: str):
        """添加段落"""
        # 将换行符转换为HTML换行
        text = text.replace('\n', '<br/>')
        self.story.append(Paragraph(text, self.body_style))
        self.story.append(Spacer(1, 0.2 * cm))
    
    def add_caption(self, text: str):
        """添加图表说明文字"""
        text = text.replace('\n', '<br/>')
        self.story.append(Paragraph(text, self.caption_style))
        self.story.append(Spacer(1, 0.3 * cm))
    
    def add_spacer(self, height: float = 0.5):
        """
        添加空白间距
        :param height: 间距高度（单位：cm）
        """
        self.story.append(Spacer(1, height * cm))
    
    def add_image_with_caption(self, image_path: str, caption: str = "", max_width_scale: float = 0.85):
        """
        添加带说明的图片
        :param image_path: 图片路径
        :param caption: 图片说明文字
        :param max_width_scale: 最大宽度比例（相对于页面宽度）
        """
        if not os.path.exists(image_path):
            logger.warning(f"图片不存在: {image_path}")
            return
        
        try:
            # 计算最大可用尺寸
            max_width = self.usable_width * max_width_scale
            max_height = self.usable_height * 0.55  # 限制高度为页面55%
            
            # 使用PIL获取图片尺寸
            from PIL import Image as PILImage
            with PILImage.open(image_path) as pil_img:
                img_width, img_height = pil_img.size
            
            # 计算缩放比例
            aspect = img_width / img_height
            
            # 初始按最大宽度计算
            width = max_width
            height = width / aspect
            
            # 如果高度超标，按高度缩放
            if height > max_height:
                height = max_height
                width = height * aspect
            
            # 创建Image对象
            img = Image(image_path, width=width, height=height)
            
            # 将图片和说明放在一起，避免分页
            content = [img]
            if caption:
                content.append(Spacer(1, 0.1 * cm))
                content.append(Paragraph(caption.replace('\n', '<br/>'), self.caption_style))
            
            self.story.append(KeepTogether(content))
            self.story.append(Spacer(1, 0.4 * cm))
            
        except Exception as e:
            logger.error(f"添加图片失败 {image_path}: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def add_table(self, data: List[List], col_widths: List[float] = None):
        """添加表格"""
        if not data:
            return
        
        # 转换单元格内容为Paragraph
        formatted_data = []
        for i, row in enumerate(data):
            formatted_row = []
            for cell in row:
                if isinstance(cell, str):
                    cell = cell.replace('\n', '<br/>')
                    formatted_row.append(Paragraph(cell, self.table_content_style))
                else:
                    formatted_row.append(cell)
            formatted_data.append(formatted_row)
        
        table = Table(formatted_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.chinese_font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor(self.COLORS['text'])),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor(self.COLORS['grid'])),
            ('BOX', (0, 0), (-1, -1), 1, HexColor(self.COLORS['border'])),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f3f4f6')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
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
            ['统计期数', str(summary['total_issues']) + ' 期'],
            ['日期范围', f"{summary['date_range'][0]} 至 {summary['date_range'][1]}"],
            ['红球热门号码', ', '.join(map(str, summary['red_hot']))],
            ['红球冷门号码', ', '.join(map(str, summary['red_cold']))],
            ['蓝球热门号码', ', '.join(map(str, summary['blue_hot']))],
            ['蓝球冷门号码', ', '.join(map(str, summary['blue_cold']))],
            ['红球平均出现频次', f"{summary['red_avg_freq']:.1f} 次"],
            ['蓝球平均出现频次', f"{summary['blue_avg_freq']:.1f} 次"],
        ]
        return data
    
    def create_frequency_table(self, freq_data: Dict[int, int], is_red: bool = True) -> List[List]:
        """创建频率统计表格"""
        nums = list(freq_data.keys())
        freqs = list(freq_data.values())
        
        # 按行组织数据
        data = []
        header = [f'{i}' for i in range(1, 12)]  # 11列
        data.append(header)
        
        if is_red:
            # 红球33个号码，分成3行
            for row in range(3):
                row_data = []
                for col in range(11):
                    idx = row * 11 + col
                    if idx < 33:
                        row_data.append(f"{nums[idx]}\n({freqs[idx]})")
                    else:
                        row_data.append('')
                data.append(row_data)
        else:
            # 蓝球16个号码，分成2行
            for row in range(2):
                row_data = []
                for col in range(8):
                    idx = row * 8 + col
                    if idx < 16:
                        row_data.append(f"{nums[idx]}\n({freqs[idx]})")
                    else:
                        row_data.append('')
                data.append(row_data)
        
        return data
    
    def generate_report(self, summary: Dict, chart_files: Dict[str, str], chart_descriptions: Dict[str, str] = None):
        """
        生成完整的分析报告 - 简化版
        :param summary: 分析摘要
        :param chart_files: 图表文件路径
        :param chart_descriptions: 图表说明文字字典
        """
        logger.info("开始生成PDF报告...")
        
        # ========== 封面页 ==========
        self.add_title("双色球开奖数据分析报告")
        self.add_subtitle(f"数据范围: {summary['total_issues']} 期历史开奖数据")
        self.add_subtitle(f"统计周期: {summary['date_range'][0]} 至 {summary['date_range'][1]}")
        self.add_spacer()
        
        intro_text = """
        本报告为双色球号码统计分析报告，基于历史开奖数据自动生成。
        报告包含号码出现频率统计、走势分析、遗漏期数统计等内容。
        
        【温馨提示】彩票开奖结果完全随机，本分析仅作统计参考，不构成任何投注建议。
        """
        self.add_paragraph(intro_text.strip())
        
        # ========== 数据摘要 ==========
        self.add_page_break()
        self.add_heading1("一、数据摘要")
        self.add_spacer()
        
        summary_table = self.create_summary_table(summary)
        self.add_table(summary_table, col_widths=[4.5 * cm, 10 * cm])
        self.add_spacer()
        
        # 热门/冷门号码提示
        hot_cold_text = f"""
        热门红球（前5）：{', '.join(map(str, summary['red_hot']))}
        冷门红球（后5）：{', '.join(map(str, summary['red_cold']))}
        热门蓝球（前5）：{', '.join(map(str, summary['blue_hot']))}
        冷门蓝球（后5）：{', '.join(map(str, summary['blue_cold']))}
        """
        self.add_paragraph(hot_cold_text.strip())
        
        # ========== 红球图表 ==========
        self.add_page_break()
        self.add_heading1("二、红球号码分析")
        self.add_spacer()
        
        # 红球频率
        self.add_heading2("2.1 红球出现频率统计")
        if 'red_frequency' in chart_files:
            caption = chart_descriptions.get('red_frequency', '') if chart_descriptions else ''
            self.add_image_with_caption(chart_files['red_frequency'], caption)
        
        self.add_page_break()
        # 红球走势
        self.add_heading2("2.2 红球号码走势")
        if 'red_trend' in chart_files:
            caption = chart_descriptions.get('red_trend', '') if chart_descriptions else ''
            self.add_image_with_caption(chart_files['red_trend'], caption, max_width_scale=0.95)
        
        self.add_page_break()
        # 红球遗漏
        self.add_heading2("2.3 红球遗漏统计")
        if 'red_missing' in chart_files:
            caption = chart_descriptions.get('red_missing', '') if chart_descriptions else ''
            self.add_image_with_caption(chart_files['red_missing'], caption)
        
        # ========== 蓝球图表 ==========
        self.add_page_break()
        self.add_heading1("三、蓝球号码分析")
        self.add_spacer()
        
        # 蓝球频率
        self.add_heading2("3.1 蓝球出现频率统计")
        if 'blue_frequency' in chart_files:
            caption = chart_descriptions.get('blue_frequency', '') if chart_descriptions else ''
            self.add_image_with_caption(chart_files['blue_frequency'], caption)
        
        self.add_page_break()
        # 蓝球走势
        self.add_heading2("3.2 蓝球号码走势")
        if 'blue_trend' in chart_files:
            caption = chart_descriptions.get('blue_trend', '') if chart_descriptions else ''
            self.add_image_with_caption(chart_files['blue_trend'], caption, max_width_scale=0.95)
        
        self.add_page_break()
        # 蓝球遗漏
        self.add_heading2("3.3 蓝球遗漏统计")
        if 'blue_missing' in chart_files:
            caption = chart_descriptions.get('blue_missing', '') if chart_descriptions else ''
            self.add_image_with_caption(chart_files['blue_missing'], caption)
        
        # ========== 页脚 ==========
        self.add_page_break()
        footer_text = "报告生成时间: {} | 数据来源: 中国福利彩票发行管理中心".format(
            summary.get('generate_time', '未知')
        )
        self.story.append(Spacer(1, 20 * cm))
        self.story.append(Paragraph(footer_text, self.footer_style))
        
        # 生成PDF - 使用竖向A4
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=portrait(A4),
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin,
            title="双色球数据分析报告",
            author="SSQ Analyzer",
        )
        
        try:
            doc.build(self.story)
            logger.info(f"PDF报告已生成: {os.path.abspath(self.output_path)}")
        except Exception as e:
            logger.error(f"生成PDF失败: {e}", exc_info=True)
            raise

def main():
    """测试PDF生成"""
    # 简单测试
    pdf_gen = SSQPDFGenerator('test_report.pdf')
    pdf_gen.add_title("测试报告")
    pdf_gen.add_paragraph("这是一个测试PDF文档，用于验证中文显示。")
    
    summary = {
        'total_issues': 200,
        'date_range': ('2023-01-01', '2024-03-28'),
        'red_hot': [1, 2, 3, 4, 5],
        'red_cold': [33, 32, 31, 30, 29],
        'blue_hot': [1, 2, 3, 4, 5],
        'blue_cold': [16, 15, 14, 13, 12],
        'red_avg_freq': 6.06,
        'blue_avg_freq': 12.5,
        'red_freq': {i: 10 for i in range(1, 34)},
        'blue_freq': {i: 5 for i in range(1, 17)},
    }
    
    pdf_gen.create_summary_table(summary)
    
    try:
        doc = SimpleDocTemplate(
            'test_report.pdf',
            pagesize=landscape(A4),
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        doc.build(pdf_gen.story)
        print("测试PDF生成成功!")
    except Exception as e:
        print(f"测试PDF生成失败: {e}")

if __name__ == '__main__':
    main()
