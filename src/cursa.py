#!/usr/bin/env python
'''
Created on Oct 27, 2012

Author: John Roche

| The cursa class the main script of the cursa application
| It is a facade between the cursa application and the UI layer.
| The cursa class should be called to implement domain logic.
| Domain classes should not be called directly
'''

from dom.module import Module
from dom.topic import Topic
from dom.lab import Lab
from sys import argv
from yaml import load
from os.path import join
from errorhandling.cursa_exceptions import CursaException
from dom.utils import log


class Cursa(object):

    def __init__(self):
        self._classes = {
                         'Module': Module,
                         'Topic': Topic,
                         'Lab': Lab
                        }

    def scaffold(self, config):
        category = config.pop('category')
        Cls = self._classes[category]
        Cls().scaffold(config)

    def build(self, path, courseinfo):
        yaml_file = join(path, 'index.yaml')
        try:
            with open(yaml_file) as index:
                meta = load(index)

            meta.update(courseinfo)
            msg = 'Starting build of {0} {1}\n'.format(meta['type'],
                                                       meta['title'])
            log(msg)

            Cls = self._classes[meta['type']]
            Cls(meta).build()
        except IOError:
            msg = 'Error reading YAML file at {0}'.format(yaml_file)
            raise CursaException(msg)

    def push(self, path, courseinfo):
        yaml_file = join(path, 'index.yaml')
        try:
            with open(yaml_file) as index:
                meta = load(index)

            meta.update(courseinfo)
            msg = 'Starting push of {0} {1}\n'.format(meta['type'],
                                                      meta['title'])
            log(msg)

            Cls = self._classes[meta['type']]
            Cls(meta).push()
        except IOError:
            msg = 'Error reading YAML file at {0}'.format(yaml_file)
            raise CursaException(msg)

    if __name__ == "__main__":
        from ui.cli import CommandLine
        CommandLine(args=argv)
