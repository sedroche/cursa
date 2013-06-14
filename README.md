#Cursa static course generator
------------------------------------------

##Installation
-------------

1. git clone https://jrochebucket@bitbucket.org/jrochebucket/cursa.git

2. Add cursa.py to your path


        $ echo 'export PATH="/path/to/cursa.py:$PATH"' >> ~/.bash_profile && source ~/.bash_profile


##Tests
------

1. Install nose


        $ pip install nose

2. Run tests. From anywhere in the directory just enter 


        $ nosetests

###To produce coverage reports
------------------------------

1. Install coverage.py


        $ pip install coverage

2. From anywhere in the directory just enter


        $ nosetests --cover-branches --with-coverage --cover-erase --cover-html --cover-package=dom --cover-package=ui

   This will create a folder named cover within the directory that the command is entered, which will contain html coverage reports

##Documentation
----------------

1. Install sphinx


        $ pip install sphinx

2. From within the documentation directory


        $ make html

   The documentation will be created in documentation/_build/html

