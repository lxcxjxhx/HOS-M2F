"""XML解析器"""

from typing import Dict, Any, Optional, Union
import xml.etree.ElementTree as ET

from hos_m2f.model.universal_model import UniversalDocumentModel
from hos_m2f.parsers.base_parser import BaseParser


class XMLParser(BaseParser):
    """XML解析器"""
    
    def parse(self, content: Union[str, bytes], options: Optional[Dict[str, Any]] = None) -> UniversalDocumentModel:
        """解析XML内容为中间模型
        
        Args:
            content: XML内容
            options: 解析选项
            
        Returns:
            UniversalDocumentModel: 通用文档模型
        """
        options = options or {}
        
        # 确保content是字符串
        content = self._normalize_content(content)
        
        # 解析XML
        tree = ET.ElementTree(ET.fromstring(content))
        root = tree.getroot()
        
        # 创建通用文档模型
        model = UniversalDocumentModel()
        
        # 1. 提取元数据
        meta = self._extract_meta(root)
        model.set_meta(meta)
        
        # 2. 生成HTML内容
        html_content = self._generate_html_content(root, options)
        model.set_html_content(html_content)
        
        # 3. 分析文档结构
        structure = self._analyze_structure(root)
        for item in structure:
            model.add_structure_item(item)
        
        # 4. 提取语义信息
        semantics = self._extract_semantics(root)
        model.get_json()["semantics"].update(semantics)
        
        return model
    
    def _extract_meta(self, root: ET.Element) -> Dict[str, Any]:
        """提取元数据
        
        Args:
            root: XML根元素
            
        Returns:
            Dict[str, Any]: 元数据字典
        """
        meta = {}
        
        # 尝试从常见位置提取元数据
        # 检查根元素的属性
        for key in ["title", "author", "description", "tags", "publish_date"]:
            if key in root.attrib:
                meta[key] = root.attrib[key]
        
        # 检查子元素
        for child in root:
            tag = child.tag.split('}')[-1]  # 处理命名空间
            if tag == "title" and "title" not in meta:
                meta["title"] = child.text.strip() if child.text else ""
            elif tag == "author" and "author" not in meta:
                meta["author"] = child.text.strip() if child.text else ""
            elif tag == "description" and "description" not in meta:
                meta["description"] = child.text.strip() if child.text else ""
            elif tag == "tags" or tag == "keywords":
                tags = []
                for tag_elem in child:
                    if tag_elem.text:
                        tags.append(tag_elem.text.strip())
                if tags:
                    meta["tags"] = tags
            elif tag == "date" or tag == "publish_date":
                meta["publish_date"] = child.text.strip() if child.text else ""
        
        return meta
    
    def _generate_html_content(self, root: ET.Element, options: Dict[str, Any]) -> str:
        """生成HTML内容
        
        Args:
            root: XML根元素
            options: 生成选项
            
        Returns:
            str: HTML内容
        """
        html_parts = []
        
        # 递归转换XML为HTML
        self._xml_to_html(root, html_parts)
        
        return "<div class='content'>" + "\n".join(html_parts) + "</div>"
    
    def _xml_to_html(self, element: ET.Element, html_parts: list, level: int = 1) -> None:
        """递归将XML转换为HTML
        
        Args:
            element: XML元素
            html_parts: HTML内容列表
            level: 嵌套级别
        """
        tag = element.tag.split('}')[-1]  # 处理命名空间
        
        # 映射常见标签
        tag_map = {
            "title": f"h{min(level, 6)}",
            "heading": f"h{min(level, 6)}",
            "head": "h1",
            "h1": "h1",
            "h2": "h2",
            "h3": "h3",
            "h4": "h4",
            "h5": "h5",
            "h6": "h6",
            "p": "p",
            "paragraph": "p",
            "text": "p",
            "list": "ul",
            "ul": "ul",
            "ol": "ol",
            "li": "li",
            "item": "li",
            "table": "table",
            "tr": "tr",
            "td": "td",
            "th": "th",
            "img": "img",
            "image": "img",
            "code": "code",
            "pre": "pre"
        }
        
        # 获取对应的HTML标签
        html_tag = tag_map.get(tag, "div")
        
        # 处理文本内容
        if element.text and element.text.strip():
            if html_tag in ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th", "code"]:
                html_parts.append(f"<{html_tag}>{element.text.strip()}</{html_tag}>")
        
        # 处理子元素
        for child in element:
            self._xml_to_html(child, html_parts, level + 1)
        
        # 处理尾部文本
        if element.tail and element.tail.strip():
            html_parts.append(f"<p>{element.tail.strip()}</p>")
    
    def _analyze_structure(self, root: ET.Element) -> list:
        """分析文档结构
        
        Args:
            root: XML根元素
            
        Returns:
            list: 结构项列表
        """
        structure = []
        self._analyze_element(root, structure, 0)
        return structure
    
    def _analyze_element(self, element: ET.Element, structure: list, position: int) -> int:
        """递归分析元素
        
        Args:
            element: XML元素
            structure: 结构列表
            position: 当前位置
            
        Returns:
            int: 下一个位置
        """
        tag = element.tag.split('}')[-1]  # 处理命名空间
        
        # 识别结构元素
        if tag in ["title", "heading", "h1", "h2", "h3", "h4", "h5", "h6"]:
            level = 1
            if tag.startswith('h') and len(tag) == 2 and tag[1].isdigit():
                level = int(tag[1])
            structure.append({
                "type": "heading",
                "level": level,
                "title": element.text.strip() if element.text else "",
                "position": position
            })
        elif tag in ["table"]:
            structure.append({
                "type": "table",
                "position": position
            })
        elif tag in ["img", "image"]:
            structure.append({
                "type": "image",
                "src": element.attrib.get("src", ""),
                "alt": element.attrib.get("alt", ""),
                "position": position
            })
        elif tag in ["ul", "ol", "list"]:
            list_type = "ordered" if tag == "ol" else "unordered"
            structure.append({
                "type": "list",
                "list_type": list_type,
                "position": position
            })
        elif tag in ["pre", "code"]:
            structure.append({
                "type": "code_block",
                "position": position
            })
        
        # 递归处理子元素
        for child in element:
            position += 1
            position = self._analyze_element(child, structure, position)
        
        return position
    
    def _extract_semantics(self, root: ET.Element) -> Dict[str, Any]:
        """提取语义信息
        
        Args:
            root: XML根元素
            
        Returns:
            Dict[str, Any]: 语义信息字典
        """
        semantics = {
            "domain_tag": "",
            "section_id": {},
            "table_type": {},
            "list_type": {}
        }
        
        # 提取章节ID
        section_counter = 1
        self._extract_section_ids(root, semantics, section_counter)
        
        return semantics
    
    def _extract_section_ids(self, element: ET.Element, semantics: Dict[str, Any], counter: int) -> int:
        """递归提取章节ID
        
        Args:
            element: XML元素
            semantics: 语义信息字典
            counter: 章节计数器
            
        Returns:
            int: 更新后的计数器
        """
        tag = element.tag.split('}')[-1]  # 处理命名空间
        
        # 识别标题元素
        if tag in ["title", "heading", "h1", "h2", "h3", "h4", "h5", "h6"]:
            level = 1
            if tag.startswith('h') and len(tag) == 2 and tag[1].isdigit():
                level = int(tag[1])
            section_id = f"sec-{counter}"
            semantics["section_id"][section_id] = {
                "title": element.text.strip() if element.text else "",
                "level": level
            }
            counter += 1
        
        # 递归处理子元素
        for child in element:
            counter = self._extract_section_ids(child, semantics, counter)
        
        return counter
