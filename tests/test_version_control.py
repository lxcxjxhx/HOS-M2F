"""测试版本控制模块"""

import unittest
import tempfile
import os
from hos_m2f.version.version_control import VersionControl


class TestVersionControl(unittest.TestCase):
    """测试版本控制功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.version_control = VersionControl()
        
        # 创建测试文件
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp:
            tmp.write(b"# Test Document\n\nThis is a test document.")
            self.test_file = tmp.name
    
    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)
        
        # 清理版本控制生成的文件
        version_dir = os.path.join(os.path.dirname(self.test_file), ".versions")
        if os.path.exists(version_dir):
            import shutil
            shutil.rmtree(version_dir)
    
    def test_create_version(self):
        """测试创建版本"""
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        version_info = self.version_control.create_version(
            document_path=self.test_file,
            content=content,
            message="Test version",
            author="Test Author"
        )
        
        self.assertIsInstance(version_info, dict)
        self.assertIn("id", version_info)
        self.assertIn("timestamp", version_info)
        self.assertIn("message", version_info)
        self.assertEqual(version_info["message"], "Test version")
    
    def test_get_version_history(self):
        """测试获取版本历史"""
        # 创建多个版本
        for i in range(3):
            with open(self.test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.version_control.create_version(
                document_path=self.test_file,
                content=content,
                message=f"Test version {i}",
                author="Test Author"
            )
        
        # 获取版本历史
        history = self.version_control.get_version_history(self.test_file)
        
        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 3)
        
        # 验证版本顺序（最新的在前）
        for i in range(len(history) - 1):
            self.assertGreater(
                history[i]["timestamp"],
                history[i + 1]["timestamp"]
            )
    
    def test_revert_to_version(self):
        """测试回滚到之前的版本"""
        # 创建初始版本
        initial_content = "# Initial Content"
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        
        version1 = self.version_control.create_version(
            document_path=self.test_file,
            content=initial_content,
            message="Initial version"
        )
        
        # 修改文件内容
        modified_content = "# Modified Content"
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        version2 = self.version_control.create_version(
            document_path=self.test_file,
            content=modified_content,
            message="Modified version"
        )
        
        # 回滚到版本1
        success = self.version_control.revert_to_version(
            self.test_file, version1["id"]
        )
        
        self.assertTrue(success)
        
        # 验证文件内容已回滚
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertEqual(content, initial_content)
    
    def test_compare_versions(self):
        """测试比较版本"""
        # 创建初始版本
        initial_content = "# Initial Content\n\nLine 1"
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        
        version1 = self.version_control.create_version(
            document_path=self.test_file,
            content=initial_content,
            message="Initial version"
        )
        
        # 修改文件内容
        modified_content = "# Modified Content\n\nLine 1\nLine 2"
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        version2 = self.version_control.create_version(
            document_path=self.test_file,
            content=modified_content,
            message="Modified version"
        )
        
        # 比较版本
        diff_result = self.version_control.compare_versions(
            version1["id"], version2["id"]
        )
        
        self.assertIsInstance(diff_result, dict)
        self.assertIn("diff", diff_result)
        self.assertIsInstance(diff_result["diff"], list)
    
    def test_cleanup_versions(self):
        """测试清理版本"""
        # 创建多个版本
        for i in range(5):
            with open(self.test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.version_control.create_version(
                document_path=self.test_file,
                content=content,
                message=f"Test version {i}"
            )
        
        # 清理版本，保留2个
        deleted_count = self.version_control.cleanup_versions(
            self.test_file, keep_last=2
        )
        
        self.assertEqual(deleted_count, 3)
        
        # 验证只保留了2个版本
        history = self.version_control.get_version_history(self.test_file)
        self.assertEqual(len(history), 2)


if __name__ == '__main__':
    unittest.main()
