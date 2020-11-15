#!/usr/bin/python
#http://www.astro.ufl.edu/~warner/prog/python.html  - Python Basics if you want to learn some Python
#https://pypi.python.org/pypi/svgwrite/  - Library this script uses
#install Python27, download svgwrite, from svgwrite folder run "C:\Python27\python setup.py install"

# This script starts by asking for a file, this name is saved as 'csv_filename'
# Input file is a 'csv_filename'.csv and is referred to as file
# Be careful what characters you use.  This is a comma deliminated file, so using a comma in your text will cause problems.  
# Also, some applications will change characters to non-standard characters you will get an error (" - " is often to a larger dash that is non standard)
# Output file is a 'csv_filename'.svg and is defined before the while loop
# The script is setup for 13 fields, to add more change the global fields variable and add another section to the writeField function with the colors you want.
# If the following words are in field 1 of a line it will change the structure of the output blocks to fit that heading "Left, Right, Top, Text, Extras"
# Text will not make a box, but make a new row of text for each field, each line will be a different section of text, this section must be after blocks
# Extras will look for a file in the folder /Images called value.png and add it to the svg, useful for things like ISP headers graphic, etc. (I'm not actually using this)
# File is read until field 1 is "EOF"

import os
import svgwrite
from sys import argv, exit

################################################## GLOBAL VARIABLES ########################################

class GDSConfig(object):
    def __init__(
         self,
         height=12,
         width=45,
         rowheight=15,
         rowwidth=48,
         documentWidth = None,
         documentHeight = None,
         textheight=17,
         fontsize=12,
         imagewidth=250,
         imageheight=250,
         indent = 1,
         adjust = -2,
         tcolor = ['white', 'red',   'black', 'yellow', 'green', 'blue',  'purple',
                 'yellow', 'grey', 'purple', 'orange', 'blue', 'blue', ],
         topacity = [ 0.3,     0.8,     0.9,     0.7,      0.3,     0.4,     0.4,
             0.3,      0.3,    0.2,      0.5,      0.1,    0.1,   ],
         overwrite = False,
         pretty = True,
    ):
        self.height = height #height of a box
        self.width = width #width of a box
        self.rowheight = rowheight #height of a row (leaving enough space between rows to move)
        self.rowwidth = rowwidth #width of a 'spot', basically width plus a few
        self.documentWidth = self.rowwidth*13 +50 #maximum width the document should be
        self.documentHeight = 2250 #this is  guess since we need to make the document before we know the file size, doesn't really matter anyway
        self.textheight = textheight #how much we add each time we add a line of text
        self.fontsize = fontsize
        self.imagewidth = imagewidth
        self.imageheight = imageheight
        self.indent = indent      # move text to the right
        self.adjust = adjust      # move text down (negative for up)
        self.tcolor = tcolor
        self.topacity = topacity
        self.overwrite = overwrite # overwrite svg files in directory (Default: False)
        self.pretty = pretty # indent svg file (thereby increasing file size) (Default: True)
# "Theme"
#            Name     Power    GND      Control   Arduino  Port     Analog
#        PWM       Serial  ExtInt    PCInt     Misc    Misc2
# tcolor = ['white', 'red',   'black', 'yellow', 'green', 'blue',  'purple',
#       'yellow', 'grey', 'purple', 'orange', 'blue', 'blue', ],

################################################# FUNCTIONS ###################################################

#Writes plain text from the text section
def writeText(dwg, value, ystart, cfg=GDSConfig()):
  text = dwg.add(dwg.text(str(value), insert=(0,ystart),font_size=12, font_family='Montserrat', fill='black'))
  # print("Printing " + str(value) + " at " + ystart)
  return cfg.textheight
  #end writeText

# Creates colored blocks and text for fields
def writeField(dwg, type, value, x, y, cfg=GDSConfig()):

    color = cfg.tcolor[type]  # fill color of box
    crect = color         # color for rectangle around box
    ctext = 'black'       # default text color: black

    if color == 'white':  # white boxes get black outlines
        crect = 'black'

    if color == 'black':  # don't write black-on-black
        ctext = 'white'

    # Box
    dwg.add(dwg.rect(
        (x, y), (cfg.width, cfg.height), 1, 1,
        stroke = crect, opacity = cfg.topacity[type], fill = color
        ))

    # Text
    dwg.add(dwg.text(
        str(value), insert = (x + cfg.indent, y + cfg.height + cfg.adjust),
        font_size = cfg.fontsize, font_family='Montserrat', fill = ctext
        ))

    return cfg.rowheight


#adds images to end of document, currently not used as pngs don't work as well as I'd like and it is easier to just drag and drop the files I want into the final file.
def writeImages(dwg, i, value, ystart, cfg=GDSConfig()):
  currentimage = "Images/" + value + ".png"
  if os.access(currentimage, os.R_OK):
    print("Adding " + currentimage)
    image = dwg.add(dwg.image(href=("../" +  currentimage), insert=(i*cfg.imagewidth, ystart)))
    return i*cfg.imagewidth

  else:
    print("Could not find " + currentimage)  
    return 0
#end writeImages


def read_csv(infile):
  #open file with read access
  if infile is None:
    print("Make sure the python script is in the same folder as the file.")
    filename_root = input("Enter file name without the .csv extension (eg. ESP8266/Thing): ")
    csv_filename = filename_root + '.csv'
  else:
    filename_root = infile[0:-4]
    csv_filename = infile

  if os.access(csv_filename, os.R_OK):
    with open(csv_filename, "r") as f:
      print("File opened")
      lines = f.readlines()
      return filename_root, lines
  else:
    print("File not found, please try again, there should be a comma deliminated csv file with the data in it.  See script for more details")
    exit(0)


def write_svg(dwg, name_root, cfg=GDSConfig()):
  new_name = name_root
  if not cfg.overwrite:
    i = 2
    while os.access(new_name + '.svg', os.F_OK):
        new_name = '{0}_{1:02d}'.format(name_root, i)
        i += 1

  print("End of File, the output is located at " + new_name + ".svg")
  dwg.saveas(new_name + '.svg', pretty=cfg.pretty)


def createGDS(cfg=GDSConfig()):
  infile = None
  outfile_root = None
  if len(argv) in [2, 3] and argv[1].lower().endswith('.csv'):
    infile = argv[1]

  if len(argv) == 3 and argv[2].lower().endswith('.svg'):
    outfile_root = argv[2][0:-4]

  filename_root, lines = read_csv(infile)
  dwg = svgwrite.Drawing(filename=str(filename_root+".svg"),
                         profile='tiny', 
                         size=(cfg.documentWidth,cfg.documentHeight))
  cursor = 15
  direction = 'r'

  #read in each line parse, and send each field to writeField  
  records = [line.split(',') for line in lines]
  for record in records:
    # add space to maintain compatibility with previous version
    if direction == 'text':
      cursor += cfg.rowheight

    if (record[0] == "Left"):
      direction = "l"
      record[0] = ""
    if (record[0] == "Right"):
      direction = "r"
      record[0] = ""
    if (record[0] == "Top"):
      direction = "r"
      record[0] = ""
    if (record[0] == "Text"):
      record[0] = ""
      direction = "text"
    if(record[0] == "Extras"):
      record[0]=""
      direction = "extras"
    if (record[0] == "EOF"): #if we are done
      break

    y_add = 0
    label_index = 0
    for i in range(0, len(record)): #go through total number of fields
        if(record[i]!="" and direction=='r'):
          y_add = writeField(dwg, i,record[i], label_index*cfg.rowwidth, cursor, cfg)#call function to add that field to the svg file
          label_index += 1
                  
        if(record[i]!="" and direction=='l'):
          xstart = cfg.documentWidth - cfg.rowwidth - label_index*cfg.rowwidth
          y_add = writeField(dwg, i,record[i], xstart, cursor, cfg)#call function to add that field to the svg file
          label_index += 1
                  
        if (record[i]!="" and direction == "text"):
           cursor += writeText(dwg, record[i], cursor, cfg)
                        
        if (record[i]!="" and direction == "extras"):
            y_add = writeImages(dwg, i, record[i], cursor, cfg)
    cursor += y_add

  #end of while

  svg_root = outfile_root if outfile_root is not None else filename_root
  write_svg(dwg, svg_root, cfg)


if __name__ == '__main__':
  createGDS()

