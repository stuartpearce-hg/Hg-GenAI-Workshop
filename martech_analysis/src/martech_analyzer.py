import csv
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Set
from urllib.parse import urlparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

class MartechAnalyzer:
    def __init__(self, brands_file: str, output_csv: str):
        self.brands_file = brands_file
        self.output_csv = output_csv
        self.results = []
        
    def load_brands(self) -> List[str]:
        with open(self.brands_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    
    def find_domains(self, brand: str) -> List[str]:
        # TODO: Implement domain discovery logic
        # For now, return basic domain pattern
        return [f"www.{brand.lower().replace(' ', '')}.com"]
    
    def analyze_domain(self, domain: str) -> Dict[str, Set[str]]:
        technologies = {
            'cms': set(),
            'personalization': set(),
            'search': set()
        }
        
        try:
            response = requests.get(f"https://{domain}", timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Meta tags analysis
            meta_tags = soup.find_all('meta')
            for tag in meta_tags:
                self._analyze_meta_tag(tag, technologies)
                
            # Script tags analysis
            script_tags = soup.find_all('script')
            for tag in script_tags:
                self._analyze_script_tag(tag, technologies)
                
        except Exception as e:
            print(f"Error analyzing {domain}: {str(e)}")
            
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
        brands = self.load_brands()
        
        for brand in brands:
            domains = self.find_domains(brand)
            for domain in domains:
                tech_stack = self.analyze_domain(domain)
                self.results.append({
                    'brand': brand,
                    'domain': domain,
                    'cms': ','.join(tech_stack['cms']),
                    'personalization': ','.join(tech_stack['personalization']),
                    'search': ','.join(tech_stack['search'])
                })
                
        self._save_results()
    
    def _save_results(self):
        with open(self.output_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['brand', 'domain', 'cms', 'personalization', 'search'])
            writer.writeheader()
            writer.writerows(self.results)
    
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

if __name__ == "__main__":
    analyzer = MartechAnalyzer(
        brands_file='martech_analysis/data/brands.txt',
        output_csv='martech_analysis/output/martech_results.csv'
    )
    analyzer.process_brands()
    analyzer.generate_charts()
