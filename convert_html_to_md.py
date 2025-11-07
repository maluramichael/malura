#!/usr/bin/env python3
"""
Convert HTML blog posts to Markdown with proper formatting and image handling
"""

import os
import re
import json
import html
from pathlib import Path
from markdownify import markdownify as md
import subprocess
import sys

def install_required_packages():
    """Install required packages if not available"""
    try:
        import markdownify
    except ImportError:
        print("Installing required package: markdownify...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "markdownify"])
        import markdownify

def extract_metadata_from_html_comment(content):
    """Extract JSON metadata from HTML comment"""
    comment_pattern = r'<!--\s*(\{[^}]+\})\s*-->'
    match = re.search(comment_pattern, content, re.DOTALL)
    
    if match:
        try:
            metadata_str = match.group(1)
            metadata = json.loads(metadata_str)
            # Remove the comment from content
            content = re.sub(comment_pattern, '', content, flags=re.DOTALL).strip()
            return metadata, content
        except json.JSONDecodeError:
            print(f"Warning: Could not parse metadata JSON")
            return {}, content
    
    return {}, content

def clean_html_content(content):
    """Clean up HTML content before conversion"""
    # Decode HTML entities
    content = html.unescape(content)
    
    # Fix common HTML issues
    content = content.replace('&quot;', '"')
    content = content.replace('&amp;', '&')
    content = content.replace('&lt;', '<')
    content = content.replace('&gt;', '>')
    
    # Clean up extra whitespace
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    return content

def fix_image_paths(content, post_dir):
    """Fix image paths to work with the new structure"""
    post_name = os.path.basename(post_dir)
    
    # Find all image references
    img_patterns = [
        r'<img[^>]*src="([^"]+)"[^>]*>',  # HTML img tags
        r'!\[[^\]]*\]\(([^)]+)\)',        # Markdown images
    ]
    
    for pattern in img_patterns:
        def replace_image(match):
            original_src = match.group(1)
            
            # If it's already a relative path without directory, it needs the post directory
            if '/' not in original_src and not original_src.startswith('http'):
                new_src = f"./{original_src}"
                return match.group(0).replace(original_src, new_src)
            
            return match.group(0)
        
        content = re.sub(pattern, replace_image, content)
    
    return content

def convert_html_to_markdown(html_content):
    """Convert HTML to Markdown with proper formatting"""
    # Configure markdownify to preserve code blocks and other elements
    markdown_content = md(
        html_content,
        heading_style="ATX",  # Use # for headings
        bullets="-",          # Use - for bullets
        code_language="",     # Don't add language hints unless specified
        strip=['script', 'style'],  # Remove script and style tags
    )
    
    # Clean up the markdown
    markdown_content = clean_markdown(markdown_content)
    
    return markdown_content

def clean_markdown(content):
    """Clean up converted markdown content"""
    # Fix multiple newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Fix code blocks - ensure proper spacing
    content = re.sub(r'```\n\n+', '```\n', content)
    content = re.sub(r'\n\n+```', '\n```', content)
    
    # Clean up list formatting
    content = re.sub(r'\n\n-', '\n-', content)
    
    # Remove trailing whitespace
    content = '\n'.join(line.rstrip() for line in content.split('\n'))
    
    # Ensure file ends with single newline
    content = content.rstrip() + '\n'
    
    return content

def create_yaml_frontmatter(metadata):
    """Create YAML frontmatter from metadata"""
    frontmatter_lines = ["---"]
    
    # Add required fields
    if 'title' in metadata:
        frontmatter_lines.append(f'title: "{metadata["title"]}"')
    
    if 'date' in metadata:
        frontmatter_lines.append(f'date: {metadata["date"]}')
    
    if 'tags' in metadata:
        frontmatter_lines.append(f'tags: {metadata["tags"]}')
    
    # Add any other fields
    for key, value in metadata.items():
        if key not in ['title', 'date', 'tags']:
            if isinstance(value, str):
                frontmatter_lines.append(f'{key}: "{value}"')
            else:
                frontmatter_lines.append(f'{key}: {value}')
    
    frontmatter_lines.append("---")
    
    return '\n'.join(frontmatter_lines) + '\n'

def convert_post(post_dir):
    """Convert a single blog post from HTML to Markdown"""
    post_path = Path(post_dir)
    index_html = post_path / 'index.html'
    
    if not index_html.exists():
        print(f"No index.html found in {post_dir}")
        return False
    
    print(f"Converting {post_path.name}...")
    
    # Read the HTML file
    with open(index_html, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract metadata and clean content
    metadata, content = extract_metadata_from_html_comment(content)
    content = clean_html_content(content)
    
    # Handle __MORE__ marker
    more_marker = '__MORE__'
    if more_marker in content:
        content = content.replace(more_marker, '<!-- more -->')
    
    # Fix image paths
    content = fix_image_paths(content, post_dir)
    
    # Convert to Markdown
    markdown_content = convert_html_to_markdown(content)
    
    # Create the final markdown file content
    final_content = ""
    
    # Add frontmatter if metadata exists
    if metadata:
        final_content += create_yaml_frontmatter(metadata)
        final_content += "\n"
    
    # Add the markdown content
    final_content += markdown_content
    
    # Write the markdown file
    markdown_file = post_path / 'index.md'
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"Created {markdown_file}")
    
    # Optionally backup the HTML file
    backup_file = post_path / 'index.html.backup'
    if not backup_file.exists():
        os.rename(index_html, backup_file)
        print(f"  Backed up original to {backup_file}")
    
    return True

def convert_all_posts():
    """Convert all blog posts in the posts directory"""
    posts_dir = Path('posts')
    
    if not posts_dir.exists():
        print("Posts directory not found!")
        return
    
    converted_count = 0
    total_count = 0
    
    for post_dir in posts_dir.iterdir():
        if post_dir.is_dir() and (post_dir / 'index.html').exists():
            total_count += 1
            if convert_post(post_dir):
                converted_count += 1
    
    print(f"\nConverted {converted_count}/{total_count} posts")
    print("Original HTML files have been backed up as .backup files")

if __name__ == "__main__":
    install_required_packages()
    convert_all_posts()