'''
Created on Nov 20, 2012

Author: John Roche
'''
from generator import generate
from os.path import splitext, join
from os import sep
from utils import read_data_from_file, write_to_file
import config


class Step(object):
    '''
    | The Step Class models a step in a Lab.
    | A Step object models a Markdown file in the Cursa system.
    | The Step class is responsible for calling the generator module
      to create the output format.
    '''

    def __init__(self, stepmeta=None, filename=None, labpath=None):
        """
        Kwargs:
           - stepmeta (dict): Contains the meta data to create the Step Object
           - labpath (String): Path to the lab on the system
           - filename (String): The filename of the Markdown file.
               .. note::
                   Filename only to be used when creating a step
                   using the prefix approach.
               ..

        Returns:
               Step object
        """

        if filename and labpath and not stepmeta:
            self.markdown = filename
            prefix, self.ext = splitext(filename)
            self.title = prefix[2:]
            self.position = prefix[:1]
            self.nav_element = ('<li class="{0}">'
                                '<a href="{1}">{2}</a>'
                                '</li>').format(self.title,
                                                self.title + '.html',
                                                self.title)

        if stepmeta and labpath and not filename:
            self.__dict__.update(**stepmeta)
            self.position = None
            self.nav_element = ('<li class="{0}">'
                                '<a href="{1}">{2}</a>'
                                '</li>').format(self.markdown,
                                                self.markdown + '.html',
                                                self.title)

        self.labpath = labpath

    def build(self, navBar, css):
        """
        The build method uses the generator module to produce
        the HTML output from the Markdown file that this step models

            args:
               - navBar (String): Contains the Navigation Bar for the Lab
               - css (list):  The css to use in the step
        """

        activeNavBar = self._mark_active(navBar)
        step_params = {
                       'title': self.markdown or self.title,
                       'labpath': self.labpath,
                       'navbar': activeNavBar,
                       'css': css
                       }

        return generate(stepparams=step_params)

    def _mark_active(self, navBar):
        """
        Changes the class name on the this steps list element
        to active. This will activate CSS in the HTML output.

            args:
               navBar (String): Contains the Navigation Bar for the Lab

            Returns:
               String representation of the Navigation Bar with
               the list element in the navbar marked as active
        """

        return navBar.replace('class="' + self.markdown + '"',
                              'class="active"')

    def moodleify(self, path, topicpath, topic, courseid, sectionid):
        """
        | Configures the step for being pushed to Moodle
        | This involves changing local navigation links to navigation links
          that will work in the Moodle environment

            args:
               path (str): The base folder of the lab. This is a temp
                              folder being used for preparing the steps

               topicpath (str): The topic path of the containing Topic

               topic (str): The topic name

               courseid (str): The course id number

               sectionid (str): The section id number
        """

        name = self.markdown or self.title
        moodlestep = ''.join([path,
                              sep,
                              'html',
                              sep,
                              name,
                              '.html'])

        content = read_data_from_file(moodlestep)

        topicindex = join(topicpath, 'index.html')
        localhref = '<a href="{0}">{1}</a>'.format(topicindex,
                                                   topic)

        moodle_endpoint = 'course/view.php?id={0}&section={1}'.format(courseid,
                                                                     sectionid)
        step_moodle_url = ''.join([config.moodle_url,
                                   moodle_endpoint])

        moodlehref = '<a href="{0}">{1}</a>'.format(step_moodle_url,
                                                    topic)

        moodleified_content = content.replace(localhref, moodlehref)

        write_to_file(moodlestep, moodleified_content.encode('utf8'))
