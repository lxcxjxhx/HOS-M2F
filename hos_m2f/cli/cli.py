"""CLI命令体系模块"""

import argparse
import json
import sys
from typing import Dict, Any, Optional
from hos_m2f.engine.engine import Engine
from hos_m2f.ide.preview_server import PreviewServer


class CLI:
    """命令行接口"""
    
    def __init__(self):
        self.engine = Engine()
        self.parser = argparse.ArgumentParser(
            prog='hos-m2f',
            description='HOS-M2F v1.0 - Content Compiler Engine for AI Writing and Professional Document Production',
            epilog='For more information, visit the project documentation.'
        )
        self.subparsers = self.parser.add_subparsers(dest='command', help='Available commands')
        self._setup_commands()
    
    def _setup_commands(self):
        """设置命令"""
        # build命令
        build_parser = self.subparsers.add_parser('build', help='Build document from Markdown')
        build_parser.add_argument('input', help='Input Markdown file')
        build_parser.add_argument('output', help='Output file path')
        build_parser.add_argument('--mode', default='paper', help='Document mode')
        build_parser.add_argument('--format', choices=['epub', 'pdf', 'docx', 'json', 'html', 'xml', 'xlsx'], default='epub', help='Output format')
        build_parser.add_argument('--options', type=str, default='{}', help='Additional options as JSON string')
        
        # check命令
        check_parser = self.subparsers.add_parser('check', help='Check document structure and compliance')
        check_parser.add_argument('input', help='Input Markdown file')
        check_parser.add_argument('--mode', default='paper', help='Document mode')
        check_parser.add_argument('--options', type=str, default='{}', help='Additional options as JSON string')
        
        # parse命令
        parse_parser = self.subparsers.add_parser('parse', help='Parse Markdown content and output structured data')
        parse_parser.add_argument('input', help='Input Markdown file')
        parse_parser.add_argument('--mode', default='paper', help='Document mode')
        parse_parser.add_argument('--output', help='Output JSON file (default: stdout)')
        parse_parser.add_argument('--options', type=str, default='{}', help='Additional options as JSON string')
        
        # convert命令
        convert_parser = self.subparsers.add_parser('convert', help='Convert between different formats')
        convert_parser.add_argument('input', help='Input file')
        convert_parser.add_argument('output', help='Output file path')
        convert_parser.add_argument('--from', dest='from_format', required=True, choices=['md', 'markdown', 'docx', 'json', 'epub', 'html', 'xml', 'pdf', 'xlsx'], help='Input format')
        convert_parser.add_argument('--to', dest='to_format', required=True, choices=['md', 'markdown', 'docx', 'json', 'epub', 'html', 'xml', 'pdf', 'xlsx'], help='Output format')
        convert_parser.add_argument('--options', type=str, default='{}', help='Additional options as JSON string')
        
        # preview命令
        preview_parser = self.subparsers.add_parser('preview', help='Start preview server')
        preview_parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
        
        # info命令
        info_parser = self.subparsers.add_parser('info', help='Show information about supported modes and formats')
        info_parser.add_argument('--detail', action='store_true', help='Show detailed information')
        
        # validate命令
        validate_parser = self.subparsers.add_parser('validate', help='Validate options for a specific mode')
        validate_parser.add_argument('--mode', required=True, help='Document mode')
        validate_parser.add_argument('--options', type=str, required=True, help='Options to validate as JSON string')
        
        # batch命令
        batch_parser = self.subparsers.add_parser('batch', help='Batch process directory')
        batch_parser.add_argument('input', help='Input directory')
        batch_parser.add_argument('--format', choices=['epub', 'pdf', 'docx', 'json', 'html', 'xml', 'xlsx'], default='epub', help='Output format')
        batch_parser.add_argument('--options', type=str, default='{}', help='Additional options as JSON string')
        batch_parser.add_argument('--workers', type=int, default=4, help='Number of parallel workers')
        
        # quality命令
        quality_parser = self.subparsers.add_parser('quality', help='Analyze document quality')
        quality_parser.add_argument('input', help='Input file or directory')
        quality_parser.add_argument('--output', help='Output report file (default: logs/report.json)')
    
    def run(self, args=None):
        """运行命令
        
        Args:
            args: 命令行参数
            
        Returns:
            int: 退出码
        """
        if args is None:
            args = sys.argv[1:]
        
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 1
        
        try:
            if parsed_args.command == 'build':
                return self._run_build(parsed_args)
            elif parsed_args.command == 'check':
                return self._run_check(parsed_args)
            elif parsed_args.command == 'parse':
                return self._run_parse(parsed_args)
            elif parsed_args.command == 'convert':
                return self._run_convert(parsed_args)
            elif parsed_args.command == 'preview':
                return self._run_preview(parsed_args)
            elif parsed_args.command == 'info':
                return self._run_info(parsed_args)
            elif parsed_args.command == 'validate':
                return self._run_validate(parsed_args)
            elif parsed_args.command == 'batch':
                return self._run_batch(parsed_args)
            elif parsed_args.command == 'quality':
                return self._run_quality(parsed_args)
            else:
                self.parser.print_help()
                return 1
        except Exception as e:
            print(f'Error: {e}', file=sys.stderr)
            return 1
    
    def _run_build(self, args):
        """运行build命令"""
        # 读取输入文件
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析选项
        options = json.loads(args.options)
        
        # 构建文档
        result = self.engine.build(content, args.mode, args.format, options)
        
        # 写入输出文件
        with open(args.output, 'wb') as f:
            f.write(result.binary)
        
        print(f'Successfully built {args.output}')
        print(f'Output format: {result.output_format}')
        if result.metadata:
            print('Metadata:', json.dumps(result.metadata, ensure_ascii=False, indent=2))
        
        return 0
    
    def _run_check(self, args):
        """运行check命令"""
        # 读取输入文件
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析选项
        options = json.loads(args.options)
        
        # 检查文档
        result = self.engine.check(content, args.mode, options)
        
        # 输出结果
        print('Check result:')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 检查是否有问题
        if 'compliance' in result and not result['compliance'].get('compliant', True):
            print('\nIssues found:', file=sys.stderr)
            for issue in result['compliance'].get('issues', []):
                print(f'  - {issue}', file=sys.stderr)
            return 1
        
        print('\nNo issues found!')
        return 0
    
    def _run_parse(self, args):
        """运行parse命令"""
        # 读取输入文件
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析选项
        options = json.loads(args.options)
        
        # 根据模式选择解析器
        if args.mode == 'book':
            from hos_m2f.structure.book_parser import BookParser
            parser = BookParser()
        elif args.mode == 'patent':
            from hos_m2f.structure.patent_parser import PatentParser
            parser = PatentParser()
        elif args.mode == 'sop':
            from hos_m2f.structure.sop_parser import SOPParser
            parser = SOPParser()
        else:
            from hos_m2f.structure.semantic_parser import SemanticParser
            parser = SemanticParser()
        
        # 解析内容
        result = parser.parse(content, options)
        
        # 输出结果
        output_data = json.dumps(result, ensure_ascii=False, indent=2)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_data)
            print(f'Successfully parsed to {args.output}')
        else:
            print(output_data)
        
        return 0
    
    def _run_preview(self, args):
        """运行preview命令"""
        server = PreviewServer(port=args.port)
        result = server.start()
        
        if result['success']:
            print(f'Preview server started on port {args.port}')
            print(f'Access at: http://localhost:{args.port}')
            print('Press Ctrl+C to stop the server')
            
            # 保持运行
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print('\nStopping server...')
                server.stop()
                print('Server stopped')
        else:
            print(f'Failed to start server: {result["error"]}', file=sys.stderr)
            return 1
        
        return 0
    
    def _run_info(self, args):
        """运行info命令"""
        print('HOS-M2F v1.0 - Content Compiler Engine')
        print('=====================================')
        
        # 显示支持的模式
        print('\nSupported modes:')
        modes = self.engine.get_supported_modes()
        for mode, description in modes.items():
            print(f'  - {mode}: {description}')
        
        # 显示支持的格式
        print('\nSupported output formats:')
        formats = self.engine.get_supported_formats()
        for fmt, description in formats.items():
            print(f'  - {fmt}: {description}')
        
        if args.detail:
            print('\nDetailed information:')
            print('\nBook mode:')
            print('  Description: Supports chapter structure recognition, TOC generation, metadata packaging, cover recognition')
            print('  Output formats: epub, pdf, docx, json, xlsx')
            
            print('\nPatent mode:')
            print('  Description: Supports automatic claim numbering, patent paragraph indentation, figure numbering')
            print('  Output formats: pdf, docx, json, xlsx')
            
            print('\nSOP mode:')
            print('  Description: Supports step numbering, checklist tabularization, risk level identification')
            print('  Output formats: pdf, docx, json, xlsx')
            
            print('\nPaper mode:')
            print('  Description: Supports technical documents and paper formatting')
            print('  Output formats: pdf, docx, json, xlsx')
        
        return 0
    
    def _run_validate(self, args):
        """运行validate命令"""
        # 解析选项
        options = json.loads(args.options)
        
        # 验证选项
        from hos_m2f.ide.api import IDEAPI
        api = IDEAPI()
        result = api.validate_options(args.mode, options)
        
        # 输出结果
        print('Validation result:')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if not result['valid']:
            print('\nValidation failed:', file=sys.stderr)
            for error in result['errors']:
                print(f'  - {error}', file=sys.stderr)
            return 1
        
        print('\nValidation passed!')
        return 0
    
    def _run_batch(self, args):
        """运行batch命令"""
        # 解析选项
        options = json.loads(args.options)
        
        # 执行批量处理
        from hos_m2f.batch.batch_processor import BatchProcessor
        processor = BatchProcessor(max_workers=args.workers)
        result = processor.process_directory(args.input, args.format, options)
        
        # 输出结果
        print('Batch processing completed!')
        print(f'Processed: {result.get("processed", 0)} files')
        print(f'Success: {result.get("success_count", 0)}')
        print(f'Errors: {result.get("error_count", 0)}')
        
        if result.get("error_count", 0) > 0:
            print('\nErrors:')
            for item in result.get("results", []):
                if not item.get("success", False):
                    print(f'  - {item.get("input_path", "")}: {item.get("error", "Unknown error")}')
            return 1
        
        return 0
    
    def _run_quality(self, args):
        """运行quality命令"""
        # 执行质量分析
        from hos_m2f.quality.quality_control import QualityControl
        qc = QualityControl()
        
        # 检查输入是文件还是目录
        if os.path.isdir(args.input):
            result = qc.batch_analyze(args.input)
            print('Batch quality analysis completed!')
            print(f'Analyzed: {result.get("statistics", {}).get("total_files", 0)} files')
            print(f'Total issues: {result.get("statistics", {}).get("total_issues", 0)}')
        else:
            result = qc.analyze_document(args.input)
            print('Quality analysis completed!')
            print(f'File: {result.get("file", "")}')
            print(f'Total issues: {result.get("statistics", {}).get("total_issues", 0)}')
            
            if result.get("issues", []):
                print('\nIssues:')
                for issue in result.get("issues", []):
                    print(f'  - [{issue.get("severity", "info")}] {issue.get("type", "")}: {issue.get("message", "")}')
        
        return 0
    
    def _run_convert(self, args):
        """运行convert命令"""
        # 解析选项
        options = json.loads(args.options)
        
        # 执行转换
        result = self.engine.convert(args.input, args.output, args.from_format, args.to_format, options)
        
        # 输出结果
        print(f'Successfully converted {args.input} to {args.output}')
        print(f'From format: {args.from_format}')
        print(f'To format: {args.to_format}')
        if result['metadata']:
            print('Metadata:', json.dumps(result['metadata'], ensure_ascii=False, indent=2))
        
        return 0


def main(args=None):
    """CLI命令入口点"""
    cli = CLI()
    sys.exit(cli.run(args))

# 命令行入口
if __name__ == '__main__':
    main()
