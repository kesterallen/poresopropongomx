# -*- coding: utf-8 -*-
"""Render template class"""

IS_TEST = False
# Relative to /cgi-bin:
if IS_TEST:
    NAVBAR_HTML_FILENAME = "navbar.html"
else:
    NAVBAR_HTML_FILENAME = "../navbar.html"

SM_METADATA_TEMPLATE = """
  <!-- Twitter card -->
  <meta name="twitter:card"        content="gallery"/>
  <meta name="twitter:site"        content="@poresopropongo"/>
  <meta name="twitter:title"       content="Por Eso Propongo"/>
  <meta name="twitter:creator"     content="@poresopropongo"/>
  <meta name="twitter:url"         content="{0}"/>
  <meta name="twitter:image0:src"  content="http://poresopropongo.mx/{1}"/>
  <meta name="twitter:image1:src"  content="http://poresopropongo.mx/{2}"/>
  <meta name="twitter:image2:src"  content="http://poresopropongo.mx/{1}"/>
  <meta name="twitter:image3:src"  content="http://poresopropongo.mx/{2}"/>

  <!-- Facebook preview-->
  <meta property="og:type"         content="blog"/>
  <meta property="og:site_name"    content="Por Eso Propongo"/>
  <meta property="og:title"        content="Por Eso Propongo"/>
  <meta property="fb:admins"       content="386237151543281"/>
                          <!-- from http://graph.facebook.com/poresopropongo -->
  <meta property="og:url"          content="{0}"/>
  <meta property="og:image"        content="http://poresopropongo.mx/{1}"/>
  <meta property="og:image"        content="http://poresopropongo.mx/{2}"/>
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
      padding-top: 180px;
    }
    .navbar-nav > li > a {
      padding-top:25px !important;
      padding-bottom:25px !important;
    }
    .navbar {
      min-height:140px !important;
    }
  </style>
  <!-- social media metadata start -->
  %s
  <!-- social media metadata end -->
  <title>Por Eso Propongo</title>
</head>

<div class="container-fluid">
  %s <!-- navbar -->
  <div class="row">
    <!-- postcards start -->
%s
    <!-- postcards end -->
  </div>
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
        if self.view.num_images_display == 1: # single image
            sizes = [12, 12, 12, 12]
        elif self.view.num_images_display == 2: # card
            sizes = [6, 12, 12, 12]
        else: # gallery
            sizes = [3, 6, 6, 6]
        self.div_class = ('col-lg-%s col-md-%s col-sm-%s col-xm-%s' %
                          (sizes[0], sizes[1], sizes[2], sizes[3]))

    def render_navlinks(self):
        """Render the navlinks' HTML in bootstrap style and return the text.
        Skip if the view is a single card."""
        # Skip if this is a single image, or a single card:
        #
        if self.view.num_images_display <= 2:
            return ""

        navlinks_html = ['    <ul class="pagination">']

        for navlink in self.view.navlinks:
            if navlink is None:
                navlink = {'active': 'disabled', 'href': '#', 'text': '...'}
            navlinks_html.append(
                '      <li class="%s"><a href="/%s">%s</a></li>' %
                (navlink['active'], navlink['href'], navlink['text'])
            )
        navlinks_html.append('    </ul>')

        text = "\n".join(navlinks_html)
        return text

    def render_navbar(self):
        """
        This is a kludgy way to get the navbar all in one file which
        is used by the static pages and this class. This method does replaces
        on the FB and Twitter button included URLs, and renders the navlinks
        if applicable.
        """
        if self.view.do_render_navlinks:
            navlinks = self.render_navlinks()
        else:
            navlinks = ""

        with open(NAVBAR_HTML_FILENAME) as nb_file:
            navbar_html = nb_file.read()
        navbar_html = navbar_html.replace(
                          'data-href="http://poresopropongo.mx"',
                          'data-href="%s"' % self.view.permalink)
        navbar_html = navbar_html.replace(
                           'data-url="http://poresopropongo.mx"',
                           'data-url="%s"' % self.view.permalink)
        navbar_html = navbar_html.replace(
                            '<div class="navlinks"></div>',
                            '<li>%s</li>' % navlinks)
        return navbar_html

    def render_social_media_metadata(self):
        """Render the twitter and FB metadata cards."""
        sm_metadata_html = SM_METADATA_TEMPLATE.format(
                               self.view.permalink,
                               self.view.img_urls[1],
                               self.view.img_urls[0],)
        return sm_metadata_html

    def render_postcards(self):
        """Render the postcards' HTML and return the text."""
        postcards = []
        for postcard_image in self.view.postcard_images:
            postcard = (
                '    <div class="%s" style="background-color:black;">\n'
                '        <a href="%s" >\n'
                '          <img src="%s" class="thumbnail img-responsive">\n'
                '        </a>\n'
                '    </div>') % (self.div_class,
                                 postcard_image['href'],
                                 postcard_image['img_src'])
            postcards.append(postcard)
        text = "\n".join(postcards)
        return text

    def render(self):
        """Render the page and return the text."""
        navbar = self.render_navbar()
        postcards = self.render_postcards()
        sm_metadata = self.render_social_media_metadata()

        return PAGE_TEMPLATE % (sm_metadata, navbar, postcards)
