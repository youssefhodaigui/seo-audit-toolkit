/**
 * SEO Audit Toolkit - JavaScript Entry Point
 * 
 * Author: Youssef Hodaigui - Mindflow Marketing
 * Website: https://youssefhodaigui.com
 */

const PageSpeedAnalyzer = require('./pagespeed-analyzer');
const MetaExtractor = require('./meta-extractor');
const StructuredDataParser = require('./structured-data');

/**
 * SEO Audit Toolkit main class
 */
class SEOAuditToolkit {
  constructor(options = {}) {
    this.options = {
      timeout: 30000,
      retries: 3,
      userAgent: 'SEO-Audit-Toolkit/1.0 (Node.js)',
      ...options
    };
    
    // Initialize modules
    this.pageSpeed = new PageSpeedAnalyzer(this.options);
    this.metaExtractor = new MetaExtractor(this.options);
    this.structuredData = new StructuredDataParser(this.options);
  }

  /**
   * Run a complete SEO audit on a URL
   * @param {string} url - The URL to audit
   * @param {Array} checks - Specific checks to run (optional)
   * @returns {Promise<Object>} Audit results
   */
  async audit(url, checks = null) {
    const results = {
      url,
      timestamp: new Date().toISOString(),
      checks: {},
      score: 0,
      issues: {
        critical: 0,
        warnings: 0,
        passed: 0
      }
    };

    // Default checks if none specified
    const checksToRun = checks || [
      'pageSpeed',
      'meta',
      'structuredData'
    ];

    try {
      // Run each check
      for (const check of checksToRun) {
        switch (check) {
          case 'pageSpeed':
            results.checks.pageSpeed = await this.pageSpeed.analyze(url);
            break;
          case 'meta':
            results.checks.meta = await this.metaExtractor.extract(url);
            break;
          case 'structuredData':
            results.checks.structuredData = await this.structuredData.parse(url);
            break;
        }
      }

      // Calculate overall score and issues
      this._calculateScore(results);
      
    } catch (error) {
      results.error = error.message;
      results.status = 'error';
    }

    return results;
  }

  /**
   * Analyze page speed for a URL
   * @param {string} url - The URL to analyze
   * @param {string} strategy - 'mobile' or 'desktop'
   * @returns {Promise<Object>} Page speed results
   */
  async analyzePageSpeed(url, strategy = 'mobile') {
    return this.pageSpeed.analyze(url, strategy);
  }

  /**
   * Extract meta tags from a URL
   * @param {string} url - The URL to analyze
   * @returns {Promise<Object>} Meta tag analysis
   */
  async extractMeta(url) {
    return this.metaExtractor.extract(url);
  }

  /**
   * Parse structured data from a URL
   * @param {string} url - The URL to analyze
   * @returns {Promise<Object>} Structured data analysis
   */
  async parseStructuredData(url) {
    return this.structuredData.parse(url);
  }

  /**
   * Bulk analyze multiple URLs
   * @param {Array<string>} urls - Array of URLs to analyze
   * @param {Array} checks - Checks to run
   * @returns {Promise<Array>} Array of results
   */
  async bulkAnalyze(urls, checks = null) {
    const results = [];
    
    for (const url of urls) {
      console.log(`Analyzing ${url}...`);
      try {
        const result = await this.audit(url, checks);
        results.push(result);
      } catch (error) {
        results.push({
          url,
          error: error.message,
          status: 'error'
        });
      }
      
      // Rate limiting - be nice to servers
      await this._delay(1000);
    }
    
    return results;
  }

  /**
   * Generate a report from audit results
   * @param {Object} results - Audit results
   * @param {string} format - 'json', 'html', or 'text'
   * @returns {string} Formatted report
   */
  generateReport(results, format = 'json') {
    switch (format) {
      case 'json':
        return JSON.stringify(results, null, 2);
      
      case 'text':
        return this._generateTextReport(results);
      
      case 'html':
        return this._generateHTMLReport(results);
      
      default:
        throw new Error(`Unsupported format: ${format}`);
    }
  }

  /**
   * Calculate overall score from check results
   * @private
   */
  _calculateScore(results) {
    let totalScore = 0;
    let checkCount = 0;

    for (const [checkName, checkResult] of Object.entries(results.checks)) {
      if (checkResult.score !== undefined) {
        totalScore += checkResult.score;
        checkCount++;
      }

      // Count issues
      if (checkResult.issues) {
        results.issues.critical += checkResult.issues.critical || 0;
        results.issues.warnings += checkResult.issues.warnings || 0;
        results.issues.passed += checkResult.issues.passed || 0;
      }
    }

    results.score = checkCount > 0 ? Math.round(totalScore / checkCount) : 0;
  }

  /**
   * Generate text report
   * @private
   */
  _generateTextReport(results) {
    const lines = [
      '='.repeat(60),
      'SEO AUDIT REPORT',
      '='.repeat(60),
      `URL: ${results.url}`,
      `Score: ${results.score}%`,
      `Timestamp: ${results.timestamp}`,
      '',
      'SUMMARY',
      '-'.repeat(40),
      `Critical Issues: ${results.issues.critical}`,
      `Warnings: ${results.issues.warnings}`,
      `Passed: ${results.issues.passed}`,
      ''
    ];

    // Add check results
    for (const [checkName, checkResult] of Object.entries(results.checks)) {
      lines.push(checkName.toUpperCase());
      lines.push('-'.repeat(40));
      
      if (checkResult.score !== undefined) {
        lines.push(`Score: ${checkResult.score}%`);
      }
      
      if (checkResult.recommendations) {
        lines.push('Recommendations:');
        checkResult.recommendations.forEach(rec => {
          lines.push(`  - ${rec}`);
        });
      }
      
      lines.push('');
    }

    lines.push('='.repeat(60));
    lines.push('Report generated by SEO Audit Toolkit');
    lines.push('Created by Youssef Hodaigui - Mindflow Marketing');
    lines.push('https://youssefhodaigui.com');

    return lines.join('\n');
  }

  /**
   * Generate HTML report
   * @private
   */
  _generateHTMLReport(results) {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Audit Report - ${results.url}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .score {
            font-size: 48px;
            font-weight: bold;
            color: ${results.score >= 80 ? '#4caf50' : results.score >= 60 ? '#ff9800' : '#f44336'};
        }
        .section {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .issue-critical { color: #f44336; }
        .issue-warning { color: #ff9800; }
        .issue-passed { color: #4caf50; }
        h2 { color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .recommendation {
            background: #e3f2fd;
            padding: 10px;
            border-left: 4px solid #2196f3;
            margin: 10px 0;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>SEO Audit Report</h1>
        <p><strong>URL:</strong> <a href="${results.url}" target="_blank">${results.url}</a></p>
        <p><strong>Date:</strong> ${new Date(results.timestamp).toLocaleString()}</p>
        <div class="score">${results.score}%</div>
    </div>

    <div class="section">
        <h2>Summary</h2>
        <p class="issue-critical">Critical Issues: ${results.issues.critical}</p>
        <p class="issue-warning">Warnings: ${results.issues.warnings}</p>
        <p class="issue-passed">Passed: ${results.issues.passed}</p>
    </div>

    ${Object.entries(results.checks).map(([checkName, checkResult]) => `
        <div class="section">
            <h2>${checkName.charAt(0).toUpperCase() + checkName.slice(1)}</h2>
            ${checkResult.score !== undefined ? `<p><strong>Score:</strong> ${checkResult.score}%</p>` : ''}
            ${checkResult.recommendations ? `
                <h3>Recommendations</h3>
                ${checkResult.recommendations.map(rec => `
                    <div class="recommendation">${rec}</div>
                `).join('')}
            ` : ''}
        </div>
    `).join('')}

    <div class="footer">
        <p>Report generated by SEO Audit Toolkit</p>
        <p>Created by <a href="https://youssefhodaigui.com">Youssef Hodaigui</a> - 
           <a href="https://mindflowmarketing.com">Mindflow Marketing</a></p>
    </div>
</body>
</html>
    `;
  }

  /**
   * Delay helper for rate limiting
   * @private
   */
  _delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Export for use in Node.js
module.exports = SEOAuditToolkit;

// Also export individual modules
module.exports.PageSpeedAnalyzer = PageSpeedAnalyzer;
module.exports.MetaExtractor = MetaExtractor;
module.exports.StructuredDataParser = StructuredDataParser;

// CLI support
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node index.js <url> [format]');
    console.log('Format: json (default), text, or html');
    process.exit(1);
  }

  const url = args[0];
  const format = args[1] || 'json';
  
  const toolkit = new SEOAuditToolkit();
  
  console.log(`Running SEO audit for ${url}...`);
  
  toolkit.audit(url)
    .then(results => {
      const report = toolkit.generateReport(results, format);
      console.log(report);
    })
    .catch(error => {
      console.error('Error:', error.message);
      process.exit(1);
    });
}
