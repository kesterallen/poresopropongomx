# -*- coding: utf-8 -*-
"""
View class.

This version implicitly assumes that images are in ../images_numbered (relative
to cgi-bin) and are in directory/filenames of the form '%07d/%10d.png', where
the directory is the 1000s place, and the filename is the starting-from-1 image
in that directory, e.g. '0001000/0001073.jpg' or '0013000/0013910.jpg'.
"""

import cgi
#import cgitb
import logging
import os
import random
from renderer import Renderer

NUM_IMAGES_IN_DIRECTORY = 1000

NUM_IMAGES_MINIMUM = 1
DEFAULT_NUM_IMAGES = 100
DEFAULT_NUM_IMAGES_ONE_CARD = 2

IMAGE_FILE_LOCATION_TEMPLATE = 'images_numbered/%s'
IMAGE_HREF_LOCATION_TEMPLATE = '/%s' % IMAGE_FILE_LOCATION_TEMPLATE
IMAGE_TEMPLATE = '%07d/%010d.jpg'

PERMALINK_TEMPLATE = 'http://poresopropongo.mx/%s'
IMG_URL_TEMPLATE = '/img/%s'
CARD_URL_TEMPLATE = '/card/%s'

IS_TEST = False
IS_CACHING_ON = False

# Relative to /cgi-bin:
if IS_TEST:
    IMAGE_COUNT_FILE = '/home/kester/Desktop/images_numbered/image_count.txt'
    CACHE_DIR = '/home/kester/Desktop/cached'
else:
    IMAGE_COUNT_FILE = '../images_numbered/image_count.txt'
    CACHE_DIR = '../cached'

def redirect(url):
    """Redirect to the url."""
    print "Status: 303 See other"
    print "Location: %s" % url

class ViewGalleryHandler(object):
    """The view handler for the gallery."""

    def __init__(self,
                 offset=None,
                 num_images_display=DEFAULT_NUM_IMAGES):
        """Construct an object and initialize the images and indices."""

        # Init member vars here to make pylint happy.
        self.postcard_images = []
        self.image_indices = []
        self.navlinks = []
        self.num_images = None
        self.num_images_display = None
        self.offset = offset
        self.do_render_navlinks = True
        self.permalink_suffix = None
        self.image_page = None

        # Load data. Don't change the order these loads are done in.
        self.load_image_count()
        self.load_indices(num_images_display)

        self.num_pages = int(self.num_images) / int(self.num_images_display)

        if IS_CACHING_ON and self.is_cached:
            return
        self.load_navlinks()
        self.load_postcards()
        self.permalink_suffix = self.offset

        if self.offset % 2 == 0:
            pair_offset = self.offset + 1
        else:
            pair_offset = self.offset - 1

        self.img_urls = [
            IMAGE_FILE_LOCATION_TEMPLATE % self.image_name(self.offset),
            IMAGE_FILE_LOCATION_TEMPLATE % self.image_name(pair_offset),]

    def load_indices(self, num_images_display):
        """
        Create a list of the indexes to the newest images.
        Require the list to be an even number of images, so that a postcard
          front is matched to a postcard back.
        Require self.offset to be an even number, so that the right postcard
          front is matched to the postcard back.
        Don't index out of the image_names list, on either side

        SETS: self.image_indices, .offset, .num_images_display, .image_page
        """

        # Load the num_images_display:
        #
        try:
            num_images_display = int(float(num_images_display))
        except (ValueError, TypeError) as err:
            logging.info("Error converting num_images_display: %s", err)
            num_images_display = DEFAULT_NUM_IMAGES
        if num_images_display < NUM_IMAGES_MINIMUM:
            num_images_display = NUM_IMAGES_MINIMUM
        self.num_images_display = num_images_display

        # Load the offset:
        #
        try:
            self.offset = int(float(self.offset))
        except (ValueError, TypeError) as err:
            logging.info("Error converting offset: %s", err)
            self.offset = self.max_good_display_offset
        if self.offset < 0:
            self.offset = 0
        if self.offset > self.max_good_display_offset:
            self.offset = self.max_good_display_offset
        is_odd = (self.offset % 2) == 1
        is_multi = self.num_images_display != 1
        if is_odd and is_multi:
            self.offset -= 1

        # Load the image_indices:
        #
        stop_index = self.offset + self.num_images_display
        if stop_index > self.num_images:
            stop_index = self.num_images
        if stop_index < 1:
            stop_index = NUM_IMAGES_MINIMUM
        image_indices = range(self.offset, stop_index)
        self.image_indices = image_indices

        # The current page number, where one page contains num_images_display:
        self.image_page = int(self.offset) / int(self.num_images_display)

    @property
    def random_card_url(self):
        """Generate the URL of a random card."""
        random_index = random.randint(0, self.num_images-1)
        return CARD_URL_TEMPLATE % random_index

    @property
    def max_good_display_offset(self):
        """Determine the most recent set of self.num_images_display images to
        display, and return the offset to that set of images."""
        offset = self.num_images_display * (self.num_images /
                                            self.num_images_display - 1)
        if offset < 0:
            offset = NUM_IMAGES_MINIMUM

        return offset

    @property
    def newest_page_offset(self):
        """Return the offset of the newest full page."""
        return self.num_pages * self.num_images_display

    def load_image_count(self):
        """Load the image names, and set self.num_images."""

        # Load the image list from the (pre-generated, sorted) list of images
        # file:
        #
        try:
            with open(IMAGE_COUNT_FILE) as img_file:
                image_count = int(float(img_file.read().strip()))
            logging.info("Read image count file, using its data")
        except IOError as ioe:
            logging.error("Error reading image list file: %s", ioe)
            image_count = 2
        self.num_images = image_count

        # Ensure there are an even number of images, for side-by-side card
        # display:
        #
        if self.num_images % 2 == 1:
            self.num_images -= 1
        if self.num_images < NUM_IMAGES_MINIMUM:
            self.num_images = NUM_IMAGES_MINIMUM

    def load_navlinks(self):
        """
        Trying just a '<< >>' navlink set.

        ###Generate a " < 1 current n > " type of navlink set. The '1'
        ###link will go to the oldest set, the n link will go to the newest set.
        ###The math in the 'href' definition controls this.
        ###
        ###Note that this math is more awkward than it could be. This is caused
        ###by the implicit date-descending sort of the images.
        """

        self.navlinks = []

        next_offset = self.offset + self.num_images_display
        prev_offset = self.offset - self.num_images_display

        # Make an "More Recent" (<<) arrow button if this is not the newest
        # page:
        if next_offset <= self.max_good_display_offset:
            self.navlinks.append(
                {'href': next_offset, 'text': '&laquo;', 'active': ''})

        page_indices = range(self.num_pages)

        for ipage in page_indices:
            is_current_page = (self.num_pages - ipage - 1) == self.image_page
            is_edge_page = ipage in [page_indices[0],
                                     #page_indices[1],
                                     #page_indices[-2],
                                     page_indices[-1],]
            if is_current_page or is_edge_page:
                href = (self.num_pages - (ipage+1)) * self.num_images_display
                navlink = {
                    'href': href,
                    'text': '%s' % (ipage+1),
                    'active': '',
                }
                if is_current_page:
                    navlink['active'] = 'active'
            else:
                navlink = None

            # Add the navlink if it is a the current page #valid page:
            #
            if navlink and is_current_page:
                self.navlinks.append(navlink)

            ## Add the navlink if it isn't the second consecutive '...' link
            #if (len(self.navlinks) > 0 and
            #    self.navlinks[-1] is None and navlink is None):
            #    pass
            #else:
            #    self.navlinks.append(navlink)

        # Make an "Older Page" (>>) arrow button if this is not the oldest
        # page:
        if prev_offset >= 0:
            self.navlinks.append(
                {'href': prev_offset, 'text': '&raquo;', 'active': ''})

    def image_name(self, i):
        """Make a URL of the form IMAGE_TEMPLATE, where the directory is the
        1000s place, and the filename is the starting-from-1 image in that
        directory.  e.g. '0001000/0001073.jpg' """

        idir = (i + 1) / NUM_IMAGES_IN_DIRECTORY
        number_image_name = IMAGE_TEMPLATE % (idir, i + 1)
        return number_image_name

    def make_postcard_image(self, i):
        """If the gallery is being displayed, the link should go to a
        single-card view. If a single card is being displayed, the
        link should go to the image."""

        image_name = self.image_name(i)
        img_src = IMAGE_HREF_LOCATION_TEMPLATE % image_name

        postcard_image = {
            'name': image_name,
            'img_src': img_src,
        }
        if self.num_images_display == 1: # one image
            postcard_image['href'] = img_src
        if self.num_images_display == 2: # single postcard --
                                         # two images (front and back)
            postcard_image['href'] = IMG_URL_TEMPLATE % i
        else: # gallery
            postcard_image['href'] = CARD_URL_TEMPLATE % i

        return postcard_image

    def load_postcards(self):
        """Aggregate every postcard for the contents of image_indices."""
        self.postcard_images = []
        for image_index in self.image_indices:
            postcard_image = self.make_postcard_image(image_index)
            self.postcard_images.append(postcard_image)

        # Do a pairwise swap of the postcards, so front of the card displays
        # first:
        #
        for i in range(1, len(self.postcard_images), 2):
            front = self.postcard_images[i]
            back = self.postcard_images[i-1]
            self.postcard_images[i] = back
            self.postcard_images[i-1] = front

    @property
    def permalink(self):
        """Generate a permanent link for gallery page."""
        return PERMALINK_TEMPLATE % self.permalink_suffix

    def jump_to_card(self):
        """Redirect to a random card view."""
        redirect(self.random_card_url)

    def jump_to_page(self, page_number):
        """
        Redirect to the correct page.
        Users will enter a page number, so translate that into an offset.
        """
        try:
            page_number = int(float(page_number))
            offset = self.newest_page_offset - (
                            self.num_images_display * page_number)
            if offset < 0:
                offset = 0
            if offset > self.max_good_display_offset:
                offset = self.max_good_display_offset
        except (ValueError, TypeError) as err:
            logging.info("Error doing redirect: %s", err)
            offset = 0

        url = PERMALINK_TEMPLATE % offset
        redirect(url)

    def get(self):
        """Handle a GET request for the page."""

        if IS_CACHING_ON and self.is_cached:
            with open(self.cached_name) as cachefile:
                page = cachefile.read()
        else:
            renderer = Renderer(view=self)
            page = renderer.render()
            if IS_CACHING_ON:
                self.write_page_to_cache(page)
        print "Content-type:text/html\n", page

    @property
    def is_cached(self):
        """Return if the current view page is cached or not."""
        return os.path.isfile(self.cached_name)

    @property
    def cached_name(self):
        """Return this view's caching name."""
        name = "%s/%s_%s.html" % (
                    CACHE_DIR, self.__class__.__name__, self.offset)
        return name

    def write_page_to_cache(self, page):
        """Write the page to cache, if it isn't already in the cache."""
        if not os.path.isfile(self.cached_name):
            with open(self.cached_name, 'w') as cachefile:
                cachefile.write(page)

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

class ViewJumpHandler(ViewGalleryHandler):
    """The view handler for jumping to a random gallery page or or card.  This
    is only used to distinguish it from possibly-cached pages."""

def main():
    """Page view entry point."""
    #cgitb.enable()

    try:
        # Parse request arguments:
        #
        args = cgi.FieldStorage()
        view_type = args['type'].value if 'type' in args else 'gallery'
        offset = args['offset'].value if 'offset' in args else None

        # If a jump or random card is requested, do that and exit:
        #
        if view_type == 'jump':
            view_handler = ViewJumpHandler(offset)
            pg_num = args['page_number'].value if 'page_number' in args else 1
            view_handler.jump_to_page(pg_num)
            return
        if view_type == 'randcard':
            view_handler = ViewJumpHandler(offset)
            view_handler.jump_to_card()
            return

        # Normal use: construct the appropriate handler and serve the page:
        #
        if view_type == 'card':
            view_handler = ViewCardHandler(offset)
        elif view_type == 'img':
            view_handler = ViewImageHandler(offset)
        else:
            view_handler = ViewGalleryHandler(offset)
        view_handler.get()
    except:
        print "Status: 500"
        #cgitb.handler()

if __name__ == "__main__":
    main()
