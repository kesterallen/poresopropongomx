# -*- coding: utf-8 -*-
"""View class"""

import logging
import os
import cgi
import cgitb
from renderer import Renderer

NUM_IMAGES_MINIMUM = 1
DEFAULT_NUM_IMAGES = 100
DEFAULT_NUM_IMAGES_ONE_CARD = 2

IMAGE_FILE_LOCATION_TEMPLATE = '/images/%s'

PERMALINK_TEMPLATE = 'http://poresopropongo.mx/%s'
IMAGE_URL_TEMPLATE = '/img/%s'
CARD_URL_TEMPLATE = '/card/%s'

IMAGE_LIST_FILE = '../images/image_list.txt' # relative to /cgi-bin

class ViewGalleryHandler(object):
    """The view handler for the gallery."""

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

        # Load the num_images_display:
        #
        try:
            num_images_display = int(float(num_images_display))
        except (ValueError, TypeError) as err:
            logging.info("Error converting num_images_display: %s", err)
            num_images_display = DEFAULT_NUM_IMAGES
        #if num_images_display % 2 == 1:
            #num_images_display -= 1
        if num_images_display < 1:
            num_images_display = NUM_IMAGES_MINIMUM
        self.num_images_display = num_images_display

        # Load the offset:
        #
        try:
            offset = int(float(offset))
        except (ValueError, TypeError) as err:
            logging.info("Error converting offset: %s", err)
            offset = self.max_good_display_offset
        if offset < 0:
            offset = 0
        if offset > self.max_good_display_offset:
            offset = self.max_good_display_offset
        if offset % 2 == 1 and self.num_images_display != 1:
            offset -= 1
        self.offset = offset

        # Load the image_indices:
        #
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

        # Load the image list from the pre-generated file, if it exists,
        # otherwise disk-scan it.
        #
        try:
            with open(IMAGE_LIST_FILE) as img_file:
                image_names = img_file.read().splitlines()
                image_names = [i.split('/')[-1] for i in image_names]
            logging.info("Read image list file, using its data")
        except IOError as ioe:
            logging.error("Error reading image list file, doing ls: %s", ioe)
            image_names = os.listdir('../images')
        image_names = [f for f in image_names
                          if (f.lower().endswith('png') or 
                              #f.lower().endswith('jpeg') or
                              f.lower().endswith('jpg')
                             ) and f != 'logo.png']

        self.image_names = sorted(image_names, key=lambda s: s.lower())
        self.num_images = len(self.image_names)

        # Do a pairwise swap of the image names, so front of the card displays
        # first:
        #
        for i in range(1, self.num_images, 2):
            self.image_names[i-1], self.image_names[i] = self.image_names[i],\
                                                         self.image_names[i-1]

        # Ensure there are an even number of images, for side-by-side card
        # display:
        #
        if self.num_images % 2 == 1:
            self.image_names.pop(-1)
            self.num_images = len(self.image_names)

    def load_navlinks(self):
        """
        Generate a " < 1 2 3 ... n-2 n-1 n > " type of navlink set. The '1'
        link will go to the oldest set, the n link will go to the newest set.
        The math in the 'href' definition controls this.

        Note that this math is more awkward than it could be. This is caused
        by the implicit date-descending sort of self.image_names.
        """

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
            is_edge_page = ipage in [page_indices[0], page_indices[1],
                                     page_indices[-2], page_indices[-1],]
            if is_current_page or is_edge_page:
                navlink = {
                    'href': (self.num_pages - (ipage+1)) * \
                                self.num_images_display,
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
                'img_src': IMAGE_FILE_LOCATION_TEMPLATE % image,
            }
            if self.num_images_display == 1: # single image
                postcard_image['href'] = '#'
            if self.num_images_display == 2: # single postcard --
                                             # two images (front and back)
                postcard_image['href'] = IMAGE_URL_TEMPLATE % i
            else: # gallery
                postcard_image['href'] = CARD_URL_TEMPLATE % i

            self.postcard_images.append(postcard_image)

    @property
    def permalink(self):
        """Generate a permanent link for gallery page."""
        return PERMALINK_TEMPLATE % self.permalink_suffix

    def get(self):
        """Handle a GET request for the page."""
        renderer = Renderer(view=self)
        print "Content-type:text/html\n", renderer.render()

    def __init__(self,
                 offset=None,
                 num_images_display=DEFAULT_NUM_IMAGES):

        # Init member vars here to make pylint happy.
        self.image_names = None
        self.postcard_images = None
        self.image_indices = None
        self.offset = None
        self.navlinks = None
        self.num_images = None
        self.num_images_display = None

        # Load data.
        self.load_images()
        self.load_indices(offset, num_images_display)
        self.load_navlinks()
        self.load_postcards()
        self.permalink_suffix = self.offset
        self.img_url = "images/%s" % self.image_names[self.offset]
        self.do_render_navlinks = True

class ViewCardHandler(ViewGalleryHandler):
    """The view handler for a single card."""
    def __init__(self,
                 offset=None,
                 num_images_display=DEFAULT_NUM_IMAGES_ONE_CARD):
        """Passthrough with num_images_display set for card views."""
        super(ViewCardHandler, self).__init__(offset,
                                              num_images_display)
        self.permalink_suffix = "card/%s" % self.offset
        self.do_render_navlinks = False

class ViewImageHandler(ViewGalleryHandler):
    """The view handler for a single image (one side of a postcard)."""
    def __init__(self,
                 offset=None,
                 num_images_display=1):
        """Passthrough with num_images_display set for single image views."""
        super(ViewImageHandler, self).__init__(offset,
                                              num_images_display)
        self.permalink_suffix = "img/%s" % self.offset

def main():
    """Page view entry point."""
    cgitb.enable()

    try:
        args = cgi.FieldStorage()

        view_type = args['type'].value if 'type' in args else 'gallery'
        offset = args['offset'].value if 'offset' in args else None

        if view_type == 'card':
            view_handler = ViewCardHandler(offset)
        elif view_type == 'img':
            view_handler = ViewImageHandler(offset)
        else:
            view_handler = ViewGalleryHandler(offset)

        view_handler.get()
    except:
        print "Status: 500"
        cgitb.handler()

if __name__ == "__main__":
    main()
