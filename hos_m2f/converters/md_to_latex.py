"""Markdown到LaTeX格式转换器"""

from typing import Any, Optional, Dict
from hos_m2f.converters.base_converter import BaseConverter
from hos_m2f.renderers.latex_renderer import LaTeXRenderer
from hos_m2f.structure.semantic_parser import SemanticParser


class MDToLaTeXConverter(BaseConverter):
    """Markdown到LaTeX格式转换器"""
    
    def __init__(self):
        """初始化转换器"""
        self.renderer = LaTeXRenderer()
        self.parser = SemanticParser()
    
    def convert(self, input_content: str, options: Optional[Dict[str, Any]] = None) -> bytes:
        """将Markdown转换为LaTeX
        
        Args:
            input_content: Markdown内容
            options: 转换选项
            
        Returns:
            bytes: LaTeX文件的二进制数据
        """
        if options is None:
            options = {}
        
        # 使用SemanticParser解析Markdown内容
        parsed_content = self.parser.parse(input_content)
        
        # 增强解析结果
        parsed_content = self._enhance_parsed_content(parsed_content, options)
        
        # 使用LaTeXRenderer渲染LaTeX文件
        latex_content = self.renderer.render(parsed_content, options)
        
        return latex_content
    
    def _enhance_parsed_content(self, parsed_content: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """增强解析结果"""
        # 添加选项中的元数据
        if 'title' in options:
            parsed_content.setdefault('metadata', {})['title'] = options['title']
        if 'author' in options:
            parsed_content.setdefault('metadata', {})['author'] = options['author']
        if 'date' in options:
            parsed_content.setdefault('metadata', {})['date'] = options['date']
        if 'abstract' in options:
            parsed_content.setdefault('metadata', {})['abstract'] = options['abstract']
        if 'keywords' in options:
            parsed_content.setdefault('metadata', {})['keywords'] = options['keywords']
        
        # 添加文档类型
        if 'document_class' in options:
            parsed_content['document_class'] = options['document_class']
        
        return parsed_content
    
    def get_supported_formats(self) -> tuple:
        """获取支持的格式"""
        return ('markdown', 'latex')