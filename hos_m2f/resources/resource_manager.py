"""资源管理模块"""

import os
import hashlib
import requests
from typing import Dict, Any, List, Optional
import json
import time
from io import BytesIO


class ResourceManager:
    """资源管理器
    
    负责资源的提取、管理、存储和引用
    """
    
    def __init__(self, base_dir: str = "."):
        """初始化资源管理器
        
        Args:
            base_dir: 基础目录
        """
        self.base_dir = base_dir
        self.assets_dir = os.path.join(base_dir, "assets")
        self.images_dir = os.path.join(self.assets_dir, "images")
        self.code_dir = os.path.join(self.assets_dir, "code")
        self.mermaid_dir = os.path.join(self.assets_dir, "mermaid")
        self.fonts_dir = os.path.join(self.assets_dir, "fonts")
        self.other_dir = os.path.join(self.assets_dir, "other")
        
        # 创建必要的目录
        self._create_directories()
        
        # 资源缓存，用于去重
        self.resource_cache = {}
        self.resource_counter = {
            "image": 0,
            "code": 0,
            "mermaid": 0,
            "font": 0,
            "other": 0
        }
        
        # 资源版本控制
        self.resource_versions = {}
        self.current_version = "1.0.0"
    
    def _create_directories(self) -> None:
        """创建必要的目录"""
        directories = [
            self.assets_dir,
            self.images_dir,
            self.code_dir,
            self.mermaid_dir,
            self.fonts_dir,
            self.other_dir
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def process_image(self, src: str, alt: str = "", title: str = "") -> Dict[str, Any]:
        """处理图片资源
        
        Args:
            src: 图片源地址
            alt: 图片替代文本
            title: 图片标题
            
        Returns:
            Dict[str, Any]: 处理后的资源信息
        """
        # 计算资源哈希，用于去重
        resource_hash = hashlib.md5(src.encode()).hexdigest()
        
        # 检查是否已处理过
        if resource_hash in self.resource_cache:
            return self.resource_cache[resource_hash]
        
        # 生成资源ID
        asset_id = f"img_{self.resource_counter['image']:03d}"
        self.resource_counter['image'] += 1
        
        # 确定文件扩展名
        import os.path
        ext = os.path.splitext(src)[1].lower()
        if not ext:
            ext = ".png"
        elif ext not in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"]:
            ext = ".png"
        
        # 生成本地路径
        local_path = os.path.join("assets", "images", f"{asset_id}{ext}")
        full_local_path = os.path.join(self.images_dir, f"{asset_id}{ext}")
        
        # 处理图片
        try:
            if os.path.exists(src):
                # 处理本地图片
                import shutil
                shutil.copy2(src, full_local_path)
            else:
                # 处理远程图片
                self._download_image(src, full_local_path)
        except Exception as e:
            print(f"Warning: Failed to process image {src}: {e}")
        
        # 构建资源信息
        asset_info = {
            "id": asset_id,
            "type": "image",
            "src": src,
            "alt": alt,
            "title": title,
            "local_path": local_path,
            "hash": resource_hash,
            "created_at": time.time(),
            "version": self.current_version
        }
        
        # 缓存资源
        self.resource_cache[resource_hash] = asset_info
        
        # 记录版本
        self.resource_versions[asset_id] = asset_info
        
        return asset_info
    
    def _download_image(self, url: str, local_path: str) -> None:
        """下载图片
        
        Args:
            url: 图片URL
            local_path: 本地保存路径
        """
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            f.write(response.content)
    
    def process_code_block(self, code: str, language: str = "") -> Dict[str, Any]:
        """处理代码块资源
        
        Args:
            code: 代码内容
            language: 代码语言
            
        Returns:
            Dict[str, Any]: 处理后的资源信息
        """
        # 计算资源哈希，用于去重
        resource_hash = hashlib.md5((code + language).encode()).hexdigest()
        
        # 检查是否已处理过
        if resource_hash in self.resource_cache:
            return self.resource_cache[resource_hash]
        
        # 生成资源ID
        asset_id = f"code_{self.resource_counter['code']:03d}"
        self.resource_counter['code'] += 1
        
        # 生成本地路径
        local_path = os.path.join("assets", "code", f"{asset_id}.txt")
        full_local_path = os.path.join(self.code_dir, f"{asset_id}.txt")
        
        # 保存代码
        with open(full_local_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # 构建资源信息
        asset_info = {
            "id": asset_id,
            "type": "code",
            "language": language,
            "content": code,
            "local_path": local_path,
            "hash": resource_hash
        }
        
        # 缓存资源
        self.resource_cache[resource_hash] = asset_info
        
        return asset_info
    
    def process_mermaid(self, code: str) -> Dict[str, Any]:
        """处理Mermaid图表资源
        
        Args:
            code: Mermaid代码
            
        Returns:
            Dict[str, Any]: 处理后的资源信息
        """
        # 计算资源哈希，用于去重
        resource_hash = hashlib.md5(code.encode()).hexdigest()
        
        # 检查是否已处理过
        if resource_hash in self.resource_cache:
            return self.resource_cache[resource_hash]
        
        # 生成资源ID
        asset_id = f"mermaid_{self.resource_counter['mermaid']:03d}"
        self.resource_counter['mermaid'] += 1
        
        # 生成本地路径
        local_path = os.path.join("assets", "mermaid", f"{asset_id}.svg")
        full_local_path = os.path.join(self.mermaid_dir, f"{asset_id}.svg")
        
        # 保存Mermaid代码
        with open(full_local_path.replace('.svg', '.md'), 'w', encoding='utf-8') as f:
            f.write(f"```mermaid\n{code}\n```")
        
        # 构建资源信息
        asset_info = {
            "id": asset_id,
            "type": "mermaid",
            "content": code,
            "local_path": local_path,
            "hash": resource_hash
        }
        
        # 缓存资源
        self.resource_cache[resource_hash] = asset_info
        
        return asset_info
    
    def get_all_resources(self) -> List[Dict[str, Any]]:
        """获取所有处理过的资源
        
        Returns:
            List[Dict[str, Any]]: 资源列表
        """
        return list(self.resource_cache.values())
    
    def process_font(self, font_path: str, font_name: str = "", font_family: str = "") -> Dict[str, Any]:
        """处理字体资源
        
        Args:
            font_path: 字体文件路径
            font_name: 字体名称
            font_family: 字体家族
            
        Returns:
            Dict[str, Any]: 处理后的资源信息
        """
        # 计算资源哈希，用于去重
        resource_hash = hashlib.md5(font_path.encode()).hexdigest()
        
        # 检查是否已处理过
        if resource_hash in self.resource_cache:
            return self.resource_cache[resource_hash]
        
        # 生成资源ID
        asset_id = f"font_{self.resource_counter['font']:03d}"
        self.resource_counter['font'] += 1
        
        # 确定文件扩展名
        import os.path
        ext = os.path.splitext(font_path)[1].lower()
        if not ext:
            ext = ".ttf"
        
        # 生成本地路径
        local_path = os.path.join("assets", "fonts", f"{asset_id}{ext}")
        full_local_path = os.path.join(self.fonts_dir, f"{asset_id}{ext}")
        
        # 处理字体文件
        try:
            if os.path.exists(font_path):
                # 处理本地字体
                import shutil
                shutil.copy2(font_path, full_local_path)
            else:
                # 处理远程字体
                self._download_resource(font_path, full_local_path)
        except Exception as e:
            print(f"Warning: Failed to process font {font_path}: {e}")
        
        # 构建资源信息
        asset_info = {
            "id": asset_id,
            "type": "font",
            "path": font_path,
            "name": font_name,
            "family": font_family,
            "local_path": local_path,
            "hash": resource_hash,
            "created_at": time.time(),
            "version": self.current_version
        }
        
        # 缓存资源
        self.resource_cache[resource_hash] = asset_info
        
        # 记录版本
        self.resource_versions[asset_id] = asset_info
        
        return asset_info
    
    def process_other(self, resource_path: str, resource_type: str = "other", name: str = "") -> Dict[str, Any]:
        """处理其他资源
        
        Args:
            resource_path: 资源路径
            resource_type: 资源类型
            name: 资源名称
            
        Returns:
            Dict[str, Any]: 处理后的资源信息
        """
        # 计算资源哈希，用于去重
        resource_hash = hashlib.md5(resource_path.encode()).hexdigest()
        
        # 检查是否已处理过
        if resource_hash in self.resource_cache:
            return self.resource_cache[resource_hash]
        
        # 生成资源ID
        asset_id = f"other_{self.resource_counter['other']:03d}"
        self.resource_counter['other'] += 1
        
        # 确定文件扩展名
        import os.path
        ext = os.path.splitext(resource_path)[1].lower()
        
        # 生成本地路径
        local_path = os.path.join("assets", "other", f"{asset_id}{ext}")
        full_local_path = os.path.join(self.other_dir, f"{asset_id}{ext}")
        
        # 处理资源文件
        try:
            if os.path.exists(resource_path):
                # 处理本地资源
                import shutil
                shutil.copy2(resource_path, full_local_path)
            else:
                # 处理远程资源
                self._download_resource(resource_path, full_local_path)
        except Exception as e:
            print(f"Warning: Failed to process resource {resource_path}: {e}")
        
        # 构建资源信息
        asset_info = {
            "id": asset_id,
            "type": resource_type,
            "path": resource_path,
            "name": name,
            "local_path": local_path,
            "hash": resource_hash,
            "created_at": time.time(),
            "version": self.current_version
        }
        
        # 缓存资源
        self.resource_cache[resource_hash] = asset_info
        
        # 记录版本
        self.resource_versions[asset_id] = asset_info
        
        return asset_info
    
    def _download_resource(self, url: str, local_path: str) -> None:
        """下载资源
        
        Args:
            url: 资源URL
            local_path: 本地保存路径
        """
        response = requests.get(url, timeout=15, verify=False)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            f.write(response.content)
    
    def get_resource_by_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取资源
        
        Args:
            resource_id: 资源ID
            
        Returns:
            Optional[Dict[str, Any]]: 资源信息
        """
        for resource in self.resource_cache.values():
            if resource.get('id') == resource_id:
                return resource
        return None
    
    def get_resources_by_type(self, resource_type: str) -> List[Dict[str, Any]]:
        """根据类型获取资源
        
        Args:
            resource_type: 资源类型
            
        Returns:
            List[Dict[str, Any]]: 资源列表
        """
        return [resource for resource in self.resource_cache.values() if resource.get('type') == resource_type]
    
    def clean_unused_resources(self) -> int:
        """清理未使用的资源
        
        Returns:
            int: 清理的资源数量
        """
        # 这里可以实现更复杂的清理逻辑
        # 例如检查资源是否被引用，或者根据时间戳清理
        return 0
    
    def update_resource_version(self, resource_id: str, new_version: str) -> bool:
        """更新资源版本
        
        Args:
            resource_id: 资源ID
            new_version: 新版本
            
        Returns:
            bool: 更新是否成功
        """
        for resource in self.resource_cache.values():
            if resource.get('id') == resource_id:
                resource['version'] = new_version
                resource['updated_at'] = time.time()
                self.resource_versions[resource_id] = resource
                return True
        return False
    
    def load_resource_map(self, input_path: str) -> None:
        """加载资源映射
        
        Args:
            input_path: 输入路径
        """
        if not os.path.exists(input_path):
            return
        
        with open(input_path, 'r', encoding='utf-8') as f:
            resource_map = json.load(f)
        
        # 恢复资源缓存
        for resource in resource_map.get('resources', []):
            self.resource_cache[resource['hash']] = resource
        
        # 恢复计数器
        self.resource_counter.update(resource_map.get('counters', {}))
        
        # 恢复版本信息
        self.resource_versions.update(resource_map.get('versions', {}))
        self.current_version = resource_map.get('current_version', self.current_version)
    
    def save_resource_map(self, output_path: str) -> None:
        """保存资源映射
        
        Args:
            output_path: 输出路径
        """
        resource_map = {
            "resources": self.get_all_resources(),
            "counters": self.resource_counter,
            "versions": self.resource_versions,
            "current_version": self.current_version,
            "generated_at": time.time()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(resource_map, f, ensure_ascii=False, indent=2)
