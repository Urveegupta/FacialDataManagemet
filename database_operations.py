import os
import datetime
import numpy as np
import face_recognition
from PIL import Image, ExifTags
from connect_database import faces,engine


# helper function to correct orientation properties (if any) of the image
def correct_orientation(filepath):
    try:
        image=Image.open(filepath)

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        
        exif = image._getexif()

        if exif[orientation] == 3:
            image=image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image=image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image=image.rotate(90, expand=True)

        image.save(filepath)
        image.close()
    except (AttributeError, KeyError, IndexError,TypeError):
        # cases: image don't have getexif
        pass

def without_ids(d):
     return {x: d[x] for x in d if x != "id"}

# helper function to check if name already 
# present in database and return 
# latest version
def latest_prev_version(name,meta_data,nameset):

    # for version
    pid = 0

    #check if name already exists (from nameset)
    if name in nameset:
        ans = []

        #name already exists in database, find version
        for x in meta_data:
            
            if x["name"] == name:
                ans.append(int(x["version"]))

        # latest version
        pid = max(ans)

    #update nameset if new name
    if pid == 0:
        meta_data.append(name)
    
    return pid


# function to add faces with names to database in bulk
def add_to_database_bulk(DATA_DIR,faceset,meta_data,nameset):

    KNOWN_FACES_DIR = DATA_DIR

    # a count of num of entries added to database
    numofentries=0

    # load new known faces
    for name in os.listdir(KNOWN_FACES_DIR):
        
        tempname = KNOWN_FACES_DIR + '/' + name
        
        # for version
        pid = latest_prev_version(name,meta_data,nameset)

        if pid == 0:
            # new name found, add in nameset
            nameset.add(name)

        if(os.path.isfile(tempname)):
            continue

        # iterate through image files
        for filename in os.listdir(tempname):

            tempname2 = KNOWN_FACES_DIR + '/' + name + '/' + filename
            correct_orientation(tempname2)
            
            # load image
            image = face_recognition.load_image_file(tempname2)
            
            # encode image for efficient storage
            encoding = face_recognition.face_encodings(image)[0]

            # version of the image
            pid = pid + 1

            # datetime of the image
            dt = datetime.datetime.now()
            
            # insert in database
            query = faces.insert().returning(faces.c.id).values(name = name, data = encoding, version= pid , date = None , location= None)
            
            newid =  engine.execute(query).fetchall()
            
            numofentries = numofentries +1

            # update meta data
            # (id,name,version,location,date)
            meta_data.append({
                'id': newid,
                'name': name,
                'version': pid,
                'location': None,
                'date': dt
            })

            # update faceset (encodings)
            faceset.append(encoding)

    return numofentries # no of new entries in database

# helper function 

# function to add a single file to database
def add_single_face(name,location,filepath,faceset,meta_data,nameset):

    print("file path: "+filepath)

    # for version
    pid = latest_prev_version(name,meta_data,nameset)
    
    correct_orientation(filepath)

    if pid == 0: 
        # new name found, add in nameset
        nameset.add(name)

    # load image
    image = face_recognition.load_image_file(filepath)

    # encode image for efficient storage
    encoding = face_recognition.face_encodings(image)
    
    print(str(len(encoding)) + " faces found")
    # if more than one face
    if(len(encoding) > 1):
        return {"Status":"Error","Body":"Please upload images with a single face"}
    if(len(encoding)==0):
        return {"Status":"Error","Body":"No face found in the image"}

    encoding = encoding[0]

    # version of the image
    pid = int(pid) + 1
    
    # datetime of the image
    dt = datetime.datetime.now()

    # insert in database
    query = faces.insert().returning(faces.c.id).values(name = name, data = encoding, version= pid , date = None , location= location)
            
    newid =  engine.execute(query).fetchone()

    # update meta data
    # (id,name,version,location,date)
    meta_data.append({
        'id': newid["id"],
        'name': name,
        'version': pid,
        'location': location,
        'date': dt
    })

    # update faceset (encodings)
    faceset.append(encoding)
    
    return {"Status":"OK","Body":"Face added","id":newid["id"]}


# function to find k best matches from database
def find_k_matches(k,strictness,filename,faceset,meta_data):

    TOLERANCE = (0.7) - (0.003)*strictness

    correct_orientation(filename)

    # load image
    image = face_recognition.load_image_file(filename)
    locations = face_recognition.face_locations(image)
    encodings = face_recognition.face_encodings(image,locations)
   
    # no of faces found in image
    no_of_faces = len(encodings)
    print(str(no_of_faces)+" faces found in file: "+filename)

    # dictionary to return
    to_return = {}

    # corner cases
    if(no_of_faces == 0):
        return {"Status":"Error","Body":"No face found in uploaded image"}
    if(faceset == []):
        return {"Status":"Error","Body":"No image data found in dataset"}
    
    #index for dictionary (to_return)
    ind=1

    # iterate through the found faces
    for face_enco in encodings:

        # calculate closeness to databases images to pick best k
        results = face_recognition.face_distance(faceset,face_enco)
        
        # indexes of best k matches
        kbestindexes = np.argsort(results)[:k]
        
        # will contain information about the matches
        kbest = []

        no_of_good_matches=0
        for i in range(min(k,len(kbestindexes))):
            
            # check if result falls within the TOLERANCE range 
            if results[kbestindexes[i]] > TOLERANCE:
                # only i good matches found
                break
            
            no_of_good_matches = no_of_good_matches + 1

            # add result to list
            dataresult = without_ids(meta_data[kbestindexes[i]])
            
            kbest.append(dataresult)
        
        # if k good matches not found give additional info in output
        if(no_of_good_matches<k and no_of_good_matches!=0):

            kbest.append({"additional info":f"only {no_of_good_matches} matches found within strictness limit"})

        # if no good match found
        if(no_of_good_matches==0):

            kbest.append({"Info":"No good match found in the database within strictness limit"})

        # append result in to_return dictionary
        faceno = "face "+str(ind)

        # increment index
        ind= ind+1

        # add to dictionary
        to_return[faceno]=kbest

    return to_return