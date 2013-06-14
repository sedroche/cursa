'''
Created on Oct 20, 2012

Author: John Roche

  The utils module contains a set of utility functions used in the system.
'''
from os.path import exists, join, isfile, sep
from os import makedirs, remove, listdir, chdir
from codecs import open as codec_open
from shutil import copy
from shutil import make_archive, rmtree
from tempfile import mkdtemp
from errorhandling.cursa_exceptions import CursaException
import config


def make_dirs(directoryArray):
    """
    utilty function for creating multiple directories

    args:
         directoryArray (Array):
                                 | String Array containing the directory paths
                                   to create.

    Raises:
         CursaException
    """

    if isinstance(directoryArray, list):
        for directory in directoryArray:
            make_dir(directory)


def make_dir(directory):
    """
    utilty function for creating a directory

    args:
         directory (String):
                            | String indicating the directory path
                              to create.

    Raises:
         CursaException
    """

    try:
        if not exists(directory):
            makedirs(directory)
    except OSError:
        msg = 'Error creating directory at {0}'.format(directory)
        raise CursaException(msg)


def create_file(filePath):
    """
    utilty function for creating a file.

    args:
         filePath (String):
                            | String indicating the file path
                              to create.

    Raises:
         CursaException
    """

    try:
        with open(filePath, 'w'):
            pass
    except IOError:
        msg = 'Error creating file at {0}'.format(filePath)
        raise CursaException(msg)


def create_files(filePathArray):
    """
    utilty function for creating multiple files.

    args:
         filePathArray (Array):
                                 | String Array containing files paths
                                   to create.

    Raises:
         CursaException
    """

    for filePath in filePathArray:
        create_file(filePath)


def create_yaml_template(path, template):
    """
    utilty function for writing YAML template to a file

    args:
         path (str):
                    | Path to create the YAML file

         template (str):
                    | Template to write to the YAML file

    Raises:
         CursaException
    """

    try:
        with open(join(path, 'index.yaml'), 'w') as yaml_tmplt:
            yaml_tmplt.write(template)
    except IOError:
        msg = 'Error creating YAML file at {0}'.format(path)
        raise CursaException(msg)


def read_data_from_file(file_location):
    """| Reads data from a file.
       | This function uses codecs.open() and ensures
         unicode compatability.
       | Function will only read from text files

    Args:
       - file_location (str):  File name with file path

    Returns:
       - (str): The data from the file

    Raises:
         CursaException
    """

    try:
        with codec_open(file_location, mode="r", encoding="utf-8") as f:
            data = f.read()

        return data
    except IOError:
        msg = 'Error opening file at {0}'.format(file_location)
        raise CursaException(msg)


def copy_files(fileArray, dest):
    """| Creates each file in the filearray to dest

        Args:
           - fileArray (List):  List of files to copy
           - dest (str): The destination path to copy the files to

        Raises:
             CursaException
    """

    for f in fileArray:
        try:
            copy(f, dest)
        except IOError:
            msg = 'Error copying file {0} to {1}'.format(f, dest)
            raise CursaException(msg)


def get_css_assets(extra_css=None):
    """| Creates a List of the basic CSS assets needed in a HTML page

        Args:
           - extra_css (List):  List of extra css to add to the page

        Returns:
               List of CSS assets
    """

    bootstrap_css = join(config.cursa_path,
                         'bootstrap.min.css')

    responsive_bootstrap_css = join(config.cursa_path,
                                    'bootstrap-responsive.min.css')

    cursa_css = join(config.cursa_path,
                     'cursa.css')

    css_assets = [bootstrap_css,
                  responsive_bootstrap_css,
                  cursa_css]

    if extra_css:
        for theme in extra_css:
            if theme['css']:
                css = join(config.cursa_path, theme['css'])
                css_assets.append(css)

    return css_assets


def get_js_assets():
    """| Creates a List of the basic CSS assets needed in a HTML page

        Returns:
               List of Javascript assets
    """

    jquery_js = join(config.cursa_path,
                     'jquery-1.7.2.min.js')

    bootstrap_js = join(config.cursa_path,
                        'bootstrap.min.js')

    highight_js = join(config.cursa_path,
                       'highlight.pack.js')

    return [jquery_js,
            bootstrap_js,
            highight_js]


def create_push_params(ob, resourcetype, displayname='', mainfile='',
                       mainfilepath='', labeltext='', labeltextformat=''):
    """| prepares the params for a push to the Moodle web service

        Args:
           - ob (Object):  The calling object, Module, Topic or Lab
           - resourcetype (str): file or label
           - displayname (str): The name beside the resource in Moodle
           - mainfile (str): The file that will be linked to in Moodle
                             This is usually the first step in the lab
                             or the presentation HTML file
           - labeltext (str): The content for the label
           - labelformat (str): HTML or markdown

        Returns:
               Dict of params
    """

    return {
                 'courseid': ob.courseid,
                 'sectionid': ob.sectionid,
                 'type': resourcetype,
                 'displayname': displayname,
                 'mainfile': mainfile,
                 'mainfilepath': mainfilepath,
                 'labeltext': labeltext,
                 'labeltextformat': labeltextformat
             }


def make_tmpdir_with_archive(path):
    '''
    | Creates a temporary directory and an zip archive
      of the temporary directory

    Args:
       - path (str):  The file path to the directory

    Returns:
       - (Dict): Containing the zip path and temporary directory path
    '''

    tmpdir = mkdtemp()
    zip_file_path = make_archive(tmpdir, 'zip', root_dir=path)
    return {
            'zippath': zip_file_path,
            'tmpdir': tmpdir
            }


def delete_tmpdir_and_archive(archiveinfo):
    '''
    | Deletes a temporary directory and an zip archive

    Args:
       - archiveinfo (Dict):  Containing the zip path and temporary directory
                              path
    '''

    remove(archiveinfo['zippath'])
    rmtree(archiveinfo['tmpdir'])


def gather_file_names(path):
    '''
    | Gather all the file names in the given path directory

    Args:
       - path (str):  The file path to the directory

    Returns:
       - (List): List of file names
    '''

    return [f for f in listdir(path) if isfile(join(path, f))]


def delete_files(filelist, path):
    '''
    | Delete all the filenames in filelist

    Args:
       - filelist (List):  List containing the names of the files
       - path (Str):  The file path to the directory

    Raises:
         CursaException
    '''

    chdir(path)
    for each_file in filelist:
        try:
            remove(each_file)
        except OSError:
            msg = 'Error deleting file {0} in {1}'.format(each_file, path)
            raise CursaException(msg)


def clean(path):
    '''
    | Delete all the files in the directory

    Args:
       - path (Str):  The file path to the directory

    Raises:
         CursaException
    '''

    files = gather_file_names(path)
    delete_files(files, path)


def clean_directories(directories):
    '''
    | Delete all the files in the list of directories

    Args:
       - directories (List):  A list containing paths to the directories
    '''

    for path in directories:
        clean(path)


def log(msg):
# Logs a message
# No actual logging being done
# Just prints to stdout
    '''
    | Stub message for logging
    | Prints to stdout for now

    Args:
       - msg (str):  A string to print to the user interface
    '''

    print msg


def write_to_file(path, data):
    """
    utilty function for creating a file and writing data to the file

    args:
         path (str):
                    | Path to create the file

         data (str):
                    | Data to write to the YAML file

    Raises:
         CursaException
    """

    try:
        with open(join(path), 'w') as f:
            f.write(data)
    except IOError:
        msg = 'Error writing to file at {0}'.format(path)
        raise CursaException(msg)


def create_course_info(path):
    '''| Create the course info for a Module, Topic or Lab,
         from the given path
       | The course info defines what Module, Topic or Lab the
         current course section being built belongs to.
       | The cursa path convention can be used to compute this info

           e.g.
                Given a path;

                /cursahome/modulename/topics/topicname/labs/labname

                The course info;

                    {
                      module: modulename,
                      topic: topicname,
                      lab: labname
                    }

                can be computed from the path
        Args:
           - path (str):  current working directory

        Returns:
           - (dict): The course info
    '''

    path_from_app_root = path.replace(''.join([config.cursa_home, sep]), '')
    path_components = path_from_app_root.split(sep)

    if 'topics' in path_components:
        path_components.remove('topics')
    if 'labs' in path_components:
        path_components.remove('labs')

    courseinfo = {}
    path_attributes = ['module', 'topic', 'lab']
    for i in range(0, len(path_components)):
        courseinfo[path_attributes[i]] = path_components[i]

    return courseinfo


def get_img_assets(extra_css):
    img_assets = []
    for theme in extra_css:
        if theme['img']:
            img = join(config.cursa_path, theme['img'])
            img_assets.append(img)

    return img_assets
