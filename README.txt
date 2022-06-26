# CS305 ASSIGNMENT 2

Name: Urvee Gupta

Roll No.: 2019CSB1128

Course: CS305

=================================


1. What does this program do

	==>	This program implements a server that maintains a database consisting of facial information.
	==>	It provides routines like adding single image to database or uploading images in bulk by uploading
		a zip file.
	==>	It provides routines for scanning an image containing single or multiple faces and finding the
		closest k matches in the database. We can also specify the level of strictness (/accuracy) we
		want in our search
	==>	Provides a routine for searching a given face_id in the database


2. A description of how this program works (i.e. its logic)

	==>   when main.py is run, the server is setup and all the routines can be accessed via swagger docs.
	==>   on startup, the program establishes a connection with the database (whose link is in config.json file)
	==>   The connection to the database is maintained as long as the program runs and while disconnects during shutdown
	==>	the routines in main.py use modules of file_operations.py and database_operations.py for uploading/extracting
		data and performing serach/insert operations.
	==> 	face_recognition module is used for evaluating the faces from images.
	==>	The database stores name, face encoding, version, date and location of each image to be processed.


3. How to compile and run this program

	==>	In the current directory, first we will activate the python environment, and then we will run the testfile.

	==>	COMMANDS/STEPS TO COMPILE AND RUN THIS PROGRAM
		
		1) in config.json file, add your url to a postgres database
			
			############### {"url":/********YOUR DATABASE URL HERE********/} ###############

			{format = "postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE NAME}"}

		2) Open a command line terminal

		3) run-> "./env/bin/activate"   					--->[for activating python environment]

		4) run-> "python main.py"						--->[to start the sever]

		5) the server will start at ->  http://127.0.0.1:8000		--->[server started (page shows a temporary json)]

		6) navigate to -> http://127.0.0.1:8000/docs			--->[opens swagger ui where we can implement the routines]

		7) The routines are shown here and can be used via this UI

		##FOR RUNNING THE TESTS

		8) run-> "coverage run -m pytest testfile.py"			--->[runs the tests for all the routines]

		9) run-> "coverage report"						--->[shows the percentage coverage after running tests]

		A SCREENSHOT OF COVERAGE REPORT: (94% covered)
			
		Name                     Stmts   Miss  Cover
		--------------------------------------------
		connect_database.py         13      0   100%
		database_operations.py     113     15    87%
		file_operations.py          38      1    97%
		main.py                     62      1    98%
		testfile.py                 67      0   100%
		--------------------------------------------
		TOTAL                      293     17    94%


# DESIGN DETAILS

# file structure- 

	Python environment files:	-.idea
						-.pytest_cache
						-__pycache__
						-dlib
						-env
						-face_recognition
	
	Source files:			-main.py
						-connect_database.py
						-database_operations.py
						-file_operations.py
						-config.json
						-testfile.py

	Other files and folders		-test
						-uploads
						-.coverage
						-README


# file details: 

        #1 main.py - 
            contains all the routes the server is offering (search_faces,add_face,add_faces_in_bulk,get_face_info,clean_testdata).
        #2 connect_database - 
		does all the work to connect to the database.            
        #3 database_operations.py - 
            contains all modules used to process the data.
        #4 file_operations.py -
            contains all modules used to upload/extract image and zip files
        #5 config.json -
            user has to enter the database url here.
        #6 testfile.py - 
            implements tests for all the routines provided by the server, and an additional cleanup test to remove the data added during test run
		(the tests need to be implemented in the order specified in the test file only as the data they use is inter-related)
        
# folder structures:

	  #1 uploads : this folder contains 3 sub directories -find,-bulk,-single. 
			   When search_faces request is called, the image is upload in 'find' directory, 
			   When add_face request is called, the image to be added is uploaded in 'single' directory,
			   When add_faces_in_bulk is called, the compressed files are stored in 'bulk' directory and 
			   extraction is done in '_{compressed file name}' directory created during extraction.
 	  #2 test	 : The sources used in the testfile.py file are stored in this directory.


# Some design infos (SOLID principles, design techniques, efficient testing, etc):

		#1 main.py contains only the routine modules and does not contain any helper functions within it.
			This makes main.py file independent of implementation details.
	  
		#2 The database url is taken separately in config.json file and database connection is handled by connect_database only
	     		(Hence, in future if we need to implement some other database engine, we would just need a new url and 
			no changes will be required in other source files)
	  
		#3 The file_operations.py contains separate classes for uploading and extracting files.
	     		File extraction can be done from any compressed file (.zip, .tar, .tgz, .tar.gz)
	     		if we need to add more extension compatibility, we just need to add that module in Extract class.
	     		The class receives the compressed file, checks the extension, and uses the appropriate extraction method by itself.
			Hence, no changes would be required in other source files
	  
		#4 the database_operations.py file contains all modules that are called by main.py routines. 
			Any other functionality can be added as a new function in this file and called by main.py
        
		#5 the databse stores the images in form of their encoding data obtained from "face_recognition.face_encodings()" function 
			rather than storing entire images in database. This makes the storage efficient and faster.

		#6 appropriate comments are added at every step and a description of each function is given at its definition.

		#7 The uploaded data is stored in a proper folder format and is consistent. 
			uploading the data makes it independent of the location of the actual file in our system.
			Hence, data can be picked up from any location in our pc.

		#8 The test cases used cover 94% of the program. (screenshot provided above)