'''
Created on Oct 27, 2012

@author: john
'''
#import unittest
#from dom.module import Module
#from dom.cursa import Cursa
#from dom.topic import Topic
#from dom.lab import Lab
#from dom import utils


#class testCursa(unittest.TestCase):

#    def setUp(self):
#        self.testCursa = Cursa()

    #def tearDown(self):
        #self.testCursa = None

#    def testDir(self):
#        self.testCursa.dir('cursa_test_module')
#        self.assertIsInstance(self.testCursa.modules['cursa_test_module'], Module)
#        self.assertEqual(self.testCursa.modules['cursa_test_module'].name, 'cursa_test_module') 
#
#    def testTopic(self):
#        self.testCursa.dir('cursa_test_module')
#        self.testCursa.topic('cursa_test_module','cursa_test_topic')
#        self.assertIsInstance(self.testCursa.modules['cursa_test_module'].topics['cursa_test_topic'], Topic)
#        self.assertEqual(self.testCursa.modules['cursa_test_module'].topics['cursa_test_topic'].name, 'cursa_test_topic')
#
#    def testLab(self):
#        self.testCursa.dir('cursa_test_module')
#        self.testCursa.topic('cursa_test_module','cursa_test_topic')
#        self.testCursa.lab('cursa_test_module','cursa_test_topic','cursa_test_lab')
#        self.assertIsInstance(self.testCursa.modules['cursa_test_module'].topics['cursa_test_topic'].labs['cursa_test_lab'], Lab)
#        self.assertEqual(self.testCursa.modules['cursa_test_module'].topics['cursa_test_topic'].labs['cursa_test_lab'].name, 'cursa_test_lab') 

#    def testCreateObjectModel(self):
#        utils.makeDir(Cursa.path + 'testCOM/testYaml/')
#        open(Cursa.path + 'testCOM/testYaml/test.yaml', 'w')
#
#        self.testCursa._createObjectModel(Cursa.path + 'testCOM/testYaml/test.yaml')
#
#        modules = self.testCursa.modules
#        self.assertTrue('testCOM' in modules)
#        self.assertIsInstance(modules.get('testCOM'),Module)
#
#        topics = self.testCursa.modules.get('testCOM').topics
#        self.assertTrue('testCOMtopic' in topics)
#        self.assertIsInstance(topics.get('testCOMtopic'),Topic)
#
#        labs = self.testCursa.modules.get('testCOM').topics.get('testCOMtopic').labs
#        self.assertTrue('testCOMlab' in labs)
#        self.assertIsInstance(labs.get('testCOMlab'),Lab)

#    if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.test']
#        unittest.main()

