'''
Created on Oct 20, 2012

@author: john
'''
import unittest
from yaml import load
from dom.topic import Topic
from dom.utils import make_dir, create_file, create_files, make_dirs
from os.path import join, exists, abspath, dirname, pardir
from dom.lab import Lab
from shutil import rmtree
from errorhandling.cursa_exceptions import CursaException
from dom.webserviceclient import WebServiceClient
import config


class testTopic(unittest.TestCase):

    def setUp(self):
        config.cursa_home = abspath(join(dirname(__file__),
                                  pardir,
                                  pardir,
                                  'test_data'
                                  )
                            )

        template = """type        : Topic
title    : Test title
module   : testm
topic    : testt
courseid : 7
sectionid: 3
presentations :
     - title   : pres
       markdown  : pres
prestheme   :
        style : web-2.0.css
        transition : horizontal-slide.css
preshighlight   :
        css : school_book.css
        img : school_book.png
labs    :
    - folder  : testl1
    - folder  : testl2"""

        topicmeta = load(template)
        self.testTopic = Topic(topicmeta=topicmeta)

    def tearDown(self):
        if exists(config.cursa_home):
            rmtree(config.cursa_home)

        self.testTopic = None

    def test_init(self):
        self.assertEqual(self.testTopic.title, 'Test title')
        self.assertEqual(self.testTopic.module, 'testm')
        self.assertEqual(self.testTopic.topic, 'testt')

        self.assertTrue(isinstance(self.testTopic.labs, list))

    def test_create_topic_dirs(self):
        path = self.testTopic.path
        directories = [join(path, 'presentations'),
                       join(path, 'labs'),
                       join(path, 'assets', 'css'),
                       join(path, 'assets', 'js'),
                       join(path, 'presentations', 'html', 'assets', 'css'),
                       join(path, 'presentations', 'html', 'assets', 'js'),
                       join(path, 'presentations', 'md'),
                       join(path, 'presentations', 'html')]

        self.testTopic._create_topic_dirs(self.testTopic.module,
                                          self.testTopic.topic,
                                          False)

        for directory in directories:
            self.assertTrue(exists(directory))

    def test_create_topic_dirs_rich(self):
        path = self.testTopic.path
        directories = [join(path, 'presentations'),
                       join(path, 'labs'),
                       join(path, 'assets', 'css'),
                       join(path, 'assets', 'js'),
                       join(path, 'presentations', 'html', 'assets', 'css'),
                       join(path, 'presentations', 'html', 'assets', 'js'),
                       join(path, 'presentations', 'md'),
                       join(path, 'presentations', 'html'),
                       join(path, 'img'),
                       join(path, 'archive'),
                       join(path, 'media')]

        self.testTopic._create_topic_dirs(self.testTopic.module,
                                          self.testTopic.topic,
                                          True)

        for directory in directories:
            self.assertTrue(exists(directory))

    def test_copy_assets(self):
        module = self.testTopic.module
        topic = self.testTopic.topic
        path = self.testTopic.path
        self.testTopic._create_topic_dirs(module, topic, False)

        self.testTopic._copy_assets()

        files = [join(path, 'assets', 'css', 'bootstrap.min.css'),
                 join(path, 'assets', 'css', 'bootstrap-responsive.min.css'),
                 join(path, 'assets', 'css', 'cursa.css'),
                 join(path, 'assets', 'js', 'bootstrap.min.js'),
                 join(path, 'assets', 'js', 'highlight.pack.js'),
                 join(path, 'assets', 'js', 'jquery-1.7.2.min.js')]

        for each_file in files:
            self.assertTrue(exists(each_file))

    def test_create_topic_yaml_template(self):
        path = join(self.testTopic.path)
        make_dir(path)
        self.testTopic._create_topic_yaml_template(self.testTopic.module,
                                                   self.testTopic.topic,
                                                   self.testTopic.title)
        self.assertTrue(exists(join(self.testTopic.path, 'index.yaml')))

    def test_create_lab_objects_success(self):
        self.assertEquals(2, len(self.testTopic.labs))
        self.assertEquals(0, len(self.testTopic.lab_objects))

        for lab in self.testTopic.labs:
            path = join(self.testTopic.path,
                        'labs',
                        lab['folder'])
            make_dir(path)
            with open(join(path, 'index.yaml'), 'w') as f:
                sample_template = '''
                type        : Lab
                title       : testtitle
                courseid    :
                sectionid   :
                displayname :
                highlight   :
                        - css : school_book.css
                          img : school_book.png
                steps:
                        - markdown :
                          title    :
                            '''

                f.write(sample_template)

        self.testTopic._create_lab_objects()
        self.assertEqual(2, len(self.testTopic.lab_objects))

        for i in range(0, len(self.testTopic.lab_objects)):
            self.assertEqual(self.testTopic.lab_objects[i].__class__, Lab)

    def test_create_lab_objects_fail(self):
        with self.assertRaises(CursaException) as context:
            self.testTopic._create_lab_objects()

        path = join(self.testTopic.path,
                    'labs',
                    'testl1',
                    'index.yaml')
        expected_msg = 'Error opening file at {0}'.format(path)
        self.assertEqual(context.exception.message, expected_msg)

    def test_clean(self):
        module = self.testTopic.module
        topic = self.testTopic.topic
        path = self.testTopic.path
        self.testTopic._create_topic_dirs(module, topic, False)

        self.testTopic._copy_pres_assets()
        pres = [join(path, 'presentations', 'html', 'pres.html'),
                join(path, 'presentations', 'pdf', 'pres.pdf')]

        create_files(pres)

        files = [join(path, 'presentations', 'html', 'assets', 'css', 'bootstrap.min.css'),
                 join(path, 'presentations', 'html', 'assets', 'css', 'deck.core.css'),
                 join(path, 'presentations', 'html', 'assets', 'css', 'deck.goto.css'),
                 join(path, 'presentations', 'html', 'assets', 'css', 'deck.menu.css'),
                 join(path, 'presentations', 'html', 'assets', 'css', 'deck.navigation.css'),
                 join(path, 'presentations', 'html', 'assets', 'css', 'deck.status.css'),
                 join(path, 'presentations', 'html', 'assets', 'css', 'deck.hash.css'),
                 join(path, 'presentations', 'html', 'assets', 'css', 'deck.scale.css'),
                 join(path, 'presentations', 'html', 'assets', 'css', 'school_book.css'),
                 join(path, 'presentations', 'html', 'assets', 'css', 'school_book.png'),
                 join(path, 'presentations', 'html', 'assets', 'css', 'web-2.0.css'),
                 join(path, 'presentations', 'html', 'assets', 'css', 'horizontal-slide.css'),
                 join(path, 'presentations', 'html', 'assets', 'js', 'highlight.pack.js'),
                 join(path, 'presentations', 'html', 'assets', 'js', 'jquery-1.7.2.min.js'),
                 join(path, 'presentations', 'html', 'assets', 'js', 'modernizr.custom.js'),
                 join(path, 'presentations', 'html', 'assets', 'js', 'deck.core.js'),
                 join(path, 'presentations', 'html', 'assets', 'js', 'deck.goto.js'),
                 join(path, 'presentations', 'html', 'assets', 'js', 'deck.menu.js'),
                 join(path, 'presentations', 'html', 'assets', 'js', 'deck.navigation.js'),
                 join(path, 'presentations', 'html', 'assets', 'js', 'deck.status.js'),
                 join(path, 'presentations', 'html', 'assets', 'js', 'deck.hash.js'),
                 join(path, 'presentations', 'html', 'assets', 'js', 'deck.scale.js'),
                 join(path, 'presentations', 'html', 'pres.html'),
                 join(path, 'presentations', 'pdf', 'pres.pdf')]

        for each_file in files:
            self.assertTrue(exists(each_file))

        self.testTopic._clean()

        for each_file in files:
            self.assertFalse(exists(each_file))

    def test_presentation(self):
        self.testTopic._create_topic_dirs('testm', 'testt', False)
        presfile = join(self.testTopic.path,
                        'presentations',
                        'md',
                        'pres.md')

        template = '''===
                      #test slide 1
                      ===
                      ===
                      #test slide 2
                      ===
                   '''

        with open(presfile, 'w') as pres:
            pres.write(template)

        self.testTopic._presentation()

        pres_html = join(self.testTopic.path,
                         'presentations',
                         'html',
                         'pres.html')

        pres_pdf = join(self.testTopic.path,
                         'presentations',
                         'pdf',
                         'pres.pdf')

        self.assertTrue(exists(pres_html))
        self.assertTrue(exists(pres_pdf))

    def test_create_topic_md(self):
        filepath = join(self.testTopic.path, 'index.md')
        make_dir(self.testTopic.path)
        self.testTopic._create_topic_md()
        self.assertTrue(exists(filepath))

    def test_create_index(self):
        filepath = join(self.testTopic.path, 'index.md')
        make_dir(self.testTopic.path)
        create_file(filepath)

        lab = Lab()
        lab.title = 'Test lab'
        lab.info = '#The objective for the lab'

        self.testTopic.lab_objects.append(lab)

        self.testTopic._create_index()
        self.assertTrue(exists(join(self.testTopic.path, 'index.html')))

    def test_push_success(self):
        # In this test if an exception occurs, the test will fail
        # so there is no assert statement

        # Monkey patch the _push_labs function
        initial_push_labs_func = self.testTopic._push_labs()
        self.testTopic._push_labs = lambda: True

        # Monkey patch the WebServiceClient.send_resource function
        initial_send_resource_func = WebServiceClient.send_resource
        WebServiceClient.send_resource = lambda ob, wbs_params, filepath=None: True

        self.testTopic._create_topic_dirs('testm', 'testt', False)
        index = join(self.testTopic.path,
                     'index.md')
        with open(index, 'w') as f:
            f.write('##Sample Markdown')

        labpath1 = join(self.testTopic.path,
                        'labs',
                        'testl1')
        labpath2 = join(self.testTopic.path,
                        'labs',
                        'testl2')
        labpaths = [labpath1,
                    labpath2]

        lab_yamls = [join(labpath1,
                        'index.yaml'),
                     join(labpath2,
                        'index.yaml')]

        make_dirs(labpaths)
        for lab_yaml in lab_yamls:
            with open(lab_yaml, 'w') as yaml:
                yaml.write('type: Lab')

        self.testTopic.push()

        self.testTopic._push_labs = initial_push_labs_func
        WebServiceClient.send_resource = initial_send_resource_func

    def test_push_courseid_fail(self):
        self.testTopic.courseid = None
        with self.assertRaises(ValueError) as context:
            self.testTopic.push()

        expected_msg = 'No course id value defined in testt'
        self.assertEqual(context.exception.message, expected_msg)

    def test_push_sectionid_fail(self):
        self.testTopic.sectionid = None
        with self.assertRaises(ValueError) as context:
            self.testTopic.push()

        expected_msg = 'No section id value defined in testt'
        self.assertEqual(context.exception.message, expected_msg)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
