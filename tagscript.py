#!/usr/bin/python3
"""Create a Graphical Datasheet SVG file from a formatted CSV file.

Syntax: `python tagscript.py [[<CSV filename>] [<SVG filename>]]
A comma-separated values (CSV) filename can be supplied to the script as
an argument:
    e.g., `python tagscript.py ProMini.csv`
Alternatively, the user may run the script without arguments and enter
the CSV filename root when prompted.  The proper CSV formatting is
described in the accompanying README.md.

By default the root of the CSV filename will be used for the SVG file.
So `ProMini.csv` will result in a `ProMini.svg`.  A different SVG
filename can be specified by entering a SVG filename with the second
parameter:
    e.g., `python tagscript.py ProMini.csv foo.svg`

The following were used as resources for creating the script:
* <http://www.astro.ufl.edu/~warner/prog/python.html> Python Basics
* <https://pypi.python.org/pypi/svgwrite/>  svgwrite library
"""

import os
from sys import argv, exit as sys_exit
from urllib.error import HTTPError, URLError

from svgwrite import Drawing


class GDConfig(object):
    """Configuration settings for Graphical Datasheet creation.

    Instantiation of GDConfig without arguments results in a default
    configuration object.  Use keyword arguments to override default
    options:
        `GDConfig(font='Times', tab_margin_x=5, overwrite=True)`

    Attributes:
        font: (str, Default:'Varta') The font used throughout the
            datasheet.
        google_font: (str, Default:None) Google font to download and
            embed.  Note that the font will only be used if it is
            specified with 'font' (or a stylesheet).
        default_google_fonts: (set) This is a private attribute that CANNOT be
            set during instantiation. Set of google font names that will
            automatically be embedded without being specified with the
            'google_font' attribute. The list includes:
                'Montserrat', 'IBM Plex Sans', 'Big Shoulders Display',
                'Varta', 'Roboto Condensed', 'Inconsolata'
        font_size: (int, Default: 12) Size of font for all datasheet
            text.
        tag_txt_margins: (tuple/list, Default: (1, 2)) Number of pixels (on
            left and bottom) before text of tag begins.
        tag_txt_color: (str, Default: '#000000') Default text color for
            tags (can be overridden using 'tag_colors')
        tag_colors: (list, Default: None) List of colors to use for each
            tag index.  Each item in the list is itself a list of 3
            color strings. The first color corresponds to the tag
            background color, the second to the tag outline, and the
            third to the tag
            text: [<bkg_color>, <outline_color>, <text_color>].
                e.g., [['red', 'blue', 'white'], ['cyan', 'orange',
                'black'], ...]
        tag_size: (tuple/list, Default: (45, 12)) Width, Height of tag
            background.
        tag_margins: (tuple/list, Default: (3, 3)) Pixels to left and below tag
            bkgs.
        image_size: (tuple/list, Default: (250, 250)) Width/Height of embedded
            PNG images (maintains aspect ratio).
        text_line_height: (int, Default 17) Line height for 'Text' mode
            lines.
        document_size: (tuple/list, Default: (None, None)) Width/Height of the
            SVG in pixels.  If either dimension is set to 'None' the size will
            be set dynamically to accommodate all of the included SVG elements.
        link_stylesheet: (bool, Default: False) Link stylesheet rather
            than embedding it. Note, linked stylesheets are not
            currently supported by Inkskape (although they may be
            supported in future releases).
        overwrite: (bool, Default: False) Overwrite SVG files.  If False
            and the presumed filename already exists it increments
            (e.g., foo.svg, foo_2.svg, foo_3.svg,...)
        pretty: (bool, Default: True) Save SVG file in a more readable,
            indented file.  If False, the resulting SVG will not have
            indentation and multiple elements per line.  Setting it to
            False will thereby result in a smaller file size.
    """

    def __init__(
                 self,
                 font='Varta',
                 google_font=None,
                 font_size=12,
                 tag_txt_margins=(1, 2),
                 tag_txt_color='#000000',
                 tag_colors=None,
                 tag_size=(45, 12),
                 tag_margins=(3, 3),
                 image_size=(250, 250),
                 text_line_height=17,
                 document_size=(None, None),
                 link_stylesheet=False,
                 overwrite=False,
                 pretty=True,
                ):
        """Initializes a GDConfig object.

        Args:
            (See GDConfig 'Attributes' descriptions)
            tag_colors: (list, Default: None) Specifies the list of
                colors to use with each tag index.  Each list item is
                itself a list of three color strings corresponding to
                the tag background, outline and text. If list items are
                a list of two colors, then 'tag_txt_color' will be used
                for the third list item.  If the item is a list of a
                single color (i.e., ['red']) or simply a color string,
                that color is used as both the background color and the
                outline color with the 'tag_txt_color' used for the
                text.
                If a 'tag_colors' list item is None or is improperly
                formatted, the default colors will be used instead.  So
                `[None, 2, ['purple', 'yellow', 'white'], 4, 'red']`
                will only alter the colors for the third and fifth tags
                (index 2 and 6).
        """
        self.font = font
        self.google_font = google_font
        self.default_google_fonts = {
                              'Montserrat',
                              'IBM Plex Sans',
                              'Big Shoulders Display',
                              'Varta',
                              'Roboto Condensed',
                              'Inconsolata',
                             }
        self.font_size = font_size
        self.tag_txt_margins = list(tag_txt_margins)
        self.tag_txt_color = tag_txt_color
        self.tag_colors = self.get_colors(tag_colors)
        self.tag_size = list(tag_size)
        self.tag_margins = list(tag_margins)
        self.image_size = list(image_size)
        self.text_line_height = text_line_height
        self.document_size = list(document_size)
        self.link_stylesheet = link_stylesheet
        self.overwrite = overwrite
        self.pretty = pretty

    def get_colors(self, new_colors):
        """Alters the default tag color scheme.

        If list items are a list of two colors, then 'tag_txt_color'
        will be used for the third list item.  If the item is a list of
        a single color (i.e., ['red']) or simply a color string, that
        color is used as both the background color and the outline color
        with the 'tag_txt_color' used for the text.  If a 'tag_colors'
        list item is None or is improperly formatted, the default colors
        will be used instead.

        `get_colors([None, 2, ['purple', 'yellow', 'white'], 4, 'red'])`
        will only alter the colors for the third and fifth tags (index 2
        and 4).

        Args:
            new_colors: (list) A list of color settings for each tag
                index.
        Returns:
            A list of tag color settings (each in the form of a three
            string list).  If new_colors is None, the default_colors
            list is returned unchanged.  Otherwise the list is created
            based on the passed-in new_colors list.
        """
        default_colors = [
            ['#ffffff', '#b3b3b3', self.tag_txt_color],
            ['#ff3333', '#ff3333', self.tag_txt_color],
            ['#191919', '#191919', '#ffffff'],
            ['#ffff4d', '#ffff4d', self.tag_txt_color],
            ['#b3d9b3', '#b3d9b3', self.tag_txt_color],
            ['#9999ff', '#9999ff', self.tag_txt_color],
            ['#cc99cc', '#cc99cc', self.tag_txt_color],
            ['#ffffb3', '#ffffb3', self.tag_txt_color],
            ['#d9d9d9', '#d9d9d9', self.tag_txt_color],
            ['#e6cce6', '#e6cce6', self.tag_txt_color],
            ['#ffd280', '#ffd280', self.tag_txt_color],
            ['#e6e6ff', '#e6e6ff', self.tag_txt_color],
        ]
        if new_colors is None and not isinstance(new_colors, (list, tuple)):
            return default_colors

        if isinstance(new_colors, tuple):
            new_colors = [*new_colors]

        for i, value in enumerate(new_colors):
            new_colors[i] = None
            if isinstance(new_colors[i], str):
                new_colors[i] = [value,
                                 value,
                                 self.tag_txt_color]
            elif isinstance(new_colors[i], (list, tuple)):
                if len(new_colors[i]) == 3:
                    new_colors[i] = list(new_colors[i])
                elif len(new_colors[i]) == 2:
                    new_colors[i] = [value[0],
                                     value[1],
                                     self.tag_txt_color]
                elif len(new_colors[i]) == 1:
                    new_colors[i] = [value[0],
                                     value[0],
                                     self.tag_txt_color]

        if len(new_colors) > len(default_colors):
            default_colors = [*default_colors + [default_colors[-1]] * (
                              len(new_colors) - len(default_colors))]

        final_colors = default_colors[:]
        for i, value in enumerate(new_colors):
            if value is not None:
                final_colors[i] = value

        return final_colors


def add_tag(dwg, i, value, position, cfg=GDConfig()):
    """Add tags comprised of colored blocks and text.

    Args:
        dwg: (svg.drawing.Drawing) A svgwrite Drawing instance to amend.
        i: (int) The index of the tag element.
        value: (str) A string of text to add above the tag background.
        y: (int) The vertical position to add the tag in the SVG.
        cfg: (GDConfig Default=GDConfig()) Graphical Datasheet
            configuration to use.

    Returns:
        An int, providing the amount of vertical space used.
    """
    color_bkg, color_outline, color_txt = cfg.tag_colors[i]
    position_x, position_y = position

    dwg.add(dwg.rect(
        insert=(position_x, position_y),
        size=(cfg.tag_size[0], cfg.tag_size[1]),
        rx=1,
        ry=1,
        stroke=color_outline,
        fill=color_bkg,
        class_='tag{:d} tag_bkg'.format(i)
    ))

    dwg.add(dwg.text(
        value,
        insert=(position_x + cfg.tag_txt_margins[0],
                position_y + cfg.tag_size[1] - cfg.tag_txt_margins[1]),
        font_size=cfg.font_size,
        font_family=cfg.font,
        fill=color_txt,
        class_='tag{:d} tag_txt'.format(i)
    ))

    return cfg.tag_size[1] + cfg.tag_margins[1]


def add_text(dwg, i, value, ystart, cfg=GDConfig()):
    """Add plain text from the 'Text' section of the CSV.

    Args:
        dwg: (svg.drawing.Drawing) A svgwrite Drawing instance to amend.
        i: (int) The index of the text element.
        value: (str) A string of text to add to the SVG.
        ystart: (int) The vertical position to add the text in the SVG.
        cfg: (GDConfig Default=GDConfig()) Graphical Datasheet
            configuration to use.

    Returns:
        An int, providing the amount of vertical space used.
    """
    dwg.add(dwg.text(str(value),
                     insert=(0, ystart),
                     font_size=12,
                     font_family=cfg.font,
                     fill='black',
                     class_='text_line{:d} text'.format(i)))
    return cfg.text_line_height


def add_images(dwg, i, value, ystart, cfg=GDConfig()):
    """Adds PNG images to the SVG.

    Args:
        dwg: (svg.drawing.Drawing) A svgwrite Drawing instance to amend.
        i: (int) The index of the image element.
        value: (str) The PNG filename root.
        ystart: (int) The vertical position to add the image.
        cfg: (GDConfig Default=GDConfig()) Graphical Datasheet
            configuration to use.

    Returns:
        An int, providing the amount of vertical space used.
    """
    currentimage = os.path.join('Images', value + '.png')
    if os.access(currentimage, os.R_OK):
        print('Adding {}'.format(currentimage))
        dwg.add(dwg.image(href=currentimage,
                          insert=(i*cfg.image_size[0], ystart),
                          size=(cfg.image_size[0], cfg.image_size[1])))
        return cfg.image_size[1]

    print('Could not find {}'.format(currentimage))
    return 0


def read_csv(infile):
    """Gets data from a CSV file for processing into an SVG file.

    If 'infile' is None the user is prompted to enter the root of a CSV
    filename.

    Args:
        infile: (str) CSV filename to read
    """
    if infile is None:
        print('Make sure the python script is in the same folder as the file.')
        filename_root = input(
            'Enter filename without the .csv extension (e.g., ESP8266/Thing): '
        )
        csv_filename = filename_root + '.csv'
    else:
        filename_root = infile[0:-4]
        csv_filename = infile

    if os.access(csv_filename, os.R_OK):
        with open(csv_filename, 'r') as csv_file:
            print('"{}" opened'.format(csv_filename))
            lines = csv_file.read().splitlines()
            return filename_root, lines
    else:
        print('CSV data file not found. Please try again. '
              'See README.md for details.')
        sys_exit(0)


def embed_style(dwg, filename_root, cfg=GDConfig()):
    """Embed any necessary google fonts and stylesheets.

    Args:
        dwg: (svg.drawing.Drawing) A svgwrite Drawing instance to amend.
        filename_root: (str) root of the CSV file to embed.
        cfg: (GDConfig Default=GDConfig()) Graphical Datasheet
            configuration to use.
    """
    embed_fonts = []
    if cfg.font in cfg.default_google_fonts:
        embed_fonts.append(cfg.font)
    if cfg.google_font is not None:
        embed_fonts.append(cfg.google_font)

    for embed_font in embed_fonts:
        print('Embedding Google Font: "{:s}"'.format(embed_font))
        try:
            dwg.embed_google_web_font(
                embed_font,
                ('https://fonts.googleapis.com/css?family='
                 + embed_font.replace(' ', '+')))
        except (HTTPError, URLError) as exc:
            print('\t' + str(type(exc)), exc)
            print('\tSorry, unable to embed "{:s}"'.format(embed_font))

    style_filename = filename_root + '.css'
    if cfg.link_stylesheet:
        print('Linking "{}" stylesheet'.format('default.css'))
        dwg.add_stylesheet('default.css', 'Default SVG Theme')
        print('Linking "{}" stylesheet'.format(style_filename))
        dwg.add_stylesheet(style_filename,
                           '{} Theme'.format(filename_root))
    else:
        if os.access('default.css', os.R_OK):
            print('Embedding "{}" stylesheet'.format('default.css'))
            with open('default.css', 'r') as css_file:
                dwg.embed_stylesheet(css_file.read())
        if os.access(style_filename, os.R_OK):
            print('Embedding "{}" stylesheet'.format(style_filename))
            with open(style_filename, 'r') as css_file:
                dwg.embed_stylesheet(css_file.read())


def process_csv_data(dwg, lines, cfg=GDConfig()):
    """Parse data and call add_field(), add_text(), and add_images().

    Args:
        dwg: (svg.drawing.Drawing) A svgwrite Drawing instance to amend.
        lines: (list) CSV file lines in a list of strings.
        cfg: (GDConfig Default=GDConfig()) Graphical Datasheet
            configuration to use.
    """
    cursor = cfg.tag_size[1] + cfg.tag_margins[1]
    mode = None

    records = [line.split(',') for line in lines]
    ribbon_width = (len(records[0]) + 1) * (cfg.tag_size[0]
                                            + cfg.tag_margins[0])
    images_width = 0

    if len(records[0]) > len(cfg.tag_colors):
        diff = len(records[0]) - len(cfg.tag_colors)
        cfg.tag_colors = [*cfg.tag_colors + [cfg.tag_colors[-1]] * diff]

    for record in records:
        # Some repository CSV files have a '1' in the last column.  This
        # '1' is ignored for determining mode.
        if record[0] in ('Left', 'Right', 'Top', 'Text', 'Extras') and (
                record[0] == ''.join(record).rstrip('1')):
            mode = record[0]
            cursor += 15
            continue

        if record[0] == 'EOF' and record[0] == ''.join(record).rstrip('1'):
            break

        if mode == 'Text':
            cursor += cfg.tag_size[1] + cfg.tag_margins[1]

        y_add = 0
        label_index = 0
        image_index = 0
        for i, rec in enumerate(record):
            if rec and mode in ('Right', 'Top', None):
                x_start = label_index * (cfg.tag_size[0] + cfg.tag_margins[0])
                y_add = add_tag(dwg, i, rec, (x_start, cursor), cfg)
                label_index += 1

            elif rec and mode == 'Left':
                tag_space = cfg.tag_size[0] + cfg.tag_margins[0]
                x_start = ribbon_width - tag_space - (label_index * tag_space)
                y_add = add_tag(dwg, i, rec, (x_start, cursor), cfg)
                label_index += 1

            elif rec and mode == 'Text':
                cursor += add_text(dwg, i, rec, cursor, cfg)

            elif rec and mode == 'Extras':
                found_image = add_images(dwg, i, record[i], cursor, cfg)
                if found_image != 0:
                    y_add = found_image
                    image_index += 1

        cursor += y_add
        if mode == 'Extras' and images_width < image_index * cfg.image_size[0]:
            images_width = image_index * cfg.image_size[0]

    min_width = ribbon_width if ribbon_width > images_width else images_width
    width = min_width if cfg.document_size[0] is None else cfg.document_size[0]
    height = cursor if cfg.document_size[1] is None else cfg.document_size[1]
    dwg.update({'width': str(width), 'height': str(height)})


def write_svg(dwg, name_root, cfg=GDConfig()):
    """Saves the SVG to the current directory

    Args:
        dwg: (svg.drawing.Drawing) A svgwrite Drawing to save to disk.
        name_root: (str) root for the output SVG file.
        cfg: (GDConfig Default=GDConfig()) Graphical Datasheet
            configuration to use.
    """
    new_name = name_root
    if not cfg.overwrite:
        i = 2
        while os.access(new_name + '.svg', os.F_OK):
            new_name = '{0}_{1:02d}'.format(name_root, i)
            i += 1

    print('End of File, the output is located at {}.svg'.format(new_name))
    dwg.saveas(new_name + '.svg', pretty=cfg.pretty)


def create_gd(cfg=GDConfig()):
    """Main function to load the CSV, processes it, and save the SVG.

    Args:
        cfg: (GDConfig Default=GDConfig()) Graphical Datasheet
            configuration to use.
    """
    infile = None
    outfile_root = None
    if len(argv) in (2, 3) and argv[1].lower().endswith('.csv'):
        infile = argv[1] if len(argv[1]) > 4 else None

    if len(argv) == 3 and argv[2].lower().endswith('.svg'):
        outfile_root = argv[2][0:-4] if len(argv[2]) > 4 else None

    filename_root, lines = read_csv(infile)
    dwg = Drawing(filename=filename_root + '.svg')
    svg_root = outfile_root if outfile_root is not None else filename_root

    embed_style(dwg, filename_root, cfg)
    process_csv_data(dwg, lines, cfg)
    write_svg(dwg, svg_root, cfg)


if __name__ == '__main__':
    config = GDConfig(
                      # google_font='Mr Roboto',
                      # image_size[0]=500,
                     )
    create_gd(config)
