import datetime
import os
import random
import re
from dataclasses import fields
from glob import glob
from shutil import copy
import pprint

from jinja2 import Environment, select_autoescape, FileSystemLoader, Template
from tqdm import tqdm
import pathlib
import minify_html
import markdown

from .html_parser import MetaDataHtmlParser
from .page import Page

from .npmjs_extension import get_npm_infos
from .github_extension import get_github_infos
from .steam_extension import get_steam_infos
from .gog_extension import get_gog_infos
from .twitter_extension import get_twitter_infos
from .personal_extension import get_personal_infos
from .translations import get_translation

more_tag = '__MORE__'

global_context = {
    'debug': os.environ.get('DEBUG') is not None,
    'github': get_github_infos(),
    'npmjs': get_npm_infos(),
    'twitter': get_twitter_infos(),
    'steam': get_steam_infos(),
    'gog': get_gog_infos(),
    'personal': get_personal_infos()
}

pp = pprint.PrettyPrinter()
pp.pprint(global_context)

default_jinja_env = Environment(
    loader=FileSystemLoader(['.', 'templates']),
    autoescape=select_autoescape(),
)

default_jinja_env.trim_blocks = True

# Add translation function to Jinja globals
default_jinja_env.globals['get_translation'] = get_translation


def strip_comments(html):
    return re.sub("(<!--.*?-->)", "", html, flags=re.MULTILINE)


directory_to_template = {
    'posts': 'post.html',
    'pages': 'page.html',
    'projects': 'page.html',
}


def render_page_content(page_to_render, context):
    if not page_to_render.url.startswith('/'):
        page_to_render.url = '/' + page_to_render.url

    string_file_path = str(page_to_render.file_path).replace('\\', '/')
    template_directory = os.path.split(string_file_path)[0].replace('./', '').split('/')[0]
    
    # For markdown files, content is already converted to HTML, just set it as rendered
    if str(page_to_render.file_path).endswith('.md'):
        page_to_render.rendered = page_to_render.content
    else:
        # For HTML files, use template rendering
        temporary_template = default_jinja_env.get_template(string_file_path)
        page_to_render.rendered = temporary_template.render(page=page_to_render, **context, **global_context)

    # Apply the layout template for all files
    template_name = directory_to_template[template_directory]
    temporary_template = default_jinja_env.get_template(template_name)
    rendered = temporary_template.render(page=page_to_render, **context, **global_context)

    page_to_render.rendered = rendered


def parse_file_and_create_page_entity(file_path):
    with open(file_path, encoding='utf-8') as f:
        page = Page()
        page.file_path = file_path
        page.content = f.read()

        path_object = pathlib.Path(file_path)
        stat = path_object.stat()
        modification_date = datetime.datetime.fromtimestamp(stat.st_mtime)
        page.last_update_time = modification_date

        # Handle markdown files
        if str(file_path).endswith('.md'):
            import re
            # Extract frontmatter from markdown
            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', page.content, re.DOTALL)
            if frontmatter_match:
                frontmatter_text = frontmatter_match.group(1)
                page.content = frontmatter_match.group(2).strip()
                
                # Parse YAML-like frontmatter
                meta_data = {}
                for line in frontmatter_text.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                        meta_data[key] = value
                
                names = set([f.name for f in fields(page)])
                for key, value in meta_data.items():
                    if key in names:
                        if key == 'date':
                            setattr(page, key, datetime.datetime.strptime(value, "%Y-%m-%d"))
                        else:
                            setattr(page, key, value)
        else:
            # Handle HTML files
            htmlParser = MetaDataHtmlParser()
            htmlParser.feed(page.content)

            if htmlParser.parsed and htmlParser.meta_data != None:
                names = set([f.name for f in fields(page)])
                for key, value in htmlParser.meta_data.items():
                    if key in names:
                        if key == 'date':
                            setattr(page, key, datetime.datetime.strptime(value, "%Y-%m-%d"))
                        else:
                            setattr(page, key, value)

        # Convert markdown to HTML if it's a markdown file
        if str(file_path).endswith('.md'):
            page.content = markdown.markdown(
                page.content, 
                extensions=['codehilite', 'fenced_code'],
                extension_configs={
                    'codehilite': {
                        'css_class': 'code',
                        'use_pygments': True
                    }
                }
            )

        # Handle both __MORE__ and <!-- more --> markers
        more_markers = [more_tag, '<!-- more -->']
        for marker in more_markers:
            if marker in page.content:
                more_start = page.content.index(marker)
                page.teaser = page.content[0:more_start]
                break

        return page


def write_page_as_html_to_disk(page_to_write, output_dir, destination_dir):
    destination_dir = os.path.join(output_dir, destination_dir)

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    if page_to_write.rendered == '' or page_to_write.rendered is None:
        raise Exception(f'{page_to_write}')

    rendered = page_to_write.rendered
    rendered = re.sub('(<!--.*?-->)', '', rendered, flags=re.DOTALL)

    lines = rendered.splitlines()
    lines = [line for line in lines if more_tag not in line]
    lines = [line for line in lines if line != '']

    rendered = '\n'.join(lines)

    page_to_write.rendered = rendered

    with open(os.path.join(destination_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(rendered)


def get_destination_dir_for_blog_post(entry, absolute=False):
    # Normalize path separators for consistent behavior across platforms
    file_path = str(entry.file_path).replace('\\', '/')
    directory, filename = os.path.split(file_path)
    destination_dir = 'blog/'
    filename, extension = os.path.splitext(filename)
    destination_dir += entry.date.strftime('%Y/%m/%d') + '/'

    if '/' in directory:
        root_dir, subdir = directory.rsplit('/', 1)  # Use rsplit to get the last part
        destination_dir += subdir + '/'
        entry.other_files = glob(f'{directory}/*[!.html]')
    else:
        destination_dir += filename + '/'

    if absolute and not destination_dir.startswith('/'):
        destination_dir = '/' + destination_dir
        return destination_dir

    return destination_dir


def get_destination_dir_for_entry(entry, destination_dir):
    directory, filename = os.path.split(entry.file_path)
    filename, extension = os.path.splitext(filename)
    return os.path.join(destination_dir, filename) + '/'


def set_blog_post_urls(entries):
    for entry in tqdm(entries, desc='Set blog post urls'):
        entry.url = get_destination_dir_for_blog_post(entry, True)


def set_urls(entries, destination_dir=''):
    for entry in tqdm(entries, desc='Set urls'):
        url = get_destination_dir_for_entry(entry, destination_dir)
        entry.url = url


def write_blog_posts(entries, output_dir):
    for entry in tqdm(entries, desc='Write posts to disk'):
        destination_dir = get_destination_dir_for_blog_post(entry)
        write_page_as_html_to_disk(entry, output_dir, destination_dir)

        for other_file in entry.other_files:
            copy(other_file, os.path.join(output_dir, destination_dir))


def render_entries(entries, context):
    for entry in tqdm(entries, desc='Render entries'):
        render_page_content(entry, context)


def write_list_entries(entries, output_dir, destination_dir=''):
    for entry in tqdm(entries, desc='Write entries to disk'):
        directory, filename = os.path.split(entry.file_path)
        filename, extension = os.path.splitext(filename)
        final_dir = destination_dir

        if filename != 'index':
            final_dir = os.path.join(final_dir, filename)

        write_page_as_html_to_disk(entry, output_dir, final_dir)

        # Copy other files (like images) next to the entry
        other_files = glob(f'{directory}/{filename}.*[!.html]')
        for other_file in other_files:
            copy(other_file, os.path.join(output_dir, final_dir))


def render_list_index(title, entries, context=None):
    list_template = default_jinja_env.get_template('list.html')
    published_entries = [p for p in entries if not p.draft]
    template_context = {
        'title': title,
        'entries': published_entries,
        'last_update_time': datetime.datetime.now()
    }
    if context:
        template_context.update(context)
    rendered = list_template.render(**template_context)

    return rendered


def render_projects_index(projects, context=None):
    projects_template = default_jinja_env.get_template('projects_index.html')
    published_projects = [p for p in projects if not p.draft]
    template_context = {
        'projects': published_projects, 
        'github': global_context['github']
    }
    if context:
        template_context.update(context)
    rendered = projects_template.render(**template_context)

    return rendered


def render_and_write_tags_to_disk(tags, pages_grouped_by_tags, output_dir, context=None):
    tag_list_template = default_jinja_env.get_template('tag_list.html')
    template_context = {
        'tags': tags, 
        'pages_grouped_by_tags': pages_grouped_by_tags
    }
    if context:
        template_context.update(context)
    tag_list_result = tag_list_template.render(**template_context)
    
    destination_dir = os.path.join(output_dir, 'tag')
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    with open(os.path.join(destination_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(tag_list_result)

    for tag_name, posts_grouped_by_tag in tqdm(pages_grouped_by_tags.items(), desc='Write tags to disk'):
        tag_list_result = render_list_index(
            f'Seiten mit dem Tag "{tag_name}"', posts_grouped_by_tag, context)
        destination_dir = os.path.join(output_dir, 'tag', tag_name)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        with open(os.path.join(destination_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(tag_list_result)


def set_related_pages(pages, pages_grouped_by_tags):
    for page in pages:
        page.related_pages = []

        for tag in page.tags.split():
            if tag in pages_grouped_by_tags.keys():
                # Filter out abandoned projects and exclude current page
                pages_by_tag = [p for p in pages_grouped_by_tags[tag] 
                              if p != page and not getattr(p, 'abandoned', False)]
                if len(pages_by_tag):
                    random_post_by_tag = random.choice(pages_by_tag)

                    if random_post_by_tag not in page.related_pages:
                        page.related_pages.append(random_post_by_tag)
