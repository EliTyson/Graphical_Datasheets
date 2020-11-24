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
         documentWidth=None,
         documentHeight=None,
         textheight=17,
         link_stylesheet=False,
         font='Varta',
         google_font=None,
         fontsize=12,
         imagewidth=250,
         imageheight=250,
         indent=1,
         adjust=-2,
         tagtxt_color='#000000',
         tag_colors=None,
         overwrite=False,
         pretty=True,
    ):
        self.height = height #height of a box
        self.width = width #width of a box
        self.rowheight = rowheight #height of a row (leaving enough space between rows to move)
        self.rowwidth = rowwidth #width of a 'spot', basically width plus a few
        self.documentWidth = self.rowwidth*13 +50 #maximum width the document should be
        self.documentHeight = 2250 #this is  guess since we need to make the document before we know the file size, doesn't really matter anyway
        self.textheight = textheight #how much we add each time we add a line of text
        self.link_stylesheet = link_stylesheet
        self.font = font
        self.google_font = google_font
        self._google_fonts = {
                              'Montserrat',
                              'IBM Plex Sans',
                              'Big Shoulders Display',
                              'Varta',
                              'Roboto Condensed',
                              'Inconsolata',
                             }
        self.fontsize = fontsize
        self.imagewidth = imagewidth
        self.imageheight = imageheight
        self.indent = indent      # move text to the right
        self.adjust = adjust      # move text down (negative for up)
        self.tagtxt_color = tagtxt_color
        self.tag_colors = self.get_colors(tag_colors)
        self.overwrite = overwrite # overwrite svg files in directory (Default: False)
        self.pretty = pretty # indent svg file (thereby increasing file size) (Default: True)

    def get_colors(self, tag_colors):
        default_colors = [
            ['#ffffff', '#b3b3b3', self.tagtxt_color],
            ['#ff3333', '#ff3333', self.tagtxt_color],
            ['#191919', '#191919', '#ffffff'],
            ['#ffff4d', '#ffff4d', self.tagtxt_color],
            ['#b3d9b3', '#b3d9b3', self.tagtxt_color],
            ['#9999ff', '#9999ff', self.tagtxt_color],
            ['#cc99cc', '#cc99cc', self.tagtxt_color],
            ['#ffffb3', '#ffffb3', self.tagtxt_color],
            ['#d9d9d9', '#d9d9d9', self.tagtxt_color],
            ['#e6cce6', '#e6cce6', self.tagtxt_color],
            ['#ffd280', '#ffd280', self.tagtxt_color],
            ['#e6e6ff', '#e6e6ff', self.tagtxt_color],
        ]

        if tag_colors is None and not isinstance(tag_colors, (list, tuple)):
            return default_colors

        if isinstance(tag_colors, tuple):
            tag_colors = [*tag_colors]

        for i in range(len(tag_colors)):
            if isinstance(tag_colors[i], str):
                tag_colors[i] = [tag_colors[i],
                                 tag_colors[i],
                                 self.tagtxt_color]
            elif isinstance(tag_colors[i], (list, tuple)):
                if len(tag_colors[i]) == 3:
                    tag_colors[i] = list(tag_colors[i])
                elif len(tag_colors[i]) == 2:
                    tag_colors[i] = [tag_colors[i][0],
                                     tag_colors[i][1],
                                     self.tagtxt_color]
                elif len(tag_colors[i]) == 1:
                    tag_colors[i] = [tag_colors[i][0],
                                     tag_colors[i][0],
                                     self.tagtxt_color]
                else:
                    tag_colors[i] = None
            else:
                tag_colors[i] = None

        if len(tag_colors) > len(default_colors):
            default_colors = [*default_colors + [default_colors[-1]] * (
                                len(tag_colors) - len(default_colors))]

        new_colors = list(default_colors)
        for i in range(len(tag_colors)):
            if tag_colors[i] is not None:
                new_colors[i] = tag_colors[i]

        return new_colors

################################################# FUNCTIONS ###################################################

#Writes plain text from the text section
def writeText(dwg, value, i, ystart, cfg=GDSConfig()):
  text = dwg.add(dwg.text(str(value), 
                          insert=(0,ystart),
                          font_size=12,
                          font_family=cfg.font,
                          fill='black',
                          class_='text_line{:d} text'.format(i),
                         ))
  # print("Printing " + str(value) + " at " + ystart)
  return cfg.textheight
  #end writeText

# Creates colored blocks and text for fields
def writeField(dwg, i, value, x, y, cfg=GDSConfig()):

    color = cfg.tag_colors[i][0]  # fill color of box
    crect = cfg.tag_colors[i][1]  # color for rectangle around box
    ctext = cfg.tag_colors[i][2]  # default text color: black

    # Box
    dwg.add(dwg.rect(
        (x, y), (cfg.width, cfg.height), 1, 1,
        stroke = crect, fill = color,
        class_='tag{:d} tag_bkg'.format(i)
    ))

    # Text
    dwg.add(dwg.text(
        str(value), insert = (x + cfg.indent, y + cfg.height + cfg.adjust),
        font_size=cfg.fontsize, font_family=cfg.font, fill=ctext,
        class_='tag{:d} tag_txt'.format(i)
    ))

    return cfg.rowheight


#adds images to end of document, currently not used as pngs don't work as well as I'd like and it is easier to just drag and drop the files I want into the final file.
def writeImages(dwg, i, value, ystart, cfg=GDSConfig()):
  currentimage = os.path.join('Images', value + '.png')
  if os.access(currentimage, os.R_OK):
    print('Adding {}'.format(currentimage))
    image = dwg.add(dwg.image(href=currentimage,
                              insert=(i*cfg.imagewidth, ystart),
                              size=(cfg.imagewidth, cfg.imageheight)))
    return cfg.imageheight
  else:
    print("Could not find {}".format(currentimage))  
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


def embed_style(dwg, filename_root, cfg=GDSConfig()):
  if cfg.font in cfg._google_fonts or cfg.font == cfg.google_font:
    print('Embedding Google Font: "{:s}" ... '.format(cfg.font))
    try:
        dwg.embed_google_web_font(
        cfg.font, 
        'https://fonts.googleapis.com/css?family=' + cfg.font.replace(' ', '+'),
        )
    except Exception as e:
        print('\t' + str(type(e)), e)
        print('\tSorry, unable to embed "{:s}"'.format(cfg.font)) 
    else:
        print('\tSuccess, embedded "{:s}"'.format(cfg.font))

  style_filename = '{}.css'.format(filename_root)
  if cfg.link_stylesheet:
    dwg.add_stylesheet('default.css', 'Default SVG Theme')
    dwg.add_stylesheet('{}'.format(style_filename),
                       '{} Theme'.format(filename_root))
  else:
    if os.access('default.css', os.R_OK):
        print('Embedding "{}" stylesheet'.format('default.css'))
        with open('default.css', "r") as f:
            dwg.embed_stylesheet(f.read())
    if os.access(style_filename, os.R_OK):
        print('Embedding "{}" stylesheet'.format(style_filename))
        with open(style_filename, "r") as f:
            dwg.embed_stylesheet(f.read())


def process_csv_data(dwg, lines, cfg=GDSConfig()):
  cursor = 15
  direction = 'Right'

  #read in each line parse, and send each field to writeField  
  records = [line.rstrip().split(',') for line in lines]
  ribbon_width = len(records[0])*cfg.rowwidth + 50 

  if len(records[0]) > len(cfg.tag_colors):
    cfg.tag_colors = [*cfg.tag_colors + [cfg.tag_colors[-1]] * (
        len(records[0]) - len(cfg.tag_colors))]

  for record in records:

    if record[0] in ('Left', 'Right', 'Top', 'Text', 'Extras') and (
            record[0] == ''.join(record).rstrip()):
        direction = record[0]
        cursor += 15
        continue
    elif record[0] == 'EOF' and record[0] == ''.join(record).rstrip():
        break

    if direction == 'Text':
      cursor += cfg.rowheight

    y_add = 0
    label_index = 0
    for i in range(0, len(record)): #go through total number of fields
        if record[i] and direction in ('Right', 'Top'):
          y_add = writeField(dwg, i,record[i], label_index*cfg.rowwidth, cursor, cfg)#call function to add that field to the svg file
          label_index += 1
                  
        elif record[i] and direction=='Left':
          xstart = ribbon_width - cfg.rowwidth - label_index*cfg.rowwidth
          y_add = writeField(dwg, i,record[i], xstart, cursor, cfg)#call function to add that field to the svg file
          label_index += 1
                  
        elif record[i] and direction == 'Text':
           cursor += writeText(dwg, record[i], i, cursor, cfg)
                        
        elif record[i] and direction == 'Extras':
            found_image = writeImages(dwg, i, record[i], cursor, cfg)
            y_add = found_image if found_image else y_add

    cursor += y_add
  # print('cursor: {}\nlength: {}\nwidth: {}'.format(cursor, len(records[0]), cfg.rowwidth))
  dwg.update({'width': str(ribbon_width), 'height': str(cursor)})


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
  if len(argv) in (2, 3) and argv[1].lower().endswith('.csv'):
    infile = argv[1] if len(argv[1]) > 4 else None

  if len(argv) == 3 and argv[2].lower().endswith('.svg'):
    outfile_root = argv[2][0:-4] if len(argv[2]) > 4 else None

  filename_root, lines = read_csv(infile)
  dwg = svgwrite.Drawing(filename=str(filename_root+".svg"),
                         size=(cfg.documentWidth,cfg.documentHeight))
  svg_root = outfile_root if outfile_root is not None else filename_root

  embed_style(dwg, filename_root, cfg)
  process_csv_data(dwg, lines, cfg)
  write_svg(dwg, svg_root, cfg)


if __name__ == '__main__':
  createGDS()

