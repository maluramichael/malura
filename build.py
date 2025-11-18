from pathlib import Path
import os
import sys
import argparse
import subprocess
from shutil import copy, rmtree
from tqdm import tqdm
import rcssmin
from dotenv import load_dotenv

# Parse command line arguments
parser = argparse.ArgumentParser(description='Build the static site')
parser.add_argument('--clear-cache', action='store_true', help='Clear the cache before building')
args = parser.parse_args()

# Clear cache if requested
if args.clear_cache:
    cache_dir = '_cache'
    if os.path.exists(cache_dir):
        print(f'Clearing cache directory: {cache_dir}')
        rmtree(cache_dir)
        print('Cache cleared!')

# Load environment variables before importing modules that need them
load_dotenv()

# Build Tailwind CSS before processing
print('Building Tailwind CSS...')
try:
    subprocess.run(['npm', 'run', 'build:css'], check=True)
    print('Tailwind CSS built successfully!')
except subprocess.CalledProcessError as e:
    print(f'Error building Tailwind CSS: {e}')
    sys.exit(1)
except FileNotFoundError:
    print('npm not found. Skipping Tailwind CSS build.')
    print('Install Node.js and run "npm install" to enable CSS building.')

from lib import builder
from lib.html_parser import LinkParser
from lib.rss import generate_rss_feed_posts
from lib.sitemap import generate_sitemap
from lib.translations import get_translation, get_available_languages

def build_for_language(lang='de'):
    """Build site for specific language"""
    print(f"\nBuilding for language: {lang}")
    
    # Set output directory based on language
    if lang == 'de':
        output_dir = '_output'  # German at root
    else:
        output_dir = f'_output/{lang}'  # Other languages in subdirs
    
    posts_dir = 'posts'

    # Exclude backup files from processing
    post_files = [
        f for f in (list(Path('posts').rglob('*.html')) + list(Path('posts').rglob('*.md')))
        if not str(f).endswith('.backup')
    ]
    page_files = list(Path('pages').rglob('*.html'))
    project_files = list(Path('projects').rglob('*.html')) + list(Path('projects').rglob('*.md'))
    asset_files = list(Path('assets').rglob('*.*'))

    ################################
    # Parse all documents and build context
    ################################
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
        'pages_grouped_by_tags': {},
        'current_lang': lang  # Add current language to context
    }

    ################################
    # Sort context
    ################################
    context['posts'].sort(key=lambda x: x.date, reverse=True)
    context['pages'].sort(key=lambda x: x.date, reverse=True)
    # Sort projects: active first (by date desc), then abandoned (by date desc)
    context['projects'].sort(key=lambda x: (x.abandoned, -x.date.timestamp()))

    ################################
    # Group pages by tags
    ################################
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

    ################################
    # Gather external links
    ################################
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
    builder.render_and_write_tags_to_disk(context['tags'], context['pages_grouped_by_tags'], output_dir, context)

    builder.write_blog_posts(context['posts'], output_dir)
    builder.write_list_entries(context['pages'], output_dir)
    builder.write_list_entries(context['projects'], output_dir, 'projects')

    with open(os.path.join(output_dir, 'blog/index.html'), 'w', encoding='utf-8') as output_file:
        output_file.write(builder.render_list_index('Blog', context['posts'], context))
    with open(os.path.join(output_dir, 'projects/index.html'), 'w', encoding='utf-8') as output_file:
        output_file.write(builder.render_projects_index(context['projects'], context))

    if not os.path.exists(os.path.join(output_dir, 'assets')):
        os.makedirs(os.path.join(output_dir, 'assets'))

    for asset_file in tqdm(asset_files, desc='Copy assets'):
        copy(asset_file, os.path.join(output_dir, 'assets'))

    css_files = [str(file) for file in asset_files if str(file).endswith('.css')]
    combined_css_files = ''

    for css_file in css_files:
        with open(css_file, 'r') as f:
            combined_css_files += f.read()

    with open(os.path.join(output_dir, 'assets', 'styles.css'), 'w') as f:
        minified = rcssmin.cssmin(combined_css_files)
        f.write(minified)

    generate_sitemap(output_dir, context['pages'], context['posts'], context['tags'])
    generate_rss_feed_posts(output_dir, context['posts'])


# Build for all available languages
available_languages = get_available_languages()
for lang in available_languages:
    build_for_language(lang)
