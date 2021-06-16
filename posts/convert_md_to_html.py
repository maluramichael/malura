from pathlib import Path

import markdown

post_files = Path('.').rglob('*.md')

for file_path in post_files:
    with open(file_path) as read_file:
        html = markdown.markdown(read_file.read(), extensions=['codehilite', 'fenced_code'])
        with open(read_file.name.replace('.md', '.html'), 'w') as write_file:
            write_file.write(html)
