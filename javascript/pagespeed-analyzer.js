/**
 * PageSpeed Analyzer Module
 * Analyzes page performance using Google PageSpeed Insights API
 * 
 * Author: Youssef Hodaigui - Mindflow Marketing
 * Website: https://youssefhodaigui.com
 */

const axios = require('axios');
const ora = require('ora');
const chalk = require('chalk');

class PageSpeedAnalyzer {
  constructor(options = {}) {
    this.apiKey = options.apiKey || process.env.PAGESPEED_API_KEY;
    this.apiUrl = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed';
    this.timeout = options.timeout || 30000;
  }

  /**
   * Analyze page speed for a URL
   * @param {string} url - URL to analyze
   * @param {string} strategy - 'mobile' or 'desktop'
   * @returns {Promise<Object>} Analysis results
   */
  async analyze(url, strategy = 'mobile') {
    const spinner = ora(`Analyzing ${strategy} performance for ${url}...`).start();
    
    const results = {
      url,
      strategy,
      timestamp: new Date().toISOString(),
      score: 0,
      metrics: {},
      opportunities: [],
      diagnostics: [],
      recommendations: [],
      issues: {
        critical: 0,
        warnings: 0,
        passed: 0
      }
    };

    try {
      // Build API request parameters
      const params = {
        url,
        strategy,
        category: ['performance', 'accessibility', 'best-practices', 'seo']
      };

      if (this.apiKey) {
        params.key = this.apiKey;
      }

      // Make API request
      const response = await axios.get(this.apiUrl, {
        params,
        timeout: this.timeout
      });

      spinner.succeed('Analysis complete');

      // Process results
      const data = response.data;
      
      if (data.lighthouseResult) {
        const lighthouse = data.lighthouseResult;
        
        // Extract score
        results.score = Math.round(
          lighthouse.categories.performance.score * 100
        );

        // Extract Core Web Vitals
        results.metrics = this._extractCoreWebVitals(lighthouse.audits);

        // Extract opportunities
        results.opportunities = this._extractOpportunities(lighthouse.audits);

        // Extract diagnostics
        results.diagnostics = this._extractDiagnostics(lighthouse.audits);

        // Generate recommendations
        results.recommendations = this._generateRecommendations(results);

        // Count issues
        this._countIssues(results);
      }

      // Add field data if available
      if (data.loadingExperience) {
        results.fieldData = this._extractFieldData(data.loadingExperience);
      }

    } catch (error) {
      spinner.fail('Analysis failed');
      results.error = error.message;
      results.status = 'error';
    }

    return results;
  }

  /**
   * Extract Core Web Vitals metrics
   * @private
   */
  _extractCoreWebVitals(audits) {
    const metrics = {
      lcp: this._extractMetric(audits['largest-contentful-paint']),
      fid: this._extractMetric(audits['max-potential-fid']),
      cls: this._extractMetric(audits['cumulative-layout-shift']),
      fcp: this._extractMetric(audits['first-contentful-paint']),
      ttfb: this._extractMetric(audits['server-response-time']),
      tti: this._extractMetric(audits['interactive']),
      tbt: this._extractMetric(audits['total-blocking-time']),
      speedIndex: this._extractMetric(audits['speed-index'])
    };

    // Add status for each metric
    metrics.lcp.status = this._getLCPStatus(metrics.lcp.value);
    metrics.fid.status = this._getFIDStatus(metrics.fid.value);
    metrics.cls.status = this._getCLSStatus(metrics.cls.value);

    return metrics;
  }

  /**
   * Extract a single metric
   * @private
   */
  _extractMetric(audit) {
    if (!audit) {
      return { value: 0, score: 0, displayValue: 'N/A' };
    }

    return {
      value: audit.numericValue || 0,
      score: audit.score || 0,
      displayValue: audit.displayValue || 'N/A'
    };
  }

  /**
   * Extract optimization opportunities
   * @private
   */
  _extractOpportunities(audits) {
    const opportunities = [];
    const opportunityAudits = [
      'render-blocking-resources',
      'unused-css',
      'unused-javascript',
      'modern-image-formats',
      'uses-optimized-images',
      'uses-text-compression',
      'uses-responsive-images',
      'efficient-animated-content',
      'duplicated-javascript',
      'legacy-javascript'
    ];

    for (const auditName of opportunityAudits) {
      const audit = audits[auditName];
      if (audit && audit.score < 0.9) {
        opportunities.push({
          id: auditName,
          title: audit.title,
          description: audit.description,
          score: audit.score,
          displayValue: audit.displayValue || '',
          savings: {
            bytes: audit.details?.overallSavingsBytes || 0,
            ms: audit.details?.overallSavingsMs || 0
          }
        });
      }
    }

    // Sort by potential impact
    opportunities.sort((a, b) => {
      const aImpact = (1 - a.score) * (a.savings.ms || 1000);
      const bImpact = (1 - b.score) * (b.savings.ms || 1000);
      return bImpact - aImpact;
    });

    return opportunities;
  }

  /**
   * Extract diagnostics
   * @private
   */
  _extractDiagnostics(audits) {
    const diagnostics = [];
    const diagnosticAudits = [
      'font-display',
      'uses-passive-event-listeners',
      'no-document-write',
      'dom-size',
      'critical-request-chains',
      'user-timings',
      'bootup-time',
      'mainthread-work-breakdown',
      'third-party-summary',
      'third-party-facades'
    ];

    for (const auditName of diagnosticAudits) {
      const audit = audits[auditName];
      if (audit && audit.score < 1) {
        diagnostics.push({
          id: auditName,
          title: audit.title,
          description: audit.description,
          score: audit.score,
          displayValue: audit.displayValue || ''
        });
      }
    }

    return diagnostics;
  }

  /**
   * Extract field data from Chrome User Experience Report
   * @private
   */
  _extractFieldData(loadingExperience) {
    return {
      id: loadingExperience.id,
      origin: loadingExperience.origin_fallback || false,
      overallCategory: loadingExperience.overall_category,
      metrics: {
        FIRST_CONTENTFUL_PAINT_MS: loadingExperience.metrics?.FIRST_CONTENTFUL_PAINT_MS,
        LARGEST_CONTENTFUL_PAINT_MS: loadingExperience.metrics?.LARGEST_CONTENTFUL_PAINT_MS,
        FIRST_INPUT_DELAY_MS: loadingExperience.metrics?.FIRST_INPUT_DELAY_MS,
        CUMULATIVE_LAYOUT_SHIFT_SCORE: loadingExperience.metrics?.CUMULATIVE_LAYOUT_SHIFT_SCORE
      }
    };
  }

  /**
   * Generate recommendations based on analysis
   * @private
   */
  _generateRecommendations(results) {
    const recommendations = [];

    // Core Web Vitals recommendations
    if (results.metrics.lcp.status === 'poor') {
      recommendations.push(
        'Improve Largest Contentful Paint (LCP) - currently over 4 seconds',
        '- Optimize server response times (TTFB)',
        '- Use a CDN for static assets',
        '- Optimize images with modern formats (WebP, AVIF)',
        '- Preload critical resources'
      );
    }

    if (results.metrics.fid.status === 'poor') {
      recommendations.push(
        'Reduce First Input Delay (FID) - high JavaScript execution time',
        '- Break up long JavaScript tasks',
        '- Use web workers for heavy computations',
        '- Reduce JavaScript bundle sizes',
        '- Implement code splitting'
      );
    }

    if (results.metrics.cls.status === 'poor') {
      recommendations.push(
        'Fix Cumulative Layout Shift (CLS) - currently over 0.25',
        '- Add size attributes to images and videos',
        '- Reserve space for ads and embeds',
        '- Avoid inserting content above existing content',
        '- Use CSS transforms instead of position changes'
      );
    }

    // Top opportunities
    const topOpportunities = results.opportunities.slice(0, 3);
    if (topOpportunities.length > 0) {
      recommendations.push('Top optimization opportunities:');
      topOpportunities.forEach(opp => {
        const savings = [];
        if (opp.savings.bytes > 0) {
          savings.push(`${Math.round(opp.savings.bytes / 1024)}KB`);
        }
        if (opp.savings.ms > 0) {
          savings.push(`${Math.round(opp.savings.ms)}ms`);
        }
        const savingsText = savings.length > 0 ? ` (save ${savings.join(', ')})` : '';
        recommendations.push(`- ${opp.title}${savingsText}`);
      });
    }

    return recommendations;
  }

  /**
   * Count issues by severity
   * @private
   */
  _countIssues(results) {
    // Count based on Core Web Vitals
    ['lcp', 'fid', 'cls'].forEach(metric => {
      const status = results.metrics[metric].status;
      if (status === 'poor') {
        results.issues.critical++;
      } else if (status === 'needs-improvement') {
        results.issues.warnings++;
      } else {
        results.issues.passed++;
      }
    });

    // Count opportunities as warnings
    results.issues.warnings += results.opportunities.length;

    // Count diagnostics as warnings
    results.issues.warnings += results.diagnostics.length;
  }

  /**
   * Get LCP status based on value
   * @private
   */
  _getLCPStatus(value) {
    const seconds = value / 1000;
    if (seconds <= 2.5) return 'good';
    if (seconds <= 4.0) return 'needs-improvement';
    return 'poor';
  }

  /**
   * Get FID status based on value
   * @private
   */
  _getFIDStatus(value) {
    if (value <= 100) return 'good';
    if (value <= 300) return 'needs-improvement';
    return 'poor';
  }

  /**
   * Get CLS status based on value
   * @private
   */
  _getCLSStatus(value) {
    if (value <= 0.1) return 'good';
    if (value <= 0.25) return 'needs-improvement';
    return 'poor';
  }

  /**
   * Compare multiple URLs
   * @param {Array<string>} urls - URLs to compare
   * @param {string} strategy - 'mobile' or 'desktop'
   * @returns {Promise<Object>} Comparison results
   */
  async compareUrls(urls, strategy = 'mobile') {
    console.log(chalk.blue(`Comparing ${urls.length} URLs...`));
    
    const results = [];
    
    for (const url of urls) {
      const result = await this.analyze(url, strategy);
      results.push(result);
      
      // Rate limiting
      if (urls.indexOf(url) < urls.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    // Generate comparison summary
    const comparison = {
      urls,
      strategy,
      timestamp: new Date().toISOString(),
      results,
      summary: this._generateComparisonSummary(results)
    };

    return comparison;
  }

  /**
   * Generate comparison summary
   * @private
   */
  _generateComparisonSummary(results) {
    const summary = {
      averageScore: 0,
      bestPerforming: null,
      worstPerforming: null,
      metrics: {}
    };

    // Calculate average score
    const scores = results.map(r => r.score).filter(s => s > 0);
    summary.averageScore = Math.round(
      scores.reduce((a, b) => a + b, 0) / scores.length
    );

    // Find best and worst
    const sorted = results
      .filter(r => !r.error)
      .sort((a, b) => b.score - a.score);
    
    if (sorted.length > 0) {
      summary.bestPerforming = {
        url: sorted[0].url,
        score: sorted[0].score
      };
      summary.worstPerforming = {
        url: sorted[sorted.length - 1].url,
        score: sorted[sorted.length - 1].score
      };
    }

    // Average metrics
    const metricNames = ['lcp', 'fid', 'cls'];
    metricNames.forEach(metric => {
      const values = results
        .filter(r => r.metrics && r.metrics[metric])
        .map(r => r.metrics[metric].value);
      
      if (values.length > 0) {
        summary.metrics[metric] = {
          average: values.reduce((a, b) => a + b, 0) / values.length,
          min: Math.min(...values),
          max: Math.max(...values)
        };
      }
    });

    return summary;
  }
}

module.exports = PageSpeedAnalyzer;

// CLI support
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node pagespeed-analyzer.js <url> [mobile|desktop]');
    process.exit(1);
  }

  const url = args[0];
  const strategy = args[1] || 'mobile';
  
  const analyzer = new PageSpeedAnalyzer();
  
  analyzer.analyze(url, strategy)
    .then(results => {
      console.log('\n' + chalk.bold('PageSpeed Analysis Results'));
      console.log('='.repeat(50));
      console.log(`URL: ${results.url}`);
      console.log(`Strategy: ${results.strategy}`);
      console.log(`Score: ${results.score}%`);
      console.log('\nCore Web Vitals:');
      console.log(`  LCP: ${results.metrics.lcp.displayValue} (${results.metrics.lcp.status})`);
      console.log(`  FID: ${results.metrics.fid.displayValue} (${results.metrics.fid.status})`);
      console.log(`  CLS: ${results.metrics.cls.displayValue} (${results.metrics.cls.status})`);
      
      if (results.recommendations.length > 0) {
        console.log('\nRecommendations:');
        results.recommendations.forEach(rec => console.log(rec));
      }
    })
    .catch(error => {
      console.error(chalk.red('Error:'), error.message);
      process.exit(1);
    });
}
