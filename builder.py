import datetime
import json
import os
import re
from dataclasses import dataclass, fields
from email import utils
from glob import glob
from html.parser import HTMLParser
from io import StringIO
from shutil import copy
from jinja2 import Environment, select_autoescape, FileSystemLoader

jinja_env = Environment(
    loader=FileSystemLoader(['templates']),
    autoescape=select_autoescape()
)


class MetaDataHtmlParser(HTMLParser):
    parsed = False
    meta_data = None

    def handle_comment(self, data):
        if self.parsed:
            return

        self.parsed = True
        self.meta_data = json.loads(data)


class HtmlStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = HtmlStripper()
    s.feed(html)
    return s.get_data()


def strip_comments(html):
    return re.sub("(<!--.*?-->)", "", html, flags=re.MULTILINE)


@dataclass()
class Page:
    title: str = ''
    content: str = ''
    file_path: str = ''
    rendered: str = ''
    teaser: str = ''
    tags: str = ''
    url: str = '/'
    date: datetime.datetime = datetime.datetime.now()


def render_page(page_to_render, template_name='page.html'):
    page_template = jinja_env.get_template(template_name)

    return page_template.render(page=page_to_render)


def parse_file_and_create_page_entity(file_path):
    more_tag = 'MORE'
    with open(file_path) as f:
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


def generate_sitemap(output_dir, pages, posts, tags):
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages + posts:
        sitemap += f"<url>\n  <loc>https://malura.de{page.url}</loc>\n  <lastmod>{page.date.strftime('%Y-%m-%d')}</lastmod>\n</url>\n"

    for tag in tags:
        sitemap += f"<url>\n  <loc>https://malura.de/blog/tag/{tag}</loc>\n  <lastmod>{datetime.datetime.now().strftime('%Y-%m-%d')}</lastmod>\n</url>\n"

    sitemap += '</urlset>'

    with open(os.path.join(output_dir, 'sitemap.xml'), 'w') as output_file:
        output_file.write(sitemap)


def generate_rss_feed_posts(output_dir, posts):
    now_2822 = utils.format_datetime(datetime.datetime.now())
    channel = f'''
        <title>Michael Malura</title>
        <link>https://malura.de</link>
        <description>Mein persoenlicher Blog</description>
        <language>de-de</language>
        <copyright>Michael Malura</copyright>
        <pubDate>{now_2822}</pubDate>'''

    for page in posts:
        page_2822 = utils.format_datetime(page.date)
        url = f'https://malura.de{page.url}'
        description = '<description/>'

        if page.teaser != '':
            description = f'<description>{strip_tags(page.teaser).strip()}</description>'

        channel += f'''
        <item>
            <title>{page.title}</title>
            <link>{url}</link>
            <author>michael@malura.de (Michael Malura)</author>
            <guid isPermaLink="true">{url}</guid>
            <pubDate>{page_2822}</pubDate>
            {description}
        </item>'''

    feed = f'    <channel>{channel}\n    </channel>'
    feed = f'<rss version="2.0">\n{feed}\n</rss>'
    feed = f'<?xml version="1.0" encoding="UTF-8"?>\n{feed}'

    with open(os.path.join(output_dir, 'feed.xml'), 'w') as output_file:
        output_file.write(feed)


def write_page_as_html_to_disk(page_to_write, output_dir, destination_dir):
    page_to_write.url = '/' + destination_dir
    destination_dir = os.path.join(output_dir, destination_dir)

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    if page_to_write.rendered == '' or page_to_write.rendered is None:
        raise Exception(f'{page_to_write}')

    with open(os.path.join(destination_dir, 'index.html'), 'w') as f:
        # stripped = strip_comments(page_to_write.rendered)
        f.write(page_to_write.rendered)


def render_and_write_page_has_html_to_disk(page, output_dir, destination_dir):
    rendered_page = render_page(page)
    page.rendered = rendered_page

    write_page_as_html_to_disk(page, output_dir, destination_dir)


def render_and_write_blog_posts_to_disk(entries, output_dir):
    for entry in entries:
        directory, filename = os.path.split(entry.file_path)
        destination_dir = 'blog/'
        filename, extension = os.path.splitext(filename)
        other_files = []
        destination_dir += entry.date.strftime('%Y/%m/%d') + '/'

        if '/' in directory:
            root_dir, subdir = os.path.split(directory)
            destination_dir += subdir + '/'
            other_files = glob(f'{directory}/*[!.html]')
        else:
            destination_dir += filename + '/'

        entry.rendered = render_page(entry, 'post.html')
        entry.url = destination_dir

        write_page_as_html_to_disk(entry, output_dir, destination_dir)

        for other_file in other_files:
            copy(other_file, os.path.join(output_dir, destination_dir))


def render_and_write_list_entries_to_disk(entries, output_dir, destination_dir=''):
    for entry in entries:
        _, filename = os.path.split(entry.file_path)
        filename, extension = os.path.splitext(filename)
        final_dir = destination_dir

        if filename != 'index':
            final_dir = os.path.join(final_dir, filename)

        render_and_write_page_has_html_to_disk(entry, output_dir, final_dir)


def render_list_index(title, entries):
    list_template = jinja_env.get_template('list.html')
    return list_template.render(title=title, entries=entries)


def render_and_write_tags_to_disk(tags, posts_grouped_by_tags, output_dir):
    tag_list_template = jinja_env.get_template('tag_list.html')
    tag_list_result = tag_list_template.render(tags=tags, posts_grouped_by_tags=posts_grouped_by_tags)
    destination_dir = os.path.join(output_dir, 'blog/tag')
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    with open(os.path.join(destination_dir, 'index.html'), 'w') as f:
        f.write(tag_list_result)

    for tag_name, posts_grouped_by_tag in posts_grouped_by_tags.items():
        tag_list_result = render_list_index(f'Beiträge mit dem Tag "{tag_name}"', posts_grouped_by_tag)
        destination_dir = os.path.join(output_dir, 'blog/tag', tag_name)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        with open(os.path.join(destination_dir, 'index.html'), 'w') as f:
            f.write(tag_list_result)


def render_blog_list(posts): return render_list_index(
    'Blog',
    posts,
)


def render_project_list(projects): return render_list_index(
    'Projekte',
    projects,
)
