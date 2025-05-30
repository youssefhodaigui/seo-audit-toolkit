
# Usage Guide

Complete guide for using the SEO Audit Toolkit to perform technical SEO audits.

## Quick Start

### Basic Website Audit

```python
from seo_audit_toolkit import TechnicalAuditor

# Initialize the auditor
auditor = TechnicalAuditor()

# Run a basic audit
results = auditor.audit_website("https://example.com")

# Print results
print(results)
```

## Available Modules

### 1. Technical Auditor

The main module for comprehensive technical SEO audits.

```python
from seo_audit_toolkit import TechnicalAuditor

auditor = TechnicalAuditor()

# Full audit with all checks
results = auditor.audit_website(
    url="https://example.com",
    checks=[
        'title',
        'meta_description',
        'headings',
        'images',
        'schema',
        'core_web_vitals'
    ]
)

# Generate HTML report
auditor.generate_report(results, format='html', output='audit-report.html')
```

### 2. Core Web Vitals Analyzer

Analyze Core Web Vitals metrics for any URL.

```python
from seo_audit_toolkit import CoreWebVitals

cwv = CoreWebVitals()
metrics = cwv.analyze("https://example.com")

print(f"LCP: {metrics['lcp']}s")
print(f"FID: {metrics['fid']}ms")
print(f"CLS: {metrics['cls']}")
```

### 3. Schema Validator

Validate structured data implementation.

```python
from seo_audit_toolkit import SchemaValidator

validator = SchemaValidator()

# Check specific URL
errors = validator.validate_url("https://example.com/product")

# Validate schema string
schema_json = '{"@context": "https://schema.org", "@type": "Product"}'
is_valid = validator.validate_json(schema_json)
```

### 4. Sitemap Analyzer

Analyze XML sitemaps for issues.

```python
from seo_audit_toolkit import SitemapAnalyzer

analyzer = SitemapAnalyzer()

# Analyze sitemap
report = analyzer.analyze("https://example.com/sitemap.xml")

print(f"Total URLs: {report['total_urls']}")
print(f"Valid URLs: {report['valid_urls']}")
print(f"Errors: {report['errors']}")
```

## Command Line Usage

### Basic Audit

```bash
# Run basic audit
python -m seo_audit_toolkit audit https://example.com

# Save results to file
python -m seo_audit_toolkit audit https://example.com --output results.json

# Generate HTML report
python -m seo_audit_toolkit audit https://example.com --format html
```

### Specific Checks

```bash
# Check only Core Web Vitals
python -m seo_audit_toolkit cwv https://example.com

# Validate schema
python -m seo_audit_toolkit schema https://example.com/product

# Analyze sitemap
python -m seo_audit_toolkit sitemap https://example.com/sitemap.xml
```

## Advanced Usage

### Bulk URL Auditing

```python
from seo_audit_toolkit import BulkAuditor

# Audit multiple URLs
urls = [
    "https://example.com",
    "https://example.com/about",
    "https://example.com/products"
]

auditor = BulkAuditor()
results = auditor.audit_urls(urls, parallel=True, max_workers=5)

# Export to CSV
auditor.export_csv(results, "bulk-audit-results.csv")
```

### Custom Rules

```python
from seo_audit_toolkit import CustomRuleEngine

# Create custom rules
rules = CustomRuleEngine()

# Add title rules
rules.add_rule("title_length", min=30, max=60)
rules.add_rule("title_keyword", must_contain=["SEO", "Marketing"])

# Add meta description rules
rules.add_rule("meta_description_length", min=120, max=160)

# Apply rules
violations = rules.check_url("https://example.com")
```

### Scheduled Monitoring

```python
from seo_audit_toolkit import SEOMonitor

# Set up monitoring
monitor = SEOMonitor()

# Add URLs to monitor
monitor.add_url("https://example.com", checks=['cwv', 'technical'])

# Run monitoring (saves results to database)
monitor.run_checks()

# Get historical data
history = monitor.get_history("https://example.com", days=30)
```

## Output Formats

### JSON Output

```json
{
  "url": "https://example.com",
  "timestamp": "2024-01-15T10:30:00Z",
  "overall_score": 85,
  "issues": {
    "critical": 1,
    "warnings": 3,
    "passed": 15
  }
}
```

### HTML Report

The HTML report includes:
- Executive summary
- Detailed findings
- Recommendations
- Technical details
- Export options

### CSV Export

Perfect for bulk audits and data analysis:
- One row per URL
- All metrics in columns
- Easy to import into spreadsheets

## Best Practices

1. **Run Regular Audits**: Schedule weekly or monthly audits
2. **Monitor Trends**: Track improvements over time
3. **Prioritize Issues**: Focus on critical issues first
4. **Benchmark Competitors**: Compare your metrics
5. **Document Changes**: Keep audit history

## Troubleshooting

### Common Issues

**Error: "Connection timeout"**
- Increase timeout: `auditor.timeout = 30`

**Error: "JavaScript required"**
- Use headless browser mode: `auditor.use_browser = True`

**Error: "Rate limited"**
- Add delays: `auditor.delay_between_requests = 2`

## Need Help?

- 📚 [API Reference](api-reference.md)
- 🐛 [Report Issues](https://github.com/youssefhodaigui/seo-audit-toolkit/issues)
- 💬 [Discussions](https://github.com/youssefhodaigui/seo-audit-toolkit/discussions)
- 📧 Contact: youssef@mindflowmarketing.com

