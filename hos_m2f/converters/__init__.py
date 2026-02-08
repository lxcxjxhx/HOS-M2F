"""基础格式互转模块"""

from hos_m2f.converters.base_converter import BaseConverter
from hos_m2f.converters.md_to_docx import MDToDOCXConverter
from hos_m2f.converters.md_to_json import MDToJSONConverter
from hos_m2f.converters.md_to_epub import MDToEPUBConverter
from hos_m2f.converters.md_to_html import MDToHTMLConverter
from hos_m2f.converters.md_to_xml import MDToXMLConverter
from hos_m2f.converters.md_to_latex import MDToLaTeXConverter
from hos_m2f.converters.docx_to_md import DOCXToMDConverter
from hos_m2f.converters.docx_to_html import DOCXToHTMLConverter
from hos_m2f.converters.json_to_md import JSONToMDConverter
from hos_m2f.converters.epub_to_md import EPUBToMDConverter
from hos_m2f.converters.html_to_md import HTMLToMDConverter
from hos_m2f.converters.html_to_docx import HTMLToDOCXConverter
from hos_m2f.converters.xml_to_md import XMLToMDConverter
from hos_m2f.converters.pdf_to_md import PDFToMDConverter

__all__ = [
    "BaseConverter",
    "MDToDOCXConverter",
    "MDToJSONConverter",
    "MDToEPUBConverter",
    "MDToHTMLConverter",
    "MDToXMLConverter",
    "MDToLaTeXConverter",
    "DOCXToMDConverter",
    "DOCXToHTMLConverter",
    "JSONToMDConverter",
    "EPUBToMDConverter",
    "HTMLToMDConverter",
    "HTMLToDOCXConverter",
    "XMLToMDConverter",
    "PDFToMDConverter",
    "get_converter"
]

# 转换映射
converter_mapping = {
    ("md", "docx"): MDToDOCXConverter,
    ("markdown", "docx"): MDToDOCXConverter,
    ("md", "json"): MDToJSONConverter,
    ("markdown", "json"): MDToJSONConverter,
    ("md", "epub"): MDToEPUBConverter,
    ("markdown", "epub"): MDToEPUBConverter,
    ("md", "html"): MDToHTMLConverter,
    ("markdown", "html"): MDToHTMLConverter,
    ("md", "xml"): MDToXMLConverter,
    ("markdown", "xml"): MDToXMLConverter,
    ("md", "latex"): MDToLaTeXConverter,
    ("markdown", "latex"): MDToLaTeXConverter,
    ("docx", "md"): DOCXToMDConverter,
    ("docx", "markdown"): DOCXToMDConverter,
    ("docx", "html"): DOCXToHTMLConverter,
    ("json", "md"): JSONToMDConverter,
    ("json", "markdown"): JSONToMDConverter,
    ("epub", "md"): EPUBToMDConverter,
    ("epub", "markdown"): EPUBToMDConverter,
    ("html", "md"): HTMLToMDConverter,
    ("html", "markdown"): HTMLToMDConverter,
    ("html", "docx"): HTMLToDOCXConverter,
    ("xml", "md"): XMLToMDConverter,
    ("xml", "markdown"): XMLToMDConverter,
    ("pdf", "md"): PDFToMDConverter,
    ("pdf", "markdown"): PDFToMDConverter
}

def get_converter(from_format: str, to_format: str) -> BaseConverter:
    """获取转换器
    
    Args:
        from_format: 输入格式
        to_format: 输出格式
        
    Returns:
        对应的转换器实例
    """
    # 标准化格式名称
    from_format = from_format.lower()
    to_format = to_format.lower()
    
    # 获取转换器类
    converter_class = converter_mapping.get((from_format, to_format))
    
    if not converter_class:
        # 如果没有找到精确匹配，尝试使用默认转换器
        if from_format in ["md", "markdown"]:
            # Markdown到其他格式
            if to_format == "docx":
                converter_class = MDToDOCXConverter
            elif to_format == "json":
                converter_class = MDToJSONConverter
            elif to_format == "epub":
                converter_class = MDToEPUBConverter
            elif to_format == "html":
                converter_class = MDToHTMLConverter
            elif to_format == "xml":
                converter_class = MDToXMLConverter
        elif to_format in ["md", "markdown"]:
            # 其他格式到Markdown
            if from_format == "docx":
                converter_class = DOCXToMDConverter
            elif from_format == "pdf":
                converter_class = PDFToMDConverter
    
    if not converter_class:
        raise ValueError(f"不支持的格式转换: {from_format} -> {to_format}")
    
    return converter_class()
