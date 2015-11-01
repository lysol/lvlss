from player import Player
from lobject import LObject
from area import Area
from event import Event
import shelve
import os
import logging
import saulscript
import saulscript.syntax_tree
from PIL import Image
from StringIO import StringIO

class ImageHandler(object):

    def __init__(self, world):
        self.world = world

    def save_image(self, img_id, img_content):
        self.world.save_file(img_id, img_content)

    def retrieve_image(self, img_id):
        return self.world.retrieve_file(img_id)

    def get_data(self, obj_id):
        image = self.retrieve_image(obj_id)
        inputted = StringIO(image)
        pimg = Image.open(inputted)
        data = [1 if x[0] == 255 else 0 for x in list(pimg.getdata())]
        logging.debug("Image Data: %s", repr(data))
        return data

    def set_pixel(self, obj_id, x, y, pix_on=True, dimensions=(32, 32)):
        logging.debug("Setting pixel for %s at (%d, %d)", obj_id, x, y)
        try:
            image = self.retrieve_image(obj_id)
            inputted = StringIO(image)
            pimg = Image.open(inputted)
        except KeyError:
            pimg = Image.new('RGB', dimensions)
        pimg.readonly = False
        pixelmap = pimg.load()
        output = StringIO()
        pixelmap[y, x] = (255, 255, 255) if pix_on else (0, 0, 0)
        logging.debug("Pixelmap: %s", repr(pixelmap[x, y]))
        pimg.save(output, format='PNG')
        self.save_image(obj_id, output.getvalue())

    def set_data(self, obj_id, data, dimensions=(32,32)):
        white = '\xff\xff\xff'
        black = '\x00\x00\x00'
        datastring = ''
        for pixel in data:
            datastring += white if pixel else black
        new_image = Image.frombytes('RGB', dimensions, datastring)
        output = StringIO()
        new_image.save(output, format='PNG')
        self.save_image(obj_id, output.getvalue())

    def init_content(self):
        self.world.datastore['content'] = dict()
        self.world.datastore.sync()
        self.set_data('default', [0 for x in range(32)] * 32)

