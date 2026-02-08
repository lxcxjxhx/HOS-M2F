"""批量处理模块"""

import os
import concurrent.futures
import logging
import time
from typing import List, Dict, Any, Optional, Callable
from hos_m2f.engine.engine import Engine


class BatchProcessor:
    """批量处理器
    
    支持目录级批量转换
    """
    
    def __init__(self, max_workers: int = 4, log_level: int = logging.INFO):
        """初始化批量处理器
        
        Args:
            max_workers: 最大并行工作数
            log_level: 日志级别
        """
        self.engine = Engine()
        self.max_workers = max_workers
        self.output_dirs = {
            "html": "build/html",
            "docx": "build/docx",
            "pdf": "build/pdf",
            "json": "build/json",
            "epub": "build/epub",
            "xml": "build/xml",
            "xlsx": "build/xlsx"
        }
        
        # 配置日志
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def process_directory(self, input_dir: str, output_format: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理整个目录
        
        Args:
            input_dir: 输入目录
            output_format: 输出格式
            options: 转换选项
                - output_dir: 自定义输出目录
                - file_patterns: 文件过滤模式列表
                - exclude_patterns: 排除文件模式列表
                - retry_count: 错误重试次数
                - callback: 处理完成后的回调函数
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        options = options or {}
        
        # 检查输入目录是否存在
        if not os.path.exists(input_dir):
            raise ValueError(f"Input directory {input_dir} does not exist")
        
        # 获取选项
        custom_output_dir = options.get('output_dir')
        file_patterns = options.get('file_patterns', [])
        exclude_patterns = options.get('exclude_patterns', [])
        retry_count = options.get('retry_count', 0)
        callback = options.get('callback')
        
        # 创建输出目录
        output_dir = custom_output_dir or self.output_dirs.get(output_format, f"build/{output_format}")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 收集输入文件
        input_files = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                if self._is_supported_file(file):
                    # 应用文件过滤
                    if not self._should_process_file(file, file_patterns, exclude_patterns):
                        continue
                    
                    input_path = os.path.join(root, file)
                    # 生成输出路径
                    relative_path = os.path.relpath(input_path, input_dir)
                    output_filename = os.path.splitext(relative_path)[0] + f".{output_format}"
                    output_path = os.path.join(output_dir, output_filename)
                    # 创建输出目录
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    input_files.append((input_path, output_path))
        
        if not input_files:
            self.logger.warning("No supported files found")
            return {"success": False, "message": "No supported files found", "processed": 0}
        
        self.logger.info(f"Found {len(input_files)} files to process")
        
        # 批量处理
        results = []
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交任务
            future_to_task = {}
            for input_path, output_path in input_files:
                input_format = self._detect_format(input_path)
                future = executor.submit(
                    self._process_file,
                    input_path,
                    output_path,
                    input_format,
                    output_format,
                    options,
                    retry_count
                )
                future_to_task[future] = (input_path, output_path)
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_task):
                input_path, output_path = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.logger.info(f"Processed: {input_path} -> {output_path}")
                except Exception as e:
                    self.logger.error(f"Error processing {input_path}: {e}")
                    results.append({
                        "success": False,
                        "input_path": input_path,
                        "output_path": output_path,
                        "error": str(e)
                    })
        
        # 执行回调
        if callback and callable(callback):
            try:
                callback(results)
            except Exception as e:
                self.logger.error(f"Error executing callback: {e}")
        
        # 统计结果
        success_count = sum(1 for r in results if r.get("success", False))
        error_count = len(results) - success_count
        elapsed_time = time.time() - start_time
        
        self.logger.info(f"Batch processing completed in {elapsed_time:.2f} seconds")
        self.logger.info(f"Success: {success_count}, Errors: {error_count}")
        
        return {
            "success": error_count == 0,
            "processed": len(results),
            "success_count": success_count,
            "error_count": error_count,
            "elapsed_time": elapsed_time,
            "results": results
        }
    
    def _is_supported_file(self, filename: str) -> bool:
        """检查文件是否支持
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否支持
        """
        supported_extensions = {
            '.md', '.markdown', '.html', '.htm', '.json',
            '.docx', '.epub', '.pdf', '.xml', '.xlsx'
        }
        ext = os.path.splitext(filename)[1].lower()
        return ext in supported_extensions
    
    def _detect_format(self, file_path: str) -> str:
        """检测文件格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 格式名称
        """
        ext = os.path.splitext(file_path)[1].lower()
        format_map = {
            '.md': 'md',
            '.markdown': 'md',
            '.html': 'html',
            '.htm': 'html',
            '.json': 'json',
            '.docx': 'docx',
            '.epub': 'epub',
            '.pdf': 'pdf',
            '.xml': 'xml',
            '.xlsx': 'xlsx'
        }
        return format_map.get(ext, 'md')
    
    def _should_process_file(self, filename: str, file_patterns: List[str], exclude_patterns: List[str]) -> bool:
        """检查文件是否应该被处理
        
        Args:
            filename: 文件名
            file_patterns: 文件过滤模式列表
            exclude_patterns: 排除文件模式列表
            
        Returns:
            bool: 是否应该处理
        """
        import fnmatch
        
        # 检查排除模式
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return False
        
        # 检查包含模式
        if file_patterns:
            for pattern in file_patterns:
                if fnmatch.fnmatch(filename, pattern):
                    return True
            return False
        
        # 默认处理所有支持的文件
        return True
    
    def _process_file(self, input_path: str, output_path: str, input_format: str, output_format: str, options: Dict[str, Any], retry_count: int = 0) -> Dict[str, Any]:
        """处理单个文件
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            input_format: 输入格式
            output_format: 输出格式
            options: 转换选项
            retry_count: 错误重试次数
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        attempts = 0
        while attempts <= retry_count:
            try:
                result = self.engine.convert(input_path, output_path, input_format, output_format, options)
                return {
                    "success": True,
                    "input_path": input_path,
                    "output_path": output_path,
                    "result": result,
                    "attempts": attempts + 1
                }
            except Exception as e:
                attempts += 1
                if attempts > retry_count:
                    return {
                        "success": False,
                        "input_path": input_path,
                        "output_path": output_path,
                        "error": str(e),
                        "attempts": attempts
                    }
                self.logger.warning(f"Attempt {attempts} failed for {input_path}: {e}. Retrying...")
                time.sleep(1)  # 等待1秒后重试
