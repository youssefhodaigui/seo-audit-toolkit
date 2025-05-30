# API Reference

Complete API documentation for the SEO Audit Toolkit modules.

## Table of Contents

- [Python Modules](#python-modules)
  - [TechnicalAuditor](#technicalauditor)
  - [CoreWebVitals](#corewebvitals)
  - [SchemaValidator](#schemavalidator)
  - [SitemapAnalyzer](#sitemapanalyzer)
  - [MobileChecker](#mobilechecker)
- [JavaScript Modules](#javascript-modules)
  - [SEOAuditToolkit](#seoaudittoolkit)
  - [PageSpeedAnalyzer](#pagespeedanalyzer)
  - [MetaExtractor](#metaextractor)
  - [StructuredDataParser](#structureddataparser)

---

## Python Modules

### TechnicalAuditor

Performs comprehensive technical SEO audits on websites.

```python
from seo_audit_toolkit import TechnicalAuditor

auditor = TechnicalAuditor()
```

#### Methods

##### `audit_website(url, checks=None)`

Run a comprehensive technical SEO audit on a website.

**Parameters:**
- `url` (str): The URL to audit
- `checks` (list, optional): Specific checks to run. If None, runs all checks.

**Returns:**
- `dict`: Audit results containing scores, issues, and recommendations

**Example:**
```python
results = auditor.audit_website("https://example.com")
print(f"Score: {results['score']}%")
```

##### `generate_report(results, format='json', output=None)`

Generate an audit report in the specified format.

**Parameters:**
- `results` (dict): Audit results from `audit_website()`
- `format` (str): Output format - 'json', 'html', or 'text'
- `output` (str, optional): File path to save the report

**Returns:**
- `str`: Formatted report

**Example:**
```python
html_report = auditor.generate_report(results, format='html')
```

---

### CoreWebVitals

Analyzes Core Web Vitals metrics using Google PageSpeed Insights API.

```python
from seo_audit_toolkit import CoreWebVitals

cwv = CoreWebVitals(api_key='your_api_key')  # API key optional
```

#### Methods

##### `analyze(url, strategy='mobile')`

Analyze Core Web Vitals for a URL.

**Parameters:**
- `url` (str): URL to analyze
- `strategy` (str): 'mobile' or 'desktop' (default: 'mobile')

**Returns:**
- `dict`: Contains metrics (LCP, FID, CLS), scores, and recommendations

**Example:**
```python
results = cwv.analyze("https://example.com", strategy='mobile')
print(f"LCP: {results['metrics']['lcp']['value']}s")
```

##### `analyze_bulk(urls, strategy='mobile')`

Analyze multiple URLs for Core Web Vitals.

**Parameters:**
- `urls` (list): List of URLs to analyze
- `strategy` (str): 'mobile' or 'desktop'

**Returns:**
- `list`: List of analysis results

##### `compare_urls(urls, strategy='mobile')`

Compare Core Web Vitals across multiple URLs.

**Parameters:**
- `urls` (list): URLs to compare
- `strategy` (str): 'mobile' or 'desktop'

**Returns:**
- `dict`: Comparison analysis with averages and rankings

---

### SchemaValidator

Validates structured data/schema markup implementation.

```python
from seo_audit_toolkit import SchemaValidator

validator = SchemaValidator()
```

#### Methods

##### `validate_url(url)`

Validate schema markup on a URL.

**Parameters:**
- `url` (str): URL to validate

**Returns:**
- `dict`: Validation results with errors, warnings, and found schemas

**Example:**
```python
results = validator.validate_url("https://example.com/product")
print(f"Schemas found: {results['schemas_found']}")
```

##### `validate_json(schema_json)`

Validate a JSON-LD schema string.

**Parameters:**
- `schema_json` (str): JSON-LD string to validate

**Returns:**
- `dict`: Validation results

**Example:**
```python
schema = '{"@context": "https://schema.org", "@type": "Product", "name": "Example"}'
results = validator.validate_json(schema)
```

---

### SitemapAnalyzer

Analyzes XML sitemaps for technical SEO issues.

```python
from seo_audit_toolkit import SitemapAnalyzer

analyzer = SitemapAnalyzer()
```

#### Methods

##### `analyze(sitemap_url, check_urls=False)`

Analyze an XML sitemap.

**Parameters:**
- `sitemap_url` (str): URL of the sitemap
- `check_urls` (bool): Whether to check if URLs are accessible

**Returns:**
- `dict`: Analysis results with stats, issues, and recommendations

**Example:**
```python
results = analyzer.analyze("https://example.com/sitemap.xml")
print(f"Total URLs: {results['urls_count']}")
```

##### `find_sitemaps(domain)`

Find all sitemaps for a domain.

**Parameters:**
- `domain` (str): Domain to check (e.g., 'example.com')

**Returns:**
- `list`: List of sitemap URLs found

**Example:**
```python
sitemaps = analyzer.find_sitemaps("example.com")
```

---

### MobileChecker

Checks mobile-friendliness and responsiveness of websites.

```python
from seo_audit_toolkit import MobileChecker

checker = MobileChecker()
```

#### Methods

##### `check_mobile_friendliness(url)`

Check mobile-friendliness of a URL.

**Parameters:**
- `url` (str): URL to check

**Returns:**
- `dict`: Mobile-friendliness analysis with score and issues

**Example:**
```python
results = checker.check_mobile_friendliness("https://example.com")
print(f"Mobile Friendly: {results['mobile_friendly']}")
```

---

## JavaScript Modules

### SEOAuditToolkit

Main class that orchestrates all SEO audit tools.

```javascript
const SEOAuditToolkit = require('seo-audit-toolkit');

const toolkit = new SEOAuditToolkit(options);
```

#### Constructor Options

- `timeout` (number): Request timeout in milliseconds (default: 30000)
- `retries` (number): Number of retries for failed requests (default: 3)
- `userAgent` (string): Custom user agent string

#### Methods

##### `audit(url, checks)`

Run a complete SEO audit on a URL.

**Parameters:**
- `url` (string): The URL to audit
- `checks` (array): Specific checks to run (optional)

**Returns:**
- `Promise<Object>`: Audit results

**Example:**
```javascript
const results = await toolkit.audit('https://example.com', ['pageSpeed', 'meta']);
console.log(`Score: ${results.score}%`);
```

##### `analyzePageSpeed(url, strategy)`

Analyze page speed for a URL.

**Parameters:**
- `url` (string): URL to analyze
- `strategy` (string): 'mobile' or 'desktop' (default: 'mobile')

**Returns:**
- `Promise<Object>`: Page speed results

##### `extractMeta(url)`

Extract meta tags from a URL.

**Parameters:**
- `url` (string): URL to analyze

**Returns:**
- `Promise<Object>`: Meta tag analysis

##### `parseStructuredData(url)`

Parse structured data from a URL.

**Parameters:**
- `url` (string): URL to analyze

**Returns:**
- `Promise<Object>`: Structured data analysis

##### `bulkAnalyze(urls, checks)`

Analyze multiple URLs.

**Parameters:**
- `urls` (array): Array of URLs to analyze
- `checks` (array): Checks to run (optional)

**Returns:**
- `Promise<Array>`: Array of results

##### `generateReport(results, format)`

Generate a report from audit results.

**Parameters:**
- `results` (object): Audit results
- `format` (string): 'json', 'html', or 'text'

**Returns:**
- `string`: Formatted report

---

### PageSpeedAnalyzer

Analyzes page performance using Google PageSpeed Insights API.

```javascript
const { PageSpeedAnalyzer } = require('seo-audit-toolkit');

const analyzer = new PageSpeedAnalyzer({ apiKey: 'your_api_key' });
```

#### Methods

##### `analyze(url, strategy)`

Analyze page speed for a URL.

**Parameters:**
- `url` (string): URL to analyze
- `strategy` (string): 'mobile' or 'desktop'

**Returns:**
- `Promise<Object>`: Analysis results with Core Web Vitals

**Example:**
```javascript
const results = await analyzer.analyze('https://example.com', 'mobile');
console.log(`LCP: ${results.metrics.lcp.displayValue}`);
```

##### `compareUrls(urls, strategy)`

Compare multiple URLs.

**Parameters:**
- `urls` (array): URLs to compare
- `strategy` (string): 'mobile' or 'desktop'

**Returns:**
- `Promise<Object>`: Comparison results

---

### MetaExtractor

Extracts and analyzes meta tags for SEO optimization.

```javascript
const { MetaExtractor } = require('seo-audit-toolkit');

const extractor = new MetaExtractor();
```

#### Methods

##### `extract(url)`

Extract meta tags from a URL.

**Parameters:**
- `url` (string): URL to analyze

**Returns:**
- `Promise<Object>`: Meta tag analysis with issues and recommendations

**Example:**
```javascript
const results = await extractor.extract('https://example.com');
console.log(`Title: ${results.meta.title.content}`);
```

##### `bulkExtract(urls)`

Extract meta tags from multiple URLs.

**Parameters:**
- `urls` (array): URLs to analyze

**Returns:**
- `Promise<Array>`: Array of results

##### `generateCSV(results)`

Generate CSV report from results.

**Parameters:**
- `results` (object|array): Extraction results

**Returns:**
- `string`: CSV formatted report

---

### StructuredDataParser

Parses and validates structured data (JSON-LD, Microdata, RDFa).

```javascript
const { StructuredDataParser } = require('seo-audit-toolkit');

const parser = new StructuredDataParser();
```

#### Methods

##### `parse(url)`

Parse structured data from a URL.

**Parameters:**
- `url` (string): URL to analyze

**Returns:**
- `Promise<Object>`: Structured data analysis with validation

**Example:**
```javascript
const results = await parser.parse('https://example.com');
console.log(`Schemas found: ${results.schemas.length}`);
```

---

## Common Response Formats

### Audit Result Object

```javascript
{
  url: "https://example.com",
  timestamp: "2024-01-15T10:30:00Z",
  score: 85,
  issues: {
    critical: 2,
    warnings: 5,
    passed: 15
  },
  checks: {
    // Individual check results
  },
  recommendations: [
    "Recommendation 1",
    "Recommendation 2"
  ]
}
```

### Error Response

```javascript
{
  status: "error",
  error: "Error message",
  url: "https://example.com",
  timestamp: "2024-01-15T10:30:00Z"
}
```

### Core Web Vitals Metrics

```javascript
{
  lcp: {
    value: 2500,          // milliseconds
    score: 0.9,
    displayValue: "2.5 s",
    status: "good"        // "good", "needs-improvement", or "poor"
  },
  fid: {
    value: 100,
    score: 0.95,
    displayValue: "100 ms",
    status: "good"
  },
  cls: {
    value: 0.1,
    score: 0.9,
    displayValue: "0.1",
    status: "good"
  }
}
```

## Status Codes and Error Handling

All methods may throw errors in the following cases:

- **Network Errors**: Connection timeouts, DNS failures
- **HTTP Errors**: 4xx or 5xx status codes
- **Parsing Errors**: Invalid HTML or JSON
- **API Errors**: Rate limiting, invalid API keys

Example error handling:

```python
try:
    results = auditor.audit_website("https://example.com")
except Exception as e:
    print(f"Audit failed: {str(e)}")
```

```javascript
try {
  const results = await toolkit.audit('https://example.com');
} catch (error) {
  console.error('Audit failed:', error.message);
}
```

## Rate Limiting

To avoid overwhelming servers:

- Default delay between requests: 1 second
- Configurable timeout: 10-30 seconds
- Respect robots.txt directives
- Use appropriate User-Agent headers

## Best Practices

1. **API Keys**: Store API keys in environment variables
2. **Error Handling**: Always wrap API calls in try-catch blocks
3. **Rate Limiting**: Add delays between bulk operations
4. **Caching**: Cache results when possible to reduce API calls
5. **Logging**: Log errors and important events for debugging

---

For more examples and use cases, see the [Usage Guide](usage-guide.md) and example scripts in the `/examples` directory.
