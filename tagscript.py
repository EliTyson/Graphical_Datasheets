#!/usr/bin/python
#http://www.astro.ufl.edu/~warner/prog/python.html  - Python Basics if you want to learn some Python
#https://pypi.python.org/pypi/svgwrite/  - Library this script uses
#install Python27, download svgwrite, from svgwrite folder run "C:\Python27\python setup.py install"

# This script starts by asking for a file, this name is saved as 'myfile'
# Input file is a 'myfile'.csv and is referred to as file
# Be careful what characters you use.  This is a comma deliminated file, so using a comma in your text will cause problems.  
# Also, some applications will change characters to non-standard characters you will get an error (" - " is often to a larger dash that is non standard)
# Output file is a 'myfile'.svg and is defined before the while loop
# The script is setup for 13 fields, to add more change the global fields variable and add another section to the writeField function with the colors you want.
# If the following words are in field 1 of a line it will change the structure of the output blocks to fit that heading "Left, Right, Top, Text, Extras"
# Text will not make a box, but make a new row of text for each field, each line will be a different section of text, this section must be after blocks
# Extras will look for a file in the folder /Images called value.png and add it to the svg, useful for things like ISP headers graphic, etc. (I'm not actually using this)
# File is read until field 1 is "EOF"

import os
import svgwrite
import time

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


def createGDS(cfg=GDSConfig()):
  cursor = 15
  direction = 'r'

  #open file with read access
  print("Make sure the python script is in the same folder as the file.")
  myfile = input("Enter file name without the .csv extension (eg. ESP8266/Thing): ")
  if os.access(myfile +".csv", os.R_OK):
    file = open(myfile +".csv","r")
    print("File opened")
  else:
    print("File not found, please try again, there should be a comma deliminated csv file with the data in it.  See script for more details")
    time.sleep(1)
    os._exit(0)

  #read in each line parse, and send each field to writeField  
  rawline="not empty"
  dwg = svgwrite.Drawing(filename=str(myfile+".svg"), profile='tiny', size=(cfg.documentWidth,cfg.documentHeight))
  while (rawline!=""):
    # add space to maintain compatibility with previous version
    if direction == 'text':
      cursor += cfg.rowheight

    rawline  = file.readline()
    line = rawline.split(",") #Split into fields separated by ","
    if (line[0] == "Left"):
      direction = "l"
      line[0] = ""
    if (line[0] == "Right"):
      direction = "r"
      offset = 0
      line[0] = ""
    if (line[0] == "Top"):
      direction = "r"
      offset = 0
      line[0] = ""
    if (line[0] == "Text"):
      offset = 0
      line[0] = ""
      direction = "text"
    if(line[0] == "Extras"):
      offset=0
      line[0]=""
      direction = "extras"
    if (line[0] == "EOF"): #if we are done
      dwg.save()
      break

    y_add = 0
    label_index = 0
    for i in range(0, len(line)): #go through total number of fields
        if(line[i]!="" and direction=='r'):
          y_add = writeField(dwg, i,line[i], label_index*cfg.rowwidth, cursor, cfg)#call function to add that field to the svg file
          label_index += 1
                  
        if(line[i]!="" and direction=='l'):
          xstart = cfg.documentWidth - cfg.rowwidth - label_index*cfg.rowwidth
          y_add = writeField(dwg, i,line[i], xstart, cursor, cfg)#call function to add that field to the svg file
          label_index += 1
                  
        if (line[i]!="" and direction == "text"):
           cursor += writeText(dwg, line[i], cursor, cfg)
                        
        if (line[i]!="" and direction == "extras"):
            y_add = writeImages(dwg, i, line[i], cursor, cfg)
    cursor += y_add

  #end of while


  print("End of File, the output is located at " + myfile + ".svg")
  dwg.save()
  file.close()


if __name__ == '__main__':
  createGDS()

