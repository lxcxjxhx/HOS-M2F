from setuptools import setup, find_packages

setup(
    name="hos-m2f",
    version="0.6.6",
    description="HOS-M2F: Markdown to Industry Standard Format Compiler Engine",
    long_description="""HOS-M2F is a powerful compiler engine that converts Markdown files to various industry standard formats.

Key Features:
- Multiple output formats: PDF, DOCX, EPUB, and JSON
- Specialized modes for different document types:
  - Book mode for book-length documents
  - Paper mode for academic papers
  - Patent mode for patent applications
  - SOP (Standard Operating Procedure) mode for technical procedures
- Command-line interface for easy automation
- Semantic parsing for intelligent document structure
- Extensible architecture for custom renderers and modes

Use Cases:
- Convert technical documentation to professional formats
- Generate academic papers from Markdown sources
- Create standardized operating procedures
- Prepare patent applications with proper formatting
- Build eBooks from Markdown content

HOS-M2F simplifies the process of creating professionally formatted documents from plain Markdown, saving time and ensuring consistency across document types.""",
    long_description_content_type="text/markdown",
    author="HOS Team",
    author_email="team@hos-m2f.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "mistune>=2.0.0",
        "pyyaml>=6.0",
        "click>=8.0.0",
        "ebooklib>=0.17.0",
        "weasyprint>=54.0",
        "python-docx>=0.8.11"
    ],
    extras_require={
        "test": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0"
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "isort>=5.0.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "hos=hos_m2f.cli:main",
            "hos-m2f=hos_m2f.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8'
)