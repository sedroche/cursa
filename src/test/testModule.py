'''
Created on Jan 16, 2013

Author: John Roche
'''
import unittest
from dom.module import Module
from dom.topic import Topic
from os.path import exists, join, abspath, dirname, pardir
from yaml import load
from shutil import rmtree
from dom.utils import make_dir, create_yaml_template
from errorhandling.cursa_exceptions import CursaException
import config


class testModule(unittest.TestCase):

    def setUp(self):
        config.cursa_home = abspath(join(dirname(__file__),
                                         pardir,
                                         pardir,
                                         'test_data'
                                         )
                                    )

        template = """type        : Module
title    : Agile Software Development
module   : testm
topics   :
    - folder  : testt1
    - folder  : testt2"""

        modulemeta = load(template)
        self.testmodule = Module(modulemeta=modulemeta)

    def tearDown(self):
        if exists(config.cursa_home):
            rmtree(config.cursa_home)

        self.testmodule = None

    def test__init__(self):
        self.assertEqual(self.testmodule.title, 'Agile Software Development')
        self.assertEqual(self.testmodule.module, 'testm')
        self.assertTrue(isinstance(self.testmodule.topics, list))
        self.assertEquals(len(self.testmodule.topics), 2)

    def test_create_module_dirs(self):
        directories = [join(self.testmodule.path, 'topics'),
                       join(self.testmodule.path, 'assets'),
                       join(self.testmodule.path, 'assets', 'js'),
                       join(self.testmodule.path, 'assets', 'css')]

        self.testmodule._create_module_dirs(self.testmodule.module)

        for directory in directories:
            self.assertTrue(exists(directory))

    def test_create_module_yaml_template(self):
        path = join(self.testmodule.path)
        make_dir(path)
        self.testmodule._create_module_yaml_template(self.testmodule.module,
                                                     self.testmodule.title)
        self.assertTrue(exists(join(self.testmodule.path, 'index.yaml')))

    def test_create_topic_object_success(self):
        self.assertEquals(2, len(self.testmodule.topics))
        self.assertEquals(0, len(self.testmodule.topic_objects))

        for topic in self.testmodule.topics:
            path = join(self.testmodule.path,
                        'topics',
                        topic['folder'])
            make_dir(path)
            template = '''
            type        : Topic
            title    : 'Play: Application Structure, Forms & Models'
            module   : app-dev-modelling
            topic    : session01'''
            create_yaml_template(path, template)

        self.testmodule._create_topic_objects()
        self.assertEqual(2, len(self.testmodule.topic_objects))

        for i in range(0, len(self.testmodule.topic_objects)):
            self.assertEqual(self.testmodule.topic_objects[i].__class__, Topic)

    def test_create_topic_object_fail(self):
        with self.assertRaises(CursaException) as context:
            self.testmodule._create_topic_objects()

        indexpath = join(self.testmodule.path,
                         'topics',
                         self.testmodule.topics[0]['folder'],
                         'index.yaml')
        expected_msg = 'Error opening file at {0}'.format(indexpath)
        self.assertEqual(context.exception.message, expected_msg)

    def test_create_index(self):
        make_dir(self.testmodule.path)
        for each_topic in self.testmodule.topics:
            each_topic['title'] = 'A dummy title'

        self.testmodule._create_index()
        self.assertTrue(exists(join(self.testmodule.path, 'index.html')))

    def test_create_topic_links(self):
        for each_topic in self.testmodule.topics:
            each_topic['title'] = 'A dummy title'
        result = self.testmodule._create_topic_links()

        href1 = join(self.testmodule.path,
                     'topics',
                     self.testmodule.topics[0]['folder'],
                     'index.html')

        href2 = join(self.testmodule.path,
                     'topics',
                     self.testmodule.topics[1]['folder'],
                     'index.html')

        expected_result = (u'<div class="row-fluid">'
                           '<ul class="no-bullet">'
                           '<li class="border emmargin moduleli">'
                           '<div class="margin">'
                           '<h3>'
                           '<a href="' +
                           href1 +
                           '">A dummy title</a>'
                           '</h3>'
                           '</div>'
                           '</li>'
                           '<li class="border emmargin moduleli">'
                           '<div class="margin">'
                           '<h3>'
                           '<a href="' +
                           href2 +
                           '">A dummy title</a>'
                           '</h3>'
                           '</div>'
                           '</li>'
                           '</ul>'
                           '</div>')

        self.assertEquals(expected_result, result)

    def test_copy_assets(self):
        module = self.testmodule.module
        path = self.testmodule.path
        self.testmodule._create_module_dirs(module)

        self.testmodule._copy_assets()

        files = [join(path, 'assets', 'css', 'bootstrap.min.css'),
                 join(path, 'assets', 'css', 'bootstrap-responsive.min.css'),
                 join(path, 'assets', 'css', 'cursa.css'),
                 join(path, 'assets', 'js', 'bootstrap.min.js'),
                 join(path, 'assets', 'js', 'highlight.pack.js'),
                 join(path, 'assets', 'js', 'jquery-1.7.2.min.js')]

        for each_file in files:
            self.assertTrue(exists(each_file))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCreateModule']
    unittest.main()
