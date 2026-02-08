"""基础转换器类"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict


class BaseConverter(ABC):
    """基础转换器抽象类"""
    
    @abstractmethod
    def convert(self, input_content: Any, options: Optional[Dict[str, Any]] = None) -> Any:
        """转换方法
        
        Args:
            input_content: 输入内容
            options: 转换选项
            
        Returns:
            Any: 转换后的内容
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> tuple:
        """获取支持的格式
        
        Returns:
            tuple: (输入格式, 输出格式)
        """
        pass
