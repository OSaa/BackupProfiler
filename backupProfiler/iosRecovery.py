import optparse
import os
import shutil
import sqlite3
import sys
import mimetypes
import re
import xml.etree.ElementTree as ET

from PIL import Image
from shutil import copyfile

from datetime import datetime

import plistlib
import biplist
import hashlib

#http://stackoverflow.com/questions/1342000/how-to-replace-non-ascii-characters-in-string
#thanks Fortran (the user not the language); http://stackoverflow.com/users/106979/fortran
def removeNonAscii(s):
    return "".join(i for i in s if ord(i)<128) 


#http://stackoverflow.com/questions/266648/python-check-if-uploaded-file-is-jpg
#thanks user Brian; http://stackoverflow.com/users/9493/brian
def is_jpg(filename):
    data = open(filename,'rb').read(11)
    if data[:4] != '\xff\xd8\xff\xe0': return False
    return True

#same as above just changed the magic number to find png
def is_png(filename):
    data = open(filename,'rb').read(11)
    if data[:4] != '\x89\x50\x4e\x47': return False
    return True

#same as above just changed the magic number to find .amr files
def is_amr(filename):
    data = open(filename,'rb').read(18)
    if data[:6] != '\x23\x21\x41\x4d\x52\x0A': return False
    return True


def getVoiceMail(bckupPath, destPath):
    try:
        
        for i in os.listdir(bckupPath):
            file_to_check = os.path.join(bckupPath, i)

                        
            if is_amr(file_to_check):
                copyfile(file_to_check, destPath + i + '.amr')
                continue
    
    except:
        print "** Voicemail Error **"

    
#Target of Evaluation (TOE), user may want to run this script against many backups
#from the same phone or many backups from different phones.  This will create a unique
#unique directory for each backup.
#nameing sceme: iPhone ser# -- Date/Time 

def TOE(plist):
    #code taken from http://docs.python.org/2/library/xml.etree.elementtree.html
    try:
    
        try:
            info = plistlib.readPlist(plist)
        except:
            try:
                info = biplist.readPlist(plist)
            except:
                print "Cannot read Info.plist for app data"
        
        guid = info.get("GUID")

        backupdate = info.get("Last Backup Date").strftime('%Y-%m-%d-%H-%M-%S')

        targetDir = os.path.join("static/backups", guid + '--' + backupdate)

        return targetDir

    except:
        print "iosRecovery.py: Info.plist error"
        return "None"


def getImages(bckupPath, JPG, PNG):
    
    try:
        
        for i in os.listdir(bckupPath):
            file_to_check = os.path.join(bckupPath, i)
            
            if is_jpg(file_to_check):
                copyfile(file_to_check, JPG + i + '.jpg')
                continue
            
            if is_png(file_to_check):
                copyfile(file_to_check, PNG + i + '.png')
            
    except:
        print "** Images Error **"
 
def getSMS(msgDB, destPath):
    try:
        copyfile(msgDB, destPath + 'sms.sqlite')

        f = open(destPath + "sms.tsv", 'w')

        conn = sqlite3.Connection(msgDB)
        c = conn.cursor()
        
        #old ios backup structure (pre- ios 6)
        #c.execute('select is_from_me as \'sent\',datetime (date, \'unixepoch\', \'31 years\',\'utc\'), \
        #          address, text from message WHERE address>0;')

        #current iPhone backup structure
        try:
            c.execute('SELECT is_from_me as \'sent\',datetime (date, \'unixepoch\', \'31 years\',\'utc\'),id, text \
                      FROM message , handle \
                      WHERE message.handle_id = handle.rowid ORDER by date;')
        except:
            print "SMS DB Invalid Format"
            
        for row in c:
            orig = row[0]
            date = str(row[1])
            addr = str(row[2])
            
            #Some text in newer iOSs contain unicode, but some texts are empty
            #so each query return must be checked through a loop and fail gracefully
            #if empty

            if row[3] == None:
                text = 'N/A'
            else:
                text = removeNonAscii(row[3]).replace('\n', ' ').replace('\t', ' ').encode("utf-8")

            #Need to know if the text was sent or recived by the iPhone owner
            if orig:
                sent = "Sent"
            else:
                sent = "Received"
                
            r = '\n' + sent + '\t' + date + "\t" + addr + "\t" + text
            f.write(r)

    except:
        print "** SMS Error **"
        print row
    
    conn.close()
    f.close()
    
def getContacts(msgDB, destPath):

    f = open(destPath + "contacts.tsv", 'w')

    copyfile(msgDB, destPath + 'Contacts.sqlite')


    conn = sqlite3.Connection(msgDB)
    c = conn.cursor()
    
    
    c.execute('SELECT  c0First, c1Last, c15Phone, c16email from ABPersonFullTextSearch_content;')
    
    try:
        for row in c:
            if row[0]:
                fName = str(row[0].encode("utf-8"))
            else:
                fName = "N/A"

            if row[1]:
                subs = row[1]
                lName = str(subs.encode("utf-8"))
                if not lName or lName == " ":
                    lName = "N/A"
            else:
                lName = "N/A"

            if row[2]:
                # Clean up phone number
                phone = str(row[2].encode('utf-8'))

                splitPhone = phone.split()
                
                if len(splitPhone[0]) < 10 and len(splitPhone) > 3:

                    complete = splitPhone[0] + splitPhone[1]

                    temp = " ".join(splitPhone[2:])

                    phone = complete + " " + temp

                    if len(complete) < 10  or complete[:3] == "011":
                        complete = splitPhone[0] + splitPhone[1] + splitPhone[2]

                        temp2 = " ".join(splitPhone[3:])

                        phone = complete + " " + temp2

                        if len(complete) < 10:
                            complete = splitPhone[0] + splitPhone[1] + splitPhone[2] + splitPhone[3]

                            temp3 = " ".join(splitPhone[4:])

                            phone = complete + " " + temp2
                
                if not phone or phone == " ":
                    phone = "N/A"
            else: 
                phone = "N/A"

            if row[3]:
                email = str(row[3].encode('utf-8'))
            else:
                email = "N/A"

            r = '\n' + fName + '\t'+ lName +'\t' + phone + '\t' + email

            f.write(r)

    except:
        print "** Contacts Error **"
        print row
    
        conn.close()
        f.close()

def getCalendar(msgDB, destPath):

    f = open(destPath + "calendar.tsv", 'w')
    
    try:
        copyfile(msgDB, destPath + 'Calendar.sqlite')
        conn = sqlite3.Connection(msgDB)
        calItem_cursor = conn.cursor()
        loc_cursor = conn.cursor()
        calID = conn.cursor()
        
        try:
            calItem_cursor.execute('SELECT  summary, datetime(start_date, \'unixepoch\', \'31 years\',\'utc\'), datetime(end_date, \'unixepoch\', \'31 years\',\'utc\'), location_id, description, start_tz, end_tz, calendar_id  from CalendarItem;')
        except:
            print "Calendar Invalid Format"

        for row in calItem_cursor:
            try:
                summary = str((row[0].replace('\n',' ').replace('\t', ' ')).encode('utf-8'))

                if summary == ' ' or summary == '' or summary == None:
                    summary = "N/A"

                StartDate = str(row[1])
                EndDate = str(row[2])
                location = ""
                description = ""
                calendarType = ""
                ownerEmail = ""

                if row[3] > 0 and row[3]:
                    for item in loc_cursor.execute("SELECT title FROM Location WHERE ROWID=?;", (row[3],) ):
                        if item[0]:
                            location = str(item[0].replace('\n', ' ').replace('\t', ' '))
                        else:
                            location = "N/A"
                else:
                    location = "N/A"

                if row[4]:
                    description = str( removeNonAscii( row[4].replace('\n', ' ').replace('\t', ' ') ) ).encode('utf-8')
                else:
                    description = "N/A"

                if row[5] != "_float":
                    start_timezone = str(row[5])
                else:
                    start_timezone = "N/A"

                if row[6] != "_float":
                    end_timezone = str(row[6])
                else:
                  end_timezone = "N/A"  


                if row[7]:
                    for item2 in calID.execute("SELECT title, owner_identity_email FROM Calendar WHERE ROWID=?", (row[7],) ):
                        calendarType = str(item2[0])
                        ownerEmail = str(item2[1])
                else:
                    calendarType = "N/A"
                    ownerEmail = "N/A"

                r= '\n' + summary + '\t'+ StartDate +'\t'+ EndDate + '\t' + location + '\t' + description + '\t' + start_timezone + '\t' + end_timezone + '\t' + calendarType + '\t' + ownerEmail
                f.write(r)
            except:
                print "Calendar Row Error"
                print row

    except:
        print "Calendar Error"
    
    conn.close()
    f.close()

def getNotes(msgDB, destPath):
    f = open(destPath + "notes.tsv", 'w')
    
    try:
        copyfile(msgDB, destPath + 'notes.sqlite')
        conn = sqlite3.Connection(msgDB)
        znote_cursor = conn.cursor()
        zbody_cursor = conn.cursor()

        try:
            znote_cursor.execute('SELECT zbody, datetime(zcreationdate, \'unixepoch\',\'31 years\',\'utc\'), datetime(zmodificationdate, \'unixepoch\',\'31 years\',\'utc\'), zauthor, ztitle from znote')
        except:
            print "Error reading ZNOTE for Notes data"
            pass

        for row in znote_cursor:
            zbody_id = str(row[0])
            creation_date = row[1]
            modification_date = row[2]

            if row[3] == None:
                author = "N/A"
            else:
                author = str(row[3])

            title = str(row[4])

            try:
                for item in zbody_cursor.execute('SELECT zcontent FROM znotebody WHERE z_pk=?;', (zbody_id, ) ):
                    note_body = removeNonAscii( item[0] ).replace('\n', ' ').replace('\t', ' ').encode('utf-8')
            except:
                print "Error reading ZNOTEBODY for Notes data"
                pass
            
            r = '\n' + title + '\t' + author + '\t' + creation_date + '\t' + modification_date + '\t' + note_body
            
            f.write(r)

    except:
        print "Notes Error"
        print row
    
    conn.close()
    f.close()

def getCalls(msgDB, destPath):

    f = open(destPath + "calls.tsv", 'w')
    
    try:
        copyfile(msgDB, destPath + 'Calls.sqlite')
        conn = sqlite3.Connection(msgDB)

        c = conn.cursor()
        
        c.execute('SELECT  address, datetime(date, \'unixepoch\',\'utc\'), flags, duration from call;')

        for row in c:
            address = str(row[0])
            Date = str(row[1])
            flag = row[2]
            duration = str(row[3])

            #Need to know if phone call and facetime is inbound or outbound
            if flag == 4:
                flag = "Incoming Call"
            if flag == 0:
                flag = "Incoming Call"
            elif flag == 5:
                flag = "Outgoing Call"
            elif flag == 9:
                flag = "Outgoing Call"
            elif flag == 8:
                flag = "Blocked"
            elif flag == 16:
                flag = "Incoming Facetime"
            elif flag == 17:
                flag = "Outgoing Facetime"
            else:
                flag = "N/A"
            
            r = '\n' + address + '\t'+ Date + '\t' + flag + '\t' + duration
            
            f.write(r)

    except:
        print "** Calls Error **"
        print row
    
    conn.close()
    f.close()

def getAppFiles(infoplist, backupDir, AppFiles):

    # Get files in backup
    fileList = list()
    for root, dirs, files in os.walk(backupDir):
        for filename in os.listdir(backupDir):
            fullpath = os.path.join(backupDir, filename)
            if os.path.isfile(fullpath):
                fileList.append(filename)
        
    
    encryptedDict = dict()

    try:
        info = plistlib.readPlist(infoplist)
    except:
        try:
            info = biplist.readPlist(infoplist)
        except:
            print "Cannot read Info.plist for app data"

    InstalledApps = info.get("Installed Applications")

    for app in InstalledApps:
        data = ("AppDomain-" + app + "-Library/Preferences/" + app + ".plist")
        data = hashlib.sha1(data).hexdigest()
        if (not encryptedDict.has_key(data)):
            encryptedDict[data] = app

    for plistName in fileList:
        if encryptedDict.has_key(plistName):
            if not os.path.exists( AppFiles + plistName + ".plist"):
                fullPath = os.path.join(backupDir, plistName)
                shutil.copy(fullPath, AppFiles)
                appFolder = AppFiles + plistName
                newname = os.rename(appFolder, appFolder + ".plist")
        
        elif encryptedDict.has_key(plistName[:-6]):
            fullPath = os.path.join(backupDir, plistName)
            shutil.copy(fullPath, AppFiles)

    # 37d957bda6d8be85555e7c0a7d30c5a8bc1b5cce - Recent Searches
    # ed50eadf14505ef0b433e0c4a380526ad6656d3a - Web History Dates
    # 4f6a6e175b8b087c833905bcc4e304d1389ae7b4 - Weather Cities
    # 691fe25b949227d26b6c59432bf108f6e3ec54ec - Stocks Data
    # 3ea0280c7d1bd352397fc658b2328a7f3b124f3b - Signatures
    # ade0340f576ee14793c607073bd7e8e409af07a8 - List of known networks
    # 51a4616e576dd33cd2abadfea874eb8ff246bf0e - Keychain Data

    dataPlists = ["51a4616e576dd33cd2abadfea874eb8ff246bf0e", "ade0340f576ee14793c607073bd7e8e409af07a8", "5ceceae7e957a53682cf500e5dd9499b5e2278aa", "3ea0280c7d1bd352397fc658b2328a7f3b124f3b", "691fe25b949227d26b6c59432bf108f6e3ec54ec", "4f6a6e175b8b087c833905bcc4e304d1389ae7b4", "37d957bda6d8be85555e7c0a7d30c5a8bc1b5cce", "ed50eadf14505ef0b433e0c4a380526ad6656d3a"]

    for plist in dataPlists:
        if plist in fileList:
            if not os.path.exists( AppFiles + plist + ".plist"):
                fullPath = os.path.join(backupDir, plist)
                shutil.copy(fullPath, AppFiles)

                appFolder = os.path.join(AppFiles, plist)
                newname = os.rename(appFolder, appFolder + ".plist")

def getint(data, offset, intsize):
    """Retrieve an integer (big-endian) and new offset from the current offset"""
    value = 0
    while intsize > 0:
        value = (value<<8) + ord(data[offset])
        offset = offset + 1
        intsize = intsize - 1
    return value, offset

def getstring(data, offset):
    """Retrieve a string and new offset from the current offset into the data"""
    if data[offset] == chr(0xFF) and data[offset+1] == chr(0xFF):
        return '', offset+2 # Blank string
    length, offset = getint(data, offset, 2) # 2-byte length
    value = data[offset:offset+length]
    return value, (offset + length)

def process_mbdb_file(filename, mbdx):
    mbdb = {} # Map offset of info in this file => file info
    data = open(filename).read()
    if data[0:4] != "mbdb": raise Exception("This does not look like an MBDB file")
    offset = 4
    offset = offset + 2 # value x05 x00, not sure what this is
    while offset < len(data):
        fileinfo = {}
        fileinfo['start_offset'] = offset
        fileinfo['domain'], offset = getstring(data, offset)
        fileinfo['filename'], offset = getstring(data, offset)
        fileinfo['linktarget'], offset = getstring(data, offset)
        fileinfo['datahash'], offset = getstring(data, offset)
        fileinfo['unknown1'], offset = getstring(data, offset)
        fileinfo['mode'], offset = getint(data, offset, 2)
        fileinfo['unknown2'], offset = getint(data, offset, 4)
        fileinfo['unknown3'], offset = getint(data, offset, 4)
        fileinfo['userid'], offset = getint(data, offset, 4)
        fileinfo['groupid'], offset = getint(data, offset, 4)
        fileinfo['mtime'], offset = getint(data, offset, 4)
        fileinfo['atime'], offset = getint(data, offset, 4)
        fileinfo['ctime'], offset = getint(data, offset, 4)
        fileinfo['filelen'], offset = getint(data, offset, 8)
        fileinfo['flag'], offset = getint(data, offset, 1)
        fileinfo['numprops'], offset = getint(data, offset, 1)
        fileinfo['properties'] = {}
        for ii in range(fileinfo['numprops']):
            propname, offset = getstring(data, offset)
            propval, offset = getstring(data, offset)
            fileinfo['properties'][propname] = propval
        mbdb[fileinfo['start_offset']] = fileinfo
        fullpath = fileinfo['domain'] + '-' + fileinfo['filename']
        id = hashlib.sha1(fullpath)
        mbdx[fileinfo['start_offset']] = id.hexdigest()
    return mbdb

def modestr(val):
    def mode(val):
        if (val & 0x4): r = 'r'
        else: r = '-'
        if (val & 0x2): w = 'w'
        else: w = '-'
        if (val & 0x1): x = 'x'
        else: x = '-'
        return r+w+x
    return mode(val>>6) + mode((val>>3)) + mode(val)

def fileinfo_str(f, verbose=False):
    if not verbose: return "(%s)%s::%s" % (f['fileID'], f['domain'], f['filename'])
    if (f['mode'] & 0xE000) == 0xA000: type = 'l' # symlink
    elif (f['mode'] & 0xE000) == 0x8000: type = '-' # file
    elif (f['mode'] & 0xE000) == 0x4000: type = 'd' # dir
    else: 
        print >> sys.stderr, "Unknown file type %04x for %s" % (f['mode'], fileinfo_str(f, False))
        type = '?' # unknown
    info = ("%s%s %08x %08x %7d %10d %10d %10d (%s)%s::%s" % 
            (type, modestr(f['mode']&0x0FFF) , f['userid'], f['groupid'], f['filelen'], 
             f['mtime'], f['atime'], f['ctime'], f['fileID'], f['domain'], f['filename']))
    if type == 'l': info = info + ' -> ' + f['linktarget'] # symlink destination
    for name, value in f['properties'].items(): # extra properties
        info = info + ' ' + name + '=' + repr(value)
    return info

def parse_output(backup_dir, dbsDIR):
    with open(dbsDIR + "/manifest_output.txt", "r") as f:

        # DBs that have already been extracted (i.e. SMS.db)
        knownSHAs = ['3d0d7e5fb2ce288813306e4d4636395e047a3d28', '31bb7ba8914766d4ba40d6dfb6113c8b614be442', '2041457d5fe04d39d0ab481178355df6781e6858', '2b2b0084a1bc3a5ac8c27afdf14afb42c61a19ca', 'ca3bc056d4da0bbf88b5fb3be254f3b7147e639c' ]

        for line in f:

            if line[-4:] == "sql\n" or line[-9:] == "sqlitedb\n" or line[-7:] == "sqlite\n" or line[-3:] == "db\n":

                # Avoid google analytics DBs, no interesting info there
                if line[-23:] != "googleanalytics-v3.sql\n" and line[-23:] != "googleanalytics-v2.sql\n" and line[-20:] != "googleanalytics.sql\n" and (line[-23:][:15] != "googleanalytics") :
                    openparen = line.index("(") + 1
                    closeparen = line.index(")")

                    dbSHA = line[openparen:closeparen]      # Getting hash on each line

                    if dbSHA not in knownSHAs:
                        fullPath = os.path.join(backup_dir, dbSHA)

                        afterparen = closeparen+1
                        filelocation = line[afterparen:]
                        templist = filelocation.split("/")

                        temp = templist[len(templist)-1][:-1]

                        app = str(filelocation.split("::")[0])

                        # Using '~' to make it easy to split later on
                        dbname = app + "~" + templist[len(templist)-1][:-1]
                        
                        if len( temp.split(".") ) > 1:
                            newPath = os.path.join(dbsDIR, dbname)

                            if not os.path.exists( newPath ):
                                shutil.copy(fullPath, dbsDIR)

                                oldDBfile = os.path.join(dbsDIR, dbSHA)
                                newDBfile = os.path.join(dbsDIR, dbname)

                                # Rename file in DBs
                                os.rename(oldDBfile, newDBfile)


def extract_mandata(backup_dir, extracted_dir):
    mbdx = {}
    verbose = True

    f = open(extracted_dir + "/manifest_output.txt", "w+")
    mbdb = process_mbdb_file(backup_dir + "/Manifest.mbdb", mbdx)

    for offset, fileinfo in mbdb.items():
        if offset in mbdx:
            fileinfo['fileID'] = mbdx[offset]
        else:
            fileinfo['fileID'] = "<nofileID>"
            f.write( "No fileID found for %s" % fileinfo_str(fileinfo) + "\n" )

        f.write( fileinfo_str(fileinfo, verbose) + "\n" )

    f.close()
    # print "manifest_output.txt created"
    parse_output(backup_dir, extracted_dir)


def main(newBackup):

    pathName = newBackup
    
    
    if pathName == None:
        exit(0)
    else:
        print " ****** iosRecovery.py ****** "
        
        dirList = os.listdir(pathName)
        SMS = os.path.join(pathName, '3d0d7e5fb2ce288813306e4d4636395e047a3d28')
        Contacts = os.path.join(pathName, '31bb7ba8914766d4ba40d6dfb6113c8b614be442')
        Calendar = os.path.join(pathName, '2041457d5fe04d39d0ab481178355df6781e6858')
        Calls = os.path.join(pathName, '2b2b0084a1bc3a5ac8c27afdf14afb42c61a19ca')
        Notes = os.path.join(pathName, 'ca3bc056d4da0bbf88b5fb3be254f3b7147e639c')
        infoPlist = os.path.join(pathName, 'Info.plist')
        
        
        # Get iPhones serial number and date/time of last backup,
        # Use it for the target directory name
        # Also get app data
        dest = TOE(infoPlist)

        if not os.path.isdir(dest):
        	if dest != "None":
		        print "directory: " + dest + " Created"
		        os.makedirs(dest)
		        
		        # Process SMS text 
		        SMSoutputdir = dest + '/SMS/'
		        os.mkdir(SMSoutputdir)
		        print "Getting SMS"
		        getSMS(SMS, SMSoutputdir)
		        print "Done Getting SMS"

		        # Proocess Address Book
		        ABputputdir = dest + '/Contacts/'
		        os.mkdir(ABputputdir)
		        print "Getting Contacts"
		        getContacts(Contacts, ABputputdir)
		        print "Done Getting Contacts"
		        
		        # Process Calendar
		        Caloutputdir = dest + '/Calendar/'
		        os.mkdir(Caloutputdir)
		        print "Getting Calendar"
		        getCalendar(Calendar, Caloutputdir)
		        print "Done Getting Calendar"
		        
		        # Process Notes
		        Notesoutputdir = dest + '/Notes/'
		        os.mkdir(Notesoutputdir)
		        print "Getting Notes"
		        getNotes(Notes, Notesoutputdir)
		        print "Done Getting Notes"
		        
		        # Process Calls
		        Calloutputdir = dest + '/Calls/'
		        os.mkdir(Calloutputdir)
		        print "Getting Call History"
		        getCalls(Calls, Calloutputdir)
		        print "Done Getting Call History"
		        
		        # Process Voicemail
		        Voicemaildir = dest + '/Voicemail/'
		        os.mkdir(Voicemaildir)
		        print "Getting VoiceMail"
		        getVoiceMail(pathName, Voicemaildir)
		        print "Done Getting VoiceMail"
		        
		        # # Process App Files
		        AppOutputdir = dest + '/AppData/'
		        os.mkdir(AppOutputdir)
		        shutil.copy(infoPlist, AppOutputdir)
		        print "Getting App Files"
		        getAppFiles(infoPlist, pathName, AppOutputdir)
		        print "Done Getting App Data"
		        
		        # Process Images
		        Imagesoutputdir = dest + '/Images/'
		        os.mkdir(Imagesoutputdir)
		        Jpgoutputdir = Imagesoutputdir + 'JPG/'
		        os.mkdir(Jpgoutputdir)
		        Pngoutputdir = Imagesoutputdir + 'PNG/'
		        os.mkdir(Pngoutputdir)
		        print "Getting Images"
		        getImages(pathName, Jpgoutputdir, Pngoutputdir)
		        print "Done Getting Images"

                if "Manifest.mbdb" in dirList:
                    dbsOutputDir = os.path.join(dest, "DBs")
                    os.makedirs(dbsOutputDir)
                    print "Getting Databases"
                    extract_mandata(pathName, dbsOutputDir)
                    print "Done Getting Databases"

                return dest
        else:
            print str(dest) + " Already Exists."
            return "Already Exists"


if __name__ == '__main__':
	main()