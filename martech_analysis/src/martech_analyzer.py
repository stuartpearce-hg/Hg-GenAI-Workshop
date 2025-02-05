import csv
import requests
from bs4 import BeautifulSoup, Comment
from typing import List, Dict, Set
from urllib.parse import urlparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from requests.exceptions import Timeout, RequestException

class MartechAnalyzer:
    def __init__(self, todo_file: str, output_csv: str):
        self.todo_file = todo_file
        self.output_csv = output_csv
        self.results = []
        
    def load_next_brand(self) -> str:
        with open(self.todo_file, 'r') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            if line.startswith('- [ ]'):
                brand = line[5:].strip()
                # Mark as processed
                lines[i] = line.replace('- [ ]', '- [x]')
                with open(self.todo_file, 'w') as f:
                    f.writelines(lines)
                return brand
        return None
    
    def find_domains(self, brand: str) -> List[str]:
        """Find domain variations for a brand."""
        domains = set()
        
        # Clean brand name for domain construction
        clean_brand = brand.lower().replace("'", "").replace(" ", "")
        
        # Common domain patterns - limited to main TLDs
        tlds = ['.com', '.co.uk']
        patterns = [
            f"www.{clean_brand}",  # www.brand.com
            clean_brand            # brand.com
        ]
        
        # Generate domain combinations
        for pattern in patterns:
            for tld in tlds:
                domains.add(f"{pattern}{tld}")
        
        # Special case for brands that might have 'company' or 'corp' in domain
        domains.add(f"{clean_brand}company.com")
        domains.add(f"{clean_brand}corp.com")
        
        # Filter domains that actually resolve or have web servers
        valid_domains = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for domain in domains:
            try:
                response = requests.head(
                    f"https://{domain}",
                    timeout=3,
                    allow_redirects=True,
                    headers=headers
                )
                if response.status_code < 400:
                    valid_domains.append(domain)
                    print(f"Found valid domain: {domain}")
            except (Timeout, RequestException) as e:
                print(f"Connection error for {domain}: {str(e)}")
                continue
            except Exception as e:
                print(f"Unexpected error for {domain}: {str(e)}")
                continue
        
        return valid_domains if valid_domains else [f"www.{clean_brand}.com"]
    
    def analyze_domain(self, domain: str) -> Dict[str, Set[str]]:
        technologies = {
            'cms': set(),
            'personalization': set(),
            'search': set()
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(
                f"https://{domain}",
                timeout=3,
                headers=headers
            )
            response.raise_for_status()
            
            html_content = response.text.lower()
            soup = BeautifulSoup(html_content, 'html.parser')
            
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
            
        return technologies
    
    def _analyze_meta_tag(self, tag, technologies: Dict[str, Set[str]]):
        # Common CMS indicators
        if tag.get('name') == 'generator':
            content = tag.get('content', '').lower()
            if 'wordpress' in content:
                technologies['cms'].add('WordPress')
            elif 'drupal' in content:
                technologies['cms'].add('Drupal')
            elif 'joomla' in content:
                technologies['cms'].add('Joomla')
                
    def _analyze_script_tag(self, tag, technologies: Dict[str, Set[str]]):
        src = tag.get('src', '').lower()
        
        # Personalization tools
        if 'optimizely' in src:
            technologies['personalization'].add('Optimizely')
        elif 'adobe' in src and 'target' in src:
            technologies['personalization'].add('Adobe Target')
            
        # Search vendors
        if 'algolia' in src:
            technologies['search'].add('Algolia')
        elif 'elasticsearch' in src:
            technologies['search'].add('Elasticsearch')
            
    def process_brands(self):
        print("Starting brand analysis...")
        while True:
            brand = self.load_next_brand()
            if brand is None:
                break
                
            print(f"\nAnalyzing brand: {brand}")
            domains = self.find_domains(brand)
            print(f"Found {len(domains)} domains for {brand}")
            
            brand_tech_stack = {
                'cms': defaultdict(float),
                'personalization': defaultdict(float),
                'search': defaultdict(float)
            }
            
            for domain in domains:
                try:
                    print(f"Analyzing domain: {domain}")
                    tech_stack = self.analyze_domain(domain)
                    
                    # Calculate weights for each category on this domain
                    for category in tech_stack:
                        if tech_stack[category]:
                            weight = 1.0 / len(tech_stack[category])
                            for tech in tech_stack[category]:
                                brand_tech_stack[category][tech] += weight
                    
                    # Store raw results
                    self.results.append({
                        'brand': brand,
                        'domain': domain,
                        'cms': ','.join(tech_stack['cms']),
                        'personalization': ','.join(tech_stack['personalization']),
                        'search': ','.join(tech_stack['search'])
                    })
                except Exception as e:
                    print(f"Error analyzing {domain}: {str(e)}")
                    continue
            
            # Add weighted results for the brand
            for category in ['cms', 'personalization', 'search']:
                for tech, weight in brand_tech_stack[category].items():
                    self.results.append({
                        'brand': brand,
                        'domain': '*BRAND_TOTAL*',
                        'technology_type': category,
                        'technology': tech,
                        'weight': weight
                    })
                
        self._save_results()
    
    def _save_results(self):
        # Save detailed domain results
        domain_results = [r for r in self.results if 'cms' in r]
        with open('martech_analysis/output/domain_results.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['brand', 'domain', 'cms', 'personalization', 'search'])
            writer.writeheader()
            writer.writerows(domain_results)
            
        # Save weighted brand results
        brand_results = [r for r in self.results if 'technology_type' in r]
        with open(self.output_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['brand', 'domain', 'technology_type', 'technology', 'weight'])
            writer.writeheader()
            writer.writerows(brand_results)
    
    def generate_charts(self):
        df = pd.read_csv(self.output_csv)
        
        # Process each technology category
        categories = ['cms', 'personalization', 'search']
        for category in categories:
            self._generate_category_charts(df, category)
    
    def _generate_category_charts(self, df: pd.DataFrame, category: str):
        # Split multiple technologies per cell
        tech_counts = defaultdict(int)
        brand_counts = defaultdict(set)
        
        for _, row in df.iterrows():
            if pd.notna(row[category]):
                techs = row[category].split(',')
                for tech in techs:
                    tech = tech.strip()
                    if tech:
                        tech_counts[tech] += 1
                        brand_counts[tech].add(row['brand'])
        
        # Convert brand sets to counts
        brand_counts = {k: len(v) for k, v in brand_counts.items()}
        
        # Create domain count chart
        plt.figure(figsize=(10, 6))
        plt.bar(tech_counts.keys(), tech_counts.values())
        plt.title(f'{category.title()} Distribution by Domain Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'martech_analysis/output/{category}_domain_distribution.png')
        plt.close()
        
        # Create brand count chart
        plt.figure(figsize=(10, 6))
        plt.bar(brand_counts.keys(), brand_counts.values())
        plt.title(f'{category.title()} Distribution by Brand Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'martech_analysis/output/{category}_brand_distribution.png')
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
        if 'wp-content' in content or 'wp-includes' in content:
            technologies['cms'].add('WordPress')
        if 'drupal.settings' in content:
            technologies['cms'].add('Drupal')
        if 'sitecore' in content:
            technologies['cms'].add('Sitecore')
            
        if 'mboxCreate' in content or 'adobe.target' in content:
            technologies['personalization'].add('Adobe Target')
        if 'tealium' in content:
            technologies['personalization'].add('Tealium')
            
        if 'instantsearch.js' in content:
            technologies['search'].add('Algolia')
        if 'coveo' in content:
            technologies['search'].add('Coveo')

if __name__ == "__main__":
    analyzer = MartechAnalyzer(
        todo_file='/home/ubuntu/todo.txt',
        output_csv='martech_analysis/output/martech_results.csv'
    )
    analyzer.process_brands()
    analyzer.generate_charts()
