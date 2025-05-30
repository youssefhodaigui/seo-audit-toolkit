#!/usr/bin/env node
/**
 * Full Site SEO Scan Example
 * Demonstrates how to scan multiple pages of a website and generate a comprehensive report
 * 
 * Author: Youssef Hodaigui - Mindflow Marketing
 * Website: https://youssefhodaigui.com
 */

const path = require('path');
const fs = require('fs').promises;
const SEOAuditToolkit = require('../javascript/index');
const axios = require('axios');
const cheerio = require('cheerio');
const { URL } = require('url');
const chalk = require('chalk');
const ora = require('ora');

class FullSiteScan {
  constructor(options = {}) {
    this.toolkit = new SEOAuditToolkit(options);
    this.maxPages = options.maxPages || 10;
    this.visitedUrls = new Set();
    this.urlsToVisit = [];
    this.results = [];
    this.domain = '';
  }

  /**
   * Start scanning from a base URL
   * @param {string} baseUrl - The starting URL
   */
  async scan(baseUrl) {
    console.log(chalk.bold.blue('\n🔍 SEO Full Site Scan'));
    console.log('='.repeat(50));
    console.log(`Starting URL: ${baseUrl}`);
    console.log(`Max pages to scan: ${this.maxPages}`);
    console.log('='.repeat(50));

    try {
      // Parse base URL
      const urlObj = new URL(baseUrl);
      this.domain = urlObj.hostname;
      
      // Add base URL to queue
      this.urlsToVisit.push(baseUrl);
      
      // Start crawling
      while (this.urlsToVisit.length > 0 && this.visitedUrls.size < this.maxPages) {
        const url = this.urlsToVisit.shift();
        
        if (!this.visitedUrls.has(url)) {
          await this.scanPage(url);
          this.visitedUrls.add(url);
        }
      }

      // Generate summary report
      await this.generateReport();
      
    } catch (error) {
      console.error(chalk.red('\n❌ Scan failed:'), error.message);
      process.exit(1);
    }
  }

  /**
   * Scan individual page
   * @param {string} url - URL to scan
   */
  async scanPage(url) {
    const spinner = ora(`Scanning ${url}...`).start();
    
    try {
      // Run SEO audit
      const auditResult = await this.toolkit.audit(url, [
        'pageSpeed',
        'meta',
        'structuredData'
      ]);
      
      // Store results
      this.results.push(auditResult);
      
      // Extract links for crawling
      await this.extractLinks(url);
      
      spinner.succeed(`✅ Scanned ${url} (Score: ${auditResult.score}%)`);
      
      // Show immediate issues
      if (auditResult.issues.critical > 0) {
        console.log(chalk.red(`   Critical issues: ${auditResult.issues.critical}`));
      }
      if (auditResult.issues.warnings > 0) {
        console.log(chalk.yellow(`   Warnings: ${auditResult.issues.warnings}`));
      }
      
    } catch (error) {
      spinner.fail(`❌ Failed to scan ${url}: ${error.message}`);
    }
  }

  /**
   * Extract links from a page
   * @param {string} url - URL to extract links from
   */
  async extractLinks(url) {
    try {
      const response = await axios.get(url, {
        timeout: 10000,
        headers: {
          'User-Agent': 'SEO-Audit-Toolkit/1.0 (Site Scanner)'
        }
      });
      
      const $ = cheerio.load(response.data);
      const baseUrl = new URL(url);
      
      // Extract all links
      $('a[href]').each((i, elem) => {
        const href = $(elem).attr('href');
        
        if (href && !href.startsWith('#') && !href.startsWith('mailto:')) {
          try {
            const linkUrl = new URL(href, baseUrl);
            
            // Only follow internal links
            if (linkUrl.hostname === this.domain) {
              const cleanUrl = `${linkUrl.protocol}//${linkUrl.host}${linkUrl.pathname}`;
              
              if (!this.visitedUrls.has(cleanUrl) && 
                  !this.urlsToVisit.includes(cleanUrl) &&
                  this.visitedUrls.size + this.urlsToVisit.length < this.maxPages) {
                this.urlsToVisit.push(cleanUrl);
              }
            }
          } catch (e) {
            // Invalid URL, skip
          }
        }
      });
      
    } catch (error) {
      // Failed to extract links, continue
    }
  }

  /**
   * Generate comprehensive report
   */
  async generateReport() {
    console.log(chalk.bold.blue('\n📊 Scan Summary'));
    console.log('='.repeat(50));
    
    const summary = {
      totalPages: this.results.length,
      averageScore: 0,
      totalIssues: {
        critical: 0,
        warnings: 0,
        passed: 0
      },
      pagesByScore: {
        excellent: [], // 90-100
        good: [],      // 70-89
        needsWork: [], // 50-69
        poor: []       // 0-49
      },
      commonIssues: {},
      timestamp: new Date().toISOString()
    };

    // Calculate statistics
    let totalScore = 0;
    
    for (const result of this.results) {
      totalScore += result.score || 0;
      
      // Count issues
      summary.totalIssues.critical += result.issues.critical || 0;
      summary.totalIssues.warnings += result.issues.warnings || 0;
      summary.totalIssues.passed += result.issues.passed || 0;
      
      // Categorize by score
      const pageInfo = {
        url: result.url,
        score: result.score
      };
      
      if (result.score >= 90) {
        summary.pagesByScore.excellent.push(pageInfo);
      } else if (result.score >= 70) {
        summary.pagesByScore.good.push(pageInfo);
      } else if (result.score >= 50) {
        summary.pagesByScore.needsWork.push(pageInfo);
      } else {
        summary.pagesByScore.poor.push(pageInfo);
      }
      
      // Track common issues
      this.trackCommonIssues(result, summary.commonIssues);
    }

    summary.averageScore = Math.round(totalScore / summary.totalPages);

    // Display summary
    console.log(`Pages Scanned: ${summary.totalPages}`);
    console.log(`Average Score: ${summary.averageScore}%`);
    console.log(`\nTotal Issues Found:`);
    console.log(`  ${chalk.red('Critical:')} ${summary.totalIssues.critical}`);
    console.log(`  ${chalk.yellow('Warnings:')} ${summary.totalIssues.warnings}`);
    console.log(`  ${chalk.green('Passed:')} ${summary.totalIssues.passed}`);

    // Pages by score
    console.log(`\nPages by Score:`);
    console.log(`  ${chalk.green('Excellent (90-100):')} ${summary.pagesByScore.excellent.length}`);
    console.log(`  ${chalk.blue('Good (70-89):')} ${summary.pagesByScore.good.length}`);
    console.log(`  ${chalk.yellow('Needs Work (50-69):')} ${summary.pagesByScore.needsWork.length}`);
    console.log(`  ${chalk.red('Poor (0-49):')} ${summary.pagesByScore.poor.length}`);

    // Show worst performing pages
    if (summary.pagesByScore.poor.length > 0) {
      console.log(chalk.red('\n⚠️  Pages Needing Immediate Attention:'));
      summary.pagesByScore.poor.forEach(page => {
        console.log(`  - ${page.url} (Score: ${page.score}%)`);
      });
    }

    // Common issues
    console.log(chalk.bold('\n🔍 Most Common Issues:'));
    const sortedIssues = Object.entries(summary.commonIssues)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);
    
    sortedIssues.forEach(([issue, count]) => {
      console.log(`  - ${issue}: ${count} pages`);
    });

    // Save detailed results
    await this.saveResults(summary);
  }

  /**
   * Track common issues across pages
   */
  trackCommonIssues(result, commonIssues) {
    // Check meta issues
    if (result.checks.meta) {
      const meta = result.checks.meta;
      
      if (!meta.meta.title) {
        commonIssues['Missing page title'] = (commonIssues['Missing page title'] || 0) + 1;
      }
      if (!meta.meta.description) {
        commonIssues['Missing meta description'] = (commonIssues['Missing meta description'] || 0) + 1;
      }
      if (!meta.meta.viewport) {
        commonIssues['Missing viewport meta tag'] = (commonIssues['Missing viewport meta tag'] || 0) + 1;
      }
      if (meta.headings.h1.length === 0) {
        commonIssues['No H1 tag'] = (commonIssues['No H1 tag'] || 0) + 1;
      }
      if (meta.headings.h1.length > 1) {
        commonIssues['Multiple H1 tags'] = (commonIssues['Multiple H1 tags'] || 0) + 1;
      }
      if (meta.images.withoutAlt > 0) {
        commonIssues['Images without alt text'] = (commonIssues['Images without alt text'] || 0) + 1;
      }
    }

    // Check structured data issues
    if (result.checks.structuredData) {
      const sd = result.checks.structuredData;
      if (sd.schemas.length === 0) {
        commonIssues['No structured data'] = (commonIssues['No structured data'] || 0) + 1;
      }
    }

    // Check performance issues
    if (result.checks.pageSpeed) {
      const ps = result.checks.pageSpeed;
      if (ps.metrics.lcp && ps.metrics.lcp.status === 'poor') {
        commonIssues['Poor LCP (>4s)'] = (commonIssues['Poor LCP (>4s)'] || 0) + 1;
      }
      if (ps.metrics.cls && ps.metrics.cls.status === 'poor') {
        commonIssues['Poor CLS (>0.25)'] = (commonIssues['Poor CLS (>0.25)'] || 0) + 1;
      }
    }
  }

  /**
   * Save results to files
   */
  async saveResults(summary) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const domain = this.domain.replace(/\./g, '_');
    
    // Save JSON results
    const jsonFile = `site_scan_${domain}_${timestamp}.json`;
    const fullResults = {
      summary,
      pages: this.results,
      scanDate: new Date().toISOString(),
      domain: this.domain
    };
    
    await fs.writeFile(jsonFile, JSON.stringify(fullResults, null, 2));
    console.log(chalk.green(`\n✅ Detailed results saved to: ${jsonFile}`));

    // Generate HTML report
    const htmlFile = `site_scan_${domain}_${timestamp}.html`;
    const htmlContent = this.generateHTMLReport(fullResults);
    
    await fs.writeFile(htmlFile, htmlContent);
    console.log(chalk.green(`✅ HTML report saved to: ${htmlFile}`));

    // Generate CSV summary
    const csvFile = `site_scan_${domain}_${timestamp}.csv`;
    const csvContent = this.generateCSV(this.results);
    
    await fs.writeFile(csvFile, csvContent);
    console.log(chalk.green(`✅ CSV summary saved to: ${csvFile}`));
  }

  /**
   * Generate HTML report
   */
  generateHTMLReport(data) {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Site Scan Report - ${data.domain}</title>
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
            text-align: center;
        }
        .score-circle {
            display: inline-block;
            width: 120px;
            height: 120px;
            line-height: 120px;
            border-radius: 50%;
            font-size: 36px;
            font-weight: bold;
            color: white;
            background: ${data.summary.averageScore >= 70 ? '#4caf50' : data.summary.averageScore >= 50 ? '#ff9800' : '#f44336'};
            margin: 20px 0;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number {
            font-size: 32px;
            font-weight: bold;
            color: #2196f3;
        }
        .issues {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        .issue-critical { color: #f44336; }
        .issue-warning { color: #ff9800; }
        .issue-passed { color: #4caf50; }
        .pages-list {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        .page-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-score {
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 5px;
            color: white;
        }
        .score-excellent { background: #4caf50; }
        .score-good { background: #2196f3; }
        .score-needs-work { background: #ff9800; }
        .score-poor { background: #f44336; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #f5f5f5;
            font-weight: bold;
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
        <h1>SEO Site Scan Report</h1>
        <p><strong>Domain:</strong> ${data.domain}</p>
        <p><strong>Scan Date:</strong> ${new Date(data.scanDate).toLocaleString()}</p>
        <p><strong>Pages Scanned:</strong> ${data.summary.totalPages}</p>
        <div class="score-circle">${data.summary.averageScore}%</div>
        <p>Average SEO Score</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">${data.summary.totalPages}</div>
            <div>Pages Scanned</div>
        </div>
        <div class="stat-card">
            <div class="stat-number issue-critical">${data.summary.totalIssues.critical}</div>
            <div>Critical Issues</div>
        </div>
        <div class="stat-card">
            <div class="stat-number issue-warning">${data.summary.totalIssues.warnings}</div>
            <div>Warnings</div>
        </div>
        <div class="stat-card">
            <div class="stat-number issue-passed">${data.summary.totalIssues.passed}</div>
            <div>Passed Checks</div>
        </div>
    </div>

    <div class="issues">
        <h2>Most Common Issues</h2>
        <table>
            <thead>
                <tr>
                    <th>Issue</th>
                    <th>Pages Affected</th>
                    <th>Impact</th>
                </tr>
            </thead>
            <tbody>
                ${Object.entries(data.summary.commonIssues)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 10)
                    .map(([issue, count]) => `
                        <tr>
                            <td>${issue}</td>
                            <td>${count}</td>
                            <td>${count > data.summary.totalPages / 2 ? 'High' : 'Medium'}</td>
                        </tr>
                    `).join('')}
            </tbody>
        </table>
    </div>

    <div class="pages-list">
        <h2>Pages by Score</h2>
        
        ${data.summary.pagesByScore.poor.length > 0 ? `
            <h3>Poor Performance (0-49%)</h3>
            ${data.summary.pagesByScore.poor.map(page => `
                <div class="page-item">
                    <span>${page.url}</span>
                    <span class="page-score score-poor">${page.score}%</span>
                </div>
            `).join('')}
        ` : ''}

        ${data.summary.pagesByScore.needsWork.length > 0 ? `
            <h3>Needs Work (50-69%)</h3>
            ${data.summary.pagesByScore.needsWork.map(page => `
                <div class="page-item">
                    <span>${page.url}</span>
                    <span class="page-score score-needs-work">${page.score}%</span>
                </div>
            `).join('')}
        ` : ''}

        ${data.summary.pagesByScore.good.length > 0 ? `
            <h3>Good (70-89%)</h3>
            ${data.summary.pagesByScore.good.map(page => `
                <div class="page-item">
                    <span>${page.url}</span>
                    <span class="page-score score-good">${page.score}%</span>
                </div>
            `).join('')}
        ` : ''}

        ${data.summary.pagesByScore.excellent.length > 0 ? `
            <h3>Excellent (90-100%)</h3>
            ${data.summary.pagesByScore.excellent.map(page => `
                <div class="page-item">
                    <span>${page.url}</span>
                    <span class="page-score score-excellent">${page.score}%</span>
                </div>
            `).join('')}
        ` : ''}
    </div>

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
   * Generate CSV summary
   */
  generateCSV(results) {
    const rows = [
      ['URL', 'Score', 'Critical Issues', 'Warnings', 'Title', 'Description', 'H1 Count', 'Structured Data']
    ];

    results.forEach(result => {
      const meta = result.checks.meta || {};
      const sd = result.checks.structuredData || {};
      
      rows.push([
        result.url,
        result.score || 0,
        result.issues.critical || 0,
        result.issues.warnings || 0,
        meta.meta?.title?.content || 'Missing',
        meta.meta?.description?.content || 'Missing',
        meta.headings?.h1?.length || 0,
        sd.schemas?.length || 0
      ]);
    });

    return rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');
  }
}

// CLI execution
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node full-site-scan.js <url> [max-pages]');
    console.log('Example: node full-site-scan.js https://example.com 20');
    process.exit(1);
  }

  const url = args[0];
  const maxPages = parseInt(args[1]) || 10;

  const scanner = new FullSiteScan({ maxPages });
  
  try {
    await scanner.scan(url);
    console.log(chalk.green('\n✅ Site scan completed successfully!'));
  } catch (error) {
    console.error(chalk.red('❌ Scan failed:'), error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = FullSiteScan;
