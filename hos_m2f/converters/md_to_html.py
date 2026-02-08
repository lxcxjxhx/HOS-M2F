"""Markdown到HTML格式转换器"""

from typing import Any, Optional, Dict
from hos_m2f.converters.base_converter import BaseConverter
from hos_m2f.renderers.html_renderer import HTMLRenderer


class MDToHTMLConverter(BaseConverter):
    """Markdown到HTML格式转换器"""
    
    def convert(self, input_content: str, options: Optional[Dict[str, Any]] = None) -> bytes:
        """将Markdown转换为HTML
        
        Args:
            input_content: Markdown内容
            options: 转换选项
            
        Returns:
            bytes: HTML文件的二进制数据
        """
        if options is None:
            options = {}
        
        # 创建HTML渲染器实例
        renderer = HTMLRenderer()
        
        # 构建结构化内容
        structured_content = {
            "content": input_content,
            "book_metadata": options.get('metadata', {})
        }
        
        # 使用渲染器生成HTML
        html_bytes = renderer.render(structured_content, options)
        
        return html_bytes
    
    def get_supported_formats(self) -> tuple:
        """获取支持的格式"""
        return ('markdown', 'html')
