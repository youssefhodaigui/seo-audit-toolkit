/**
 * Tests for Meta Extractor Module
 * Author: Youssef Hodaigui - Mindflow Marketing
 */

const MetaExtractor = require('../javascript/meta-extractor');
const axios = require('axios');

// Mock axios
jest.mock('axios');

describe('MetaExtractor', () => {
  let extractor;
  
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    extractor = new MetaExtractor();
  });

  describe('constructor', () => {
    test('should initialize with default options', () => {
      expect(extractor.timeout).toBe(10000);
      expect(extractor.userAgent).toContain('Meta Extractor');
      expect(extractor.followRedirects).toBe(true);
    });

    test('should accept custom options', () => {
      const customExtractor = new MetaExtractor({
        timeout: 5000,
        userAgent: 'CustomBot',
        followRedirects: false
      });
      
      expect(customExtractor.timeout).toBe(5000);
      expect(customExtractor.userAgent).toBe('CustomBot');
      expect(customExtractor.followRedirects).toBe(false);
    });
  });

  describe('extract', () => {
    const mockHTML = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Test Page - SEO Audit Toolkit</title>
        <meta name="description" content="This is a test page for SEO audit testing with proper length for meta description.">
        <meta name="keywords" content="seo, audit, testing">
        <meta name="robots" content="index, follow">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta charset="UTF-8">
        <meta property="og:title" content="Test Page OG Title">
        <meta property="og:description" content="Test OG Description">
        <meta property="og:image" content="https://example.com/image.jpg">
        <meta property="og:url" content="https://example.com/test">
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="Test Twitter Title">
        <link rel="canonical" href="https://example.com/test-page">
      </head>
      <body>
        <h1>Main Heading</h1>
        <h2>Subheading 1</h2>
        <h2>Subheading 2</h2>
        <h3>Sub-subheading</h3>
        <img src="test1.jpg" alt="Test image 1">
        <img src="test2.jpg" alt="Test image 2">
        <img src="test3.jpg">
        <a href="/internal">Internal Link</a>
        <a href="https://example.com/another">Another Internal</a>
        <a href="https://external.com">External Link</a>
      </body>
      </html>
    `;

    beforeEach(() => {
      axios.get.mockResolvedValue({
        data: mockHTML,
        status: 200,
        headers: {}
      });
    });

    test('should extract meta tags successfully', async () => {
      const results = await extractor.extract('https://example.com');
      
      expect(results.status).toBe('completed');
      expect(results.url).toBe('https://example.com');
      expect(results.meta.title).toEqual({
        content: 'Test Page - SEO Audit Toolkit',
        length: 30
      });
    });

    test('should extract meta description', async () => {
      const results = await extractor.extract('https://example.com');
      
      expect(results.meta.description.content).toContain('test page for SEO audit');
      expect(results.meta.description.length).toBeGreaterThan(60);
    });

    test('should extract Open Graph tags', async () => {
      const results = await extractor.extract('https://example.com');
      
      expect(results.meta['og:title']).toBe('Test Page OG Title');
      expect(results.meta['og:description']).toBe('Test OG Description');
      expect(results.meta['og:image']).toBe('https://example.com/image.jpg');
    });

    test('should extract Twitter Card tags', async () => {
      const results = await extractor.extract('https://example.com');
      
      expect(results.meta['twitter:card']).toBe('summary_large_image');
      expect(results.meta['twitter:title']).toBe('Test Twitter Title');
    });

    test('should extract canonical URL', async () => {
      const results = await extractor.extract('https://example.com');
      
      expect(results.meta.canonical).toBe('https://example.com/test-page');
    });

    test('should count headings correctly', async () => {
      const results = await extractor.extract('https://example.com');
      
      expect(results.headings.h1).toHaveLength(1);
      expect(results.headings.h2).toHaveLength(2);
      expect(results.headings.h3).toHaveLength(1);
      expect(results.headings.h1[0]).toBe('Main Heading');
    });

    test('should analyze images', async () => {
      const results = await extractor.extract('https://example.com');
      
      expect(results.images.total).toBe(3);
      expect(results.images.withAlt).toBe(2);
      expect(results.images.withoutAlt).toBe(1);
    });

    test('should count internal and external links', async () => {
      const results = await extractor.extract('https://example.com');
      
      expect(results.links.total).toBe(3);
      expect(results.links.internal).toBe(2);
      expect(results.links.external).toBe(1);
    });

    test('should generate recommendations', async () => {
      const results = await extractor.extract('https://example.com');
      
      expect(results.recommendations).toBeInstanceOf(Array);
      expect(results.recommendations.length).toBeGreaterThan(0);
    });

    test('should calculate score', async () => {
      const results = await extractor.extract('https://example.com');
      
      expect(results.score).toBeDefined();
      expect(results.score).toBeGreaterThanOrEqual(0);
      expect(results.score).toBeLessThanOrEqual(100);
    });

    test('should handle missing title', async () => {
      const htmlNoTitle = '<html><head></head><body></body></html>';
      axios.get.mockResolvedValue({ data: htmlNoTitle });
      
      const results = await extractor.extract('https://example.com');
      
      expect(results.issues).toContain('Missing page title');
      expect(results.score).toBeLessThan(100);
    });

    test('should handle missing meta description', async () => {
      const htmlNoDesc = '<html><head><title>Test</title></head><body></body></html>';
      axios.get.mockResolvedValue({ data: htmlNoDesc });
      
      const results = await extractor.extract('https://example.com');
      
      expect(results.issues).toContain('Missing meta description');
    });

    test('should handle network errors', async () => {
      axios.get.mockRejectedValue(new Error('Network error'));
      
      const results = await extractor.extract('https://example.com');
      
      expect(results.status).toBe('error');
      expect(results.error).toBe('Network error');
    });

    test('should detect missing viewport meta tag', async () => {
      const htmlNoViewport = `
        <html>
        <head>
          <title>Test</title>
          <meta name="description" content="Test description">
        </head>
        <body></body>
        </html>
      `;
      axios.get.mockResolvedValue({ data: htmlNoViewport });
      
      const results = await extractor.extract('https://example.com');
      
      expect(results.issues).toContain('Missing viewport meta tag - critical for mobile optimization');
    });

    test('should detect multiple H1 tags', async () => {
      const htmlMultipleH1 = `
        <html>
        <head><title>Test</title></head>
        <body>
          <h1>First H1</h1>
          <h1>Second H1</h1>
        </body>
        </html>
      `;
      axios.get.mockResolvedValue({ data: htmlMultipleH1 });
      
      const results = await extractor.extract('https://example.com');
      
      expect(results.headings.h1).toHaveLength(2);
      expect(results.warnings).toContain(expect.stringContaining('Multiple H1 tags found'));
    });
  });

  describe('bulkExtract', () => {
    test('should extract from multiple URLs', async () => {
      const urls = ['https://example1.com', 'https://example2.com'];
      axios.get.mockResolvedValue({
        data: '<html><head><title>Test</title></head><body></body></html>'
      });
      
      const results = await extractor.bulkExtract(urls);
      
      expect(results).toHaveLength(2);
      expect(axios.get).toHaveBeenCalledTimes(2);
    });

    test('should add delay between requests', async () => {
      jest.useFakeTimers();
      const urls = ['https://example1.com', 'https://example2.com'];
      
      axios.get.mockResolvedValue({
        data: '<html><head><title>Test</title></head><body></body></html>'
      });
      
      const bulkPromise = extractor.bulkExtract(urls);
      
      // Fast forward time
      jest.runAllTimers();
      
      await bulkPromise;
      
      expect(setTimeout).toHaveBeenCalled();
      jest.useRealTimers();
    });
  });

  describe('generateCSV', () => {
    test('should generate CSV from single result', () => {
      const result = {
        url: 'https://example.com',
        meta: {
          title: { content: 'Test Title', length: 10 },
          description: { content: 'Test Description', length: 16 }
        },
        headings: { h1: ['Heading 1'] },
        images: { total: 5, withoutAlt: 2 },
        score: 85,
        issues: ['Issue 1'],
        warnings: ['Warning 1', 'Warning 2']
      };
      
      const csv = extractor.generateCSV(result);
      
      expect(csv).toContain('URL,Title,Title Length');
      expect(csv).toContain('https://example.com');
      expect(csv).toContain('Test Title');
      expect(csv).toContain('85');
    });

    test('should generate CSV from multiple results', () => {
      const results = [
        {
          url: 'https://example1.com',
          meta: { title: { content: 'Title 1', length: 7 } },
          headings: { h1: [] },
          images: { total: 0, withoutAlt: 0 },
          score: 90,
          issues: [],
          warnings: []
        },
        {
          url: 'https://example2.com',
          meta: { title: { content: 'Title 2', length: 7 } },
          headings: { h1: [] },
          images: { total: 0, withoutAlt: 0 },
          score: 80,
          issues: [],
          warnings: []
        }
      ];
      
      const csv = extractor.generateCSV(results);
      const lines = csv.split('\n');
      
      expect(lines).toHaveLength(3); // Header + 2 data rows
      expect(csv).toContain('example1.com');
      expect(csv).toContain('example2.com');
    });

    test('should escape quotes in CSV', () => {
      const result = {
        url: 'https://example.com',
        meta: {
          title: { content: 'Title with "quotes"', length: 18 },
          description: { content: 'Description', length: 11 }
        },
        headings: { h1: [] },
        images: { total: 0, withoutAlt: 0 },
        score: 100,
        issues: [],
        warnings: []
      };
      
      const csv = extractor.generateCSV(result);
      
      expect(csv).toContain('Title with ""quotes""');
    });
  });
});

// Integration tests (skipped by default)
describe('MetaExtractor Integration', () => {
  test.skip('should extract from real website', async () => {
    const extractor = new MetaExtractor();
    const results = await extractor.extract('https://example.com');
    
    expect(results.status).toBe('completed');
    expect(results.meta.title).toBeDefined();
  });
});
