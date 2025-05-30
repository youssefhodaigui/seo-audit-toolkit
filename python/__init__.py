"""
SEO Audit Toolkit
A comprehensive technical SEO audit library for Python

Author: Youssef Hodaigui
Website: https://youssefhodaigui.com
Company: Mindflow Marketing
"""

__version__ = "1.0.0"
__author__ = "Youssef Hodaigui"
__email__ = "youssef@mindflowmarketing.com"
__license__ = "MIT"

# Import main classes for easy access
from .technical_audit import TechnicalAuditor
from .core_web_vitals import CoreWebVitals
from .schema_validator import SchemaValidator
from .sitemap_analyzer import SitemapAnalyzer
from .mobile_checker import MobileChecker

# Define what's available when using "from seo_audit_toolkit import *"
__all__ = [
    'TechnicalAuditor',
    'CoreWebVitals',
    'SchemaValidator',
    'SitemapAnalyzer',
    'MobileChecker',
]

# Package metadata
PACKAGE_NAME = "seo-audit-toolkit"
PACKAGE_DESCRIPTION = "Comprehensive technical SEO audit scripts and tools"

def get_version():
    """Return the current version of the package"""
    return __version__

def about():
    """Display information about the package"""
    info = f"""
    SEO Audit Toolkit v{__version__}
    
    Created by: {__author__}
    Email: {__email__}
    License: {__license__}
    
    A comprehensive toolkit for performing technical SEO audits,
    analyzing Core Web Vitals, validating schema markup, and more.
    
    For more information, visit:
    https://github.com/youssefhodaigui/seo-audit-toolkit
    """
    return info.strip()
