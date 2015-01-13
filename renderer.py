# -*- coding: utf-8 -*-
"""Render template class"""

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
  <meta property="fb:admins"       content="poresopropongo"/>
  <meta property="og:url"          content="{0}"/>
  <meta property="og:image"        content="http://poresopropongo.mx/{1}"/>
  <meta property="og:image"        content="http://poresopropongo.mx/{2}"/>
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

        <a class="pull-left" href="/">
          <img alt="Ya Me Cansé Por Eso Propongo"
               src="/logo.png"
               width="300px" />
        </a>
      </div>
      <div class="navbar-collapse collapse">

        <ul class="nav navbar-nav navbar-right">
          <li><a href="/">Postales enviadas</a></li>
          <li><a href="http://postcard.com/join-a-movement/15"> Manda tu postal </a> </li>
          <li><a href="/randcard">Postal al azar</a></li>
          <li><a href="/about.html">¿Por qué proponer?</a></li>
          <li><a href="/contact.html">Contacto</a></li>
          <li>%s</li> <!-- navlinks -->
          <li>
            <form class="navbar-form navbar-right" action="/jump" method="POST" >
              <div class="input-group">
                <input type="text"
                       class="form-control"
                       name="page_number"
                       size="12"
                       placeholder="Jump to page">
              </div>
            </form>
          </li>
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
        if self.view.do_render_navlinks:
            navlinks = self.render_navlinks()
        else:
            navlinks = ""
        navbar_html = NAVBAR_HTML % (self.view.permalink,
                                     self.view.permalink,
                                     navlinks,)
        return navbar_html

    def render_social_media_metadata(self):
        sm_metadata_html = SM_METADATA_TEMPLATE.format(
                               self.view.permalink,
                               self.view.img_urls[0],
                               self.view.img_urls[1],)
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

        return PAGE_TEMPLATE % (sm_metadata,
                                navbar,
                                postcards)
