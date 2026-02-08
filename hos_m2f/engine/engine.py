"""核心引擎模块"""

import os
import json
from typing import Dict, Any, Optional, Union
from hos_m2f.converters import get_converter
from hos_m2f.parsers import get_parser
from hos_m2f.resources.resource_manager import ResourceManager


class Engine:
    """核心引擎类，负责处理文档转换和构建"""
    
    def __init__(self):
        """初始化引擎"""
        self.resource_manager = ResourceManager()
        self.supported_modes = {
            "paper": "学术论文模式",
            "patent": "专利申请模式",
            "book": "书籍模式",
            "sop": "标准操作流程模式"
        }
        self.supported_formats = {
            "md": "Markdown",
            "markdown": "Markdown",
            "docx": "Microsoft Word",
            "json": "JSON",
            "epub": " EPUB电子书",
            "html": "HTML",
            "xml": "XML",
            "pdf": "PDF",
            "xlsx": "Excel"
        }
    
    def build(self, content: str, mode: str, format: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """构建文档
        
        Args:
            content: 输入内容
            mode: 文档模式
            format: 输出格式
            options: 额外选项
            
        Returns:
            构建结果
        """
        if options is None:
            options = {}
        
        # 解析内容
        parser = get_parser("md")
        parsed_content = parser.parse(content, options)
        
        # 转换为目标格式
        converter = get_converter("md", format)
        result = converter.convert(content, options)
        
        return {
            "binary": result,
            "output_format": format,
            "metadata": {
                "mode": mode,
                "format": format,
                "options": options
            }
        }
    
    def check(self, content: str, mode: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """检查文档
        
        Args:
            content: 输入内容
            mode: 文档模式
            options: 额外选项
            
        Returns:
            检查结果
        """
        if options is None:
            options = {}
        
        # 简单的检查实现
        issues = []
        
        # 检查内容长度
        if len(content) < 10:
            issues.append("内容过短")
        
        # 检查模式是否支持
        if mode not in self.supported_modes:
            issues.append(f"不支持的模式: {mode}")
        
        return {
            "compliance": {
                "compliant": len(issues) == 0,
                "issues": issues
            },
            "metadata": {
                "mode": mode,
                "content_length": len(content)
            }
        }
    
    def convert(self, input_path: str, output_path: str, from_format: str, to_format: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """转换文件格式
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            from_format: 输入格式
            to_format: 输出格式
            options: 额外选项
            
        Returns:
            转换结果
        """
        if options is None:
            options = {}
        
        # 读取输入文件
        with open(input_path, 'r', encoding='utf-8') as f:
            input_content = f.read()
        
        # 获取转换器
        converter = get_converter(from_format, to_format)
        
        # 执行转换
        output_content = converter.convert(input_content, options)
        
        # 写入输出文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        return {
            "success": True,
            "input_path": input_path,
            "output_path": output_path,
            "from_format": from_format,
            "to_format": to_format,
            "metadata": {
                "input_size": len(input_content),
                "output_size": len(output_content),
                "options": options
            }
        }
    
    def get_supported_modes(self) -> Dict[str, str]:
        """获取支持的模式
        
        Returns:
            支持的模式字典
        """
        return self.supported_modes
    
    def get_supported_formats(self) -> Dict[str, str]:
        """获取支持的格式
        
        Returns:
            支持的格式字典
        """
        return self.supported_formats
