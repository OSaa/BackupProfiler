import csv
import sys
import os
import re
from datetime import datetime
import time
import strftime_1900
from PIL import Image
from PIL.ExifTags import TAGS
import random
# from HTMLParser import HTMLParser

# Because of CSV Error generated: _csv.Error: field larger than field limit (131072)
csv.field_size_limit(sys.maxsize)

# Removes HTML tags from strings
# class MLStripper(HTMLParser):
#     def __init__(self):
#         self.reset()
#         self.fed = []
#     def handle_data(self, d):
#         self.fed.append(d)
#     def get_data(self):
#         return '\n'.join(self.fed)

# def strip_tags(html):
#     s = MLStripper()
#     s.feed(html)
#     return s.get_data()

class Data_Extraction():
    def __init__(self, mainDirs):

        self.directoryExtracted = mainDirs

        # Generate contact list
        self.extract_ContactsInfo()
        self.extract_CalendarInfo()


        # Initializers
        self.numPeopleCalled = 0
        self.numPeopleSMS = 0
        self.imageTable = list()
        self.mapData = list()
        self.imagePaths = list()
        self.extract_ImageData()
        self.extract_NotesData()

    def extract_NotesData(self):

        self.notesTitles = dict()

        notesdirectory = os.path.join(self.directoryExtracted, "Notes")

        for filename in os.listdir(notesdirectory):
            if filename == "notes.tsv":
                with open(os.path.join(notesdirectory, filename), "rb") as csvfile:
                    reader = csv.reader(csvfile, delimiter='\t', quotechar="|")

                    for row in reader:
                        if len(row) > 0:
                            title = row[0]
                            author = row[1]
                            c_date = row[2]

                            obj = datetime.strptime(c_date, "%Y-%m-%d %H:%M:%S")

                            try:
                                formatted = obj.strftime("%b %d, %Y %H:%M:%S")
                                creation_date = formatted
                            except:
                                formatted = strftime_1900.strftime_1900(obj, "%b %d, %Y %H:%M:%S")
                                creation_date = formatted

                            m_date = row[3]

                            obj = datetime.strptime(m_date, "%Y-%m-%d %H:%M:%S")

                            try:
                                formatted = obj.strftime("%b %d, %Y %H:%M:%S")
                                modification_date = formatted
                            except:
                                formatted = strftime_1900.strftime_1900(obj, "%b %d, %Y %H:%M:%S")
                                modification_date = formatted

                            note_body = row[4]
                            # note_body = strip_tags(row[4])

                            self.notesTitles[title] = [creation_date, modification_date, note_body]

    def returnNotesTitles(self):

        return self.notesTitles

    def extract_ImageData(self):
        ImagesDir = os.path.join(self.directoryExtracted, "Images")
        JPGdir = os.path.join(ImagesDir, "JPG")
        imageDict = dict()
        markers = ["blue", "green", "pink"]

        if JPGdir:
            for root, dirs, files in os.walk(JPGdir):
                for f in files:
                    if f != ".DS_Store":
                        fullpath = str(os.path.join( JPGdir, f))
                        # abs_fullpath = os.path.abspath(fullpath)

                        if fullpath not in self.imagePaths:
                            self.imagePaths.append( fullpath )
                        
                        # Verify if Image File
                        picture = Image.open(fullpath)
                        if picture:
                            # File Name
                            baseName = os.path.basename(fullpath)
                            ret = dict()

                            # Get Image File's Metadata
                            picinfo = picture._getexif()

                            if not picinfo is None:
                                for tag, val in picinfo.iteritems():
                                    decoded = TAGS.get(tag, tag)
                                    ret[decoded] = val

                            if not imageDict.has_key(baseName):
                                imageDict[baseName] = ret

        for k, v in imageDict.iteritems():
            meta = v
            # List format
            # [name, date, model, make, software, lens model]
            dateTaken = "N/A"
            software = "N/A"
            make = "N/A"
            lensmodel = "N/A"
            model = "N/A"
            
            markColor = random.choice(markers)
            try:
                # Get GPS Locations
                if meta.get("GPSInfo"):
                    lat = [float(x)/float(y) for x, y in meta["GPSInfo"][2]]
                    latref = meta["GPSInfo"][1]
                    
                    lon = [float(x)/float(y) for x, y in meta["GPSInfo"][4]]
                    lonref = meta["GPSInfo"][3]

                    # Calculate Latitude and Longitude
                    lat = lat[0] + lat[1]/60 + lat[2]/3600
                    lon = lon[0] + lon[1]/60 + lon[2]/3600
                    if latref == 'S':
                        lat = -lat
                    if lonref == 'W':
                        lon = -lon

                    self.mapData.append( [lat, lon, markColor] )


                if meta.get("DateTime"):
                    unformatted = meta.get("DateTime").encode('utf-8')
                    obj = datetime.strptime(unformatted, "%Y:%m:%d %H:%M:%S")
                    try:
                        formatted = obj.strftime("%b %d, %Y %H:%M:%S")
                        dateTaken = formatted
                    except:
                        formatted = strftime_1900.strftime_1900(obj, "%b %d, %Y %H:%M:%S")
                        dateTaken = formatted

                elif meta.get("DateTimeOriginal"):
                    unformatted = meta.get("DateTimeOriginal").encode('utf-8')
                    obj = datetime.strptime(unformatted, "%Y:%m:%d %H:%M:%S")
                    try:
                        formatted = obj.strftime("%b %d, %Y %H:%M:%S")
                        dateTaken = formatted
                    except:
                        formatted = strftime_1900.strftime_1900(obj, "%b %d, %Y %H:%M:%S")
                        dateTaken = formatted

                elif meta.get("DateTimeDigitized"):
                    unformatted = meta.get("DateTimeDigitized").encode('utf-8')
                    obj = datetime.strptime(unformatted, "%Y:%m:%d %H:%M:%S")
                    try:
                        formatted = obj.strftime("%b %d, %Y %H:%M:%S")
                        dateTaken = formatted
                    except:
                        formatted = strftime_1900.strftime_1900(obj, "%b %d, %Y %H:%M:%S")
                        dateTaken = formatted

                if meta.get("Make"):
                    make = meta.get("Make").encode('utf-8')

                if meta.get("Software"):
                    software = meta.get("Software").encode('utf-8')

                if meta.get("LensModel"):
                    lensmodel = meta.get("LensModel").encode('utf-8')

                if meta.get("Model"):
                    model = meta.get("Model").encode('utf-8')
            except:
                pass

            if [k.encode('utf-8'), dateTaken, model, make, software, lensmodel] not in self.imageTable:
                self.imageTable.append( [k.encode('utf-8'), dateTaken, model, make, software, lensmodel] )

    def returnImageTable(self):
        return self.imageTable

    def returnMapData(self):
        return self.mapData

    def returnImagePaths(self):
        return self.imagePaths

    def extract_CalendarInfo(self):

        self.calendarList = list()
        self.calendarJSON = list()

        Calendardirectory = os.path.join(self.directoryExtracted, "Calendar")

        for filename in os.listdir(Calendardirectory):
            if filename == "calendar.tsv":
                with open(os.path.join(Calendardirectory, filename), "rb") as csvfile:
                    reader = csv.reader(csvfile, delimiter='\t', quotechar="|")

                    for row in reader:
                        if row and row[0] != " ":
                            try:
                                if row[0]:
                                    event = row[0]
                                else:
                                    event = "N/A"
                            
                                if row[1] and row[1] != "None":
                                    unformatted = row[1]
                                    obj = datetime.strptime(unformatted, "%Y-%m-%d %H:%M:%S")
                                    try:
                                        startDateList = obj.strftime("%b %d, %Y %H:%M:%S")
                                        startDateJSON = obj.strftime("%Y-%m-%dT%H:%M:%S")
                                    except:
                                        startDateList = strftime_1900.strftime_1900(obj, "%b %d, %Y %H:%M:%S")
                                        startDateJSON = obj.isoformat()
                                else:
                                    startDateList = "N/A"
                                    startDateJSON = "N/A"

                                if row[2] and row[2] != "None":
                                    unformatted2 = row[2]
                                    obj2 = datetime.strptime(unformatted2, "%Y-%m-%d %H:%M:%S")
                                    try:
                                        endDateList = obj2.strftime("%b %d, %Y %H:%M:%S")
                                        endDateJSON = obj2.strftime("%Y-%m-%dT%H:%M:%S")
                                    except:
                                        endDateList = strftime_1900.strftime_1900(obj2, "%b %d, %Y %H:%M:%S")
                                        endDateJSON = obj2.isoformat()
                                else:
                                    endDateList = "N/A"
                                    endDateJSON = "N/A"
                                
                                if len(row) > 3:
                                    if row[3] == 'None':
                                        location = "N/A"
                                    else:
                                        location = row[3]
                                else:
                                    location = "N/A"

                                if len(row) > 4:
                                    if row[4] == 'None':
                                        description = "N/A"
                                    else:
                                        description = row[4]
                                else:
                                    description = "N/A"
                                
                                if len(row) > 5:
                                    if row[5] == 'None':
                                        start_timezone = "N/A"
                                    else:
                                        start_timezone = row[5]
                                else:
                                    start_timezone = "N/A"

                                if len(row) > 6:
                                    if row[6] == 'None':
                                        end_timezone = "N/A"
                                    else:
                                        end_timezone = row[6]
                                else:
                                    end_timezone = "N/A"

                                if len(row) > 7:
                                    if row[7] == 'None':
                                        calendar_type = "N/A"
                                    else:
                                        calendar_type = row[7]
                                else:
                                    calendar_type = "N/A"

                                if len(row) > 8:
                                    if row[8] == 'None':
                                        ownerEmail = "N/A"
                                    else:
                                        ownerEmail = row[8]
                                else:
                                    ownerEmail = "N/A"

                                self.calendarList.append( [event, startDateList, endDateList, location, description, start_timezone, end_timezone, calendar_type, ownerEmail] )
                                self.calendarJSON.append( {'title': event, 'start': startDateJSON, 'end': endDateJSON, 'location': location, 'description': description, "start_timezone":start_timezone, "end_timezone":end_timezone, "calendar_type":calendar_type, "ownerEmail":ownerEmail})

                            except:
                                print " ****** extraction.py ****** "
                                print "Calendar Data Extraction Error"
                                print row

                            


        return [self.calendarList, self.calendarJSON]

    def extract_ContactsInfo(self):

        # Key: Phone Number --> Value: Full Name of Contact
        self.contactsDict = dict()

        Contactsdirectory = os.path.join(self.directoryExtracted, "Contacts")

        for filename in os.listdir(Contactsdirectory):
            if filename == "contacts.tsv":
                with open(os.path.join(Contactsdirectory, filename), "rb") as csvfile:
                    reader = csv.reader(csvfile, delimiter='\t', quotechar="|")

                    for row in reader:
                        if row and row[0] != " ":
                            if row[1] != "N/A":
                                fullName = row[0] + " " + row[1]
                            else:
                                fullName = row[0]

                            allNums = row[2].split()

                            for item in allNums:
                                if not self.contactsDict.has_key(item):
                                    self.contactsDict[item] = fullName

    def extract_CallInfo(self):
        callDict = dict()

        self.allCalls = list()

        Callsdirectory = os.path.join(self.directoryExtracted, "Calls")

        for filename in os.listdir(Callsdirectory):
            if filename == "calls.tsv":
                with open(os.path.join(Callsdirectory, filename), "rb") as csvfile:
                    reader = csv.reader(csvfile, delimiter='\t', quotechar="|")

                    for row in reader:
                        if row and row[0] != " ":
                            num = row[0]

                            date = row[1]
                            obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                            try:
                                formatted = obj.strftime("%b %d, %Y %H:%M:%S")
                            except:
                                formatted = strftime_1900.strftime_1900(obj, "%b %d, %Y %H:%M:%S")

                            calltype = row[2]
                            duration = row[3]

                            if self.contactsDict.has_key(num):
                                name = self.contactsDict[num]
                            else:
                                name = "N/A"

                            self.allCalls.append( [name, num, formatted, calltype, duration] )

                            if self.contactsDict.has_key(num):
                                name = self.contactsDict[num]

                                if callDict.has_key(name):
                                    callDict[name] += 1
                                else:
                                    callDict[name] = 1
                            else:
                                if callDict.has_key(num):
                                    callDict[num] += 1
                                else:
                                    callDict[num] = 1
        
        self.numPeopleCalled = len(callDict)

        top10 = dict()
        for key, val in sorted(callDict.iteritems(), key=lambda (k, v): (-v, k))[:10]:
            top10[key] = val

        return top10

    def returnCallsTable(self):
        return self.allCalls

    def returnPeopleCalled(self):
        return self.numPeopleCalled


    def extract_SMSInfo(self):
        # Key: Phone Number --> Value: list [0]-numberoftexts [1:]-all datetimes
        numberDict = dict()

        sentReceivedDict = dict()

        self.SMStableList = list()

        SMSdirectory = os.path.join(self.directoryExtracted, "SMS")

        for filename in os.listdir(SMSdirectory):
            temp = os.path.join(SMSdirectory, "sms.tsv")
            if filename == "sms.tsv":
                if os.stat( temp ).st_size != 0:
                    with open(os.path.join(SMSdirectory, filename), "rU") as csvfile:
                        reader = csv.reader(csvfile, delimiter='\t', quotechar="|")

                        for row in reader:
                            if row and row[0] != " ":
                                sent_rec = row[0]
                                date = row[1]
                                phoneNum = row[2]
                                text = row[3]

                                obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

                                try:
                                    formatted = obj.strftime("%b %d, %Y %H:%M:%S")
                                except:
                                    formatted = strftime_1900.strftime_1900(obj, "%b %d, %Y %H:%M:%S")


                                if self.contactsDict.has_key(phoneNum):
                                    name = self.contactsDict[phoneNum]
                                else:
                                    name = "N/A"

                                self.SMStableList.append( [name, phoneNum, sent_rec, formatted, text] )

                                if self.contactsDict.has_key(phoneNum):
                                    name = self.contactsDict[phoneNum]

                                    if numberDict.has_key(name):
                                        numberDict[name] += 1
                                    else:
                                        numberDict[name] = 1
                                else:
                                    if numberDict.has_key(phoneNum):
                                        numberDict[phoneNum] += 1
                                    else:
                                        numberDict[phoneNum] = 1

        self.numPeopleSMS = len(numberDict)
        top10 = dict()

        for key, val in sorted(numberDict.iteritems(), key=lambda (k, v): (-v, k))[:10]:
            top10[key] = val

        return top10

    def returnSMSTable(self):
        return self.SMStableList

    def returnPeopleSMS(self):
        return self.numPeopleSMS

