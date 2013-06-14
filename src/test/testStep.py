'''
Created on Nov 22, 2012

@author: john
'''
import unittest
from dom.step import Step
from os.path import join, exists, abspath, dirname, pardir
from os import remove
from shutil import rmtree
from dom import utils
from tempfile import mkdtemp
import config


class testStep(unittest.TestCase):

    def setUp(self):
        cursa_home = abspath(join(dirname(__file__),
                                  pardir,
                                  pardir,
                                  'test_data'
                                  )
                            )

        stepmeta = {
                    "markdown": "test",
                    "title": "test"
                    }

        labpath = join(cursa_home,
                       'test_module',
                       'topics',
                       'test_topic',
                       'labs',
                       'test_lab')

        self.teststep = Step(stepmeta=stepmeta,
                             labpath=labpath)

    def tearDown(self):
        if exists(config.cursa_home):
            rmtree(config.cursa_home)

        self.teststep = None

    def test_build_step(self):
        navbar = (u'<div class="navbar navbar-fixed-top">'
                '<p id="title">lab title&nbsp;&nbsp;</p>'
                '<div class="navbar-inner">'
                '<ul class="nav">'
                '<li class="test"><a href="test.html">test</a></li>'
                '</ul>'
                '<p class="navbar-text pull-right">'
                '<a href="path/to/topic/home">topic name</a> &nbsp; &nbsp;</p>'
                '</div>'
                '</div>')

        utils.make_dir(join(self.teststep.labpath, 'md'))
        utils.make_dir(join(self.teststep.labpath, 'html'))
        utils.create_file(join(self.teststep.labpath,
                         'md',
                         'test.md'))
        with open(join(self.teststep.labpath,
                         'md',
                         'test.md'), 'w') as exer:
            exer.write('![](../img/08.png)')
            exer.write('![](../img/09.png)')

        css = '<link rel="stylesheet" href="path/" type="text/css">'
        self.teststep.build(navbar, css)

        self.assertTrue(exists(join(self.teststep.labpath,
                                    'html',
                                    'test.html')))

    def test_mark_active(self):
        navbar = (u'<div class="navbar navbar-fixed-top">'
                  '<p id="title">lab title&nbsp;&nbsp;</p>'
                  '<div class="navbar-inner">'
                  '<ul class="nav">' +
                  self.teststep.nav_element +
                  '</ul>'
                  '<p class="navbar-text pull-right">'
                  '<a href="path/to/topic/home">topic name</a> &nbsp; &nbsp;'
                  '</p>'
                  '</div>'
                  '</div>')

        resultString = self.teststep._mark_active(navbar)

        expectedString = (u'<div class="navbar navbar-fixed-top">'
                          '<p id="title">lab title&nbsp;&nbsp;</p>'
                          '<div class="navbar-inner">'
                          '<ul class="nav">'
                          '<li class="active">'
                          '<a href="test.html">test</a></li>'
                          '</ul>'
                          '<p class="navbar-text pull-right">'
                          '<a href="path/to/topic/home">topic name'
                          '</a> &nbsp; &nbsp;'
                          '</p>'
                          '</div>'
                          '</div>')

        self.assertEqual(expectedString, resultString)

    def test_moodleify(self):
        topicpath = join(config.cursa_home,
                         'test_module',
                         'topics',
                         'test_topic')

        path = mkdtemp()
        utils.make_dir(join(path, 'html'))
        testfile = join(path, 'html', 'test.html')
        utils.create_file(testfile)

        topic = 'test_topic'
        topicindex = join(topicpath, 'index.html')
        locallink = '<a href="{0}">{1}</a>'.format(topicindex,
                                                   topic)
        utils.write_to_file(testfile, locallink)

        self.teststep.moodleify(path, topicpath, 'test_topic', '1', '1')

        result = utils.read_data_from_file(testfile)

        moodle_endpoint = 'course/view.php?id={0}&section={1}'.format('1',
                                                                      '1')
        moodle_url = ''.join([config.moodle_url,
                              moodle_endpoint])

        expected_result = '<a href="{0}">{1}</a>'.format(moodle_url,
                                                         topic)
        self.assertEquals(expected_result, result)

        remove(testfile)
        rmtree(path)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
