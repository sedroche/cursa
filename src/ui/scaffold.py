'''
Created on 19 Jan 2013

Author: John Roche
'''
from cursa import Cursa
from os import sep, getcwd
from os.path import split as path_split
from argparse import ArgumentError
from argparse import Action
from dom.utils import log
from config import cursa_home


class Scaffold(object):
    '''
    | The Scaffold class is an implementation of a command line interface
      command in the cursa application.
    | As a command class it has implemented a static setup(namespace) method
      and a call(namespace) method. The call(namespace) method must implement
      the functionality of the command from the command line interface.
    | As a command class it has implemented a static setup(namespace) method
      and a call(namespace) method.
    | The class attributes title (str) and help (str) must also be implemented
    '''

    title = 'scaffold'
    help = '''Create file structure and templates
              for the specified module, topic or lab'''

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
            valid_folders = ['cursa', 'topics', 'labs']
            path = getcwd()
            tail = path_split(path)[1]

            if not (cursa_home in path and tail in valid_folders):
                raise ValueError('Please move to a valid folder')

            if tail == 'cursa':
                if namespace.rich:
                    action = Action(option_strings=['-r', '--rich'],
                                    dest='RICH')
                    raise ArgumentError(action,
                               'Can only be used when scaffolding a topic')

                category = 'Module'
                config = {
                          'category': category,
                          'name': namespace.name,
                          'title': namespace.title
                          }

            elif tail == 'topics':
                category = 'Topic'
                # Obtain parent module from file path
                module = path.replace(cursa_home, '').split(sep)[1]
                config = {
                          'category': category,
                          'name': namespace.name,
                          'title': namespace.title,
                          'module': module,
                          'rich': namespace.rich
                          }

            elif tail == 'labs':
                if namespace.rich:
                    action = Action(option_strings=['-r', '--rich'],
                                    dest='RICH')
                    raise ArgumentError(action,
                               'Can only be used when scaffolding a topic')
                category = 'Lab'
                # Obtain module and topic name from file path
                module = path.replace(cursa_home, '').split(sep)[1]
                topic = path.replace(cursa_home, '').split(sep)[3]
                config = {
                          'category': category,
                          'name': namespace.name,
                          'title': namespace.title,
                          'module': module,
                          'topic': topic
                          }

            Cursa().scaffold(config)
            log('Scaffold completed')

        except KeyboardInterrupt:
            # fail silently. tidy terminal
            newline = ''
            log(newline)
        except Exception as why:
            msg = '\n'.join(['Error while attempting scaffold',
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

        command_parser.add_argument('name',
                                    help='''The name of the course section to
                                            scaffold''')

        command_parser.add_argument('-t', '--title',
                                    help='''The title of the course section.
                                            If the title is supplied it will be
                                            used to identify the course section
                                            in any HTML pages.
                                            The title will also be used to name
                                            any output from cursa.
                                            If a title is not supplied the name
                                            of the course section will be used
                                            ''')

        command_parser.add_argument('-r', '--rich',
                                    action='store_true',
                                    help='''This option only can be used when
                                            scaffolding a topic.Indicates
                                            whether the topicindex.html page
                                            will contain rich content, e.g.
                                            images, archives. Folders will be
                                            created for this content.
                                            ''')

        command_parser.set_defaults(command=cls)
