"""EPUB到Markdown格式转换器"""

from typing import Any, Optional, Dict
from hos_m2f.converters.base_converter import BaseConverter
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


class EPUBToMDConverter(BaseConverter):
    """EPUB到Markdown格式转换器"""
    
    def convert(self, input_content: bytes, options: Optional[Dict[str, Any]] = None) -> bytes:
        """将EPUB转换为Markdown
        
        Args:
            input_content: EPUB文件的二进制数据
            options: 转换选项
            
        Returns:
            bytes: Markdown文件的二进制数据
        """
        if options is None:
            options = {}
        
        # 加载EPUB书籍
        import io
        book = epub.read_epub(io.BytesIO(input_content))
        
        # 转换为Markdown
        md_content = []
        
        # 提取元数据
        md_content.append('---')
        if book.get_metadata('DC', 'title'):
            md_content.append(f'title: {book.get_metadata("DC", "title")[0][0]}')
        if book.get_metadata('DC', 'creator'):
            md_content.append(f'author: {book.get_metadata("DC", "creator")[0][0]}')
        if book.get_metadata('DC', 'language'):
            md_content.append(f'language: {book.get_metadata("DC", "language")[0][0]}')
        md_content.append('---')
        md_content.append('')
        
        # 处理章节
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # 解析HTML内容
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                
                # 提取标题
                h1 = soup.find('h1')
                if h1:
                    md_content.append(f'# {h1.get_text()}')
                    md_content.append('')
                
                # 提取段落
                for p in soup.find_all('p'):
                    text = p.get_text().strip()
                    if text:
                        md_content.append(text)
                        md_content.append('')
                
                # 提取列表
                for ul in soup.find_all('ul'):
                    for li in ul.find_all('li'):
                        text = li.get_text().strip()
                        if text:
                            md_content.append(f'- {text}')
                    md_content.append('')
                
                for ol in soup.find_all('ol'):
                    for i, li in enumerate(ol.find_all('li'), 1):
                        text = li.get_text().strip()
                        if text:
                            md_content.append(f'{i}. {text}')
                    md_content.append('')
                
                # 提取表格
                for table in soup.find_all('table'):
                    # 提取表头
                    headers = []
                    thead = table.find('thead')
                    if thead:
                        for th in thead.find_all('th'):
                            headers.append(th.get_text().strip())
                    else:
                        # 尝试从第一行提取表头
                        first_row = table.find('tr')
                        if first_row:
                            for th in first_row.find_all(['th', 'td']):
                                headers.append(th.get_text().strip())
                    
                    if headers:
                        # 生成表格
                        md_content.append('| ' + ' | '.join(headers) + ' |')
                        md_content.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
                        
                        # 提取表格数据
                        tbody = table.find('tbody')
                        rows = tbody.find_all('tr') if tbody else table.find_all('tr')[1:] if table.find_all('tr') else []
                        
                        for row in rows:
                            cells = []
                            for td in row.find_all('td'):
                                cells.append(td.get_text().strip())
                            if cells:
                                md_content.append('| ' + ' | '.join(cells) + ' |')
                        
                        md_content.append('')
        
        # 生成Markdown内容
        md_text = '\n'.join(md_content)
        
        return md_text.encode('utf-8')
    
    def get_supported_formats(self) -> tuple:
        """获取支持的格式"""
        return ('epub', 'markdown')
