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

    def save_image_2x(self, img_id):
        x2 = img_id + '_2x'
        image = self.retrieve_image(img_id)
        inputted = StringIO(image)
        pimg = Image.open(inputted)
        newimg = pimg.resize([x * 2 for x in pimg.size], Image.NEAREST)
        output = StringIO()
        newimg.save(output, format='PNG')
        self.world.save_file(x2, output.getvalue())

    def retrieve_image(self, img_id):
        return self.world.retrieve_file(img_id)

    def retrieve_image_2x(self, img_id):
        x2 = img_id + '_2x'
        if not self.world.file_exists(x2):
            self.save_image_2x(img_id)
        logging.debug("Sending %s", x2)
        return self.world.retrieve_file(x2)

    def copy_image(self, old_id, new_id):
        if not self.world.file_exists(old_id):
            old_id = 'default'
        old_id_2x = old_id + '_2x'
        new_id_2x = new_id + '_2x'
        self.world.copy_file(old_id, new_id)
        self.world.copy_file(old_id_2x, new_id_2x)

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
        self.set_data('default_2x', [0 for x in range(64)] * 64, (64, 64))

