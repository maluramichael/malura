"""
Translation system for multi-language support
"""

translations = {
    'de': {
        'active_projects': 'Aktive Projekte',
        'archived_projects': 'Archivierte Projekte',
        'archived': 'Archiviert',
        'no_longer_active': 'Nicht mehr aktiv',
        'learn_more': 'Mehr erfahren',
        'github_repositories': 'GitHub Repositories',
        'view_all': 'Alle ansehen',
        'similar_posts': 'Ähnliche Beiträge',
        'welcome': 'Willkommen',
        'blog': 'Blog',
        'projects': 'Projekte',
        'cv': 'Werdegang',
        'contact': 'Kontakt',
        'made_with_love': 'Made with ♥ by Michael Malura'
    },
    'en': {
        'active_projects': 'Active Projects',
        'archived_projects': 'Archived Projects',
        'archived': 'Archived',
        'no_longer_active': 'No longer active',
        'learn_more': 'Learn more',
        'github_repositories': 'GitHub Repositories',
        'view_all': 'View all',
        'similar_posts': 'Similar Posts',
        'welcome': 'Welcome',
        'blog': 'Blog',
        'projects': 'Projects',
        'cv': 'CV',
        'contact': 'Contact',
        'made_with_love': 'Made with ♥ by Michael Malura'
    }
}

def get_translation(key, lang='de'):
    """Get translated text for given key and language"""
    return translations.get(lang, {}).get(key, translations.get('de', {}).get(key, key))

def get_available_languages():
    """Get list of available language codes"""
    return list(translations.keys())