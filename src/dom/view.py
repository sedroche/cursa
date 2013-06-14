'''
Created on 2 Feb 2013

Author: John Roche
'''
import config


def get_topic_view(title, content):
    top = _create_top(title).format(css=_topiccss())
    content = _create_content(content)
    bottom = _create_bottom().format(js=_topicjs())
    return u''.join([top,
                    content,
                    bottom])


def get_step_view(title, content, navbar, css):
    top = _create_top(title).format(css=_stepcss(css))
    content = _create_content(content)
    bottom = _create_bottom().format(js=_stepjs())
    return u''.join([top,
                    navbar,
                    content,
                    bottom])


def get_module_view(title, content):
    top = _create_top(title).format(css=_modulecss())
    content = _create_content(content)
    bottom = _create_bottom().format(js=_modulejs())
    return u''.join([top,
                    content,
                    bottom])


def get_pres_view(title, content, css):
    return _pres_view(title, content, css)


def get_lab_text_view(content, css):
    top = _create_top('').format(css=_step_text_css(css))
    content = _create_content(content)
    bottom = _create_step_text_bottom().format(js=_step_text_js())
    return u''.join([top,
                    content,
                    bottom])


def get_pres_text_view(sections, css):
    return _pres_text_view(sections, css)


def _create_top(title):
    return u"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{{css}}
</head>
<body>

<div id="container" class="container-fluid">

""".format(title=title)


def _create_content(content):
    return u"""

<div id="content" class="row-fluid">
<div class="span12">
  <!--Body content-->
  {content}
</div>

</div>

""".format(content=content)


def _create_bottom():
    return u"""

      </div>

      <footer id="footer" class="container-fluid">
        <p id="footertext">
          Prepared by {contributor}s. Except where otherwise noted, this content is licensed under a 
          <a class="externalLink" href="http://creativecommons.org/licenses/by-nc/3.0/" 
            title="External link to http://creativecommons.org/licenses/by-nc/3.0/" 
            target="_blank">Creative Commons Attribution-NonCommercial 3.0 License
          </a>
        </p>
      </footer>
{{js}}
  </body>
</html>
 """.format(contributor=config.contributor)


def _create_step_text_bottom():
    return u"""

      </div>
{js}
  </body>
</html>
 """


def _stepcss(css):
    cssstring = ''
    for cssfile in css:
        csslink = '<link rel="stylesheet" href="./assets/css/{0}" type="text/css">'.format(cssfile)
        cssstring = '\n'.join([cssstring,
                               csslink])
    return cssstring


def _step_text_css(css):
    cssstring = ''
    for cssfile in css:
        csslink = '<link rel="stylesheet" href="{0}/{1}" type="text/css">'.format(config.cursa_path,
                                                                                  cssfile)
        cssstring = '\n'.join([cssstring,
                               csslink])

    pagebreak_css = '''<style type="text/css" media="screen,print">
                            .page-breaker {
                            position: relative !important;
                            display: block !important;
                            page-break-after: always !important;
                            clear: both !important;
                            }
                       </style>'''

    cssstring = '\n'.join([cssstring,
                           pagebreak_css])

    return cssstring


def _stepjs():
    return u"""

<script src="./assets/js/highlight.pack.js"></script>
<script src="./assets/js/jquery-1.7.2.min.js"></script>
<script src="./assets/js/bootstrap.min.js"></script>

  <script>
  hljs.tabReplace = '    ';
  hljs.initHighlightingOnLoad();
  </script>
"""


def _step_text_js():
    return u"""

<script src="{path}/highlight.pack.js"></script>

  <script>
  hljs.tabReplace = '    ';
  hljs.initHighlightingOnLoad();
  </script>
""".format(path=config.cursa_path)


def _topiccss():
    return u"""
<link rel="stylesheet" href="./assets/css/bootstrap.min.css" type="text/css">
<link rel="stylesheet" href="./assets/css/bootstrap-responsive.min.css" type="text/css">
<link rel="stylesheet" href="./assets/css/cursa.css" type="text/css">
"""


def _topicjs():
    return u"""

<script src="./assets/js/highlight.pack.js"></script>
<script src="./assets/js/jquery-1.7.2.min.js"></script>
<script src="./assets/js/bootstrap.min.js"></script>

  <script>
  hljs.tabReplace = '    ';
  hljs.initHighlightingOnLoad();
  </script>
"""


def _modulecss():
    return u"""
<link rel="stylesheet" href="./assets/css/bootstrap.min.css" type="text/css">
<link rel="stylesheet" href="./assets/css/bootstrap-responsive.min.css" type="text/css">
<link rel="stylesheet" href="./assets/css/cursa.css" type="text/css">
<link rel="stylesheet" href="./assets/css/github.css" type="text/css"/>
"""


def _modulejs():
    return u"""

<script src="./assets/js/highlight.pack.js"></script>
<script src="./assets/js/jquery-1.7.2.min.js"></script>
<script src="./assets/js/bootstrap.min.js"></script>

  <script>
  hljs.tabReplace = '    ';
  hljs.initHighlightingOnLoad();
  </script>
"""


def _pres_view(title, content, css):
    cssstring = ''
    for cssfile in css:
        csslink = '<link rel="stylesheet" href="./assets/css/{0}" type="text/css">'.format(cssfile)
        cssstring = '\n'.join([cssstring,
                               csslink])

    return u"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta name="viewport" content="width=1024, user-scalable=no">

    <title>{title}</title>

    <!-- Required stylesheet -->

    {css}

    <!-- Required Modernizr file -->
    <script src="./assets/js/modernizr.custom.js"></script>
</head>
<body class="deck-container">

<!-- Begin slides. Just make elements with a class of slide. -->

{content}

<!-- End slides. -->


<!-- Begin extension snippets. Add or remove as needed. -->

<!-- deck.navigation snippet -->
<a href="#" class="deck-prev-link" title="Previous">&#8592;</a>
<a href="#" class="deck-next-link" title="Next">&#8594;</a>

<!-- deck.status snippet -->
<p class="deck-status">
    <span class="deck-status-current"></span>
    /
    <span class="deck-status-total"></span>
</p>

<!-- deck.goto snippet -->
<form action="." method="get" class="goto-form">
    <label for="goto-slide">Go to slide:</label>
    <input type="text" name="slidenum" id="goto-slide" list="goto-datalist">
    <datalist id="goto-datalist"></datalist>
    <input type="submit" value="Go">
</form>

<!-- deck.hash snippet -->
<a href="." title="Permalink to this slide" class="deck-permalink">#</a>

<!-- End extension snippets. -->


<!-- Required JS files. -->
<script src="./assets/js/jquery-1.7.2.min.js"></script>
<script src="./assets/js/deck.core.js"></script>

<!-- Extension JS files. Add or remove as needed. -->
<script src="./assets/js/deck.core.js"></script>
<script src="./assets/js/deck.hash.js"></script>
<script src="./assets/js/deck.menu.js"></script>
<script src="./assets/js/deck.goto.js"></script>
<script src="./assets/js/deck.status.js"></script>
<script src="./assets/js/deck.navigation.js"></script>
<script src="./assets/js/deck.scale.js"></script>
<script src="./assets/js/highlight.pack.js"></script>

<!-- Initialize the deck. You can put this in an external file if desired. -->
<script>
    $(function() {{
        $.deck('.slide');
        hljs.tabReplace = '    ';
        hljs.initHighlightingOnLoad();
    }});
</script>
</body>
</html>""".format(title=title,
                  content=content,
                  css=cssstring)


def _pres_text_view(sections, css):
    cssstring = ''
    for cssfile in css:
        csslink = '<link rel="stylesheet" href="{path}/{css}" type="text/css">'.format(path=config.cursa_path,
                                                                                       css=cssfile)
        cssstring = '\n'.join([cssstring,
                               csslink])

    return u"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta name="viewport" content="width=1024, user-scalable=no">

    <title></title>

    {css}

    <style type="text/css" media="screen,print">
    .page-breaker {{
        position: relative !important;
        display: block !important;
        page-break-after: always !important;
        clear: both !important;
    }}

     * {{
        -webkit-transition: none !important;
        visibility: visible !important;
    }}

    body{{
        padding: 0em !important;
        margin: 0em !important;
        }}
    </style>

</head>

<body class="deck-container">

{sections}

<script src="{path}/highlight.pack.js"></script>

<script>
hljs.tabReplace = '    ';
hljs.initHighlightingOnLoad();
</script>

</body>
</html>""".format(css=cssstring,
                  sections=sections,
                  path=config.cursa_path)
