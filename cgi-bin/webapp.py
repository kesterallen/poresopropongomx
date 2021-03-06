# -*- coding: utf-8 -*- 

import logging
import os
import jinja2
import webapp2
import urllib

NUM_IMAGES_MINIMUM = 2
DEFAULT_NUM_IMAGES = 100
DEFAULT_NUM_IMAGES_ONE_CARD = 2

IMAGE_URL_TEMPLATE ='http://poresopropongo.mx/images/%s' 
CARD_URL_TEMPLATE = '/card/%s'
IMAGE_LIST_FILE = 'http://poresopropongo.mx/images/image_list.txt'

JINJA_ENVIRONMENT = jinja2.Environment(
                        loader=jinja2.FileSystemLoader(
                                        os.path.dirname(__file__)),
                        extensions=['jinja2.ext.autoescape'],
                        autoescape=True)


class ViewAllHandler(webapp2.RequestHandler):
    """The view handler for this app."""

    def load_indices(self, offset, num_images_display):
        """
        Create a list of the indexes to the newest images.
        Require the list to be an even number of images, so that a postcard
          front is matched to a postcard back.
        Require the offset to be an even number, so that the right postcard
          front is matched to the postcard back.
        Don't index out of the image_names list, on either side

        SETS: self.image_indices, self.offset, self.num_images_display
              Implicitly sets self.image_page
        """
        try:
            num_images_display = int(float(num_images_display))
        except:
            num_images_display = DEFAULT_NUM_IMAGES
        if num_images_display % 2 == 1:
            num_images_display -= 1
        if num_images_display < 1:
            num_images_display = NUM_IMAGES_MINIMUM
        self.num_images_display = num_images_display

        try:
            offset = int(float(offset))
        except:
            offset = self.max_good_display_offset
        if offset < 0:
            offset = 0
        if offset > self.max_good_display_offset:
            offset = self.max_good_display_offset
        if offset % 2 == 1:
            offset -= 1
        self.offset = offset

        stop_index = self.offset + num_images_display
        if stop_index > self.num_images:
            stop_index = self.num_images
        if stop_index < 1:
            stop_index = NUM_IMAGES_MINIMUM

        image_indices = range(self.offset, stop_index)
        self.image_indices = image_indices

    @property
    def max_good_display_offset(self):
        """Determine the most recent set of self.num_images_display images to
        display, and return the offset to that set of images."""
        offset = self.num_images_display * (self.num_images /
                                            self.num_images_display - 1)
        return offset

    @property
    def image_page(self):
        """Return the current page number, where one page has
        num_images_display on it."""
        return int(self.offset) / int(self.num_images_display)

    @property
    def num_pages(self):
        """Return the total number of pages, where one page has
        num_images_display on it."""
        return int(self.num_images) / int(self.num_images_display)

    @property
    def newest_page_offset(self):
        """Return the offset of the newest full page."""
        return self.num_pages * self.num_images_display

    def load_images(self):
        """Load the image names, and set self.num_images."""

        # TODO: os.listdir doesn't seem to work on GAE
        #image_names = os.listdir('images')
        image_names = urllib.urlopen(IMAGE_LIST_FILE).read().splitlines()
        self.image_names = sorted(image_names, key=lambda s: s.lower())
        self.num_images = len(self.image_names)
        #for i in range(0, self.num_images, 2):
            #self.image_names[i], self.image_names[i+1] = self.image_names[i+1],\
                                                         #self.image_names[i]

        if self.num_images % 2 == 1:
            self.image_names.pop(-1)
            self.num_images = len(self.image_names)

    def load_navlinks(self):
        """Generate a " < 1 2 3 ... n-2 n-1 n > " type of navlink set. The '1'
        link will go to the oldest set, the n link will go to the newest set.
        The math in the 'href' definition controls this."""

        self.navlinks = []

        next_offset = self.offset + self.num_images_display
        prev_offset = self.offset - self.num_images_display

        # Make an "More Recent" arrow button if this is not the most recent
        # page:
        if next_offset <= self.max_good_display_offset:
            self.navlinks.append(
                {'href': next_offset, 'text': '&laquo;', 'active': ''})

        page_indices = range(self.num_pages)

        for ipage in page_indices:
            is_current_page = (self.num_pages - ipage - 1) == self.image_page
            is_edge_page = ipage in [page_indices[0],  page_indices[1],
                                     page_indices[-2], page_indices[-1],]
            if is_current_page or is_edge_page:
                navlink = {
                    'href': (self.num_pages - (ipage+1)) * self.num_images_display,
                    'text': '%s' % (ipage+1),
                    'active': '',
                }
                if is_current_page:
                    navlink['active'] = 'active'
            else:
                navlink = None
            # Add the navlink if it isn't a double '...' link
            if (len(self.navlinks) > 0 and
                self.navlinks[-1] is None and navlink is None):
                pass
            else:
                self.navlinks.append(navlink)

        # Make an "Older Page" arrow button if this is not the most oldest
        # page:
        if prev_offset >= 0:
            self.navlinks.append(
                {'href': prev_offset, 'text': '&raquo;', 'active': ''})

    def load_postcards(self):
        """If the gallery is being displayed, the link should go to a 
        single-card view. If a single card is being displayed, the 
        link should go to the image."""

        self.postcard_images = []
        for i in self.image_indices:
            image = self.image_names[i]
            postcard_image = {
                'name': image,
                'img_src': IMAGE_URL_TEMPLATE % image,
            }
            if self.is_single:
                postcard_image['href'] = IMAGE_URL_TEMPLATE % image
            else:
                postcard_image['href'] = CARD_URL_TEMPLATE % i

            self.postcard_images.append(postcard_image)

    def object_init(self, offset, num_images_display):
        self.load_images()
        self.load_indices(offset, num_images_display)
        self.load_navlinks()
        self.load_postcards()

    def get_page(self, offset, num_images_display):
        self.object_init(offset, num_images_display)
        template = JINJA_ENVIRONMENT.get_template('page_webapp.html')
        template_data = {'navlinks': self.navlinks, 'postcard_images': self.postcard_images}
        self.response.write(template.render(template_data))

    def get(self, offset=None):
        self.is_single = False
        self.get_page(offset, DEFAULT_NUM_IMAGES)

class ViewOneHandler(ViewAllHandler):
    def get(self, offset=0):
        self.is_single = True
        self.get_page(offset, DEFAULT_NUM_IMAGES_ONE_CARD)

def handle_404(request, response, exception):
    """Page not found handler"""
    logging.exception(exception)
    response.write('Page not found. Error is "%s"' % exception)
    response.set_status(404)

def handle_500(request, response, exception):
    """Server error handler"""
    logging.exception(exception)
    response.write('A server error occurred!')
    response.set_status(500)

app = webapp2.WSGIApplication(
          routes=[
              ('/card/(.+?)', ViewOneHandler),
              ('/card.*', ViewOneHandler),
              ('/(.+?)/(.+?)', ViewAllHandler),
              ('/(.+?)/', ViewAllHandler),
              ('/(.+?)', ViewAllHandler),
              ('/.*', ViewAllHandler),
          ],
          debug=True
      )
app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500
