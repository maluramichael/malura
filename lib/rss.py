import datetime
import os
from email import utils

from tqdm import tqdm

from .html_parser import HtmlStripper


def strip_tags(html):
    s = HtmlStripper()
    s.feed(html)
    return s.get_data()


def generate_rss_feed_posts(output_dir, posts):
    now_2822 = utils.format_datetime(datetime.datetime.now())
    channel = f'''
        <title>Michael Malura</title>
        <link>https://malura.de</link>
        <description>Mein persoenlicher Blog</description>
        <language>de-de</language>
        <copyright>Michael Malura</copyright>
        <pubDate>{now_2822}</pubDate>'''

    for page in tqdm(posts, desc='Write posts to rss feed'):
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