"""
Core Web Vitals Analysis Module
Analyzes Google's Core Web Vitals metrics for SEO performance

Author: Youssef Hodaigui - Mindflow Marketing
Website: https://youssefhodaigui.com
"""

import requests
import json
import time
from typing import Dict, Optional, List
from datetime import datetime
import statistics

class CoreWebVitals:
    """Analyze Core Web Vitals metrics for any URL"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Core Web Vitals analyzer
        
        Args:
            api_key: Optional Google PageSpeed Insights API key
        """
        self.api_key = api_key
        self.psi_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        
    def analyze(self, url: str, strategy: str = 'mobile') -> Dict:
        """
        Analyze Core Web Vitals for a URL
        
        Args:
            url: URL to analyze
            strategy: 'mobile' or 'desktop'
            
        Returns:
            Dictionary containing CWV metrics and analysis
        """
        results = {
            'url': url,
            'strategy': strategy,
            'timestamp': datetime.now().isoformat(),
            'metrics': {},
            'score': 0,
            'status': 'completed',
            'recommendations': []
        }
        
        try:
            # Call PageSpeed Insights API
            params = {
                'url': url,
                'strategy': strategy,
                'category': 'performance'
            }
            
            if self.api_key:
                params['key'] = self.api_key
            
            response = requests.get(self.psi_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract Core Web Vitals
            if 'lighthouseResult' in data:
                lighthouse = data['lighthouseResult']
                audits = lighthouse.get('audits', {})
                
                # Extract metrics
                results['metrics'] = self._extract_metrics(audits)
                results['score'] = int(lighthouse.get('categories', {}).get('performance', {}).get('score', 0) * 100)
                
                # Generate recommendations
                results['recommendations'] = self._generate_recommendations(results['metrics'])
                
                # Lab vs Field data
                if 'loadingExperience' in data:
                    results['field_data'] = self._extract_field_data(data['loadingExperience'])
            
        except requests.exceptions.RequestException as e:
            results['status'] = 'error'
            results['error'] = str(e)
        except Exception as e:
            results['status'] = 'error'
            results['error'] = f"Analysis failed: {str(e)}"
        
        return results
    
    def _extract_metrics(self, audits: Dict) -> Dict:
        """Extract Core Web Vitals metrics from audit data"""
        metrics = {
            'lcp': {
                'value': 0,
                'score': 0,
                'displayValue': '',
                'status': 'unknown'
            },
            'fid': {
                'value': 0,
                'score': 0,
                'displayValue': '',
                'status': 'unknown'
            },
            'cls': {
                'value': 0,
                'score': 0,
                'displayValue': '',
                'status': 'unknown'
            },
            'fcp': {
                'value': 0,
                'score': 0,
                'displayValue': '',
                'status': 'unknown'
            },
            'ttfb': {
                'value': 0,
                'score': 0,
                'displayValue': '',
                'status': 'unknown'
            },
            'tti': {
                'value': 0,
                'score': 0,
                'displayValue': '',
                'status': 'unknown'
            }
        }
        
        # LCP - Largest Contentful Paint
        if 'largest-contentful-paint' in audits:
            lcp = audits['largest-contentful-paint']
            metrics['lcp']['value'] = lcp.get('numericValue', 0) / 1000  # Convert to seconds
            metrics['lcp']['score'] = lcp.get('score', 0)
            metrics['lcp']['displayValue'] = lcp.get('displayValue', '')
            metrics['lcp']['status'] = self._get_lcp_status(metrics['lcp']['value'])
        
        # FID - First Input Delay (using TBT as proxy in lab data)
        if 'total-blocking-time' in audits:
            tbt = audits['total-blocking-time']
            metrics['fid']['value'] = tbt.get('numericValue', 0)
            metrics['fid']['score'] = tbt.get('score', 0)
            metrics['fid']['displayValue'] = f"{metrics['fid']['value']} ms (TBT)"
            metrics['fid']['status'] = self._get_fid_status(metrics['fid']['value'])
        
        # CLS - Cumulative Layout Shift
        if 'cumulative-layout-shift' in audits:
            cls = audits['cumulative-layout-shift']
            metrics['cls']['value'] = cls.get('numericValue', 0)
            metrics['cls']['score'] = cls.get('score', 0)
            metrics['cls']['displayValue'] = cls.get('displayValue', '')
            metrics['cls']['status'] = self._get_cls_status(metrics['cls']['value'])
        
        # FCP - First Contentful Paint
        if 'first-contentful-paint' in audits:
            fcp = audits['first-contentful-paint']
            metrics['fcp']['value'] = fcp.get('numericValue', 0) / 1000
            metrics['fcp']['score'] = fcp.get('score', 0)
            metrics['fcp']['displayValue'] = fcp.get('displayValue', '')
        
        # TTFB - Time to First Byte
        if 'server-response-time' in audits:
            ttfb = audits['server-response-time']
            metrics['ttfb']['value'] = ttfb.get('numericValue', 0)
            metrics['ttfb']['score'] = ttfb.get('score', 0)
            metrics['ttfb']['displayValue'] = ttfb.get('displayValue', '')
        
        # TTI - Time to Interactive
        if 'interactive' in audits:
            tti = audits['interactive']
            metrics['tti']['value'] = tti.get('numericValue', 0) / 1000
            metrics['tti']['score'] = tti.get('score', 0)
            metrics['tti']['displayValue'] = tti.get('displayValue', '')
        
        return metrics
    
    def _get_lcp_status(self, value: float) -> str:
        """Determine LCP status based on thresholds"""
        if value <= 2.5:
            return 'good'
        elif value <= 4.0:
            return 'needs-improvement'
        else:
            return 'poor'
    
    def _get_fid_status(self, value: float) -> str:
        """Determine FID/TBT status based on thresholds"""
        if value <= 100:
            return 'good'
        elif value <= 300:
            return 'needs-improvement'
        else:
            return 'poor'
    
    def _get_cls_status(self, value: float) -> str:
        """Determine CLS status based on thresholds"""
        if value <= 0.1:
            return 'good'
        elif value <= 0.25:
            return 'needs-improvement'
        else:
            return 'poor'
    
    def _extract_field_data(self, loading_experience: Dict) -> Dict:
        """Extract field data from Chrome User Experience Report"""
        field_data = {
            'origin_summary': loading_experience.get('origin_fallback', False),
            'overall_category': loading_experience.get('overall_category', 'unknown'),
            'metrics': {}
        }
        
        metrics_data = loading_experience.get('metrics', {})
        
        # Extract each metric's field data
        for metric_key, metric_data in metrics_data.items():
            if 'percentile' in metric_data:
                field_data['metrics'][metric_key] = {
                    'p75': metric_data['percentile'],
                    'category': metric_data.get('category', 'unknown')
                }
        
        return field_data
    
    def _generate_recommendations(self, metrics: Dict) -> List[str]:
        """Generate recommendations based on CWV metrics"""
        recommendations = []
        
        # LCP recommendations
        lcp_status = metrics['lcp']['status']
        if lcp_status == 'poor':
            recommendations.extend([
                "Optimize largest content element loading (LCP > 4s)",
                "- Optimize server response times",
                "- Use a CDN for static assets",
                "- Optimize images with next-gen formats",
                "- Preload critical resources"
            ])
        elif lcp_status == 'needs-improvement':
            recommendations.append("Improve LCP (currently 2.5-4s) by optimizing images and server response")
        
        # FID/TBT recommendations
        fid_status = metrics['fid']['status']
        if fid_status == 'poor':
            recommendations.extend([
                "Reduce JavaScript execution time (High TBT indicates poor interactivity)",
                "- Break up long tasks",
                "- Minimize main thread work",
                "- Remove unused JavaScript",
                "- Use web workers for heavy computations"
            ])
        elif fid_status == 'needs-improvement':
            recommendations.append("Optimize JavaScript to improve interactivity (TBT: 100-300ms)")
        
        # CLS recommendations
        cls_status = metrics['cls']['status']
        if cls_status == 'poor':
            recommendations.extend([
                "Fix layout shifts (CLS > 0.25)",
                "- Add size attributes to images and videos",
                "- Reserve space for ad slots",
                "- Avoid inserting content above existing content",
                "- Use CSS transform for animations"
            ])
        elif cls_status == 'needs-improvement':
            recommendations.append("Reduce layout shifts (CLS: 0.1-0.25) by defining dimensions for media")
        
        return recommendations
    
    def analyze_bulk(self, urls: List[str], strategy: str = 'mobile') -> List[Dict]:
        """
        Analyze multiple URLs for Core Web Vitals
        
        Args:
            urls: List of URLs to analyze
            strategy: 'mobile' or 'desktop'
            
        Returns:
            List of analysis results
        """
        results = []
        
        for i, url in enumerate(urls):
            print(f"Analyzing {i+1}/{len(urls)}: {url}")
            
            # Analyze URL
            result = self.analyze(url, strategy)
            results.append(result)
            
            # Rate limiting (be respectful to the API)
            if i < len(urls) - 1:
                time.sleep(1)
        
        return results
    
    def compare_urls(self, urls: List[str], strategy: str = 'mobile') -> Dict:
        """
        Compare Core Web Vitals across multiple URLs
        
        Args:
            urls: List of URLs to compare
            strategy: 'mobile' or 'desktop'
            
        Returns:
            Comparison analysis with averages and rankings
        """
        # Analyze all URLs
        results = self.analyze_bulk(urls, strategy)
        
        # Prepare comparison data
        comparison = {
            'urls': urls,
            'strategy': strategy,
            'timestamp': datetime.now().isoformat(),
            'metrics_comparison': {},
            'rankings': {},
            'averages': {}
        }
        
        # Extract metrics for comparison
        metric_keys = ['lcp', 'fid', 'cls', 'fcp', 'ttfb']
        
        for metric in metric_keys:
            values = []
            url_metrics = []
            
            for i, result in enumerate(results):
                if result['status'] == 'completed' and metric in result['metrics']:
                    value = result['metrics'][metric]['value']
                    values.append(value)
                    url_metrics.append({
                        'url': urls[i],
                        'value': value,
                        'status': result['metrics'][metric]['status']
                    })
            
            # Calculate average
            if values:
                comparison['averages'][metric] = {
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'min': min(values),
                    'max': max(values)
                }
            
            # Rank URLs by metric (lower is better for all CWV)
            url_metrics.sort(key=lambda x: x['value'])
            comparison['rankings'][metric] = url_metrics
        
        return comparison
    
    def generate_report(self, results: Dict, format: str = 'text') -> str:
        """
        Generate a Core Web Vitals report
        
        Args:
            results: Analysis results
            format: 'text' or 'json'
            
        Returns:
            Formatted report
        """
        if format == 'json':
            return json.dumps(results, indent=2)
        
        # Text format
        lines = [
            "=" * 60,
            "CORE WEB VITALS REPORT",
            "=" * 60,
            f"URL: {results['url']}",
            f"Strategy: {results['strategy']}",
            f"Performance Score: {results['score']}%",
            f"Timestamp: {results['timestamp']}",
            "",
            "METRICS",
            "-" * 40
        ]
        
        # Add metrics
        metrics = results.get('metrics', {})
        
        # LCP
        if 'lcp' in metrics:
            lcp = metrics['lcp']
            lines.extend([
                f"Largest Contentful Paint (LCP): {lcp['value']:.2f}s",
                f"  Status: {lcp['status']}",
                f"  Score: {lcp['score']:.2f}",
                ""
            ])
        
        # FID/TBT
        if 'fid' in metrics:
            fid = metrics['fid']
            lines.extend([
                f"First Input Delay (TBT): {fid['value']}ms",
                f"  Status: {fid['status']}",
                f"  Score: {fid['score']:.2f}",
                ""
            ])
        
        # CLS
        if 'cls' in metrics:
            cls = metrics['cls']
            lines.extend([
                f"Cumulative Layout Shift (CLS): {cls['value']:.3f}",
                f"  Status: {cls['status']}",
                f"  Score: {cls['score']:.2f}",
                ""
            ])
        
        # Add recommendations
        if results.get('recommendations'):
            lines.extend([
                "RECOMMENDATIONS",
                "-" * 40
            ])
            for rec in results['recommendations']:
                lines.append(rec)
        
        # Add field data if available
        if 'field_data' in results:
            lines.extend([
                "",
                "FIELD DATA (Real User Metrics)",
                "-" * 40,
                f"Overall Category: {results['field_data']['overall_category']}"
            ])
        
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
        print("Usage: python core_web_vitals.py <url> [mobile|desktop]")
        sys.exit(1)
    
    url = sys.argv[1]
    strategy = sys.argv[2] if len(sys.argv) > 2 else 'mobile'
    
    analyzer = CoreWebVitals()
    print(f"Analyzing Core Web Vitals for {url} ({strategy})...")
    
    results = analyzer.analyze(url, strategy)
    print("\nResults:")
    print(analyzer.generate_report(results))
