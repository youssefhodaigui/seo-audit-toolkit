/**
 * Meta Tag Extractor Module
 * Extracts and analyzes meta tags for SEO optimization
 * 
 * Author: Youssef Hodaigui - Mindflow Marketing
 * Website: https://youssefhodaigui.com
 */

const axios = require('axios');
const cheerio = require('cheerio');
const { URL } = require('url');

class MetaExtractor {
  constructor(options = {}) {
    this.timeout = options.timeout || 10000;
    this.userAgent = options.userAgent || 'SEO-Audit-Toolkit/1.0 (Meta Extractor)';
    this.followRedirects = options.followRedirects !== false;
  }

  /**
   * Extract meta tags from a URL
   * @param {string} url - URL to analyze
   * @returns {Promise<Object>} Meta tag analysis
   */
  async extract(url) {
    const results = {
      url,
      timestamp: new Date().toISOString(),
      status: 'completed',
      meta: {
        title: null,
        description: null,
        keywords: null,
        robots: null,
        canonical: null,
        viewport: null,
        charset: null,
        'og:title': null,
        'og:description': null,
        'og:image': null,
        'og:url': null,
        'og:type': null,
        'twitter:card': null,
        'twitter:title': null,
        'twitter:description': null,
        'twitter:image': null
      },
      headings: {
        h1: [],
        h2: [],
        h3: [],
        h4: [],
        h5: [],
        h6: []
      },
      images: {
        total: 0,
        withAlt: 0,
        withoutAlt: 0,
        images: []
      },
      links: {
        internal: 0,
        external: 0,
        total: 0
      },
      issues: [],
      warnings: [],
      recommendations: [],
      score: 100
    };

    try {
      // Fetch the page
      const response = await axios.get(url, {
        timeout: this.timeout,
        headers: {
          'User-Agent': this.userAgent
        },
        maxRedirects: this.followRedirects ? 5 : 0
      });

      const $ = cheerio.load(response.data);
      const pageUrl = new URL(url);

      // Extract title
      this._extractTitle($, results);

      // Extract meta tags
      this._extractMetaTags($, results);

      // Extract canonical
      this._extractCanonical($, results);

      // Extract headings
      this._extractHeadings($, results);

      // Extract images
      this._extractImages($, results);

      // Extract links
      this._extractLinks($, pageUrl, results);

      // Analyze and generate recommendations
      this._analyzeResults(results);

    } catch (error) {
      results.status = 'error';
      results.error = error.message;
      results.issues.push(`Failed to analyze URL: ${error.message}`);
    }

    return results;
  }

  /**
   * Extract page title
   * @private
   */
  _extractTitle($, results) {
    const title = $('title').text().trim();
    
    if (!title) {
      results.issues.push('Missing page title');
      results.score -= 20;
    } else {
      results.meta.title = {
        content: title,
        length: title.length
      };

      // Check title length
      if (title.length < 30) {
        results.warnings.push(`Title too short (${title.length} chars) - aim for 30-60 characters`);
        results.score -= 5;
      } else if (title.length > 60) {
        results.warnings.push(`Title too long (${title.length} chars) - keep under 60 characters`);
        results.score -= 5;
      }

      // Check for generic titles
      const genericTitles = ['home', 'index', 'untitled', 'welcome'];
      if (genericTitles.includes(title.toLowerCase())) {
        results.issues.push('Generic page title detected - make it unique and descriptive');
        results.score -= 10;
      }
    }
  }

  /**
   * Extract meta tags
   * @private
   */
  _extractMetaTags($, results) {
    // Meta description
    const description = $('meta[name="description"]').attr('content');
    if (!description) {
      results.issues.push('Missing meta description');
      results.score -= 15;
    } else {
      results.meta.description = {
        content: description.trim(),
        length: description.trim().length
      };

      // Check description length
      if (description.length < 120) {
        results.warnings.push(`Description too short (${description.length} chars) - aim for 120-160 characters`);
        results.score -= 5;
      } else if (description.length > 160) {
        results.warnings.push(`Description too long (${description.length} chars) - keep under 160 characters`);
        results.score -= 5;
      }
    }

    // Keywords (less important but still extracted)
    const keywords = $('meta[name="keywords"]').attr('content');
    if (keywords) {
      results.meta.keywords = keywords.trim();
    }

    // Robots
    const robots = $('meta[name="robots"]').attr('content');
    if (robots) {
      results.meta.robots = robots.trim();
      
      // Check for indexing issues
      if (robots.includes('noindex')) {
        results.warnings.push('Page is set to noindex - ensure this is intentional');
      }
      if (robots.includes('nofollow')) {
        results.warnings.push('Page is set to nofollow - this prevents link equity flow');
      }
    }

    // Viewport
    const viewport = $('meta[name="viewport"]').attr('content');
    if (!viewport) {
      results.issues.push('Missing viewport meta tag - critical for mobile optimization');
      results.score -= 10;
    } else {
      results.meta.viewport = viewport.trim();
      
      // Check viewport content
      if (!viewport.includes('width=device-width')) {
        results.warnings.push('Viewport should include width=device-width');
      }
      if (!viewport.includes('initial-scale=1')) {
        results.warnings.push('Viewport should include initial-scale=1');
      }
    }

    // Charset
    const charset = $('meta[charset]').attr('charset') || 
                   $('meta[http-equiv="Content-Type"]').attr('content');
    if (charset) {
      results.meta.charset = charset;
    }

    // Open Graph tags
    this._extractOpenGraphTags($, results);

    // Twitter Card tags
    this._extractTwitterCardTags($, results);
  }

  /**
   * Extract Open Graph tags
   * @private
   */
  _extractOpenGraphTags($, results) {
    const ogTags = ['title', 'description', 'image', 'url', 'type', 'site_name'];
    let hasOgTags = false;

    ogTags.forEach(tag => {
      const content = $(`meta[property="og:${tag}"]`).attr('content');
      if (content) {
        results.meta[`og:${tag}`] = content.trim();
        hasOgTags = true;
      }
    });

    if (!hasOgTags) {
      results.warnings.push('No Open Graph tags found - consider adding for better social sharing');
      results.score -= 5;
    } else {
      // Check for essential OG tags
      if (!results.meta['og:title']) {
        results.warnings.push('Missing og:title tag');
      }
      if (!results.meta['og:description']) {
        results.warnings.push('Missing og:description tag');
      }
      if (!results.meta['og:image']) {
        results.warnings.push('Missing og:image tag - important for social sharing');
      }
    }
  }

  /**
   * Extract Twitter Card tags
   * @private
   */
  _extractTwitterCardTags($, results) {
    const twitterTags = ['card', 'title', 'description', 'image', 'site', 'creator'];
    let hasTwitterTags = false;

    twitterTags.forEach(tag => {
      const content = $(`meta[name="twitter:${tag}"]`).attr('content');
      if (content) {
        results.meta[`twitter:${tag}`] = content.trim();
        hasTwitterTags = true;
      }
    });

    if (!hasTwitterTags) {
      results.warnings.push('No Twitter Card tags found - consider adding for Twitter sharing');
      results.score -= 3;
    }
  }

  /**
   * Extract canonical URL
   * @private
   */
  _extractCanonical($, results) {
    const canonical = $('link[rel="canonical"]').attr('href');
    
    if (!canonical) {
      results.warnings.push('No canonical URL found - consider adding to prevent duplicate content issues');
      results.score -= 5;
    } else {
      results.meta.canonical = canonical.trim();
      
      // Validate canonical URL
      try {
        new URL(canonical);
      } catch (e) {
        results.issues.push('Invalid canonical URL format');
        results.score -= 5;
      }
    }
  }

  /**
   * Extract headings
   * @private
   */
  _extractHeadings($, results) {
    const headingTags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'];
    
    headingTags.forEach(tag => {
      $(tag).each((i, elem) => {
        const text = $(elem).text().trim();
        if (text) {
          results.headings[tag].push(text);
        }
      });
    });

    // Check H1
    if (results.headings.h1.length === 0) {
      results.issues.push('No H1 tag found - add exactly one H1 tag');
      results.score -= 10;
    } else if (results.headings.h1.length > 1) {
      results.warnings.push(`Multiple H1 tags found (${results.headings.h1.length}) - use only one H1 per page`);
      results.score -= 5;
    }

    // Check heading hierarchy
    if (results.headings.h3.length > 0 && results.headings.h2.length === 0) {
      results.warnings.push('H3 tags found without H2 - maintain proper heading hierarchy');
      results.score -= 3;
    }
  }

  /**
   * Extract images
   * @private
   */
  _extractImages($, results) {
    $('img').each((i, elem) => {
      const $img = $(elem);
      const src = $img.attr('src');
      const alt = $img.attr('alt');
      
      if (src) {
        results.images.total++;
        
        const imageInfo = {
          src: src,
          alt: alt || '',
          title: $img.attr('title') || '',
          width: $img.attr('width') || '',
          height: $img.attr('height') || ''
        };
        
        results.images.images.push(imageInfo);
        
        if (alt && alt.trim()) {
          results.images.withAlt++;
        } else {
          results.images.withoutAlt++;
        }
      }
    });

    // Check for alt text issues
    if (results.images.withoutAlt > 0) {
      results.issues.push(`${results.images.withoutAlt} images missing alt text - add descriptive alt text for accessibility and SEO`);
      results.score -= Math.min(15, results.images.withoutAlt * 2);
    }

    // Check for missing dimensions
    const missingDimensions = results.images.images.filter(img => !img.width || !img.height).length;
    if (missingDimensions > 0) {
      results.warnings.push(`${missingDimensions} images missing width/height attributes - add to prevent layout shift`);
      results.score -= Math.min(5, missingDimensions);
    }
  }

  /**
   * Extract links
   * @private
   */
  _extractLinks($, pageUrl, results) {
    $('a[href]').each((i, elem) => {
      const href = $(elem).attr('href');
      if (!href || href.startsWith('#')) return;

      results.links.total++;

      try {
        const linkUrl = new URL(href, pageUrl);
        
        if (linkUrl.hostname === pageUrl.hostname) {
          results.links.internal++;
        } else {
          results.links.external++;
          
          // Check for rel attributes on external links
          const rel = $(elem).attr('rel') || '';
          if (!rel.includes('nofollow') && !rel.includes('noopener')) {
            results.warnings.externalLinksNoRel = (results.warnings.externalLinksNoRel || 0) + 1;
          }
        }
      } catch (e) {
        // Invalid URL
      }
    });

    if (results.warnings.externalLinksNoRel > 0) {
      results.warnings.push(`${results.warnings.externalLinksNoRel} external links missing rel="nofollow" or rel="noopener"`);
      delete results.warnings.externalLinksNoRel;
    }
  }

  /**
   * Analyze results and generate recommendations
   * @private
   */
  _analyzeResults(results) {
    const recommendations = [];

    // Title recommendations
    if (!results.meta.title) {
      recommendations.push('Add a unique, descriptive page title between 30-60 characters');
    }

    // Description recommendations
    if (!results.meta.description) {
      recommendations.push('Add a compelling meta description between 120-160 characters');
    }

    // Mobile recommendations
    if (!results.meta.viewport) {
      recommendations.push('Add viewport meta tag: <meta name="viewport" content="width=device-width, initial-scale=1">');
    }

    // Social media recommendations
    if (!results.meta['og:image']) {
      recommendations.push('Add Open Graph image for better social media sharing');
    }

    // Heading recommendations
    if (results.headings.h1.length === 0) {
      recommendations.push('Add an H1 tag that includes your target keywords');
    }

    // Image recommendations
    if (results.images.withoutAlt > 0) {
      recommendations.push('Add descriptive alt text to all images for accessibility and SEO');
    }

    // Schema recommendations
    recommendations.push('Consider adding structured data (Schema.org) for rich snippets');

    results.recommendations = recommendations;
  }

  /**
   * Bulk extract from multiple URLs
   * @param {Array<string>} urls - URLs to analyze
   * @returns {Promise<Array>} Array of results
   */
  async bulkExtract(urls) {
    const results = [];
    
    for (const url of urls) {
      console.log(`Extracting meta tags from ${url}...`);
      const result = await this.extract(url);
      results.push(result);
      
      // Rate limiting
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    return results;
  }

  /**
   * Generate CSV report from results
   * @param {Object|Array} results - Extraction results
   * @returns {string} CSV formatted report
   */
  generateCSV(results) {
    const data = Array.isArray(results) ? results : [results];
    const rows = [
      ['URL', 'Title', 'Title Length', 'Description', 'Description Length', 'H1 Count', 'Images Total', 'Images Without Alt', 'Score', 'Issues', 'Warnings']
    ];

    data.forEach(result => {
      rows.push([
        result.url,
        result.meta.title?.content || '',
        result.meta.title?.length || 0,
        result.meta.description?.content || '',
        result.meta.description?.length || 0,
        result.headings.h1.length,
        result.images.total,
        result.images.withoutAlt,
        result.score,
        result.issues.length,
        result.warnings.length
      ]);
    });

    return rows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
  }
}

module.exports = MetaExtractor;

// CLI support
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node meta-extractor.js <url>');
    process.exit(1);
  }

  const url = args[0];
  const extractor = new MetaExtractor();
  
  console.log(`Extracting meta tags from ${url}...`);
  
  extractor.extract(url)
    .then(results => {
      console.log('\nMeta Tag Analysis Results');
      console.log('='.repeat(50));
      console.log(`URL: ${results.url}`);
      console.log(`Score: ${results.score}%`);
      
      if (results.meta.title) {
        console.log(`\nTitle (${results.meta.title.length} chars):`);
        console.log(`  ${results.meta.title.content}`);
      }
      
      if (results.meta.description) {
        console.log(`\nDescription (${results.meta.description.length} chars):`);
        console.log(`  ${results.meta.description.content}`);
      }
      
      console.log(`\nHeadings:`);
      console.log(`  H1: ${results.headings.h1.length}`);
      console.log(`  H2: ${results.headings.h2.length}`);
      console.log(`  H3: ${results.headings.h3.length}`);
      
      console.log(`\nImages:`);
      console.log(`  Total: ${results.images.total}`);
      console.log(`  Without Alt: ${results.images.withoutAlt}`);
      
      if (results.issues.length > 0) {
        console.log('\nIssues:');
        results.issues.forEach(issue => console.log(`  ❌ ${issue}`));
      }
      
      if (results.warnings.length > 0) {
        console.log('\nWarnings:');
        results.warnings.forEach(warning => console.log(`  ⚠️  ${warning}`));
      }
      
      if (results.recommendations.length > 0) {
        console.log('\nRecommendations:');
        results.recommendations.forEach(rec => console.log(`  💡 ${rec}`));
      }
    })
    .catch(error => {
      console.error('Error:', error.message);
      process.exit(1);
    });
}
