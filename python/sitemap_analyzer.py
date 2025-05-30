"""
Sitemap Analyzer Module
Analyzes XML sitemaps for SEO optimization

Author: Youssef Hodaigui - Mindflow Marketing
Website: https://youssefhodaigui.com
"""

import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
from datetime import datetime
import gzip
from io import BytesIO
from typing import Dict, List, Optional, Tuple
import re

class SitemapAnalyzer:
    """Analyze XML sitemaps for technical SEO issues"""
    
    def __init__(self):
        """Initialize Sitemap Analyzer"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SEO-Audit-Toolkit/1.0 (Sitemap Analyzer)'
        })
        self.timeout = 30
        self.max_urls = 50000  # Google's limit per sitemap
        self.max_size = 52428800  # 50MB uncompressed
        
    def analyze(self, sitemap_url: str, check_urls: bool = False) -> Dict:
        """
        Analyze an XML sitemap
        
        Args:
            sitemap_url: URL of the sitemap
            check_urls: Whether to check if URLs are accessible
            
        Returns:
            Dictionary containing analysis results
        """
        results = {
            'url': sitemap_url,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'type': 'unknown',
            'urls_count': 0,
            'issues': {
                'errors': [],
                'warnings': [],
                'info': []
            },
            'stats': {},
            'recommendations': []
        }
        
        try:
            # Fetch sitemap
            sitemap_content, content_type = self._fetch_sitemap(sitemap_url)
            
            # Determine sitemap type
            if '<sitemapindex' in sitemap_content:
                results['type'] = 'sitemap_index'
                self._analyze_sitemap_index(sitemap_content, sitemap_url, results)
            elif '<urlset' in sitemap_content:
                results['type'] = 'url_sitemap'
                self._analyze_url_sitemap(sitemap_content, sitemap_url, results, check_urls)
            else:
                results['status'] = 'error'
                results['issues']['errors'].append('Invalid sitemap format')
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
            
        except requests.exceptions.RequestException as e:
            results['status'] = 'error'
            results['issues']['errors'].append(f"Failed to fetch sitemap: {str(e)}")
        except ET.ParseError as e:
            results['status'] = 'error'
            results['issues']['errors'].append(f"XML parsing error: {str(e)}")
        except Exception as e:
            results['status'] = 'error'
            results['issues']['errors'].append(f"Analysis failed: {str(e)}")
        
        return results
    
    def _fetch_sitemap(self, url: str) -> Tuple[str, str]:
        """Fetch sitemap content, handling compression"""
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '').lower()
        
        # Handle gzipped sitemaps
        if url.endswith('.gz') or 'gzip' in content_type:
            try:
                content = gzip.decompress(response.content).decode('utf-8')
            except:
                content = response.text
        else:
            content = response.text
        
        return content, content_type
    
    def _analyze_sitemap_index(self, content: str, base_url: str, results: Dict):
        """Analyze a sitemap index file"""
        try:
            root = ET.fromstring(content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            sitemaps = root.findall('.//ns:sitemap', namespace)
            results['urls_count'] = len(sitemaps)
            results['stats']['child_sitemaps'] = len(sitemaps)
            
            if len(sitemaps) == 0:
                results['issues']['errors'].append('No sitemaps found in index')
                return
            
            # Analyze each child sitemap reference
            for sitemap in sitemaps:
                loc = sitemap.find('ns:loc', namespace)
                lastmod = sitemap.find('ns:lastmod', namespace)
                
                if loc is None or not loc.text:
                    results['issues']['errors'].append('Sitemap entry missing <loc> tag')
                    continue
                
                # Check URL validity
                sitemap_url = loc.text.strip()
                if not sitemap_url.startswith(('http://', 'https://')):
                    results['issues']['warnings'].append(
                        f"Relative URL in sitemap index: {sitemap_url}"
                    )
                
                # Check lastmod
                if lastmod is not None and lastmod.text:
                    try:
                        datetime.fromisoformat(lastmod.text.replace('Z', '+00:00'))
                    except:
                        results['issues']['warnings'].append(
                            f"Invalid lastmod date format: {lastmod.text}"
                        )
            
        except ET.ParseError as e:
            results['issues']['errors'].append(f"XML parsing error: {str(e)}")
    
    def _analyze_url_sitemap(self, content: str, base_url: str, results: Dict, check_urls: bool):
        """Analyze a URL sitemap"""
        try:
            root = ET.fromstring(content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            urls = root.findall('.//ns:url', namespace)
            results['urls_count'] = len(urls)
            
            if len(urls) == 0:
                results['issues']['errors'].append('No URLs found in sitemap')
                return
            
            # Check sitemap size limits
            if len(urls) > self.max_urls:
                results['issues']['errors'].append(
                    f"Sitemap exceeds 50,000 URL limit ({len(urls)} URLs)"
                )
            
            if len(content.encode('utf-8')) > self.max_size:
                results['issues']['errors'].append(
                    f"Sitemap exceeds 50MB size limit"
                )
            
            # Initialize stats
            results['stats'] = {
                'total_urls': len(urls),
                'with_lastmod': 0,
                'with_changefreq': 0,
                'with_priority': 0,
                'duplicate_urls': 0,
                'invalid_urls': 0,
                'status_codes': {}
            }
            
            seen_urls = set()
            base_domain = urlparse(base_url).netloc
            
            # Analyze each URL
            for i, url_elem in enumerate(urls):
                loc = url_elem.find('ns:loc', namespace)
                lastmod = url_elem.find('ns:lastmod', namespace)
                changefreq = url_elem.find('ns:changefreq', namespace)
                priority = url_elem.find('ns:priority', namespace)
                
                # Check required <loc> tag
                if loc is None or not loc.text:
                    results['issues']['errors'].append(f"URL entry {i} missing <loc> tag")
                    continue
                
                url = loc.text.strip()
                
                # Check for duplicates
                if url in seen_urls:
                    results['stats']['duplicate_urls'] += 1
                    results['issues']['warnings'].append(f"Duplicate URL: {url}")
                seen_urls.add(url)
                
                # Validate URL
                parsed_url = urlparse(url)
                if not parsed_url.scheme or not parsed_url.netloc:
                    results['stats']['invalid_urls'] += 1
                    results['issues']['errors'].append(f"Invalid URL: {url}")
                    continue
                
                # Check if URL is from same domain
                if parsed_url.netloc != base_domain:
                    results['issues']['warnings'].append(
                        f"URL from different domain: {url}"
                    )
                
                # Check optional tags
                if lastmod is not None and lastmod.text:
                    results['stats']['with_lastmod'] += 1
                    try:
                        datetime.fromisoformat(lastmod.text.replace('Z', '+00:00'))
                    except:
                        results['issues']['warnings'].append(
                            f"Invalid lastmod date: {lastmod.text} for {url}"
                        )
                
                if changefreq is not None and changefreq.text:
                    results['stats']['with_changefreq'] += 1
                    valid_frequencies = [
                        'always', 'hourly', 'daily', 'weekly',
                        'monthly', 'yearly', 'never'
                    ]
                    if changefreq.text.lower() not in valid_frequencies:
                        results['issues']['warnings'].append(
                            f"Invalid changefreq: {changefreq.text}"
                        )
                
                if priority is not None and priority.text:
                    results['stats']['with_priority'] += 1
                    try:
                        pri_value = float(priority.text)
                        if not (0.0 <= pri_value <= 1.0):
                            results['issues']['warnings'].append(
                                f"Invalid priority value: {priority.text}"
                            )
                    except ValueError:
                        results['issues']['warnings'].append(
                            f"Invalid priority format: {priority.text}"
                        )
                
                # Check URL accessibility if requested
                if check_urls and i < 10:  # Only check first 10 URLs
                    self._check_url_status(url, results)
            
            # Calculate percentages
            total = results['stats']['total_urls']
            if total > 0:
                results['stats']['lastmod_percentage'] = round(
                    (results['stats']['with_lastmod'] / total) * 100, 1
                )
                results['stats']['changefreq_percentage'] = round(
                    (results['stats']['with_changefreq'] / total) * 100, 1
                )
                results['stats']['priority_percentage'] = round(
                    (results['stats']['with_priority'] / total) * 100, 1
                )
                
        except ET.ParseError as e:
            results['issues']['errors'].append(f"XML parsing error: {str(e)}")
    
    def _check_url_status(self, url: str, results: Dict):
        """Check if URL is accessible"""
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            status_code = response.status_code
            
            if status_code not in results['stats']['status_codes']:
                results['stats']['status_codes'][status_code] = 0
            results['stats']['status_codes'][status_code] += 1
            
            if status_code >= 400:
                results['issues']['warnings'].append(
                    f"URL returns {status_code}: {url}"
                )
                
        except requests.exceptions.RequestException:
            results['issues']['info'].append(f"Could not check URL: {url}")
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Check for critical errors
        if results['status'] == 'error':
            recommendations.append("Fix sitemap errors before proceeding with optimization")
            return recommendations
        
        stats = results.get('stats', {})
        
        # URL count recommendations
        if results['urls_count'] == 0:
            recommendations.append("Add URLs to your sitemap")
        elif results['urls_count'] > 45000:
            recommendations.append(
                "Consider splitting sitemap (approaching 50,000 URL limit)"
            )
        
        # Lastmod recommendations
        lastmod_pct = stats.get('lastmod_percentage', 0)
        if lastmod_pct < 50:
            recommendations.append(
                f"Add lastmod dates to more URLs (currently {lastmod_pct}%)"
            )
        
        # Duplicate URLs
        if stats.get('duplicate_urls', 0) > 0:
            recommendations.append(
                f"Remove {stats['duplicate_urls']} duplicate URLs from sitemap"
            )
        
        # Invalid URLs
        if stats.get('invalid_urls', 0) > 0:
            recommendations.append(
                f"Fix {stats['invalid_urls']} invalid URLs in sitemap"
            )
        
        # Status codes
        status_codes = stats.get('status_codes', {})
        for code, count in status_codes.items():
            if code >= 400:
                recommendations.append(
                    f"Fix {count} URLs returning {code} status codes"
                )
        
        # Priority usage
        priority_pct = stats.get('priority_percentage', 0)
        if priority_pct == 100:
            recommendations.append(
                "Vary priority values to indicate relative importance of pages"
            )
        elif priority_pct == 0:
            recommendations.append(
                "Consider adding priority values to indicate page importance"
            )
        
        # Sitemap index recommendation
        if results['type'] == 'url_sitemap' and results['urls_count'] > 10000:
            recommendations.append(
                "Consider using a sitemap index for better organization"
            )
        
        return recommendations
    
    def find_sitemaps(self, domain: str) -> List[str]:
        """
        Find all sitemaps for a domain
        
        Args:
            domain: Domain to check
            
        Returns:
            List of sitemap URLs found
        """
        if not domain.startswith(('http://', 'https://')):
            domain = f'https://{domain}'
        
        sitemaps = []
        
        # Common sitemap locations
        common_paths = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap-index.xml',
            '/sitemaps/sitemap.xml',
            '/sitemap/',
            '/sitemap.xml.gz',
            '/sitemap_index.xml.gz',
            '/wp-sitemap.xml',  # WordPress
            '/news-sitemap.xml',
            '/video-sitemap.xml',
            '/image-sitemap.xml',
            '/mobile-sitemap.xml'
        ]
        
        # Check robots.txt first
        try:
            robots_url = urljoin(domain, '/robots.txt')
            response = self.session.get(robots_url, timeout=5)
            if response.status_code == 200:
                # Look for sitemap directives
                for line in response.text.splitlines():
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        if sitemap_url not in sitemaps:
                            sitemaps.append(sitemap_url)
        except:
            pass
        
        # Check common paths
        for path in common_paths:
            try:
                url = urljoin(domain, path)
                response = self.session.head(url, timeout=5)
                if response.status_code == 200:
                    if url not in sitemaps:
                        sitemaps.append(url)
            except:
                continue
        
        return sitemaps
    
    def generate_report(self, results: Dict) -> str:
        """Generate analysis report"""
        lines = [
            "=" * 60,
            "SITEMAP ANALYSIS REPORT",
            "=" * 60,
            f"URL: {results['url']}",
            f"Type: {results['type']}",
            f"Total URLs: {results['urls_count']}",
            f"Status: {results['status']}",
            f"Timestamp: {results['timestamp']}",
            ""
        ]
        
        # Statistics
        if results.get('stats'):
            lines.extend([
                "STATISTICS",
                "-" * 40
            ])
            stats = results['stats']
            for key, value in stats.items():
                if not key.endswith('_percentage') and key != 'status_codes':
                    lines.append(f"  {key.replace('_', ' ').title()}: {value}")
            
            # Add percentages
            if 'lastmod_percentage' in stats:
                lines.append(f"  URLs with lastmod: {stats['lastmod_percentage']}%")
            if 'changefreq_percentage' in stats:
                lines.append(f"  URLs with changefreq: {stats['changefreq_percentage']}%")
            if 'priority_percentage' in stats:
                lines.append(f"  URLs with priority: {stats['priority_percentage']}%")
            
            lines.append("")
        
        # Issues
        issues = results.get('issues', {})
        
        if issues.get('errors'):
            lines.extend([
                "ERRORS",
                "-" * 40
            ])
            for error in issues['errors'][:10]:  # Show first 10
                lines.append(f"  ❌ {error}")
            if len(issues['errors']) > 10:
                lines.append(f"  ... and {len(issues['errors']) - 10} more errors")
            lines.append("")
        
        if issues.get('warnings'):
            lines.extend([
                "WARNINGS",
                "-" * 40
            ])
            for warning in issues['warnings'][:10]:  # Show first 10
                lines.append(f"  ⚠️  {warning}")
            if len(issues['warnings']) > 10:
                lines.append(f"  ... and {len(issues['warnings']) - 10} more warnings")
            lines.append("")
        
        # Recommendations
        if results.get('recommendations'):
            lines.extend([
                "RECOMMENDATIONS",
                "-" * 40
            ])
            for rec in results['recommendations']:
                lines.append(f"  💡 {rec}")
        
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
        print("Usage: python sitemap_analyzer.py <sitemap_url|domain>")
        print("       python sitemap_analyzer.py --find <domain>")
        sys.exit(1)
    
    analyzer = SitemapAnalyzer()
    
    if sys.argv[1] == '--find' and len(sys.argv) > 2:
        domain = sys.argv[2]
        print(f"Finding sitemaps for {domain}...")
        sitemaps = analyzer.find_sitemaps(domain)
        
        if sitemaps:
            print(f"\nFound {len(sitemaps)} sitemap(s):")
            for sitemap in sitemaps:
                print(f"  - {sitemap}")
        else:
            print("No sitemaps found")
    else:
        sitemap_url = sys.argv[1]
        print(f"Analyzing sitemap: {sitemap_url}...")
        
        results = analyzer.analyze(sitemap_url, check_urls=True)
        print("\nResults:")
        print(analyzer.generate_report(results))
