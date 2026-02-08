"""通用文档模型定义"""

from typing import Dict, Any, List, Optional
import json


class UniversalDocumentModel:
    """基于HTML+JSON双层结构的通用文档模型
    
    JSON层：负责文档结构、元数据、语义信息、AI处理
    HTML层：负责样式、表格、富文本、图片、排版
    """
    
    def __init__(self):
        """初始化通用文档模型"""
        # JSON结构层
        self.json_model = {
            "meta": {
                "title": "",
                "author": "",
                "mode": "paper",
                "description": "",
                "tags": [],
                "publish_date": "",
                "version": "1.0",
                "document_version": "1.0",
                "created_at": "",
                "updated_at": ""
            },
            "blocks": [],
            "structure": [],
            "semantics": {
                "domain_tag": "",
                "section_id": {},
                "table_type": {},
                "list_type": {}
            },
            "assets": [],
            "version_history": []
        }
        
        # HTML内容层
        self.html_content = ""
    
    def set_meta(self, meta: Dict[str, Any]) -> None:
        """设置元数据
        
        Args:
            meta: 元数据字典
        """
        self.json_model["meta"].update(meta)
    
    def add_structure_item(self, item: Dict[str, Any]) -> None:
        """添加结构项
        
        Args:
            item: 结构项字典
        """
        self.json_model["structure"].append(item)
    
    def add_block(self, block: Dict[str, Any]) -> None:
        """添加内容块
        
        Args:
            block: 内容块字典
        """
        self.json_model["blocks"].append(block)
    
    def add_asset(self, asset: Dict[str, Any]) -> None:
        """添加资源
        
        Args:
            asset: 资源字典
        """
        self.json_model["assets"].append(asset)
    
    def add_version_history(self, version_info: Dict[str, Any]) -> None:
        """添加版本历史
        
        Args:
            version_info: 版本信息字典
        """
        self.json_model["version_history"].append(version_info)
    
    def update_version(self, new_version: str) -> None:
        """更新文档版本
        
        Args:
            new_version: 新版本号
        """
        import datetime
        current_time = datetime.datetime.now().isoformat()
        
        # 记录版本历史
        self.add_version_history({
            "version": self.json_model["meta"]["document_version"],
            "timestamp": self.json_model["meta"]["updated_at"],
            "changes": "Auto version update"
        })
        
        # 更新版本信息
        self.json_model["meta"]["document_version"] = new_version
        self.json_model["meta"]["updated_at"] = current_time
        
        # 如果是首次创建，设置创建时间
        if not self.json_model["meta"]["created_at"]:
            self.json_model["meta"]["created_at"] = current_time
    
    def set_html_content(self, html: str) -> None:
        """设置HTML内容
        
        Args:
            html: HTML内容
        """
        self.html_content = html
    
    def get_json(self) -> Dict[str, Any]:
        """获取JSON模型
        
        Returns:
            Dict[str, Any]: JSON模型
        """
        return self.json_model
    
    def get_html(self) -> str:
        """获取HTML内容
        
        Returns:
            str: HTML内容
        """
        return self.html_content
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式
        
        Returns:
            Dict[str, Any]: 包含JSON和HTML的完整模型
        """
        return {
            "json": self.json_model,
            "html": self.html_content
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """从字典加载模型
        
        Args:
            data: 包含JSON和HTML的完整模型
        """
        if "json" in data:
            self.json_model = data["json"]
        if "html" in data:
            self.html_content = data["html"]
    
    def save(self, json_path: str, html_path: str) -> None:
        """保存模型到文件
        
        Args:
            json_path: JSON文件路径
            html_path: HTML文件路径
        """
        # 保存JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.json_model, f, ensure_ascii=False, indent=2)
        
        # 保存HTML
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(self.html_content)
    
    def load(self, json_path: str, html_path: str) -> None:
        """从文件加载模型
        
        Args:
            json_path: JSON文件路径
            html_path: HTML文件路径
        """
        # 加载JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            self.json_model = json.load(f)
        
        # 加载HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            self.html_content = f.read()
    
    def validate(self) -> Dict[str, Any]:
        """验证模型完整性
        
        Returns:
            Dict[str, Any]: 验证结果
        """
        errors = []
        
        # 验证元数据
        if not self.json_model.get("meta", {}).get("title"):
            errors.append("Missing title in metadata")
        
        # 验证结构
        if not self.json_model.get("structure"):
            errors.append("Missing structure")
        
        # 验证HTML内容
        if not self.html_content:
            errors.append("Missing HTML content")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def merge(self, other: "UniversalDocumentModel") -> None:
        """合并另一个模型
        
        Args:
            other: 另一个通用文档模型
        """
        # 合并元数据
        self.json_model["meta"].update(other.json_model["meta"])
        
        # 合并结构
        self.json_model["structure"].extend(other.json_model["structure"])
        
        # 合并HTML内容
        self.html_content += other.html_content
    
    def clear(self) -> None:
        """清空模型"""
        self.__init__()
    
    def __repr__(self) -> str:
        """字符串表示
        
        Returns:
            str: 模型的字符串表示
        """
        return f"UniversalDocumentModel(title='{self.json_model['meta']['title']}', mode='{self.json_model['meta']['mode']}')"
