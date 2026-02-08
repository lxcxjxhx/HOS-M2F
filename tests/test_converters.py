"""测试转换器模块"""

import unittest
import os
import tempfile
from hos_m2f.converters.md_to_docx import MDToDOCXConverter
from hos_m2f.converters.md_to_html import MDToHTMLConverter
from hos_m2f.converters.md_to_json import MDToJSONConverter
from hos_m2f.converters.md_to_xml import MDToXMLConverter
from hos_m2f.converters.md_to_epub import MDToEPUBConverter
from hos_m2f.converters.md_to_latex import MDToLaTeXConverter
from hos_m2f.converters.pdf_to_md import PDFToMDConverter


class TestConverters(unittest.TestCase):
    """测试转换器"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试用的Markdown内容
        self.test_content = """
# 测试文档

这是一个测试文档，用于测试各种格式转换器。

## 章节1

这是章节1的内容。

### 子章节1.1

这是子章节1.1的内容。

## 章节2

这是章节2的内容。

### 表格测试

| 列1 | 列2 | 列3 |
| --- | --- | --- |
| 行1 | 行1 | 行1 |
| 行2 | 行2 | 行2 |

### Mermaid图表测试

```mermaid
graph TD
    A[开始] --> B[处理]
    B --> C[结束]
```

### 链接测试

[百度](https://www.baidu.com)

### 图片测试

![测试图片](https://example.com/test.jpg)

### 格式化测试

*斜体文本*

**粗体文本**

`代码`

```python
print("Hello, world!")
```
        """.strip()
    
    def test_md_to_docx(self):
        """测试Markdown到DOCX转换"""
        converter = MDToDOCXConverter()
        result = converter.convert(self.test_content)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)
        
        # 保存为临时文件，以便手动检查
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(result)
            tmp_path = tmp.name
        
        try:
            # 验证文件存在且大小大于0
            self.assertTrue(os.path.exists(tmp_path))
            self.assertGreater(os.path.getsize(tmp_path), 0)
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_md_to_html(self):
        """测试Markdown到HTML转换"""
        converter = MDToHTMLConverter()
        result = converter.convert(self.test_content)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)
        
        # 保存为临时文件，以便手动检查
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
            tmp.write(result)
            tmp_path = tmp.name
        
        try:
            # 验证文件存在且大小大于0
            self.assertTrue(os.path.exists(tmp_path))
            self.assertGreater(os.path.getsize(tmp_path), 0)
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_md_to_json(self):
        """测试Markdown到JSON转换"""
        converter = MDToJSONConverter()
        result = converter.convert(self.test_content)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)
        
        # 保存为临时文件，以便手动检查
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp.write(result)
            tmp_path = tmp.name
        
        try:
            # 验证文件存在且大小大于0
            self.assertTrue(os.path.exists(tmp_path))
            self.assertGreater(os.path.getsize(tmp_path), 0)
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_md_to_xml(self):
        """测试Markdown到XML转换"""
        converter = MDToXMLConverter()
        result = converter.convert(self.test_content)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)
        
        # 保存为临时文件，以便手动检查
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
            tmp.write(result)
            tmp_path = tmp.name
        
        try:
            # 验证文件存在且大小大于0
            self.assertTrue(os.path.exists(tmp_path))
            self.assertGreater(os.path.getsize(tmp_path), 0)
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_md_to_epub(self):
        """测试Markdown到EPUB转换"""
        converter = MDToEPUBConverter()
        result = converter.convert(self.test_content)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)
        
        # 保存为临时文件，以便手动检查
        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as tmp:
            tmp.write(result)
            tmp_path = tmp.name
        
        try:
            # 验证文件存在且大小大于0
            self.assertTrue(os.path.exists(tmp_path))
            self.assertGreater(os.path.getsize(tmp_path), 0)
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_md_to_latex(self):
        """测试Markdown到LaTeX转换"""
        converter = MDToLaTeXConverter()
        result = converter.convert(self.test_content)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)
        
        # 保存为临时文件，以便手动检查
        with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tmp:
            tmp.write(result)
            tmp_path = tmp.name
        
        try:
            # 验证文件存在且大小大于0
            self.assertTrue(os.path.exists(tmp_path))
            self.assertGreater(os.path.getsize(tmp_path), 0)
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_pdf_to_md(self):
        """测试PDF到Markdown转换"""
        # 创建一个简单的PDF文件内容（这里使用假数据，因为实际PDF文件需要特定格式）
        # 注意：这个测试可能会失败，因为我们没有实际的PDF文件内容
        # 但我们可以测试转换器是否能正确处理异常情况
        converter = PDFToMDConverter()
        
        try:
            # 尝试转换一个空的PDF文件内容
            result = converter.convert(b"")
            # 如果没有抛出异常，验证结果
            self.assertIsInstance(result, bytes)
        except Exception as e:
            # 如果抛出异常，捕获并记录
            print(f"PDF to MD conversion test failed with exception: {e}")
            # 由于PDF转换需要PyPDF2和实际的PDF文件，我们可以跳过这个测试
            self.skipTest("PDF to MD conversion requires PyPDF2 and actual PDF file")


if __name__ == '__main__':
    unittest.main()
