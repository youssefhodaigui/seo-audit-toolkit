"""
Schema Markup Validator Module
Validates structured data implementation for SEO

Author: Youssef Hodaigui - Mindflow Marketing
Website: https://youssefhodaigui.com
"""

import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse

class SchemaValidator:
    """Validate and analyze structured data/schema markup"""
    
    def __init__(self):
        """Initialize Schema Validator"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SEO-Audit-Toolkit/1.0 (Schema Validator)'
        })
        self.google_validator_url = "https://validator.schema.org/"
        
        # Common schema types for different page types
        self.recommended_schemas = {
            'homepage': ['Organization', 'WebSite', 'SearchAction'],
            'article': ['Article', 'NewsArticle', 'BlogPosting', 'BreadcrumbList'],
            'product': ['Product', 'Offer', 'AggregateRating', 'Review'],
            'local': ['LocalBusiness', 'PostalAddress', 'GeoCoordinates', 'OpeningHoursSpecification'],
            'person': ['Person', 'ProfilePage'],
            'event': ['Event', 'Place', 'Offer'],
            'faq': ['FAQPage', 'Question', 'Answer'],
            'recipe': ['Recipe', 'NutritionInformation', 'AggregateRating'],
            'video': ['VideoObject', 'Clip', 'BroadcastEvent']
        }
        
    def validate_url(self, url: str) -> Dict:
        """
        Validate schema markup on a URL
        
        Args:
            url: URL to validate
            
        Returns:
            Dictionary containing validation results
        """
        results = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'schemas_found': [],
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        try:
            # Fetch the page
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract all structured data
            structured_data = self._extract_structured_data(soup)
            
            if not structured_data:
                results['status'] = 'warning'
                results['warnings'].append('No structured data found on the page')
                results['recommendations'].append('Add appropriate schema markup for better search visibility')
            else:
                # Validate each schema
                for i, schema in enumerate(structured_data):
                    validation = self._validate_schema(schema, i)
                    results['schemas_found'].append(validation['type'])
                    results['errors'].extend(validation['errors'])
                    results['warnings'].extend(validation['warnings'])
                
                # Generate recommendations based on page type
                page_type = self._detect_page_type(url, soup, structured_data)
                results['page_type'] = page_type
                results['recommendations'] = self._generate_recommendations(
                    page_type, results['schemas_found']
                )
            
            # Calculate validation score
            results['score'] = self._calculate_score(results)
            
        except requests.exceptions.RequestException as e:
            results['status'] = 'error'
            results['errors'].append(f"Failed to fetch URL: {str(e)}")
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(f"Validation failed: {str(e)}")
        
        return results
    
    def validate_json(self, schema_json: str) -> Dict:
        """
        Validate a JSON-LD schema string
        
        Args:
            schema_json: JSON-LD string to validate
            
        Returns:
            Validation results
        """
        results = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'type': 'unknown'
        }
        
        try:
            # Parse JSON
            data = json.loads(schema_json)
            
            # Basic validation
            validation = self._validate_schema(data)
            results['valid'] = len(validation['errors']) == 0
            results['errors'] = validation['errors']
            results['warnings'] = validation['warnings']
            results['type'] = validation['type']
            
        except json.JSONDecodeError as e:
            results['errors'].append(f"Invalid JSON: {str(e)}")
        except Exception as e:
            results['errors'].append(f"Validation error: {str(e)}")
        
        return results
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract all structured data from the page"""
        structured_data = []
        
        # Extract JSON-LD
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in json_ld_scripts:
            try:
                # Clean the JSON string
                json_str = script.string.strip()
                if json_str:
                    data = json.loads(json_str)
                    if isinstance(data, list):
                        structured_data.extend(data)
                    else:
                        structured_data.append(data)
            except json.JSONDecodeError:
                continue
        
        # Extract Microdata (basic support)
        microdata_items = soup.find_all(attrs={'itemscope': True})
        for item in microdata_items:
            microdata = self._parse_microdata(item)
            if microdata:
                structured_data.append(microdata)
        
        return structured_data
    
    def _parse_microdata(self, element) -> Optional[Dict]:
        """Parse microdata from HTML element"""
        itemtype = element.get('itemtype', '')
        if not itemtype:
            return None
        
        microdata = {
            '@type': itemtype.split('/')[-1],
            '_format': 'microdata'
        }
        
        # Extract properties
        properties = element.find_all(attrs={'itemprop': True})
        for prop in properties:
            prop_name = prop.get('itemprop')
            prop_value = (
                prop.get('content') or 
                prop.get('href') or 
                prop.get('src') or 
                prop.text.strip()
            )
            if prop_name and prop_value:
                microdata[prop_name] = prop_value
        
        return microdata
    
    def _validate_schema(self, schema: Dict, index: int = 0) -> Dict:
        """Validate individual schema object"""
        validation = {
            'type': 'unknown',
            'errors': [],
            'warnings': [],
            'index': index
        }
        
        # Check for @type
        if '@type' not in schema:
            validation['errors'].append(f"Schema {index}: Missing @type property")
        else:
            validation['type'] = schema['@type']
        
        # Check for @context (JSON-LD)
        if '_format' not in schema and '@context' not in schema:
            validation['warnings'].append(
                f"Schema {index}: Missing @context. Should reference schema.org"
            )
        
        # Type-specific validation
        schema_type = schema.get('@type', '').lower()
        
        if schema_type in ['organization', 'localBusiness']:
            self._validate_organization(schema, validation)
        elif schema_type == 'product':
            self._validate_product(schema, validation)
        elif schema_type in ['article', 'newsarticle', 'blogposting']:
            self._validate_article(schema, validation)
        elif schema_type == 'breadcrumblist':
            self._validate_breadcrumb(schema, validation)
        elif schema_type == 'faqpage':
            self._validate_faq(schema, validation)
        elif schema_type == 'recipe':
            self._validate_recipe(schema, validation)
        
        return validation
    
    def _validate_organization(self, schema: Dict, validation: Dict):
        """Validate Organization schema"""
        required_fields = ['name', 'url']
        recommended_fields = ['logo', 'sameAs', 'contactPoint']
        
        for field in required_fields:
            if field not in schema:
                validation['errors'].append(
                    f"Organization: Missing required field '{field}'"
                )
        
        for field in recommended_fields:
            if field not in schema:
                validation['warnings'].append(
                    f"Organization: Missing recommended field '{field}'"
                )
        
        # Validate logo
        if 'logo' in schema:
            logo = schema['logo']
            if isinstance(logo, dict) and '@type' not in logo:
                validation['warnings'].append(
                    "Organization: Logo should be an ImageObject with @type"
                )
    
    def _validate_product(self, schema: Dict, validation: Dict):
        """Validate Product schema"""
        required_fields = ['name', 'image']
        recommended_fields = ['description', 'sku', 'offers', 'aggregateRating', 'brand']
        
        for field in required_fields:
            if field not in schema:
                validation['errors'].append(
                    f"Product: Missing required field '{field}'"
                )
        
        for field in recommended_fields:
            if field not in schema:
                validation['warnings'].append(
                    f"Product: Missing recommended field '{field}'"
                )
        
        # Validate offers
        if 'offers' in schema:
            offers = schema['offers']
            if isinstance(offers, dict):
                offers = [offers]
            
            for offer in offers:
                if 'price' not in offer:
                    validation['errors'].append(
                        "Product: Offer missing required 'price' field"
                    )
                if 'priceCurrency' not in offer:
                    validation['errors'].append(
                        "Product: Offer missing required 'priceCurrency' field"
                    )
    
    def _validate_article(self, schema: Dict, validation: Dict):
        """Validate Article schema"""
        required_fields = ['headline', 'image', 'author', 'datePublished']
        recommended_fields = ['dateModified', 'publisher', 'mainEntityOfPage', 'description']
        
        for field in required_fields:
            if field not in schema:
                validation['errors'].append(
                    f"Article: Missing required field '{field}'"
                )
        
        for field in recommended_fields:
            if field not in schema:
                validation['warnings'].append(
                    f"Article: Missing recommended field '{field}'"
                )
        
        # Validate images
        if 'image' in schema:
            images = schema['image']
            if not isinstance(images, list):
                images = [images]
            
            if len(images) < 1:
                validation['errors'].append(
                    "Article: At least one image is required"
                )
    
    def _validate_breadcrumb(self, schema: Dict, validation: Dict):
        """Validate BreadcrumbList schema"""
        if 'itemListElement' not in schema:
            validation['errors'].append(
                "BreadcrumbList: Missing required 'itemListElement'"
            )
        else:
            items = schema['itemListElement']
            if not isinstance(items, list):
                validation['errors'].append(
                    "BreadcrumbList: itemListElement must be an array"
                )
            else:
                for i, item in enumerate(items):
                    if 'position' not in item:
                        validation['errors'].append(
                            f"BreadcrumbList: Item {i} missing 'position'"
                        )
                    if 'name' not in item:
                        validation['errors'].append(
                            f"BreadcrumbList: Item {i} missing 'name'"
                        )
    
    def _validate_faq(self, schema: Dict, validation: Dict):
        """Validate FAQPage schema"""
        if 'mainEntity' not in schema:
            validation['errors'].append(
                "FAQPage: Missing required 'mainEntity' property"
            )
        else:
            questions = schema['mainEntity']
            if not isinstance(questions, list):
                questions = [questions]
            
            for i, question in enumerate(questions):
                if '@type' not in question or question['@type'] != 'Question':
                    validation['errors'].append(
                        f"FAQPage: Item {i} should be of type 'Question'"
                    )
                if 'name' not in question:
                    validation['errors'].append(
                        f"FAQPage: Question {i} missing 'name'"
                    )
                if 'acceptedAnswer' not in question:
                    validation['errors'].append(
                        f"FAQPage: Question {i} missing 'acceptedAnswer'"
                    )
    
    def _validate_recipe(self, schema: Dict, validation: Dict):
        """Validate Recipe schema"""
        required_fields = ['name', 'image', 'recipeIngredient', 'recipeInstructions']
        recommended_fields = [
            'prepTime', 'cookTime', 'totalTime', 'recipeYield',
            'nutrition', 'aggregateRating', 'author'
        ]
        
        for field in required_fields:
            if field not in schema:
                validation['errors'].append(
                    f"Recipe: Missing required field '{field}'"
                )
        
        for field in recommended_fields:
            if field not in schema:
                validation['warnings'].append(
                    f"Recipe: Missing recommended field '{field}'"
                )
    
    def _detect_page_type(self, url: str, soup: BeautifulSoup, schemas: List[Dict]) -> str:
        """Detect the type of page based on URL and content"""
        url_lower = url.lower()
        
        # Check URL patterns
        if url.endswith('/') or '/home' in url_lower:
            return 'homepage'
        elif '/product' in url_lower or '/shop' in url_lower:
            return 'product'
        elif '/blog' in url_lower or '/article' in url_lower or '/post' in url_lower:
            return 'article'
        elif '/contact' in url_lower or '/about' in url_lower:
            return 'local'
        elif '/event' in url_lower:
            return 'event'
        elif '/faq' in url_lower:
            return 'faq'
        elif '/recipe' in url_lower:
            return 'recipe'
        
        # Check existing schemas
        schema_types = [s.get('@type', '').lower() for s in schemas if isinstance(s, dict)]
        if 'product' in schema_types:
            return 'product'
        elif any(t in schema_types for t in ['article', 'newsarticle', 'blogposting']):
            return 'article'
        
        # Default
        return 'general'
    
    def _generate_recommendations(self, page_type: str, found_schemas: List[str]) -> List[str]:
        """Generate schema recommendations based on page type"""
        recommendations = []
        
        # Get recommended schemas for page type
        recommended = self.recommended_schemas.get(page_type, [])
        found_lower = [s.lower() for s in found_schemas]
        
        # Check for missing recommended schemas
        for schema_type in recommended:
            if schema_type.lower() not in found_lower:
                recommendations.append(
                    f"Consider adding {schema_type} schema for {page_type} pages"
                )
        
        # General recommendations
        if not found_schemas:
            recommendations.append(
                "No structured data found. Add schema markup to improve search appearance"
            )
        
        if 'WebSite' not in found_schemas and page_type == 'homepage':
            recommendations.append(
                "Add WebSite schema with SearchAction for sitelinks search box"
            )
        
        if page_type == 'product' and 'Review' not in found_schemas:
            recommendations.append(
                "Add Review schema to display star ratings in search results"
            )
        
        if page_type == 'article' and 'BreadcrumbList' not in found_schemas:
            recommendations.append(
                "Add BreadcrumbList schema for better navigation in search results"
            )
        
        return recommendations
    
    def _calculate_score(self, results: Dict) -> int:
        """Calculate validation score"""
        if results['status'] == 'error':
            return 0
        
        base_score = 100
        
        # Deduct for errors (10 points each)
        base_score -= len(results['errors']) * 10
        
        # Deduct for warnings (5 points each)
        base_score -= len(results['warnings']) * 5
        
        # Bonus for having schemas
        if results['schemas_found']:
            base_score += 10
        
        return max(0, min(100, base_score))
    
    def generate_report(self, results: Dict) -> str:
        """Generate validation report"""
        lines = [
            "=" * 60,
            "SCHEMA VALIDATION REPORT",
            "=" * 60,
            f"URL: {results['url']}",
            f"Page Type: {results.get('page_type', 'unknown')}",
            f"Validation Score: {results.get('score', 0)}%",
            f"Timestamp: {results['timestamp']}",
            ""
        ]
        
        # Schemas found
        if results['schemas_found']:
            lines.extend([
                "SCHEMAS FOUND",
                "-" * 40
            ])
            for schema in results['schemas_found']:
                lines.append(f"  - {schema}")
            lines.append("")
        
        # Errors
        if results['errors']:
            lines.extend([
                "ERRORS",
                "-" * 40
            ])
            for error in results['errors']:
                lines.append(f"  ❌ {error}")
            lines.append("")
        
        # Warnings
        if results['warnings']:
            lines.extend([
                "WARNINGS",
                "-" * 40
            ])
            for warning in results['warnings']:
                lines.append(f"  ⚠️  {warning}")
            lines.append("")
        
        # Recommendations
        if results['recommendations']:
            lines.extend([
                "RECOMMENDATIONS",
                "-" * 40
            ])
            for rec in results['recommendations']:
                lines.append(f"  💡 {rec}")
        
        lines.extend([
            "",
            "=" * 60,
            "Report generated by SEO Audit Toolkit",
            "Created by Youssef Hodaigui - Mindflow Marketing",
            "https://youssefhodaigui.com"
        ])
        
        return "\n".join(lines)


# Command line interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python schema_validator.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    validator = SchemaValidator()
    
    print(f"Validating schema markup for {url}...")
    results = validator.validate_url(url)
    
    print("\nResults:")
    print(validator.generate_report(results))
