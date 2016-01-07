from django.shortcuts import render_to_response
from django.template import RequestContext
import extraction
import json
import os
import AppParser
import PlistParser
import iosRecovery
import shutil
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import time
import datetime
from django.shortcuts import redirect
from django.core.urlresolvers import reverse 

'''
	Ex 3: Keychain sqlite database file is 51a4616e576dd33cd2ababadfea874eb8ff246bf0e and this value is 
	computer from SHA-1(KeychainDomain-keychain-backup.plist)
		Address books and favorite contacts
		App Store data
		Application parameters, preferences and data
		Form fill data for Web pages
		CalDAV and signed calendar accounts
		Calendar accounts
		Calendar events
		Call history
		Pictures
		The list of purchased applications
		Keychain
		External sync sources (Mobile Me, Exchange ActiveSync)
		Microsoft Exchange account settings
		Mail accounts
		Network accounts and settings (Wi-Fi, VPN settings)
'''

class ViewsHandler():

	def __init__(self):
		self.extractedBackups()
		
		extracted = self.all_backups

		if len(extracted) != 0:
			self.currentBackup = extracted[0][1]

			self.extractor = extraction.Data_Extraction(self.currentBackup)
			self.SMSdata = self.extractor.extract_SMSInfo()
			self.CallsData = self.extractor.extract_CallInfo()
			self.imageParse = self.extractor.extract_ImageData()

			appDataPath = os.path.join(self.currentBackup, "AppData")
			self.parser = AppParser.BackupParser( appDataPath )

			''' Biggest Apps 
				- Safari 
				- Snapchat
				- HopStop
			'''
			self.safariData = self.parser.returnSafariData()
			self.snap_data = self.parser.returnSnapData()
			self.snap_friends = self.parser.returnSnapFriends()
			self.snap_rec = self.parser.snapRecent()

			self.hopstop_data = self.parser.returnHopStop()
			self.hostop_rec = self.parser.returnHopStopRec()

			# All Plist Data
			self.plistParser = PlistParser.PlistParser(appDataPath)

			# WiFi Data
			self.wifiData = self.plistParser.wifiPlists()
			
			# Keychain Data
			self.keychainData = self.plistParser.KeyChainPlist()

			self.wirelessSSID = self.plistParser.wireless_SSID()
		else:
			self.currentBackup = None
			self.extractor = None
			self.SMSdata = None
			self.CallsData = None
			self.imageParse = None
			self.parser = None
			self.safariData = None
			self.snap_data = None
			self.snap_friends = None
			self.snap_rec = None
			self.hostop_rec = None
			self.hopstop_data = None
			self.keychainData = None
			self.wirelessSSID = None
			self.wifiData = None

	@csrf_exempt
	def update(self, currBackup):
		self.currentBackup = currBackup

		self.extractor = extraction.Data_Extraction(self.currentBackup)
		self.SMSdata = self.extractor.extract_SMSInfo()
		self.CallsData = self.extractor.extract_CallInfo()
		self.imageParse = self.extractor.extract_ImageData()

		self.parser = AppParser.BackupParser( os.path.join(self.currentBackup, "AppData") )

		''' Biggest Apps 
			- Safari 
			- Snapchat
			- HopStop
		'''
		self.safariData = self.parser.returnSafariData()
		self.snap_data = self.parser.returnSnapData()
		self.snap_friends = self.parser.returnSnapFriends()
		self.snap_rec = self.parser.snapRecent()

		self.hopstop_data = self.parser.returnHopStop()
		self.hostop_rec = self.parser.returnHopStopRec()

		# All Plist Data
		self.plistParser = PlistParser.PlistParser(appDataPath)

		# WiFi Data
		self.wifiData = self.plistParser.wifiPlists()

		# Keychain Data
		self.keychainData = self.plistParser.KeyChainPlist()

		# WiFi Specific Data
		self.wirelessSSID = self.plistParser.wireless_SSID()

		''' Return user to overview page with all data updated to point to selected/just created backup '''

		# return HttpResponse( json.dumps( {"keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "guid":guid, "device_name": devicename, "backup_date": backupdate, "phone_number": phoneNum, "producttype": producttype, "prod_version": iosV, "serial_num": serial, "uid": uid, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec} ), content_type='application/json' )
		# return HttpResponse( json.dumps( {"success": "success"} ), content_type='application/json' )
		# return render_to_response("overview.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "guid":guid, "device_name": devicename, "backup_date": backupdate, "phone_number": phoneNum, "producttype": producttype, "prod_version": iosV, "serial_num": serial, "uid": uid, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec})
		return HttpResponse( {"success":"success"})
		# return render_to_response("overview.html", {"success":"success"})

	def extractedBackups(self):
		extractedBackups = "static/backups/"
		backupList = list()

		for root, dirs, files in os.walk(extractedBackups):
			for d in dirs:
				base = d
				fullpath = extractedBackups + d
				backupList.append([base, fullpath])
			break

		self.all_backups = backupList

	@csrf_exempt
	def homepage(self, request):
		compUser = os.path.expanduser("~/") 
		
		# Location for Mac
		backupLocation = os.path.join(compUser, "Library/Application Support/MobileSync/Backup")

		# Location for Windows XP
		if not backupLocation:
			backupLocation = os.path.join(compUser, "Application Data\\Apple Computer\\MobileSync\\Backup")

		# Location for Windows 7
		if not backupLocation:
			backupLocation = os.path.join(compUser, "AppData\\Roaming\\Apple Computer\\MobileSync\\Backup")

		backup_creation = list()

		# Get all backups
		for root, dirs, files in os.walk(backupLocation):
			for d in dirs:
				backup = os.path.join(backupLocation, d)
				basename = os.path.basename(backup)
				backup_creation.append( [ backup, basename, datetime.date.fromtimestamp( os.stat(backup).st_ctime ), datetime.date.fromtimestamp( os.stat(backup).st_mtime ) ] )
			break
			
		return render_to_response("index.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "current_Backup":self.currentBackup, "backup_creation":backup_creation, "all_backups":self.all_backups, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec } )

	@csrf_exempt
	def createBackup(self, request):
		if request.method == "POST":
			if request.POST['createBackup']:
				backup_location = iosRecovery.main( request.POST['createBackup'] )

				# Return already exists message to user/web app for user to know
				if backup_location == "Already Exists":
					print backup_location
				else:
					self.update( backup_location )

	@csrf_exempt
	def overviewPage(self, request):

		# if request.method == "POST":
		# 	self.update( request.POST['backupSelected'] )

		info = self.parser.deviceInfo()
		devicename = info[0]
		backupdate = info[1]
		phoneNum = info[2]
		producttype = info[3]
		iosV = info[4]
		serial = info[5]
		uid = info[6]
		guid = info[7]

		return render_to_response("overview.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "guid":guid, "device_name": devicename, "backup_date": backupdate, "phone_number": phoneNum, "producttype": producttype, "prod_version": iosV, "serial_num": serial, "uid": uid, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec}, context_instance=RequestContext(request))

	def allSMSpage(self, request):

		tabledata = self.extractor.returnSMSTable()
		jsonTableData = json.dumps(tabledata)
		jsonSMSData = json.dumps(self.SMSdata)

		return render_to_response("SMStemplate.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "json_SMS_Table_Data":jsonTableData, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec})

	def top10Data(self, request):

		jsonCallData = json.dumps(self.CallsData)
		jsonSMSData = json.dumps(self.SMSdata)
		peopleSMS = self.extractor.returnPeopleSMS()
		peopleCall = self.extractor.returnPeopleCalled()

		return render_to_response("top10.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "Calltotal":peopleCall, "SMStotal":peopleSMS, "json_SMS_data":jsonSMSData, "json_Call_data":jsonCallData, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec})

	def allCallspage(self, request):

		tabledata = self.extractor.returnCallsTable()
		jsonCallsTableData = json.dumps(tabledata)
		jsonSMSData = json.dumps(self.SMSdata)

		return render_to_response("Callstemplate.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "json_Calls_Table_Data":jsonCallsTableData, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec})


	def allCalendarpage(self, request):

		[calendarList, calendarJSON] = self.extractor.extract_CalendarInfo()
		jsonCalendarTableData = json.dumps(calendarList)
		jsonCalendarJSON = json.dumps(calendarJSON)

		return render_to_response("Calendartemplate.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "jsonCalendarJSON":jsonCalendarJSON, "json_Calendar_Table_Data":jsonCalendarTableData, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec})

	def allAppPage(self, request):

		allAppData = self.parser.allAppTable()
		jsonAppTableData = json.dumps(allAppData)

		return render_to_response("Apptemplate.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "json_App_Table_Data":jsonAppTableData, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec})

	def appSpecificsPage(self, request):

		fb_data = self.parser.returnFBdata()
		sunrise_data = self.parser.returnsunriseData()
		gmap_data = self.parser.returngMapData()
		appleMail_data = self.parser.returnAppleMail()
		insta_data = self.parser.returnInsta()
		linkedin_data = self.parser.linkedInData()
		whatsapp_data = self.parser.whatsappData()
		applemap_data = self.parser.appleMapData()
		uber_data = self.parser.uberData()
		dunkin_data = self.parser.dunkinData()
		groupMe_data = self.parser.groupmeData()
		gasBud_data = self.parser.gasBudData()
		opentable_rec = self.parser.openTableRecent()
		opentable_data = self.parser.openTableData()

		return render_to_response("AppSpecifictemplate.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "safari_data":self.safariData, "fb_data":fb_data, "sunrise_data":sunrise_data, "googleMap_data":gmap_data, "appleMail_data":appleMail_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec, "insta_data":insta_data, "snap_data":self.snap_data, "snap_friends":self.snap_friends, "linkedin_data":linkedin_data, "whatsapp_data":whatsapp_data, "applemap_data":applemap_data, "opentable_rec":opentable_rec, "opentable_data":opentable_data, "uber_data":uber_data, "dunkin_data":dunkin_data, "groupMe_data":groupMe_data, "gasBud_data":gasBud_data})
	
	def appPlistsPage(self, request):
		plistData = self.plistParser.returnAppPlistData()

		return render_to_response("AppPlistTemplate.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "plistData":plistData, "all_backups":self.all_backups, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec, "snap_rec":self.snap_rec})
	
	def accountsPage(self, request):

		accounts = self.parser.accountTable()
		jsonAccountsTable = json.dumps(accounts)

		return render_to_response("Accountstemplate.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "json_Accounts_Table_Data":jsonAccountsTable, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec})

	def safariPage(self, request):

		return render_to_response("safariSearchestemplate.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "safari_data":self.safariData, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec})

	def snapchatPage(self, request):

		return render_to_response("snapchattemplate.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec, "snap_rec":self.snap_rec})

	def hopstopPage(self, request):

		return render_to_response("hopstoptemplate.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec})

	def wifiPage(self, request):
		
		return render_to_response("WifiTemplate.html", {"wirelessSSID":self.wirelessSSID, "keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec, "snap_rec":self.snap_rec})

	def keychainPage(self, request):

		return render_to_response("KeychainTemplate.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec, "snap_rec":self.snap_rec})

	def imagesPage(self, request):

		map_table = self.extractor.returnImageTable()
		map_Data = self.extractor.returnMapData()
		image_paths = self.extractor.returnImagePaths()

		return render_to_response("imagesTemplate.html", {"keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "image_paths":image_paths, "map_Data":map_Data, "map_table":map_table, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec})

	def notesPage(self, request):

		notesTitles = self.extractor.returnNotesTitles()

		return render_to_response("NotesTemplate.html", {"notestitles": notesTitles, "keychainData":self.keychainData, "wifiData":self.wifiData, "all_backups":self.all_backups, "safari_data":self.safariData, "snap_friends":self.snap_friends, "snap_data":self.snap_data, "hopstop_data":self.hopstop_data, "hostop_rec":self.hostop_rec } )



