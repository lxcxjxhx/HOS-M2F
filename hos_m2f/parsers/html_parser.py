"""HTML解析器"""

import hashlib
from typing import Dict, Any, Optional, Union
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse

from hos_m2f.model.universal_model import UniversalDocumentModel
from hos_m2f.parsers.base_parser import BaseParser


class HTMLParser(BaseParser):
    """HTML解析器"""
    
    def parse(self, content: Union[str, bytes], options: Optional[Dict[str, Any]] = None) -> UniversalDocumentModel:
        """解析HTML内容为中间模型
        
        Args:
            content: HTML内容
            options: 解析选项
            
        Returns:
            UniversalDocumentModel: 通用文档模型
        """
        options = options or {}
        
        # 确保content是字符串
        content = self._normalize_content(content)
        
        # 创建通用文档模型
        model = UniversalDocumentModel()
        
        # 1. 解析HTML (DOM解析层)
        soup = BeautifulSoup(content, 'html.parser')
        
        # 2. 提取元数据
        meta = self._extract_meta(soup)
        model.set_meta(meta)
        
        # 3. 提取资源 (资源抽取层)
        assets = []
        
        # 提取图片
        assets.extend(self._extract_images(soup))
        
        # 提取代码块（包括Mermaid）
        assets.extend(self._extract_code_blocks(soup))
        
        # 4. 重构内容 (内容重构层)
        html_content = self._extract_html_content(soup)
        model.set_html_content(html_content)
        
        # 5. 分析文档结构
        structure = self._analyze_structure(soup)
        for item in structure:
            model.add_structure_item(item)
        
        # 6. 提取语义信息
        semantics = self._extract_semantics(soup)
        model.get_json()["semantics"].update(semantics)
        
        # 7. 添加资源信息
        model.get_json()["assets"] = assets
        
        return model
    
    def _extract_meta(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """提取元数据
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            Dict[str, Any]: 元数据字典
        """
        meta = {}
        
        # 提取标题
        title_tag = soup.find('title')
        if title_tag:
            meta["title"] = title_tag.get_text().strip()
        
        # 提取meta标签中的信息
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            if tag.get('name') == 'description':
                meta["description"] = tag.get('content', '').strip()
            elif tag.get('name') == 'author':
                meta["author"] = tag.get('content', '').strip()
            elif tag.get('name') == 'keywords':
                keywords = tag.get('content', '').strip()
                if keywords:
                    meta["tags"] = [k.strip() for k in keywords.split(',')]
        
        # 提取Open Graph标签
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            property_name = tag.get('property', '').replace('og:', '')
            if property_name == 'title' and 'title' not in meta:
                meta["title"] = tag.get('content', '').strip()
            elif property_name == 'description' and 'description' not in meta:
                meta["description"] = tag.get('content', '').strip()
            elif property_name == 'image':
                meta["cover_image"] = tag.get('content', '').strip()
        
        return meta
    
    def _extract_images(self, soup: BeautifulSoup) -> list:
        """提取图片资源
        
        Args:
            soup: BeautifulSoup对象
            
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
        
        for i, img in enumerate(soup.find_all('img')):
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            if not src:
                continue
            
            # 处理图片资源
            if resource_manager:
                asset_info = resource_manager.process_image(src, alt)
                asset_id = asset_info['id']
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
            
            # 替换图片标签为自定义标签
            img.replace_with(f'<hos-image id="{asset_id}"/>')
        
        return assets
    
    def _extract_code_blocks(self, soup: BeautifulSoup) -> list:
        """提取代码块资源
        
        Args:
            soup: BeautifulSoup对象
            
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
        
        for i, pre in enumerate(soup.find_all('pre')):
            code = pre.find('code')
            if not code:
                continue
            
            # 提取代码内容
            code_content = code.get_text()
            
            # 检测语言
            language = ""  
            if code.get('class'):
                for cls in code.get('class'):
                    if cls.startswith('language-'):
                        language = cls[9:]
                        break
            
            # 检测Mermaid
            if language == 'mermaid' or 'mermaid' in code_content.lower():
                # 处理Mermaid资源
                if resource_manager:
                    asset_info = resource_manager.process_mermaid(code_content)
                    asset_id = asset_info['id']
                    assets.append(asset_info)
                else:
                    # 降级处理
                    asset_id = f"mermaid_{i:03d}"
                    assets.append({
                        "id": asset_id,
                        "type": "mermaid",
                        "language": "mermaid",
                        "content": code_content,
                        "local_path": f"assets/{asset_id}.svg"
                    })
                
                # 替换为自定义标签
                pre.replace_with(f'<hos-mermaid id="{asset_id}"/>')
            else:
                # 处理普通代码块
                if resource_manager:
                    asset_info = resource_manager.process_code_block(code_content, language)
                    asset_id = asset_info['id']
                    assets.append(asset_info)
                else:
                    # 降级处理
                    asset_id = f"code_{i:03d}"
                    assets.append({
                        "id": asset_id,
                        "type": "code",
                        "language": language,
                        "content": code_content,
                        "local_path": f"assets/{asset_id}.txt"
                    })
        
        return assets
    
    def _extract_html_content(self, soup: BeautifulSoup) -> str:
        """提取HTML内容
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            str: HTML内容
        """
        # 提取body内容
        body = soup.find('body')
        if body:
            return str(body)
        
        # 如果没有body标签，返回整个HTML
        return str(soup)
    
    def _analyze_structure(self, soup: BeautifulSoup) -> list:
        """分析文档结构
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            list: 结构项列表
        """
        structure = []
        
        # 分析标题层级
        for level in range(1, 7):
            headings = soup.find_all(f'h{level}')
            for i, heading in enumerate(headings):
                # 解码URL编码的标题
                title = unquote(heading.get_text().strip())
                structure.append({
                    "type": "heading",
                    "level": level,
                    "title": title,
                    "id": heading.get('id', '')
                })
        
        # 分析表格
        tables = soup.find_all('table')
        for i, table in enumerate(tables):
            structure.append({
                "type": "table",
                "id": table.get('id', f"table-{i+1}")
            })
        
        # 分析自定义图片标签
        hos_images = soup.find_all(lambda tag: tag.name == 'hos-image')
        for i, img in enumerate(hos_images):
            structure.append({
                "type": "image",
                "id": img.get('id', f"img-{i+1}")
            })
        
        # 分析列表
        lists = soup.find_all(['ul', 'ol'])
        for i, lst in enumerate(lists):
            list_type = "ordered" if lst.name == 'ol' else "unordered"
            structure.append({
                "type": "list",
                "list_type": list_type,
                "id": lst.get('id', f"list-{i+1}")
            })
        
        # 分析代码块
        code_blocks = soup.find_all(['pre', 'hos-mermaid'])
        for i, block in enumerate(code_blocks):
            block_type = "mermaid" if block.name == 'hos-mermaid' else "code_block"
            structure.append({
                "type": block_type,
                "id": block.get('id', f"code-{i+1}")
            })
        
        return structure
    
    def _extract_semantics(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """提取语义信息
        
        Args:
            soup: BeautifulSoup对象
            
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
        for level in range(1, 7):
            headings = soup.find_all(f'h{level}')
            for heading in headings:
                section_id = heading.get('id', f"sec-{section_counter}")
                # 解码URL编码
                section_id = unquote(section_id)
                semantics["section_id"][section_id] = {
                    "title": unquote(heading.get_text().strip()),
                    "level": level
                }
                section_counter += 1
        
        # 识别表格类型
        tables = soup.find_all('table')
        for i, table in enumerate(tables):
            table_id = table.get('id', f"table-{i+1}")
            # 简单的表格类型识别
            if 'class' in table.attrs and any('data' in cls.lower() for cls in table['class']):
                table_type = "data"
            else:
                table_type = "general"
            semantics["table_type"][table_id] = table_type
        
        # 识别列表类型
        lists = soup.find_all(['ul', 'ol'])
        for i, lst in enumerate(lists):
            list_id = lst.get('id', f"list-{i+1}")
            list_type = "ordered" if lst.name == 'ol' else "unordered"
            semantics["list_type"][list_id] = list_type
        
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
    
    def _normalize_content(self, content: Union[str, bytes]) -> str:
        """规范化内容
        
        Args:
            content: 原始内容
            
        Returns:
            str: 规范化后的内容
        """
        if isinstance(content, bytes):
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                return content.decode('latin-1')
        return content
