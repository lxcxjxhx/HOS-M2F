"""HTML到Markdown格式转换器"""

from typing import Any, Optional, Dict
from hos_m2f.converters.base_converter import BaseConverter
from bs4 import BeautifulSoup


class HTMLToMDConverter(BaseConverter):
    """HTML到Markdown格式转换器"""
    
    def convert(self, input_content: bytes, options: Optional[Dict[str, Any]] = None) -> bytes:
        """将HTML转换为Markdown
        
        Args:
            input_content: HTML文件的二进制数据
            options: 转换选项
            
        Returns:
            bytes: Markdown文件的二进制数据
        """
        if options is None:
            options = {}
        
        # 解析HTML
        soup = BeautifulSoup(input_content, 'html.parser')
        
        # 转换为Markdown
        md_content = self._html_to_md(soup)
        
        return md_content.encode('utf-8')
    
    def _html_to_md(self, soup: BeautifulSoup) -> str:
        """将HTML转换为Markdown
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            str: Markdown字符串
        """
        md_parts = []
        
        # 处理标题
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                md_parts.append('#' * level + ' ' + heading.get_text())
                md_parts.append('')
        
        # 处理段落
        for paragraph in soup.find_all('p'):
            text = paragraph.get_text().strip()
            if text:
                md_parts.append(text)
                md_parts.append('')
        
        # 处理列表
        for ul in soup.find_all('ul'):
            for li in ul.find_all('li'):
                text = li.get_text().strip()
                if text:
                    md_parts.append('- ' + text)
            md_parts.append('')
        
        for ol in soup.find_all('ol'):
            for i, li in enumerate(ol.find_all('li'), 1):
                text = li.get_text().strip()
                if text:
                    md_parts.append(f'{i}. ' + text)
            md_parts.append('')
        
        # 处理表格
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
                md_parts.append('| ' + ' | '.join(headers) + ' |')
                md_parts.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
                
                # 提取表格数据
                tbody = table.find('tbody')
                rows = tbody.find_all('tr') if tbody else table.find_all('tr')[1:] if table.find_all('tr') else []
                
                for row in rows:
                    cells = []
                    for td in row.find_all('td'):
                        cells.append(td.get_text().strip())
                    if cells:
                        md_parts.append('| ' + ' | '.join(cells) + ' |')
                
                md_parts.append('')
        
        # 处理代码块
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if code:
                language = code.get('class', [''])[0].replace('language-', '')
                md_parts.append(f'```python' if language == 'python' else '```')
                md_parts.append(code.get_text())
                md_parts.append('```')
                md_parts.append('')
        
        # 处理链接
        for a in soup.find_all('a', href=True):
            text = a.get_text().strip()
            if text:
                md_parts.append(f'[{text}]({a["href"]})')
                md_parts.append('')
        
        # 处理图片
        for img in soup.find_all('img', src=True):
            alt = img.get('alt', '')
            src = img['src']
            md_parts.append(f'![{alt}]({src})')
            md_parts.append('')
        
        return '\n'.join(md_parts)
    
    def get_supported_formats(self) -> tuple:
        """获取支持的格式"""
        return ('html', 'markdown')
