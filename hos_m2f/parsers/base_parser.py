"""基础解析器"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union

from hos_m2f.model.universal_model import UniversalDocumentModel


class BaseParser(ABC):
    """基础解析器类"""
    
    @abstractmethod
    def parse(self, content: Union[str, bytes], options: Optional[Dict[str, Any]] = None) -> UniversalDocumentModel:
        """解析内容为中间模型
        
        Args:
            content: 输入内容
            options: 解析选项
            
        Returns:
            UniversalDocumentModel: 通用文档模型
        """
        pass
    
    def _extract_basic_meta(self, content: str) -> Dict[str, Any]:
        """提取基本元数据
        
        Args:
            content: 输入内容
            
        Returns:
            Dict[str, Any]: 基本元数据
        """
        return {
            "title": "Untitled Document",
            "author": "",
            "description": "",
            "tags": [],
            "publish_date": ""
        }
    
    def _normalize_content(self, content: Union[str, bytes]) -> str:
        """规范化内容
        
        Args:
            content: 输入内容
            
        Returns:
            str: 规范化后的内容
        """
        if isinstance(content, bytes):
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                return content.decode('latin-1')
        return content
