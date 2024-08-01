import glob
import math
import os
import tkinter
from tkinter import ttk
from typing import List

from PIL import Image, ImageTk, ImageOps

from primitive import Primitive, discover_primitives
from uicomponents import PrimitiveButton

PRIMITIVE_PATH = os.path.dirname(__file__) + '/assets/primitives'
PRIMITIVE_BUTTON_SIZE = 36
PRIMITIVE_BUTTON_SIZE_TUPLE = (PRIMITIVE_BUTTON_SIZE,) * 2


def rgbToHwb():
  pass


def polarToRect(r: float, theta: float):
  '''Helper function to convert polar coordinates to rectangular ones.

  `theta` is measured in degrees.
  '''
  rad = math.radians(theta)
  return r * math.cos(rad), r * math.sin(rad)


class MandalaGrid:
  '''Grid that is drawn on the canvas.'''

  def __init__(self, *, color: str = 'cyan', color_bold: str = 'blue', order: int = 3, radial_increment: float = 10, angular_divisions: int = 12):
    self._color = color
    self._color_bold = color_bold
    self._order = order
    self._radial_increment = radial_increment
    self._angular_divisions = angular_divisions
  
  def draw_on(self, canvas: tkinter.Canvas, width: int, height: int):
    size = min(width, height)

    center_x, center_y = width / 2, height / 2

    order = self._order
    major_angles = [-90 + x * 360 / order for x in range(order)]
    
    total_angles = order * self._angular_divisions
    minor_angles = [-90 + x * 360 / (total_angles) for x in range(total_angles)]

    radial_increment = self._radial_increment
    for r in range(radial_increment, size // 2, radial_increment):
      canvas.create_oval(center_x - r, center_y - r, center_x + r, center_y + r, width=2, outline=self._color)

    for angle in minor_angles:
      offset_x, offset_y = polarToRect(size / 2, angle)
      canvas.create_line(center_x, center_y, center_x + offset_x, center_y + offset_y, width=2, fill=self._color)

    for angle in major_angles:
      offset_x, offset_y = polarToRect(size / 2, angle)
      canvas.create_line(center_x, center_y, center_x + offset_x, center_y + offset_y, width=2, fill=self._color_bold)
  
  def get_info(self):
    return {
      'color': self._color,
      'order': self._order,
      'radial_increment': self._radial_increment,
      'angular_divisions': self._angular_divisions
    }

class MandalaLayer:
  '''Data structure to represent mandala layer.'''

  def __init__(self, *, primitive: Primitive, order: int, polar_radius: float = 0.5, polar_angle: float = 0, self_rotation: float = 0, size: float = 0.25, multiplicity: int = 1, color: str = 'black'):
    self._primitive = primitive
    self._order = order
    self._polar_radius = polar_radius
    self._polar_angle = polar_angle
    self._self_rotation = self_rotation
    self._size = size
    self._multiplicity = multiplicity
    self._color = color

    self._image_data: List[ImageTk.PhotoImage] = []
  
  def draw_on(self, canvas: tkinter.Canvas, width: int, height: int):
    self._image_data = []

    image = image=self._primitive.get_image()

    size = min(width, height)

    center_x, center_y = width / 2, height / 2

    num_copies: int
    if self._multiplicity == 0:
      num_copies = 1
    else:
      num_copies = self._multiplicity * self._order
    
    angles = [-90 + x * 360 / num_copies for x in range(num_copies)]
    for angle in angles:
      final_angle = 90 + angle + self._self_rotation

      image_w, image_h = image.size
      image_copy = image.copy().resize(size=(math.trunc(image_w * self._size), math.trunc(image_h * self._size))).rotate(-final_angle, expand=True)
      image_drawn = ImageTk.PhotoImage(image_copy)
      self._image_data.append(image_drawn)

      distance = self._polar_radius * size / 2
      x, y = polarToRect(distance, angle + self._polar_angle)
      canvas.create_image(center_x + x, center_y + y, image=image_drawn)


class AtlasFrame(ttk.Frame):
  def __init__(self, parent, *, columns: int = 1, primitives: List[Primitive] | None = None):
    super().__init__(parent)

    if primitives is None:
      primitives = []

    self._columns = columns
    self._next_position = 0

    self._canvas = tkinter.Canvas(self)
    self._scrollbar_v = ttk.Scrollbar(self, orient='vertical', command=self._canvas.yview)
    self._scrollbar_h = ttk.Scrollbar(self, orient='horizontal', command=self._canvas.xview)
    self._button_frame = ttk.Frame(self._canvas)

    tentative_width = self._columns * PRIMITIVE_BUTTON_SIZE
    self._canvas.configure(width=tentative_width, scrollregion=(0, 0, tentative_width, 0), yscrollcommand=self._scrollbar_v.set, xscrollcommand=self._scrollbar_h.set, relief='solid', border=1)

    self.rowconfigure(0, weight=1)
    self.columnconfigure(0, weight=1)

    self._canvas.grid(row=0, column=0, sticky='nswe')
    self._scrollbar_v.grid(row=0, column=1, sticky='ns')
    self._scrollbar_h.grid(row=1, column=0, sticky='we')
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


class LeftFrame(ttk.Frame):
  def __init__(self, parent):
    super().__init__(parent)

    self._builtin_atlas = ttk.Labelframe(self, text='Built-in Motifs')
    self._custom_atlas = ttk.Labelframe(self, text='Custom Motifs')

    primitives = discover_primitives(PRIMITIVE_PATH)
    self._builtin_atlas_frame = AtlasFrame(self._builtin_atlas, columns=4, primitives=primitives)
    self._builtin_atlas_frame.grid(row=0, column=0, sticky='nswe')

    self._custom_atlas_frame = AtlasFrame(self._custom_atlas, columns=4)
    self._custom_atlas_frame.grid(row=1, column=0, sticky='nswe')

    self._builtin_atlas.grid(row=0, column=0, sticky='nswe')
    self._custom_atlas.grid(row=1, column=0, sticky='nswe')

    self._builtin_atlas.rowconfigure(0, weight=1)
    self._builtin_atlas.columnconfigure(0, weight=1)

    self._custom_atlas.rowconfigure(0, weight=1)
    self._custom_atlas.columnconfigure(0, weight=1)

    self.rowconfigure(0, weight=1)
    self.rowconfigure(1, weight=1)
    self.columnconfigure(0, weight=1)


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


def test():
  root = tkinter.Tk()

  content_frame = ttk.Frame(root, relief='solid', border=5)
  content_frame.grid(row=0, column=0, sticky='nsew')

  left_frame = LeftFrame(content_frame)
  left_frame.grid(row=0, column=0, rowspan=2, sticky='nswe')

  mandala_canvas = MandalaCanvas(content_frame)
  mandala_canvas.grid(row=0, column=1, rowspan=2, sticky='nswe')

  dummy_frame_1 = ttk.Labelframe(content_frame, width=200, height=200, text='Used Motifs Go Here')
  dummy_frame_2 = ttk.Labelframe(content_frame, width=200, height=200, text='Parameters Go Here')

  dummy_frame_1.grid(row=0, column=2, sticky='nswe')
  dummy_frame_2.grid(row=1, column=2, sticky='nswe')
  
  content_frame.rowconfigure(0, weight=1)
  content_frame.rowconfigure(0, weight=1)
  content_frame.columnconfigure(0, weight=0)
  content_frame.columnconfigure(1, weight=1)
  content_frame.columnconfigure(2, weight=0)

  root.rowconfigure(0, weight=1)
  root.columnconfigure(0, weight=1)

  order = 8

  mandala_canvas.update_idletasks()
  grid = MandalaGrid(order=order)
  grid.draw_on(mandala_canvas._canvas, width=800, height=800)

  primitives = discover_primitives(PRIMITIVE_PATH)

  circle = primitives[0]
  eye = primitives[16]
  butterfly = primitives[79]

  mandala_layers = []

  mandala_layers.append(MandalaLayer(primitive=circle, order=order, polar_radius=0, polar_angle=0, self_rotation=0, size=0.25, multiplicity=0))
  mandala_layers[0].draw_on(mandala_canvas._canvas, width=800, height=800)

  mandala_layers.append(MandalaLayer(primitive=eye, order=order, polar_radius=0.1, polar_angle=0, self_rotation=0, size=0.2, multiplicity=1))
  mandala_layers[1].draw_on(mandala_canvas._canvas, width=800, height=800)

  mandala_layers.append(MandalaLayer(primitive=circle, order=order, polar_radius=0.2, polar_angle=0, self_rotation=0, size=0.2, multiplicity=2))
  mandala_layers[2].draw_on(mandala_canvas._canvas, width=800, height=800)

  mandala_layers.append(MandalaLayer(primitive=circle, order=order, polar_radius=0.25, polar_angle=0, self_rotation=0, size=0.2, multiplicity=2))
  mandala_layers[3].draw_on(mandala_canvas._canvas, width=800, height=800)

  mandala_layers.append(MandalaLayer(primitive=circle, order=order, polar_radius=0.3, polar_angle=0, self_rotation=0, size=0.2, multiplicity=2))
  mandala_layers[4].draw_on(mandala_canvas._canvas, width=800, height=800)

  mandala_layers.append(MandalaLayer(primitive=circle, order=order, polar_radius=0.35, polar_angle=0, self_rotation=0, size=0.2, multiplicity=1))
  mandala_layers[5].draw_on(mandala_canvas._canvas, width=800, height=800)

  mandala_layers.append(MandalaLayer(primitive=circle, order=order, polar_radius=1, polar_angle=0, self_rotation=0, size=0.5, multiplicity=2))
  mandala_layers[6].draw_on(mandala_canvas._canvas, width=800, height=800)

  mandala_layers.append(MandalaLayer(primitive=circle, order=order, polar_radius=0.9, polar_angle=0, self_rotation=0, size=0.5, multiplicity=2))
  mandala_layers[7].draw_on(mandala_canvas._canvas, width=800, height=800)

  mandala_layers.append(MandalaLayer(primitive=circle, order=order, polar_radius=0.8, polar_angle=0, self_rotation=0, size=0.5, multiplicity=2))
  mandala_layers[8].draw_on(mandala_canvas._canvas, width=800, height=800)

  mandala_layers.append(MandalaLayer(primitive=butterfly, order=order, polar_radius=0.4, polar_angle=11.5, self_rotation=45, size=0.05, multiplicity=2))
  mandala_layers[9].draw_on(mandala_canvas._canvas, width=800, height=800)

  mandala_layers.append(MandalaLayer(primitive=butterfly, order=order, polar_radius=0.45, polar_angle=16.5, self_rotation=45, size=0.05, multiplicity=2))
  mandala_layers[10].draw_on(mandala_canvas._canvas, width=800, height=800)

  mandala_layers.append(MandalaLayer(primitive=butterfly, order=order, polar_radius=0.5, polar_angle=21.5, self_rotation=45, size=0.05, multiplicity=2))
  mandala_layers[11].draw_on(mandala_canvas._canvas, width=800, height=800)

  mandala_layers.append(MandalaLayer(primitive=butterfly, order=order, polar_radius=0.6, polar_angle=-11.5, self_rotation=-45, size=0.05, multiplicity=2))
  mandala_layers[12].draw_on(mandala_canvas._canvas, width=800, height=800)

  mandala_layers.append(MandalaLayer(primitive=butterfly, order=order, polar_radius=0.65, polar_angle=-16.5, self_rotation=-45, size=0.05, multiplicity=2))
  mandala_layers[13].draw_on(mandala_canvas._canvas, width=800, height=800)

  mandala_layers.append(MandalaLayer(primitive=butterfly, order=order, polar_radius=0.7, polar_angle=-21.5, self_rotation=-45, size=0.05, multiplicity=2))
  mandala_layers[14].draw_on(mandala_canvas._canvas, width=800, height=800)

  root.mainloop()


def main():
  pass


if __name__ == '__main__':
  test()