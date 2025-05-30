"""
Technical SEO Audit Module
Performs comprehensive technical SEO audits on websites

Author: Youssef Hodaigui - Mindflow Marketing
Website: https://youssefhodaigui.com
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime

class TechnicalAuditor:
    """Comprehensive technical SEO auditor for websites"""
    
    def __init__(self, user_agent: Optional[str] = None):
        """
        Initialize the Technical Auditor
        
        Args:
            user_agent: Custom user agent string
        """
        self.session = requests.Session()
        self.user_agent = user_agent or 'SEO-Audit-Toolkit/1.0 (by Youssef Hodaigui; +https://mindflowmarketing.com)'
        self.session.headers.update({
            'User-Agent': self.user_agent
        })
        self.timeout = 10
        
    def audit_website(self, url: str, checks: Optional[List[str]] = None) -> Dict:
        """
        Run comprehensive technical SEO audit on a website
        
        Args:
            url: Website URL to audit
            checks: List of specific checks to run (if None, runs all)
            
        Returns:
            Dictionary containing audit results
        """
        # Default checks if none specified
        if checks is None:
            checks = [
                'title', 'meta_description', 'headings', 'images',
                'canonical', 'robots', 'schema', 'links'
            ]
        
        results = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'checks': {},
            'score': 0,
            'issues': {
                'critical': 0,
                'warnings': 0,
                'passed': 0
            }
        }
        
        # Fetch page
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
        except requests.exceptions.RequestException as e:
            results['status'] = 'error'
            results['error'] = str(e)
            return results
        
        # Run selected checks
        check_methods = {
            'title': self._check_title,
            'meta_description': self._check_meta_description,
            'headings': self._check_headings,
            'images': self._check_images,
            'canonical': self._check_canonical,
            'robots': self._check_robots_meta,
            'schema': self._check_schema,
            'links': self._check_links
        }
        
        for check in checks:
            if check in check_methods:
                results['checks'][check] = check_methods[check](soup, response)
                
                # Update issue counts
                status = results['checks'][check].get('status', 'error')
                if status == 'error':
                    results['issues']['critical'] += 1
                elif status == 'warning':
                    results['issues']['warnings'] += 1
                elif status == 'ok':
                    results['issues']['passed'] += 1
        
        # Calculate overall score
        total_checks = sum(results['issues'].values())
        if total_checks > 0:
            results['score'] = int((results['issues']['passed'] / total_checks) * 100)
        
        return results
    
    def _check_title(self, soup: BeautifulSoup, response: requests.Response) -> Dict:
        """Check page title optimization"""
        title_tag = soup.find('title')
        
        if not title_tag:
            return {
                'status': 'error',
                'message': 'No title tag found',
                'recommendations': ['Add a unique, descriptive title tag to the page']
            }
        
        title_text = title_tag.text.strip()
        title_length = len(title_text)
        
        result = {
            'status': 'ok',
            'content': title_text,
            'length': title_length,
            'recommendations': []
        }
        
        # Check length
        if title_length < 30:
            result['status'] = 'warning'
            result['recommendations'].append(
                f'Title is too short ({title_length} chars). Aim for 30-60 characters.'
            )
        elif title_length > 60:
            result['status'] = 'warning'
            result['recommendations'].append(
                f'Title is too long ({title_length} chars). Keep it under 60 characters.'
            )
        
        # Check for common issues
        if title_text.lower() in ['untitled', 'home', 'index']:
            result['status'] = 'error'
            result['recommendations'].append('Title appears to be generic. Make it unique and descriptive.')
        
        return result
    
    def _check_meta_description(self, soup: BeautifulSoup, response: requests.Response) -> Dict:
        """Check meta description optimization"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        
        if not meta_desc or not meta_desc.get('content'):
            return {
                'status': 'error',
                'message': 'No meta description found',
                'recommendations': [
                    'Add a compelling meta description that summarizes the page content'
                ]
            }
        
        desc_text = meta_desc.get('content', '').strip()
        desc_length = len(desc_text)
        
        result = {
            'status': 'ok',
            'content': desc_text,
            'length': desc_length,
            'recommendations': []
        }
        
        # Check length
        if desc_length < 120:
            result['status'] = 'warning'
            result['recommendations'].append(
                f'Description is too short ({desc_length} chars). Aim for 120-160 characters.'
            )
        elif desc_length > 160:
            result['status'] = 'warning'
            result['recommendations'].append(
                f'Description is too long ({desc_length} chars). Keep it under 160 characters.'
            )
        
        # Check for duplicate content
        title_tag = soup.find('title')
        if title_tag and desc_text == title_tag.text.strip():
            result['status'] = 'error'
            result['recommendations'].append('Meta description is identical to title. Make it unique.')
        
        return result
    
    def _check_headings(self, soup: BeautifulSoup, response: requests.Response) -> Dict:
        """Check heading structure and optimization"""
        headings = {
            'h1': soup.find_all('h1'),
            'h2': soup.find_all('h2'),
            'h3': soup.find_all('h3'),
            'h4': soup.find_all('h4'),
            'h5': soup.find_all('h5'),
            'h6': soup.find_all('h6')
        }
        
        result = {
            'status': 'ok',
            'structure': {},
            'recommendations': []
        }
        
        # Count headings
        for tag, elements in headings.items():
            result['structure'][tag] = {
                'count': len(elements),
                'content': [elem.text.strip() for elem in elements[:5]]  # First 5
            }
        
        # Check H1
        h1_count = len(headings['h1'])
        if h1_count == 0:
            result['status'] = 'error'
            result['recommendations'].append('No H1 tag found. Add exactly one H1 tag.')
        elif h1_count > 1:
            result['status'] = 'warning'
            result['recommendations'].append(f'Multiple H1 tags found ({h1_count}). Use only one H1 per page.')
        
        # Check heading hierarchy
        if headings['h3'] and not headings['h2']:
            result['status'] = 'warning'
            result['recommendations'].append('H3 tags found without H2. Maintain proper heading hierarchy.')
        
        return result
    
    def _check_images(self, soup: BeautifulSoup, response: requests.Response) -> Dict:
        """Check image optimization"""
        images = soup.find_all('img')
        
        result = {
            'status': 'ok',
            'total_images': len(images),
            'issues': {
                'missing_alt': 0,
                'empty_alt': 0,
                'missing_dimensions': 0
            },
            'recommendations': []
        }
        
        for img in images:
            # Check alt text
            alt = img.get('alt')
            if alt is None:
                result['issues']['missing_alt'] += 1
            elif alt.strip() == '':
                result['issues']['empty_alt'] += 1
            
            # Check dimensions
            if not (img.get('width') and img.get('height')):
                result['issues']['missing_dimensions'] += 1
        
        # Set status based on issues
        if result['issues']['missing_alt'] > 0:
            result['status'] = 'error'
            result['recommendations'].append(
                f"{result['issues']['missing_alt']} images missing alt attributes. Add descriptive alt text."
            )
        
        if result['issues']['empty_alt'] > 0:
            result['status'] = 'warning' if result['status'] == 'ok' else result['status']
            result['recommendations'].append(
                f"{result['issues']['empty_alt']} images have empty alt attributes. Add meaningful descriptions."
            )
        
        if result['issues']['missing_dimensions'] > 0:
            result['status'] = 'warning' if result['status'] == 'ok' else result['status']
            result['recommendations'].append(
                f"{result['issues']['missing_dimensions']} images missing width/height. Add dimensions to prevent CLS."
            )
        
        return result
    
    def _check_canonical(self, soup: BeautifulSoup, response: requests.Response) -> Dict:
        """Check canonical URL implementation"""
        canonical = soup.find('link', {'rel': 'canonical'})
        
        result = {
            'status': 'ok',
            'recommendations': []
        }
        
        if not canonical:
            result['status'] = 'warning'
            result['recommendations'].append('No canonical URL found. Add canonical tag to prevent duplicate content issues.')
        else:
            canonical_url = canonical.get('href', '')
            result['canonical_url'] = canonical_url
            
            # Validate canonical URL
            if not canonical_url:
                result['status'] = 'error'
                result['recommendations'].append('Canonical tag found but href is empty.')
            elif not canonical_url.startswith(('http://', 'https://')):
                result['status'] = 'warning'
                result['recommendations'].append('Canonical URL should be absolute, not relative.')
        
        return result
    
    def _check_robots_meta(self, soup: BeautifulSoup, response: requests.Response) -> Dict:
        """Check robots meta tag"""
        robots_meta = soup.find('meta', {'name': 'robots'})
        
        result = {
            'status': 'ok',
            'recommendations': []
        }
        
        if robots_meta:
            content = robots_meta.get('content', '').lower()
            result['content'] = content
            
            if 'noindex' in content:
                result['status'] = 'warning'
                result['recommendations'].append('Page is set to noindex. Ensure this is intentional.')
            
            if 'nofollow' in content:
                result['status'] = 'warning'
                result['recommendations'].append('Page is set to nofollow. This prevents link equity flow.')
        else:
            result['content'] = 'Not specified (defaults to index, follow)'
        
        return result
    
    def _check_schema(self, soup: BeautifulSoup, response: requests.Response) -> Dict:
        """Check for structured data/schema markup"""
        result = {
            'status': 'ok',
            'types_found': [],
            'recommendations': []
        }
        
        # Look for JSON-LD
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        
        if json_ld_scripts:
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if '@type' in data:
                        result['types_found'].append(data['@type'])
                except json.JSONDecodeError:
                    result['status'] = 'error'
                    result['recommendations'].append('Invalid JSON-LD structured data found.')
        else:
            result['status'] = 'warning'
            result['recommendations'].append('No structured data found. Add schema markup to enhance search appearance.')
        
        return result
    
    def _check_links(self, soup: BeautifulSoup, response: requests.Response) -> Dict:
        """Check internal and external links"""
        links = soup.find_all('a', href=True)
        base_domain = urlparse(response.url).netloc
        
        result = {
            'status': 'ok',
            'total_links': len(links),
            'internal_links': 0,
            'external_links': 0,
            'broken_links': [],
            'recommendations': []
        }
        
        for link in links:
            href = link.get('href', '')
            
            # Skip empty or anchor links
            if not href or href.startswith('#'):
                continue
            
            # Make absolute URL
            absolute_url = urljoin(response.url, href)
            parsed = urlparse(absolute_url)
            
            # Categorize link
            if parsed.netloc == base_domain or not parsed.netloc:
                result['internal_links'] += 1
            else:
                result['external_links'] += 1
                
                # Check for rel="nofollow" on external links
                rel = link.get('rel', [])
                if isinstance(rel, str):
                    rel = [rel]
                if 'nofollow' not in rel and 'noopener' not in rel:
                    result['status'] = 'warning'
                    result['recommendations'].append(
                        'Some external links missing rel="nofollow" or rel="noopener".'
                    )
        
        return result
    
    def generate_report(self, results: Dict, format: str = 'json', output: Optional[str] = None) -> str:
        """
        Generate audit report in specified format
        
        Args:
            results: Audit results dictionary
            format: Output format (json, html, text)
            output: Optional file path to save report
            
        Returns:
            Formatted report string
        """
        if format == 'json':
            report = json.dumps(results, indent=2)
        elif format == 'text':
            report = self._generate_text_report(results)
        elif format == 'html':
            report = self._generate_html_report(results)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report
    
    def _generate_text_report(self, results: Dict) -> str:
        """Generate plain text report"""
        lines = [
            "=" * 60,
            "SEO AUDIT REPORT",
            "=" * 60,
            f"URL: {results['url']}",
            f"Date: {results['timestamp']}",
            f"Overall Score: {results.get('score', 0)}%",
            "",
            "SUMMARY",
            "-" * 40,
            f"Critical Issues: {results['issues']['critical']}",
            f"Warnings: {results['issues']['warnings']}",
            f"Passed: {results['issues']['passed']}",
            "",
            "DETAILED RESULTS",
            "-" * 40,
        ]
        
        for check, data in results['checks'].items():
            lines.append(f"\n{check.upper()}")
            lines.append(f"Status: {data.get('status', 'unknown')}")
            
            if 'content' in data:
                lines.append(f"Content: {data['content'][:100]}...")
            
            if data.get('recommendations'):
                lines.append("Recommendations:")
                for rec in data['recommendations']:
                    lines.append(f"  - {rec}")
        
        lines.extend([
            "",
            "=" * 60,
            "Report generated by SEO Audit Toolkit",
            "Created by Youssef Hodaigui - Mindflow Marketing",
            "https://youssefhodaigui.com"
        ])
        
        return "\n".join(lines)
    
    def _generate_html_report(self, results: Dict) -> str:
        """Generate HTML report"""
        # This is a simplified version - you can expand with templates
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SEO Audit Report - {results['url']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #f0f0f0; padding: 20px; }}
                .score {{ font-size: 48px; color: #333; }}
                .issue-critical {{ color: #d32f2f; }}
                .issue-warning {{ color: #f57c00; }}
                .issue-passed {{ color: #388e3c; }}
                .recommendation {{ background: #fff3cd; padding: 10px; margin: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>SEO Audit Report</h1>
                <p>URL: <a href="{results['url']}">{results['url']}</a></p>
                <p>Date: {results['timestamp']}</p>
                <div class="score">{results.get('score', 0)}%</div>
            </div>
            
            <h2>Summary</h2>
            <ul>
                <li class="issue-critical">Critical Issues: {results['issues']['critical']}</li>
                <li class="issue-warning">Warnings: {results['issues']['warnings']}</li>
                <li class="issue-passed">Passed: {results['issues']['passed']}</li>
            </ul>
            
            <h2>Detailed Results</h2>
        """
        
        for check, data in results['checks'].items():
            status_class = f"issue-{data.get('status', 'unknown')}"
            html += f"""
            <div class="check">
                <h3>{check.replace('_', ' ').title()}</h3>
                <p class="{status_class}">Status: {data.get('status', 'unknown')}</p>
            """
            
            if data.get('recommendations'):
                html += "<div class='recommendations'>"
                for rec in data['recommendations']:
                    html += f"<div class='recommendation'>{rec}</div>"
                html += "</div>"
            
            html += "</div>"
        
        html += """
            <footer>
                <p>Report generated by SEO Audit Toolkit</p>
                <p>Created by <a href="https://youssefhodaigui.com">Youssef Hodaigui</a> - 
                   <a href="https://mindflowmarketing.com">Mindflow Marketing</a></p>
            </footer>
        </body>
        </html>
        """
        
        return html


# Command line interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python technical_audit.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    auditor = TechnicalAuditor()
    
    print(f"Auditing {url}...")
    results = auditor.audit_website(url)
    
    print("\nResults:")
    print(auditor.generate_report(results, format='text'))
