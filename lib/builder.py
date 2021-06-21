import datetime
import os
import re
from dataclasses import fields
from glob import glob
from shutil import copy

from jinja2 import Environment, select_autoescape, FileSystemLoader, Template
from tqdm import tqdm
import pathlib

from .npmjs_extension import get_npm_infos
from .github_extension import get_github_infos

from .html_parser import MetaDataHtmlParser
from .page import Page

more_tag = '__MORE__'

global_context = {
    'debug': os.environ.get('DEBUG') is not None,
    'github': get_github_infos(),
    'npmjs': get_npm_infos()
}

default_jinja_env = Environment(
    loader=FileSystemLoader(['.', 'templates']),
    autoescape=select_autoescape()
)

default_jinja_env.trim_blocks = True


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

    string_file_path = str(page_to_render.file_path)
    template_directory = os.path.split(string_file_path)[0].replace('./', '').split('/')[0]
    temporary_template = default_jinja_env.get_template(string_file_path)
    page_to_render.rendered = temporary_template.render(page=page_to_render, **context, **global_context)

    template_name = directory_to_template[template_directory]
    temporary_template = default_jinja_env.get_template(template_name)
    rendered = temporary_template.render(page=page_to_render, **context, **global_context)

    page_to_render.rendered = rendered


def parse_file_and_create_page_entity(file_path):
    with open(file_path) as f:
        page = Page()
        page.file_path = file_path
        page.content = f.read()

        htmlParser = MetaDataHtmlParser()
        htmlParser.feed(page.content)

        if htmlParser.parsed and htmlParser.meta_data != None:
            names = set([f.name for f in fields(page)])
            for key, value in htmlParser.meta_data.items():
                if key in names:
                    if key == 'date':
                        setattr(page, key, datetime.datetime.strptime(
                            value, "%Y-%m-%d"))
                    else:
                        setattr(page, key, value)

        path_object = pathlib.Path(file_path)
        stat = path_object.stat()
        modification_date = datetime.datetime.fromtimestamp(stat.st_mtime)
        page.last_update_time = modification_date

        if more_tag in page.content:
            more_start = page.content.index(more_tag)
            page.teaser = page.content[0:more_start]

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

    with open(os.path.join(destination_dir, 'index.html'), 'w') as f:
        f.write(page_to_write.rendered)


def get_destination_dir_for_blog_post(entry):
    directory, filename = os.path.split(entry.file_path)
    destination_dir = 'blog/'
    filename, extension = os.path.splitext(filename)
    destination_dir += entry.date.strftime('%Y/%m/%d') + '/'

    if '/' in directory:
        root_dir, subdir = os.path.split(directory)
        destination_dir += subdir + '/'
        entry.other_files = glob(f'{directory}/*[!.html]')
    else:
        destination_dir += filename + '/'

    return destination_dir


def get_destination_dir_for_entry(entry, destination_dir):
    directory, filename = os.path.split(entry.file_path)
    filename, extension = os.path.splitext(filename)
    return os.path.join(destination_dir, filename) + '/'


def set_blog_post_urls(entries):
    for entry in tqdm(entries, desc='Set blog post urls'):
        entry.url = get_destination_dir_for_blog_post(entry)


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
        _, filename = os.path.split(entry.file_path)
        filename, extension = os.path.splitext(filename)
        final_dir = destination_dir

        if filename != 'index':
            final_dir = os.path.join(final_dir, filename)

        write_page_as_html_to_disk(entry, output_dir, final_dir)


def render_list_index(title, entries):
    list_template = default_jinja_env.get_template('list.html')
    return list_template.render(title=title, entries=entries, last_update_time=datetime.datetime.now())


def render_and_write_tags_to_disk(tags, posts_grouped_by_tags, output_dir):
    tag_list_template = default_jinja_env.get_template('tag_list.html')
    tag_list_result = tag_list_template.render(
        tags=tags, posts_grouped_by_tags=posts_grouped_by_tags)
    destination_dir = os.path.join(output_dir, 'blog/tag')
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    with open(os.path.join(destination_dir, 'index.html'), 'w') as f:
        f.write(tag_list_result)

    for tag_name, posts_grouped_by_tag in tqdm(posts_grouped_by_tags.items(), desc='Write tags to disk'):
        tag_list_result = render_list_index(
            f'Beiträge mit dem Tag "{tag_name}"', posts_grouped_by_tag)
        destination_dir = os.path.join(output_dir, 'blog/tag', tag_name)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        with open(os.path.join(destination_dir, 'index.html'), 'w') as f:
            f.write(tag_list_result)
