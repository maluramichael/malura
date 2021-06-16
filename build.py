import datetime
import re
from string import Template
from pathlib import Path
import os
from glob import glob
from shutil import copy
from html.parser import HTMLParser
import json
from dataclasses import dataclass, field, fields

output_dir = '_output'
posts_dir = 'posts'

templates = {}

posts = []
pages = []
projects = []
tags = []
posts_grouped_by_tags = {}

post_files = Path('posts').rglob('*.html')
page_files = Path('pages').rglob('*.html')
project_files = Path('projects').rglob('*.html')
asset_files = Path('assets').rglob('*')


class MetaDataHtmlParser(HTMLParser):
    parsed = False
    meta_data = None

    def handle_comment(self, data):
        if self.parsed:
            return

        self.parsed = True
        self.meta_data = json.loads(data)


# TEMPLATES
class CustomTemplate(Template):
    delimiter = '##'


def load_templates():
    template_paths = glob('templates/*.html')
    for template_path in template_paths:
        dir, filename = os.path.split(template_path)
        filename, ext = os.path.splitext(filename)

        with open(template_path) as f:
            templates[filename] = CustomTemplate(f.read())


def get_template(template_name):
    return templates[template_name]


def render_post(post):
    content = post.content
    rendered_post_content = get_template('post').substitute(content=content)
    header_content = get_template('header').substitute()
    final_result = get_template('root').substitute(
        title=post.title or "Hello world",
        header=header_content,
        content=rendered_post_content
    )
    return final_result


def render_page(page_content):
    rendered_page_content = get_template('page').substitute(content=page_content)
    header_content = get_template('header').substitute()
    final_result = get_template('root').substitute(
        title="Hello world",
        header=header_content,
        content=rendered_page_content
    )
    return final_result


@dataclass()
class Page():
    title: str = ''
    content: str = ''
    file_path: str = ''
    rendered: str = ''
    teaser: str = ''
    tags: str = ''
    url: str = '/'
    date: datetime.datetime = datetime.datetime.now()


def parse_file_and_create_page_entity(file_path):
    more_tag = 'MORE'
    with open(file_path) as f:
        print(f'Read: {file_path}')
        page = Page()
        page.file_path = file_path
        page.content = f.read()

        htmlParser = MetaDataHtmlParser()
        htmlParser.feed(page.content)

        if htmlParser.parsed and htmlParser.meta_data != None:
            names = set([f.name for f in fields(page)])
            for k, v in htmlParser.meta_data.items():
                if k in names:
                    if k == 'date':
                        setattr(page, k, datetime.datetime.strptime(v, "%Y-%m-%d"))
                    else:
                        setattr(page, k, v)

        # remove comment

        if more_tag in page.content:
            more_start = page.content.index(more_tag)
            page.teaser = page.content[0:more_start]
            lines = [line for line in page.content.splitlines() if more_tag not in line]
            page.content = '\n'.join(lines)

        return page


def write_page_as_html_to_disk(page, destination_dir):
    page.url = '/' + destination_dir
    destination_dir = os.path.join(output_dir, destination_dir)

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    rendered_page = render_page(page.content)
    rendered_page = re.sub("(<!--.*?-->)", "", rendered_page, flags=re.DOTALL)
    page.rendered = rendered_page

    with open(os.path.join(destination_dir, 'index.html'), 'w') as output_file:
        output_file.write(rendered_page)


# Render posts
def render_and_write_blog_posts_to_disk(entries):
    for page in entries:
        dir, filename = os.path.split(page.file_path)
        destination_dir = 'blog/'
        filename, extension = os.path.splitext(filename)
        other_files = []
        destination_dir += page.date.strftime('%Y/%m/%d') + '/'

        if '/' in dir:
            root_dir, subdir = os.path.split(dir)
            destination_dir += subdir + '/'
            other_files = glob(f'{dir}/*[!.html]')
        else:
            destination_dir += filename + '/'

        rendered_post = render_post(page)
        page.rendered = rendered_post

        write_page_as_html_to_disk(page, destination_dir)

        for other_file in other_files:
            copy(other_file, os.path.join(output_dir, destination_dir))


# Render pages
def render_and_write_list_entries_to_disk(entries, destination_dir=''):
    for page in entries:
        dir, filename = os.path.split(page.file_path)
        filename, extension = os.path.splitext(filename)
        final_dir = destination_dir

        if filename != 'index':
            final_dir = os.path.join(final_dir, filename)

        write_page_as_html_to_disk(page, final_dir)


# Render blog list
def render_list_index(title, entries, list_template, entry_template):
    rendered_list = ''

    for entry in entries:
        rendered_content = entry_template.substitute({
            'date': entry.date.strftime('%d.%m.%Y'),
            'title': entry.title,
            'url': entry.url,
            'teaser': entry.teaser
        })
        rendered_list += rendered_content

    list_page_content = list_template.substitute(content=rendered_list)
    rendered_page_content = get_template('page').substitute(content=list_page_content)
    header_content = get_template('header').substitute()
    final_result = get_template('root').substitute(
        title=title,
        header=header_content,
        content=rendered_page_content
    )
    return final_result


def render_blog_list(): return render_list_index(
    'Blog',
    posts,
    get_template('list'),
    get_template('post_list_entry')
)


def render_page_list(): return render_list_index(
    'Pages',
    pages,
    get_template('list'),
    get_template('post_list_entry')
)


def render_project_list(): return render_list_index(
    'Projects',
    projects,
    get_template('list'),
    get_template('post_list_entry')
)


load_templates()

# Parse posts
for file_path in post_files:
    post = parse_file_and_create_page_entity(file_path)
    if post is not None:
        posts.append(post)

posts.sort(key=lambda x: x.date, reverse=True)

for file_path in page_files:
    page = parse_file_and_create_page_entity(file_path)
    if page is not None:
        pages.append(page)

for file_path in project_files:
    page = parse_file_and_create_page_entity(file_path)
    if page is not None:
        projects.append(page)

# Group posts by tags and gather all tags
for post in posts:
    for tag in post.tags.split(' '):
        if tag not in tags:
            tags.append(tag)

        if tag not in posts_grouped_by_tags:
            posts_grouped_by_tags[tag] = list()

        posts_grouped_by_tags[tag].append(post)

render_and_write_blog_posts_to_disk(posts)
render_and_write_list_entries_to_disk(pages)
render_and_write_list_entries_to_disk(projects, 'projects')

with open(os.path.join(output_dir, 'blog/index.html'), 'w') as output_file:
    output_file.write(render_blog_list())

with open(os.path.join(output_dir, 'projects/index.html'), 'w') as output_file:
    output_file.write(render_project_list())

# Copy assets
if not os.path.exists(os.path.join(output_dir, 'assets')):
    os.makedirs(os.path.join(output_dir, 'assets'))

for asset_file in asset_files:
    copy(asset_file, os.path.join(output_dir, 'assets'))
