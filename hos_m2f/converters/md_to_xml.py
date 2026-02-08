"""Markdown到XML格式转换器"""

from typing import Any, Optional, Dict
from hos_m2f.converters.base_converter import BaseConverter
import mistune


class MDToXMLConverter(BaseConverter):
    """Markdown到XML格式转换器"""
    
    def convert(self, input_content: str, options: Optional[Dict[str, Any]] = None) -> bytes:
        """将Markdown转换为XML
        
        Args:
            input_content: Markdown内容
            options: 转换选项
            
        Returns:
            bytes: XML文件的二进制数据
        """
        if options is None:
            options = {}
        
        # 解析Markdown
        structure = self._parse_markdown(input_content)
        
        # 转换为XML
        xml_content = self._structure_to_xml(structure)
        
        # 生成完整的XML文档
        full_xml = f'''
        <?xml version="1.0" encoding="UTF-8"?>
        <document>
            {xml_content}
        </document>
        '''
        
        return full_xml.encode('utf-8')
    
    def _parse_markdown(self, content: str) -> Dict[str, Any]:
        """解析Markdown内容为结构化数据
        
        Args:
            content: Markdown内容
            
        Returns:
            Dict[str, Any]: 结构化数据
        """
        lines = content.split('\n')
        structure = {
            'type': 'document',
            'children': [],
            'metadata': {}
        }
        
        current_heading = None
        current_level = 0
        current_paragraph = []
        current_list = None
        current_list_items = []
        list_level = 0
        
        # 解析YAML头
        if lines and lines[0] == '---':
            metadata = []
            for i, line in enumerate(lines[1:]):
                if line == '---':
                    break
                metadata.append(line)
            
            # 解析YAML元数据
            if metadata:
                import yaml
                try:
                    metadata_content = '\n'.join(metadata)
                    structure['metadata'] = yaml.safe_load(metadata_content)
                except Exception:
                    pass
            
            # 跳过YAML头
            lines = lines[i+2:]
        
        # 解析内容
        for line in lines:
            line = line.rstrip()
            
            # 处理标题
            if line.startswith('#'):
                # 保存当前段落
                if current_paragraph:
                    structure['children'].append({
                        'type': 'paragraph',
                        'content': '\n'.join(current_paragraph)
                    })
                    current_paragraph = []
                
                # 保存当前列表
                if current_list is not None:
                    structure['children'].append({
                        'type': 'list',
                        'ordered': current_list,
                        'items': current_list_items
                    })
                    current_list = None
                    current_list_items = []
                
                # 解析标题
                level = len(line.split(' ')[0])
                title = line[level:].strip()
                structure['children'].append({
                    'type': 'heading',
                    'level': level,
                    'content': title
                })
                current_heading = title
                current_level = level
            
            # 处理有序列表
            elif line.startswith('1. ') or line.startswith('\t1. ') or line.startswith('  1. '):
                # 保存当前段落
                if current_paragraph:
                    structure['children'].append({
                        'type': 'paragraph',
                        'content': '\n'.join(current_paragraph)
                    })
                    current_paragraph = []
                
                # 开始新列表
                if current_list is None:
                    current_list = True
                elif current_list != True:
                    structure['children'].append({
                        'type': 'list',
                        'ordered': current_list,
                        'items': current_list_items
                    })
                    current_list = True
                    current_list_items = []
                
                # 解析列表项
                content = line.lstrip('1234567890. \t')
                current_list_items.append({
                    'type': 'list_item',
                    'content': content
                })
            
            # 处理无序列表
            elif line.startswith('- ') or line.startswith('* ') or line.startswith('+ ') or \
                 line.startswith('\t- ') or line.startswith('\t* ') or line.startswith('\t+ ') or \
                 line.startswith('  - ') or line.startswith('  * ') or line.startswith('  + '):
                # 保存当前段落
                if current_paragraph:
                    structure['children'].append({
                        'type': 'paragraph',
                        'content': '\n'.join(current_paragraph)
                    })
                    current_paragraph = []
                
                # 开始新列表
                if current_list is None:
                    current_list = False
                elif current_list != False:
                    structure['children'].append({
                        'type': 'list',
                        'ordered': current_list,
                        'items': current_list_items
                    })
                    current_list = False
                    current_list_items = []
                
                # 解析列表项
                content = line.lstrip('-*+ \t')
                current_list_items.append({
                    'type': 'list_item',
                    'content': content
                })
            
            # 处理代码块
            elif line.startswith('```'):
                # 保存当前段落
                if current_paragraph:
                    structure['children'].append({
                        'type': 'paragraph',
                        'content': '\n'.join(current_paragraph)
                    })
                    current_paragraph = []
                
                # 保存当前列表
                if current_list is not None:
                    structure['children'].append({
                        'type': 'list',
                        'ordered': current_list,
                        'items': current_list_items
                    })
                    current_list = None
                    current_list_items = []
                
                # 解析代码块
                code_lines = []
                language = line[3:].strip()
                
                # 读取代码内容
                try:
                    line_idx = lines.index(line)
                    code_end_idx = line_idx + 1
                    for i, code_line in enumerate(lines[line_idx+1:]):
                        if code_line.startswith('```'):
                            code_end_idx = line_idx + i + 1
                            break
                        code_lines.append(code_line)
                        code_end_idx = line_idx + i + 1
                    
                    structure['children'].append({
                        'type': 'code_block',
                        'language': language,
                        'content': '\n'.join(code_lines)
                    })
                    
                    # 跳过已处理的代码行
                    if code_end_idx < len(lines):
                        lines = lines[:line_idx] + lines[code_end_idx+1:]
                    else:
                        lines = lines[:line_idx]
                except ValueError:
                    # 如果找不到行，跳过代码块解析
                    continue
            
            # 处理表格
            elif line.startswith('|') and '|' in line[1:]:
                # 保存当前段落
                if current_paragraph:
                    structure['children'].append({
                        'type': 'paragraph',
                        'content': '\n'.join(current_paragraph)
                    })
                    current_paragraph = []
                
                # 保存当前列表
                if current_list is not None:
                    structure['children'].append({
                        'type': 'list',
                        'ordered': current_list,
                        'items': current_list_items
                    })
                    current_list = None
                    current_list_items = []
                
                # 解析表格
                table_lines = [line]
                
                # 读取表格内容
                try:
                    line_idx = lines.index(line)
                    for i, table_line in enumerate(lines[line_idx+1:]):
                        if table_line.startswith('|'):
                            table_lines.append(table_line)
                        else:
                            break
                except ValueError:
                    # 如果找不到行，跳过表格解析
                    continue
                
                # 解析表格结构
                if len(table_lines) >= 2:
                    headers = [h.strip() for h in table_lines[0].split('|') if h.strip()]
                    rows = []
                    
                    # 跳过分隔线（如果存在）
                    start_idx = 1
                    if len(table_lines) > 1 and any('---' in cell for cell in table_lines[1].split('|')):
                        start_idx = 2
                    
                    for table_line in table_lines[start_idx:]:
                        cells = [c.strip() for c in table_line.split('|') if c.strip()]
                        if cells:
                            rows.append(dict(zip(headers, cells)))
                    
                    structure['children'].append({
                        'type': 'table',
                        'headers': headers,
                        'rows': rows
                    })
                
                # 跳过已处理的表格行
                lines = lines[:lines.index(line)] + lines[lines.index(line)+i+1:]
            
            # 处理段落
            else:
                if line or current_paragraph:
                    current_paragraph.append(line)
        
        # 保存最后一个段落
        if current_paragraph:
            structure['children'].append({
                'type': 'paragraph',
                'content': '\n'.join(current_paragraph)
            })
        
        # 保存最后一个列表
        if current_list is not None:
            structure['children'].append({
                'type': 'list',
                'ordered': current_list,
                'items': current_list_items
            })
        
        return structure
    
    def _structure_to_xml(self, structure: Dict[str, Any]) -> str:
        """将结构化数据转换为XML
        
        Args:
            structure: 结构化数据
            
        Returns:
            str: XML字符串
        """
        xml_parts = []
        
        # 处理元数据
        if structure.get('metadata'):
            xml_parts.append('<metadata>')
            for key, value in structure['metadata'].items():
                xml_parts.append(f'<{key}>{self._escape_xml(str(value))}</{key}>')
            xml_parts.append('</metadata>')
        
        # 处理子元素
        for child in structure.get('children', []):
            if child['type'] == 'heading':
                xml_parts.append(f'<heading level="{child["level"]}">{self._escape_xml(child["content"])}</heading>')
            elif child['type'] == 'paragraph':
                xml_parts.append(f'<paragraph>{self._escape_xml(child["content"])}</paragraph>')
            elif child['type'] == 'list':
                list_type = 'ordered' if child['ordered'] else 'unordered'
                xml_parts.append(f'<list type="{list_type}">')
                for item in child['items']:
                    xml_parts.append(f'<list_item>{self._escape_xml(item["content"])}</list_item>')
                xml_parts.append('</list>')
            elif child['type'] == 'code_block':
                xml_parts.append(f'<code_block language="{child.get("language", "")}">{self._escape_xml(child["content"])}</code_block>')
            elif child['type'] == 'table':
                xml_parts.append('<table>')
                xml_parts.append('<headers>')
                for header in child['headers']:
                    xml_parts.append(f'<header>{self._escape_xml(header)}</header>')
                xml_parts.append('</headers>')
                xml_parts.append('<rows>')
                for row in child['rows']:
                    xml_parts.append('<row>')
                    for key, value in row.items():
                        xml_parts.append(f'<cell column="{self._escape_xml(key)}">{self._escape_xml(value)}</cell>')
                    xml_parts.append('</row>')
                xml_parts.append('</rows>')
                xml_parts.append('</table>')
        
        return '\n'.join(xml_parts)
    
    def _escape_xml(self, text: str) -> str:
        """转义XML特殊字符
        
        Args:
            text: 原始文本
            
        Returns:
            str: 转义后的文本
        """
        escape_map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&apos;'
        }
        
        for char, replacement in escape_map.items():
            text = text.replace(char, replacement)
        
        return text
    
    def get_supported_formats(self) -> tuple:
        """获取支持的格式"""
        return ('markdown', 'xml')
