#!/bin/python
# Evan Widloski - 2015-12-12
# Cereal - Minimal static website generator

# rendering utils
import yaml
import time
from yaml import nodes
import mistune
from jinja2 import Environment, FileSystemLoader, Template
# file handling and system
import os, sys, shutil, errno, getopt,re
# useful exceptions
from jinja2.exceptions import TemplateNotFound
import traceback

content_dir = 'content'
layout_dir = 'layout'
output_dir = 'out'

# Jinja file loader - delete extra newlines
env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)

# Markdown renderer - disable mistune <p> insertion
class disable_paragraph_renderer(mistune.Renderer):
    def paragraph(self, text):
        return '<br>%s' % text.strip(' ')
renderer = disable_paragraph_renderer()
markdown = mistune.Markdown(renderer, escape=False)

#------------- Content Processors --------------
# Use processors to specify how content nodes are parsed
# `value` is node content, and `args` is list of arguments
# passed to node tag, eg. `code(python)`

def join_processor(value, args):
    return '\n'.join(value)


def md_processor(value, args):
    print(value)
    return markdown(value)

def jinja_processor(value,args):
    value = "{% extends 'layout/macros.html' %} {% block _macro_ %}" \
        + value \
        + "{% endblock %}"
    return env.from_string(value).render()

# pass in language using code(lang)
def code_processor(value, args):
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter
    return highlight(value, get_lexer_by_name(args[0], stripall=True), HtmlFormatter())

def py_processor(value, args):
    from cStringIO import StringIO
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    exec(value)
    sys.stdout = old_stdout
    return redirected_output.getvalue()

# Map tag to each processor
processors = {'join':join_processor,
              'md':md_processor,
              'j2':jinja_processor,
              'code':code_processor,
              'py':py_processor
              }

#-----------------------------------------

# Allow comma separated yaml tags
def constructor(loader, suffix, node):
    if isinstance(node,nodes.ScalarNode):
        value = loader.construct_scalar(node)
    if isinstance(node,nodes.SequenceNode):
        value = loader.construct_sequence(node)
    if isinstance(node,nodes.MappingNode):
        value = loader.construct_mapping(node)
    for tag in suffix.split(','):
        # Accept processor arguments
        search = re.search('(.*)\((.*)\)',tag)
        if search:
            processor = search.groups()[0]
            args = search.groups()[1].split(',')
        else:
            processor = tag
            args = None

        value = processors[processor](value,args)
    return value

yaml.add_multi_constructor(u'!',constructor)

# make all dirs up to path
def make_path(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else: raise

# copy or symlink a file
def copy_resource(source,dest,symlink=False):
    try:
        if symlink:
            os.symlink(source, dest)
        else:
            shutil.copy2(source,dest)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(dest)
            copy_resource(source, dest)

# build site
def build(symlink=False):
    if not os.path.exists(content_dir):
        print('Could not find content directory. Quitting...')
        sys.exit(2)
    if not os.path.exists(layout_dir):
        print('Could not find layout directory. Quitting...')
        sys.exit()
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # iterate through all files in content_dir
    for subdir, dirs, files in os.walk(content_dir):
        for file in files:

            content_file =  os.path.join(subdir, file)
            # where does this file get output to?
            output_file = "%s/%s" % (output_dir, os.path.relpath(content_file,content_dir))
            make_path(os.path.dirname(output_file))

            # if this is a nonhidden yaml file, do site rendering
            if file.endswith('.yaml') and not file.startswith('.'):
                #rename output .html
                output_file = os.path.splitext(output_file)[0] + '.html'

                # open content file, find layout and render it
                with open(content_file) as f:
                    try:
                        yaml_data = yaml.load(f)
                        # try to find the layout specified on content_file
                        # if not specified, print a warning and skip content_file
                        layout_file = "%s/%s" % (layout_dir, yaml_data['layout'])
                        # create path to output_file and render it.
                        # if layout not found, print warning
                        template = env.get_template(layout_file)
                        with open(output_file,'w+') as out:
                            out.write(template.render(**yaml_data))
                    except Exception as e:
                        print(traceback.format_exc())
                        print('Error while loading content file: %s' % content_file)
                    except KeyError:
                        print('No layout specified for %s. Skipping...' % content_file)
                        break
                    except TemplateNotFound:
                        print('Could not find layout file %s for %s. Skipping...' %
                            (layout_file,
                            content_file))
                        break
                    except Exception as e:
                        print(traceback.format_exc())
                        print('Error while rendering content file: %s' % content_file)

            # if this is not yaml, just copy the file
            elif not file.startswith('.'):
                copy_resource(content_file,output_file,symlink)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--runserver",action="store_true",help="Run development server")
parser.add_argument("-s",action="store_true",help="Symlink resources to output dir instead of copying")
args = parser.parse_args()

# enable resource symlinking
symlink = False
if args.s:
    symlink = True

# run development server
if args.runserver:
    # build if output directory doesn't exist
    if not os.path.exists(output_dir):
        build(symlink)

    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler
    from datetime import datetime

    class handler(PatternMatchingEventHandler):
        patterns = ["./content/*","./layout/*"]
        ignore_patterns = ["*/.*"]
        ignore_directories = True

        def on_any_event(self,event):
            if event.event_type in ("modified","deleted","moved","created"):
                # we're in output_dir, we need to cd back before building
                print("Detected change in {0}. Rebuilding...".format(event.src_path))
                start_time = datetime.now()
                os.chdir('..')
                build(symlink)
                os.chdir(output_dir)
                print(" Done. {0}s".format((datetime.now()-start_time).total_seconds()))


    # watch content directory for changes

    observer = Observer()
    observer.schedule(handler(), './', recursive=True,)
    observer.start()

    # start development webserver
    import http.server
    import socketserver
    port = 8000
    # SimpleHTTPServer doesn't accept a directory, so we have to cd
    os.chdir(output_dir)
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), Handler)
    print("Serving on port", port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.exit()
else:
    build(symlink)
