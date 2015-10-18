from command import Command, is_command, CommandException
from event import Event
import PIL
from StringIO import StringIO

class ImageEditing(Command):

    @is_command
    def get_image(self, player, *args):
        if len(args) == 0:
            raise CommandException(CommandException.NOT_ENOUGH_ARGUMENTS)
        obj_id = args[0]
        if self.world.is_area(obj_id):
            dims = (64, 32)
        else:
            dims = (32, 32)

        data = self.world.image_handler.get_data(obj_id)
        return Event('image-content', {"pixels": data, "dimensions": dims})

    @is_command
    def save_pixel(self, player, *args):
        if len(args) < 4:
            raise CommandException(CommandException.NOT_ENOUGH_ARGUMENTS)        
        obj_id = args[0]
        coords = (args[1], args[2])
        pix_on = bool(args[3])
        if self.world.is_area(obj_id):
            dims = (64, 32)
        else:
            dims = (32, 32)        
        self.world.image_handler.set_pixel(obj_id, coords[0], coords[1], pix_on, dimensions=dims)
        return Event('pixel-set', {'x': coords[0], 'y': coords[1], 'pixel': int(pix_on)})
