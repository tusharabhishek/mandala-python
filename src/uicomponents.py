'''Module containing various UI components'''

from tkinter import ttk

from PIL import ImageTk

from primitive import Primitive

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