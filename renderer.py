# -*- coding: utf-8 -*-
"""Render template class"""

NAVBAR_HTML = """
  <div class="navbar navbar-default navbar-fixed-top">
    <div class="container">
      <div class="navbar-header">
        <button type="button"
                class="navbar-toggle collapsed"
                data-toggle="collapse"
                data-target=".navbar-collapse">
          <span class="sr-only">Toggle navigation</span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
        </button>

        <a class="pull-left" href="/">
          <img alt="Ya Me Cansé Por Eso Propongo"
               src="/logo.png"
               width="300px" />
        </a>
      </div>
      <div class="navbar-collapse collapse">

        <!-- Social media buttons-->
        <div class="fb-share-button"
             data-href="%s"
             data-layout="button_count">
        </div>
        <a href="https://twitter.com/share" 
          class="twitter-share-button" 
          data-url="%s"
          data-text="#YaMeCansé #PorEsoPropongo"
          data-dnt="true"
        >Tweet</a>
        <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}(document, 'script', 'twitter-wjs');</script>

        <ul class="nav navbar-nav navbar-right">
          <li><a href="/">Postales enviadas</a></li>
          <li><a href="http://postcard.com/join-a-movement/15">Manda tu postal</a></li>
          <li><a href="/about.html">¿Por qué proponer?</a></li>
          <li><a href="/contact.html">Contacto</a></li>
          <li>%s</li> <!-- navlinks -->
        </ul>
      </div><!--/.nav-collapse -->


    </div>
  </div>
"""

PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="/bootstrap-3.2.0.min.css">
  <style>
    body {
      padding-top: 150px;
    }
    .navbar-nav > li > a {
      padding-top:25px !important;
      padding-bottom:25px !important;
    }
    .navbar {
      min-height:140px !important
    }
  </style>
</head>

<body role="document">
<!-- Hook for FB Share button-->
<div id="fb-root"></div>
<script>(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.0";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));</script>

<div class="container-fluid">
""" + NAVBAR_HTML + """
  <div class="row">
%s
  </div>
</div>

<script src="/jquery-1.11.1.min.js"></script>
<script src="/bootstrap-3.2.0.min.js"></script>
</body>
</html>
"""

class Renderer(object):
    """Rendering workaround for FatCow."""

    def __init__(self, view):
        """Set up the view CSS."""
        self.view = view
        if self.view.is_single:
            sizes = [6, 12, 12, 12]
        else:
            sizes = [3, 6, 6, 6]
        self.img_css = ('    <div class="col-lg-%s '
                                        'col-md-%s '
                                        'col-sm-%s '
                                        'col-xm-%s" '
                                 'style="background-color:black;">\n' %
                                 (sizes[0], sizes[1], sizes[2], sizes[3]))

    def render_navlinks(self):
        """Render the navlinks' HTML in bootstrap style and return the text.
        Skip if the view is a single card."""
        # Skip if this is a single card:
        #
        if self.view.is_single:
            return ""

        navlinks_html = ['    <ul class="pagination">']

        for navlink in self.view.navlinks:
            if navlink is not None:
                navlinks_html.append(
                    '      <li class="%s"><a href="/%s">%s</a></li>' %
                    (navlink['active'], navlink['href'], navlink['text'])
                )
            else:
                navlinks_html.append(
                    '      <li class="disabled"><a href="#">...</a></li>'
                )

        navlinks_html.append('    </ul>')

        text = "\n".join(navlinks_html)
        return text

    def render_postcards(self):
        """Render the postcards' HTML and return the text."""
        postcards = []
        for postcard_image in self.view.postcard_images:
            postcard = (
                '%s\n'
                '        <a href="%s" >\n'
                '          <img src="%s" class="thumbnail img-responsive">\n'
                '        </a>\n'
                '    </div>') % (self.img_css,
                                 postcard_image['href'],
                                 postcard_image['img_src'])
            postcards.append(postcard)
        text = "\n".join(postcards)
        return text

    def render(self, render_navlinks=True):
        """Render the page and return the text."""
        navlinks = self.render_navlinks() if render_navlinks else ""
        postcards = self.render_postcards()
        return PAGE_TEMPLATE % (
                    self.view.permalink,
                    self.view.permalink,
                    navlinks,
                    postcards,
               )
