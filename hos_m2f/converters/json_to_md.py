"""JSON到Markdown格式转换器"""

from typing import Any, Optional, Dict, List
from hos_m2f.converters.base_converter import BaseConverter
import json


class JSONToMDConverter(BaseConverter):
    """JSON到Markdown格式转换器"""
    
    def convert(self, input_content: bytes, options: Optional[Dict[str, Any]] = None) -> bytes:
        """将JSON转换为Markdown
        
        Args:
            input_content: JSON文件的二进制数据
            options: 转换选项
            
        Returns:
            bytes: Markdown文件的二进制数据
        """
        if options is None:
            options = {}
        
        # 解析JSON
        json_content = json.loads(input_content.decode('utf-8'))
        
        # 转换为Markdown
        md_content = self._json_to_md(json_content)
        
        return md_content.encode('utf-8')
    
    def _json_to_md(self, data: Any, indent: int = 0) -> str:
        """将JSON数据转换为Markdown
        
        Args:
            data: JSON数据
            indent: 缩进级别
            
        Returns:
            str: Markdown字符串
        """
        md_parts = []
        prefix = '  ' * indent
        
        if isinstance(data, dict):
            for key, value in data.items():
                # 处理标题
                if key in ['title', 'heading', 'Header']:
                    md_parts.append('#' * (indent + 1) + ' ' + str(value))
                # 处理列表
                elif key in ['items', 'list', 'List']:
                    md_parts.append(f'{prefix}{key}:')
                    if isinstance(value, list):
                        for item in value:
                            md_parts.append(f'{prefix}- {self._json_to_md(item, indent + 1)}')
                # 处理表格
                elif key in ['table', 'Table']:
                    if isinstance(value, dict) and 'headers' in value and 'rows' in value:
                        # 生成表格
                        headers = value['headers']
                        rows = value['rows']
                        
                        # 表头
                        md_parts.append('| ' + ' | '.join(headers) + ' |')
                        # 分隔线
                        md_parts.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
                        # 数据行
                        for row in rows:
                            if isinstance(row, dict):
                                cells = [str(row.get(header, '')) for header in headers]
                            else:
                                cells = [str(cell) for cell in row]
                            md_parts.append('| ' + ' | '.join(cells) + ' |')
                # 处理普通键值对
                else:
                    if isinstance(value, (dict, list)):
                        md_parts.append(f'{prefix}{key}:')
                        md_parts.append(self._json_to_md(value, indent + 1))
                    else:
                        md_parts.append(f'{prefix}{key}: {value}')
        
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    md_parts.append(f'{prefix}-')
                    md_parts.append(self._json_to_md(item, indent + 1))
                else:
                    md_parts.append(f'{prefix}- {item}')
        
        elif isinstance(data, str):
            md_parts.append(f'{prefix}{data}')
        
        return '\n'.join(md_parts)
    
    def get_supported_formats(self) -> tuple:
        """获取支持的格式"""
        return ('json', 'markdown')
