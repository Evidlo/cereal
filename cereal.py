#!/bin/python
# Evan Widloski - 2015-12-12
# Cereal - Minimal static website generator

#issues - how to do template inheritance

import yaml
import mistune
import os, shutil, errno
from jinja2 import Environment, FileSystemLoader

# useful exceptions
from jinja2.exceptions import TemplateNotFound

content_dir = 'content'
layout_dir = 'layout'
output_dir = 'out'
symlink = False

env = Environment(loader=FileSystemLoader('.'))

#make all dirs up to path
def make_path(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else: raise

#copy or symlink a file
def copy_resource(source,dest):
    try:
        if symlink:
            os.symlink(source, dest)
        else:
            shutil.copy2(source,dest)
    except OSError, e:
        if e.errno == errno.EEXIST:
            os.remove(dest)
            copy_resource(source, dest)

#iterate through all files in content_dir
for subdir, dirs, files in os.walk(content_dir):
    for file in files:

        content_file =  os.path.join(subdir, file)
        # where does this file get output to?
        output_file = "%s/%s" % (output_dir, os.path.relpath(content_file,content_dir))
        make_path(os.path.dirname(output_file))

        #if this is a yaml file, do site rendering
        if file.endswith('.yaml'):
            #rename output .html
            output_file = os.path.splitext(output_file)[0] + '.html'

            #open content file, find layout and render it
            with open(content_file) as f:
                yaml_data = yaml.load(f)

                #try to find the layout specified on content_file
                #if not specified, print a warning and skip content_file
                try:
                    layout_file = "%s/%s/%s" % (layout_dir,
                                                os.path.relpath(subdir,content_dir),
                                                yaml_data['layout'])

                except KeyError:
                    print('No layout specified for %s. Skipping...' % content_file)
                    break

                # process 'content' as markdown before rendering, if it exists
                if 'content' in yaml_data:
                    yaml_data['content'] = mistune.markdown(yaml_data['content'])

                # create path to output_file and render it. if layout not found, print warning
                try:
                    template = env.get_template(layout_file)
                except TemplateNotFound:
                    print('Could not find layout file %s for %s. Skipping...' %
                          (layout_file,
                          content_file))
                    break

                with open(output_file,'w+') as out:
                    out.write(template.render(**yaml_data))

        #if this is not yaml, just copy the file
        else:
            copy_resource(content_file,output_file)
