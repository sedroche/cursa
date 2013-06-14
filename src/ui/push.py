'''
Created on 11 Apr 2013

Author: John Roche
'''
from cursa import Cursa
from os import getcwd
from dom.utils import log, create_course_info


class Push(object):
    '''
    | The Push class is an implementation of a command line interface
      command in the cursa application.
    | As a command class it has implemented a static setup(namespace) method
      and a call(namespace) method. The call(namespace) method must implement
      the functionality of the command from the command line interface.
    | As a command class it has implemented a static setup(namespace) method
      and a call(namespace) method.
    | The class attributes title (str) and help (str) must also be implemented
    '''

    title = 'push'
    help = '''Push a Lab, Topic, or Module to Moodle'''

    def __init__(self):
        '''
        Constructor
        '''

    def call(self, namespace):
        '''Implements the functionality of the command from the command line
           interface.
           This is the public method that the CommandLine class invokes when
           instructed to perform a command.
        '''
        try:
                path = getcwd()
                courseinfo = create_course_info(path)
                Cursa().push(path, courseinfo)
                log('Push completed')
        except KeyboardInterrupt:
            # fail silently. tidy terminal
            newline = ''
            log(newline)
        except Exception as why:
            msg = '\n'.join(['Error while attempting push',
                             str(why)])
            log(msg)

    @classmethod
    def setup(cls, command_parser):
        '''Defines the command.
           This method should define which switches and arguments the command
           can receive from the command line interface
           Registers the class with the CommandLine class by setting
           an attribute in the namespace returned from the parse_args
           method.
        '''

        command_parser.set_defaults(command=cls)
