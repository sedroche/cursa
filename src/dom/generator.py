'''
Created on Nov 29, 2012

Author: John Roche

| The generator module is a facade between the cursa application
| and the output generation modules, tools and applications that cursa uses to
  create the output from the content files
'''

from mdx_video import VideoExtension
import view
from utils import read_data_from_file
from os.path import join, exists
from os import sep, remove, devnull, chdir
from codecs import open as codec_open
from re import findall, DOTALL, UNICODE
from subprocess import Popen, PIPE
from markdown import markdown
from tarfile import open as tarfile_open
from errorhandling.cursa_exceptions import CursaException
import config


def generate(stepparams=None,  labparams=None,
             topicparams=None, moduleparams=None):
    """
    | This function is the single public method that the system can
      use to interact the output generation modules.
    | generate will decide what action to take based on the parameters passed
      and create the output.

      args:
           - stepparams (Dict): A dictionary object containing the
                                params for the Step.

           - labparams (Dict): A dictionary object containing the
                                params for the Lab.

           - topicparams (Dict): A dictionary object containing the
                                 params for the Topic.
                                 topicparams should have a key named 'category'
                                 which indicates which output to create
                                 valid entries for category are;
                                     - 'index'
                                     - 'text'
                                     - 'pres_text'
                                     - 'label'

           - moduleparams (Dict): A dictionary object containing the
                                  params for the Topic.
    """

    if stepparams:
        _do_step(stepparams)

    elif labparams:
        _do_lab_text(labparams)

    elif topicparams:
        category = topicparams.pop('category')

        if category == 'index':
            _do_topic(topicparams)

        if category == 'label':
            return _parse_markdown(topicparams['content'])

        elif category == 'pres':
            _do_pres(topicparams)

        elif category == 'pres_text':
            _do_pres_text(topicparams)

    elif moduleparams:
        _do_module(moduleparams)


def _do_step(stepparams):
    """| Creates a HTML file that contains the content
         stored in the Markdown file

        Args:
           - stepparams (dict):  stepparams should have the
                                 structure:

                                   {
                                     | 'title':
                                     | 'labpath':
                                     | 'navbar':
                                     | 'css' :
                                   }

                     - title: Name of Markdown file
                     - labpath: Path to Lab containing step
                     - navbar: Navigation bar for the Lab
                     - css: The css for the step
    """

    md_location = ''.join([stepparams['labpath'],
                       sep,
                       'md',
                       sep,
                       stepparams['title'],
                       '.md'])

    step_html = _parse_markdown(md_location)

    title = stepparams['title']
    navbar = stepparams['navbar']

    step_view = view.get_step_view(title, step_html, navbar, stepparams['css'])

    output_dest = ''.join([stepparams['labpath'],
                           sep,
                           'html',
                           sep,
                           stepparams['title'],
                           '.html'])

    _write_view_to_file(output_dest, step_view)


def _do_lab_text(labparams):
    """| Creates a PDF file that contains the combined content
         of all the steps in a lab

        Args:
           - labparams (dict):  labparams should have the
                                 structure:

                                   {
                                      | 'title':
                                      | 'steps':
                                      | 'labpath':
                                      | 'css':
                                   }

                     - title (str): Name of the PDF file
                     - steps (List): Contains the meta data about all steps in
                                     the lab
                     - labpath (str): file path to Lab
                     - css (List): List of CSS assets for the lab
    """

    lab_html = _create_lab_html(labparams['steps'],
                                labparams['labpath'])

    lab_text_view = view.get_lab_text_view(lab_html, labparams['css'])

    output_dest = ''.join([labparams['labpath'],
                           sep,
                           'pdf',
                           sep,
                           labparams['title'],
                           '.pdf'])

    args = ['wkhtmltopdf',
            '--quiet',
            'toc',
            '--xsl-style-sheet',
            'toc.xsl',
            '-',
            output_dest]

    _remove_output_dest(output_dest)
    _create_pdf(args, lab_text_view.encode('utf8'))


def _do_pres_text(topicparams):
    """| Creates a PDF version of a HTML presentation

        Args:
           - topicparams (dict):  topicparams should have the structure:

                                   {
                                      | 'title':
                                      | 'content':
                                      | 'prespath'
                                   }

                         - title of the topic
                         - content: The content file name
                         - prespath: Path to presentations folder
                         - css: The CSS for the presentation text
    """

    md_location = join(topicparams['prespath'],
                       'md',
                       topicparams['content'])

    content = read_data_from_file(md_location)
    pres_html = _parse_pres_markdown(content)

    # This class is added so the user can change the wkhtmltopdf slides
    # without affecting the HTML presentation slides
    pres_html = pres_html.replace(u'<section class="slide" [extra css]>',
                                  u'<section class="slide wkhtmltopdf-slide">')

    pres_text_view = view.get_pres_text_view(pres_html, topicparams['css'])

    output_dest = ''.join([topicparams['prespath'],
                           sep,
                           'pdf',
                           sep,
                           topicparams['title'],
                           '.pdf'])

    args = ['wkhtmltopdf',
            '--quiet',
            '--orientation',
            'landscape',
            '--page-size',
            'A3',
            '--margin-right',
            '0mm',
            '--margin-top',
            '0mm',
            '--margin-bottom',
            '0mm',
            '--margin-left',
            '0mm',
            '-',
            output_dest]

    _remove_output_dest(output_dest)
    _create_pdf(args, pres_text_view.encode('utf8'))


def _create_lab_html(steps, labpath):
    """| Parses the content from each step in the list steps into HTML
         and combines the HTML into one String

        Args:
             - steps (List): Contains the meta data about all steps in
                             the lab
             - labpath (str): file path to Lab

        Returns:
           - (str): Generated HTML from Markdown of the combined steps in the
                    lab
    """

    lab_html = u''
    len_steps = len(steps)
    for i in range(0, len_steps):
        md_location = ''.join([labpath,
                              sep,
                              'md',
                              sep,
                              steps[i]['markdown'],
                              '.md'])

        content = read_data_from_file(md_location)
        content = _make_imageurls_absolute(content, labpath)
        step_html = _generate_html(content)

        page_end = ''
        if i < len_steps - 1:
            page_end = '&nbsp;<div class="page-breaker"></div>'

        lab_html = u''.join([lab_html,
                             step_html,
                             page_end])

    return lab_html


def _remove_output_dest(output_dest):
    """| Remove the file at the path
    """

    if exists(output_dest):
        remove(output_dest)


def _untar_macosx_directory():
    """| Before a call to wkhtmltopdf on OSX can be made,
         some dependencies need to be extracted from archive.
       | This is becuse PyInstaller does not allow directories to be bundled
         into the executable so an archive of the directory was bundled
    """

    macosx_files = join(config.cursa_path, 'qt_menu.nib.tar')
    if exists(macosx_files):
        with tarfile_open(macosx_files) as nib_tar:
            nib_tar.extractall(path=config.cursa_path)


def _do_topic(topicparams):
    """| Creates a HTML file - index.html - that is the
         interface to the topic.

        Args:
           - topicparams (dict):  topicparams should have the structure:

                                   {
                                      | 'title':
                                      | 'content':
                                      | 'topicpath':
                                      | 'topicinfo':
                                   }


                         - title: Title of the topic,
                         - content: The content file name,
                         - topicpath: Path to topic,
                         - topicinfo: markdown with info about the labs
                                      and presenations in the topic
    """

    md_location = topicparams['content']

    topic_html = _parse_markdown(md_location)
    lab_info = _generate_html(topicparams['topicinfo'])
    topic_html = '\n'.join([topic_html,
                          lab_info])

    title = topicparams['title']
    topic_view = view.get_topic_view(title, topic_html)

    output_dest = join(topicparams['topicpath'],
                       'index.html')

    _write_view_to_file(output_dest, topic_view)


def _do_pres(topicparams):
    """| Creates a HTML presentation

        Args:
           - topicparams (dict):  topicparams should have the structure:

                                   {
                                      | 'title':
                                      | 'content':
                                      | 'prespath':
                                      | 'css':
                                   }

                         - title of the topic
                         - content: The content file name
                         - prespath: Path to presentations folder
                         - css: The CSS for the presentation
    """

    md_location = join(topicparams['prespath'],
                       'md',
                       topicparams['content'])

    content = read_data_from_file(md_location)
    pres_html = _parse_pres_markdown(content)

    # No Extra CSS added on the HTML presentation
    pres_html = pres_html.replace(u'<section class="slide" [extra css]>',
                                  u'<section class="slide">')

    pres_view = view.get_pres_view(topicparams['title'],
                                   pres_html,
                                   topicparams['css'])

    output_dest = ''.join([topicparams['prespath'],
                          sep,
                          'html',
                          sep,
                          topicparams['title'],
                          '.html'])

    _write_view_to_file(output_dest, pres_view)


def _create_pdf(args, data):
    """| Creates a PDF from a string containing HTML

        Args:
           - args (List):  The list of arguments to the wkhtmltopdf
                           application

           - data (str): The HTML string
    """

    _untar_macosx_directory()
    chdir(config.cursa_path)

    # wkhtmltopdf sends unwanted error messages to stdout
    # Send them to the null device
    with open(devnull, 'wb') as null:
        ps = Popen(args,
                   stdin=PIPE,
                   stdout=null,
                   stderr=null,
                   shell=False)

        # Send the data to stdin
        ps.communicate(data)


def _do_module(moduleparams):
    """| Creates a HTML file, index.html, that is the
         interface to the module.

        Args:
           - moduleparams (dict):  moduleparams should have the structure:

                                   {
                                     | 'title':
                                     | 'modulepath':
                                     | 'topiclinks':
                                   }

                         - title: Title of the module
                         - modulepath: Path to Module
                         - topiclinks: Hypertext links to each topic in the
                                       module
    """

    title = moduleparams['title']
    topic_links = moduleparams['topiclinks']

    module_html = view.get_module_view(title, topic_links)

    output_dest = join(moduleparams['modulepath'],
                       'index.html')

    _write_view_to_file(output_dest, module_html)


def _parse_markdown(md_location):
    """| Parses Markdown that will be converted to HTML

        Args:
           - md_location (str):  File name with file path to location of
                                 the Markdown file

        Returns:
           - (str): Generated HTML from Markdown
    """

    content = read_data_from_file(md_location)
    html = _generate_html(content)
    return html


def _parse_pres_markdown(md):
    """| Parses Markdown that will be converted to a HTML Presentation

       .. note::
                   | Cursa Presentation Markdown has new syntax delimiting the
                     start and end of a presentation slide.
                   | The new delimiting syntax is 3 equal signs, e.g.
                       ===

                       ##Standard Markdown here

                       ===

                   | Equal signs are replaced with HTML section tags, e.g.

                       <section class="slide">

                       <h2>Standard Markdown here</h2>

                       </section>
        ..

        Args:
           - md (str):  The markdown content

        Returns:
           - (str): Generated HTML from Markdown
    """

    pattern = r'(={3})(.*?)(={3})'
    mdsections = findall(pattern, md, flags=DOTALL | UNICODE)

    len_mdsections = len(mdsections)
    html = u''
    for i in range(0, len_mdsections):
        #No page break on last section.
        #Inserts a unnecessary blank page at the end of the generated file
        page_end = ''
        if i < len_mdsections - 1:
            page_end = '&nbsp;<div class="page-breaker"></div>'

        html = u''.join([html,
                         u'<section class="slide" [extra css]>',
                         _generate_html(mdsections[i][1]),
                         u'</section>',
                         page_end])
    return html


def _make_imageurls_absolute(content, labpath):
    """| Changes any Markdown image syntax with a relative src
         to an absolute src

       .. note::
                     e.g.

                    ![](../img/image.png)

                    will be replaced with

                    ![](absolute/path/to/img/image.png)
        ..

        Args:
           - content (str):  The Markdown content

        Returns:
           - (str): The content with img src set to absolute path
    """

#This regex is the actual regex used in the markdown.inlinepatterns class
#This will match the url pattern exactly the same as markdown.py
    NOBRACKET = r'[^\]\[]*'
    BRK = (r'\[(' +
    (NOBRACKET + r'(\[') * 6 +
    (NOBRACKET + r'\])*') * 6 +
    NOBRACKET + r')\]')

    IMAGE_LINK_RE = r'\!' + BRK + r'\s*\((<.*?>|([^\)]*))\)'

    matches = findall(IMAGE_LINK_RE, content)

    if matches:
        for match in matches:
            image_src = match[8]
            image_src_absolute = image_src.replace('../',
                                                   ''.join([labpath, sep]))

            content = content.replace(image_src,
                                      image_src_absolute)

    return content


def _generate_html(content):
    """| Generates a HTML string from a Markdown string

    Args:
       - content (Unicode str):  Markdown content

    Returns:
       - (Unicode str): HTML form of the Markdown content
    """

    video = VideoExtension({})
    html = markdown(content,
                    ['extra', video],
                    output_format='html5')
    return html


def _write_view_to_file(file_to_create, data):
    """| Creates a file and writes data to that file.
       | This function uses codecs.open() and ensures
         unicode compatability.
       | data must be a string, not Binary data

    Args:
       - file_to_create (str):  File name with file path
       - data (str):  The data to write to the file

    Raises:
         CursaException
    """

    try:
        with codec_open(file_to_create,
                        mode='w',
                        encoding="utf-8",
                        errors="xmlcharrefreplace") as f:

            f.write(data)
    except IOError:
        msg = 'Error creating file {0}'.format(file_to_create)
        raise CursaException(msg)
