#!/usr/bin/env python3
"""
Basic SEO Audit Example
Demonstrates how to use the SEO Audit Toolkit for a comprehensive website audit

Author: Youssef Hodaigui - Mindflow Marketing
Website: https://youssefhodaigui.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python import TechnicalAuditor, CoreWebVitals, SchemaValidator, SitemapAnalyzer, MobileChecker
import json
from datetime import datetime

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f" {title} ")
    print("="*60)

def run_comprehensive_audit(url):
    """
    Run a comprehensive SEO audit on a URL
    
    Args:
        url: The URL to audit
    """
    print(f"\nStarting comprehensive SEO audit for: {url}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize all audit modules
    technical_auditor = TechnicalAuditor()
    cwv_analyzer = CoreWebVitals()
    schema_validator = SchemaValidator()
    sitemap_analyzer = SitemapAnalyzer()
    mobile_checker = MobileChecker()
    
    # Overall results container
    audit_results = {
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'audits': {}
    }
    
    # 1. Technical SEO Audit
    print_section("Technical SEO Audit")
    print("Checking title, meta tags, headings, images, links...")
    
    technical_results = technical_auditor.audit_website(url)
    audit_results['audits']['technical'] = technical_results
    
    print(f"Overall Score: {technical_results.get('score', 0)}%")
    print(f"Issues Found:")
    print(f"  - Critical: {technical_results['issues']['critical']}")
    print(f"  - Warnings: {technical_results['issues']['warnings']}")
    print(f"  - Passed: {technical_results['issues']['passed']}")
    
    # 2. Core Web Vitals Analysis
    print_section("Core Web Vitals Analysis")
    print("Analyzing page performance metrics...")
    
    cwv_results = cwv_analyzer.analyze(url)
    audit_results['audits']['core_web_vitals'] = cwv_results
    
    if cwv_results['status'] == 'completed':
        metrics = cwv_results.get('metrics', {})
        print(f"Performance Score: {cwv_results.get('score', 0)}%")
        print(f"Core Web Vitals:")
        print(f"  - LCP: {metrics.get('lcp', {}).get('displayValue', 'N/A')} "
              f"({metrics.get('lcp', {}).get('status', 'unknown')})")
        print(f"  - FID: {metrics.get('fid', {}).get('displayValue', 'N/A')} "
              f"({metrics.get('fid', {}).get('status', 'unknown')})")
        print(f"  - CLS: {metrics.get('cls', {}).get('displayValue', 'N/A')} "
              f"({metrics.get('cls', {}).get('status', 'unknown')})")
    else:
        print(f"Error: {cwv_results.get('error', 'Unknown error')}")
    
    # 3. Schema Markup Validation
    print_section("Schema Markup Validation")
    print("Checking for structured data...")
    
    schema_results = schema_validator.validate_url(url)
    audit_results['audits']['schema'] = schema_results
    
    print(f"Validation Score: {schema_results.get('score', 0)}%")
    print(f"Schemas Found: {len(schema_results.get('schemas_found', []))}")
    
    if schema_results.get('schemas_found'):
        print("Schema Types:")
        for schema_type in schema_results['schemas_found']:
            print(f"  - {schema_type}")
    
    errors = len(schema_results.get('errors', []))
    warnings = len(schema_results.get('warnings', []))
    
    if errors > 0:
        print(f"\nErrors: {errors}")
        for error in schema_results['errors'][:3]:  # Show first 3
            print(f"  ❌ {error}")
            
    if warnings > 0:
        print(f"\nWarnings: {warnings}")
        for warning in schema_results['warnings'][:3]:  # Show first 3
            print(f"  ⚠️  {warning}")
    
    # 4. Sitemap Analysis
    print_section("Sitemap Analysis")
    print("Looking for XML sitemaps...")
    
    # Try to find sitemaps
    domain = url.split('/')[2]
    sitemaps = sitemap_analyzer.find_sitemaps(f"https://{domain}")
    
    if sitemaps:
        print(f"Found {len(sitemaps)} sitemap(s)")
        # Analyze the first sitemap found
        sitemap_url = sitemaps[0]
        print(f"Analyzing: {sitemap_url}")
        
        sitemap_results = sitemap_analyzer.analyze(sitemap_url)
        audit_results['audits']['sitemap'] = sitemap_results
        
        print(f"Type: {sitemap_results.get('type', 'unknown')}")
        print(f"URLs Found: {sitemap_results.get('urls_count', 0)}")
        
        issues = sitemap_results.get('issues', {})
        if issues.get('errors'):
            print(f"Errors: {len(issues['errors'])}")
        if issues.get('warnings'):
            print(f"Warnings: {len(issues['warnings'])}")
    else:
        print("No sitemaps found")
        audit_results['audits']['sitemap'] = {'status': 'not_found'}
    
    # 5. Mobile-Friendliness Check
    print_section("Mobile-Friendliness Check")
    print("Analyzing mobile usability...")
    
    mobile_results = mobile_checker.check_mobile_friendliness(url)
    audit_results['audits']['mobile'] = mobile_results
    
    print(f"Mobile Friendly: {'✅ Yes' if mobile_results['mobile_friendly'] else '❌ No'}")
    print(f"Score: {mobile_results.get('score', 0)}%")
    
    if mobile_results.get('issues'):
        print(f"\nCritical Issues: {len(mobile_results['issues'])}")
        for issue in mobile_results['issues'][:3]:  # Show first 3
            print(f"  ❌ {issue}")
    
    if mobile_results.get('warnings'):
        print(f"\nWarnings: {len(mobile_results['warnings'])}")
        for warning in mobile_results['warnings'][:3]:  # Show first 3
            print(f"  ⚠️  {warning}")
    
    # Generate Overall Summary
    print_section("Audit Summary")
    
    total_critical = 0
    total_warnings = 0
    
    for audit_name, audit_data in audit_results['audits'].items():
        if isinstance(audit_data, dict):
            # Count issues from different audit formats
            if 'issues' in audit_data:
                if isinstance(audit_data['issues'], dict):
                    total_critical += audit_data['issues'].get('critical', 0)
                    total_warnings += audit_data['issues'].get('warnings', 0)
                elif isinstance(audit_data['issues'], list):
                    total_critical += len(audit_data['issues'])
            
            if 'errors' in audit_data:
                total_critical += len(audit_data.get('errors', []))
            
            if 'warnings' in audit_data and isinstance(audit_data['warnings'], list):
                total_warnings += len(audit_data['warnings'])
    
    print(f"Total Critical Issues: {total_critical}")
    print(f"Total Warnings: {total_warnings}")
    
    # Calculate overall health score
    total_audits = len(audit_results['audits'])
    total_score = sum(
        audit.get('score', 0) 
        for audit in audit_results['audits'].values() 
        if isinstance(audit, dict) and 'score' in audit
    )
    
    scored_audits = sum(
        1 for audit in audit_results['audits'].values() 
        if isinstance(audit, dict) and 'score' in audit
    )
    
    if scored_audits > 0:
        overall_score = int(total_score / scored_audits)
        print(f"\nOverall SEO Health Score: {overall_score}%")
    
    # Top Recommendations
    print_section("Top Recommendations")
    
    recommendations = []
    
    # Gather recommendations from all audits
    for audit_name, audit_data in audit_results['audits'].items():
        if isinstance(audit_data, dict) and 'recommendations' in audit_data:
            recs = audit_data['recommendations']
            if isinstance(recs, list):
                recommendations.extend(recs[:2])  # Top 2 from each audit
    
    # Print unique recommendations
    unique_recommendations = []
    for rec in recommendations:
        if rec not in unique_recommendations:
            unique_recommendations.append(rec)
    
    for i, rec in enumerate(unique_recommendations[:10], 1):  # Top 10 overall
        print(f"{i}. {rec}")
    
    # Save results to file
    print_section("Saving Results")
    
    output_filename = f"seo_audit_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_filename, 'w') as f:
        json.dump(audit_results, f, indent=2)
    
    print(f"Full audit results saved to: {output_filename}")
    
    # Generate HTML report
    html_report = technical_auditor.generate_report(
        technical_results, 
        format='html'
    )
    
    html_filename = f"seo_audit_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    with open(html_filename, 'w') as f:
        f.write(html_report)
    
    print(f"HTML report saved to: {html_filename}")
    
    return audit_results

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python basic-audit.py <url>")
        print("Example: python basic-audit.py https://example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        results = run_comprehensive_audit(url)
        print("\n✅ Audit completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n❌ Audit interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\n❌ Error during audit: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
