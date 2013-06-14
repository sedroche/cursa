'''
Created on 18 Jan 2013

Author: John Roche
'''
import unittest
from argparse import ArgumentParser
from ui.cli import CommandLine


class TestCommandLine(unittest.TestCase):

    def setUp(self):
        CommandLine.commands.append(TestCommand)

    def tearDown(self):
        self.commandline = None

    def test_init(self):
        args = ['path/to/script', 'test']
        self.commandline = CommandLine(args=args)
        self.assertTrue(self.commandline._parser.__class__, ArgumentParser)
        self.assertEquals(self.commandline._parser.prog, 'cursa')
        self.assertTrue(self.commandline._subparsers.__class__, ArgumentParser)

        dest = self.commandline._subparsers.dest
        self.assertEquals(dest, 'subparser_name')

        metavar = self.commandline._subparsers.metavar
        self.assertEquals(metavar, "COMMAND")

    def test_setup_commands(self):
        args = ['path/to/script', 'test']
        commandline = CommandLine(args=args)

        len_choices = len(commandline._subparsers.choices)
        self.assertEquals(len_choices, 4)
        classes = ['build', 'scaffold', 'push', 'test']
        for klass in classes:
            self.assertTrue(klass in commandline._subparsers.choices)

    def test_do_commands(self):
        args = ['path/to/script', 'test']
        commandline = CommandLine(args=args)

        self.assertTrue(commandline.commands[3].passedtest)


class TestCommand(object):
    title = 'test'
    help = 'This is a test command class'
    passedtest = False

    def __init__(self):
        '''class docs'''

    def call(self, namespace):
        TestCommand.passedtest = True

    @classmethod
    def setup(cls, command_parser):
        command_parser.set_defaults(command=cls)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
