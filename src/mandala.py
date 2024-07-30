import glob
import os
import tkinter
from tkinter import ttk
from typing import List

from PIL import Image, ImageTk, ImageOps

PRIMITIVE_PATH = '/home/tushar/work/mtp1/workspaces/mandala-python/src/assets/primitives'
PRIMITIVE_BUTTON_SIZE = 36
PRIMITIVE_BUTTON_SIZE_TUPLE = (PRIMITIVE_BUTTON_SIZE,) * 2

class Primitive:
  '''Data structure to represent a primitive in its most basic form.'''

  def __init__(self, image_path: str):
    '''Create a `primitive` object based on the image located at `image_path`.
    '''
    with Image.open(image_path) as image_file:
      # Copying image (and not just reference) to a persistent variable because
      # access to the opened image file will be lost on exiting this block.
      self.image = image_file.copy()
    
    # Extract primitive and store it (with transparent background)
    self.image = Primitive.extract_primitive(self.image)
  
  def get_image(self):
    '''Return a copy of the `Image` object associated with this primitive.'''
    return self.image.copy()
  
  def show_image(self):
    '''**[DEBUG]** Show the `Image` associated with this primitive in an image
    viewer.
    '''
    self.image.show()
  
  def extract_primitive(image: Image.Image):
    '''Extract primitive from the image.
    
    Currently, the primitive is assumed to be made up of black pixels,
    with white pixels assumed to be the background.
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
  
  def __init__(self, parent, *, primitive: Primitive, size: tuple[int, int]):
    '''Create a button of given `size` (width x height) based on the
    `primitive` supplied.
    '''
    super().__init__(parent)

    image = primitive.get_image()
    image.thumbnail(size)
    # Reference to thumbnail shown on the button
    self.thumbnail = ImageTk.PhotoImage(image)
    
    thumbnail_size = (self.thumbnail.width(), self.thumbnail.height())
    # Padding needed to bring the button to `size`.
    # Otherwise, the button will only be as large as the thumbnail.
    padding = PrimitiveButton.get_padding(thumbnail_size, size)
    
    self.configure(image=self.thumbnail, padding=padding)
  
  def get_padding(thumbnail_size: tuple[int, int],
                  bounds_size: tuple[int, int]):
    '''Return a tuple of padding that needs to be added to bring
    `thumbnail_size` to `bounds_size`.
    '''
    x_diff = bounds_size[0] - thumbnail_size[0]
    y_diff = bounds_size[1] - thumbnail_size[1]
    half_x, half_y = x_diff // 2, y_diff // 2

    # In order, left, top, right, bottom
    return (half_x, half_y, x_diff - half_x, y_diff - half_y)


class AtlasFrame(ttk.Frame):
  def __init__(self, parent, *, columns: int = 1, primitives: List[Primitive]):
    super().__init__(parent)

    self._columns = columns
    self._next_position = 0

    self._canvas = tkinter.Canvas(self)
    self._scrollbar = ttk.Scrollbar(self, orient='vertical', command=self._canvas.yview)
    self._button_frame = ttk.Frame(self._canvas)

    self._canvas.configure(width=self._columns * PRIMITIVE_BUTTON_SIZE, yscrollcommand=self._scrollbar.set)

    self.rowconfigure(0, weight=1)
    self.columnconfigure(0, weight=1)

    self._canvas.grid(row=0, column=0, sticky='nswe')
    self._scrollbar.grid(row=0, column=1, sticky='ns')
    self._canvas.create_window(0, 0, anchor='nw', window=self._button_frame)

    for primitive in primitives:
      self.add_primitive_button(primitive)
  
  def add_primitive_button(self, primitive: Primitive):
    row, col = self._next_position // self._columns, self._next_position % self._columns
    button = PrimitiveButton(self._button_frame, primitive=primitive, size=PRIMITIVE_BUTTON_SIZE_TUPLE)
    button.grid(row=row, column=col)

    self.update_idletasks()
    w, h = self._button_frame.winfo_width(), self._button_frame.winfo_height()
    self._canvas.configure(width=w, scrollregion=(0, 0, w, h))

    self._next_position += 1


class MandalaCanvas(ttk.Frame):
  def __init__(self,
               parent,
               *,
               size: tuple[int, int] = (800, 800),
               background: str = 'white'):
    super().__init__(parent)

    self.canvas_size = size

    self._canvas = tkinter.Canvas(self, background=background)
    self._scrollbar_h = ttk.Scrollbar(self,
                                      orient='horizontal',
                                      command=self._canvas.xview)
    self._scrollbar_v = ttk.Scrollbar(self,
                                      orient='vertical',
                                      command=self._canvas.yview)
    
    w, h = self.canvas_size
    self._canvas.configure(scrollregion=(0, 0, w, h),
                           xscrollcommand=self._scrollbar_h.set,
                           yscrollcommand=self._scrollbar_v.set)
    
    self.rowconfigure(0, weight=1)
    self.columnconfigure(0, weight=1)
    
    self._canvas.grid(row=0, column=0, sticky='nsew')
    self._scrollbar_h.grid(row=1, column=0, sticky='ew')
    self._scrollbar_v.grid(row=0, column=1, sticky='ns')


class AtlasFrame2(ttk.LabelFrame):
  '''Frame that holds a grid containing a number of `PrimitiveButton`s.'''
  def __init__(self,
               parent,
               *,
               title: str,
               columns: int,
               button_size: tuple[int, int],
               primitives: List[Primitive] | None = None):
    super().__init__(parent)

    self.columns = columns
    self.button_size = button_size

    # Reference to primitive buttons added so far.
    self.primitive_buttons: List[PrimitiveButton] = []

    # Grid position to add the next PrimitiveButton at.
    # A single value since the actual position
    # will vary depending on the number of columns.
    self.next_position: int = 0

    if primitives is None:
      primitives = []
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
  primitives = [Primitive(path) for path in primitive_paths]
  return primitives


def test():
  root = tkinter.Tk()

  content_frame = ttk.Frame(root)
  content_frame.grid(sticky='nsew')

  content_frame.rowconfigure(0, weight=1)
  content_frame.columnconfigure(0, weight=1)

  primitives = discover_primitives(PRIMITIVE_PATH)

  atlas_frame = AtlasFrame(content_frame, columns=8, primitives=primitives)
  atlas_frame.grid(sticky='nswe')
  
  root.rowconfigure(0, weight=1)
  root.columnconfigure(0, weight=1)
  root.mainloop()


def main():
  pass


if __name__ == '__main__':
  test()