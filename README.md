# cereal
A minimal static website generator.

Cereal is a tiny static website generator which reads your page content from one file then stuffs it into a template, allowing you to quickly create multiple pages like blog posts or project documentation.

I created Cereal because most of the static site generators I researched (Jekyll, Pelican, Nikola, etc.) did way more than I wanted, which was simply to separate content from layout.

## Dependencies

* jinja2
* yaml
* mistune (markdown support)

## Example

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
    content: |
        ## Instructions
        - buy milk
        - buy cereal
        - mix them together
        ![img delicious](cereal.jpg)

Note that the only 'special' fields here are `layout` and `content`.  `layout` tells Cereal which layout to use for generating the html, and `content` is the main body for the page (in Markdown) which gets converted into html.  `title` and `date` are just strings that get inserted into the Jinja2 template.  Now lets build the website.

    python build.py

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

![Wowza!](http://i.imgur.com/5xYkoQD.png)

## Directories

Build your directory structure however you want.  Cereal will descend into directories in `content` and output into an equivalent directory in `out`.  For example, the content file
    content/foo/myproj.yaml
would create the output
    out/foo/myproj.html
    The only requirement is that the template specified in `myproj.yaml` must be located in
    layout/foo/

    - content/
        - foo/
                myproj.yaml
    - layout/
        - foo/
                project.html
    - out/
        - foo/
                myproj.html
