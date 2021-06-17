import datetime
import json
import os
from dataclasses import dataclass, fields
from email import utils
from glob import glob
from html.parser import HTMLParser
from io import StringIO
from shutil import copy
from string import Template


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


class CustomTemplate(Template):
    delimiter = '##'


def strip_tags(html):
    s = HtmlStripper()
    s.feed(html)
    return s.get_data()


def load_templates():
    loaded_templates = {}
    template_paths = glob('templates/*.html')
    for template_path in template_paths:
        _, filename = os.path.split(template_path)
        filename, ext = os.path.splitext(filename)

        with open(template_path) as f:
            loaded_templates[filename] = CustomTemplate(f.read())
    return loaded_templates


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


templates = load_templates()


def get_template(template_name):
    return templates[template_name]


def render_root_template(title, page_content): return get_template('root').substitute(
    title=title,
    header=get_template('header').substitute(),
    content=page_content
)


def render_post(page_to_render):
    rendered_tag_list = '\n'.join(
        [
            f'<a href="/blog/tag/{post_tag}">{post_tag}</a>'
            for post_tag in page_to_render.tags.split(' ')
        ]
    )
    return render_root_template(
        page_to_render.title,
        get_template('post').substitute(content=page_to_render.content, tags=rendered_tag_list)
    )


def render_page(page_to_render):
    rendered_content = get_template('page').substitute(content=page_to_render.content)
    return render_root_template(page_to_render.title, rendered_content)


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

        entry.rendered = render_post(entry)
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


def render_and_write_tags_to_disk(tags, posts_grouped_by_tags, output_dir):
    tag_list = '\n'.join(
        [
            f'<li><a href="/blog/tag/{tag_entry}">{tag_entry} ({len(posts_grouped_by_tags[tag_entry])})</a></li>' for
            tag_entry in tags
        ]
    )
    tag_list = f'<ul>{tag_list}</ul>'
    rendered_page_content = get_template('page').substitute(content=tag_list)
    header_content = get_template('header').substitute()
    tag_list_result = get_template('root').substitute(
        title="Tags",
        header=header_content,
        content=rendered_page_content
    )
    destination_dir = os.path.join(output_dir, 'blog/tag')
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    with open(os.path.join(destination_dir, 'index.html'), 'w') as f:
        f.write(tag_list_result)

    for tag_name, posts_grouped_by_tag in posts_grouped_by_tags.items():
        post_list = '\n'.join([get_template('post_list_entry').substitute({
            'date': post.date.strftime('%d.%m.%Y'),
            'title': post.title,
            'url': post.url,
            'teaser': post.teaser
        }) for post in posts_grouped_by_tag])
        rendered_page_content = get_template('post_list_by_tag').substitute(content=post_list, tag=tag_name)
        header_content = get_template('header').substitute()
        tag_list_result = get_template('root').substitute(
            title=f'Beiträge mit dem Tag "{tag_name}"',
            header=header_content,
            content=rendered_page_content
        )
        destination_dir = os.path.join(output_dir, 'blog/tag', tag_name)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        with open(os.path.join(destination_dir, 'index.html'), 'w') as f:
            f.write(tag_list_result)


def render_blog_list(posts): return render_list_index(
    'Blog',
    posts,
    get_template('list'),
    get_template('post_list_entry')
)


def render_project_list(projects): return render_list_index(
    'Projects',
    projects,
    get_template('list'),
    get_template('post_list_entry')
)