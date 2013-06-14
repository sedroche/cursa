'''
Created on Oct 20, 2012

Author: John Roche
'''
import utils
from step import Step
from os.path import join, abspath
from os import sep, chdir
from generator import generate
from webserviceclient import WebServiceClient
from errorhandling.cursa_exceptions import CursaException
from distutils.dir_util import copy_tree
from tempfile import mkdtemp
from shutil import make_archive
from glob import glob
import config


class Lab(object):
    '''
    | The Lab class is responsible for creating the file structure for a Lab
      and the orchestration of a build of a Lab.
    | A Lab consists of a collection of Steps and is responsible for the
      management of the Steps in the Lab.
    '''

    def __init__(self, labmeta=None):
        """
        Kwargs:
           labmeta (dict): Contains the meta data to create the Lab Object.
                           Meta data will be read from the index.yaml file
                           for the Lab.
                           Check the documentation to learn about the
                           structure of the Topic index.yaml file in the
                           documentation.


        Returns:
               Lab object
        """

        if labmeta:
            self.__dict__.update(**labmeta)
            self.topicpath = join(config.cursa_home,
                                  self.module,
                                  'topics',
                                  self.topic)

            self.path = join(self.topicpath,
                             'labs',
                             self.lab)

        if not labmeta:
            self.steps = []

        self.stepobjects = []
        self.src = ''

    def _create_lab_yaml_template(self, module, topic, lab, title):
        """Create a YAML file with a template that
           contains the default Lab structure

        Args:
           - module(str):  The name of the module
           - topic (str):  The name of the topic
           - lab (str):  The name of the lab
           - title (str):  The title of the lab
        """

        template = """type        : Lab
title       : {0}
courseid    :
sectionid   :
displayname :
highlight   :
        - css : school_book.css
          img : school_book.png
steps:
        - markdown :
          title    :""".format(title or '')

        utils.create_yaml_template(self.path, template)

    def _create_lab_dirs(self, modulename, topicname, labname):
        """| Create the directories for the Lab.
           | If the path has not been declared the path will be created

        Args:
           - modulename (str):  The name of the module
           - topicname (str):  The name of the topic
           - labname (str):  The name of the lab
        """

        if not hasattr(self, 'path'):
            self.path = join(config.cursa_home,
                             modulename,
                             'topics',
                             topicname,
                             'labs',
                             labname)

        directories = [join(self.path, 'html'),
                       join(self.path, 'html', 'assets'),
                       join(self.path, 'html', 'assets', 'css'),
                       join(self.path, 'html', 'assets', 'js'),
                       join(self.path, 'archives'),
                       join(self.path, 'md'),
                       join(self.path, 'img'),
                       join(self.path, 'pdf')]

        utils.make_dirs(directories)

    def _copy_assets(self):
        """| Copy CSS and JavaScript files used in the Lab.
           | The files will be copied to the assets subfolder
             of the Lab HTML folder.
        """

        if hasattr(self, 'highlight'):
            css_assets = utils.get_css_assets(extra_css=self.highlight)
            js_assets = utils.get_js_assets()
            css_dest = join(self.path,
                            'html',
                            'assets',
                            'css')

            js_dest = join(self.path,
                           'html',
                           'assets',
                           'js')

            img_assets = utils.get_img_assets(self.highlight)

            utils.copy_files(css_assets, css_dest)
            utils.copy_files(img_assets, css_dest)
            utils.copy_files(js_assets, js_dest)

    def _create_md_templates(self):
        """| Create sample markdown files for the Lab.
           | Files will contain the default template used.
           | The markdown files will take the names
               - Exercises.md
               - Objectives.md
               - RENAME-STEP.md

             and will be stored in the md folder of
             the Lab directory structure
        """

        path = join(self.path, 'md')

        utils.create_files([join(path, 'Exercises.md'),
                            join(path, 'Objectives.md'),
                            join(path, 'RENAME-STEP.md')])

    def scaffold(self, config):
        """| Orchestrates the scaffolding of the Lab.
           | This involves creating the directories for the Lab,
             creating sample markdown files for the Lab and
             creating a sample YAML file for the Lab

        Args:
           - config (dict):  config should have the
                                 structure:

                                   {
                                      | 'name':
                                      | 'title':
                                      | 'module':
                                      | 'topic':
                                    }

                     - name: The name of the lab
                     - title: The title of the lab
                     - module: Which module the lab belongs to
                     - topic: Which topic the lab belongs to
        """

        self._create_lab_dirs(config['module'],
                              config['topic'],
                              config['name'])

        self._create_md_templates()

        self._create_lab_yaml_template(config['module'],
                                       config['topic'],
                                       config['name'],
                                       config['title'])

    def _build_steps(self, css):
        """| Builds each step in the lab.
             The outcome of a call to this method should
             result in HTML output from the Markdown files

            Args:
               - css (list):  The css to use in the step
        """

        if hasattr(self, 'steps'):
            navBar = self._create_nav_bar()

            for step in self.stepobjects:
                step.build(navBar, css)

    def build(self):
        '''
        | Orchestrates the build of the Lab.
        | This involves invoking the self._create_steps(),
          and self._build_steps() methods
        | Check the documentation for a description of these
          methods

            Returns (dict):
               Lab info containing:
                           - Markdown from the first step
                           - Markdown link to the first step
                           - Markdown link to the pdf
        '''

        self._clean()
        self._copy_assets()
        self._create_steps()

        csspath = join(self.path, 'html', 'assets', 'css')
        chdir(csspath)
        css_assets = glob("*.css")
        chdir(self.path)

        self._build_steps(css_assets)
        self._create_text(css_assets)
        lab_info = self._create_lab_info()

        msg = 'Lab => {0} built'.format(self.title or self.lab)
        utils.log(msg)

        return lab_info

    def _clean(self):
        '''
        | Delete any files from a previous build of the lab
        '''

        directories = [join(self.path, 'html'),
                       join(self.path, 'pdf'),
                       join(self.path, 'html', 'assets', 'css'),
                       join(self.path, 'html', 'assets', 'js')]

        utils.clean_directories(directories)

    def _create_lab_info(self):
        '''
        | Creates the lab info

            Returns (dict):
               Lab info containing:
                           - Markdown from the first step
                           - Markdown link to the first step
                           - Markdown link to the pdf
        '''

        first_step_md = ''.join([self.path,
                                 sep,
                                 'md',
                                 sep,
                                 self.stepobjects[0].markdown,
                                 '.md'])

        with open(first_step_md) as f:
            md = f.read()

        path_to_first_step = ''.join([self.path,
                                      sep,
                                      'html',
                                      sep,
                                      self.stepobjects[0].markdown,
                                      '.html'])

        path_to_pdf = ''.join([self.path,
                              sep,
                              'pdf',
                              sep,
                              self.title or self.lab,
                              '.pdf'])

        lab_info = '\n\n'.join([md,
                            '[{0}]({1})'.format(self.title or self.lab,
                                                path_to_first_step),
                            '[{0}]({1})'.format(self.title or self.lab,
                                                path_to_pdf)])

        return lab_info

    def _get_mdfile_names(self):
        """Gathers markdown files in the md directory
           and uses the meta data from the files to create
           the Step meta data

           .. note::
               Method only to be used when creating output
               using the prefix approach.
           ..

           Returns:
               List (String) containing the markdown file names in the
               md folder of this lab
        """

        path = join(abspath(self.path), 'md')

        mdFiles = sorted(utils.gather_file_names(path))
        return mdFiles

    def _create_steps(self):
        """Creates the Step objects
        """

        if len(self.steps) == 0:
            self.steps = self._get_mdfile_names()

            for f in self.steps:
                self.stepobjects.append(Step(filename=f, labpath=self.path))

            self.stepobjects.sort(key=lambda step: step.position)
        else:
            for step in self.steps:
                self.stepobjects.append(Step(stepmeta=step, labpath=self.path))

    def _create_nav_bar(self):
        """Creates the HTML Navigation Bar for the Lab.
           Polls each Step in the Lab for the step list element.

            Returns:
               String representation of the Navigation Bar
               or empty string on fail
        """

        try:
            li = ''.join([step.nav_element for step in self.stepobjects])

            path_to_topic_home = join(self.topicpath,
                                      'index.html')

            return (u'<div class="navbar navbar-fixed-top">'
                    '<div class="clearfix background-white">'
                    '<span id="title" class="pull-right">{0}</span>'
                    '</div>'
                    '<div class="navbar-inner">'
                    '<div class="container-fluid">'
                    '<ul class="nav">'
                    '{1}'
                    '</ul>'
                    '<p class="navbar-text pull-right">'
                    '<a href="{2}">{3}</a></p>'
                    '</div>'
                    '</div>'
                    '</div>').format(self.title,
                                     li,
                                     path_to_topic_home,
                                     self.topic)
        except:
            return ''

    def _create_text(self, css):
        '''| Creates a PDF file that contains the combined content
             of all the steps in a lab
           | This method uses the generate module to create the PDF file
        '''

        lab_params = {
                      'title': self.title or self.lab,
                      'steps': self.steps,
                      'labpath': self.path,
                      'css': css
                      }

        generate(labparams=lab_params)

    def push(self):
        """| Sends the lab to a Moodle LMS using a Web service.
           | The lab is sent as three resources.
           | The HTML steps, the PDF and a Label consisting of the objectives
             Markdown.
           | To use this functionality the clarity plugin for
             Moodle must be installed in your Moodle site

            Raises:
                 ValueError
        """

        if not self.courseid:
            msg = 'No course id value defined in {0}'.format(self.lab)
            raise ValueError(msg)
        if not self.sectionid:
            msg = 'No section id value defined in {0}'.format(self.lab)
            raise ValueError(msg)

        self._pushlabel()
        self._pushsteps()
        self._pushpdf()

        msg = 'Lab => {0} pushed'.format(self.title or self.lab)
        utils.log(msg)

    def _pushlabel(self):
        """| Sends the label resource to Moodle for this lab
           | The label is usually the first step in the lab
             - the objectives.md - which outlines the lab

            Raises:
                 CursaException
            """

        first_md_file = ''.join([self.steps[0]['markdown'], '.md'])
        path_to_first_md_file = join(self.path,
                                           'md',
                                           first_md_file)

        try:
            with open(path_to_first_md_file) as f:
                labeltext = f.read()

            label_params = utils.create_push_params(self,
                                                    'label',
                                                    labeltext=labeltext,
                                                    labeltextformat='markdown')

            WebServiceClient().send_resource(label_params)

        except IOError:
            msg = 'Error opening file at {0}'.format(path_to_first_md_file)
            raise CursaException(msg)

    def _pushsteps(self):
        """| Sends the steps (HTML) version of this lab as a resource to Moodle
             including all accompanying files
        """

        tmpdir = mkdtemp()
        self._copy_steps_to_path(tmpdir)

        self._moodleify_lab(tmpdir)

        zip_file_path = make_archive(tmpdir, 'zip', root_dir=tmpdir)

        # Moodle needs to know which file in the folder
        # the hyperlink will navigate to
        mainfile = ''.join([self.steps[0]['markdown'], '.html'])

        displayname = self.displayname or self.lab
        lab_params = utils.create_push_params(self,
                                              'folder',
                                              displayname=displayname,
                                              mainfile=mainfile,
                                              mainfilepath='/html/')

        WebServiceClient().send_resource(lab_params,
                                         filepath=zip_file_path)

        archiveinfo = {
                        'zippath': zip_file_path,
                        'tmpdir': tmpdir
                      }

        utils.delete_tmpdir_and_archive(archiveinfo)

    def _copy_steps_to_path(self, path):
        """| Copies all the steps in the lab to a new path, along with all CSS,
             JS, archives, and images
        """

        dirs_to_push = [{'src': join(self.path, 'html'),
                 'dst': join(path, 'html')},
                {'src': join(self.path, 'archives'),
                 'dst': join(path, 'archives')},
                {'src': join(self.path, 'img'),
                 'dst': join(path, 'img')}]

        for each_dir in dirs_to_push:
            copy_tree(each_dir['src'], each_dir['dst'])

    def _moodleify_lab(self, path):
        """| Configures each step in the Lab for being pushed to Moodle
           | This involves changing local navigation links to navigation links
             that will work in the Moodle environment
           | The moodlyify() method of each step in the lab is invoked
           | Check the documentation for a description of this method
        """

        self._create_steps()

        for step in self.stepobjects:
            step.moodleify(path, self.topicpath, self.topic,
                           self.courseid, self.sectionid)

    def _pushpdf(self):
        """| Sends the PDF version of this lab as a resource to Moodle
        """

        pdffile = ''.join([self.path,
                           sep,
                           'pdf',
                           sep,
                           self.title or self.lab,
                           '.pdf'])

        displayname = self.title or self.lab
        pdf_params = utils.create_push_params(self,
                                              'file',
                                              displayname=displayname)

        WebServiceClient().send_resource(pdf_params, filepath=pdffile)
