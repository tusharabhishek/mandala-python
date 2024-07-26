import glob
import os
import tkinter
from tkinter import ttk
from typing import List

from PIL import Image, ImageTk, ImageOps

PRIMITIVE_PATH = '/home/tushar/work/mtp1/workspaces/mandala-python/src/assets/primitives'
PRIMITIVE_BUTTON_SIZE = (36, 36)

class Primitive:
  '''Data structure to represent a primitive in its most basic form.'''

  def __init__(self, image_path: str):
    '''Create a `primitive` object based on the image located at `image_path`.'''
    with Image.open(image_path) as image_file:
      # Copying image to a persistent variable because
      # access to the opened image file will be lost on exiting this block.
      self.image = image_file.copy()
    
    # Reference to image data (after processing)
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
    # Transparent pixels appear on Tk buttons only when using RGBA images.
    result_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
    mask_image = ImageOps.invert(image)
    result_image.paste(image, mask=mask_image)
    return result_image


class PrimitiveButton(ttk.Button):
  '''Button that adds a layer of its associated primitive to the canvas.'''
  
  def __init__(self, parent, *, primitive: Primitive, size: tuple[int, int], **keywords):
    '''Create a button of given `size` (width x height) based on the `primitive` supplied.'''
    super().__init__(parent, **keywords)

    image = primitive.get_image()
    image.thumbnail(size)
    # Reference to thumbnail shown on the button
    self.thumbnail = ImageTk.PhotoImage(image)
    
    thumbnail_size = (self.thumbnail.width(), self.thumbnail.height())
    # Padding needed to bring the button to size.
    # Otherwise, the button will only be as large as the thumbnail.
    padding = PrimitiveButton.get_padding(thumbnail_size, size)
    
    self.configure(image=self.thumbnail, padding=padding)
  
  def get_padding(thumbnail_size: tuple[int, int], bounds_size: tuple[int, int]):
    '''Return a tuple of padding needed to bring `thumbnail_size` to `bounds_size`.'''
    x_diff, y_diff = bounds_size[0] - thumbnail_size[0], bounds_size[1] - thumbnail_size[1]
    half_x, half_y = x_diff // 2, y_diff // 2

    return (half_x, half_y, x_diff - half_x, y_diff - half_y)


class AtlasFrame(ttk.LabelFrame):
  def __init__(self, parent, *, title: str, columns: int, button_size: tuple[int, int], primitives: List[Primitive], **keywords):
    super().__init__(parent, **keywords)

    self.columns = columns
    self.button_size = button_size

    # Reference to primitive buttons added so far.
    self.primitive_buttons: List[PrimitiveButton] = []

    # Grid position to add the next PrimitiveButton at.
    # A single value since the actual position
    # will vary depending on the number of columns.
    self.next_position: int = 0

    for primitive in primitives:
      self.add_primitive_button(primitive)
    
    self.configure(text=title)
  
  def add_primitive_button(self, primitive: Primitive):
    row, column = self.next_position // self.columns, self.next_position % self.columns
    
    button = PrimitiveButton(self, primitive=primitive, size=self.button_size)
    button.grid(row=row, column=column)
    self.primitive_buttons.append(button)

    self.next_position += 1


def discover_primitives(dirpath):
  primitive_paths = [f'{dirpath}/{path}' for path in glob.glob('*.png', root_dir=dirpath)]
  primitive_paths.sort()
  return primitive_paths


def test():
  root = tkinter.Tk()

  content_frame = ttk.Frame(root)
  content_frame.grid()
  
  primitives = [Primitive(path) for path in discover_primitives(PRIMITIVE_PATH)]

  atlas_frame = AtlasFrame(content_frame, title='Built-in Primitives', columns=8, button_size=PRIMITIVE_BUTTON_SIZE, primitives=primitives)
  atlas_frame.grid()

  root.mainloop()


def main():
  pass


if __name__ == '__main__':
  test()