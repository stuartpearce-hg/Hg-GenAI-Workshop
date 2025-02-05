import csv
import requests
import urllib3
from bs4 import BeautifulSoup, Comment
from typing import List, Dict, Set, Optional
from urllib.parse import urlparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from requests.exceptions import Timeout, RequestException

# Suppress SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MartechAnalyzer:
    def __init__(self, todo_file: str, output_csv: str):
        self.todo_file = todo_file
        self.output_csv = output_csv
        self.results = []
        
        # Ensure output directory exists
        import os
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        
    def load_next_brand(self) -> Optional[str]:
        print("\nLoading next brand from todo file...")
        try:
            with open(self.todo_file, 'r') as f:
                lines = f.readlines()
                print(f"Found {len(lines)} lines in todo file")
            
            for i, line in enumerate(lines):
                print(f"Checking line {i+1}: {line.strip()}")
                if line.startswith('- [ ]'):
                    brand = line[5:].strip()
                    print(f"Found unprocessed brand: {brand}")
                    # Mark as processed
                    lines[i] = line.replace('- [ ]', '- [x]')
                    with open(self.todo_file, 'w') as f:
                        f.writelines(lines)
                    return brand
            print("No unprocessed brands found in todo file")
            return None
        except Exception as e:
            print(f"Error loading brands: {str(e)}")
            return None
    
    def find_domains(self, brand: str) -> List[str]:
        """Find domain variations for a brand."""
        print(f"\nFinding domains for brand: {brand}")
        domains = set()
        
        # Clean brand name for domain construction
        clean_brand = brand.lower().replace("'", "").replace(" ", "")
        print(f"Cleaned brand name: {clean_brand}")
        
        # Common domain patterns - limited to main TLDs
        tlds = ['.com', '.co.uk']
        patterns = [
            f"www.{clean_brand}",  # www.brand.com
            clean_brand            # brand.com
        ]
        
        # Generate domain combinations
        for pattern in patterns:
            for tld in tlds:
                domain = f"{pattern}{tld}"
                domains.add(domain)
                print(f"Generated domain: {domain}")
        
        # Special case for brands that might have 'company' or 'corp' in domain
        special_domains = [
            f"{clean_brand}company.com",
            f"{clean_brand}corp.com"
        ]
        for domain in special_domains:
            domains.add(domain)
            print(f"Generated special domain: {domain}")
        
        print(f"Testing {len(domains)} potential domains...")
        
        # For testing, return first domain without validation
        test_domain = next(iter(domains))
        print(f"Using test domain: {test_domain}")
        return [test_domain]
    
    def analyze_domain(self, domain: str) -> Dict[str, str]:
        print(f"\n=== Detailed Analysis for {domain} ===")
        technologies = {
            'cms': set(),
            'personalization': set(),
            'search': set()
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        try:
            print(f"\nAnalyzing HTML content for {domain}")
            
            # Check for Adobe Experience Cloud domains
            adobe_domains = [
                f"{domain.split('.')[0]}.tt.omtrdc.net",
                f"{domain.split('.')[0]}.sc.omtrdc.net",
                f"{domain.split('.')[0]}.demdex.net"
            ]
            
            for adobe_domain in adobe_domains:
                try:
                    adobe_response = requests.head(
                        f"https://{adobe_domain}",
                        timeout=5,
                        headers=headers,
                        verify=False
                    )
                    if adobe_response.status_code < 400:
                        print(f"Found Adobe domain: {adobe_domain}")
                        technologies['cms'].add('Adobe Experience Manager')
                        technologies['personalization'].add('Adobe Target')
                        break
                except:
                    continue
                    
            response = requests.get(
                f"https://{domain}",
                timeout=10,
                headers=headers,
                verify=False
            )
            response.raise_for_status()
            
            html_content = response.text
            print(f"Retrieved {len(html_content)} bytes of HTML content")
            
            # Initial HTML analysis
            html_lower = html_content.lower()
            
            # Adobe detection
            if any(x in html_lower for x in ['mbox.js', 'at.js', 'adobe.target', 'mboxdefine', '/etc.clientlibs/', 'dam/experience-fragments']):
                technologies['cms'].add('Adobe Experience Manager')
                technologies['personalization'].add('Adobe Target')
            
            # Sitecore detection
            if any(x in html_lower for x in ['sitecore', '_scwebapp', 'sc_site', 'sxa-', '/sitecore/shell']):
                technologies['cms'].add('Sitecore')
                technologies['personalization'].add('Sitecore Personalization')
            
            # Optimizely detection
            if any(x in html_lower for x in ['optimizely', 'optimizelyDataApi', 'optimizely.init']):
                technologies['personalization'].add('Optimizely')
            
            # Contentful detection
            if any(x in html_lower for x in ['contentful', 'ctfl-', 'contentful-delivery']):
                technologies['cms'].add('Contentful')
            
            # Drupal detection
            if any(x in html_lower for x in ['drupal', 'sites/default/files', 'drupal.settings']):
                technologies['cms'].add('Drupal')
            
            # Salesforce detection
            if any(x in html_lower for x in ['salesforce', 'sfmc-', 'force.com', 'marketing-cloud-']):
                technologies['personalization'].add('Salesforce')
                technologies['search'].add('Salesforce Search')
            
            # Acquia detection
            if any(x in html_lower for x in ['acquia', 'acquiadam', 'acquia-content']):
                technologies['cms'].add('Acquia')
            
            # Liferay detection
            if any(x in html_lower for x in ['liferay', 'lfr-', 'liferay-portal']):
                technologies['cms'].add('Liferay')
            
            # BloomReach detection
            if any(x in html_lower for x in ['bloomreach', 'br-', 'hippo:docbase', 'brx-']):
                technologies['cms'].add('BloomReach')
                technologies['search'].add('BloomReach Search')
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Analyze meta tags, scripts, and comments
            self._analyze_meta_tag(soup.find_all('meta'), technologies)
            self._analyze_script_tag(soup.find_all('script'), technologies)
            self._analyze_link_tag(soup.find_all('link'), technologies)
            self._analyze_comment(soup.find_all(string=lambda text: isinstance(text, Comment)), technologies)
            self._analyze_html_content(html_content, technologies)
            
        except Exception as e:
            print(f"Error analyzing {domain}: {str(e)}")
        
        # Convert sets to comma-separated strings
        result = {
            'cms': ','.join(technologies['cms']) or 'Unknown',
            'personalization': ','.join(technologies['personalization']) or 'Unknown',
            'search': ','.join(technologies['search']) or 'Unknown'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        try:
            print(f"\nAnalyzing HTML content for {domain}")
            
            # Check for Adobe Target and Experience Cloud domains
            adobe_domains = [
                f"{domain.split('.')[0]}.tt.omtrdc.net",
                f"{domain.split('.')[0]}.sc.omtrdc.net",
                f"{domain.split('.')[0]}.demdex.net"
            ]
            
            for adobe_domain in adobe_domains:
                try:
                    adobe_response = requests.head(
                        f"https://{adobe_domain}",
                        timeout=5,
                        headers=headers,
                        verify=False
                    )
                    if adobe_response.status_code < 400:
                        print(f"Found Adobe domain: {adobe_domain}")
                        technologies['personalization'].add('Adobe Target')
                        break
                except:
                    continue
            
            response = requests.get(
                f"https://{domain}",
                timeout=10,
                headers=headers,
                verify=False
            )
            response.raise_for_status()
            
            html_content = response.text
            print(f"Retrieved {len(html_content)} bytes of HTML content")
            
            # Check for common technology indicators in raw HTML
            html_lower = html_content.lower()
            if any(x in html_lower for x in ['mbox.js', 'at.js', 'adobe.target', 'mboxdefine']):
                technologies['personalization'].add('Adobe Target')
            if any(x in html_lower for x in ['sitecore', '_scwebapp', 'sc_site']):
                technologies['cms'].add('Sitecore')
                
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check for vendor-specific elements
            if soup.find_all(class_=lambda x: isinstance(x, str) and ('sc_' in x or 'sitecore' in x)):
                technologies['cms'].add('Sitecore')
            if soup.find_all(class_=lambda x: isinstance(x, str) and ('mboxDefault' in x or 'target-' in x)):
                technologies['personalization'].add('Adobe Target')
            
            # Meta tags analysis
            meta_tags = soup.find_all('meta')
            for tag in meta_tags:
                self._analyze_meta_tag(tag, technologies)
                
            # Script tags analysis
            script_tags = soup.find_all('script')
            for tag in script_tags:
                self._analyze_script_tag(tag, technologies)
                
            # Link tags analysis
            link_tags = soup.find_all('link')
            for tag in link_tags:
                self._analyze_link_tag(tag, technologies)
                
            # HTML comments analysis
            comments = soup.find_all(string=lambda text: isinstance(text, Comment))
            for comment in comments:
                self._analyze_comment(comment, technologies)
                
            # Full HTML content analysis
            self._analyze_html_content(html_content, technologies)
                
        except (Timeout, RequestException) as e:
            print(f"Connection error analyzing {domain}: {str(e)}")
        except Exception as e:
            print(f"Unexpected error analyzing {domain}: {str(e)}")
            
        return result
    
    def _analyze_meta_tag(self, tag, technologies: Dict[str, Set[str]]):
        content = tag.get('content', '').lower()
        name = tag.get('name', '').lower()
        
        # CMS detection
        if name == 'generator':
            cms_patterns = {
                'wordpress': 'WordPress',
                'drupal': 'Drupal',
                'joomla': 'Joomla',
                'sitecore': 'Sitecore',
                'adobe': 'Adobe Experience Manager',
                'umbraco': 'Umbraco'
            }
            for pattern, cms in cms_patterns.items():
                if pattern in content:
                    technologies['cms'].add(cms)
                    
        # Personalization detection
        if 'adobe target' in content or 'adobe marketing cloud' in content:
            technologies['personalization'].add('Adobe Target')
        if 'optimizely' in content:
            technologies['personalization'].add('Optimizely')
            
        # Search detection
        if 'algolia' in content:
            technologies['search'].add('Algolia')
        if 'coveo' in content:
            technologies['search'].add('Coveo')
                
    def _analyze_script_tag(self, tag, technologies: Dict[str, Set[str]]):
        try:
            src = tag.get('src', '').lower() if tag.get('src') else ''
            script_content = tag.string.lower() if tag.string else ''
            data_attrs = ' '.join([f"{k}={v}" for k, v in tag.attrs.items() if k.startswith('data-')]).lower()
            
            # Print debug info for script analysis
            if src:
                print(f"Analyzing script src: {src}")
            if data_attrs:
                print(f"Found data attributes: {data_attrs}")
            
            patterns = {
                'cms': {
                    'wordpress': ['wp-content', 'wp-includes', 'wp-json', '/wp-'],
                    'drupal': ['drupal', 'sites/all/modules', 'sites/default/files'],
                    'sitecore': ['sitecore', '_scwebapp', 'sitecore-config'],
                    'aem': ['aem-grid', '/etc/clientlibs', 'foundation-layout', '/content/dam/', 'adobe.target'],
                    'umbraco': ['umbraco', 'umb_', 'umbraco-forms'],
                    'kentico': ['kentico', '/cmssiteutils/', 'kentico.forms']
                },
                'personalization': {
                    'adobe target': ['mbox', 'target.js', 'adobe.target', 'at.js', 'mbox.js', 'target-global-mbox', 'tt.omtrdc.net'],
                    'optimizely': ['optimizely', 'cdn.optimizely.com', 'optimizelyDataApi'],
                    'tealium': ['tealium', 'utag.js', 'utag_data', 'tags.tiqcdn.com'],
                    'dynamic yield': ['dy-', 'dynamicyield', 'cdn.dynamicyield.com'],
                    'monetate': ['monetate', 'shopinterest', 'monetate.net']
                },
                'search': {
                    'algolia': ['algolia', 'algoliasearch', 'instantsearch.js', 'cdn.algolia.net'],
                    'elasticsearch': ['elasticsearch', '_msearch', 'elastic.co'],
                    'coveo': ['coveo', 'coveoua', 'static.cloud.coveo.com'],
                    'searchspring': ['searchspring', 'ss-wrapper', 'searchspring.net'],
                    'klevu': ['klevu', 'klevu-', 'js.klevu.com']
                }
            }
            
            for category, vendors in patterns.items():
                for vendor, vendor_patterns in vendors.items():
                    for pattern in vendor_patterns:
                        if (pattern in src or 
                            pattern in script_content or 
                            pattern in data_attrs):
                            vendor_name = ' '.join(word.capitalize() for word in vendor.split())
                            technologies[category].add(vendor_name)
                            print(f"Found {category} technology: {vendor_name} (matched pattern: {pattern})")
                            break
                    
        except Exception as e:
            print(f"Error analyzing script tag: {str(e)}")
            
        # Check for common JavaScript libraries and frameworks
        common_libs = {
            'jquery': 'jQuery',
            'react': 'React',
            'angular': 'Angular',
            'vue': 'Vue.js'
        }
        for lib, name in common_libs.items():
            if lib in src.lower() or lib in script_content:
                print(f"Found JavaScript library: {name}")
            
    def process_brands(self):
        print("Starting brand analysis...")
        self.results = []  # Reset results list
        
        while True:
            brand = self.load_next_brand()
            if brand is None:
                break
                
            print(f"\nAnalyzing brand: {brand}")
            domains = self.find_domains(brand)
            print(f"Found {len(domains)} domains for {brand}: {domains}")
            
            for domain in domains:
                try:
                    print(f"\nAnalyzing domain: {domain}")
                    tech_stack = self.analyze_domain(domain)
                    print(f"Technology stack detected: {tech_stack}")
                    
                    # Store domain-level results
                    domain_result = {
                        'brand': brand,
                        'domain': domain,
                        'cms': tech_stack['cms'],
                        'personalization': tech_stack['personalization'],
                        'search': tech_stack['search']
                    }
                    self.results.append(domain_result)
                    print(f"Saved domain result: {domain_result}")
                    
                    # Add brand-level results for each technology type
                    for tech_type in ['cms', 'personalization', 'search']:
                        if tech_stack[tech_type]:
                            techs = [t.strip() for t in tech_stack[tech_type].split(',') if t.strip()]
                            weight = 1.0 / len(techs) if techs else 0
                            for tech in techs:
                                brand_result = {
                                    'brand': brand,
                                    'domain': '*BRAND_TOTAL*',
                                    'technology_type': tech_type,
                                    'technology': tech,
                                    'weight': weight
                                }
                                self.results.append(brand_result)
                                print(f"Saved brand result: {brand_result}")
                    
                except Exception as e:
                    print(f"Error analyzing {domain}: {str(e)}")
                    continue
            
        self._save_results()
    
    def _save_results(self):
        output_dir = os.path.dirname(self.output_csv)
        
        print("\nDebug: Results before saving:")
        for r in self.results:
            print(f"Result entry: {r}")
        
        # Filter results by type
        domain_results = []
        brand_results = []
        
        for result in self.results:
            if isinstance(result, dict):
                if 'technology_type' in result:
                    brand_results.append(result)
                else:
                    domain_results.append(result)
        
        print(f"\nFound {len(domain_results)} domain results and {len(brand_results)} brand results")
        
        # Save detailed domain results
        domain_results_path = os.path.join(output_dir, 'domain_results.csv')
        with open(domain_results_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['brand', 'domain', 'cms', 'personalization', 'search'])
            writer.writeheader()
            writer.writerows(domain_results)
            print(f"Saved domain results to {domain_results_path}")
            
        # Save weighted brand results
        with open(self.output_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['brand', 'domain', 'technology_type', 'technology', 'weight'])
            writer.writeheader()
            writer.writerows(brand_results)
            print(f"Saved brand results to {self.output_csv}")
    
    def generate_charts(self):
        df = pd.read_csv(self.output_csv)
        
        # Process each technology category
        categories = ['cms', 'personalization', 'search']
        for category in categories:
            self._generate_category_charts(df, category)
    
    def _generate_category_charts(self, df: pd.DataFrame, category: str):
        output_dir = os.path.dirname(self.output_csv)
        
        # Filter for brand totals and get technology distribution
        brand_df = df[df['domain'] == '*BRAND_TOTAL*']
        brand_df = brand_df[brand_df['technology_type'] == category.lower()]
        
        # Group by technology and sum weights for brand-level analysis
        tech_weights = brand_df.groupby('technology')['weight'].sum().sort_values(ascending=False)
        
        # Create brand count chart
        plt.figure(figsize=(12, 6))
        sns.barplot(x=tech_weights.index, y=tech_weights.values, palette='viridis')
        plt.title(f'{category.title()} Distribution by Brand Count (Weighted)')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Weighted Brand Count')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{category}_brand_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Calculate domain-level distribution
        domain_df = df[df['domain'] != '*BRAND_TOTAL*']
        domain_techs = defaultdict(int)
        
        for _, row in domain_df.iterrows():
            if category.lower() == 'cms':
                techs = row['cms'].split(', ')
            elif category.lower() == 'personalization':
                techs = row['personalization'].split(', ')
            else:
                techs = row['search'].split(', ')
            
            for tech in techs:
                if tech:
                    domain_techs[tech] += 1
        
        # Sort and create domain count chart
        domain_counts = pd.Series(domain_techs).sort_values(ascending=False)
        
        plt.figure(figsize=(12, 6))
        sns.barplot(x=domain_counts.index, y=domain_counts.values, palette='viridis')
        plt.title(f'{category.title()} Distribution by Domain Count')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Number of Domains')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{category}_domain_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()

    def _analyze_link_tag(self, tag, technologies: Dict[str, Set[str]]):
        href = tag.get('href', '').lower()
        rel = tag.get('rel', [])
        
        cms_patterns = {
            'wp-content': 'WordPress',
            'drupal': 'Drupal',
            'sitecore': 'Sitecore',
            'kentico': 'Kentico'
        }
        
        for pattern, cms in cms_patterns.items():
            if pattern in href:
                technologies['cms'].add(cms)
                
    def _analyze_comment(self, comment: str, technologies: Dict[str, Set[str]]):
        comment_text = comment.lower()
        
        cms_patterns = {
            'generated by wordpress': 'WordPress',
            'drupal': 'Drupal',
            'sitecore': 'Sitecore',
            'umbraco': 'Umbraco',
            'episerver': 'Episerver'
        }
        
        for pattern, cms in cms_patterns.items():
            if pattern in comment_text:
                technologies['cms'].add(cms)
                
    def _analyze_html_content(self, content: str, technologies: Dict[str, Set[str]]):
        content_lower = content.lower()
        patterns = {
            'cms': {
                'Adobe Experience Manager': ['aem-grid', '/etc/clientlibs', '/content/dam/', 'cq:template', 'cq-analytics'],
                'Sitecore': ['sitecore', '_scwebapp', 'sxa-', '/sitecore/shell', 'sc_site'],
                'Contentful': ['contentful', 'ctfl-', 'contentful-delivery', 'contentful-space'],
                'Drupal': ['drupal.settings', 'drupal-', 'sites/all/modules', 'sites/default/files'],
                'Acquia': ['acquia', 'acquiadam', 'acquia-content', 'acquia-site-studio'],
                'Liferay': ['liferay', 'lfr-', 'liferay-portal', 'liferay-theme'],
                'BloomReach': ['bloomreach', 'br-', 'hippo:docbase', 'brx-', 'br-snippet']
            },
            'personalization': {
                'Adobe Target': ['mboxcreate', 'adobe.target', 'at.js', 'mbox.js', 'target-global-mbox', 'tt.omtrdc.net'],
                'Sitecore Personalization': ['sitecore-personalization', 'sc-personalization', 'sitecore-tracking'],
                'Optimizely': ['optimizely', 'optimizelyDataApi', 'optimizely.init', 'optimizely-snippet'],
                'Salesforce': ['salesforce', 'sfmc-', 'force.com', 'marketing-cloud-', 'mc-']
            },
            'search': {
                'BloomReach Search': ['bloomreach-search', 'br-search', 'br-suggest'],
                'Salesforce Search': ['salesforce-search', 'commerce-cloud-search', 'einstein-search'],
                'Sitecore Search': ['sitecore-search', 'coveo', 'sitecore-suggest']
            }
        }
        
        for category, vendors in patterns.items():
            for vendor, vendor_patterns in vendors.items():
                for pattern in vendor_patterns:
                    if pattern in content_lower:
                        vendor_name = vendor.title()
                        technologies[category].add(vendor_name)
                        print(f"Found {category} technology: {vendor_name} (matched pattern: {pattern})")
                        break

if __name__ == "__main__":
    import os
    
    # Get project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    # Set up paths
    output_dir = os.path.join(project_root, 'martech_analysis', 'output')
    data_dir = os.path.join(project_root, 'martech_analysis', 'data')
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create todo file if it doesn't exist
    todo_path = os.path.join(data_dir, 'todo.txt')
    if not os.path.exists(todo_path):
        with open(os.path.join(data_dir, 'brands.txt'), 'r') as f:
            brands = [line.strip() for line in f if line.strip()]
        with open(todo_path, 'w') as f:
            for brand in brands:
                f.write(f'- [ ] {brand}\n')
    
    analyzer = MartechAnalyzer(
        todo_file=todo_path,
        output_csv=os.path.join(output_dir, 'martech_results.csv')
    )
    
    try:
        analyzer.process_brands()
        analyzer.generate_charts()
        print("\nAnalysis complete! Check the output files:")
        print("1. martech_analysis/output/domain_results.csv")
        print("2. martech_analysis/output/martech_results.csv")
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
