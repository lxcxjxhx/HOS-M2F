"""测试LaTeX渲染器和转换器"""

import unittest
import os
import tempfile
from hos_m2f.renderers.latex_renderer import LaTeXRenderer
from hos_m2f.converters.md_to_latex import MDToLaTeXConverter


class TestLaTeX(unittest.TestCase):
    """测试LaTeX渲染器和转换器"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试用的Markdown内容
        self.test_content = """
# 测试文档

## 摘要

这是一个测试文档，用于测试LaTeX渲染功能。

## 引言

这是引言章节的内容。

### 背景

这是背景部分的内容。

## 方法

这是方法章节的内容。

### 实验设计

这是实验设计部分的内容。

## 结果

这是结果章节的内容。

### 数据表格

| 列1 | 列2 | 列3 |
| --- | --- | --- |
| 行1 | 行1 | 行1 |
| 行2 | 行2 | 行2 |

### 代码示例

```python
print("Hello, world!")
```

## 讨论

这是讨论章节的内容。

## 结论

这是结论章节的内容。

## 参考文献

[1] 参考文献1
[2] 参考文献2
        """.strip()
        
        # 创建测试用的结构化内容
        self.structured_content = {
            "metadata": {
                "title": "测试文档",
                "author": "测试作者",
                "date": "2023-01-01",
                "abstract": "这是一个测试文档，用于测试LaTeX渲染功能。",
                "keywords": ["测试", "LaTeX", "渲染"]
            },
            "structure": [
                {"level": 1, "title": "测试文档", "line_number": 1},
                {"level": 2, "title": "摘要", "line_number": 3},
                {"level": 2, "title": "引言", "line_number": 7},
                {"level": 3, "title": "背景", "line_number": 9},
                {"level": 2, "title": "方法", "line_number": 13},
                {"level": 3, "title": "实验设计", "line_number": 15},
                {"level": 2, "title": "结果", "line_number": 19},
                {"level": 3, "title": "数据表格", "line_number": 21},
                {"level": 3, "title": "代码示例", "line_number": 29},
                {"level": 2, "title": "讨论", "line_number": 35},
                {"level": 2, "title": "结论", "line_number": 39},
                {"level": 2, "title": "参考文献", "line_number": 43}
            ],
            "chapters": [
                {"title": "测试文档", "content": "", "level": 1, "start_line": 1, "end_line": 1},
                {"title": "摘要", "content": "这是一个测试文档，用于测试LaTeX渲染功能。", "level": 2, "start_line": 3, "end_line": 5},
                {"title": "引言", "content": "这是引言章节的内容。", "level": 2, "start_line": 7, "end_line": 8},
                {"title": "背景", "content": "这是背景部分的内容。", "level": 3, "start_line": 9, "end_line": 11},
                {"title": "方法", "content": "这是方法章节的内容。", "level": 2, "start_line": 13, "end_line": 14},
                {"title": "实验设计", "content": "这是实验设计部分的内容。", "level": 3, "start_line": 15, "end_line": 17},
                {"title": "结果", "content": "这是结果章节的内容。", "level": 2, "start_line": 19, "end_line": 20},
                {"title": "数据表格", "content": "| 列1 | 列2 | 列3 |\n| --- | --- | --- |\n| 行1 | 行1 | 行1 |\n| 行2 | 行2 | 行2 |", "level": 3, "start_line": 21, "end_line": 28},
                {"title": "代码示例", "content": "```python\nprint(\"Hello, world!\")\n```", "level": 3, "start_line": 29, "end_line": 34},
                {"title": "讨论", "content": "这是讨论章节的内容。", "level": 2, "start_line": 35, "end_line": 37},
                {"title": "结论", "content": "这是结论章节的内容。", "level": 2, "start_line": 39, "end_line": 41},
                {"title": "参考文献", "content": "[1] 参考文献1\n[2] 参考文献2", "level": 2, "start_line": 43, "end_line": 46}
            ],
            "references": [
                {"text": "参考文献1"},
                {"text": "参考文献2"}
            ]
        }
    
    def test_latex_renderer(self):
        """测试LaTeX渲染器"""
        renderer = LaTeXRenderer()
        
        # 测试渲染功能
        latex_content = renderer.render(self.structured_content)
        self.assertIsInstance(latex_content, bytes)
        self.assertGreater(len(latex_content), 0)
        
        # 保存为临时文件，以便手动检查
        with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tmp:
            tmp.write(latex_content)
            tmp_path = tmp.name
        
        try:
            # 验证文件存在且大小大于0
            self.assertTrue(os.path.exists(tmp_path))
            self.assertGreater(os.path.getsize(tmp_path), 0)
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_md_to_latex_converter(self):
        """测试Markdown到LaTeX转换器"""
        converter = MDToLaTeXConverter()
        
        # 测试转换功能
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
    
    def test_latex_with_options(self):
        """测试带选项的LaTeX渲染"""
        renderer = LaTeXRenderer()
        converter = MDToLaTeXConverter()
        
        # 测试带选项的渲染
        options = {
            "document_class": "article",
            "document_options": "a4paper, 12pt",
            "table_of_contents": True
        }
        
        latex_content = renderer.render(self.structured_content, options)
        self.assertIsInstance(latex_content, bytes)
        self.assertGreater(len(latex_content), 0)
        
        # 测试带选项的转换
        result = converter.convert(self.test_content, options)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)


if __name__ == '__main__':
    unittest.main()