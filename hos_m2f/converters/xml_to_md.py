"""XML到Markdown格式转换器"""

from typing import Any, Optional, Dict
from hos_m2f.converters.base_converter import BaseConverter
import xml.etree.ElementTree as ET


class XMLToMDConverter(BaseConverter):
    """XML到Markdown格式转换器"""
    
    def convert(self, input_content: bytes, options: Optional[Dict[str, Any]] = None) -> bytes:
        """将XML转换为Markdown
        
        Args:
            input_content: XML文件的二进制数据
            options: 转换选项
            
        Returns:
            bytes: Markdown文件的二进制数据
        """
        if options is None:
            options = {}
        
        # 解析XML
        root = ET.fromstring(input_content)
        
        # 转换为Markdown
        md_content = self._xml_to_md(root)
        
        return md_content.encode('utf-8')
    
    def _xml_to_md(self, element: ET.Element, indent: int = 0) -> str:
        """将XML元素转换为Markdown
        
        Args:
            element: XML元素
            indent: 缩进级别
            
        Returns:
            str: Markdown字符串
        """
        md_parts = []
        prefix = '  ' * indent
        
        # 处理document根元素
        if element.tag == 'document':
            for child in element:
                child_md = self._xml_to_md(child, indent)
                if child_md:
                    md_parts.append(child_md)
        
        # 处理元数据
        elif element.tag == 'metadata':
            # 跳过元数据，在Markdown中不需要
            pass
        
        # 处理标题
        elif element.tag == 'heading':
            # 获取标题级别
            level = int(element.get('level', indent + 1))
            # 获取标题内容
            content = element.text.strip() if element.text else ''
            if content:
                md_parts.append('#' * level + ' ' + content)
                md_parts.append('')
        
        # 处理段落
        elif element.tag == 'paragraph':
            content = element.text.strip() if element.text else ''
            if content:
                md_parts.append(content)
                md_parts.append('')
        
        # 处理列表
        elif element.tag == 'list':
            list_type = element.get('type', 'unordered')
            for item in element.findall('list_item'):
                item_content = item.text.strip() if item.text else ''
                if item_content:
                    md_parts.append(f'{prefix}- {item_content}')
            md_parts.append('')
        
        # 处理列表项
        elif element.tag == 'list_item':
            content = element.text.strip() if element.text else ''
            if content:
                md_parts.append(f'{prefix}- {content}')
        
        # 处理代码块
        elif element.tag == 'code_block':
            language = element.get('language', '')
            content = element.text.strip() if element.text else ''
            if content:
                md_parts.append(f'```{language}' if language else '```')
                md_parts.append(content)
                md_parts.append('```')
                md_parts.append('')
        
        # 处理表格
        elif element.tag == 'table':
            # 提取表头
            headers = []
            for header in element.findall('.//header'):
                header_content = header.text.strip() if header.text else ''
                headers.append(header_content)
            
            if headers:
                # 生成表格
                md_parts.append('| ' + ' | '.join(headers) + ' |')
                md_parts.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
                
                # 提取表格数据
                rows = element.findall('.//row')
                for row in rows:
                    cells = []
                    for cell in row.findall('.//cell'):
                        cell_content = cell.text.strip() if cell.text else ''
                        cells.append(cell_content)
                    if cells:
                        md_parts.append('| ' + ' | '.join(cells) + ' |')
                md_parts.append('')
        
        # 处理普通文本
        else:
            if element.text and element.text.strip():
                md_parts.append(f'{prefix}{element.tag}: {element.text.strip()}')
        
        # 添加空行
        if md_parts:
            md_parts.append('')
        
        return '\n'.join(md_parts)
    
    def get_supported_formats(self) -> tuple:
        """获取支持的格式"""
        return ('xml', 'markdown')
