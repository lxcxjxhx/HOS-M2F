"""质量控制模块"""

import os
import json
import re
import datetime
from typing import Dict, Any, List, Optional, Callable
from hos_m2f.parsers.html_parser import HTMLParser
from hos_m2f.parsers.md_parser import MDParser


class QualityControl:
    """质量控制器
    
    用于检测文档中的问题并生成质量报告
    """
    
    def __init__(self, custom_rules: Optional[List[Dict[str, Any]]] = None):
        """初始化质量控制器
        
        Args:
            custom_rules: 自定义质量检测规则
        """
        self.html_parser = HTMLParser()
        self.md_parser = MDParser()
        self.logs_dir = "logs"
        self.custom_rules = custom_rules or []
        
        # 创建日志目录
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir, exist_ok=True)
        
        # 定义问题严重程度
        self.severity_levels = {
            "error": 3,
            "warning": 2,
            "info": 1
        }
        
        # 定义问题类型描述
        self.issue_types = {
            "mermaid": "Mermaid图表问题",
            "image": "图片问题",
            "table": "表格问题",
            "heading": "标题问题",
            "code_block": "代码块问题",
            "link": "链接问题",
            "spelling": "拼写问题",
            "format": "格式问题",
            "content": "内容问题"
        }
    
    def analyze_document(self, input_path: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """分析文档质量
        
        Args:
            input_path: 输入文件路径
            options: 分析选项
                - include_suggestions: 是否包含修复建议
                - custom_rules: 自定义质量检测规则
                - severity_threshold: 严重程度阈值
            
        Returns:
            Dict[str, Any]: 质量分析结果
        """
        options = options or {}
        
        # 获取选项
        include_suggestions = options.get('include_suggestions', True)
        custom_rules = options.get('custom_rules', self.custom_rules)
        severity_threshold = options.get('severity_threshold', 1)
        
        # 检测文件类型
        ext = os.path.splitext(input_path)[1].lower()
        
        if ext in ['.md', '.markdown']:
            return self._analyze_markdown(input_path, include_suggestions, custom_rules, severity_threshold)
        elif ext in ['.html', '.htm']:
            return self._analyze_html(input_path, include_suggestions, custom_rules, severity_threshold)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _analyze_markdown(self, input_path: str, include_suggestions: bool = True, custom_rules: List[Dict[str, Any]] = None, severity_threshold: int = 1) -> Dict[str, Any]:
        """分析Markdown文档
        
        Args:
            input_path: Markdown文件路径
            include_suggestions: 是否包含修复建议
            custom_rules: 自定义质量检测规则
            severity_threshold: 严重程度阈值
            
        Returns:
            Dict[str, Any]: 质量分析结果
        """
        # 读取文件内容
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析文档
        model = self.md_parser.parse(content)
        json_content = model.get_json()
        html_content = model.get_html()
        
        # 检测问题
        issues = []
        
        # 检测Mermaid未转换
        issues.extend(self._detect_mermaid_issues(content))
        
        # 检测图片缺失
        issues.extend(self._detect_image_issues(json_content.get('assets', [])))
        
        # 检测表格异常
        issues.extend(self._detect_table_issues(content))
        
        # 检测标题跳级
        issues.extend(self._detect_heading_issues(content))
        
        # 检测空代码块
        issues.extend(self._detect_empty_code_blocks(content))
        
        # 检测链接问题
        issues.extend(self._detect_link_issues(content))
        
        # 应用自定义规则
        if custom_rules:
            issues.extend(self._apply_custom_rules(content, custom_rules))
        
        # 根据严重程度阈值过滤问题
        filtered_issues = [issue for issue in issues if self.severity_levels.get(issue.get('severity'), 1) >= severity_threshold]
        
        # 为问题添加修复建议
        if include_suggestions:
            for issue in filtered_issues:
                issue['suggestion'] = self._get_suggestion(issue)
        
        # 计算质量评分
        quality_score = self._calculate_quality_score(filtered_issues, content)
        
        # 生成报告
        report = {
            "file": input_path,
            "format": "markdown",
            "issues": filtered_issues,
            "statistics": {
                "total_issues": len(filtered_issues),
                "assets_count": len(json_content.get('assets', [])),
                "blocks_count": len(json_content.get('blocks', [])),
                "structure_count": len(json_content.get('structure', [])),
                "quality_score": quality_score,
                "issue_distribution": self._get_issue_distribution(filtered_issues)
            },
            "timestamp": self._get_timestamp()
        }
        
        # 保存报告
        self._save_report(report)
        
        return report
    
    def _analyze_html(self, input_path: str, include_suggestions: bool = True, custom_rules: List[Dict[str, Any]] = None, severity_threshold: int = 1) -> Dict[str, Any]:
        """分析HTML文档
        
        Args:
            input_path: HTML文件路径
            include_suggestions: 是否包含修复建议
            custom_rules: 自定义质量检测规则
            severity_threshold: 严重程度阈值
            
        Returns:
            Dict[str, Any]: 质量分析结果
        """
        # 读取文件内容
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析文档
        model = self.html_parser.parse(content)
        json_content = model.get_json()
        html_content = model.get_html()
        
        # 检测问题
        issues = []
        
        # 检测Mermaid未转换
        issues.extend(self._detect_mermaid_issues(html_content))
        
        # 检测图片缺失
        issues.extend(self._detect_image_issues(json_content.get('assets', [])))
        
        # 检测表格异常
        issues.extend(self._detect_table_issues(html_content))
        
        # 检测标题跳级
        issues.extend(self._detect_heading_issues(html_content))
        
        # 检测空代码块
        issues.extend(self._detect_empty_code_blocks(html_content))
        
        # 检测链接问题
        issues.extend(self._detect_link_issues(html_content))
        
        # 应用自定义规则
        if custom_rules:
            issues.extend(self._apply_custom_rules(html_content, custom_rules))
        
        # 根据严重程度阈值过滤问题
        filtered_issues = [issue for issue in issues if self.severity_levels.get(issue.get('severity'), 1) >= severity_threshold]
        
        # 为问题添加修复建议
        if include_suggestions:
            for issue in filtered_issues:
                issue['suggestion'] = self._get_suggestion(issue)
        
        # 计算质量评分
        quality_score = self._calculate_quality_score(filtered_issues, content)
        
        # 生成报告
        report = {
            "file": input_path,
            "format": "html",
            "issues": filtered_issues,
            "statistics": {
                "total_issues": len(filtered_issues),
                "assets_count": len(json_content.get('assets', [])),
                "blocks_count": len(json_content.get('blocks', [])),
                "structure_count": len(json_content.get('structure', [])),
                "quality_score": quality_score,
                "issue_distribution": self._get_issue_distribution(filtered_issues)
            },
            "timestamp": self._get_timestamp()
        }
        
        # 保存报告
        self._save_report(report)
        
        return report
    
    def _detect_mermaid_issues(self, content: str) -> List[Dict[str, Any]]:
        """检测Mermaid未转换问题
        
        Args:
            content: 文档内容
            
        Returns:
            List[Dict[str, Any]]: 问题列表
        """
        issues = []
        
        # 检测Mermaid代码块
        import re
        mermaid_pattern = re.compile(r'```mermaid\n((?:.|\n)*?)```', re.MULTILINE)
        matches = mermaid_pattern.findall(content)
        
        for i, match in enumerate(matches):
            if match.strip():
                issues.append({
                    "type": "mermaid",
                    "severity": "info",
                    "message": f"Found Mermaid chart #{i+1}",
                    "line": self._find_line_number(content, match)
                })
        
        return issues
    
    def _detect_image_issues(self, assets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检测图片缺失问题
        
        Args:
            assets: 资源列表
            
        Returns:
            List[Dict[str, Any]]: 问题列表
        """
        issues = []
        
        for i, asset in enumerate(assets):
            if asset['type'] == 'image':
                # 检查图片URL是否有效
                if not asset['src']:
                    issues.append({
                        "type": "image",
                        "severity": "error",
                        "message": f"Missing image source for asset #{asset['id']}",
                        "asset_id": asset['id']
                    })
            
        return issues
    
    def _detect_table_issues(self, content: str) -> List[Dict[str, Any]]:
        """检测表格异常问题
        
        Args:
            content: 文档内容
            
        Returns:
            List[Dict[str, Any]]: 问题列表
        """
        issues = []
        
        # 检测Markdown表格
        import re
        table_pattern = re.compile(r'\|.*\|\n\|.*\|', re.MULTILINE)
        matches = table_pattern.findall(content)
        
        for i, match in enumerate(matches):
            # 检查表格是否有表头
            lines = match.split('\n')
            if len(lines) < 2:
                issues.append({
                    "type": "table",
                    "severity": "warning",
                    "message": f"Table #{i+1} may be malformed",
                    "line": self._find_line_number(content, match)
                })
        
        return issues
    
    def _detect_heading_issues(self, content: str) -> List[Dict[str, Any]]:
        """检测标题跳级问题
        
        Args:
            content: 文档内容
            
        Returns:
            List[Dict[str, Any]]: 问题列表
        """
        issues = []
        
        # 检测标题
        import re
        heading_pattern = re.compile(r'^(#{1,6})\s+(.*)$', re.MULTILINE)
        matches = heading_pattern.findall(content)
        
        # 检查标题级别是否连续
        prev_level = 0
        for i, (hashes, title) in enumerate(matches):
            current_level = len(hashes)
            
            if prev_level > 0 and current_level > prev_level + 1:
                issues.append({
                    "type": "heading",
                    "severity": "warning",
                    "message": f"Heading level jump detected: level {prev_level} to {current_level}",
                    "line": self._find_line_number(content, hashes + ' ' + title)
                })
            
            prev_level = current_level
        
        return issues
    
    def _detect_empty_code_blocks(self, content: str) -> List[Dict[str, Any]]:
        """检测空代码块
        
        Args:
            content: 文档内容
            
        Returns:
            List[Dict[str, Any]]: 问题列表
        """
        issues = []
        
        # 检测代码块
        import re
        code_pattern = re.compile(r'```(\w*)\n((?:.|\n)*?)```', re.MULTILINE)
        matches = code_pattern.findall(content)
        
        for i, (language, code) in enumerate(matches):
            if not code.strip():
                issues.append({
                    "type": "code_block",
                    "severity": "info",
                    "message": f"Empty code block detected",
                    "line": self._find_line_number(content, f"```(\w*)\n{code}```")
                })
        
        return issues
    
    def _find_line_number(self, content: str, search_text: str) -> int:
        """查找文本在文件中的行号
        
        Args:
            content: 文件内容
            search_text: 搜索文本
            
        Returns:
            int: 行号
        """
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if search_text in line:
                return i
        return 0
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳
        
        Returns:
            str: 时间戳
        """
        import datetime
        return datetime.datetime.now().isoformat()
    
    def _save_report(self, report: Dict[str, Any]) -> None:
        """保存质量报告
        
        Args:
            report: 质量报告
        """
        report_path = os.path.join(self.logs_dir, "report.json")
        
        # 读取现有报告
        existing_reports = []
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                existing_reports = json.load(f)
        
        # 添加新报告
        existing_reports.append(report)
        
        # 保存报告
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(existing_reports, f, ensure_ascii=False, indent=2)
    
    def _detect_link_issues(self, content: str) -> List[Dict[str, Any]]:
        """检测链接问题
        
        Args:
            content: 文档内容
            
        Returns:
            List[Dict[str, Any]]: 问题列表
        """
        issues = []
        
        # 检测Markdown链接
        markdown_link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)', re.MULTILINE)
        markdown_matches = markdown_link_pattern.findall(content)
        
        for i, (text, url) in enumerate(markdown_matches):
            if not url or url.strip() == '':
                issues.append({
                    "type": "link",
                    "severity": "error",
                    "message": f"Empty link URL detected",
                    "line": self._find_line_number(content, f"[{text}]({url})")
                })
            elif not text or text.strip() == '':
                issues.append({
                    "type": "link",
                    "severity": "warning",
                    "message": f"Empty link text detected",
                    "line": self._find_line_number(content, f"[{text}]({url})")
                })
        
        # 检测HTML链接
        html_link_pattern = re.compile(r'<a[^>]+href="([^"]*)"[^>]*>(.*?)</a>', re.DOTALL)
        html_matches = html_link_pattern.findall(content)
        
        for i, (href, text) in enumerate(html_matches):
            if not href or href.strip() == '':
                issues.append({
                    "type": "link",
                    "severity": "error",
                    "message": f"Empty link href detected",
                    "line": self._find_line_number(content, f"href=\"{href}\"")
                })
        
        return issues
    
    def _apply_custom_rules(self, content: str, custom_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """应用自定义质量检测规则
        
        Args:
            content: 文档内容
            custom_rules: 自定义规则列表
            
        Returns:
            List[Dict[str, Any]]: 问题列表
        """
        issues = []
        
        for rule in custom_rules:
            pattern = rule.get('pattern')
            issue_type = rule.get('type', 'content')
            severity = rule.get('severity', 'info')
            message = rule.get('message', 'Custom rule violation')
            
            if pattern:
                matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                for i, match in enumerate(matches):
                    issues.append({
                        "type": issue_type,
                        "severity": severity,
                        "message": message,
                        "line": self._find_line_number(content, str(match))
                    })
        
        return issues
    
    def _get_suggestion(self, issue: Dict[str, Any]) -> str:
        """获取问题修复建议
        
        Args:
            issue: 问题信息
            
        Returns:
            str: 修复建议
        """
        suggestions = {
            "mermaid": "确保Mermaid图表代码格式正确，使用```mermaid代码块",
            "image": "添加有效的图片URL，并确保图片可以正常访问",
            "table": "检查表格格式，确保表头和数据行对齐",
            "heading": "保持标题层级连续，避免跳级",
            "code_block": "为代码块添加语言标识，并确保代码内容完整",
            "link": "添加有效的链接URL和描述性链接文本",
            "spelling": "检查并修正拼写错误",
            "format": "保持文档格式一致，遵循Markdown/HTML规范",
            "content": "确保内容完整，逻辑清晰"
        }
        
        return suggestions.get(issue.get('type'), "检查并修复问题")
    
    def _calculate_quality_score(self, issues: List[Dict[str, Any]], content: str) -> int:
        """计算文档质量评分
        
        Args:
            issues: 问题列表
            content: 文档内容
            
        Returns:
            int: 质量评分（0-100）
        """
        # 基础分数
        base_score = 100
        
        # 根据问题严重程度扣分
        for issue in issues:
            severity = issue.get('severity', 'info')
            severity_level = self.severity_levels.get(severity, 1)
            base_score -= severity_level * 2
        
        # 确保分数在0-100之间
        return max(0, min(100, base_score))
    
    def _get_issue_distribution(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """获取问题分布
        
        Args:
            issues: 问题列表
            
        Returns:
            Dict[str, int]: 问题类型分布
        """
        distribution = {}
        
        for issue in issues:
            issue_type = issue.get('type', 'other')
            distribution[issue_type] = distribution.get(issue_type, 0) + 1
        
        return distribution
    
    def batch_analyze(self, input_dir: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """批量分析目录中的文档
        
        Args:
            input_dir: 输入目录
            options: 分析选项
                - include_suggestions: 是否包含修复建议
                - custom_rules: 自定义质量检测规则
                - severity_threshold: 严重程度阈值
            
        Returns:
            Dict[str, Any]: 批量分析结果
        """
        options = options or {}
        
        if not os.path.exists(input_dir):
            raise ValueError(f"Input directory {input_dir} does not exist")
        
        results = []
        total_issues = 0
        total_quality_score = 0
        processed_files = 0
        
        for root, _, files in os.walk(input_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in ['.md', '.markdown', '.html', '.htm']:
                    file_path = os.path.join(root, file)
                    try:
                        report = self.analyze_document(file_path, options)
                        results.append(report)
                        total_issues += len(report['issues'])
                        total_quality_score += report['statistics'].get('quality_score', 0)
                        processed_files += 1
                    except Exception as e:
                        results.append({
                            "file": file_path,
                            "error": str(e),
                            "timestamp": self._get_timestamp()
                        })
        
        # 计算平均质量评分
        average_quality_score = total_quality_score / processed_files if processed_files > 0 else 0
        
        batch_report = {
            "directory": input_dir,
            "results": results,
            "statistics": {
                "total_files": len(results),
                "processed_files": processed_files,
                "total_issues": total_issues,
                "average_quality_score": average_quality_score
            },
            "timestamp": self._get_timestamp()
        }
        
        # 保存批量报告
        batch_report_path = os.path.join(self.logs_dir, "batch_report.json")
        with open(batch_report_path, 'w', encoding='utf-8') as f:
            json.dump(batch_report, f, ensure_ascii=False, indent=2)
        
        return batch_report
