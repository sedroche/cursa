'''
Created on Oct 20, 2012

Author: John Roche
'''
from lab import Lab
from os.path import join
from os import sep, chdir
import utils
from generator import generate
from yaml import load
from webserviceclient import WebServiceClient
from errorhandling.cursa_exceptions import CursaException
from glob import glob
import config


class Topic(object):
    '''
    | The Topic class is responsible for creating the file structure for the
      topic and the orchestration of a build of a Topic
    | A Topic consists of a collection of Labs and is responsible for the
      management of the Labs in the TOPIC.
    '''

    def __init__(self, topicmeta=None):
        """
        Kwargs:
           topicmeta (dict): Contains the meta data to create the Topic Object
                             Meta data will be read from the index.yaml file
                             for the topic.
                             Check the documentation to learn about the
                             structure of the Topic index.yaml file in the
                             documentation.

        Returns:
               Topic object
        """

        if topicmeta:
            self.__dict__.update(**topicmeta)
            self.path = join(config.cursa_home,
                             self.module,
                             'topics',
                             self.topic)

        self.lab_objects = []

    def _create_topic_dirs(self, modulename, topicname, rich):
        """Create the directories for the topic.
        """

        if not hasattr(self, 'path'):
            self.path = join(config.cursa_home,
                             modulename,
                             'topics',
                             topicname)

        directories = [join(self.path, 'presentations'),
                       join(self.path, 'presentations', 'md'),
                       join(self.path, 'presentations', 'pdf'),
                       join(self.path,
                            'presentations',
                            'html',
                            'assets',
                            'css'),
                       join(self.path,
                            'presentations',
                            'html',
                            'assets',
                            'js'),
                       join(self.path, 'assets'),
                       join(self.path, 'assets', 'css'),
                       join(self.path, 'assets', 'js'),
                       join(self.path, 'labs')]

        utils.make_dirs(directories)

        if rich:
            rich_dirs = [join(self.path, 'img'),
                         join(self.path, 'archive'),
                         join(self.path, 'media')]

            utils.make_dirs(rich_dirs)

    def _copy_assets(self):
        """| Copy CSS and JavaScript files used in the Topic.
           | The files will be copied to the assets subfolder
             of the Topic HTML folder.
        """

        css_assets = utils.get_css_assets()
        js_assets = utils.get_js_assets()
        css_dest = join(self.path,
                        'assets',
                        'css')

        js_dest = join(self.path,
                       'assets',
                       'js')

        utils.copy_files(css_assets, css_dest)
        utils.copy_files(js_assets, js_dest)

    def _create_topic_yaml_template(self, module, topic, title):
        """Create a YAML file with a template that
           contains the default Topic structure

            Args:
               - module(str):  The name of the module
               - topic (str):  The name of the topic
               - title (str):  The title of the Topic
        """

        template = """type        : Topic
title    : {0}
courseid    :
sectionid   :
presentations :
    - markdown  :
      title     :
prestheme   :
        style : web-2.0.css
        transition : horizontal-slide.css
preshighlight   :
        css : school_book.css
        img : school_book.png
labs    :
    - folder :
""".format(title or '')

        utils.create_yaml_template(self.path, template)

    def _create_lab_objects(self):
        """Creates the Lab objects from the meta data which should have been
           configured in the index.yaml file for this topic.

        Raises:
             CursaException
        """

        if hasattr(self, 'labs'):
            for lab in self.labs:
                if lab['folder']:
                    path = join(self.path,
                                'labs',
                                lab['folder'])
                    indexpath = join(path,
                                     'index.yaml')

                    try:
                        with open(indexpath, 'r') as labindex:
                            labmeta = load(labindex)
                            courseinfo = utils.create_course_info(path)
                            labmeta.update(courseinfo)
                            self.lab_objects.append(Lab(labmeta=labmeta))
                    except IOError:
                        msg = 'Error opening file at {0}'.format(indexpath)
                        raise CursaException(msg)

    def _scaffold_labs(self):
        """| Orchestrates the scaffolding of each lab in the Topic.
           | This involves invoking the scaffold() method of each lab.
             Check the documentation for a description of the
             Lab.scaffold() method
        """

        for lab_object in self.lab_objects:
            lab_object.scaffold()

    def _build_labs(self):
        """| Orchestrates the build of each lab in the Topic.
           | This involves invoking the build() method of each lab.
             Check the documentation for a description of the
             Lab.build() method
           | Each lab object has the lab.src attribute set to
             point to the first html page in lab
        """

        for lab_object in self.lab_objects:
            lab_object.info = lab_object.build()

    def build(self):
        """| Orchestrates the build of a full Topic.
           | This involves invoking the self._create_lab_objects(),
             self._build_labs(), self._create_index() and
             self._presentation methods
             Check the documentation for a description of these
             methods
        """

        self._clean()
        self._create_lab_objects()
        self._build_labs()
        self._copy_assets()
        self._presentation()
        self._create_index()

        msg = 'Topic => {0} built\n'.format(self.title or self.topic)
        utils.log(msg)

    def _clean(self):
        '''
        | Delete any files from a previous build of the lab
        '''

        directories = [join(self.path, 'presentations', 'html'),
                       join(self.path,
                            'presentations',
                            'html',
                            'assets',
                            'css'),
                       join(self.path,
                            'presentations',
                            'html',
                            'assets',
                            'js'),
                       join(self.path, 'presentations', 'pdf')]

        utils.clean_directories(directories)

    def scaffold(self, config):
        """| Orchestrates the scaffolding of the Topic.
           | This involves creating the directories for the Topic,
             and creating a sample YAML file for the Topic

        Args:
           - config (dict):  config should have the
                                 structure:

                                   {
                                      | 'name':
                                      | 'title':
                                      | 'module':
                                      | 'rich':
                                    }

                     - name: The name of the lab
                     - title: The title of the lab
                     - module: Which module the lab belongs to
                     - rich: Whether the topic index.html will have images and
                             multimedia content
        """

        self._create_topic_dirs(config['module'],
                                config['name'],
                                config['rich'])

        self._create_topic_yaml_template(config['module'],
                                         config['name'],
                                         config['title'])

        self._create_topic_md()

    def _create_topic_md(self):
        '''| Creates the index.md file that will be used
             to generate the index.html interface to the Topic
           | This method uses the generate module to create the html page
        '''

        filepath = join(self.path, 'index.md')
        utils.create_file(filepath)

    def _create_pres_info(self):
        '''| Creates a Markdown string that has the links
             to the HTML presentation and the PDF presentation

            Returns:
               String containing Markdown links to the HTML presentations and
               the PDF presentations or an empty string if there are no
               presentations in the topic
        '''

        presinfo = ''
        if hasattr(self, 'presentations'):
            for pres in self.presentations:
                title = pres['title'] or pres['markdown']
                if(title):
                    preslink = ''.join([self.path,
                                        sep,
                                        'presentations',
                                        sep,
                                        'html',
                                        sep,
                                        title,
                                        '.html'])

                    pres_text_link = ''.join([self.path,
                                              sep,
                                              'presentations',
                                              sep,
                                              'pdf',
                                              sep,
                                              title,
                                              '.pdf'])

                    presinfo = '\n\n'.join(['[{0}]({1})'.format(title,
                                                                preslink),
                                            '[{0}]({1})'.format(title,
                                                                pres_text_link)])
        return presinfo

    def _create_index(self):
        '''| Creates the index.html page that will be the
             interface to the topic.
           | This method uses the generate module to create the html page
        '''

        topicinfo = ''
        presinfo = self._create_pres_info()

        topicinfo = '\n'.join([topicinfo,
                               presinfo])

        for lab_object in self.lab_objects:
            topicinfo = '\n'.join([topicinfo,
                                   lab_object.info])
        topic_params = {
                        'category': 'index',
                        'title': self.title,
                        'content': join(self.path, 'index.md'),
                        'topicpath': self.path,
                        'topicinfo': topicinfo
                        }

        generate(topicparams=topic_params)

    def _presentation(self):
        '''| Creates a HTML presentation of the markdown input
           | This method uses the generate module to create the presentation
        '''

        if hasattr(self, 'presentations'):
            if(self.presentations[0]['markdown']):
                self._copy_pres_assets()

                csspath = join(self.path, 'presentations', 'html', 'assets', 'css')
                chdir(csspath)
                css_assets = glob("*.css")
                chdir(self.path)

                for pres in self.presentations:
                    topic_params = {
                                    'category': 'pres',
                                    'title': pres['title'] or pres['markdown'],
                                    'content': ''.join([pres['markdown'], '.md']),
                                    'prespath': join(self.path, 'presentations'),
                                    'css': css_assets
                                    }

                    generate(topicparams=topic_params)
                    self._pres_text(topic_params)
                    msg = 'Presentation => {0} built'.format(pres['title'])
                    utils.log(msg)

    def _get_pres_css_assets(self):
        """| Creates a List of the CSS assets needed for a
             presentation

            Returns:
                   List of CSS assets
        """

        core_css = join(config.cursa_path,
                        'deck.core.css')

        bootstrap_css = join(config.cursa_path,
                             'bootstrap.min.css')

        goto_css = join(config.cursa_path,
                        'deck.goto.css')

        menu_css = join(config.cursa_path,
                        'deck.menu.css')

        navigation_css = join(config.cursa_path,
                              'deck.navigation.css')

        status_css = join(config.cursa_path,
                          'deck.status.css')

        hash_css = join(config.cursa_path,
                        'deck.hash.css')

        scale_css = join(config.cursa_path,
                         'deck.scale.css')

        highlight_css = join(config.cursa_path,
                             self.preshighlight['css'])

        highlight_img = ''
        if self.preshighlight['img']:
            highlight_img = join(config.cursa_path,
                                 self.preshighlight['img'])

        theme_style = join(config.cursa_path,
                           self.prestheme['style'])

        theme_transition = join(config.cursa_path,
                                self.prestheme['transition'])

        assets = [core_css,
                  bootstrap_css,
                  goto_css,
                  menu_css,
                  navigation_css,
                  status_css,
                  hash_css,
                  scale_css,
                  highlight_css,
                  theme_style,
                  theme_transition]

        if highlight_img:
            assets.append(highlight_img)

        return assets

    def _get_pres_js_assets(self):
        """| Creates a List of the Javascript assets needed for a
             presentation

            Returns:
                   List of Javascript assets
        """

        modernizr = join(config.cursa_path,
                         'modernizr.custom.js')

        jquery_js = join(config.cursa_path,
                         'jquery-1.7.2.min.js')

        core_js = join(config.cursa_path,
                       'deck.core.js')

        goto_js = join(config.cursa_path,
                       'deck.goto.js')

        menu_js = join(config.cursa_path,
                       'deck.menu.js')

        navigation_js = join(config.cursa_path,
                             'deck.navigation.js')

        status_js = join(config.cursa_path,
                         'deck.status.js')

        hash_js = join(config.cursa_path,
                       'deck.hash.js')

        scale_js = join(config.cursa_path,
                        'deck.scale.js')

        highlight_js = join(config.cursa_path,
                             'highlight.pack.js')

        return [modernizr,
                jquery_js,
                core_js,
                goto_js,
                menu_js,
                navigation_js,
                status_js,
                hash_js,
                scale_js,
                highlight_js]

    def _copy_pres_assets(self):
        """| Copy CSS and JavaScript files used in the HTML presentations
           | The files will be copied to the assets subfolder
             of the presentation HTML folder.
        """

        css_assets = self._get_pres_css_assets()
        js_assets = self._get_pres_js_assets()

        css_dest = join(self.path,
                        'presentations',
                        'html',
                        'assets',
                        'css')

        js_dest = join(self.path,
                       'presentations',
                       'html',
                       'assets',
                       'js')

        utils.copy_files(css_assets, css_dest)
        utils.copy_files(js_assets, js_dest)

    def _pres_text(self, pres_meta):
        '''| Creates a PDF presentation of the markdown input
           | This method uses the generate module to create the PDF
             presentation

            Args:
               - pres_meta (dict):  Contains the meta data to create the
                                    presentation text
        '''

        pres_meta['category'] = 'pres_text'
        pres_meta['css'] = ['deck.core.css',
                            self.preshighlight['css'],
                            self.prestheme['style']]

        generate(topicparams=pres_meta)

    def push(self):
        """| Sends the Topic to a Moodle LMS using a Web service.
           | The HTML presentation, the PDF version of the presentation
             and and all the labs are sent.
           | To use this functionality the clarity plugin for
             Moodle must be installed in your Moodle site

            Raises:
                 ValueError
        """

        if not self.courseid:
            msg = 'No course id value defined in {0}'.format(self.topic)
            raise ValueError(msg)
        if not self.sectionid:
            msg = 'No section id value defined in {0}'.format(self.topic)
            raise ValueError(msg)

        self._push_index()

        if hasattr(self, 'presentations'):
            if(self.presentations[0]['markdown']):
                for pres in self.presentations:
                    self._push_presentation(pres)
                    self._push_pdf_presentation(pres)
        self._create_lab_objects()
        self._push_labs()

        msg = 'Topic => {0} pushed\n'.format(self.title or self.topic)
        utils.log(msg)

    def _push_index(self):
        """| Sends the Topic outline to Moodle.
           | The outline is sent as a label resource.
           | The label content is specified the Topic index.md file
        """

        topic_params = {
                        'category': 'label',
                        'content': join(self.path, 'index.md')
                        }

        label_html = generate(topicparams=topic_params)
        if(label_html):
            label_params = utils.create_push_params(self,
                                                    'label',
                                                    labeltext=label_html,
                                                    labeltextformat='html')

            WebServiceClient().send_resource(label_params)

    def _push_presentation(self, pres):
        """| Sends a HTML presentation as a resource to Moodle
        """

        prespath = join(self.path, 'presentations')
        archiveinfo = utils.make_tmpdir_with_archive(prespath)

        # Moodle needs to know which file in the folder
        # the hyperlink will navigate to
        mainfile = ''.join([pres['title'],
                             '.html'])

        pres_params = utils.create_push_params(self,
                                               'folder',
                                               displayname=pres['title'],
                                               mainfile=mainfile,
                                               mainfilepath='/html/')

        WebServiceClient().send_resource(pres_params,
                                         filepath=archiveinfo['zippath'])

        utils.delete_tmpdir_and_archive(archiveinfo)

    def _push_pdf_presentation(self, pres):
        """| Sends a PDF presentation as a resource to Moodle
        """

        pdffile = ''.join([self.path,
                           sep,
                           'presentations',
                           sep,
                           'pdf',
                           sep,
                           pres['title'],
                           '.pdf'])

        pdf_params = utils.create_push_params(self,
                                              'file',
                                              displayname=pres['title'])

        WebServiceClient().send_resource(pdf_params, filepath=pdffile)

    def _push_labs(self):
        """| Orchestrates the push of each lab in the Topic.
           | This involves invoking the push() method of each lab.
             Check the documentation for a description of the
             Lab.push() method
        """

        for lab_object in self.lab_objects:
            lab_object.push()
