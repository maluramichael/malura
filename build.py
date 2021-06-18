from pathlib import Path
import os
from shutil import copy
from tqdm import tqdm
import art

from lib import builder

output_dir = '_output'
posts_dir = 'posts'

tags = []
posts_grouped_by_tags = {}

print(art.text2art('Find files'))

post_files = Path('posts').rglob('*.html')
page_files = Path('pages').rglob('*.html')
project_files = Path('projects').rglob('*.html')
asset_files = Path('assets').rglob('*')

print(art.text2art('Parse files'))

projects = [builder.parse_file_and_create_page_entity(file_path) for file_path in
            tqdm(project_files, desc='Parse projects')]
posts = [builder.parse_file_and_create_page_entity(file_path) for file_path in tqdm(post_files, desc='Parse posts')]
pages = [builder.parse_file_and_create_page_entity(file_path) for file_path in tqdm(page_files, desc='Parse pages')]

posts.sort(key=lambda x: x.date, reverse=True)

# Group posts by tags and gather all tags
for post in tqdm(posts, desc='Group posts by tags'):
    for tag in post.tags.split(' '):
        if tag not in tags:
            tags.append(tag)

        if tag not in posts_grouped_by_tags:
            posts_grouped_by_tags[tag] = list()

        posts_grouped_by_tags[tag].append(post)

for tag_group, posts_by_tag in posts_grouped_by_tags.items():
    posts_by_tag.sort(key=lambda x: x.date, reverse=True)

tags.sort()

context = {
    'projects': projects,
    'pages': pages,
    'posts': posts,
}

print(art.text2art('Write to disk'))

builder.render_and_write_blog_posts_to_disk(posts, context, output_dir)
builder.render_and_write_list_entries_to_disk(pages, context, output_dir)
builder.render_and_write_list_entries_to_disk(projects, context, output_dir, 'projects')
builder.render_and_write_tags_to_disk(tags, posts_grouped_by_tags, output_dir)

with open(os.path.join(output_dir, 'blog/index.html'), 'w') as output_file:
    output_file.write(builder.render_blog_list(posts))
with open(os.path.join(output_dir, 'projects/index.html'), 'w') as output_file:
    output_file.write(builder.render_project_list(projects))

print(art.text2art('Assets'))

if not os.path.exists(os.path.join(output_dir, 'assets')):
    os.makedirs(os.path.join(output_dir, 'assets'))

for asset_file in tqdm(asset_files, desc='Copy assets'):
    copy(asset_file, os.path.join(output_dir, 'assets'))

print(art.text2art('Xml files'))

builder.generate_sitemap(output_dir, pages, posts, tags)
builder.generate_rss_feed_posts(output_dir, posts)
