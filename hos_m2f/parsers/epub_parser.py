"""EPUB解析器"""

import io
import zipfile
from typing import Dict, Any, Optional, Union
import xml.etree.ElementTree as ET

from hos_m2f.model.universal_model import UniversalDocumentModel
from hos_m2f.parsers.base_parser import BaseParser


class EPUBParser(BaseParser):
    """EPUB解析器"""
    
    def parse(self, content: Union[str, bytes], options: Optional[Dict[str, Any]] = None) -> UniversalDocumentModel:
        """解析EPUB内容为中间模型
        
        Args:
            content: EPUB内容
            options: 解析选项
            
        Returns:
            UniversalDocumentModel: 通用文档模型
        """
        options = options or {}
        
        # 打开EPUB文件
        if isinstance(content, bytes):
            epub_file = zipfile.ZipFile(io.BytesIO(content), 'r')
        else:
            epub_file = zipfile.ZipFile(content, 'r')
        
        # 创建通用文档模型
        model = UniversalDocumentModel()
        
        try:
            # 1. 提取元数据
            meta = self._extract_meta(epub_file)
            model.set_meta(meta)
            
            # 2. 生成HTML内容
            html_content = self._generate_html_content(epub_file, options)
            model.set_html_content(html_content)
            
            # 3. 分析文档结构
            structure = self._analyze_structure(epub_file)
            for item in structure:
                model.add_structure_item(item)
            
            # 4. 提取语义信息
            semantics = self._extract_semantics(epub_file)
            model.get_json()["semantics"].update(semantics)
        finally:
            epub_file.close()
        
        return model
    
    def _extract_meta(self, epub_file: zipfile.ZipFile) -> Dict[str, Any]:
        """提取元数据
        
        Args:
            epub_file: EPUB文件对象
            
        Returns:
            Dict[str, Any]: 元数据字典
        """
        meta = {}
        
        # 查找content.opf文件
        opf_path = None
        for file_name in epub_file.namelist():
            if file_name.endswith('content.opf'):
                opf_path = file_name
                break
        
        if opf_path:
            with epub_file.open(opf_path) as f:
                tree = ET.parse(f)
                root = tree.getroot()
                
                # 提取dc:metadata
                ns = {
                    'dc': 'http://purl.org/dc/elements/1.1/',
                    'opf': 'http://www.idpf.org/2007/opf'
                }
                
                # 提取标题
                title_elem = root.find('.//dc:title', ns)
                if title_elem is not None:
                    meta["title"] = title_elem.text
                
                # 提取作者
                author_elem = root.find('.//dc:creator', ns)
                if author_elem is not None:
                    meta["author"] = author_elem.text
                
                # 提取描述
                desc_elem = root.find('.//dc:description', ns)
                if desc_elem is not None:
                    meta["description"] = desc_elem.text
                
                # 提取标签
                subject_elems = root.findall('.//dc:subject', ns)
                if subject_elems:
                    meta["tags"] = [elem.text for elem in subject_elems if elem.text]
                
                # 提取出版日期
                date_elem = root.find('.//dc:date', ns)
                if date_elem is not None:
                    meta["publish_date"] = date_elem.text
        
        return meta
    
    def _generate_html_content(self, epub_file: zipfile.ZipFile, options: Dict[str, Any]) -> str:
        """生成HTML内容
        
        Args:
            epub_file: EPUB文件对象
            options: 生成选项
            
        Returns:
            str: HTML内容
        """
        html_parts = []
        
        # 收集所有HTML文件
        html_files = []
        for file_name in epub_file.namelist():
            if file_name.endswith('.html') or file_name.endswith('.xhtml'):
                html_files.append(file_name)
        
        # 按顺序读取HTML文件
        for html_file in sorted(html_files):
            try:
                with epub_file.open(html_file) as f:
                    html_content = f.read().decode('utf-8')
                    html_parts.append(html_content)
            except Exception as e:
                print(f"Warning: Failed to read {html_file}: {e}")
        
        return "<div class='content'>" + "\n".join(html_parts) + "</div>"
    
    def _analyze_structure(self, epub_file: zipfile.ZipFile) -> list:
        """分析文档结构
        
        Args:
            epub_file: EPUB文件对象
            
        Returns:
            list: 结构项列表
        """
        structure = []
        
        # 查找toc.ncx文件
        ncx_path = None
        for file_name in epub_file.namelist():
            if file_name.endswith('toc.ncx'):
                ncx_path = file_name
                break
        
        if ncx_path:
            with epub_file.open(ncx_path) as f:
                tree = ET.parse(f)
                root = tree.getroot()
                
                # 提取导航项
                ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
                nav_points = root.findall('.//ncx:navPoint', ns)
                
                for i, nav_point in enumerate(nav_points):
                    nav_label = nav_point.find('.//ncx:navLabel/ncx:text', ns)
                    if nav_label is not None:
                        structure.append({
                            "type": "heading",
                            "level": 1,
                            "title": nav_label.text,
                            "position": i
                        })
        
        return structure
    
    def _extract_semantics(self, epub_file: zipfile.ZipFile) -> Dict[str, Any]:
        """提取语义信息
        
        Args:
            epub_file: EPUB文件对象
            
        Returns:
            Dict[str, Any]: 语义信息字典
        """
        semantics = {
            "domain_tag": "ebook",
            "section_id": {},
            "table_type": {},
            "list_type": {}
        }
        
        # 从toc.ncx提取章节ID
        ncx_path = None
        for file_name in epub_file.namelist():
            if file_name.endswith('toc.ncx'):
                ncx_path = file_name
                break
        
        if ncx_path:
            with epub_file.open(ncx_path) as f:
                tree = ET.parse(f)
                root = tree.getroot()
                
                ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
                nav_points = root.findall('.//ncx:navPoint', ns)
                
                for i, nav_point in enumerate(nav_points):
                    nav_label = nav_point.find('.//ncx:navLabel/ncx:text', ns)
                    if nav_label is not None:
                        section_id = f"sec-{i+1}"
                        semantics["section_id"][section_id] = {
                            "title": nav_label.text,
                            "level": 1,
                            "position": i
                        }
        
        return semantics
