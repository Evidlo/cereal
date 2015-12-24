# Demo
To build the demo, run `cereal.py` from this directory.

    python ../cereal.py
    
Note:  You need `PyYaml`, `jinja2`, and `mistune`

    pip install PyYaml jinja2 mistune
    
## Extended Features

This is an extension of the README provided in the base directory. 

## Custom processors and other shenanigans
You can write your own content processors for more customizability.  Below is a demo of the Python context processor.

`content/projects/numbers.yaml`

    layout: project.html

    title: Number fun
    content: !py |
        print "Hello World"
        print "<ul>"
        for x in range(99):
            print "<li>%s</li>" % x
        print "</ul>"
        layout: project.html

`out/projects/numbers.html`

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

## Multiple content processors and the `!join` processor

You can run your nodes through multiple content processors by separating them with a comma.  This allows you to do something like use markdown and Jinja2 in the same node.

`content/projects/egg_salad.yaml`

    layout: project.html

    title: How to make Egg Salad
    date: 2015-12-12
    content: !md,j2 |
        {{ project_img('egg-salad.jpg','This looks delicious!') }}
        ## Instructions
        - buy eggs
        - buy salad
        - blend
        - enjoy
        
Alternatively, you can process different parts of a node with different processors using the `!join` tag.  This will process each item in a list with whatever processor you specify, and then join the result, similar to Python's string join function.

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
        
Note the lack of '|' after `!join`.  This is because this node contains a YAML list (sequence node) instead of a block of text (scalar node).

## Jinja2 macros inside content files

Jinja2 in your content files allows you to do more complex things, like functionally generated html.

The example below shows how to use jinja2 macros to create captioned images in your content files.

First define a Jinja2 macro.

`layout/macros.html`
    {# Define custom macros here #}
    {# These are available to all content nodes with the !j2 tag #}

    {% macro project_img(src,desc='') -%}
    <img style="display:block;" src="{{src}}">
    <span>{{desc}}</span>
    {%- endmacro %}

    {% block _macro_ %}
    {% endblock %}
    
Now you can use this on any node with a `!j2 tag`

`content/projects/egg_salad.yaml`
 
    layout: project.html

    title: How to make Egg Salad
    date: 2015-12-12
    content: !j2 |
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
            


