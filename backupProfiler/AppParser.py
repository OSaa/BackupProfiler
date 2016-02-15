import hashlib
import os
import sys
import plistlib
import biplist
import re
import csv
from datetime import datetime
import strftime_1900
import time
import collections

class BackupParser():
    
	def __init__(self, backup):
		print "Running AppParser.py"
		self.backupDir = backup

		# App Name -- App Folder Name -- Status -- Installed -- Last Used -- Number of times used(Maybe)
		self.allAppBasicData = dict()
		self.deletedAppList = list()
		self.recentSearches = dict()
		self.usernames = list()
		self.AppFolderNames = dict()
		self.safariRecentSearches = list()
		self.facebookItems = dict()

		# Initializers
		self.gasBudZips = list()
		self.groupmeReturn = dict()
		self.dunkinReturn = dict()
		self.uberReturn = dict()
		self.openTableReturn = dict()
		self.openTableRecReturn = list()
		self.appleMapReturn = dict()
		self.whatsappReturn = dict()
		self.linkedInReturn = dict()
		self.snapchatReturn = dict()
		self.snapchatFriends = list()
		self.instaReturnDict = dict()
		self.hopStopReturn = dict()
		self.hopStopRec = list()
		self.appleMailReturn = dict()
		self.gMapDict = dict()
		self.sunriseData = dict()
		self.snapChatRecent = list()


		self.openAppCSV()
		self.getInfoPlist()
		self.info_plist_parser()


	''' Make SHA1 Hash File into a plist File'''
	def renameFile(self, filename):
		fullPath = self.backupDir + "/" + filename
		newname = os.rename(fullPath, fullPath + ".plist")
		newname = fullPath + ".plist"

	def openAppCSV(self):
		fullpath = os.path.dirname(os.path.abspath(__file__))

		for filename in os.listdir(fullpath):
			if filename == "apps.csv":
				with open(os.path.join(fullpath, filename), "Ub") as csvfile:
					reader = csv.reader(csvfile, delimiter=',', quotechar="|")

					for row in reader:
						
						# row[0] app name
						# row[1] app folder
						appFolder = row[1]
						appName = row[0]
						preinstalled = row[2]
						# row[2] if preinstalled

						if not self.AppFolderNames.has_key(row[1]):
							self.AppFolderNames[appFolder] = [appName, preinstalled]

	def get_folder_name(self, folder):
		if self.AppFolderNames.has_key(folder):
			return self.AppFolderNames[folder] # returns list: [appName, preinstalled]
		else:
			return ["N/A","N/A"]

	
	def getInfoPlist(self):
		infoPlist = self.backupDir + "/Info.plist"
			
		encryptedDict = dict()

		try:
			info = biplist.readPlist(infoPlist)
		except:
			try:
				info = plistlib.readPlist(infoPlist)
			except:
				print "Error reading Info.plist"


		self.DeviceName = info.get("Device Name")
		self.LastBackupDate = info.get("Last Backup Date")
		self.ownerNumber = info.get("Phone Number")
		self.phoneType = info.get("Product Name")
		self.iOS = info.get("Product Version")
		self.serialNumber = info.get("Serial Number")
		self.uid = info.get("Unique Identifier")
		self.guid = info.get("GUID")
		
		InstalledApps = info.get("Installed Applications")

		for app in InstalledApps:
			data = ("AppDomain-" + app + "-Library/Preferences/" + app + ".plist")
			data = hashlib.sha1(data).hexdigest()
			if (not encryptedDict.has_key(data)):
				encryptedDict[data] = app
		
		LibraryApps = info.get('iTunes Settings')

		for item in LibraryApps:
			if item == "DeletedApplications":
					deletedApps = LibraryApps["DeletedApplications"]
					for dapp in deletedApps:
						self.deletedAppList.append(dapp)


		return encryptedDict

	def deviceInfo(self):
		deviceData = list()

		deviceData.append( self.DeviceName )
		deviceData.append( self.LastBackupDate )
		deviceData.append( self.ownerNumber )
		deviceData.append( self.phoneType )
		deviceData.append( self.iOS )
		deviceData.append( self.serialNumber )
		deviceData.append( self.uid )
		deviceData.append( self.guid )

        return deviceData

    ''' Retrieve all files in backup directory '''
    def retrieveBackupFiles(self):
        # All Files in Backup Folder
        fileList = list()
        for root, dirs, files in os.walk(self.backupDir):
            for filename in os.listdir(self.backupDir):
                fullpath = os.path.join(self.backupDir, filename)
                if os.path.isfile(fullpath):
                    fileList.append(filename)

        return fileList

    ''' Use both methods to open Plist in case it is a binary plist or not '''
    def openPlists(self, filename):

        try:
            tryFile = biplist.readPlist(self.backupDir + "/" + filename)
            return tryFile
        except:
            try:
                tryFile = plistlib.readPlist(self.backupDir + "/" + filename)
                return tryFile
            except:
                # print "Error reading file: " + filename
                pass

    def mobilemeApp2(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("lastUsername"):
                appData["email"] = pfileInfo.get("lastUsername")
                self.usernames.append( ["Mobile Me", appData["email"] ] )

            (appName, pre) = self.get_folder_name(folder)

            appData["installDate"] = "N/A"
            appData["lastUsed"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

        except:
            pass
            # print "Error reading: " + folder

    def mobileMeApp(self, plistName, folder):
        try:
            appData = dict()

            # Open Plist file
            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("lastUsedUsername"):
                appData["email1"] = pfileInfo.get("lastUsedUsername")

                self.usernames.append( [ "Mobile Me", appData["email1"] ] )

            if (pfileInfo["lastLoggedInUsername"]):
                appData["email2"] = pfileInfo["lastLoggedInUsername"]
                self.usernames.append( ["Mobile Me", appData["email2"]] )

            appData["installDate"] = "N/A"
            appData["lastUsed"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def iStudiezApp(self, plistName, folder):
        
        try:
            appData = dict()

            # Open Plist file
            pfileInfo = self.openPlists(plistName)

            if (pfileInfo.get("STLastSyncDateKey")):
                unfomatted = pfileInfo.get("STLastSyncDateKey")
                formatted = unfomatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted

            if (pfileInfo.get("kSyncSessionEmailKey")):
                appData["email1"] = pfileInfo.get("kSyncSessionEmailKey")
                self.usernames.append( ["iStudiez Pro", appData["email1"]] )

            if pfileInfo.get("FoundationDefaults"):

                found = pfileInfo.get("FoundationDefaults")

                for item in found:
                    if item == "SyncUserEmail":
                        appData["email2"] = found[item]
                        self.usernames.append( ["iStudiez Pro", appData["email2"]] )
                
            appData["installDate"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def fbMessengerApp(self, plistName, folder):
        try:
            appData = dict()
            
            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("FBUserAgentSystemUserAgent"):
                appData["FBbrowsers"] = pfileInfo.get("FBUserAgentSystemUserAgent")
                self.facebookItems["Facebook Messenger Browsers"] = (appData["FBbrowsers"])

            
            if pfileInfo.get("OrcaAppConfigLastUpdated"):
                unformatted = pfileInfo.get("OrcaAppConfigLastUpdated")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted

            else:
                appData["lastUsed"] = "N/A"

            appData["installDate"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]] 

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def sunRiseApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            
            if pfileInfo["DefaultCalendarID"]:
                appData["Default Calendar"] = pfileInfo["DefaultCalendarID"]
                splitted = appData["Default Calendar"].split(":")
                self.usernames.append( ["Sunrise Calendar", splitted[2] ] )

            if pfileInfo["TimezoneName"]:
                self.sunriseData["Timezone"] = pfileInfo["TimezoneName"]

            if pfileInfo["EmailClient"]:
                self.sunriseData["Email Client"] = pfileInfo["EmailClient"]

            if pfileInfo["MapClient"]:
                self.sunriseData["Map Client"] = pfileInfo["MapClient"]

            # Google Maps Version
            if pfileInfo["com.google.Maps.GMSCoreLastVersion"]:
                self.sunriseData["Google Map Version"] = pfileInfo["com.google.Maps.GMSCoreLastVersion"]

            if pfileInfo["LastUpdatedDate"]:
                unformatted = pfileInfo["LastUpdatedDate"]
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted

            else:
                appData["lastUsed"] = "N/A"

            if pfileInfo["kGMSMapsUserClientLegalCountry"]:
                self.sunriseData["Country Map"] = pfileInfo["kGMSMapsUserClientLegalCountry"]

            if pfileInfo["OpenUDID"]:
                uid = pfileInfo["OpenUDID"]

                for item in uid:
                    if item == "OpenUDID_createdTS":
                        unformatted = uid[item]
                        formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                        appData["installDate"] = formatted

            elif pfileInfo["SRInstallDate"]:
                unformatted = pfileInfo["SRInstallDate"]
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["installDate"] = formatted
            else:
                appData["installDate"] = "N/A"

            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def googleMapApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("UserCountry"):
                self.gMapDict["User Country"] = pfileInfo.get("UserCountry")

            if pfileInfo.get("UserLanguage"):
                self.gMapDict["Language"] = pfileInfo.get("UserLanguage")
            
            if pfileInfo.get("appName"):
                appData["appName"] = pfileInfo.get("appName")
            
            if pfileInfo.get("appVersion"):
                self.gMapDict["Version"] = pfileInfo.get("appVersion")
            
            if pfileInfo.get("kAZDefaultKeyAppFirstRunDate"):
                unformatted = pfileInfo.get("kAZDefaultKeyAppFirstRunDate")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["installDate"] = formatted
            else:
                appData["installDate"] = "N/A"

            if pfileInfo.get("kDefaultKeyGLSReportingLastBurstLocationLatitude"):
                self.gMapDict["Last Latitude"] = pfileInfo.get("kDefaultKeyGLSReportingLastBurstLocationLatitude")

            if pfileInfo.get("kDefaultKeyGLSReportingLastBurstLocationLongitude"):
                self.gMapDict["Last Longitude"] = pfileInfo.get("kDefaultKeyGLSReportingLastBurstLocationLongitude")

            if pfileInfo.get("kAZDefaultKeyOfflineMapLastUpdateCheckDate"):
                unformatted = pfileInfo.get("kAZDefaultKeyOfflineMapLastUpdateCheckDate")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            if pfileInfo.get("kAZDefaultKeyCountAppForeground"):
                appData["numOfTimesUsed"] = str( pfileInfo.get("kAZDefaultKeyCountAppForeground") )
            else:
                appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def mixologistApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("OpenUDID"):
                
                mixInfo = pfileInfo.get("OpenUDID")

                for item in mixInfo:
                    if item == "OpenUDID_createdTS":
                        unformatted = mixInfo["OpenUDID_createdTS"]
                        formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                        appData["installDate"] = formatted

            else:
                appData["installDate"] = "N/A"

            # Carrier Information
            if pfileInfo.get("com.mopub.carrierinfo"):

                carrierInfo = pfileInfo.get("com.mopub.carrierinfo")

                for item in carrierInfo:
                    if item == "carrierName":
                        appData["carrier"] = carrierInfo["carrierName"]

                    if item == "isoCountryCode":
                        appData["carrierCountryCode"] = carrierInfo["isoCountryCode"]

                    if item == "mobileCountryCode":
                        appData["mobileCountryCode"] = carrierInfo["mobileCountryCode"]

                    if item == "mobileNetworkCode":
                        appData["mobileNetworkCode"] = carrierInfo["mobileNetworkCode"]

            appData["lastUsed"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def APnewsApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("CSComScore-lastTransmission"):
                unformatted = pfileInfo.get("CSComScore-lastTransmission")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            if pfileInfo.get("kRegisteredLocaleDict"):

                localeData = pfileInfo.get("kRegisteredLocaleDict")

                for item in localeData:
                    if item == "locale_key":
                        appData["locale"] = localeData["locale_key"]

                    if item == "name":
                        appData["localeName"] = localeData["name"]

            if pfileInfo.get("OpenUDID"):
                udid = pfileInfo.get("OpenUDID")

                for item in udid:
                    if item == "OpenUDID_createdTS":
                        unformatted = udid[item]
                        formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                        appData["installDate"] = formatted

            elif pfileInfo.get("install_date"):
                unformatted = pfileInfo.get("install_date")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["installDate"] = formatted
            else:
                appData["installDate"] = "N/A"

            if pfileInfo.get("CSComScore-runsCount"):
                appData["numOfTimesUsed"] = str( pfileInfo.get("CSComScore-runsCount") )
            else:
                appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"


            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def fitnessPalApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("logged_in_as_username"):
                appData["Logged_in_username"] = pfileInfo.get("logged_in_as_username")
                self.usernames.append( ["Fitness Pal", appData["Logged_in_username"] ] )

            if pfileInfo.get("username"):
                appData["username"] = pfileInfo.get("username")

            if pfileInfo.get("installation_date"):
                unformatted = pfileInfo.get("installation_date")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["installDate"] = formatted
            else:
                appData["installDate"] = "N/A"

            appData["lastUsed"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]] 

            return appData

        except:
            pass
            # print "Error reading: " + plistName

    def FBapp(self, plistName, folder):
        try:
            appData = dict()
            
            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("FBUserAgentSystemUserAgent"):
                appData["FBbrowsers"] = pfileInfo.get("FBUserAgentSystemUserAgent")
                self.facebookItems["Facebook Browsers"] = (appData["FBbrowsers"])

            appData["installDate"] = "N/A"

            if pfileInfo.get("kAppiraterUseCount"):
                appData["numOfTimesUsed"] = str( pfileInfo.get("kAppiraterUseCount") )
            else:
                appData["numOfTimesUsed"] = "N/A"

            if pfileInfo.get("RefreshTableView_LastRefresh"):
                last = pfileInfo.get("RefreshTableView_LastRefresh")
                unformatted = last[14:]
                obj = datetime.strptime(unformatted, "%m/%d/%y, %I:%M %p")
                try:
                    formatted = obj.strftime("%b %d, %Y %H:%M %p")
                except:
                    formatted = strftime_1900.strftime_1900(obj, "%b %d, %Y %H:%M %p")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def sudokuApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("com.mopub.carrierinfo"):

                carrierInfo = pfileInfo.get("com.mopub.carrierinfo")

                for item in carrierInfo:
                    if item == "carrierName":
                        appData[item] = carrierInfo[item]
                    elif item == "isoCountryCode":
                        appData[item] = carrierInfo[item]
                    elif item == "mobileCountryCode":
                        appData[item] = carrierInfo[item]
                    elif item == "mobileNetworkCode":
                        appData[item] = carrierInfo[item]

            if pfileInfo.get("mad_lastDate"):
                unformatted = pfileInfo.get("mad_lastDate")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"]


            if pfileInfo.get("kAppiraterUseCount"):
                appData["numOfTimesUsed"] = str( pfileInfo.get("kAppiraterUseCount") )
            else:
                appData["numOfTimesUsed"] = "N/A"


            if pfileInfo.get("TBFlurryUsageTrackerFirstUsageDate"):
                unformatted =  pfileInfo.get("TBFlurryUsageTrackerFirstUsageDate")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["installDate"] = formatted

            else:
                appData["installDate"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def MailApp(self, plistName, folder):
        try:
            appData = dict()
            mailList = list()

            pfileInfo = self.openPlists(plistName)

            # Email addresses connected to phone
            if pfileInfo.get("LastDataProviderSubsections"):

                mailBoxes = pfileInfo.get("LastDataProviderSubsections")
                
                for mailName in mailBoxes:
                    mailList.append(mailName["name"])
                    self.usernames.append( ["Apple Mailbox", mailName["name"] ] )
                    self.appleMailReturn[ mailName["name"] ] = mailName["uniqueID"]

                appData["mailboxes"] = mailList

            if pfileInfo.get("SignatureKey"):
                appData["SignatureKey"] = pfileInfo.get("SignatureKey")

            appData["installDate"] = "Pre-Installed"
            appData["lastUsed"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + plistName

    def HopStopApp(self, plistName, folder):
        try:
            appData = dict()
            recentHistoryList = list()
            
            pfileInfo = self.openPlists(plistName)
            if pfileInfo.get("SavedTransitMapName"):
                self.hopStopReturn["Saved Transit Map"] = pfileInfo.get("SavedTransitMapName")

            if pfileInfo.get("com.hopstop.CityDataLastUpdated"):
                appData["CityDataLastUpdated"] = pfileInfo.get("com.hopstop.CityDataLastUpdated")

            if pfileInfo.get("defaultCity"):
                self.hopStopReturn["Default City"] = pfileInfo.get("defaultCity")

            if pfileInfo.get("defaultCounty"):
                self.hopStopReturn["Default County"] = pfileInfo.get("defaultCounty")

            if pfileInfo.get("lfcity"):
                self.hopStopReturn["lfcity"] = pfileInfo.get("lfcity")

            if pfileInfo.get("lfcounty"):
                self.hopStopReturn["lfcounty"] = pfileInfo.get("lfcounty")

            if pfileInfo.get("ltcity"):
                self.hopStopReturn["ltcity"] = pfileInfo.get("ltcity")

            if pfileInfo.get("ltcounty"):
                self.hopStopReturn["ltcounty"] = pfileInfo.get("ltcounty")

            if pfileInfo.get("lto"):
                self.hopStopReturn["lto"] = pfileInfo.get("lto")


            if pfileInfo.get("rhist"):

                recentHistory = pfileInfo.get("rhist")

                for rh in recentHistory:
                    if rh[-6:] == "||||||":
                            recentHistoryList.append(rh[:-6])
                            self.hopStopRec.append(rh[:-6])
                    else:
                        recentHistoryList.append(rh)
                        self.hopStopRec.append(rh)

                appData["recent_history_list"] = recentHistoryList

                self.recentSearches["HopStop"] = recentHistoryList

            appData["installDate"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"
            appData["lastUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def grubHubApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            ''' Figure out how to get key: CurrentUser_FirstLogin_iPhone-arianaanastos@gmail.com '''

            if pfileInfo.get("lastPhoneNum"):
                appData["lastPhoneNum"] = pfileInfo.get("lastPhoneNum")
            
            ''' Figure out how to get key: kLastPaymentType-5573575 which also gets payment type'''

            if pfileInfo.get("FIRST_TIME_MOBILE_TIMESTAMP"):
                unformatted = pfileInfo.get("FIRST_TIME_MOBILE_TIMESTAMP")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["installDate"] = formatted
            else:
                appData["installDate"] = "N/A"

            if pfileInfo.get("kAppiraterUseCount"):
                appData["numOfTimesUsed"] = str( pfileInfo.get("kAppiraterUseCount") )
            else:
                appData["numOfTimesUsed"] = "N/A"

            appData["lastUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def irisApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("OpenUDID"):

                uidInfo = pfileInfo.get("OpenUDID")

                for item in uidInfo:
                    if item == "OpenUDID_createdTS":
                        # Get install date
                        unformatted = uidInfo["OpenUDID_createdTS"]
                        formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                        appData["installDate"] = formatted
            else:
                appData["installDate"] = "N/A"

            if pfileInfo.get("lastLogin"):
                appData["LastUsername"] = pfileInfo.get("lastLogin")
                self.usernames.append( ["Iris", appData["LastUsername"] ] )

            appData["lastUsed"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def instaApp(self, plistName, folder):
        try:
            appData = dict()
            recentHashList = list()
            visitedHashList = list()
            flaggedList = list()

            pfileInfo = self.openPlists(plistName)

            # Get install date
            if pfileInfo.get("ds-app-install-date"):
                unformatted = pfileInfo.get("ds-app-install-date")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["installDate"] = formatted
            else:
                appData["installDate"] = "N/A"


            if pfileInfo.get("flagged_comments"):

                flagged = pfileInfo.get("flagged_comments")

                for key, val in flagged.iteritems():
                    flaggedList.append( val )

                self.instaReturnDict["Flagged Comments"] = flaggedList
                appData["flaggedList"] = flaggedList


            if pfileInfo.get("last-logged-in-username"):
                appData["LastUsername"] = pfileInfo.get("last-logged-in-username")
                self.usernames.append( ["Instagram", appData["LastUsername"] ] )


            if pfileInfo.get("recent-hashtags"):

                recentHashTags = pfileInfo.get("recent-hashtags")

                for tag in recentHashTags:
                    recentHashList.append(tag)

                self.instaReturnDict["Recent Hashtags"] = recentHashList
                self.recentSearches["Instagram Recent Hashtags"] = recentHashList

                appData["Recent_Hash_List"] = recentHashList


            if pfileInfo.get("visited-hashtags"):

                visitedHashTags = pfileInfo.get("visited-hashtags")

                for has in visitedHashTags:
                    visitedHashList.append(has)

                self.instaReturnDict["Visited Hashtags"] = visitedHashList
                self.recentSearches["Instagram Visited Hashtags"] = visitedHashList

                appData["Visited_Hash_List"] = visitedHashList


            if pfileInfo.get("kAppiraterUseCount"):
                appData["numOfTimesUsed"] = str( pfileInfo.get("kAppiraterUseCount") )
            else:
                appData["numOfTimesUsed"] = "N/A"


            if pfileInfo.get("last_main_feed_fetch"):
                unformatted = pfileInfo.get("last_main_feed_fetch")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def snapChatApp(self, plistName, folder):
        try:
            appData = dict()
            bestFriendList = list()
            blockedList = list()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("LastLoginUsername"):
                appData["LastUsername"] = pfileInfo.get("LastLoginUsername")
                self.usernames.append( ["Snapchat", appData["LastUsername"] ] )

            if pfileInfo.get("LatestFriendStoryTimestamp"):
                appData["LatestFriendStoryTimestamp"] = pfileInfo.get("LatestFriendStoryTimestamp")

            if pfileInfo.get("name"):
                appData["DisplayName"] = pfileInfo.get("name")

            ''' Could get carrier info but need to iterate through keys - also has username '''
            
            # User Info
            if pfileInfo.get("userInfo"):

                userInfo = pfileInfo.get("userInfo")

                for item in userInfo:
                    if item == "bests":
                        # list of best friends snapchat usernames
                        bestFriendList.append(userInfo[item])
                        self.snapchatReturn["Best Friends"] = bestFriendList
                        appData["bestfriendlist"] = bestFriendList

                    elif item == "blocked":
                        # list of blocked snapchat usernames
                        blockedList.append(userInfo[item])
                        self.snapchatReturn["Blocked List"] = blockedList
                        appData["blockedlist"] = blockedList

                    elif item == "email":
                        # user's email
                        temp = list()
                        appData["email"] = userInfo[item]
                        temp.append( [appData["email"]] )
                        self.snapchatReturn["User Email"] = temp

                    elif item == "mobile":
                        # user's phone number
                        temp2 = list()
                        appData["number"] = userInfo[item]
                        temp2.append( [ appData["number"] ] )
                        self.snapchatReturn["User Phone Number"] = temp2

                    elif item == "friends_map":
                        # User's contacts with snapchat
                        appData["friendsDict"] = userInfo[item]
                        temp = appData["friendsDict"]
                        for key in temp:
                            self.snapchatFriends.append( [key, temp[key] ] )

                    elif item == "rec":
                        # recent people snapchatted
                        appData["recentlist"] = userInfo[item]
                        for item in appData["recentlist"]:
                            self.snapChatRecent.append(item)

            appData["installDate"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            if pfileInfo.get("EGORefreshTableView_LastRefresh"):
                last = pfileInfo.get("EGORefreshTableView_LastRefresh")
                unformatted = last[14:]
                obj = datetime.strptime(unformatted, "%m/%d/%y, %I:%M %p")
                try:
                    formatted = obj.strftime("%b %d, %Y %H:%M %p")
                except:
                    formatted = strftime_1900.strftime_1900(obj, "%b %d, %Y %H:%M %p")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def linkedInApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)
            
            # OR - userInfo = pfileInfo.get("userObject") not sure which one, both have same data
            if pfileInfo.get("com.brick.userObject"):

                userInfo = pfileInfo.get("com.brick.userObject")

                for item in userInfo:
                    if item == "email":
                        self.linkedInReturn["Email"] = userInfo[item]
                        self.usernames.append( ["LinkedIn", self.linkedInReturn["Email"] ] )

                    elif item == "formattedName":
                        self.linkedInReturn["Full Name"] = userInfo[item]

                    elif item == "firstName":
                        self.linkedInReturn["First Name"] = userInfo[item]

                    elif item == "lastName":
                        self.linkedInReturn["Last Name"] = userInfo[item]


                    elif item == "headline":
                        self.linkedInReturn["Title"] = userInfo[item]

                    elif item == "picture":
                        self.linkedInReturn["Profile Picture URL"] = userInfo[item]

                    elif item == "profileUrl":
                        self.linkedInReturn["Profile URL"] = userInfo[item]

            appData["installDate"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"
            appData["lastUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def whatsApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("AcctType"):
                self.whatsappReturn["Account Type"] = pfileInfo.get("AcctType")

            if pfileInfo.get("CurrentStatusText"):
                self.whatsappReturn["Current Status"] = pfileInfo.get("CurrentStatusText")

            if pfileInfo.get("FullUserName"):
                self.whatsappReturn["Full Username"] = pfileInfo.get("FullUserName")
                self.usernames.append( ["Whatsapp", self.whatsappReturn["Full Username"] ] )

            if pfileInfo.get("SrvCurr"):
                self.whatsappReturn["Service Currency"] = pfileInfo.get("SrvCurr")

            if pfileInfo.get("SrvType"):
                self.whatsappReturn["Service Type"] = pfileInfo.get("SrvType")

            if pfileInfo.get("SrvPrice"):
                self.whatsappReturn["Service Price"] = pfileInfo.get("SrvPrice")

            if pfileInfo.get("UserAgent"):
                self.whatsappReturn["User Agent"] = pfileInfo.get("UserAgent")

            if pfileInfo.get("lastAutoBackupDate"):
                unformatted = pfileInfo.get("lastAutoBackupDate")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            appData["installDate"] = "N/A"

            if pfileInfo.get("LogCounter"):
                appData["numOfTimesUsed"] = str( pfileInfo.get("LogCounter") )
            else:
                appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"


            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def seamlessApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            emailList = list()

            if pfileInfo.get("Seamless_AmobeeAlphaArray"):

                userEmails = pfileInfo.get("Seamless_AmobeeAlphaArray")

                for item in userEmails:
                    match = re.search('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', item)
                    if match:
                        emailList.append(match.group())

                appData["emailList"] = emailList


            if pfileInfo.get("currentUserOrderCount"):
                appData["orderCount"] = pfileInfo.get("currentUserOrderCount")

            if pfileInfo.get("username"):
                appData["username"] = pfileInfo.get("username")
                self.usernames.append( ["Seamless", appData["username"] ] )

            if pfileInfo.get("user_password"):
                appData["user_password"] = pfileInfo.get("user_password")

            if pfileInfo.get("userType"):
                appData["userType"] = pfileInfo.get("userType")

            appData["installDate"] = "N/A"
            appData["lastUsed"] = "N/A"

            if pfileInfo.get("kAppLaunchCountKey"):
                appData["numOfTimesUsed"] = str( pfileInfo.get("kAppLaunchCountKey") )
            else:
                appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def appleMapApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("SearchString"):
                appData["searchString"] = pfileInfo.get("SearchString")
                self.appleMapReturn["Last Search String"] = pfileInfo.get("SearchString")
                self.recentSearches["Apple Maps"] = [ appData["searchString"] ]

            if pfileInfo.get("LastSearchLatitudeKey"):
                self.appleMapReturn["Last Latitude Search"] = pfileInfo.get("LastSearchLatitudeKey")

            if pfileInfo.get("LastSearchLongitudeKey"):
                self.appleMapReturn["Last Longitude Search"] = pfileInfo.get("LastSearchLongitudeKey")

            appData["installDate"] = "Pre-Installed"
            appData["lastUsed"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + plistName

    def safarApp(self, plistName, folder):
        try:
            appData = dict()
            allSearches = list()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("RecentWebSearches"):
                searches = pfileInfo.get("RecentWebSearches")

                for item in searches:
                    unformatted = item["Date"]
                    formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                    safariItem = formatted + " " + item["SearchString"]
                    allSearches.append( safariItem )
                    self.safariRecentSearches.append( [ formatted, item["SearchString"] ] )

                self.recentSearches["Safari Recent"] = allSearches

                appData["searchesList"] = allSearches

            if pfileInfo.get("SearchEngineStringSetting"):
                appData["SearchEngineSet"] = pfileInfo.get("SearchEngineStringSetting")

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            appData["installDate"] = "Pre-Installed"
            appData["lastUsed"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def openTableApp(self, plistName, folder):
        try:
            appData = dict()
            recentRestaurants = list()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("Number of reservations"):
                appData["Number of Reservations"] = pfileInfo.get("Number of reservations")
                self.openTableReturn["Number of Reservations"] = appData["Number of Reservations"]

            if pfileInfo.get("Number of restaurant viewed"):
                appData["Number of restaurant viewed"] = pfileInfo.get("Number of restaurant viewed")
                self.openTableReturn["Number of Restaurants Viewed"] = appData["Number of restaurant viewed"]

            if pfileInfo.get("OpenUDID"):

                udid = pfileInfo.get("OpenUDID")

                for item in udid:
                    # Get install date
                    if item == "OpenUDID_createdTS":
                        unformatted = udid[item]
                        formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                        appData["installDate"] = formatted

            elif pfileInfo.get("install_date"):
                unformatted = pfileInfo.get("install_date")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["installDate"] = formatted
            else:
                appData["installDate"] = "N/A"


            ''' pfileInfo.get("recentLocation") - dictionary data, look into if someone has it '''
            ''' pfileInfo.get("recentSelectedPOIs") - array data, look into if someone has it '''

            if pfileInfo.get("recentSelectedRestaurants"):
                searches = pfileInfo.get("recentSelectedRestaurants")

                for item in searches:
                    tableItem = "City: " + item["cityName"] + " ID: " + item['id'] + " Name: "+ item['name']
                    self.openTableRecReturn.append( tableItem )
                    recentRestaurants.append( tableItem )

                self.recentSearches["OpenTable"] = recentRestaurants

                appData["recentRestaurants"] = recentRestaurants

            appData["lastUsed"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def bbcApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            # Get last time used
            if pfileInfo.get("kBBCNEWS_TIME_LAST_EXIT"):
                unformatted = pfileInfo.get("kBBCNEWS_TIME_LAST_EXIT")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            # No install date found
            appData["installDate"] = "N/A"

            # Not found
            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + plistName

    def backgammonApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("OpenUDID"):
                udid = pfileInfo.get("OpenUDID")

                for item in udid:
                    # Get install date
                    if item == "OpenUDID_createdTS":
                        unformatted = udid[item]
                        formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                        appData["installDate"] = formatted
            else:
                appData["installDate"] = "N/A"

            if pfileInfo.get("CBSessionCountKey"):
                appData["numOfTimesUsed"] = str( pfileInfo.get("CBSessionCountKey") )
            else:
                appData["numOfTimesUsed"] = "N/A"


            if pfileInfo.get("currency_locale"):
                appData["currency_locale"] = pfileInfo.get("currency_locale")

            if pfileInfo.get("ALLastLanguage"):
                appData["LanguageSet"] = pfileInfo.get("ALLastLanguage")

            # Not found
            appData["lastUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + plistName

    def dictApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("UAApplicationMetricLastOpenDate"):
                unformatted = pfileInfo.get("UAApplicationMetricLastOpenDate")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            if pfileInfo.get("OpenUDID"):
                
                udid = pfileInfo.get("OpenUDID")

                for item in udid:
                    if item == "OpenUDID_createdTS":
                        unformatted = udid[item]
                        formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                        appData["installDate"] = formatted
            else:
                appData["installDate"] = "N/A"

            if pfileInfo.get("appStartCount"):
                appData["numOfTimesUsed"] = str( pfileInfo.get("appStartCount") )
            else:
                appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + plistName

    def yelpApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("YPLastDateSearchedKey"):
                unformatted = pfileInfo.get("YPLastDateSearchedKey")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            if pfileInfo.get("YPAppLaunchCountKey"):
                appData["numOfTimesUsed"] = str( pfileInfo.get("YPAppLaunchCountKey") )
            else:
                appData["numOfTimesUsed"] = "N/A"

            '''
            figure out lat and long
            if pfileInfo.get("YPSearchMapRegionKey"):
                region = pfileInfo.get("YPSearchMapRegionKey")

                for item in region:
                    if item == "center":
                        print type(item)
            '''

            appData["installDate"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + plistName

    def tedApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("TEDLastLaunchedDate"):
                unformatted = pfileInfo.get("TEDLastLaunchedDate")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            # Not found
            appData["installDate"] = "N/A"

            # Not found
            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def followersApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("OpenUDID"):
                udid = pfileInfo.get("OpenUDID")

                for item in udid:
                    if item == "OpenUDID_createdTS":
                        unformatted = udid[item]
                        formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                        appData["installDate"] = formatted
            else:
                appData["installDate"] = "N/A"

            if pfileInfo.get("iRateUseCount"):
                appData["numOfTimesUsed"] = str( pfileInfo.get("iRateUseCount") )
            else:
                appData["numOfTimesUsed"] = "N/A"

            if pfileInfo.get("iNotifyLastChecked"):
                unformatted = pfileInfo.get("iNotifyLastChecked")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def cnnApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("dateOfAppExit"):
                unformatted = pfileInfo.get("dateOfAppExit")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            if pfileInfo.get("timesOpened"):
                appData["numOfTimesUsed"] = str( pfileInfo.get("timesOpened") )
            else:
                appData["numOfTimesUsed"] = "N/A"

            ''' can get carrier info crittercism_536c04d107229a6693000003 '''

            if pfileInfo.get("newsPreference"):
                appData["newsPreference"] = pfileInfo.get("newsPreference")

            # Not found in Plist
            appData["installDate"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def yahooWeatherApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("NumTimesAppRun"):
                appData["numOfTimesUsed"] = str( pfileInfo.get("NumTimesAppRun") )
            else:
                appData["numOfTimesUsed"] = "N/A"

            if pfileInfo.get("YahooSidebar.EYC.lastPartnerAppsCountry"):
                appData["Country"] = pfileInfo.get("YahooSidebar.EYC.lastPartnerAppsCountry")

            if pfileInfo.get("YMConfigTimeOfLastSuccessfulRefresh"):
                unformatted = pfileInfo.get("YMConfigTimeOfLastSuccessfulRefresh")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            # Not found
            appData["installDate"] = "N/A"

            ''' Has carrier info - crittercism_50a6ced14f633a403a000002 '''

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def recSearches(self, plistName):
        try:
            appData = list()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("RecentSearches"):
                searches = pfileInfo.get("RecentSearches")
                for item in searches:
                    self.safariRecentSearches.append( ["N/A", item] )


                self.recentSearches["Safari Searches"] = searches

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def gasBuddyApp(self, plistName, folder):
        try:
            appData = dict()
            searches = list()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("kGBPreviousSearches"):
                prevSearches = pfileInfo.get("kGBPreviousSearches")

                for item in prevSearches:
                    searches.append(item)

                self.recentSearches["Gas Buddy Zipcodes"] = searches
                self.gasBudZips.append(searches)

            if pfileInfo.get("OpenUDID"):

                udid = pfileInfo.get("OpenUDID")

                for item in udid:
                    # Get install date
                    if item == "OpenUDID_createdTS":
                        unformatted = udid[item]
                        formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                        appData["installDate"] = formatted
            else:
                appData["installDate"] = "N/A"

            appData["lastUsed"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def numbersApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("TSALastDidEnterBackgroundTime"):
                unformatted = pfileInfo.get("TSALastDidEnterBackgroundTime")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            appData["installDate"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def undergroundWeatherApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("CSComScore-lastTransmission"):
                appData["lastUsed"] = pfileInfo.get("CSComScore-lastTransmission")
            else:
                appData["lastUsed"] = "N/A"

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def appleStoreApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("lastUserId"):
                appData["username"] = pfileInfo.get("lastUserId")
                self.usernames.append( [ "App Store", appData["username"] ] )

            if pfileInfo.get("lastiOSLanguageKey"):
                appData["language"] = pfileInfo.get("lastiOSLanguageKey")

            appData["installDate"] = "N/A"
            appData["lastUsed"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def uefaApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("com.tealium.lifecyclelog"):
                lifecylelog = pfileInfo.get("com.tealium.lifecyclelog")

        except:
            pass
            # print "Error reading: " + folder

    def myRadarApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("storedLocations"):
                locations = pfileInfo.get("storedLocations")
        except:
            pass
            # print "Error reading: " + folder

    def bloombergApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("app.prefs.com.bloomberg.NavigationLastUseDate"):
                unformatted = pfileInfo.get("app.prefs.com.bloomberg.NavigationLastUseDate")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            if pfileInfo.get("CSComScore-runsCount"):
                appData["numOfTimesUsed"] = pfileInfo.get("CSComScore-runsCount")
            else:
                appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"
            
            appData["installDate"] = "N/A"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def hopperApp(self, plistName, folder):
        try:
            appData = dict()
            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("ATEngagementInstallDateKey"):
                unformatted = pfileInfo.get("ATEngagementInstallDateKey")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["installDate"] = formatted
            else:
                appData["installDate"] = "N/A"

            if pfileInfo.get("ATAppConfigurationLastUpdatePreferenceKey"):
                unformatted = pfileInfo.get("ATAppConfigurationLastUpdatePreferenceKey")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            appData["numOfTimesUsed"] = "N/A"


            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def amazonApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("com.crashlytics.insights.lastmaintenancedate"):
                unformatted = pfileInfo.get("com.crashlytics.insights.lastmaintenancedate")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            if pfileInfo.get("theApplicationStartCount"):
                appData["numOfTimesUsed"] = pfileInfo.get("theApplicationStartCount")
            else:
                appData["numOfTimesUsed"] = "N/A"

            if pfileInfo.get("US/AWUserKeyFullName"):
                appData["username"] = pfileInfo.get("US/AWUserKeyFullName")
                self.usernames.append( ["Amazon Account Name", appData["username"] ] )

            if pfileInfo.get("AmazonMarketplace"):
                appData["Marketplace Location"] = pfileInfo.get("AmazonMarketplace")


            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            
            appData["installDate"] = "N/A"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def mintApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("ABBTLastUpdateDate"):
                unformatted = pfileInfo.get("ABBTLastUpdateDate")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            if pfileInfo.get("install_date"):
                unformatted = pfileInfo.get("ABBTLastUpdateDate")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["installDate"] = formatted
            else:
                appData["installDate"] = "N/A"

            appData["numOfTimesUsed"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def uberApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("last_user_gps_location_longitude"):
                self.uberReturn["Last User Longitude Location"] = pfileInfo.get("last_user_gps_location_longitude")

            if pfileInfo.get("last_user_gps_location_Latitude"):
                self.uberReturn["Last User Latitude Location"] = pfileInfo.get("last_user_gps_location_Latitude")

            if pfileInfo.get("last_user_entered_location_Latitude"):
                self.uberReturn["Last Entered Latitude"] = pfileInfo.get("last_user_entered_location_Latitude")

            if pfileInfo.get("last_user_entered_location_longitude"):
                self.uberReturn["Last Entered Longitude"] = pfileInfo.get("last_user_entered_location_longitude")

            if pfileInfo.get("kGMSMapsUserClientLegalCountry"):
                self.uberReturn["Country"] = pfileInfo.get("kGMSMapsUserClientLegalCountry")

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            appData["installDate"] = "N/A"
            appData["lastUsed"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def dunkinApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("LastDeviceLanguage"):
                self.dunkinReturn["Language"] = pfileInfo.get("LastDeviceLanguage")

            if pfileInfo.get("dateOfBirth"):
                self.dunkinReturn["User's Birthday"] = pfileInfo.get("dateOfBirth")

            if pfileInfo.get("lastMessageRead"):
                appData["lastUsed"] = pfileInfo.get("lastMessageRead")
            else:
                appData["lastUsed"] = "N/A"

            if pfileInfo.get("lastName"):
                self.dunkinReturn["Last Name"] = pfileInfo.get("lastName")

            if pfileInfo.get("firstName"):
                self.dunkinReturn["First Name"] = pfileInfo.get("firstName")

            if pfileInfo.get("userName"):
                appData["username"] = pfileInfo.get("userName")
                self.usernames.append( ["Dunkin Donuts", appData["username"] ] )

            if pfileInfo.get("zip"):
                self.dunkinReturn["User Zipcode"] = pfileInfo.get("zip")

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            appData["installDate"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def groupMeApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("user"):
                user = pfileInfo.get("user")
                for item in user:
                    if item == "phone_number":
                        self.groupmeReturn["Phone Number"] = user[item]

                    if item == "created_at":
                        self.groupmeReturn["User Created"] = user[item]

                    if item == "email":
                        appData["Email"] = user[item]
                        self.usernames.append( ["Group Me", appData["Email"] ] )

                    if item == "name":
                        appData["username"] = user[item]
                        self.usernames.append( ["Group Me Username", appData["username"] ] )


            if pfileInfo.get("com.crashlytics.insights.lastmaintenancedate"):
                unformatted = pfileInfo.get("com.crashlytics.insights.lastmaintenancedate")
                formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                appData["lastUsed"] = formatted
            else:
                appData["lastUsed"] = "N/A"

            if pfileInfo.get("GMInstallation"):
                installdata = pfileInfo.get("GMInstallation")
                for item in installdata:
                    if item == "locale":
                        self.groupmeReturn["Locale"] = installdata[item]

                    if item == "country":
                        self.groupmeReturn["Country"] = installdata[item]

                    if item == "language":
                        self.groupmeReturn["Language"] = installdata[item]

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            appData["installDate"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def hangApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("RootAssociatedStoreKey"):
                stored = pfileInfo.get("RootAssociatedStoreKey")
                for item in stored:
                    if item == "selectedUserEmailAddress":
                        self.usernames.append( ["Google Hangouts", stored[item] ] )

            (appName, pre) = self.get_folder_name(folder)

            if not pre:
                pre = "Currently Installed"

            appData["installDate"] = "N/A"
            appData["numOfTimesUsed"] = "N/A"
            appData["lastUsed"] = "N/A"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

            return appData

        except:
            pass
            # print "Error reading: " + folder

    def jetblueApp(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("RequisitesLastRequest"):
                appData["lastUsed"] = pfileInfo.get("RequisitesLastRequest")
            else:
                appData["lastUsed"] = "N/A"

            if pfileInfo.get("bt-firstLaunch"):
                appData["installDate"] = pfileInfo.get("bt-firstLaunch")
            else:
                appData["installDate"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)

            if not pre:
                pre = "Currently Installed"

            appData["numOfTimesUsed"] = "N/A"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

        except:
            pass
            # print "Error reading: " + folder

    def getArbInstalled(self, plistName, folder):
        try:
            appData = dict()

            pfileInfo = self.openPlists(plistName)

            if pfileInfo.get("OpenUDID"):

                udid = pfileInfo.get("OpenUDID")

                for item in udid:
                    # Get install date
                    if item == "OpenUDID_createdTS":
                        unformatted = udid[item]
                        formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
                        appData["installDate"] = formatted
            else:
                appData["installDate"] = "N/A"

            (appName, pre) = self.get_folder_name(folder)
            if not pre:
                pre = "Currently Installed"

            appData["numOfTimesUsed"] = "N/A"
            appData["lastUsed"] = "N/A"

            self.allAppBasicData[folder] = [appName, folder, pre, appData["installDate"], appData["lastUsed"], appData["numOfTimesUsed"]]

        except:
            pass
            # print "Error reading: " + folder

    def info_plist_parser(self):
        if os.path.exists(self.backupDir):
        
            dirList = os.listdir(self.backupDir)

            if "Info.plist" in dirList:
                allApps = self.getInfoPlist()
            

            allBackupFiles = self.retrieveBackupFiles()
            
            for plistName in allBackupFiles:
                # Rename file in backup if it has not been
                if (plistName[-6:] != ".plist"):
                    if allApps.has_key(plistName):
                        self.renameFile(plistName)

                ''' JetBlue '''
                if plistName == "d462605b8bb39612ef623a453bb458e298c4fce0.plist":
                    jetblueFolder = allApps["d462605b8bb39612ef623a453bb458e298c4fce0"]
                    jetblueData = self.jetblueApp(plistName, jetblueFolder)

                    ''' Google Hangouts '''
                elif plistName == "bc6dade4672d6c30dc9024e961e12a66cf4fce84.plist":
                    hangFolder = allApps["bc6dade4672d6c30dc9024e961e12a66cf4fce84"]
                    hangData = self.hangApp(plistName, hangFolder)

                    ''' GroupMe '''
                elif plistName == "f268932641731af422eccc54d763797ffeb0f13b.plist":
                    groupMeFolder = allApps["f268932641731af422eccc54d763797ffeb0f13b"]
                    groupMeData = self.groupMeApp(plistName, groupMeFolder)

                    ''' Dunkin Donuts '''
                elif plistName == "1fac19b26991a0ba323e7c523d19d8937eef80f1.plist":
                    dunkinFolder = allApps["1fac19b26991a0ba323e7c523d19d8937eef80f1"]
                    dunkinData = self.dunkinApp(plistName, dunkinFolder)

                    ''' Uber '''
                elif plistName == "a51922a403decf42807904ee0f540ad53ae80880.plist":
                    uberFolder = allApps["a51922a403decf42807904ee0f540ad53ae80880"]
                    uberData = self.uberApp(plistName, uberFolder)

                    ''' Mint '''
                elif plistName == "ae56c7fed40fe52afdd0d4b771599bcfc94cc52f.plist":
                    mintFolder = allApps["ae56c7fed40fe52afdd0d4b771599bcfc94cc52f"]
                    mintData = self.mintApp(plistName, mintFolder)

                    ''' Amazon '''
                elif plistName == "e24a7e08d772c8692c9006e68a3e7cfe22c2bd6b.plist":
                    amazonFolder = allApps["e24a7e08d772c8692c9006e68a3e7cfe22c2bd6b"]
                    amazonData = self.amazonApp(plistName, amazonFolder)

                    ''' Hopper '''
                elif plistName == "87f37f7542dd6710bd585e91c992bfe1ad48b16e.plist":
                    hoppFolder = allApps["87f37f7542dd6710bd585e91c992bfe1ad48b16e"]
                    hoppData = self.hopperApp(plistName, hoppFolder)
                
                    ''' Bloomberg '''
                elif plistName == "40edcd53fce3d7f4d8fa96103dfd8ad2caf3e52e.plist":
                    bloombergFolder = allApps["40edcd53fce3d7f4d8fa96103dfd8ad2caf3e52e"]
                    bloomData = self.bloombergApp(plistName, bloombergFolder)

                    ''' My Radar '''
                elif plistName == "605ec2208a37dad9347fa11bc63cdea2000630b8.plist":
                    myRadarFolder = allApps["605ec2208a37dad9347fa11bc63cdea2000630b8"]
                    myRadarData = self.myRadarApp(plistName, myRadarFolder)

                    ''' UEFA '''
                elif plistName == "5dbbcb700ae5603c54b401af71c4ba2a5531ec91.plist":
                    uefaFolder = allApps["5dbbcb700ae5603c54b401af71c4ba2a5531ec91"]
                    uefaData = self.uefaApp(plistName, uefaFolder)

                    ''' Numbers '''
                elif plistName == "18a2fb355f1f9ab64dadef70ada9041c7618a689.plist":
                    numbersFolder = allApps["18a2fb355f1f9ab64dadef70ada9041c7618a689"]
                    numbersData = self.numbersApp(plistName, numbersFolder)

                    ''' Weather Underground '''
                elif plistName == "3766a71f0ede3ea7eda5275bbea3e02b9b8d6ec9.plist":
                    undergroundWFolder = allApps["3766a71f0ede3ea7eda5275bbea3e02b9b8d6ec9"]
                    underWeathData = self.undergroundWeatherApp(plistName, undergroundWFolder)

                    ''' Apple Store '''
                elif plistName == "39e60280362db73ec41850e5028e17475120a1c2.plist":
                    appleStoreFolder = allApps["39e60280362db73ec41850e5028e17475120a1c2"]
                    appleStoreData = self.appleStoreApp(plistName, appleStoreFolder)

                    ''' Gas Buddy '''
                elif plistName == "089fc765e3e01b1ccee2b2943a8645148c383e4a.plist":
                    gasBuddyFolder = allApps["089fc765e3e01b1ccee2b2943a8645148c383e4a"]
                    gasBuddyData = self.gasBuddyApp(plistName, gasBuddyFolder)

                    '''  BBC News Application '''
                elif plistName == "16779eede28c39b27eac09a502432a4e2d85069a.plist":
                    bbcFolder = allApps["16779eede28c39b27eac09a502432a4e2d85069a"]
                    bbcAppData = self.bbcApp(plistName, bbcFolder)

                    '''  Backgammon Application'''
                elif plistName == "2045a5674c57039ed9fabbda24944091939d8029.plist":
                    backgammonFolder = allApps["2045a5674c57039ed9fabbda24944091939d8029"]
                    backgammonAppData = self.backgammonApp(plistName, backgammonFolder)

                    ''' CNN Application '''
                elif plistName == "fa6663f6f81ef07579e45aaf599b72afb4fa1793.plist":
                    cnnFolder = allApps["fa6663f6f81ef07579e45aaf599b72afb4fa1793"]
                    cnnAppData = self.cnnApp(plistName, cnnFolder)

                    ''' Dictionary.com Application, nothing interesting - can get install date '''
                elif plistName == "a9aa0e872d39ea0960425356e656277593bee3a0.plist":
                    dictFolder = allApps["a9aa0e872d39ea0960425356e656277593bee3a0"]
                    dictAppData = self.dictApp(plistName, dictFolder)

                    ''' TED '''
                elif plistName == "f2bd4c26a8af993d6e78f14cf94389d470ebd2cd.plist":
                    tedFolder = allApps["f2bd4c26a8af993d6e78f14cf94389d470ebd2cd"]
                    tedAppData = self.tedApp(plistName, tedFolder)

                    ''' Yelp Application '''
                elif plistName == "c897722299882c4ddc7c5fa99a4b6b7f87ce6738.plist":
                    yelpFolder = allApps["c897722299882c4ddc7c5fa99a4b6b7f87ce6738"]
                    yelpAppData = self.yelpApp(plistName, yelpFolder)

                    ''' Followers '''
                elif plistName == "f8b156595b6aa89fd72e7b00c80dbb521da7c3d0.plist":
                    followersFolder = allApps["f8b156595b6aa89fd72e7b00c80dbb521da7c3d0"]
                    followersAppData = self.followersApp(plistName, followersFolder)

                    ''' Yahoo Weather '''
                elif plistName == "fb2ead1b56e4b636a747a2e7c9c68580541658fb.plist":
                    yahooWeatherFolder = allApps["fb2ead1b56e4b636a747a2e7c9c68580541658fb"]
                    yahooWeatherData = self.yahooWeatherApp(plistName, yahooWeatherFolder)

                    ''' Mobile Me 2 '''
                elif plistName == "5a47b5c58a4f7a18b3a0dd7c1562446c717d80b0.plist":
                    mobileme2folder = allApps["5a47b5c58a4f7a18b3a0dd7c1562446c717d80b0"]
                    mobileme2data = self.mobilemeApp2(plistName, mobileme2folder)

                    ''' Mobile Me Application'''
                elif plistName == "035e1532578217a6ff904e58a81889d6d5e64ccd.plist":
                    mobileMeFolder = allApps["035e1532578217a6ff904e58a81889d6d5e64ccd"]
                    mobileMeAppData = self.mobileMeApp(plistName, mobileMeFolder)

                    '''  iStudiez Application'''
                elif plistName == "09623102abe9e3e5c26afe6703e7a9854eb91bf5.plist":
                    istudiezFolder = allApps["09623102abe9e3e5c26afe6703e7a9854eb91bf5"]
                    iStudiezAppData = self.iStudiezApp(plistName, istudiezFolder)

                    ''' Facebook Messenger Application '''
                elif plistName == "0ba8559bd5e366782b1e5d846c3bb94a71f435d8.plist":
                    fbMessFolder = allApps["0ba8559bd5e366782b1e5d846c3bb94a71f435d8"]
                    fbMessAppData = self.fbMessengerApp(plistName, fbMessFolder)

                    ''' Sunrise Calendar Application '''
                elif plistName == "0c04e65763d541e4acf8a4fce426bc052e13e04d.plist":
                    sunriseFolder = allApps["0c04e65763d541e4acf8a4fce426bc052e13e04d"]
                    sunRiseAppData = self.sunRiseApp(plistName, sunriseFolder)
                
                    ''' Google Maps Application '''
                elif plistName == "2317bc192586a12099f1dc3c6703d003cc111df0.plist":
                    googleMapsFolder = allApps["2317bc192586a12099f1dc3c6703d003cc111df0"]
                    googleMapsAppData = self.googleMapApp(plistName, googleMapsFolder)

                    ''' Mixologist '''
                elif plistName == "2940131e091b91b182ab3341579769ddcb1f62a3.plist":
                    mixoloFolder = allApps["2940131e091b91b182ab3341579769ddcb1f62a3"]
                    mixoloAppData = self.mixologistApp(plistName, mixoloFolder)

                    ''' AP News Application '''
                elif plistName == "31860c71268db85481a32bdf0aedf3cf3a86d0c5.plist":
                    apFolder = allApps["31860c71268db85481a32bdf0aedf3cf3a86d0c5"]
                    APnewsAppData = self.APnewsApp(plistName, apFolder)

                    ''' Fitness Pal Application '''
                elif plistName == "32048dc3eb883e2bc06c8264a197c6551202b278.plist":
                    fitnessPalFolder = allApps["32048dc3eb883e2bc06c8264a197c6551202b278"]
                    fitnessPalAppData = self.fitnessPalApp(plistName, fitnessPalFolder)

                    ''' Facebook Application '''
                elif plistName == "384eb9e62ba50d7f3a21d9224123db62879ef423.plist":
                    fbFolder = allApps["384eb9e62ba50d7f3a21d9224123db62879ef423"]
                    FacebookAppData = self.FBapp(plistName, fbFolder)
                
                    '''  Sudoku App '''
                elif plistName == "38e815c7e3d23fb430bf764ee46cf59d07d0bbcd.plist":
                    sudokuFolder = allApps["38e815c7e3d23fb430bf764ee46cf59d07d0bbcd"]
                    sudokuAppData = self.sudokuApp(plistName, sudokuFolder)

                    ''' Mobile Mail Application '''
                elif plistName == "4800b8726fbd1a324c181bd735d6457f3eced7cc.plist":
                    mailFolder = allApps["4800b8726fbd1a324c181bd735d6457f3eced7cc"]
                    MailAppData = self.MailApp(plistName, mailFolder)

                    ''' HopStop Application '''
                elif plistName == "5e5a019bab4a0bb548b0251ae9b0f9bade4d11ef.plist":
                    hopstopFolder = allApps["5e5a019bab4a0bb548b0251ae9b0f9bade4d11ef"]
                    HopStopAppData = self.HopStopApp(plistName, hopstopFolder)
                
                    ''' Grub Hub Application '''
                elif plistName == "6d4a786f3c5dcd1a545dc37aadaff7336d63eb81.plist":
                    grubhubFolder = allApps["6d4a786f3c5dcd1a545dc37aadaff7336d63eb81"]
                    grubHubAppData = self.grubHubApp(plistName, grubhubFolder)

                    ''' Iris Application '''
                elif plistName == "70b025173a26f150dac67be74c9bb7f24d8917d5.plist":
                    irisFolder = allApps["70b025173a26f150dac67be74c9bb7f24d8917d5"]
                    irisAppData = self.irisApp(plistName, irisFolder)

                    ''' Instagram Application '''
                elif plistName == "72b88e49ac4f48605284907191d53d474397100f.plist":
                    instaFolder = allApps["72b88e49ac4f48605284907191d53d474397100f"]
                    instaAppData = self.instaApp(plistName, instaFolder)

                    ''' Snapchat Application '''
                elif plistName == "736eed74563910488dadd3bc26151245d4709336.plist":
                    snapchatFolder = allApps["736eed74563910488dadd3bc26151245d4709336"]
                    snapChatAppData = self.snapChatApp(plistName, snapchatFolder)

                    ''' LinkedIn Application '''
                elif plistName == "9c404eb0aa691005cdbd1e97ca74685c334f3635.plist":
                    linkedInFolder = allApps["9c404eb0aa691005cdbd1e97ca74685c334f3635"]
                    linkedInAppData = self.linkedInApp(plistName, linkedInFolder)

                    ''' WhatsApp Application '''
                elif plistName == "b3f5945694120cbb23254422a4dca514f32917bc.plist":
                    whatsappFolder = allApps["b3f5945694120cbb23254422a4dca514f32917bc"]
                    whatsAppData = self.whatsApp(plistName, whatsappFolder)

                    ''' Seamless Application '''
                elif plistName == "e360b1303fbe68ace4c6454be3400a29c2882d0f.plist":
                    seamlessFolder = allApps["e360b1303fbe68ace4c6454be3400a29c2882d0f"]
                    seamlessAppData = self.seamlessApp(plistName, seamlessFolder)

                    ''' Apple Maps - Last search (long&lat) '''
                elif plistName == "e3722676133184621303a00be5f4ce1714c57695.plist":
                    appMapFolder = allApps["e3722676133184621303a00be5f4ce1714c57695"]
                    appleMapData = self.appleMapApp(plistName, appMapFolder)

                    ''' Safari History Plist /Library/Safari/History.plist '''
                elif plistName == "ed50eadf14505ef0b433e0c4a380526ad6656d3a":
                    self.renameFile(plistName)
                elif plistName == "ed50eadf14505ef0b433e0c4a380526ad6656d3a.plist":

                    ''' Recent Searches '''
                elif plistName == "37d957bda6d8be85555e7c0a7d30c5a8bc1b5cce":
                    if (plistName[-6:] != ".plist"):
                        plistName = self.renameFile(plistName)
                    self.recSearches(plistName)

                elif plistName == "37d957bda6d8be85555e7c0a7d30c5a8bc1b5cce.plist":
                    self.recSearches(plistName)

                    ''' Safari Application (Play with Bookmark Panel - saved Reading List, Bookmarks)'''
                elif plistName == "ee77759a5f936cb2e4b030694ee739f111552b46.plist":
                    safariFolder = allApps["ee77759a5f936cb2e4b030694ee739f111552b46"]
                    safariData = self.safarApp(plistName, safariFolder)
                        
                    ''' OpenTable Application (Play with recent selected POIs & recentLocation)'''
                elif plistName == "f33ed7caf1a3c9635fe5a33189e5168611bb47c5.plist":
                    openTableFolder = allApps["f33ed7caf1a3c9635fe5a33189e5168611bb47c5"]
                    openTableData = self.openTableApp(plistName, openTableFolder)

                elif plistName[-6:] == ".plist":
                    if plistName[:-6] in allApps:
                        ranFolder = allApps[ plistName[:-6] ]
                        ranData = self.getArbInstalled(plistName, ranFolder)

                for item in self.deletedAppList:
                    (appName, pre) = self.get_folder_name(item)
                    self.allAppBasicData[item] = [appName, item, "Deleted", "N/A", "N/A", "N/A"]

                for key, val in allApps.iteritems():
                    if not self.allAppBasicData.has_key( val ):
                        (appName, pre) = self.get_folder_name(val)
                        if not pre:
                            pre = "Currently Installed"

                        self.allAppBasicData[val] = [appName, val, pre, "N/A", "N/A", "N/A"]

    def sortInstall(self):

        top10 = list()
        tempDict = dict() # will have datetime values
        for key, val in self.allAppBasicData.iteritems():
            vals = self.allAppBasicData[key]
            datetimeString = vals[3]
            if datetimeString != "N/A":
                if datetimeString != "Pre-Installed":
                    newObj = datetime.strptime(datetimeString, "%b %d, %Y %H:%M:%S")
                    tempDict[key] = [vals[0], vals[1], vals[2], newObj, vals[4], vals[5]]

        for key, value in sorted(tempDict.items(), key=lambda e: e[1][3])[:10]:
            appName = value[0]
            appFolder = value[1]
            unformatted = value[3]
            formatted = unformatted.strftime("%b %d, %Y %H:%M:%S")
            appDate = formatted
            top10.append( [appName, appFolder, appDate] )

        return top10

    def allAppTable(self):
        temp = list()

        for key,val in self.allAppBasicData.iteritems():
            temp.append(val)

        return temp

    def gasBudData(self):
        return self.gasBudZips

    def groupmeData(self):
        return self.groupmeReturn

    def dunkinData(self):
        return self.dunkinReturn

    def uberData(self):
        return self.uberReturn

    def openTableRecent(self):
        return self.openTableRecReturn

    def openTableData(self):
        return self.openTableReturn

    def appleMapData(self):
        return self.appleMapReturn

    def whatsappData(self):
        return self.whatsappReturn

    def linkedInData(self):
        return self.linkedInReturn

    def snapRecent(self):
        return self.snapChatRecent

    def returnSnapData(self):
        return self.snapchatReturn

    def returnSnapFriends(self):
        return self.snapchatFriends

    def returnInsta(self):
        return self.instaReturnDict

    def returnHopStopRec(self):
        return self.hopStopRec

    def returnHopStop(self):
        return self.hopStopReturn

    def returnAppleMail(self):
        return self.appleMailReturn

    def returngMapData(self):
        return self.gMapDict

    def returnsunriseData(self):
        return self.sunriseData

    def returnFBdata(self):
        return self.facebookItems

    def returnSafariData(self):
        return self.safariRecentSearches

    def accountTable(self):
        return self.usernames

    def recSearchTable(self):
        return self.recentSearches
