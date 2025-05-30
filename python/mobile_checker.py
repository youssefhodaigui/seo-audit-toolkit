"""
Mobile-Friendliness Checker Module
Analyzes mobile usability and responsiveness for SEO

Author: Youssef Hodaigui - Mindflow Marketing
Website: https://youssefhodaigui.com
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re
import json

class MobileChecker:
    """Check mobile-friendliness and responsiveness of websites"""
    
    def __init__(self):
        """Initialize Mobile Checker"""
        self.session = requests.Session()
        self.mobile_user_agent = (
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 '
            'Mobile/15E148 Safari/604.1'
        )
        self.desktop_user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/91.0.4472.124 Safari/537.36'
        )
        
    def check_mobile_friendliness(self, url: str) -> Dict:
        """
        Check mobile-friendliness of a URL
        
        Args:
            url: URL to check
            
        Returns:
            Dictionary containing mobile-friendliness analysis
        """
        results = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'mobile_friendly': True,
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'viewport_analysis': {},
            'resource_analysis': {},
            'usability_checks': {}
        }
        
        try:
            # Fetch page with mobile user agent
            mobile_response = self._fetch_page(url, 'mobile')
            mobile_soup = BeautifulSoup(mobile_response.text, 'lxml')
            
            # Fetch page with desktop user agent for comparison
            desktop_response = self._fetch_page(url, 'desktop')
            desktop_soup = BeautifulSoup(desktop_response.text, 'lxml')
            
            # Run checks
            self._check_viewport(mobile_soup, results)
            self._check_responsive_design(mobile_soup, desktop_soup, results)
            self._check_touch_elements(mobile_soup, results)
            self._check_font_sizes(mobile_soup, results)
            self._check_media_queries(mobile_response.text, results)
            self._check_mobile_resources(mobile_soup, results)
            self._check_page_speed_mobile(url, results)
            
            # Generate overall assessment
            results['mobile_friendly'] = len(results['issues']) == 0
            results['score'] = self._calculate_score(results)
            results['recommendations'] = self._generate_recommendations(results)
            
        except requests.exceptions.RequestException as e:
            results['status'] = 'error'
            results['issues'].append(f"Failed to fetch URL: {str(e)}")
        except Exception as e:
            results['status'] = 'error'
            results['issues'].append(f"Analysis failed: {str(e)}")
        
        return results
    
    def _fetch_page(self, url: str, device_type: str) -> requests.Response:
        """Fetch page with specific user agent"""
        headers = {
            'User-Agent': self.mobile_user_agent if device_type == 'mobile' else self.desktop_user_agent
        }
        
        response = self.session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    
    def _check_viewport(self, soup: BeautifulSoup, results: Dict):
        """Check viewport meta tag configuration"""
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        
        results['viewport_analysis'] = {
            'present': False,
            'content': '',
            'issues': []
        }
        
        if not viewport:
            results['issues'].append('Missing viewport meta tag')
            results['viewport_analysis']['issues'].append(
                'No viewport meta tag found - critical for mobile responsiveness'
            )
            return
        
        content = viewport.get('content', '')
        results['viewport_analysis']['present'] = True
        results['viewport_analysis']['content'] = content
        
        # Check viewport content
        if not content:
            results['issues'].append('Empty viewport meta tag')
            return
        
        # Parse viewport directives
        directives = {}
        for directive in content.split(','):
            if '=' in directive:
                key, value = directive.strip().split('=', 1)
                directives[key.strip()] = value.strip()
        
        # Check for width=device-width
        if 'width' not in directives:
            results['issues'].append('Viewport missing width directive')
        elif directives['width'] != 'device-width':
            results['warnings'].append(
                f"Viewport width set to '{directives['width']}' instead of 'device-width'"
            )
        
        # Check for initial-scale
        if 'initial-scale' not in directives:
            results['warnings'].append('Viewport missing initial-scale directive')
        elif directives.get('initial-scale') != '1':
            results['warnings'].append(
                f"Initial-scale set to {directives['initial-scale']} instead of 1"
            )
        
        # Check for maximum-scale restrictions
        if 'maximum-scale' in directives and float(directives['maximum-scale']) < 2:
            results['warnings'].append(
                'Maximum-scale restricts zooming - consider accessibility'
            )
        
        # Check for user-scalable=no
        if directives.get('user-scalable') == 'no':
            results['issues'].append(
                'user-scalable=no prevents zooming - accessibility issue'
            )
    
    def _check_responsive_design(self, mobile_soup: BeautifulSoup, desktop_soup: BeautifulSoup, results: Dict):
        """Check for responsive design implementation"""
        results['responsive_checks'] = {
            'css_media_queries': False,
            'flexible_images': False,
            'flexible_layout': False
        }
        
        # Check for responsive images
        mobile_images = mobile_soup.find_all('img')
        for img in mobile_images:
            # Check for responsive attributes
            if img.get('srcset') or img.get('sizes'):
                results['responsive_checks']['flexible_images'] = True
                break
            
            # Check for max-width in style
            style = img.get('style', '')
            if 'max-width' in style and '100%' in style:
                results['responsive_checks']['flexible_images'] = True
                break
        
        if not results['responsive_checks']['flexible_images']:
            results['warnings'].append(
                'Images may not be responsive - consider using srcset or max-width: 100%'
            )
        
        # Check for flexible containers
        containers = mobile_soup.find_all(['div', 'section', 'article'])
        fixed_width_count = 0
        
        for container in containers[:50]:  # Check first 50 containers
            style = container.get('style', '')
            if re.search(r'width:\s*\d+px', style):
                fixed_width_count += 1
        
        if fixed_width_count > 10:
            results['warnings'].append(
                f'Found {fixed_width_count} containers with fixed pixel widths'
            )
    
    def _check_touch_elements(self, soup: BeautifulSoup, results: Dict):
        """Check touch target sizes and spacing"""
        results['usability_checks']['touch_targets'] = {
            'total_checked': 0,
            'too_small': 0,
            'too_close': 0
        }
        
        # Check clickable elements
        clickable_elements = soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
        
        small_targets = []
        close_targets = []
        
        for element in clickable_elements[:100]:  # Check first 100 elements
            results['usability_checks']['touch_targets']['total_checked'] += 1
            
            # Check for size indicators in class or style
            classes = ' '.join(element.get('class', []))
            style = element.get('style', '')
            
            # Look for small indicators
            if any(indicator in classes.lower() for indicator in ['xs', 'tiny', 'small']):
                small_targets.append(element.name)
                results['usability_checks']['touch_targets']['too_small'] += 1
            
            # Check for inline styles suggesting small size
            if re.search(r'(height|width):\s*([0-2]?\d)px', style):
                small_targets.append(element.name)
                results['usability_checks']['touch_targets']['too_small'] += 1
        
        if small_targets:
            results['warnings'].append(
                f'Found {len(small_targets)} potentially small touch targets'
            )
            results['recommendations'].append(
                'Ensure touch targets are at least 48x48 CSS pixels'
            )
    
    def _check_font_sizes(self, soup: BeautifulSoup, results: Dict):
        """Check for readable font sizes on mobile"""
        results['usability_checks']['typography'] = {
            'small_text_found': False,
            'font_issues': []
        }
        
        # Check for small font sizes
        text_elements = soup.find_all(['p', 'span', 'div', 'li', 'td'])
        small_font_count = 0
        
        for element in text_elements[:100]:  # Check first 100 text elements
            style = element.get('style', '')
            
            # Check for small font sizes in inline styles
            font_size_match = re.search(r'font-size:\s*(\d+)(px|pt)', style)
            if font_size_match:
                size = int(font_size_match.group(1))
                unit = font_size_match.group(2)
                
                if (unit == 'px' and size < 12) or (unit == 'pt' and size < 9):
                    small_font_count += 1
        
        if small_font_count > 5:
            results['usability_checks']['typography']['small_text_found'] = True
            results['warnings'].append(
                f'Found {small_font_count} elements with potentially small font sizes'
            )
            results['recommendations'].append(
                'Use minimum 16px font size for body text on mobile'
            )
        
        # Check for font scaling prevention
        if soup.find('meta', attrs={'name': 'HandheldFriendly', 'content': 'true'}):
            results['usability_checks']['typography']['font_issues'].append(
                'HandheldFriendly meta tag may affect text scaling'
            )
    
    def _check_media_queries(self, html_content: str, results: Dict):
        """Check for CSS media queries indicating responsive design"""
        results['responsive_checks']['media_queries'] = {
            'found': False,
            'breakpoints': []
        }
        
        # Look for media queries in CSS
        media_query_pattern = r'@media[^{]+\{[^}]+\}'
        inline_styles = re.findall(r'<style[^>]*>(.*?)</style>', html_content, re.DOTALL)
        
        for style_content in inline_styles:
            if '@media' in style_content:
                results['responsive_checks']['media_queries']['found'] = True
                
                # Extract breakpoints
                breakpoint_pattern = r'(?:max-width|min-width):\s*(\d+)px'
                breakpoints = re.findall(breakpoint_pattern, style_content)
                results['responsive_checks']['media_queries']['breakpoints'].extend(breakpoints)
        
        # Check linked stylesheets for responsive indicators
        if not results['responsive_checks']['media_queries']['found']:
            # Look for common responsive CSS frameworks
            if any(framework in html_content.lower() for framework in 
                   ['bootstrap', 'foundation', 'tailwind', 'bulma']):
                results['responsive_checks']['media_queries']['found'] = True
                results['responsive_checks']['css_framework'] = True
    
    def _check_mobile_resources(self, soup: BeautifulSoup, results: Dict):
        """Check for mobile-optimized resources"""
        results['resource_analysis'] = {
            'large_images': 0,
            'unoptimized_scripts': 0,
            'render_blocking': 0
        }
        
        # Check images
        images = soup.find_all('img')
        for img in images:
            src = img.get('src', '')
            # Check for high-resolution indicators
            if any(indicator in src.lower() for indicator in ['@2x', '@3x', 'retina']):
                continue  # Properly handling retina
            
            # Check for loading attribute
            if not img.get('loading'):
                results['warnings'].append(
                    'Images missing loading="lazy" attribute for performance'
                )
                break
        
        # Check for render-blocking resources
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            if not script.get('async') and not script.get('defer'):
                results['resource_analysis']['render_blocking'] += 1
        
        if results['resource_analysis']['render_blocking'] > 3:
            results['warnings'].append(
                f"{results['resource_analysis']['render_blocking']} render-blocking scripts found"
            )
            results['recommendations'].append(
                'Add async or defer attributes to non-critical scripts'
            )
        
        # Check for mobile-specific optimizations
        if soup.find('link', attrs={'rel': 'manifest'}):
            results['resource_analysis']['pwa_ready'] = True
        
        if soup.find('meta', attrs={'name': 'apple-mobile-web-app-capable'}):
            results['resource_analysis']['ios_optimized'] = True
    
    def _check_page_speed_mobile(self, url: str, results: Dict):
        """Add mobile-specific performance considerations"""
        results['performance_hints'] = {
            'critical_resources': [],
            'optimization_opportunities': []
        }
        
        # Mobile-specific performance recommendations
        results['performance_hints']['optimization_opportunities'].extend([
            'Minimize Critical Rendering Path for mobile',
            'Implement AMP (Accelerated Mobile Pages) if applicable',
            'Use responsive images with srcset',
            'Enable browser caching for mobile assets',
            'Compress images for mobile bandwidth'
        ])
    
    def _calculate_score(self, results: Dict) -> int:
        """Calculate mobile-friendliness score"""
        score = 100
        
        # Deduct for issues
        score -= len(results['issues']) * 15
        score -= len(results['warnings']) * 5
        
        # Bonus for good practices
        if results.get('viewport_analysis', {}).get('present'):
            score += 5
        
        if results.get('responsive_checks', {}).get('media_queries', {}).get('found'):
            score += 5
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate mobile optimization recommendations"""
        recommendations = results.get('recommendations', [])
        
        # Viewport recommendations
        if not results.get('viewport_analysis', {}).get('present'):
            recommendations.insert(0, 
                'Add viewport meta tag: <meta name="viewport" content="width=device-width, initial-scale=1">'
            )
        
        # Responsive design recommendations
        if not results.get('responsive_checks', {}).get('media_queries', {}).get('found'):
            recommendations.append(
                'Implement responsive design with CSS media queries'
            )
        
        # Touch target recommendations
        touch_data = results.get('usability_checks', {}).get('touch_targets', {})
        if touch_data.get('too_small', 0) > 0:
            recommendations.append(
                'Increase touch target sizes to at least 48x48 CSS pixels'
            )
        
        # Performance recommendations
        if results.get('resource_analysis', {}).get('render_blocking', 0) > 0:
            recommendations.append(
                'Optimize JavaScript delivery for faster mobile loading'
            )
        
        # Additional mobile-specific recommendations
        if len(results['issues']) == 0 and len(results['warnings']) < 3:
            recommendations.extend([
                'Consider implementing Progressive Web App (PWA) features',
                'Test with real devices across different screen sizes',
                'Monitor Core Web Vitals specifically for mobile users'
            ])
        
        return recommendations
    
    def generate_report(self, results: Dict) -> str:
        """Generate mobile-friendliness report"""
        lines = [
            "=" * 60,
            "MOBILE-FRIENDLINESS REPORT",
            "=" * 60,
            f"URL: {results['url']}",
            f"Mobile Friendly: {'✅ Yes' if results['mobile_friendly'] else '❌ No'}",
            f"Score: {results['score']}%",
            f"Timestamp: {results['timestamp']}",
            ""
        ]
        
        # Viewport Analysis
        viewport = results.get('viewport_analysis', {})
        if viewport:
            lines.extend([
                "VIEWPORT CONFIGURATION",
                "-" * 40,
                f"Present: {'Yes' if viewport.get('present') else 'No'}",
            ])
            if viewport.get('content'):
                lines.append(f"Content: {viewport['content']}")
            lines.append("")
        
        # Issues
        if results['issues']:
            lines.extend([
                "CRITICAL ISSUES",
                "-" * 40
            ])
            for issue in results['issues']:
                lines.append(f"  ❌ {issue}")
            lines.append("")
        
        # Warnings
        if results['warnings']:
            lines.extend([
                "WARNINGS",
                "-" * 40
            ])
            for warning in results['warnings']:
                lines.append(f"  ⚠️  {warning}")
            lines.append("")
        
        # Responsive Checks
        responsive = results.get('responsive_checks', {})
        if responsive:
            lines.extend([
                "RESPONSIVE DESIGN CHECKS",
                "-" * 40
            ])
            lines.append(f"  Media Queries: {'✅' if responsive.get('media_queries', {}).get('found') else '❌'}")
            lines.append(f"  Flexible Images: {'✅' if responsive.get('flexible_images') else '❌'}")
            lines.append(f"  CSS Framework: {'✅' if responsive.get('css_framework') else '❌'}")
            lines.append("")
        
        # Usability Checks
        usability = results.get('usability_checks', {})
        if usability.get('touch_targets'):
            touch = usability['touch_targets']
            lines.extend([
                "TOUCH TARGET ANALYSIS",
                "-" * 40,
                f"  Elements Checked: {touch.get('total_checked', 0)}",
                f"  Too Small: {touch.get('too_small', 0)}",
                f"  Too Close: {touch.get('too_close', 0)}",
                ""
            ])
        
        # Recommendations
        if results.get('recommendations'):
            lines.extend([
                "RECOMMENDATIONS",
                "-" * 40
            ])
            for i, rec in enumerate(results['recommendations'], 1):
                lines.append(f"  {i}. {rec}")
        
        lines.extend([
            "",
            "=" * 60,
            "Report generated by SEO Audit Toolkit",
            "Created by Youssef Hodaigui - Mindflow Marketing",
            "https://youssefhodaigui.com"
        ])
        
        return "\n".join(lines)


# Command line interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python mobile_checker.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    checker = MobileChecker()
    
    print(f"Checking mobile-friendliness for {url}...")
    results = checker.check_mobile_friendliness(url)
    
    print("\nResults:")
    print(checker.generate_report(results))
