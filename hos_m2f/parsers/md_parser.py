"""Markdown解析器"""

import re
from typing import Dict, Any, Optional, Union
import mistune
from urllib.parse import unquote, urlparse

from hos_m2f.model.universal_model import UniversalDocumentModel
from hos_m2f.parsers.base_parser import BaseParser


class MDParser(BaseParser):
    """Markdown解析器"""
    
    def parse(self, content: Union[str, bytes], options: Optional[Dict[str, Any]] = None) -> UniversalDocumentModel:
        """解析Markdown内容为中间模型
        
        Args:
            content: Markdown内容
            options: 解析选项
            
        Returns:
            UniversalDocumentModel: 通用文档模型
        """
        options = options or {}
        
        # 确保content是字符串
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        
        # 创建通用文档模型
        model = UniversalDocumentModel()
        
        # 1. 提取YAML头信息
        meta = self._extract_yaml_front_matter(content)
        model.set_meta(meta)
        
        # 2. 移除YAML头信息，获取纯Markdown内容
        markdown_content = self._remove_yaml_front_matter(content)
        
        # 3. 解析Markdown为HTML
        html_content = self._markdown_to_html(markdown_content, options)
        
        # 4. 提取资源 (资源抽取层)
        assets = []
        
        # 提取图片
        assets.extend(self._extract_images(markdown_content))
        
        # 提取代码块（包括Mermaid）
        assets.extend(self._extract_code_blocks(markdown_content))
        
        # 5. 分析文档结构
        structure = self._analyze_structure(markdown_content)
        for item in structure:
            model.add_structure_item(item)
        
        # 6. 提取语义信息
        semantics = self._extract_semantics(markdown_content)
        model.get_json()["semantics"].update(semantics)
        
        # 7. 添加资源信息
        model.get_json()["assets"] = assets
        
        # 8. 设置HTML内容
        model.set_html_content(html_content)
        
        return model
    
    def _extract_yaml_front_matter(self, content: str) -> Dict[str, Any]:
        """提取YAML头信息
        
        Args:
            content: Markdown内容
            
        Returns:
            Dict[str, Any]: 元数据字典
        """
        import yaml
        
        # 检查是否有YAML头信息
        yaml_pattern = re.compile(r'^---\s*$((?:.|\n)*?)^---\s*$', re.MULTILINE)
        match = yaml_pattern.match(content)
        
        if match:
            try:
                yaml_content = match.group(1)
                meta = yaml.safe_load(yaml_content)
                if isinstance(meta, dict):
                    return meta
            except Exception as e:
                print(f"Warning: Failed to parse YAML front matter: {e}")
        
        # 从内容中提取基本元数据
        return self._extract_basic_meta(content)
    
    def _extract_basic_meta(self, content: str) -> Dict[str, Any]:
        """提取基本元数据
        
        Args:
            content: Markdown内容
            
        Returns:
            Dict[str, Any]: 基本元数据
        """
        meta = {}
        
        # 提取标题
        title_pattern = re.compile(r'^#\s+(.*)$', re.MULTILINE)
        title_match = title_pattern.search(content)
        if title_match:
            meta["title"] = title_match.group(1).strip()
        
        # 提取标签
        tags_pattern = re.compile(r'^tags:\s*\[(.*?)\]$', re.MULTILINE)
        tags_match = tags_pattern.search(content)
        if tags_match:
            tags = [tag.strip() for tag in tags_match.group(1).split(',')]
            meta["tags"] = tags
        
        return meta
    
    def _remove_yaml_front_matter(self, content: str) -> str:
        """移除YAML头信息
        
        Args:
            content: Markdown内容
            
        Returns:
            str: 纯Markdown内容
        """
        yaml_pattern = re.compile(r'^---\s*$((?:.|\n)*?)^---\s*$', re.MULTILINE)
        return yaml_pattern.sub('', content).strip()
    
    def _extract_images(self, markdown_content: str) -> list:
        """提取图片资源
        
        Args:
            markdown_content: Markdown内容
            
        Returns:
            list: 资源列表
        """
        assets = []
        
        # 尝试获取资源管理器
        try:
            from hos_m2f.resources.resource_manager import ResourceManager
            resource_manager = ResourceManager()
        except Exception:
            resource_manager = None
        
        # 匹配Markdown图片语法
        image_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)', re.MULTILINE)
        matches = image_pattern.findall(markdown_content)
        
        for i, (alt, src) in enumerate(matches):
            # 处理图片资源
            if resource_manager:
                asset_info = resource_manager.process_image(src, alt)
                assets.append(asset_info)
            else:
                # 降级处理
                asset_id = f"img_{i:03d}"
                local_path = self._generate_local_path(src, asset_id)
                assets.append({
                    "id": asset_id,
                    "type": "image",
                    "src": src,
                    "alt": alt,
                    "local_path": local_path
                })
        
        return assets
    
    def _extract_code_blocks(self, markdown_content: str) -> list:
        """提取代码块资源
        
        Args:
            markdown_content: Markdown内容
            
        Returns:
            list: 资源列表
        """
        assets = []
        
        # 尝试获取资源管理器
        try:
            from hos_m2f.resources.resource_manager import ResourceManager
            resource_manager = ResourceManager()
        except Exception:
            resource_manager = None
        
        # 匹配代码块
        code_pattern = re.compile(r'```(\w*)\n((?:.|\n)*?)```', re.MULTILINE)
        matches = code_pattern.findall(markdown_content)
        
        for i, (language, content) in enumerate(matches):
            # 检测Mermaid
            if language == 'mermaid' or 'mermaid' in content.lower():
                # 处理Mermaid资源
                if resource_manager:
                    asset_info = resource_manager.process_mermaid(content)
                    assets.append(asset_info)
                else:
                    # 降级处理
                    asset_id = f"mermaid_{i:03d}"
                    assets.append({
                        "id": asset_id,
                        "type": "mermaid",
                        "language": "mermaid",
                        "content": content,
                        "local_path": f"assets/{asset_id}.svg"
                    })
            else:
                # 处理普通代码块
                if resource_manager:
                    asset_info = resource_manager.process_code_block(content, language)
                    assets.append(asset_info)
                else:
                    # 降级处理
                    asset_id = f"code_{i:03d}"
                    assets.append({
                        "id": asset_id,
                        "type": "code",
                        "language": language,
                        "content": content,
                        "local_path": f"assets/{asset_id}.txt"
                    })
        
        return assets
    
    def _process_content(self, markdown_content: str) -> str:
        """处理内容，替换资源为自定义标签
        
        Args:
            markdown_content: Markdown内容
            
        Returns:
            str: 处理后的内容
        """
        # 直接返回原始Markdown内容，避免破坏表格结构
        # 资源提取和替换将在解析为HTML后进行
        return markdown_content
    
    def _markdown_to_html(self, markdown_content: str, options: Dict[str, Any]) -> str:
        """将Markdown转换为HTML
        
        Args:
            markdown_content: Markdown内容
            options: 转换选项
            
        Returns:
            str: HTML内容
        """
        # 创建Markdown渲染器
        markdown = mistune.create_markdown(
            plugins=[
                'url',
                'task_lists',
                'table',
                'strikethrough',
                'footnotes'
            ]
        )
        
        # 转换为HTML
        html = markdown(markdown_content)
        
        return html
    
    def _analyze_structure(self, markdown_content: str) -> list:
        """分析文档结构
        
        Args:
            markdown_content: Markdown内容
            
        Returns:
            list: 结构项列表
        """
        structure = []
        
        # 分析标题层级
        lines = markdown_content.split('\n')
        for i, line in enumerate(lines):
            # 匹配标题
            heading_match = re.match(r'^\s*(#{1,6})\s+(.*)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                title = unquote(heading_match.group(2).strip())
                structure.append({
                    "type": "heading",
                    "level": level,
                    "title": title,
                    "position": i
                })
            
            # 匹配表格
            elif re.match(r'^\s*\|.*\|$', line) and i > 0 and re.match(r'^\s*\|.*\|$', lines[i-1]):
                if not any(item.get('type') == 'table' and item.get('position') == i-1 for item in structure):
                    structure.append({
                        "type": "table",
                        "position": i-1
                    })
            
            # 匹配代码块
            elif re.match(r'^\s*```', line):
                structure.append({
                    "type": "code_block",
                    "position": i
                })
            
            # 匹配自定义图片标签
            elif re.match(r'^\s*<hos-image', line):
                structure.append({
                    "type": "image",
                    "position": i
                })
            
            # 匹配列表
            elif re.match(r'^\s*(\*|\-|\+|\d+\.)\s+', line):
                list_type = "ordered" if re.match(r'^\s*\d+\.', line) else "unordered"
                if not any(item.get('type') == 'list' and item.get('position') == i for item in structure):
                    structure.append({
                        "type": "list",
                        "list_type": list_type,
                        "position": i
                    })
        
        return structure
    
    def _extract_semantics(self, markdown_content: str) -> Dict[str, Any]:
        """提取语义信息
        
        Args:
            markdown_content: Markdown内容
            
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
        lines = markdown_content.split('\n')
        section_counter = 1
        for i, line in enumerate(lines):
            heading_match = re.match(r'^(#{1,6})\s+(.*)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                title = unquote(heading_match.group(2).strip())
                section_id = f"sec-{section_counter}"
                semantics["section_id"][section_id] = {
                    "title": title,
                    "level": level,
                    "position": i
                }
                section_counter += 1
        
        # 识别列表类型
        list_position = 0
        for i, line in enumerate(lines):
            if re.match(r'^\d+\.', line):
                semantics["list_type"][f"list-{list_position}"] = "ordered"
                list_position += 1
            elif re.match(r'^(\*|\-|\+)\s+', line):
                semantics["list_type"][f"list-{list_position}"] = "unordered"
                list_position += 1
        
        return semantics
    
    def _generate_local_path(self, url: str, asset_id: str) -> str:
        """生成本地路径
        
        Args:
            url: 原始URL
            asset_id: 资源ID
            
        Returns:
            str: 本地路径
        """
        # 解析URL
        parsed = urlparse(url)
        
        # 提取文件扩展名
        path = parsed.path
        ext = path.split('.')[-1] if '.' in path else 'png'
        
        # 确保扩展名是有效的图片格式
        valid_extensions = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg']
        if ext.lower() not in valid_extensions:
            ext = 'png'
        
        return f"assets/{asset_id}.{ext.lower()}"
