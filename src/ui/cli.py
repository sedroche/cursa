'''
Created on 14 Jan 2013

Author: John Roche
'''
from argparse import ArgumentParser
from build import Build
from scaffold import Scaffold
from push import Push
from config import version


class CommandLine(object):
    '''
    | The CommandLine class is the class that controls
      the command line interface which the user interacts
      with when using the cursa application.
    | Each command is modelled as a separate class in the cursa application.
    | The CommandLine class is responsible for registering each command class
      with the command line instruction and for invoking the call() method of
      each command class when called from the command line interface.

    | Each command class must implement a static setup(namespace) method
      and a call(namespace) method.
    '''

    commands = [Build, Scaffold, Push]

    def __init__(self, namespace=None, args=None):
        """
        Kwargs:
           namespace (object): namespace will be passed to parse_args method.
                               The parse_args method returns an object with
                               assigned attributes.
                               Use namespace if you need to assign these
                               attributes to an already existing object,
                               rather than a new Namespace object.

           args (list):        args is a list containing the instructions from
                               the command line interface.
                               This will always be sys.args


        Returns:
               CommandLine object
        """

        #Remove script name from args.
        #ArgumentParser does not like it
        args = args[1:]

        self._parser = ArgumentParser(prog='cursa')

        self._parser.add_argument('-v', '--version',
                                  action='version',
                                  version=' '.join(['%(prog)s',
                                                    version]))

        self._subparsers = self._parser.add_subparsers(
                           description='''The most commonly used %(prog)s
                                           commands are:''',
                                          dest='subparser_name',
                                          metavar="COMMAND")

        self._setup_commands()

        namespace = self._parser.parse_args(args=args, namespace=namespace)
        self._do_command(namespace)

    def _do_command(self, namespace):
        """
        Invokes the call(namespace) method of the class
        responsible for handling the command.
        The call(namespace) method should implement the
        required actions for the command.

        args:
           namespace (object): namespace object containing the information
                               about the command entered at the command line
                               interface.
                               The command attribute contains the class that
                               is responsible for managing that command.
        """

        namespace.command().call(namespace)

    def _setup_commands(self):
        """
        Registers the command classes with the command line object.
        Invokes the setup static method of each command class
        passing a parser object as an argument.
        The command class can use the parser object to define the
        command and command arguments.
        """
        for command in self.commands:
            command_parser = self._subparsers.add_parser(command.title,
                                                         help=command.help)
            command.setup(command_parser)
