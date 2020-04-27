from imutils import perspective
from imutils import contours
import imutils
import argparse
import numpy as np
import cv2
import sys
import math
import csv

# Parse arguments.
def get_cmd():
  parser = argparse.ArgumentParser()
  parser.add_argument('--image', help='Path to image.', required=True) 
  parser.add_argument('--show_images', help='Show images from each steps.', default=False) 
  parser.add_argument('--show_final', help='Show final image.', default=True) 
  parser.add_argument('--show_each_objects', help='Show each object after drawing boxes.', default=False) 
  parser.add_argument('--print_boxes', help='Print Boxes.', default=False) 
  parser.add_argument('--out_file', help='Output files.', type=str)
  return parser.parse_args()

# Define a Point class.
class Point(object):
  def __init__(self, name, x, y):
    self.name = name
    self._x = x
    self._y = y
  # Get distance between this point and point p.
  def distance(self, p):
    return math.sqrt(math.pow((self._x - p._x), 2) + math.pow((self._y - p._y), 2))
  # Get MidPoint between this point and point p.
  def mid_point(self, p):
    return Point('mid_point', (self._x + p._x) * .5, (self._y + p._y) * .5)
  # Return string representation of this box. 
  def to_string(self):
    return str(self.name) + ':x:' + '{:.2f}'.format(self._x) + ':y:' + '{:.2f}'.format(self._y)
  # Return string with just coordonates.
  def coordinate_to_string(self):
    return '(' + '{:.2f}'.format(self._x) + '/' + '{:.2f}'.format(self._y) + ')'

# To show image after each steps
def show_image(text, img):
  cv2.imshow(text, img)
  cv2.waitKey(0)

# Print all the points.
def print_box(top_left, top_right, bottom_left, bottom_right):
  print(top_left.to_string())
  print(top_right.to_string())
  print(bottom_left.to_string())
  print(bottom_right.to_string())
 
def main():
  args = get_cmd()
  
  # Write CSV Fields.
  outfile = args.image.split('.')[0] + '.csv'
  if args.out_file is not None: outfile = args.out_file
  header = ['ID', 'aspect_ratio', 'width', 'height', 'top_left', 'top_right', 'bottom_left', 'bottom_right']
  with open(outfile, 'w+') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)
    csvfile.close()
 
  # Reads image.
  image = cv2.imread(args.image)
  if args.show_images: show_image('Original Image', image)

  # Gray out image and adds some blurr.
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray, (7, 7), 0)
  if args.show_images: show_image('Gray Image', gray)

  # Perform edge detection, then perform a dilation + erosion close gaps between edges.
  edged = cv2.Canny(gray, 50, 100)
  edged = cv2.dilate(edged, None, iterations=1)
  edged = cv2.erode(edged, None, iterations=1)
  if args.show_images: show_image('Image Edges', edged)
 
  # Find contours in the edge map, then sort it from left to right.
  cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  cnts = imutils.grab_contours(cnts)
  cnts, _ = contours.sort_contours(cnts)
  
  for i in range(len(cnts)):
    contour = cnts[i]
    fields = []
    print('Object:', i)
    fields.append(str(i))

    # Compute the boxes surrounding the contours.
    box = cv2.minAreaRect(contour)
    box = cv2.boxPoints(box)
    box = np.array(box, dtype="int")
    # Reorder the boxes.
    box = perspective.order_points(box)
    cv2.drawContours(image, [box.astype("int")], -1, (0, 255,0), 2)
    for (x, y) in box: cv2.circle(image, (int(x), int(y)), 5, (0, 0, 255), -1)
    
    # Parse box, we only need topleft, topright, and bottomleft.
    (tl, tr, br, bl) = box
    top_left = Point('top_left', tl[0], tl[1])
    top_right = Point('top_right', tr[0], tr[1])
    bottom_left = Point('bottom_left', bl[0], bl[1])
    bottom_right = Point('bottom_right', br[0], br[1])
    # Get width of this object.
    width = top_left.distance(top_right)
    # Get height of this object.
    height = top_left.distance(bottom_left)
    aspect_ratio = '({:.2f}'.format(width) + '/' + '{:.2f}'.format(height) + ')'
    print('Aspect ratio:', aspect_ratio)
    fields.append(aspect_ratio)
    if args.print_boxes: print_box(top_left, top_right, bottom_left, bottom_right)
    fields.append('{:.2f}'.format(width))
    fields.append('{:.2f}'.format(height))
    tltr = top_left.mid_point(top_right)
    cv2.putText(image, '{:.2f}'.format(width),
      (int(tltr._x - 15), int(tltr._y - 10)), cv2.FONT_HERSHEY_SIMPLEX,0.65, (255, 255, 255), 2)
    trbr = top_right.mid_point(bottom_right)
    cv2.putText(image, '{:.2f}'.format(height),
      (int(trbr._x + 10), int(trbr._y)), cv2.FONT_HERSHEY_SIMPLEX,0.65, (255, 255, 255), 2)
    fields.append(top_left.coordinate_to_string())
    fields.append(top_right.coordinate_to_string())
    fields.append(bottom_left.coordinate_to_string())
    fields.append(bottom_left.coordinate_to_string())
    if args.show_each_objects: show_image('Adding Sizes', image)
    # Writing this object to the output file.
    with open(outfile, 'a') as csvfile:
      writer = csv.writer(csvfile, quoting=csv.QUOTE_NONE)
      writer.writerow(fields)
      csvfile.close()
   
  if args.show_final: show_image('With Sizes', image)
  print('Results written to:', outfile) 

if __name__ == '__main__':
  main()
