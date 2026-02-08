"""版本控制模块"""

import os
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime


class VersionControl:
    """版本控制器
    
    用于管理文档的版本历史和追踪
    """
    
    def __init__(self, base_dir: str = "."):
        """初始化版本控制器
        
        Args:
            base_dir: 基础目录
        """
        self.base_dir = base_dir
        self.version_dir = os.path.join(base_dir, ".versions")
        
        # 创建版本目录
        if not os.path.exists(self.version_dir):
            os.makedirs(self.version_dir, exist_ok=True)
        
        # 版本历史缓存
        self.version_history = {}
        
        # 版本号格式
        self.version_format = "{major}.{minor}.{patch}"
    
    def create_version(self, document_path: str, content: str, message: str = "", author: str = "") -> Dict[str, Any]:
        """创建文档版本
        
        Args:
            document_path: 文档路径
            content: 文档内容
            message: 版本说明
            author: 作者
            
        Returns:
            Dict[str, Any]: 版本信息
        """
        # 计算文档哈希
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # 生成版本ID
        version_id = f"v{datetime.now().strftime('%Y%m%d%H%M%S')}_{content_hash[:8]}"
        
        # 获取文档相对路径
        relative_path = os.path.relpath(document_path, self.base_dir)
        
        # 生成版本文件路径
        version_file = os.path.join(self.version_dir, f"{version_id}.json")
        
        # 生成版本号
        version_number = self._generate_version_number(document_path)
        
        # 创建版本信息
        version_info = {
            "id": version_id,
            "version": version_number,
            "document": relative_path,
            "timestamp": datetime.now().isoformat(),
            "author": author,
            "message": message,
            "content_hash": content_hash,
            "changes": self._detect_changes(document_path, content)
        }
        
        # 保存版本信息
        self._save_version(version_info, version_file)
        
        # 更新版本历史
        self._update_version_history(document_path, version_info)
        
        return version_info
    
    def get_version_history(self, document_path: str) -> List[Dict[str, Any]]:
        """获取文档版本历史
        
        Args:
            document_path: 文档路径
            
        Returns:
            List[Dict[str, Any]]: 版本历史列表
        """
        relative_path = os.path.relpath(document_path, self.base_dir)
        return self.version_history.get(relative_path, [])
    
    def get_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """获取指定版本
        
        Args:
            version_id: 版本ID
            
        Returns:
            Optional[Dict[str, Any]]: 版本信息
        """
        version_file = os.path.join(self.version_dir, f"{version_id}.json")
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def revert_to_version(self, document_path: str, version_id: str) -> bool:
        """回滚到指定版本
        
        Args:
            document_path: 文档路径
            version_id: 版本ID
            
        Returns:
            bool: 回滚是否成功
        """
        try:
            # 获取版本信息
            version_info = self.get_version(version_id)
            if not version_info:
                return False
            
            # 检查版本是否属于指定文档
            relative_path = os.path.relpath(document_path, self.base_dir)
            if version_info.get('document') != relative_path:
                return False
            
            # 读取版本内容
            content_file = os.path.join(self.version_dir, f"{version_id}.content")
            if not os.path.exists(content_file):
                return False
            
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 写回文档
            with open(document_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"Error reverting to version: {e}")
            return False
    
    def compare_versions(self, version_id1: str, version_id2: str) -> Dict[str, Any]:
        """比较两个版本的差异
        
        Args:
            version_id1: 版本1 ID
            version_id2: 版本2 ID
            
        Returns:
            Dict[str, Any]: 差异信息
        """
        version1 = self.get_version(version_id1)
        version2 = self.get_version(version_id2)
        
        if not version1 or not version2:
            return {"error": "One or both versions not found"}
        
        # 读取版本内容
        content1 = self._get_version_content(version_id1)
        content2 = self._get_version_content(version_id2)
        
        # 比较内容
        diff = self._diff_content(content1, content2)
        
        return {
            "version1": version1,
            "version2": version2,
            "diff": diff
        }
    
    def _generate_version_number(self, document_path: str) -> str:
        """生成版本号
        
        Args:
            document_path: 文档路径
            
        Returns:
            str: 版本号
        """
        relative_path = os.path.relpath(document_path, self.base_dir)
        history = self.get_version_history(document_path)
        
        if not history:
            return "1.0.0"
        
        # 获取最新版本号（现在在列表开头）
        latest_version = history[0].get('version', '1.0.0')
        
        # 解析版本号
        try:
            major, minor, patch = map(int, latest_version.split('.'))
            # 递增补丁号
            patch += 1
            return f"{major}.{minor}.{patch}"
        except:
            return "1.0.0"
    
    def _detect_changes(self, document_path: str, content: str) -> Dict[str, Any]:
        """检测文档变更
        
        Args:
            document_path: 文档路径
            content: 新内容
            
        Returns:
            Dict[str, Any]: 变更信息
        """
        relative_path = os.path.relpath(document_path, self.base_dir)
        history = self.get_version_history(document_path)
        
        if not history:
            return {"type": "initial", "description": "Initial version"}
        
        # 获取最新版本（现在在列表开头）
        latest_version = history[0]
        latest_content = self._get_version_content(latest_version['id'])
        
        # 计算变更大小
        old_lines = len(latest_content.split('\n')) if latest_content else 0
        new_lines = len(content.split('\n'))
        
        return {
            "type": "update",
            "description": f"Updated from version {latest_version['version']}",
            "lines_added": max(0, new_lines - old_lines),
            "lines_removed": max(0, old_lines - new_lines)
        }
    
    def _save_version(self, version_info: Dict[str, Any], version_file: str) -> None:
        """保存版本信息
        
        Args:
            version_info: 版本信息
            version_file: 版本文件路径
        """
        # 保存版本信息
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_info, f, ensure_ascii=False, indent=2)
        
        # 保存版本内容
        content_file = version_file.replace('.json', '.content')
        document_path = os.path.join(self.base_dir, version_info['document'])
        if os.path.exists(document_path):
            with open(document_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def _update_version_history(self, document_path: str, version_info: Dict[str, Any]) -> None:
        """更新版本历史
        
        Args:
            document_path: 文档路径
            version_info: 版本信息
        """
        relative_path = os.path.relpath(document_path, self.base_dir)
        
        if relative_path not in self.version_history:
            self.version_history[relative_path] = []
        
        # 插入到列表开头，确保最新版本在前
        self.version_history[relative_path].insert(0, version_info)
        
        # 保存版本历史
        history_file = os.path.join(self.version_dir, "history.json")
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.version_history, f, ensure_ascii=False, indent=2)
    
    def _get_version_content(self, version_id: str) -> str:
        """获取版本内容
        
        Args:
            version_id: 版本ID
            
        Returns:
            str: 版本内容
        """
        content_file = os.path.join(self.version_dir, f"{version_id}.content")
        if os.path.exists(content_file):
            with open(content_file, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def _diff_content(self, content1: str, content2: str) -> List[Dict[str, Any]]:
        """比较内容差异
        
        Args:
            content1: 内容1
            content2: 内容2
            
        Returns:
            List[Dict[str, Any]]: 差异列表
        """
        lines1 = content1.split('\n')
        lines2 = content2.split('\n')
        
        diff = []
        max_lines = max(len(lines1), len(lines2))
        
        for i in range(max_lines):
            if i >= len(lines1):
                # 新增行
                diff.append({
                    "type": "add",
                    "line": i + 1,
                    "content": lines2[i]
                })
            elif i >= len(lines2):
                # 删除行
                diff.append({
                    "type": "remove",
                    "line": i + 1,
                    "content": lines1[i]
                })
            elif lines1[i] != lines2[i]:
                # 修改行
                diff.append({
                    "type": "change",
                    "line": i + 1,
                    "old_content": lines1[i],
                    "new_content": lines2[i]
                })
        
        return diff
    
    def load_history(self) -> None:
        """加载版本历史"""
        history_file = os.path.join(self.version_dir, "history.json")
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                self.version_history = json.load(f)
    
    def cleanup_versions(self, document_path: str, keep_last: int = 10) -> int:
        """清理旧版本
        
        Args:
            document_path: 文档路径
            keep_last: 保留最近的版本数
            
        Returns:
            int: 清理的版本数
        """
        relative_path = os.path.relpath(document_path, self.base_dir)
        history = self.get_version_history(document_path)
        
        if len(history) <= keep_last:
            return 0
        
        # 确定要删除的版本（保留前keep_last个，删除后面的）
        versions_to_delete = history[keep_last:]
        deleted_count = 0
        
        for version in versions_to_delete:
            version_id = version['id']
            version_file = os.path.join(self.version_dir, f"{version_id}.json")
            content_file = os.path.join(self.version_dir, f"{version_id}.content")
            
            # 删除版本文件
            if os.path.exists(version_file):
                os.remove(version_file)
            if os.path.exists(content_file):
                os.remove(content_file)
            
            deleted_count += 1
        
        # 更新版本历史
        self.version_history[relative_path] = history[:keep_last]
        self._save_history()
        
        return deleted_count
    
    def _save_history(self) -> None:
        """保存版本历史"""
        history_file = os.path.join(self.version_dir, "history.json")
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.version_history, f, ensure_ascii=False, indent=2)
