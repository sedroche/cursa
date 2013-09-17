#Cursa static course generator
------------------------------------------

##Project Page
---------------
See the [project page](http://sedero.github.io/cursa/) to find out more about cursa.


##Installation
-------------

1. git clone https://github.com/sedero/cursa.git

2. Add cursa.py to your path


        $ echo 'export PATH="/path/to/cursa.py:$PATH"' >> ~/.bash_profile && source ~/.bash_profile

3. Cursa has some dependencies that need to be installed


        $ sudo pip install markdown
	 
        $ sudo pip install requests
	 

4. PyYaml needs to be downloaded and manually installed


        $ wget http://pyyaml.org/download/pyyaml/PyYAML-3.10.tar.gz
	 
        $ tar -xvzf PyYAML-3.10.tar.gz
	 
        $ sudo python setup.py install 
	

5. Finally, cursa uses the wkhtmltopdf application to create PDF output. In the wkhtmltopdf directory you will
   find the wkhtmltopdf application for your platform - Linux, Mac OSx or Windows.
   Put all the files in the directory labled with your platform into the DATA folder

   You may need to make the application executable

        $ chmod +x wkhtmltopdf


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

