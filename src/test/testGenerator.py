#encoding:UTF-8
'''
Created on Nov 29, 2012

@author: john
'''
import unittest
from dom import generator
from os.path import join, exists, abspath, dirname, pardir
from dom.utils import make_dirs, make_dir, create_file, create_files
from shutil import rmtree
import config


class Test(unittest.TestCase):

    def setUp(self):
        config.cursa_home = abspath(join(dirname(__file__),
                                         pardir,
                                         pardir,
                                         'test_data'
                                         )
                                    )

    def tearDown(self):
        if exists(config.cursa_home):
            rmtree(config.cursa_home)

    def test_generator_step(self):
        labpath = join(config.cursa_home,
                       'test_module',
                       'topics',
                       'test_topic',
                       'labs',
                       'test_lab')

        directories = [join(labpath, 'md'),
                       join(labpath, 'html')]

        make_dirs(directories)

        filepath = join(labpath, 'md', 'Test.md')
        create_file(filepath)

        navbar = (u'<div class="navbar navbar-fixed-top">'
                  '<p id="title">test title&nbsp;&nbsp;</p>'
                  '<div class="navbar-inner">'
                  '<ul class="nav">'
                  '<li class="Test">'
                  '<a href="Test.html">Test</a></li>'
                  '</ul>'
                  '<p class="navbar-text pull-right">'
                  '<a href="path/to/topic/home">topic name</a> &nbsp; &nbsp;'
                  '</p>'
                  '</div>'
                  '</div>')

        step_params = {
                           'title': 'Test',
                           'labpath': labpath,
                           'navbar': navbar,
                           'css': '<link rel="stylesheet" href="path/" type="text/css">'
                       }

        generator.generate(stepparams=step_params)

        self.assertTrue(exists(join(labpath, 'html', 'Test.html')))

    def test_generator_topic(self):
        topicpath = join(config.cursa_home,
                         'test_module',
                         'topics',
                         'test_topic')

        make_dir(topicpath)

        title = 'topic title'
        filepath = join(topicpath, 'index.md')
        create_file(filepath)

        topic_params = {
                        'category': 'index',
                        'title': title,
                        'content': join(topicpath, 'index.md'),
                        'topicpath': topicpath,
                        'topicinfo': '##some markdown text'
                        }

        generator.generate(topicparams=topic_params)

        self.assertTrue(exists(join(topicpath, 'index.html')))

    def test_generator_module(self):
        modulepath = join(config.cursa_home,
                         'test_module')

        make_dir(modulepath)

        module_params = {
                         'title': 'test_module',
                         'modulepath': modulepath,
                         'topiclinks': '<a>link to test_module</a>'
                         }

        generator.generate(moduleparams=module_params)

        self.assertTrue(exists(join(modulepath, 'index.html')))

    def test_generator_pres(self):
        markdowntext = u"""
===
#slide 1
===
===
#slide 2
===
===
#slide 3
==="""

        prespath = join(config.cursa_home,
                       'test_module',
                       'topics',
                       'test_topic',
                       'presentations')

        presmd = join(prespath, 'md', 'pres.md')

        pres_folders = [join(prespath, 'md'),
                        join(prespath, 'html')]

        make_dirs(pres_folders)

        with open(presmd, 'w') as pres:
            pres.write(markdowntext)

        topic_params = {
                        'category': 'pres',
                        'title': 'Pres',
                        'content': presmd,
                        'prespath': prespath,
                        'css': '<link rel="stylesheet" href="path/" type="text/css">'
                        }

        generator.generate(topicparams=topic_params)

        expected_output = join(config.cursa_home,
                               'test_module',
                               'topics',
                               'test_topic',
                               'presentations',
                               'html',
                               'Pres.html')

        self.assertTrue(exists(expected_output))

        #This string has to be in one line to match expected result
        expected_html = '''<section class="slide"><h1>slide 1</h1></section>&nbsp;<div class="page-breaker"></div><section class="slide"><h1>slide 2</h1></section>&nbsp;<div class="page-breaker"></div><section class="slide"><h1>slide 3</h1></section>'''

        with open(expected_output) as htmlfile:
            html = htmlfile.read()

        self.assertTrue(expected_html in html)

    def test_generator_lab_text(self):
        labpath = join(config.cursa_home,
                       'test_module',
                       'topics',
                       'test_topic',
                       'labs',
                       'test_lab')

        lab_params = {
                        'title': 'test',
                        'steps': [{'title': 'teststep1',
                                   'markdown': 'teststep1'
                                   },
                                  {'title': 'teststep2',
                                   'markdown': 'teststep2'
                                   },
                                  {'title': 'teststep3',
                                   'markdown': 'teststep3'
                                   }],
                        'labpath': labpath,
                        'css': '<link rel="stylesheet" href="path/" type="text/css">'
                     }

        mdfolder = join(labpath, 'md')
        pdffolder = join(labpath, 'pdf')
        labdirs = [mdfolder,
                   pdffolder]

        make_dirs(labdirs)

        mdfiles = [join(mdfolder, 'teststep1.md'),
                   join(mdfolder, 'teststep2.md'),
                   join(mdfolder, 'teststep3.md')]

        create_files(mdfiles)

        generator.generate(labparams=lab_params)

        expected_output = join(pdffolder, 'test.pdf')

        self.assertTrue(exists(expected_output))

    def test_generator_pres_text(self):
        prespath = join(config.cursa_home,
                         'test_module',
                         'topics',
                         'test_topic',
                         'presentations')

        mdfolder = join(prespath, 'md')
        pdffolder = join(prespath, 'pdf')
        labdirs = [mdfolder,
                   pdffolder]

        make_dirs(labdirs)

        pres_mdfile = join(mdfolder, 'testpres.md')

        create_file(pres_mdfile)

        topic_params = {
                        'category': 'pres_text',
                        'title': 'testpres',
                        'content': 'testpres.md',
                        'prespath': prespath,
                        'css': '<link rel="stylesheet" href="path/" type="text/css">'
                     }
        generator.generate(topicparams=topic_params)

        expected_output = join(pdffolder, 'testpres.pdf')

        self.assertTrue(exists(expected_output))

    def test_generator_topic_label(self):
        indexpath = join(config.cursa_home,
                         'test_module',
                         'topics',
                         'test_topic')

        indexfile = join(indexpath, 'index.md')

        topic_params = {
                        'category': 'label',
                        'content': indexfile
                        }

        make_dir(indexpath)

        create_file(indexfile)

        with open(indexfile, 'w') as f:
            f.write('#test h1')

        result = generator.generate(topicparams=topic_params)
        expected_result = '<h1>test h1</h1>'
        self.assertEquals(result, expected_result)

    def test_make_imageurls_absolute(self):
        path_with_rel_path = '![](../img/image.png)'
        labpath = 'absolute/path/to'

        result = generator._make_imageurls_absolute(path_with_rel_path,
                                                    labpath)

        expected_result = '![](absolute/path/to/img/image.png)'
        self.assertEquals(result, expected_result)

    def test_write_view_to_file(self):
        modulepath = join(config.cursa_home,
                         'test_module')

        make_dir(modulepath)
        file_to_create = join(modulepath, 'test.html')
        view = u'<htm><body><div>£$%^&*</div></body></html>'

        generator._write_view_to_file(file_to_create, view)

        self.assertTrue(exists(file_to_create))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_create_html_template']
    unittest.main()
