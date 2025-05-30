"""
Tests for Technical Audit Module
Author: Youssef Hodaigui - Mindflow Marketing
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.technical_audit import TechnicalAuditor


class TestTechnicalAuditor:
    """Test cases for TechnicalAuditor class"""
    
    @pytest.fixture
    def auditor(self):
        """Create a TechnicalAuditor instance for testing"""
        return TechnicalAuditor()
    
    @pytest.fixture
    def mock_response(self):
        """Create a mock response object"""
        mock = Mock()
        mock.status_code = 200
        mock.text = """
        <html>
        <head>
            <title>Test Page - SEO Audit Toolkit</title>
            <meta name="description" content="This is a test page for SEO audit testing with proper length.">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="canonical" href="https://example.com/test-page">
        </head>
        <body>
            <h1>Main Heading</h1>
            <h2>Subheading</h2>
            <img src="test.jpg" alt="Test image">
            <img src="test2.jpg">
            <a href="https://example.com/internal">Internal Link</a>
            <a href="https://external.com">External Link</a>
        </body>
        </html>
        """
        return mock
    
    def test_initialization(self, auditor):
        """Test auditor initialization"""
        assert auditor is not None
        assert auditor.session is not None
        assert 'User-Agent' in auditor.session.headers
    
    @patch('requests.Session.get')
    def test_audit_website_success(self, mock_get, auditor, mock_response):
        """Test successful website audit"""
        mock_get.return_value = mock_response
        
        results = auditor.audit_website('https://example.com')
        
        assert results['status'] == 'completed'
        assert results['url'] == 'https://example.com'
        assert 'score' in results
        assert 0 <= results['score'] <= 100
        assert 'checks' in results
        assert 'issues' in results
    
    @patch('requests.Session.get')
    def test_title_check(self, mock_get, auditor, mock_response):
        """Test title tag checking"""
        mock_get.return_value = mock_response
        
        results = auditor.audit_website('https://example.com')
        
        assert 'title' in results['checks']
        title_check = results['checks']['title']
        assert title_check['status'] == 'ok'
        assert title_check['content'] == 'Test Page - SEO Audit Toolkit'
        assert 30 <= title_check['length'] <= 60
    
    @patch('requests.Session.get')
    def test_meta_description_check(self, mock_get, auditor, mock_response):
        """Test meta description checking"""
        mock_get.return_value = mock_response
        
        results = auditor.audit_website('https://example.com')
        
        assert 'meta_description' in results['checks']
        desc_check = results['checks']['meta_description']
        assert desc_check['status'] == 'ok'
        assert desc_check['length'] > 0
    
    @patch('requests.Session.get')
    def test_missing_title(self, mock_get, auditor):
        """Test detection of missing title"""
        mock = Mock()
        mock.status_code = 200
        mock.text = '<html><head></head><body></body></html>'
        mock_get.return_value = mock
        
        results = auditor.audit_website('https://example.com')
        
        assert results['checks']['title']['status'] == 'error'
        assert 'No title tag found' in results['checks']['title']['message']
    
    @patch('requests.Session.get')
    def test_heading_structure(self, mock_get, auditor, mock_response):
        """Test heading structure analysis"""
        mock_get.return_value = mock_response
        
        results = auditor.audit_website('https://example.com')
        
        assert 'headings' in results['checks']
        headings = results['checks']['headings']
        assert headings['structure']['h1']['count'] == 1
        assert headings['structure']['h2']['count'] == 1
        assert headings['status'] == 'ok'
    
    @patch('requests.Session.get')
    def test_image_alt_detection(self, mock_get, auditor, mock_response):
        """Test image alt text detection"""
        mock_get.return_value = mock_response
        
        results = auditor.audit_website('https://example.com')
        
        assert 'images' in results['checks']
        images = results['checks']['images']
        assert images['total_images'] == 2
        assert images['issues']['missing_alt'] == 1
        assert images['status'] in ['warning', 'error']
    
    @patch('requests.Session.get')
    def test_canonical_check(self, mock_get, auditor, mock_response):
        """Test canonical URL checking"""
        mock_get.return_value = mock_response
        
        results = auditor.audit_website('https://example.com')
        
        assert 'canonical' in results['checks']
        canonical = results['checks']['canonical']
        assert canonical['status'] == 'ok'
        assert canonical['canonical_url'] == 'https://example.com/test-page'
    
    @patch('requests.Session.get')
    def test_network_error_handling(self, mock_get, auditor):
        """Test handling of network errors"""
        mock_get.side_effect = Exception("Network error")
        
        results = auditor.audit_website('https://example.com')
        
        assert results['status'] == 'error'
        assert 'error' in results
        assert 'Network error' in results['error']
    
    def test_report_generation_json(self, auditor):
        """Test JSON report generation"""
        results = {
            'url': 'https://example.com',
            'score': 85,
            'timestamp': '2024-01-15T10:00:00',
            'checks': {},
            'issues': {'critical': 1, 'warnings': 2, 'passed': 10}
        }
        
        report = auditor.generate_report(results, format='json')
        assert isinstance(report, str)
        
        import json
        parsed = json.loads(report)
        assert parsed['url'] == 'https://example.com'
        assert parsed['score'] == 85
    
    def test_report_generation_text(self, auditor):
        """Test text report generation"""
        results = {
            'url': 'https://example.com',
            'score': 85,
            'timestamp': '2024-01-15T10:00:00',
            'checks': {},
            'issues': {'critical': 1, 'warnings': 2, 'passed': 10}
        }
        
        report = auditor.generate_report(results, format='text')
        assert isinstance(report, str)
        assert 'SEO AUDIT REPORT' in report
        assert 'https://example.com' in report
        assert '85%' in report
    
    def test_report_generation_html(self, auditor):
        """Test HTML report generation"""
        results = {
            'url': 'https://example.com',
            'score': 85,
            'timestamp': '2024-01-15T10:00:00',
            'checks': {},
            'issues': {'critical': 1, 'warnings': 2, 'passed': 10}
        }
        
        report = auditor.generate_report(results, format='html')
        assert isinstance(report, str)
        assert '<!DOCTYPE html>' in report
        assert '<title>SEO Audit Report' in report
        assert 'https://example.com' in report
    
    def test_invalid_report_format(self, auditor):
        """Test invalid report format handling"""
        results = {'url': 'https://example.com'}
        
        with pytest.raises(ValueError, match="Unsupported format"):
            auditor.generate_report(results, format='invalid')


class TestTechnicalAuditorIntegration:
    """Integration tests for TechnicalAuditor"""
    
    @pytest.mark.integration
    @pytest.mark.skipif(not os.environ.get('RUN_INTEGRATION_TESTS'), 
                        reason="Integration tests disabled")
    def test_real_website_audit(self):
        """Test auditing a real website (requires internet)"""
        auditor = TechnicalAuditor()
        results = auditor.audit_website('https://example.com')
        
        assert results['status'] == 'completed'
        assert isinstance(results['score'], int)
        assert 'checks' in results
        assert len(results['checks']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
