'''
Created on Jan 16, 2013

Author: John Roche
'''

import utils
from generator import generate
from os.path import join
from yaml import load
from topic import Topic
from errorhandling.cursa_exceptions import CursaException
import config


class Module(object):
    '''
    | The Module class is responsible for creating the file structure for a
      Module and the orchestration of a build of a Module.
    | A Module consists of a collection of Topics and is responsible for the
      management of the Topics in the Module.
    '''

    def __init__(self, modulemeta=None):
        """
        Kwargs:
           modulemeta (dict): Contains the meta data to create the Topic Object
                              Meta data will be read from the index.yaml file
                              for the Lab.
                              Check the documentation to learn about the
                              structure of the Topic index.yaml file in the
                              documentation.


        Returns:
               Module object
        """

        if modulemeta:
            self.__dict__.update(**modulemeta)
            self.path = join(config.cursa_home, self.module)

        self.topic_objects = []

    def _create_module_dirs(self, modulename):
        """| Create the directories for the Module.
           | If the path has not been declared the path will be created

        Args:
           - modulename (str):  The name of the module
        """

        if not hasattr(self, 'path'):
            self.path = join(config.cursa_home,
                             modulename)

        directories = [join(self.path, 'topics'),
                       join(self.path, 'assets', 'css'),
                       join(self.path, 'assets', 'js')]

        utils.make_dirs(directories)

    def _copy_assets(self):
        """| Copy CSS and JavaScript files used in the Module.
           | The files will be copied to the module assets folder
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

    def _create_module_yaml_template(self, modulename, title):
        """Create a YAML file with a template that
           contains the default Topic structure

        Args:
           - module(str):  The name of the module
           - title (str):  The title of the module
        """

        template = """type        : Module
title    : {0}
topics   :
    - folder  :
""".format(title or '')

        utils.create_yaml_template(self.path, template)

    def _create_topic_objects(self):
        """Creates the Topic objects from the meta data which should have been
           configured in the index.yaml file

        Raises:
             CursaException
        """

        if hasattr(self, 'topics'):
            for topic in self.topics:
                path = join(self.path,
                            'topics',
                            topic['folder'])

                indexpath = join(path,
                                 'index.yaml')
                try:
                    with open(indexpath, 'r') as topicindex:
                        topic_meta = load(topicindex)
                        courseinfo = utils.create_course_info(path)
                        topic_meta.update(courseinfo)

                        self.topic_objects.append(Topic(topicmeta=topic_meta))
                        topic['title'] = topic_meta['title']
                except IOError:
                    msg = 'Error opening file at {0}'.format(indexpath)
                    raise CursaException(msg)

    def _create_topic_links(self):
        '''| Creates a HTML Hypertext link for each topic in the module.
             The links will be displayed in the index.html page created
             in topic._create_index().
        '''

        list_elements = u''
        link_template = (u'<li class="border emmargin moduleli">'
                         '<div class="margin">'
                         '<h3>'
                         '<a href="{0}">{1}</a>'
                         '</h3>'
                         '</div>'
                         '</li>')

        for topic in self.topics:
            href = join(self.path,
                        'topics',
                        topic['folder'],
                        'index.html')
            new_list_element = link_template.format(href, topic['title'])
            list_elements = ''.join([list_elements,
                                    new_list_element])

        containing_div = (u'<div class="row-fluid">'
                          '<ul class="no-bullet">'
                          '{0}'
                          '</ul>'
                          '</div>').format(list_elements)

        return containing_div

    def _create_index(self):
        '''| Creates the index.html page that will be the
             interface to the module.
           | This method uses the generate module to create the html page
        '''

        module_params = {
                         'title': self.title,
                         'modulepath': self.path,
                         'topiclinks': self._create_topic_links()
                         }

        generate(moduleparams=module_params)

    def _build_topics(self):
        """| Orchestrates the build of each Topic in the Module.
           | This involves invoking the build() method of each topic.
             Check the documentation for a description of the
             Topic.build() method
        """

        for topic_object in self.topic_objects:
            topic_object.build()

    def _push_topics(self):
        """| Orchestrates the build of each Topic in the Module.
           | This involves invoking the build() method of each topic.
             Check the documentation for a description of the
             Topic.build() method
        """

        for topic_object in self.topic_objects:
            topic_object.push()

    def scaffold(self, config):
        """| Orchestrates the scaffolding of the Module.
           | This involves creating the directories for the Module,
             and creating a sample YAML file for the Module

        Args:
           - config (dict):  config should have the
                                 structure:

                                   {
                                      | 'name':
                                      | 'title':
                                   }

                     - name: The name of the lab
                     - title: The title of the lab
        """

        self._create_module_dirs(config['name'])
        self._copy_assets()
        self._create_module_yaml_template(config['name'],
                                          config['title'])

    def build(self):
        """| Orchestrates the build of a full Module.
           | This involves invoking the self.create_topic_objects(),
             self.build_topics() and self.create_index() methods
           |  Check the documentation for a description of these
             methods
        """

        self._create_topic_objects()
        self._build_topics()
        self._create_index()

        msg = 'Module => {0} built\n'.format(self.title or self.module)
        utils.log(msg)

    def push(self):
        """| Orchestrates the build of a full Module.
           | This involves invoking the self.create_topic_objects(),
             self.build_topics() and self.create_index() methods
           | Check the documentation for a description of these
             methods
        """

        self._create_topic_objects()
        self._push_topics()

        msg = 'Module => {0} pushed\n'.format(self.title or self.module)
        utils.log(msg)
