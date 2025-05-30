/**
 * Structured Data Parser Module
 * Parses and validates structured data (JSON-LD, Microdata, RDFa)
 * 
 * Author: Youssef Hodaigui - Mindflow Marketing
 * Website: https://youssefhodaigui.com
 */

const axios = require('axios');
const cheerio = require('cheerio');
const chalk = require('chalk');

class StructuredDataParser {
  constructor(options = {}) {
    this.timeout = options.timeout || 10000;
    this.userAgent = options.userAgent || 'SEO-Audit-Toolkit/1.0 (Structured Data Parser)';
    this.validateWithGoogle = options.validateWithGoogle || false;
  }

  /**
   * Parse structured data from a URL
   * @param {string} url - URL to analyze
   * @returns {Promise<Object>} Structured data analysis
   */
  async parse(url) {
    const results = {
      url,
      timestamp: new Date().toISOString(),
      status: 'completed',
      formats: {
        jsonLd: [],
        microdata: [],
        rdfa: []
      },
      schemas: [],
      validation: {
        errors: [],
        warnings: []
      },
      recommendations: [],
      score: 100,
      issues: {
        critical: 0,
        warnings: 0,
        passed: 0
      }
    };

    try {
      // Fetch the page
      const response = await axios.get(url, {
        timeout: this.timeout,
        headers: {
          'User-Agent': this.userAgent
        }
      });

      const $ = cheerio.load(response.data);

      // Parse different formats
      this._parseJsonLd($, results);
      this._parseMicrodata($, results);
      this._parseRDFa($, results);

      // Validate schemas
      this._validateSchemas(results);

      // Analyze page type and generate recommendations
      this._analyzeAndRecommend(url, results);

      // Calculate final score
      this._calculateScore(results);

    } catch (error) {
      results.status = 'error';
      results.error = error.message;
      results.validation.errors.push(`Failed to fetch URL: ${error.message}`);
    }

    return results;
  }

  /**
   * Parse JSON-LD structured data
   * @private
   */
  _parseJsonLd($, results) {
    const scripts = $('script[type="application/ld+json"]');
    
    scripts.each((i, elem) => {
      const content = $(elem).html();
      
      try {
        const json = JSON.parse(content);
        const schemas = Array.isArray(json) ? json : [json];
        
        schemas.forEach(schema => {
          if (schema && typeof schema === 'object') {
            const processed = this._processSchema(schema, 'JSON-LD');
            results.formats.jsonLd.push(processed);
            results.schemas.push(processed);
          }
        });
        
      } catch (error) {
        results.validation.errors.push(`Invalid JSON-LD: ${error.message}`);
        results.issues.critical++;
      }
    });
  }

  /**
   * Parse Microdata
   * @private
   */
  _parseMicrodata($, results) {
    const items = $('[itemscope]');
    
    items.each((i, elem) => {
      const $item = $(elem);
      const itemType = $item.attr('itemtype');
      
      if (itemType) {
        const schema = {
          '@type': this._extractTypeFromUrl(itemType),
          '@context': 'http://schema.org',
          _format: 'Microdata'
        };

        // Extract properties
        this._extractMicrodataProperties($, $item, schema);
        
        const processed = this._processSchema(schema, 'Microdata');
        results.formats.microdata.push(processed);
        results.schemas.push(processed);
      }
    });
  }

  /**
   * Extract Microdata properties
   * @private
   */
  _extractMicrodataProperties($, $item, schema) {
    const properties = $item.find('[itemprop]');
    
    properties.each((i, elem) => {
      const $prop = $(elem);
      const propName = $prop.attr('itemprop');
      
      if (propName && !$prop.parents('[itemscope]').length > 1) {
        const value = this._getMicrodataValue($prop);
        
        if (schema[propName]) {
          // Convert to array if multiple values
          if (!Array.isArray(schema[propName])) {
            schema[propName] = [schema[propName]];
          }
          schema[propName].push(value);
        } else {
          schema[propName] = value;
        }
      }
    });
  }

  /**
   * Get Microdata property value
   * @private
   */
  _getMicrodataValue($elem) {
    if ($elem.attr('itemscope') !== undefined) {
      // Nested item
      return this._extractNestedMicrodata($elem);
    }
    
    // Order matters: content, src, href, text
    return $elem.attr('content') || 
           $elem.attr('src') || 
           $elem.attr('href') || 
           $elem.text().trim();
  }

  /**
   * Parse RDFa
   * @private
   */
  _parseRDFa($, results) {
    const rdfaElements = $('[typeof]');
    
    rdfaElements.each((i, elem) => {
      const $elem = $(elem);
      const type = $elem.attr('typeof');
      const vocab = $elem.attr('vocab') || 'http://schema.org/';
      
      if (type) {
        const schema = {
          '@type': type,
          '@context': vocab,
          _format: 'RDFa'
        };

        // Extract RDFa properties
        this._extractRDFaProperties($, $elem, schema);
        
        const processed = this._processSchema(schema, 'RDFa');
        results.formats.rdfa.push(processed);
        results.schemas.push(processed);
      }
    });
  }

  /**
   * Extract RDFa properties
   * @private
   */
  _extractRDFaProperties($, $elem, schema) {
    const properties = $elem.find('[property]');
    
    properties.each((i, elem) => {
      const $prop = $(elem);
      const propName = $prop.attr('property');
      const content = $prop.attr('content') || $prop.text().trim();
      
      if (propName && content) {
        schema[propName] = content;
      }
    });
  }

  /**
   * Process and validate a schema
   * @private
   */
  _processSchema(schema, format) {
    const processed = {
      format,
      type: schema['@type'] || 'Unknown',
      properties: {},
      validation: {
        errors: [],
        warnings: []
      }
    };

    // Extract properties
    Object.keys(schema).forEach(key => {
      if (!key.startsWith('@') && key !== '_format') {
        processed.properties[key] = schema[key];
      }
    });

    // Type-specific validation
    this._validateSchemaType(processed);

    return processed;
  }

  /**
   * Validate schemas based on type
   * @private
   */
  _validateSchemas(results) {
    const typeValidators = {
      'Organization': this._validateOrganization,
      'LocalBusiness': this._validateLocalBusiness,
      'Product': this._validateProduct,
      'Article': this._validateArticle,
      'BlogPosting': this._validateArticle,
      'NewsArticle': this._validateArticle,
      'BreadcrumbList': this._validateBreadcrumbList,
      'FAQPage': this._validateFAQPage,
      'Recipe': this._validateRecipe,
      'Event': this._validateEvent,
      'Person': this._validatePerson,
      'WebSite': this._validateWebSite,
      'SearchAction': this._validateSearchAction
    };

    results.schemas.forEach(schema => {
      const validator = typeValidators[schema.type];
      if (validator) {
        validator.call(this, schema, results);
      }
    });
  }

  /**
   * Validate Organization schema
   * @private
   */
  _validateOrganization(schema, results) {
    const required = ['name', 'url'];
    const recommended = ['logo', 'sameAs', 'contactPoint', 'address'];
    
    this._checkRequiredProperties(schema, required, results);
    this._checkRecommendedProperties(schema, recommended, results);

    // Special validation for logo
    if (schema.properties.logo && typeof schema.properties.logo === 'string') {
      results.validation.warnings.push(
        'Organization logo should be an ImageObject with width and height'
      );
      results.issues.warnings++;
    }
  }

  /**
   * Validate Product schema
   * @private
   */
  _validateProduct(schema, results) {
    const required = ['name', 'image'];
    const recommended = ['description', 'sku', 'offers', 'aggregateRating', 'brand', 'review'];
    
    this._checkRequiredProperties(schema, required, results);
    this._checkRecommendedProperties(schema, recommended, results);

    // Validate offers
    if (schema.properties.offers) {
      const offers = Array.isArray(schema.properties.offers) 
        ? schema.properties.offers 
        : [schema.properties.offers];
      
      offers.forEach(offer => {
        if (!offer.price && !offer.priceRange) {
          results.validation.errors.push('Product offer missing price information');
          results.issues.critical++;
        }
        if (!offer.priceCurrency) {
          results.validation.errors.push('Product offer missing priceCurrency');
          results.issues.critical++;
        }
      });
    }

    // Check for rich results eligibility
    if (!schema.properties.aggregateRating && !schema.properties.review) {
      results.validation.warnings.push(
        'Product missing ratings/reviews - needed for rich results'
      );
      results.issues.warnings++;
    }
  }

  /**
   * Validate Article schema
   * @private
   */
  _validateArticle(schema, results) {
    const required = ['headline', 'image', 'author', 'datePublished'];
    const recommended = ['dateModified', 'publisher', 'mainEntityOfPage', 'description'];
    
    this._checkRequiredProperties(schema, required, results);
    this._checkRecommendedProperties(schema, recommended, results);

    // Validate images
    if (schema.properties.image) {
      const images = Array.isArray(schema.properties.image) 
        ? schema.properties.image 
        : [schema.properties.image];
      
      if (images.length === 0) {
        results.validation.errors.push('Article requires at least one image');
        results.issues.critical++;
      }
    }

    // Validate dates
    if (schema.properties.datePublished) {
      if (!this._isValidDate(schema.properties.datePublished)) {
        results.validation.errors.push('Invalid datePublished format - use ISO 8601');
        results.issues.critical++;
      }
    }
  }

  /**
   * Validate BreadcrumbList schema
   * @private
   */
  _validateBreadcrumbList(schema, results) {
    if (!schema.properties.itemListElement) {
      results.validation.errors.push('BreadcrumbList missing itemListElement');
      results.issues.critical++;
      return;
    }

    const items = Array.isArray(schema.properties.itemListElement) 
      ? schema.properties.itemListElement 
      : [schema.properties.itemListElement];

    items.forEach((item, index) => {
      if (!item.position) {
        results.validation.errors.push(
          `BreadcrumbList item ${index} missing position`
        );
        results.issues.critical++;
      }
      if (!item.name) {
        results.validation.errors.push(
          `BreadcrumbList item ${index} missing name`
        );
        results.issues.critical++;
      }
    });
  }

  /**
   * Validate FAQPage schema
   * @private
   */
  _validateFAQPage(schema, results) {
    if (!schema.properties.mainEntity) {
      results.validation.errors.push('FAQPage missing mainEntity');
      results.issues.critical++;
      return;
    }

    const questions = Array.isArray(schema.properties.mainEntity) 
      ? schema.properties.mainEntity 
      : [schema.properties.mainEntity];

    questions.forEach((question, index) => {
      if (!question.name) {
        results.validation.errors.push(`FAQ question ${index} missing name`);
        results.issues.critical++;
      }
      if (!question.acceptedAnswer) {
        results.validation.errors.push(`FAQ question ${index} missing acceptedAnswer`);
        results.issues.critical++;
      } else if (!question.acceptedAnswer.text) {
        results.validation.errors.push(
          `FAQ question ${index} acceptedAnswer missing text`
        );
        results.issues.critical++;
      }
    });
  }

  /**
   * Validate Recipe schema
   * @private
   */
  _validateRecipe(schema, results) {
    const required = ['name', 'image', 'recipeIngredient', 'recipeInstructions'];
    const recommended = [
      'prepTime', 'cookTime', 'totalTime', 'recipeYield', 
      'nutrition', 'aggregateRating', 'author', 'description'
    ];
    
    this._checkRequiredProperties(schema, required, results);
    this._checkRecommendedProperties(schema, recommended, results);
  }

  /**
   * Validate Event schema
   * @private
   */
  _validateEvent(schema, results) {
    const required = ['name', 'startDate', 'location'];
    const recommended = ['endDate', 'description', 'image', 'performer', 'offers'];
    
    this._checkRequiredProperties(schema, required, results);
    this._checkRecommendedProperties(schema, recommended, results);

    // Validate dates
    if (schema.properties.startDate && !this._isValidDate(schema.properties.startDate)) {
      results.validation.errors.push('Invalid startDate format - use ISO 8601');
      results.issues.critical++;
    }
  }

  /**
   * Validate Person schema
   * @private
   */
  _validatePerson(schema, results) {
    const required = ['name'];
    const recommended = ['image', 'jobTitle', 'worksFor', 'sameAs', 'url'];
    
    this._checkRequiredProperties(schema, required, results);
    this._checkRecommendedProperties(schema, recommended, results);
  }

  /**
   * Validate WebSite schema
   * @private
   */
  _validateWebSite(schema, results) {
    const required = ['name', 'url'];
    const recommended = ['potentialAction', 'publisher'];
    
    this._checkRequiredProperties(schema, required, results);
    this._checkRecommendedProperties(schema, recommended, results);

    // Check for SearchAction
    if (!schema.properties.potentialAction) {
      results.validation.warnings.push(
        'WebSite schema missing SearchAction - add for sitelinks searchbox'
      );
      results.issues.warnings++;
    }
  }

  /**
   * Validate SearchAction schema
   * @private
   */
  _validateSearchAction(schema, results) {
    const required = ['target', 'query-input'];
    
    this._checkRequiredProperties(schema, required, results);

    // Validate target
    if (schema.properties.target && typeof schema.properties.target === 'string') {
      if (!schema.properties.target.includes('{search_term_string}')) {
        results.validation.errors.push(
          'SearchAction target must include {search_term_string} placeholder'
        );
        results.issues.critical++;
      }
    }
  }

  /**
   * Check required properties
   * @private
   */
  _checkRequiredProperties(schema, required, results) {
    required.forEach(prop => {
      if (!schema.properties[prop]) {
        results.validation.errors.push(
          `${schema.type} missing required property: ${prop}`
        );
        results.issues.critical++;
      }
    });
  }

  /**
   * Check recommended properties
   * @private
   */
  _checkRecommendedProperties(schema, recommended, results) {
    const missing = recommended.filter(prop => !schema.properties[prop]);
    
    if (missing.length > 0) {
      results.validation.warnings.push(
        `${schema.type} missing recommended properties: ${missing.join(', ')}`
      );
      results.issues.warnings++;
    }
  }

  /**
   * Analyze page and generate recommendations
   * @private
   */
  _analyzeAndRecommend(url, results) {
    const schemaTypes = results.schemas.map(s => s.type);
    const pageType = this._detectPageType(url, schemaTypes);

    // Page type specific recommendations
    const recommendations = {
      homepage: ['Organization or LocalBusiness', 'WebSite with SearchAction', 'BreadcrumbList'],
      product: ['Product with offers and reviews', 'BreadcrumbList', 'Organization'],
      article: ['Article or BlogPosting', 'BreadcrumbList', 'Author (Person)', 'Publisher'],
      category: ['BreadcrumbList', 'ItemList', 'WebPage'],
      faq: ['FAQPage', 'BreadcrumbList', 'Organization'],
      local: ['LocalBusiness with address', 'OpeningHoursSpecification', 'Review'],
      event: ['Event with location and dates', 'Organization', 'Offers']
    };

    const recommended = recommendations[pageType] || recommendations.homepage;
    
    recommended.forEach(rec => {
      const hasSchema = schemaTypes.some(type => 
        rec.toLowerCase().includes(type.toLowerCase())
      );
      
      if (!hasSchema) {
        results.recommendations.push(`Consider adding ${rec} schema`);
      }
    });

    // General recommendations
    if (results.schemas.length === 0) {
      results.recommendations.push(
        'No structured data found - add appropriate schemas for rich results'
      );
    }

    if (results.formats.jsonLd.length === 0) {
      results.recommendations.push(
        'Use JSON-LD format for structured data (Google\'s preferred format)'
      );
    }

    // Calculate passed checks
    results.issues.passed = results.schemas.length - 
                           results.issues.critical - 
                           results.issues.warnings;
  }

  /**
   * Detect page type from URL and schemas
   * @private
   */
  _detectPageType(url, schemaTypes) {
    const urlLower = url.toLowerCase();
    
    if (url.endsWith('/') || urlLower.includes('/home')) return 'homepage';
    if (urlLower.includes('/product') || urlLower.includes('/item')) return 'product';
    if (urlLower.includes('/article') || urlLower.includes('/blog')) return 'article';
    if (urlLower.includes('/category') || urlLower.includes('/shop')) return 'category';
    if (urlLower.includes('/faq')) return 'faq';
    if (urlLower.includes('/contact') || urlLower.includes('/location')) return 'local';
    if (urlLower.includes('/event')) return 'event';

    // Check by existing schemas
    if (schemaTypes.includes('Product')) return 'product';
    if (schemaTypes.some(t => ['Article', 'BlogPosting', 'NewsArticle'].includes(t))) return 'article';
    
    return 'general';
  }

  /**
   * Calculate score based on validation results
   * @private
   */
  _calculateScore(results) {
    let score = 100;

    // Deduct for errors (15 points each)
    score -= results.validation.errors.length * 15;

    // Deduct for warnings (5 points each)
    score -= results.validation.warnings.length * 5;

    // Bonus for having schemas
    if (results.schemas.length > 0) {
      score += 10;
    }

    // Bonus for using JSON-LD
    if (results.formats.jsonLd.length > 0) {
      score += 5;
    }

    results.score = Math.max(0, Math.min(100, score));
  }

  /**
   * Extract type from schema.org URL
   * @private
   */
  _extractTypeFromUrl(url) {
    const match = url.match(/schema\.org\/(.+)$/);
    return match ? match[1] : 'Thing';
  }

  /**
   * Validate date format
   * @private
   */
  _isValidDate(dateString) {
    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date);
  }
}

module.exports = StructuredDataParser;

// CLI support
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node structured-data.js <url>');
    process.exit(1);
  }

  const url = args[0];
  const parser = new StructuredDataParser();
  
  console.log(`Parsing structured data from ${url}...`);
  
  parser.parse(url)
    .then(results => {
      console.log('\n' + chalk.bold('Structured Data Analysis'));
      console.log('='.repeat(50));
      console.log(`URL: ${results.url}`);
      console.log(`Score: ${results.score}%`);
      console.log(`\nSchemas Found: ${results.schemas.length}`);
      
      if (results.schemas.length > 0) {
        console.log('\nSchema Types:');
        results.schemas.forEach(schema => {
          console.log(`  - ${schema.type} (${schema.format})`);
        });
      }
      
      if (results.validation.errors.length > 0) {
        console.log('\n' + chalk.red('Errors:'));
        results.validation.errors.forEach(error => {
          console.log(`  ❌ ${error}`);
        });
      }
      
      if (results.validation.warnings.length > 0) {
        console.log('\n' + chalk.yellow('Warnings:'));
        results.validation.warnings.forEach(warning => {
          console.log(`  ⚠️  ${warning}`);
        });
      }
      
      if (results.recommendations.length > 0) {
        console.log('\n' + chalk.green('Recommendations:'));
        results.recommendations.forEach(rec => {
          console.log(`  💡 ${rec}`);
        });
      }
    })
    .catch(error => {
      console.error(chalk.red('Error:'), error.message);
      process.exit(1);
    });
}
