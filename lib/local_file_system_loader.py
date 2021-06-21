import os

from jinja2 import FileSystemLoader


class local_file_system_loader(FileSystemLoader):
    def __init__(self, searchpath):
        super().__init__(searchpath)

        self.original_get_source = self.get_source

        def wrapped_get_source(environment, template):
            contents, filename, uptodate = self.original_get_source(environment, template)
            template_directory = os.path.split(filename)[0].replace('./', '').split('/')[0]

            # if 'templates' not in template_directory and '{% extends' not in contents:
            #     transformed_content = '{% extends "page.html" %}'
            #     transformed_content += '{% block page_content %}'
            #     transformed_content += '<!--' + filename + ' ' + template_directory + '-->'
            #     transformed_content += contents
                # transformed_content += '{% endblock %}'

                # return transformed_content, filename, uptodate

            return contents, filename, uptodate

        self.get_source = wrapped_get_source
