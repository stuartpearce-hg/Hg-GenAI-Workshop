with open('martech_analysis/data/brands.txt', 'r') as f:
    brands = [line.strip() for line in f if line.strip()]

with open('/home/ubuntu/todo.txt', 'w') as f:
    for brand in brands:
        f.write(f'- [ ] {brand}\n')
