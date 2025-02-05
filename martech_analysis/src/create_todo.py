import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

with open(os.path.join(project_root, 'data/brands.txt'), 'r') as f:
    brands = [line.strip() for line in f if line.strip()]

with open(os.path.join(project_root, 'data/todo.txt'), 'w') as f:
    for brand in brands:
        f.write(f'- [ ] {brand}\n')
