# cereal
A minimal static website generator.

![Cereal](http://imgur.com/j9BlQVV.png)

Cereal is a tiny static website generator which reads your page content from one file then stuffs it into a template, allowing you to quickly create multiple pages like blog posts or project documentation.

I created Cereal because most of the static site generators I researched (Jekyll, Pelican, Nikola, etc.) did way more than I wanted, which was simply to separate content from layout.

Cereal makes use of [YAML](https://en.wikipedia.org/wiki/Yaml) and [Jinja2](http://jinja.pocoo.org/docs/dev/), so a basic knowledge of those languages is a prerequisite.

#### Table of Contents

* [cereal](#cereal)
    * [Dependencies](#dependencies)
* [Simple Example](#simple-example)
    * [Template Inheritance](#template-inheritance)
    * [Iterable Data](#iterable-data)
* [Extended Features](#extended-features)
    * [Custom processors and other shenanigans](#custom-processors-and-other-shenanigans)
    * [Multiple content processors and the !join processors](#multiple-content-processors-and-the-join-processors)
    * [Jinja2 macros inside content files](#jinja2-macros-inside-content-files)
    * [Directories](#directories)
* [Demo](#demo)
* [Why cereal?](#why-cereal)
                                                      


# Dependencies

* jinja2
* PyYAML
* mistune (markdown support)

`pip install PyYaml jinja2 mistune`

# Simple Example

Let's give a simple demonstration.  Let's say you want a simple site to document your projects, where each project page is identically formatted, but the words, pictures, etc. are different.  Here's an example [Jinja2 template]().

`layout/project.html`

    <!DOCTYPE html>

    <html>
        <h1>{{ title }}</h1>
        <h2>{{ date }}</h2>

        {{ content }}

    </html>

So now we have a basic template.  Let's write some content for a new project.

`content/my_project1.yaml`

    layout: project.html
    title: How to Make Cereal
    date: 2015-12-11
    content: !md |
        ![img delicious](cereal.jpg)
        ## Instructions
        - buy milk
        - buy cereal
        - mix them together

The `layout`, `title`, `date` and `content` entries are called `nodes`, per the YAML spec.
`layout` tells cereal which layout file (aka template) to use.  It will look in `layout/` for this file.
The other three nodes correspond to the variables in our layout file and will get substituted in when we compile the website.  Note the `|` and `!md` on the `content` node.  This signifies that everything inside `content` is a string and should be parsed as Markdown.

Let's build the website.

    python cereal.py

The output looks like this

`out/my_project1.html`

    <!DOCTYPE html>

    <html>
        <h1>How to Make Cereal</h1>
        <h2>2015-12-11</h2>

        <img src="cereal.jpg" alt="img delicious"></li>
        <h2>Instructions</h2>
        <ul>
            <li>buy milk</li>
            <li>buy cereal</li>
            <li>mix them together
        </ul>

    </html>

![Wowza!](http://imgur.com/kRBCzrj.png)

#### Template Inheritance

Lets add a header and footer to all of our pages.  Template inheritance is a feature of Jinja2, not Cereal, but we'll cover it anyway.  First create a parent template.

`layout/base.html`

    <!DOCTYPE html>
    <html>
    <h1> Evidlo's Recipes </h1>
    
    {% block body %}
    {% endblock body %}
    
    <h4> Created by MasterChef Evidlo </h4>
    </html>
    
Now change our project template to make use of this base template.

`layout/project.html`

    {% extends 'layout/base.html' %}
    
    {% block body %}
    <h1>{{ title }}</h1>
    <h2>{{ date }}</h2>

    {{ content }}
    {% endblock %}

![Header](https://i.imgur.com/xdjXV3S.png)

#### Iterable Data
Since YAML data maps directly to Python datatypes, we can do interesting things like looping over content items from our templates.  Lets make an index page that's easy to update whenever we add a new recipe.

`layout/index.html`

    {% extends "layout/base.html" %}
    
    {% block body %}
    <h2> {{title}} </h2>
    <ul>
    {% for link in links %}
        <li>
            <a href="{{link.link}}"> {{link.name}}</a> - {{link.desc}}
        </li>
    {% endfor %}
    </ul>
    {% endblock body %}
    
`content/index.yaml`

    layout: index.html
    title: Tasty Recipes
    links:
      - name: Cereal
        link: projects/cereal.html
        desc: A bowl of crunchy deliciousness.
      - name: Egg Salad
        link: projects/egg_salad.html
        desc: Great for LAN parties.

    
![Index](http://i.imgur.com/naadkA4.png)


# Extended Features


#### Custom processors and other shenanigans
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

#### Multiple content processors and the `!join` processor

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
        
Note the lack of `|` after `!join`.  This is because this node contains a YAML list (sequence node) instead of a block of text (scalar node).

#### Jinja2 macros inside content files

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
            


#### Directories

Build your directory structure however you want.  Cereal will descend into directories in `content` and output into an equivalent directory in `out`.  For example, the content file
    content/foo/myproj.yaml
would create the output
    out/foo/myproj.html

    - content/
        - foo/
            myproj.yaml
    - layout/
        project.html
    - out/
        - foo/
            myproj.html

# Demo
To build the demo, run `cereal.py` from the `demo` directory.

    cd demo
    python ../cereal.py
    
    

# Why cereal?

Cereal is delicious, that's why.
