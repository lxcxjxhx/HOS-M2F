"""JSON解析器"""

import json
from typing import Dict, Any, Optional, Union
from bs4 import BeautifulSoup

from hos_m2f.model.universal_model import UniversalDocumentModel
from hos_m2f.parsers.base_parser import BaseParser


class JSONParser(BaseParser):
    """JSON解析器"""
    
    def parse(self, content: Union[str, bytes], options: Optional[Dict[str, Any]] = None) -> UniversalDocumentModel:
        """解析JSON内容为中间模型
        
        Args:
            content: JSON内容
            options: 解析选项
            
        Returns:
            UniversalDocumentModel: 通用文档模型
        """
        options = options or {}
        
        # 确保content是字符串
        content = self._normalize_content(content)
        
        # 解析JSON
        json_data = json.loads(content)
        
        # 创建通用文档模型
        model = UniversalDocumentModel()
        
        # 1. 提取元数据
        meta = self._extract_meta(json_data)
        model.set_meta(meta)
        
        # 2. 生成HTML内容
        html_content = self._generate_html_content(json_data, options)
        model.set_html_content(html_content)
        
        # 3. 分析文档结构
        structure = self._analyze_structure(json_data)
        for item in structure:
            model.add_structure_item(item)
        
        # 4. 提取语义信息
        semantics = self._extract_semantics(json_data)
        model.get_json()["semantics"].update(semantics)
        
        return model
    
    def _extract_meta(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取元数据
        
        Args:
            json_data: JSON数据
            
        Returns:
            Dict[str, Any]: 元数据字典
        """
        meta = {}
        
        # 从不同位置提取元数据
        if "meta" in json_data:
            meta.update(json_data["meta"])
        elif "metadata" in json_data:
            meta.update(json_data["metadata"])
        elif "header" in json_data:
            meta.update(json_data["header"])
        
        # 从顶层提取基本元数据
        for key in ["title", "author", "description", "tags", "publish_date"]:
            if key in json_data and key not in meta:
                meta[key] = json_data[key]
        
        return meta
    
    def _generate_html_content(self, json_data: Dict[str, Any], options: Dict[str, Any]) -> str:
        """生成HTML内容
        
        Args:
            json_data: JSON数据
            options: 生成选项
            
        Returns:
            str: HTML内容
        """
        # 如果JSON中已经包含HTML内容，直接使用
        if "html" in json_data:
            return json_data["html"]
        
        # 从JSON结构生成HTML
        html_parts = []
        
        # 添加标题
        title = json_data.get("meta", {}).get("title", json_data.get("title", ""))
        if title:
            html_parts.append(f"<h1>{title}</h1>")
        
        # 处理内容
        if "content" in json_data:
            content = json_data["content"]
            if isinstance(content, str):
                html_parts.append(f"<div>{content}</div>")
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        html_parts.append(self._render_content_item(item))
        
        # 处理结构
        if "structure" in json_data:
            for item in json_data["structure"]:
                if isinstance(item, dict) and "type" in item:
                    html_parts.append(self._render_structure_item(item))
        
        return "<div class='content'>" + "\n".join(html_parts) + "</div>"
    
    def _render_content_item(self, item: Dict[str, Any]) -> str:
        """渲染内容项
        
        Args:
            item: 内容项
            
        Returns:
            str: HTML内容
        """
        item_type = item.get("type", "")
        
        if item_type == "paragraph":
            text = item.get("text", "")
            return f"<p>{text}</p>"
        elif item_type == "heading":
            level = item.get("level", 2)
            text = item.get("text", item.get("title", ""))
            return f"<h{level}>{text}</h{level}>"
        elif item_type == "list":
            list_type = item.get("list_type", "unordered")
            items = item.get("items", [])
            tag = "ol" if list_type == "ordered" else "ul"
            list_items = [f"<li>{item}</li>" for item in items]
            return f"<{tag}>{''.join(list_items)}</{tag}>"
        elif item_type == "table":
            headers = item.get("headers", [])
            rows = item.get("rows", [])
            html = "<table><thead><tr>"
            for header in headers:
                html += f"<th>{header}</th>"
            html += "</tr></thead><tbody>"
            for row in rows:
                html += "<tr>"
                for cell in row:
                    html += f"<td>{cell}</td>"
                html += "</tr>"
            html += "</tbody></table>"
            return html
        elif item_type == "image":
            src = item.get("src", "")
            alt = item.get("alt", "")
            return f"<img src='{src}' alt='{alt}'>"
        elif item_type == "code":
            code = item.get("code", "")
            language = item.get("language", "")
            return f"<pre><code class='language-{language}'>{code}</code></pre>"
        else:
            return "<div></div>"
    
    def _render_structure_item(self, item: Dict[str, Any]) -> str:
        """渲染结构项
        
        Args:
            item: 结构项
            
        Returns:
            str: HTML内容
        """
        item_type = item.get("type", "")
        
        if item_type == "heading":
            level = item.get("level", 2)
            title = item.get("title", "")
            return f"<h{level}>{title}</h{level}>"
        elif item_type == "paragraph":
            return "<p></p>"
        elif item_type == "table":
            return "<table></table>"
        elif item_type == "image":
            return "<img>"
        elif item_type == "list":
            list_type = item.get("list_type", "unordered")
            tag = "ol" if list_type == "ordered" else "ul"
            return f"<{tag}></{tag}>"
        elif item_type == "code_block":
            return "<pre><code></code></pre>"
        else:
            return "<div></div>"
    
    def _analyze_structure(self, json_data: Dict[str, Any]) -> list:
        """分析文档结构
        
        Args:
            json_data: JSON数据
            
        Returns:
            list: 结构项列表
        """
        structure = []
        
        # 从结构字段分析
        if "structure" in json_data:
            for item in json_data["structure"]:
                if isinstance(item, dict):
                    structure.append(item)
        
        # 从内容字段分析
        elif "content" in json_data:
            content = json_data["content"]
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and "type" in item:
                        structure.append(item)
        
        return structure
    
    def _extract_semantics(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取语义信息
        
        Args:
            json_data: JSON数据
            
        Returns:
            Dict[str, Any]: 语义信息字典
        """
        semantics = {
            "domain_tag": "",
            "section_id": {},
            "table_type": {},
            "list_type": {}
        }
        
        # 从语义字段提取
        if "semantics" in json_data:
            semantics.update(json_data["semantics"])
        
        # 从结构中提取
        if "structure" in json_data:
            for i, item in enumerate(json_data["structure"]):
                if isinstance(item, dict):
                    if item.get("type") == "heading" and "id" in item:
                        semantics["section_id"][item["id"]] = {
                            "title": item.get("title", ""),
                            "level": item.get("level", 1)
                        }
                    elif item.get("type") == "table" and "id" in item:
                        semantics["table_type"][item["id"]] = item.get("table_type", "general")
                    elif item.get("type") == "list" and "id" in item:
                        semantics["list_type"][item["id"]] = item.get("list_type", "unordered")
        
        return semantics
