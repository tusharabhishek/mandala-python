import tkinter
from tkinter import ttk
from typing import List

from PIL import Image, ImageTk, ImageOps

class Primitive:
  '''Data structure to represent a primitive in its most basic form.'''

  def __init__(self, image_path: str):
    '''Create a `primitive` object based on the image located at `image_path`.'''
    with Image.open(image_path) as image_file:
      # Copying image to a persistent variable because
      # access to the opened image file will be lost on exiting this block.
      self.image = image_file.copy()
    self.image = Primitive.process_image(self.image)
  
  def get_image(self):
    '''Return a copy of the `Image` object associated with this primitive.'''
    return self.image.copy()
  
  def show_image(self):
    '''**[DEBUG]** Show the `Image` associated with this primitive in an image viewer.'''
    self.image.show()
  
  def process_image(image: Image.Image):
    '''Process the image and return the result for further usage.
    
    Currently, this function renders white pixels transparent.
    '''
    # Mask the image with its inverted copy to add transparency
    # - whiter pixels are more transparent.
    # Transparent pixels only show up on RGBA images.
    result_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
    mask_image = ImageOps.invert(image)
    result_image.paste(image, mask=mask_image)
    return result_image


class PrimitiveButton(ttk.Button):
  def __init__(self, parent, primitive: Primitive, size: tuple[float, float], **keywords):
    super().__init__(parent, **keywords)

    image = primitive.get_image()
    image.thumbnail(size)
    self.thumbnail = ImageTk.PhotoImage(image)
    
    self['image'] = self.thumbnail
  

def test():
  root = tkinter.Tk()

  content_frame = ttk.Frame(root)
  content_frame.grid()
  
  p = Primitive('/home/tushar/work/mtp1/workspaces/mandala-python/src/assets/primitives/primitives-1-100dpi-002.png')
  button = PrimitiveButton(content_frame, p, (50, 50))
  button.grid()

  root.mainloop()


def main():
  pass


if __name__ == '__main__':
  test()