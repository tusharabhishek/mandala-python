'''Module to manage and display primitives'''

import glob

from PIL import Image, ImageOps

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
    '''Extract primitive from `image`.
    
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

def discover_primitives(dirpath: str):
  '''Construct a list of primitives from .png images located at `dirpath`'''
  primitive_paths = [f'{dirpath}/{path}' for path in glob.glob('*.png', root_dir=dirpath)]
  primitive_paths.sort()
  primitives = [Primitive(path) for path in primitive_paths]
  return primitives