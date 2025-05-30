"""
Setup configuration for SEO Audit Toolkit
Author: Youssef Hodaigui - Mindflow Marketing
Website: https://youssefhodaigui.com
"""

import os
import re
from setuptools import setup, find_packages

# Read the version from __init__.py
def get_version():
    with open(os.path.join('python', '__init__.py'), 'r') as f:
        content = f.read()
        version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', content, re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError('Unable to find version string.')

# Read the long description from README.md
def get_long_description():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements from requirements.txt
def get_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read development requirements
def get_dev_requirements():
    with open('requirements-dev.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='seo-audit-toolkit',
    version=get_version(),
    author='Youssef Hodaigui',
    author_email='youssef@mindflowmarketing.com',
    description='Comprehensive technical SEO audit scripts and tools for professionals',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/youssefhodaigui/seo-audit-toolkit',
    project_urls={
        'Bug Tracker': 'https://github.com/youssefhodaigui/seo-audit-toolkit/issues',
        'Documentation': 'https://github.com/youssefhodaigui/seo-audit-toolkit/tree/main/docs',
        'Source Code': 'https://github.com/youssefhodaigui/seo-audit-toolkit',
        'Company': 'https://mindflowmarketing.com',
        'Author Website': 'https://youssefhodaigui.com',
    },
    license='MIT',
    packages=['python'],
    package_dir={'python': 'python'},
    install_requires=get_requirements(),
    extras_require={
        'dev': get_dev_requirements(),
        'all': get_requirements() + get_dev_requirements(),
    },
    entry_points={
        'console_scripts': [
            'seo-audit=python.cli:main',
            'seo-technical-audit=python.technical_audit:main',
            'seo-cwv=python.core_web_vitals:main',
            'seo-schema=python.schema_validator:main',
            'seo-sitemap=python.sitemap_analyzer:main',
            'seo-mobile=python.mobile_checker:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Environment :: Console',
        'Environment :: Web Environment',
    ],
    keywords=[
        'seo',
        'audit',
        'technical-seo',
        'core-web-vitals',
        'schema',
        'structured-data',
        'sitemap',
        'mobile-friendly',
        'page-speed',
        'search-engine-optimization',
        'website-analysis',
        'seo-tools',
        'digital-marketing',
        'web-performance',
        'lighthouse',
        'google-pagespeed',
    ],
    python_requires='>=3.8',
    include_package_data=True,
    zip_safe=False,
    platforms=['any'],
    test_suite='tests',
)
