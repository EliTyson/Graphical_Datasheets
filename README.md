Graphical Datasheets
========================================
Note: This is a Python 3 fork of the code. The
[original](https://github.com/sparkfun/Graphical_Datasheets) used Python 2.7.
This version is not (yet) backwards compatible with Python 2.

This version functions much like the previous one, with a few modifications:

Command-Line Arguments
----------------------

Syntax: `python tagscript.py [[<CSV filename>] [<SVG filename>]]`

This version also allows the user to specify the .csv file to use as a
command-line argument. For Example:

    python tagscript.py ProMini.csv

Additionally, users can specify an alternate filename for the .svg output file
(the root of the .csv filename is used by default).

    python tagscript.py ProMini.csv foo.svg

* Note that if a file already exists for your .svg filename, tagscript.py will
  increment the name (e.g., foo.svg, foo_02.svg, foo_03.svg...).

Stylesheet Support
------------------

There are a number of ways to style the datasheets using Python, XML/SVG, or
Inkskape. This version also supports embedding .css stylesheets. The script
will look in the directory for two .css files: &apos;default.css&apos; and
&apos;&lt;csv_root&gt;.css&apos; (i.e., If the .csv file is
&apos;ProMini.csv&apos;, the script will look for &apos;ProMini.css&apos;). It
will embed any files with those names (if both files are found the
'default.css' will be embedded first).

Inkskape does not currently support [external
stylesheets](https://wiki.inkscape.org/wiki/index.php/CSS_Support), so the
.css files must be edited **before** running the script.

&apos;tag&lt;#&gt;&apos;, &apos;tag_bkg&apos;, &apos;tag_txt&apos;,
&apos;text_line&apos;, and &apos;text&apos; classes can be used to specify
which element to style.

    /* Change font for non-tag Text elements */
    .text {
        font-family: Arial, Helvetica, sans-serif;
    }

    /* Make the 1st line of text elements bold */
    .text_line0 {
        font-weight: bold;
    }

    /* change the background color of the first tag  to green */
    .tag0.tag_bkg {
        fill: green;

    /* change the outline color of ALL tag backgrounds to silver */
    .tag_bkg {
        stroke: silver;

    /* change the text color of the third tag to white */
    .tag2.tag_txt {
        stroke: white;
* Note that tag #s start at 0 (so the first tag is tag0, the second is tag1,
  and so on).
* Note that any fonts used must either be embedded in the .svg or installed on
  your computer.
* [Learn more about CSS](https://www.w3schools.com/css/default.asp)

---

Code, final versions, and information on the SparkFun Graphical Datasheets.

<table class="table table-hover table-striped table-bordered">
  <tr align="center">
   <td><a href="https://cdn.sparkfun.com/assets/home_page_posts/1/9/4/7/ProMiniRaw.png"><img src="https://cdn.sparkfun.com/assets/home_page_posts/1/9/4/7/ProMiniRaw.png" alt="Generated Cells"></a></td>
   <td><a href="https://cdn.sparkfun.com/assets/home_page_posts/1/9/4/7/ProMini16MHzv1.png"><img src="https://cdn.sparkfun.com/assets/home_page_posts/1/9/4/7/ProMini16MHzv1.png" alt="Completed Graphical Datasheet"></a></td>
  </tr>
  <tr align="center">
   <td><i>Generated Cells After Running Script</i></td>
   <td><i>Example Completed Graphical Datasheet</i></td>
  </tr>
</table>

This repo includes the Python script used to help generate the graphical
datasheets.  It also includes the final .svg, and .pdf files as well as the
.csv files use for development boards.  The .csv files were used as a starting
point and some text did change between the file and the final version.  There
is also a User Submitted folder for external contributions.

### Setting Up and Running the Script via Notepad++

One method is to use **Notepad++** to edit and a plug-in to run the script.
Download and install Notepadd++ v7.7.1 on your computer. From Notepad++'s
**Plugins** > **Plugins Admin...** menu, search for **PyNPP** plug-in and
install. We used PyNPP v1.0.0. You may need to search online, download the
plug-in, and manually install on Notepad++ from the **Settings** > **Import** >
**Import plug-in(s)...** menu. This plug-in is optional if you want to run the
script from Notepad++.

We'll assume that you have **Python 3** installed. If you have not already,
open up the command prompt. To check the version of Python, type the following
to see if you are using Python 2 or Python 3. If you do not see Python 3, you
will need to adjust your environment variables [i.e. **System Properties** >
**Environment Variables...**, then **System Variables** > **Path** >
**Edit...**, and add the location of your installed Python 3 to a field] to be
able to use that specific version.

    python --version

Use the python package manager to install svgwrite from the command line.

    python -m pip install svgwrite


Alternative, to manually install, [download and unzip the **svgwrite** module
(v1.4)](https://pypi.python.org/pypi/svgwrite/). In a command line, change the
path to where **...\svgwrite** folder is located and use the following command
to install.

    python setup.py install

Create a CSV of the pinout for your development board. You can also edit the
CSV from any of the examples. For simplicity, copy the Pro Mini's file
(**...Graphical_Datasheets\Datasheets\ProMini\ProMini.csv** ) and paste it in
the same folder as the python script (**...\Graphical_Datasheets**). Open one
of the **tagscript.py** scripts in Notepad++ and run the script from the menu:
**Plugins** > **PyNPP** > **Run File in Python**. 

A window will pop up requesting for the CSV file name. Enter the file name
(like `ProMini`), it will output the SVG with the same name. 

After running the script, open the SVG file in Inkscape (or Illustrator) with
an image of your development board to align or adjust the pinouts! Feel free to
adjust the script to format your cells based on your personal preferences. Have
fun!

### Setting Up and Running the Script via Command Line

You can use any text editor to edit the script. The following instructions do
not require PyNPP. Additionally, it is an alternative method to install the
svgwrite module and run the Python script via command line.

Again, we'll assume that you have **Python 3** installed. If you have not
already, open up the command prompt. To check the version of Python, type the
following to see if you are using Python 2 or Python 3. If you do not see
Python 3, you will need to adjust your environment variables [i.e. **System
Properties** > **Environment Variables...**, then **System Variables** >
**Path** > **Edit...**, and add the location of your installed Python 3 to a
field] to be able to use that specific version.

    python --version

Open a command prompt and use the following command to install the latest
version of **svgwrite**.

    python -m pip install svgwrite
    
Create a CSV of the pinout for your development board. You can also edit the
CSV from any of the examples. For simplicity, copy the Pro Mini's file
(**...Graphical_Datasheets\Datasheets\ProMini\ProMini.csv** ) and paste it in
the same folder as the python script (**...\Graphical_Datasheets**). Use the
following command to execute the script.

    python tagscript.py

A window will pop up requesting for the CSV file name. Enter the file name
(like `ProMini`), it will output the SVG with the same name. 

After running the script, open the SVG file in Inkscape (or Illustrator) with
an image of your development board to align or adjust the pinouts! Feel free to
adjust the script to format your cells based on your personal preferences. Have
fun!

Required Software
-------------------

Some software used to create graphical datasheets. At the time of writing,
Python 3 was used to generate the tags. You may need to adjust the script to
work with the latest NotePad++, NyPP plug-in, and svgwrite versions.

* *[Notepad++ v7.7.1](https://notepad-plus-plus.org/downloads/v7.7.1/)* - Text
  editor to modify the Python script
  * *PyNPP v1.0.0* -  Optional plug-in to run Python Scripts
* **Python v3.6 or later**
  * [svgwrite v1.4](https://pypi.python.org/pypi/svgwrite/)
* **[Inkscape v0.92.4](https://inkscape.org/release/inkscape-0.92.4/)**

Repository Contents
-------------------

* **/Datasheets** - CSV of pinouts and graphical datasheets for development
  boards
* **tagscript.py** - Script to generate cells for graphical datasheets
* **default.css** - A stylesheet to use for customizing the appearance of the
  graphical datasheets.

Original Documentation
----------------------

* [Enginursday: Graphical Datasheets](https://www.sparkfun.com/news/1947) - For
  more information on the graphical datasheets check out our blog post on them.
