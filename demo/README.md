# Demo

This demo is an extension of the README provided in the base directory.  Namely, it shows to how to do template inheritance (see `layout/base.html`) and how to pass a list of items to a layout (see `content/index.html` and `layout/index.html`).  

To build the demo, run `cereal.py` from this directory.

    python ../cereal.py


## Jinja2 inside content files

Jinja2 in your content files allows you to do more complex things, like functionally generated html.

The example below shows how to use jinja2 macros to create captioned images in your content files.

`content/projects/project.html`
 
    layout: project.html

    title: How to make Egg Salad
    date: 2015-12-12
    content: |
        {% from 'layout/project.html' import project_img %}
        {{ project_img('egg-salad.jpg','This looks delicious!') }}
        ## Instructions
        - buy eggs
        - buy salad
        - blend
        - enjoy

It's necessary to import the `project_img` macro here because the content file is rendered in a separate template before substitution in your layout file.  You could also define the macro directly in this content file, but this way allows you to use the `project_img` macro elsewhere.
