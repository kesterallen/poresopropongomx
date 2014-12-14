# -*- coding: utf-8 -*-
"""Render template class"""

SM_METADATA_TEMPLATE = """
  <!-- Twitter card -->
  <meta name="twitter:card"        content="photo"/>
  <meta name="twitter:site"        content="@poresopropongo"/>
  <meta name="twitter:creator"     content="@poresopropongo"/>
  <meta name="twitter:url"         content="%s"/>
  <meta name="twitter:image"       content="http://poresopropongo.mx/%s"/>
  
  <!-- Facebook preview-->
  <meta property="og:type"         content="blog"/> 
  <meta property="og:site_name"    content="Por Eso Propongo"/> 
  <meta property="fb:admins"       content="poresopropongo"/> 
  <meta property="og:url"          content="%s"/>
  <meta property="og:image"        content="http://poresopropongo.mx/%s"/>
"""

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

        <!-- Social media buttons start-->
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
        <!-- Social media buttons end-->

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
      max-height:140px ! might work
    }
  </style>
  <!-- social media metadata start -->
  %s 
  <!-- social media metadata end -->
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
<!-- Hook for FB Share button end-->

<div class="container-fluid">
  %s <!-- navbar -->
  <div class="row">
    <!-- postcards start -->
    %s 
    <!-- postcards end -->
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
        self.img_css = ('    <div class="col-lg-%s '
                                        'col-md-%s '
                                        'col-sm-%s '
                                        'col-xm-%s" '
                                 'style="background-color:black;">\n' %
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

    def render_navbar(self):
        navlinks = self.render_navlinks() if self.view.do_render_navlinks else ""
        navbar_html = NAVBAR_HTML % (self.view.permalink,
                                     self.view.permalink,
                                     navlinks,)
        return navbar_html

    def render_social_media_metadata(self):
        sm_metadata_html = SM_METADATA_TEMPLATE % (
                               self.view.permalink,
                               self.view.img_url,
                               self.view.permalink,
                               self.view.img_url,)
        return sm_metadata_html

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

    def render(self):
        """Render the page and return the text."""
        navbar = self.render_navbar()
        postcards = self.render_postcards()
        sm_metadata = self.render_social_media_metadata()

        return PAGE_TEMPLATE % (sm_metadata, navbar, postcards,)
