"""Markdown到EPUB格式转换器"""

from typing import Any, Optional, Dict
from hos_m2f.converters.base_converter import BaseConverter
from hos_m2f.renderers.epub_renderer import EPUBRenderer
from hos_m2f.structure.book_parser import BookParser


class MDToEPUBConverter(BaseConverter):
    """Markdown到EPUB格式转换器"""
    
    def __init__(self):
        """初始化转换器"""
        self.renderer = EPUBRenderer()
        self.book_parser = BookParser()
    
    def convert(self, input_content: str, options: Optional[Dict[str, Any]] = None) -> bytes:
        """将Markdown转换为EPUB
        
        Args:
            input_content: Markdown内容
            options: 转换选项
            
        Returns:
            bytes: EPUB文件的二进制数据
        """
        if options is None:
            options = {}
        
        # 使用BookParser解析Markdown内容
        parsed_content = self.book_parser.parse(input_content, options)
        
        # 增强解析结果
        parsed_content = self._enhance_parsed_content(parsed_content, options)
        
        # 使用EPUBRenderer渲染EPUB文件
        epub_content = self.renderer.render(parsed_content, options)
        
        return epub_content
    
    def _enhance_parsed_content(self, parsed_content: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """增强解析结果"""
        # 添加选项中的元数据
        if 'title' in options:
            parsed_content.setdefault('book_metadata', {})['title'] = options['title']
        if 'author' in options:
            parsed_content.setdefault('book_metadata', {})['author'] = options['author']
        if 'language' in options:
            parsed_content.setdefault('book_metadata', {})['language'] = options['language']
        if 'publisher' in options:
            parsed_content.setdefault('book_metadata', {})['publisher'] = options['publisher']
        if 'publish_date' in options:
            parsed_content.setdefault('book_metadata', {})['publish_date'] = options['publish_date']
        if 'description' in options:
            parsed_content.setdefault('book_metadata', {})['description'] = options['description']
        
        # 添加封面信息
        if 'cover' in options:
            parsed_content['cover'] = {
                'src': options['cover'],
                'type': 'image'
            }
        
        return parsed_content
    
    def get_supported_formats(self) -> tuple:
        """获取支持的格式"""
        return ('markdown', 'epub')
