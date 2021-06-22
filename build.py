from pathlib import Path
import os
from shutil import copy
from tqdm import tqdm

from lib import builder
from lib.html_parser import LinkParser
from lib.rss import generate_rss_feed_posts
from lib.sitemap import generate_sitemap

output_dir = '_output'
posts_dir = 'posts'

post_files = Path('posts').rglob('*.html')
page_files = Path('pages').rglob('*.html')
project_files = Path('projects').rglob('*.html')
asset_files = Path('assets').rglob('*')

context = {
    'projects': [
        builder.parse_file_and_create_page_entity(file_path)
        for file_path in tqdm(project_files, desc='Parse projects')
    ],
    'pages': [
        builder.parse_file_and_create_page_entity(file_path)
        for file_path in tqdm(page_files, desc='Parse pages')
    ],
    'posts': [
        builder.parse_file_and_create_page_entity(file_path)
        for file_path in tqdm(post_files, desc='Parse posts')
    ],
    'external_links': [],
    'tags': [],
    'pages_grouped_by_tags': {}
}

context['posts'].sort(key=lambda x: x.date, reverse=True)
context['pages'].sort(key=lambda x: x.date, reverse=True)
context['projects'].sort(key=lambda x: x.date, reverse=True)

for post in tqdm(context['posts'] + context['projects'], desc='Group pages by tags'):
    for tag in post.tags.split(' '):
        if tag not in context['tags']:
            context['tags'].append(tag)

        if tag not in context['pages_grouped_by_tags']:
            context['pages_grouped_by_tags'][tag] = list()

        context['pages_grouped_by_tags'][tag].append(post)

for tag_group, pages_by_tag in context['pages_grouped_by_tags'].items():
    pages_by_tag.sort(key=lambda x: x.date, reverse=True)

context['tags'].sort()

for entry in context['posts'] + context['pages'] + context['projects']:
    parser = LinkParser()
    parser.feed(entry.content)
    for link in parser.links:
        if (link.startswith('https://') or link.startswith('http://')) and link not in context['external_links']:
            context['external_links'].append(link)

builder.set_blog_post_urls(context['posts'])
builder.set_related_pages(context['posts'] + context['projects'], context['pages_grouped_by_tags'])
builder.set_urls(context['projects'], 'projects')
builder.set_urls(context['pages'])

for page in context['pages']: page.show_create_date = False

builder.render_entries(context['posts'], context)
builder.render_entries(context['pages'], context)
builder.render_entries(context['projects'], context)
builder.render_and_write_tags_to_disk(context['tags'], context['pages_grouped_by_tags'], output_dir)

builder.write_blog_posts(context['posts'], output_dir)
builder.write_list_entries(context['pages'], output_dir)
builder.write_list_entries(context['projects'], output_dir, 'projects')

with open(os.path.join(output_dir, 'blog/index.html'), 'w') as output_file:
    output_file.write(builder.render_list_index('Blog', context['posts']))
with open(os.path.join(output_dir, 'projects/index.html'), 'w') as output_file:
    output_file.write(builder.render_list_index('Projekte', context['projects']))

if not os.path.exists(os.path.join(output_dir, 'assets')):
    os.makedirs(os.path.join(output_dir, 'assets'))

for asset_file in tqdm(asset_files, desc='Copy assets'):
    copy(asset_file, os.path.join(output_dir, 'assets'))

generate_sitemap(output_dir, context['pages'], context['posts'], context['tags'])
generate_rss_feed_posts(output_dir, context['posts'])
