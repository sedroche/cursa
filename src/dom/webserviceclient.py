'''
Created on 11 Apr 2013

Author: John Roche
'''
import requests
from errorhandling.cursa_exceptions import CursaException
import config


class WebServiceClient(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''

    def send_resource(self, webservice_params, filepath=None):
        """| Sends a resource to Moodle.
           | This function uses the custom clarity plugin

        Args:
           - webservice_params (dict):

            {
                 | 'courseid':  The course id,
                 | 'sectionid':  The section id,
                 | 'type':  file, label,
                 | 'displayname':  The name beside the resource,
                 | 'mainfile':  The main file. To be used with folder to create
                                lab or presentation,
                 | 'mainfilepath':  The path to the main file from the root of
                                    the folder. Must start and end with /,
                 | 'labeltext':  The label text,
                 | 'labeltextformat':  The label text format. markdown or html,
             }

        Raises:
             CursaException
        """

        restendpoint = 'webservice/rest/server.php?'
        token = ''.join(['wstoken=', config.moodle_token])
        function = '&wsfunction=local_clarity_create_resource'
        restformat = '&moodlewsrestformat=json'

        url = ''.join([config.moodle_url,
                       restendpoint,
                       token,
                       function,
                       restformat])

        try:
            if filepath:
                files = {'file': open(filepath, 'rb')}
                response = requests.post(url,
                                         params=webservice_params,
                                         files=files)
            else:
                response = requests.post(url,
                                         params=webservice_params)

            # Raise an exception if a bad request occurs
            response.raise_for_status()

            return response.json()

        except requests.exceptions.ConnectionError:
            msg = 'Connection failed'
            raise CursaException(msg)
        except requests.exceptions.Timeout:
            msg = 'Connection timed out'
            raise CursaException(msg)
        except requests.exceptions.HTTPError:
            msg = 'Invalid HTTP response'
            raise CursaException(msg)
        except IOError:
            msg = 'Error opening file at {0}'.format(filepath)
            raise CursaException(msg)
