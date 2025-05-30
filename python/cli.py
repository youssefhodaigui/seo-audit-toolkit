#!/usr/bin/env python3
"""
SEO Audit Toolkit CLI
Command-line interface for running SEO audits

Author: Youssef Hodaigui - Mindflow Marketing
Website: https://youssefhodaigui.com
"""

import argparse
import sys
import json
import csv
from datetime import datetime
from typing import List, Dict, Any

from .technical_audit import TechnicalAuditor
from .core_web_vitals import CoreWebVitals
from .schema_validator import SchemaValidator
from .sitemap_analyzer import SitemapAnalyzer
from .mobile_checker import MobileChecker


class SEOAuditCLI:
    """Command-line interface for SEO Audit Toolkit"""
    
    def __init__(self):
        """Initialize CLI"""
        self.parser = self._create_parser()
        
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            prog='seo-audit',
            description='SEO Audit Toolkit - Comprehensive technical SEO analysis',
            epilog='Created by Youssef Hodaigui - Mindflow Marketing (https://mindflowmarketing.com)'
        )
        
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s 1.0.0'
        )
        
        # Create subparsers for different commands
        subparsers = parser.add_subparsers(
            dest='command',
            help='Available commands'
        )
        
        # Full audit command
        audit_parser = subparsers.add_parser(
            'audit',
            help='Run a comprehensive SEO audit'
        )
        audit_parser.add_argument(
            'url',
            help='URL to audit'
        )
        audit_parser.add_argument(
            '--output',
            '-o',
            choices=['json', 'html', 'text', 'csv'],
            default='text',
            help='Output format (default: text)'
        )
        audit_parser.add_argument(
            '--save',
            '-s',
            help='Save output to file'
        )
        audit_parser.add_argument(
            '--checks',
            nargs='+',
            choices=['technical', 'cwv', 'schema', 'sitemap', 'mobile'],
            help='Specific checks to run (default: all)'
        )
        
        # Technical audit command
        tech_parser = subparsers.add_parser(
            'technical',
            help='Run technical SEO audit'
        )
        tech_parser.add_argument('url', help='URL to audit')
        tech_parser.add_argument('--output', '-o', choices=['json', 'html', 'text'], default='text')
        tech_parser.add_argument('--save', '-s', help='Save output to file')
        
        # Core Web Vitals command
        cwv_parser = subparsers.add_parser(
            'cwv',
            help='Analyze Core Web Vitals'
        )
        cwv_parser.add_argument('url', help='URL to analyze')
        cwv_parser.add_argument(
            '--strategy',
            choices=['mobile', 'desktop'],
            default='mobile',
            help='Analysis strategy (default: mobile)'
        )
        cwv_parser.add_argument('--api-key', help='PageSpeed Insights API key')
        cwv_parser.add_argument('--output', '-o', choices=['json', 'text'], default='text')
        cwv_parser.add_argument('--save', '-s', help='Save output to file')
        
        # Schema validation command
        schema_parser = subparsers.add_parser(
            'schema',
            help='Validate structured data'
        )
        schema_parser.add_argument('url', help='URL to validate')
        schema_parser.add_argument('--output', '-o', choices=['json', 'text'], default='text')
        schema_parser.add_argument('--save', '-s', help='Save output to file')
        
        # Sitemap analysis command
        sitemap_parser = subparsers.add_parser(
            'sitemap',
            help='Analyze XML sitemap'
        )
        sitemap_parser.add_argument('url', help='Sitemap URL or domain to find sitemaps')
        sitemap_parser.add_argument('--find', action='store_true', help='Find all sitemaps for domain')
        sitemap_parser.add_argument('--check-urls', action='store_true', help='Check if URLs are accessible')
        sitemap_parser.add_argument('--output', '-o', choices=['json', 'text'], default='text')
        sitemap_parser.add_argument('--save', '-s', help='Save output to file')
        
        # Mobile-friendliness command
        mobile_parser = subparsers.add_parser(
            'mobile',
            help='Check mobile-friendliness'
        )
        mobile_parser.add_argument('url', help='URL to check')
        mobile_parser.add_argument('--output', '-o', choices=['json', 'text'], default='text')
        mobile_parser.add_argument('--save', '-s', help='Save output to file')
        
        # Bulk analysis command
        bulk_parser = subparsers.add_parser(
            'bulk',
            help='Analyze multiple URLs from file'
        )
        bulk_parser.add_argument(
            'file',
            help='File containing URLs (one per line)'
        )
        bulk_parser.add_argument(
            '--checks',
            nargs='+',
            choices=['technical', 'cwv', 'schema', 'mobile'],
            default=['technical'],
            help='Checks to run (default: technical)'
        )
        bulk_parser.add_argument('--output', '-o', choices=['csv', 'json'], default='csv')
        bulk_parser.add_argument('--save', '-s', help='Save output to file', required=True)
        
        return parser
    
    def run(self, args: List[str] = None) -> int:
        """Run the CLI"""
        args = self.parser.parse_args(args)
        
        if not args.command:
            self.parser.print_help()
            return 1
        
        try:
            if args.command == 'audit':
                return self._run_full_audit(args)
            elif args.command == 'technical':
                return self._run_technical_audit(args)
            elif args.command == 'cwv':
                return self._run_cwv_analysis(args)
            elif args.command == 'schema':
                return self._run_schema_validation(args)
            elif args.command == 'sitemap':
                return self._run_sitemap_analysis(args)
            elif args.command == 'mobile':
                return self._run_mobile_check(args)
            elif args.command == 'bulk':
                return self._run_bulk_analysis(args)
            else:
                self.parser.print_help()
                return 1
                
        except KeyboardInterrupt:
            print("\n\nAnalysis interrupted by user")
            return 1
        except Exception as e:
            print(f"\nError: {str(e)}", file=sys.stderr)
            return 1
    
    def _run_full_audit(self, args) -> int:
        """Run comprehensive SEO audit"""
        print(f"\n🔍 Running comprehensive SEO audit for: {args.url}")
        print("=" * 60)
        
        results = {
            'url': args.url,
            'timestamp': datetime.now().isoformat(),
            'audits': {}
        }
        
        # Determine which checks to run
        checks = args.checks or ['technical', 'cwv', 'schema', 'sitemap', 'mobile']
        
        # Run selected audits
        if 'technical' in checks:
            print("\n📋 Technical SEO Audit...")
            auditor = TechnicalAuditor()
            results['audits']['technical'] = auditor.audit_website(args.url)
        
        if 'cwv' in checks:
            print("\n⚡ Core Web Vitals Analysis...")
            cwv = CoreWebVitals()
            results['audits']['cwv'] = cwv.analyze(args.url)
        
        if 'schema' in checks:
            print("\n📊 Schema Validation...")
            validator = SchemaValidator()
            results['audits']['schema'] = validator.validate_url(args.url)
        
        if 'sitemap' in checks:
            print("\n🗺️  Sitemap Analysis...")
            analyzer = SitemapAnalyzer()
            # Try to find sitemap
            domain = args.url.split('/')[2]
            sitemaps = analyzer.find_sitemaps(f"https://{domain}")
            if sitemaps:
                results['audits']['sitemap'] = analyzer.analyze(sitemaps[0])
            else:
                results['audits']['sitemap'] = {'status': 'not_found', 'message': 'No sitemap found'}
        
        if 'mobile' in checks:
            print("\n📱 Mobile-Friendliness Check...")
            checker = MobileChecker()
            results['audits']['mobile'] = checker.check_mobile_friendliness(args.url)
        
        # Format and output results
        output = self._format_full_audit_results(results, args.output)
        
        if args.save:
            self._save_output(output, args.save)
            print(f"\n✅ Results saved to: {args.save}")
        else:
            print(output)
        
        return 0
    
    def _run_technical_audit(self, args) -> int:
        """Run technical SEO audit"""
        print(f"\n📋 Running technical SEO audit for: {args.url}")
        
        auditor = TechnicalAuditor()
        results = auditor.audit_website(args.url)
        
        # Format output
        if args.output == 'json':
            output = json.dumps(results, indent=2)
        elif args.output == 'html':
            output = auditor.generate_report(results, format='html')
        else:
            output = auditor.generate_report(results, format='text')
        
        if args.save:
            self._save_output(output, args.save)
            print(f"\n✅ Results saved to: {args.save}")
        else:
            print(output)
        
        return 0
    
    def _run_cwv_analysis(self, args) -> int:
        """Run Core Web Vitals analysis"""
        print(f"\n⚡ Analyzing Core Web Vitals for: {args.url} ({args.strategy})")
        
        cwv = CoreWebVitals(api_key=args.api_key)
        results = cwv.analyze(args.url, strategy=args.strategy)
        
        # Format output
        if args.output == 'json':
            output = json.dumps(results, indent=2)
        else:
            output = cwv.generate_report(results, format='text')
        
        if args.save:
            self._save_output(output, args.save)
            print(f"\n✅ Results saved to: {args.save}")
        else:
            print(output)
        
        return 0
    
    def _run_schema_validation(self, args) -> int:
        """Run schema validation"""
        print(f"\n📊 Validating structured data for: {args.url}")
        
        validator = SchemaValidator()
        results = validator.validate_url(args.url)
        
        # Format output
        if args.output == 'json':
            output = json.dumps(results, indent=2)
        else:
            output = validator.generate_report(results)
        
        if args.save:
            self._save_output(output, args.save)
            print(f"\n✅ Results saved to: {args.save}")
        else:
            print(output)
        
        return 0
    
    def _run_sitemap_analysis(self, args) -> int:
        """Run sitemap analysis"""
        analyzer = SitemapAnalyzer()
        
        if args.find:
            print(f"\n🔍 Finding sitemaps for: {args.url}")
            sitemaps = analyzer.find_sitemaps(args.url)
            
            if sitemaps:
                print(f"\nFound {len(sitemaps)} sitemap(s):")
                for sitemap in sitemaps:
                    print(f"  - {sitemap}")
            else:
                print("No sitemaps found")
            
            return 0
        
        print(f"\n🗺️  Analyzing sitemap: {args.url}")
        results = analyzer.analyze(args.url, check_urls=args.check_urls)
        
        # Format output
        if args.output == 'json':
            output = json.dumps(results, indent=2)
        else:
            output = analyzer.generate_report(results)
        
        if args.save:
            self._save_output(output, args.save)
            print(f"\n✅ Results saved to: {args.save}")
        else:
            print(output)
        
        return 0
    
    def _run_mobile_check(self, args) -> int:
        """Run mobile-friendliness check"""
        print(f"\n📱 Checking mobile-friendliness for: {args.url}")
        
        checker = MobileChecker()
        results = checker.check_mobile_friendliness(args.url)
        
        # Format output
        if args.output == 'json':
            output = json.dumps(results, indent=2)
        else:
            output = checker.generate_report(results)
        
        if args.save:
            self._save_output(output, args.save)
            print(f"\n✅ Results saved to: {args.save}")
        else:
            print(output)
        
        return 0
    
    def _run_bulk_analysis(self, args) -> int:
        """Run bulk URL analysis"""
        print(f"\n📦 Running bulk analysis from: {args.file}")
        
        # Read URLs from file
        try:
            with open(args.file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found", file=sys.stderr)
            return 1
        
        print(f"Found {len(urls)} URLs to analyze")
        
        results = []
        
        # Run selected checks for each URL
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Analyzing: {url}")
            
            url_results = {
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
            
            try:
                if 'technical' in args.checks:
                    auditor = TechnicalAuditor()
                    url_results['technical'] = auditor.audit_website(url)
                
                if 'cwv' in args.checks:
                    cwv = CoreWebVitals()
                    url_results['cwv'] = cwv.analyze(url)
                
                if 'schema' in args.checks:
                    validator = SchemaValidator()
                    url_results['schema'] = validator.validate_url(url)
                
                if 'mobile' in args.checks:
                    checker = MobileChecker()
                    url_results['mobile'] = checker.check_mobile_friendliness(url)
                
                results.append(url_results)
                
            except Exception as e:
                url_results['error'] = str(e)
                results.append(url_results)
        
        # Format output
        if args.output == 'csv':
            output = self._format_bulk_csv(results, args.checks)
        else:
            output = json.dumps(results, indent=2)
        
        self._save_output(output, args.save)
        print(f"\n✅ Results saved to: {args.save}")
        
        return 0
    
    def _format_full_audit_results(self, results: Dict[str, Any], format: str) -> str:
        """Format full audit results"""
        if format == 'json':
            return json.dumps(results, indent=2)
        
        elif format == 'csv':
            # Create CSV summary
            rows = [['Check', 'Score', 'Critical Issues', 'Warnings', 'Status']]
            
            for check_name, check_data in results['audits'].items():
                if isinstance(check_data, dict):
                    score = check_data.get('score', 'N/A')
                    
                    # Count issues
                    critical = 0
                    warnings = 0
                    
                    if 'issues' in check_data:
                        if isinstance(check_data['issues'], dict):
                            critical = check_data['issues'].get('critical', 0)
                            warnings = check_data['issues'].get('warnings', 0)
                    
                    if 'errors' in check_data:
                        critical += len(check_data.get('errors', []))
                    
                    if 'warnings' in check_data:
                        warnings += len(check_data.get('warnings', []))
                    
                    status = check_data.get('status', 'unknown')
                    
                    rows.append([check_name, score, critical, warnings, status])
            
            output = []
            for row in rows:
                output.append(','.join(str(cell) for cell in row))
            
            return '\n'.join(output)
        
        elif format == 'html':
            # Generate HTML report
            auditor = TechnicalAuditor()
            # Use technical auditor's HTML generation as base
            if 'technical' in results['audits']:
                return auditor.generate_report(results['audits']['technical'], format='html')
            else:
                return self._generate_summary_html(results)
        
        else:  # text format
            lines = [
                "=" * 60,
                "COMPREHENSIVE SEO AUDIT REPORT",
                "=" * 60,
                f"URL: {results['url']}",
                f"Timestamp: {results['timestamp']}",
                "",
                "SUMMARY",
                "-" * 40
            ]
            
            for check_name, check_data in results['audits'].items():
                if isinstance(check_data, dict):
                    lines.append(f"\n{check_name.upper()}")
                    
                    if 'score' in check_data:
                        lines.append(f"  Score: {check_data['score']}%")
                    
                    if 'status' in check_data:
                        lines.append(f"  Status: {check_data['status']}")
                    
                    # Count issues
                    if 'issues' in check_data or 'errors' in check_data:
                        critical = 0
                        warnings = 0
                        
                        if isinstance(check_data.get('issues'), dict):
                            critical += check_data['issues'].get('critical', 0)
                            warnings += check_data['issues'].get('warnings', 0)
                        
                        if 'errors' in check_data:
                            critical += len(check_data.get('errors', []))
                        
                        if 'warnings' in check_data:
                            warnings += len(check_data.get('warnings', []))
                        
                        if critical > 0:
                            lines.append(f"  Critical Issues: {critical}")
                        if warnings > 0:
                            lines.append(f"  Warnings: {warnings}")
            
            lines.extend([
                "",
                "=" * 60,
                "Report generated by SEO Audit Toolkit",
                "Created by Youssef Hodaigui - Mindflow Marketing",
                "https://youssefhodaigui.com"
            ])
            
            return '\n'.join(lines)
    
    def _format_bulk_csv(self, results: List[Dict], checks: List[str]) -> str:
        """Format bulk analysis results as CSV"""
        headers = ['URL', 'Timestamp']
        
        # Add headers based on checks
        if 'technical' in checks:
            headers.extend(['Technical Score', 'Technical Issues', 'Technical Warnings'])
        if 'cwv' in checks:
            headers.extend(['CWV Score', 'LCP', 'FID', 'CLS'])
        if 'schema' in checks:
            headers.extend(['Schema Score', 'Schemas Found', 'Schema Errors'])
        if 'mobile' in checks:
            headers.extend(['Mobile Score', 'Mobile Friendly'])
        
        headers.append('Error')
        
        # Create CSV writer
        rows = [headers]
        
        for result in results:
            row = [result['url'], result['timestamp']]
            
            if 'technical' in checks:
                if 'technical' in result:
                    tech = result['technical']
                    row.extend([
                        tech.get('score', ''),
                        tech.get('issues', {}).get('critical', ''),
                        tech.get('issues', {}).get('warnings', '')
                    ])
                else:
                    row.extend(['', '', ''])
            
            if 'cwv' in checks:
                if 'cwv' in result:
                    cwv = result['cwv']
                    metrics = cwv.get('metrics', {})
                    row.extend([
                        cwv.get('score', ''),
                        metrics.get('lcp', {}).get('value', ''),
                        metrics.get('fid', {}).get('value', ''),
                        metrics.get('cls', {}).get('value', '')
                    ])
                else:
                    row.extend(['', '', '', ''])
            
            if 'schema' in checks:
                if 'schema' in result:
                    schema = result['schema']
                    row.extend([
                        schema.get('score', ''),
                        len(schema.get('schemas_found', [])),
                        len(schema.get('errors', []))
                    ])
                else:
                    row.extend(['', '', ''])
            
            if 'mobile' in checks:
                if 'mobile' in result:
                    mobile = result['mobile']
                    row.extend([
                        mobile.get('score', ''),
                        'Yes' if mobile.get('mobile_friendly') else 'No'
                    ])
                else:
                    row.extend(['', ''])
            
            row.append(result.get('error', ''))
            rows.append(row)
        
        # Convert to CSV string
        output = []
        for row in rows:
            output.append(','.join(f'"{str(cell)}"' for cell in row))
        
        return '\n'.join(output)
    
    def _generate_summary_html(self, results: Dict) -> str:
        """Generate summary HTML report"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Audit Report - {results['url']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f0f0f0; padding: 20px; }}
        .score {{ font-size: 48px; color: #333; }}
        .check {{ margin: 20px 0; padding: 20px; background: #f9f9f9; }}
        .issue-critical {{ color: #d32f2f; }}
        .issue-warning {{ color: #f57c00; }}
        .footer {{ margin-top: 40px; text-align: center; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SEO Audit Report</h1>
        <p>URL: <a href="{results['url']}">{results['url']}</a></p>
        <p>Date: {results['timestamp']}</p>
    </div>
    
    {"".join(f'<div class="check"><h2>{check}</h2><pre>{json.dumps(data, indent=2)}</pre></div>' 
             for check, data in results['audits'].items())}
    
    <div class="footer">
        <p>Report generated by SEO Audit Toolkit</p>
        <p>Created by <a href="https://youssefhodaigui.com">Youssef Hodaigui</a> - 
           <a href="https://mindflowmarketing.com">Mindflow Marketing</a></p>
    </div>
</body>
</html>
        """
    
    def _save_output(self, output: str, filename: str):
        """Save output to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(output)


def main():
    """Main entry point"""
    cli = SEOAuditCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
