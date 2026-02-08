"""PDF到Markdown格式转换器"""

from typing import Any, Optional, Dict
from hos_m2f.converters.base_converter import BaseConverter

# 延迟导入PyPDF2
pypdf2_available = False
PdfReader = None


def _check_pypdf2():
    """检查PyPDF2是否可用"""
    global pypdf2_available, PdfReader
    if not pypdf2_available:
        try:
            from PyPDF2 import PdfReader
            pypdf2_available = True
        except ImportError as e:
            print(f"Warning: PyPDF2 not available: {e}")
            print("PDF to Markdown conversion is disabled.")


class PDFToMDConverter(BaseConverter):
    """PDF到Markdown格式转换器"""
    
    def convert(self, input_content: bytes, options: Optional[Dict[str, Any]] = None) -> bytes:
        """将PDF转换为Markdown
        
        Args:
            input_content: PDF文件的二进制数据
            options: 转换选项
            
        Returns:
            bytes: Markdown文件的二进制数据
        """
        # 检查PyPDF2是否可用
        _check_pypdf2()
        if not pypdf2_available:
            raise ImportError("PyPDF2 is not available. PDF to Markdown conversion is disabled.")
        
        if options is None:
            options = {}
        
        # 解析PDF内容
        markdown_content = self._parse_pdf(input_content, options)
        
        return markdown_content.encode('utf-8')
    
    def _parse_pdf(self, pdf_content: bytes, options: Dict[str, Any]) -> str:
        """解析PDF内容并转换为Markdown"""
        import io
        
        # 创建PDF阅读器
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        
        # 提取文本
        text_content = []
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            if text:
                text_content.append(text)
        
        # 合并文本
        full_text = '\n\n'.join(text_content)
        
        # 转换为Markdown
        markdown_content = self._text_to_markdown(full_text, options)
        
        return markdown_content
    
    def _text_to_markdown(self, text: str, options: Dict[str, Any]) -> str:
        """将纯文本转换为Markdown"""
        import re
        
        # 分割行
        lines = text.split('\n')
        
        # 处理标题
        markdown_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                markdown_lines.append('')
                continue
            
            # 简单的标题识别
            # 假设以数字开头的行可能是标题
            if re.match(r'^\d+\.', line):
                # 检查数字级别
                match = re.match(r'^(\d+)\.', line)
                if match:
                    level = len(match.group(1).split('.'))
                    if level <= 6:
                        markdown_lines.append(f"{'#' * level} {line}")
                        continue
            
            # 检查是否是大写标题
            if line.isupper() and len(line) < 50:
                markdown_lines.append(f'## {line}')
                continue
            
            # 普通行
            markdown_lines.append(line)
        
        # 合并行
        markdown_content = '\n'.join(markdown_lines)
        
        # 处理列表
        markdown_content = re.sub(r'^\s*\-\s(.*)$', r'* \1', markdown_content, flags=re.MULTILINE)
        markdown_content = re.sub(r'^\s*\*\s(.*)$', r'* \1', markdown_content, flags=re.MULTILINE)
        
        # 处理粗体
        markdown_content = re.sub(r'\b([A-Z]{3,})\b', r'**\1**', markdown_content)
        
        return markdown_content
    
    def get_supported_formats(self) -> tuple:
        """获取支持的格式"""
        return ('pdf', 'md')