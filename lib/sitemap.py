import datetime
import os

from tqdm import tqdm


def generate_sitemap(output_dir, pages, posts, tags):
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    pages_and_posts = [p for p in pages + posts if not p.draft]
    for page in tqdm(pages_and_posts, desc='Write pages and posts to sitemap'):
        sitemap += f"<url>\n  <loc>https://malura.de{page.url}</loc>\n  <lastmod>{page.date.strftime('%Y-%m-%d')}</lastmod>\n</url>\n"

    for tag in tqdm(tags, desc='Write tags to sitemap'):
        sitemap += f"<url>\n  <loc>https://malura.de/tag/{tag}</loc>\n  <lastmod>{datetime.datetime.now().strftime('%Y-%m-%d')}</lastmod>\n</url>\n"

    sitemap += '</urlset>'

    with open(os.path.join(output_dir, 'sitemap.xml'), 'w') as output_file:
        output_file.write(sitemap)
