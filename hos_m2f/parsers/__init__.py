"""解析器包"""

from hos_m2f.parsers.md_parser import MDParser
from hos_m2f.parsers.html_parser import HTMLParser
from hos_m2f.parsers.json_parser import JSONParser
from hos_m2f.parsers.docx_parser import DOCXParser
from hos_m2f.parsers.epub_parser import EPUBParser
from hos_m2f.parsers.xml_parser import XMLParser
from hos_m2f.parsers.xlsx_parser import XLSXParser

__all__ = [
    "MDParser",
    "HTMLParser",
    "JSONParser",
    "DOCXParser",
    "EPUBParser",
    "XMLParser",
    "XLSXParser",
    "get_parser"
]

# 解析器映射
parser_mapping = {
    "md": MDParser,
    "markdown": MDParser,
    "html": HTMLParser,
    "json": JSONParser,
    "docx": DOCXParser,
    "epub": EPUBParser,
    "xml": XMLParser,
    "xlsx": XLSXParser
}

def get_parser(format: str):
    """获取解析器
    
    Args:
        format: 格式
        
    Returns:
        对应的解析器实例
    """
    # 标准化格式名称
    format = format.lower()
    
    # 获取解析器类
    parser_class = parser_mapping.get(format)
    
    if not parser_class:
        # 默认使用Markdown解析器
        parser_class = MDParser
    
    return parser_class()
