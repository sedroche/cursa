'''
Created on Oct 20, 2012

Author: John Roche
'''
import unittest
from dom.lab import Lab
from dom.step import Step
from dom.utils import make_dir, create_files, create_file
from shutil import rmtree
from yaml import load
from os import listdir
from os.path import abspath, dirname, pardir, exists, join, isfile
from dom.webserviceclient import WebServiceClient
from errorhandling.cursa_exceptions import CursaException
from tempfile import mkdtemp
import config


class testLab(unittest.TestCase):

    def setUp(self):
        config.cursa_home = abspath(join(dirname(__file__),
                                  pardir,
                                  pardir,
                                  'test_data'
                                  )
                            )

        template = """type        : Lab
title       : testLab labmeta object
module      : test_module
topic       : test_topic
courseid    : 7
sectionid   : 3
displayname :
lab         : test_lab
highlight   :
          - css : school_book.css
            img : school_book.png
steps:
        - markdown : Exercises
          title    : Exercises
        - markdown : Objectives
          title    : Objectives
        - markdown : RENAME-STEP
          title    : RENAME-STEP"""

        labmeta = load(template)
        self.testlab = Lab(labmeta=labmeta)

    def tearDown(self):
        if exists(config.cursa_home):
            rmtree(config.cursa_home)

        self.testlab = None

    def test_lab_Init(self):
        self.assertEqual(self.testlab.title, 'testLab labmeta object')
        self.assertEqual(self.testlab.module, 'test_module')
        self.assertEqual(self.testlab.topic, 'test_topic')
        self.assertEqual(self.testlab.lab, 'test_lab')
        self.assertEqual(3, len(self.testlab.steps))

        for step in self.testlab.steps:
            self.assertIsNotNone(step.get('markdown'))
            self.assertIsNotNone(step.get('title'))

    def test_create_lab_yaml_template(self):
        self.testlab._create_lab_dirs(self.testlab.module,
                                      self.testlab.topic,
                                      self.testlab.lab)

        self.testlab._create_lab_yaml_template(self.testlab.module,
                                               self.testlab.topic,
                                               self.testlab.lab,
                                               self.testlab.title)
        exists(join(self.testlab.path, 'index.yaml'))

    def test_create_lab_dirs(self):
        directories = [join(config.cursa_home,
                            'test_module',
                            'topics',
                            'test_topic',
                            'labs',
                            'test_lab',
                            'html'),
                       join(config.cursa_home,
                            'test_module',
                            'topics',
                            'test_topic',
                            'labs',
                            'test_lab',
                            'html',
                            'assets'),
                     join(config.cursa_home,
                            'test_module',
                            'topics',
                            'test_topic',
                            'labs',
                            'test_lab',
                            'html',
                            'assets',
                            'css'),
                     join(config.cursa_home,
                            'test_module',
                            'topics',
                            'test_topic',
                            'labs',
                            'test_lab',
                            'html',
                            'assets',
                            'js'),
                       join(config.cursa_home,
                           'test_module',
                           'topics',
                           'test_topic',
                           'labs',
                           'test_lab',
                           'archives'),
                       join(config.cursa_home,
                           'test_module',
                           'topics',
                           'test_topic',
                           'labs',
                           'test_lab',
                           'md'),
                       join(config.cursa_home,
                           'test_module',
                           'topics',
                           'test_topic',
                           'labs',
                           'test_lab',
                           'img'),
                       join(config.cursa_home,
                           'test_module',
                           'topics',
                           'test_topic',
                           'labs',
                           'test_lab',
                           'pdf')]

        self.testlab._create_lab_dirs('test_module', 'test_topic', 'test_lab')

        for directory in directories:
            self.assertTrue(exists(directory))

    def test_create_md_templates(self):
        path = join(config.cursa_home,
                    'test_module',
                    'topics',
                    'test_topic',
                    'labs',
                    'test_lab',
                    'md')

        make_dir(path)

        testTemplateArray = ['Exercises.md',
                             'Objectives.md',
                             'RENAME-STEP.md']

        self.testlab._create_md_templates()

        for filePath in testTemplateArray:
            self.assertTrue(exists(join(path, filePath)))

    def test_scaffold_lab(self):
        test_config = {
                          'name': 'test_lab',
                          'title': '',
                          'module': 'test_module',
                          'topic': 'test_topic'
                      }

        self.testlab.scaffold(test_config)

        directories = [join(config.cursa_home,
                            'test_module',
                            'topics',
                            'test_topic',
                            'labs',
                            'test_lab',
                            'html'),
                       join(config.cursa_home,
                           'test_module',
                           'topics',
                           'test_topic',
                           'labs',
                           'test_lab',
                           'archives'),
                       join(config.cursa_home,
                           'test_module',
                           'topics',
                           'test_topic',
                           'labs',
                           'test_lab',
                           'md'),
                       join(config.cursa_home,
                           'test_module',
                           'topics',
                           'test_topic',
                           'labs',
                           'test_lab',
                           'img'),
                       join(config.cursa_home,
                           'test_module',
                           'topics',
                           'test_topic',
                           'labs',
                           'test_lab',
                           'pdf')]

        for directory in directories:
            self.assertTrue(exists(directory))

        exists(join(self.testlab.path, 'index.yaml'))

        testTemplateArray = ['Exercises.md',
                             'Objectives.md',
                             'RENAME-STEP.md']

        for filePath in testTemplateArray:
            self.assertTrue(exists(join(self.testlab.path,
                                        'md',
                                        filePath)))

    def test_copy_assets(self):
        self.testlab._create_lab_dirs(self.testlab.module,
                                      self.testlab.topic,
                                      self.testlab.lab)
        self.testlab._copy_assets()

    def test_build_steps(self):
        self.testlab._create_lab_dirs(self.testlab.module,
                                      self.testlab.topic,
                                      self.testlab.lab)

        self.testlab._create_lab_yaml_template(self.testlab.module,
                                               self.testlab.topic,
                                               self.testlab.lab,
                                               self.testlab.title)
        self.testlab._create_md_templates()

        self.assertEquals(3, len(self.testlab.steps))
        self.assertEquals(0, len(self.testlab.stepobjects))

        self.testlab._create_steps()

        css = '<link rel="stylesheet" href="path/" type="text/css">'
        self.testlab._build_steps(css)

        self.assertEqual(3, len(self.testlab.stepobjects))
        for i in range(0, len(self.testlab.stepobjects)):
            self.assertEqual(self.testlab.stepobjects[i].__class__, Step)

        path = join(self.testlab.path, 'html')
        htmlfiles = [f for f in listdir(path) if isfile(join(path, f))]

        self.assertEquals(3, len(htmlfiles))

        test_html_array = ['Exercises.html',
                           'Objectives.html',
                           'RENAME-STEP.html']

        for html in test_html_array:
            self.assertTrue(html in htmlfiles)

    def test_get_mdfiles(self):
        path = join(config.cursa_home,
                    'test_module',
                    'topics',
                    'test_topic',
                    'labs',
                    'test_lab',
                    'md')

        make_dir(path)
        self.testlab._create_md_templates()

        fileNameList = self.testlab._get_mdfile_names()

        testTemplateArray = ['Exercises.md',
                             'Objectives.md',
                             'RENAME-STEP.md']

        for name in testTemplateArray:
            self.assertTrue(name in fileNameList)

    def test_create_steps_md(self):
        testlab = Lab()

        testlab._create_lab_dirs('test_module',
                                'test_topic',
                                'test_lab')

        create_files([join(self.testlab.path,
                                 'md',
                                 '3.Exercises.md'),
                            join(self.testlab.path,
                                 'md',
                                 '1.Objectives.md'),
                            join(self.testlab.path,
                                 'md',
                                 '2.RENAME-STEP.md')])

        testlab._create_steps()

        self.assertEqual(3, len(testlab.steps))

        for i in range(0, len(testlab.steps)):
            self.assertEqual(testlab.stepobjects[i].__class__, Step)
            self.assertEqual(testlab.stepobjects[i].position, str(i + 1))

    def test_create_steps_yaml(self):
        self.testlab._create_lab_dirs(self.testlab.module,
                                     self.testlab.topic,
                                     self.testlab.lab)

        self.assertEquals(3, len(self.testlab.steps))
        self.assertEquals(0, len(self.testlab.stepobjects))

        self.testlab._create_steps()

        self.assertEqual(3, len(self.testlab.steps))

        for i in range(0, len(self.testlab.steps)):
            self.assertEqual(self.testlab.stepobjects[i].__class__, Step)

    def test_create_nav_bar(self):
        self.testlab._create_steps()

        result = self.testlab._create_nav_bar()
        path_to_topic_home = join(self.testlab.topicpath,
                                  'index.html')

        expectedResult = (u'<div class="navbar navbar-fixed-top">'
                          '<div class="clearfix background-white">'
                          '<span id="title" class="pull-right">{0}</span>'
                          '</div>'
                          '<div class="navbar-inner">'
                          '<div class="container-fluid">'
                          '<ul class="nav">'
                          '<li class="Exercises">'
                          '<a href="Exercises.html">Exercises</a></li>'
                          '<li class="Objectives">'
                          '<a href="Objectives.html">Objectives</a></li>'
                          '<li class="RENAME-STEP">'
                          '<a href="RENAME-STEP.html">RENAME-STEP</a></li>'
                          '</ul>'
                          '<p class="navbar-text pull-right">'
                          '<a href="{1}">{2}</a></p>'
                          '</div>'
                          '</div>'
                          '</div>').format(self.testlab.title,
                                           path_to_topic_home,
                                           self.testlab.topic)

        self.assertEqual(expectedResult, result)

    def test_pushpdf(self):
        # Monkey patch the WebServiceClient.send_resource function
        initialfunc = WebServiceClient.send_resource
        WebServiceClient.send_resource = lambda ob, wbs_params, filepath=None: True
        self.testlab._pushpdf()
        WebServiceClient.send_resource = initialfunc

    def test_pushlabel_success(self):
        # Monkey patch the WebServiceClient.send_resource function
        initialfunc = WebServiceClient.send_resource
        WebServiceClient.send_resource = lambda ob, wbs_params, filepath=None: True

        first_md_file = ''.join([self.testlab.steps[0]['markdown'], '.md'])

        path_to_first_md_file = join(self.testlab.path,
                                     'md',
                                     first_md_file)
        self.testlab._create_lab_dirs('test_module', 'test_topic', 'test_lab')
        create_file(path_to_first_md_file)

        self.testlab._pushlabel()

        WebServiceClient.send_resource = initialfunc

    def test_pushlabel_IO_fail(self):
        with self.assertRaises(CursaException) as context:
            self.testlab._pushlabel()

        first_md_file = ''.join([self.testlab.steps[0]['markdown'], '.md'])
        path_to_first_md_file = join(self.testlab.path,
                                     'md',
                                     first_md_file)
        expected_msg = 'Error opening file at {0}'.format(path_to_first_md_file)
        self.assertEqual(context.exception.message, expected_msg)

    def test_pushsteps(self):
        # Monkey patch the WebServiceClient.send_resource function
        initialfunc = WebServiceClient.send_resource
        WebServiceClient.send_resource = lambda ob, wbs_params, filepath=None: True

        self.testlab._create_lab_dirs('test_module', 'test_topic', 'test_lab')
        self.testlab._create_md_templates()
        self.testlab.build()

        self.testlab._pushsteps()

        WebServiceClient.send_resource = initialfunc

    def test_copy_steps_to_path(self):
        self.testlab._create_lab_dirs('test_module', 'test_topic', 'test_lab')
        self.testlab._create_md_templates()
        self.testlab._copy_assets()
        self.testlab.build()

        tmpdir = mkdtemp()
        self.testlab._copy_steps_to_path(tmpdir)

        dirs = [join(tmpdir, 'html', 'assets', 'css'),
                join(tmpdir, 'html', 'assets', 'css'),
                join(tmpdir, 'img'),
                join(tmpdir, 'archives')]

        for each_dir in dirs:
            self.assertTrue(exists(each_dir))

        files = [join(tmpdir, 'html', 'Exercises.html'),
                 join(tmpdir, 'html', 'Objectives.html'),
                 join(tmpdir, 'html', 'RENAME-STEP.html'),
                 join(tmpdir, 'html', 'assets', 'css', 'bootstrap.min.css'),
                 join(tmpdir, 'html', 'assets', 'css', 'bootstrap-responsive.min.css'),
                 join(tmpdir, 'html', 'assets', 'css', 'cursa.css'),
                 join(tmpdir, 'html', 'assets', 'css', 'school_book.css'),
                 join(tmpdir, 'html', 'assets', 'css', 'school_book.png'),
                 join(tmpdir, 'html', 'assets', 'js', 'bootstrap.min.js'),
                 join(tmpdir, 'html', 'assets', 'js', 'highlight.pack.js'),
                 join(tmpdir, 'html', 'assets', 'js', 'jquery-1.7.2.min.js')]

        for each_file in files:
            self.assertTrue(exists(each_file))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
