# Demo

This demo is an extension of the README provided in the base directory.  Namely, it shows to how to do template inheritance (see `layout/base.html`) and how to pass a list of items to a layout (see `content/index.html` and `layout/index.html`).  

To build the demo, run `cereal.py` from this directory.

    python ../cereal.py

## Jinja2 macros inside content files

Jinja2 in your content files allows you to do more complex things, like functionally generated html.

The example below shows how to use jinja2 macros to create captioned images in your content files.

`content/projects/egg_salad.yaml`
 
    layout: project.html

    title: How to make Egg Salad
    date: 2015-12-12
    content: !join
        - !j2 |
            {{ project_img('egg-salad.jpg','This looks delicious!') }}
        - !md |
            ## Instructions
            - buy eggs
            - buy salad
            - blend
            - enjoy
        - !py |
            print 1+1
            print 2+3
            for x in range(99):print x

It's necessary to import the `project_img` macro here because the content file is rendered in a separate template before substitution in your layout file.  You could also define the macro directly in this content file, but this way allows you to use the `project_img` macro elsewhere.

## Custom processors and other shenanigans
You can write your own content processors for more customizability.  Below is a demo of the Python context processor.

`content/projects/numbers.yaml`

    layout: project.html

    title: Number fun
    content: !join
        - !py |
            print "Hello World"
            print "<ul>"
            for x in range(99):
            print "<li>%s</li>" % x
            print "</ul>"

Result: `out/projects/numbers.html`

    <!DOCTYPE html>
    <html>
    <h1> Evidlo's Recipes </h1>

    <h1>Number fun</h1>
    <h2></h2>

    Hello World
    <ul>
    <li>0</li>
    <li>1</li>
    <li>2</li>
    <li>3</li>
    <li>4</li>
    <li>5</li>
    <li>6</li>
    ...

![Numbers](http://i.imgur.com/WxMi8TP.png)
