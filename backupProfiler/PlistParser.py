import plistlib
import biplist
import datetime
import json
import time
import os
import csv
import hashlib
import strftime_1900

''' Data Types:
		str
		int
		float
		bool
		dict
		biplist.Data
		datetime.datetime
'''

class PlistParser():
	def __init__(self, backup):
		print "Running PlistParser.py"

		self.all_plist_data = list()
		self.encryptedDict = dict()

		self.appDir = backup

		self.getInfoPlist()

		for root, dirs, files in os.walk(self.appDir):

			for filename in files:

				self.plist_list = list() # restart for each Plist
				
				plistPath = os.path.join(self.appDir, filename)
				plistFile = ""

				try:
					plistFile = biplist.readPlist(plistPath)
					self.retrieveData("", plistFile) # [ [key, value], [key, value] ]
					
					hashed = filename[:-6]

					if ( self.encryptedDict.has_key(hashed) ) :
						appFolder= self.encryptedDict[hashed]

						self.all_plist_data.append( [appFolder, self.plist_list] )	# [ Plist Filename, [list of all data] ]
					else:
						self.all_plist_data.append( [filename, self.plist_list] )	# [ Plist Filename, [list of all data] ]

				except:
					try:
						plistFile = plistlib.readPlist(plistPath)
						self.retrieveData("", plistFile) # [ [key, value], [key, value] ]

						hashed = filename[:-6]

						if ( self.encryptedDict.has_key(hashed) ) :
							appFolder= self.encryptedDict[hashed]

							self.all_plist_data.append( [appFolder, self.plist_list] )	# [ Plist Filename, [list of all data] ]
						else:
							self.all_plist_data.append( [filename, self.plist_list] )	# [ Plist Filename, [list of all data] ]
							
					except:
						pass
						# print "Error reading: " + plistPath




	def KeyChainPlist(self):

		# 51a4616e576dd33cd2abadfea874eb8ff246bf0e - Keychain Data

		self.keychain_dict = dict()

		keychain_path = os.path.join(self.appDir, "51a4616e576dd33cd2abadfea874eb8ff246bf0e.plist")

		if os.path.exists(keychain_path):
			try:
				data = biplist.readPlist(keychain_path)

				for key, val in data.iteritems():
					count = 0
					self.keychain_dict[key] = list()
					for item in val:
						for k, v in item.iteritems():
							newstr = " ".join("{:02x}".format(ord(c)) for c in v)
							self.keychain_dict[key].append( [k, newstr] )

						count += 1
			except:
				try:
					data = plistlib.readPlist(keychain_path)

					for key, val in data.iteritems():
						count = 0
						self.keychain_dict[key] = list()
						for item in val:
							for k, v in item.iteritems():
								newstr = " ".join("{:02x}".format(ord(c)) for c in v)
								self.keychain_dict[key].append( [k, newstr] )

							count += 1

				except:
					pass
					# print "Keychain File Error"


		return self.keychain_dict


	def returnWifiPlistData(self, data, wifi_data_list):
		for wifi in data["List of known networks"]:
			temp_list = list()

			if "WiFiNetworkRequiresPassword" in wifi:
				WiFiNetworkRequiresPassword = [ "Requires Password", str(wifi["WiFiNetworkRequiresPassword"]) ]
				temp_list.append( WiFiNetworkRequiresPassword )

			if "lastAutoJoined" in wifi:
				unformatted = wifi["lastAutoJoined"]
				lastAutoJoined = [ "Last Auto Joined", unformatted.strftime("%b %d, %Y %H:%M:%S") ]
				temp_list.append( lastAutoJoined )

			if "SecurityMode" in wifi:
				securityMode = [ "Security Mode", wifi["SecurityMode"] ]
				temp_list.append( securityMode )

			if "SSID_STR" in wifi:
				name = wifi["SSID_STR"]
			else:
				name = "N/A"

			if "Strength" in wifi:
				strength = ["WiFi Strength", str(wifi["Strength"]) ]
				temp_list.append( strength )
			
			if "WEPKeyLen" in wifi:
				WEPKeyLen = ["WEP Key Length", str(wifi["WEPKeyLen"]) ]
				temp_list.append( WEPKeyLen )

			if "lastJoined" in wifi:
				 unformatted= wifi ["lastJoined"]
				 lastJoined = [ "Last Joined", unformatted.strftime("%b %d, %Y %H:%M:%S") ]
				 temp_list.append( lastJoined )
			
			if "WiFiNetworkIsSecure" in wifi:
				WiFiNetworkIsSecure = [ "WiFi Network Is Secure", str(wifi["WiFiNetworkIsSecure"]) ]
				temp_list.append( WiFiNetworkIsSecure )

			if "BSSID" in wifi:
				bssid = ["BSSID", wifi["BSSID"] ]
				temp_list.append( bssid )

			if "EnterpriseProfile" in wifi:
				if "EAPClientConfiguration" in wifi["EnterpriseProfile"]:
					if "UserName" in wifi["EnterpriseProfile"]["EAPClientConfiguration"]:
						username = [ "Username", wifi["EnterpriseProfile"]["EAPClientConfiguration"]["UserName"] ]
						temp_list.append( username )

			wifi_data_list.append( [name, temp_list ] )

		return wifi_data_list


	def wifiPlists(self):
		# 3ea0280c7d1bd352397fc658b2328a7f3b124f3b - Signatures

		# ade0340f576ee14793c607073bd7e8e409af07a8 - List of known networks
		# -- SecurityMode, WiFiNetworkRequiresPassword, lastAutoJoined, SSID_STR (name of wifi)
		# Strength, WEPKeyLen, lastJoined, WiFiNetworkIsSecure, ?80211W_ENABLED?, BSSID
		# NYU has: EnterpriseProfile/EAPClientConfiguration/UserName
		wifi_data_list = list()

		knownNets = os.path.join(self.appDir, "ade0340f576ee14793c607073bd7e8e409af07a8.plist")

		if os.path.exists(knownNets):
			
			try:
				data = biplist.readPlist(knownNets)

				wifi_data_list = self.returnWifiPlistData(data, wifi_data_list)

			except:
				try:
					data = plistlib.readPlist(knownNets)

					wifi_data_list = self.returnWifiPlistData(data, wifi_data_list)

				except:
					pass
					# print "Error reading wifi Plist"


		return wifi_data_list

	def wireless_SSID(self):
		wirelessSSID_dict = dict()

		wirelessSSID = os.path.join(self.appDir, "5ceceae7e957a53682cf500e5dd9499b5e2278aa.plist")

		if os.path.exists(wirelessSSID):

			data = biplist.readPlist(wirelessSSID)

			for key, value in data.iteritems():

				for k, v in value.iteritems():

					wirelessSSID_dict[k] = list()

					for i, j in v.iteritems():
						newstr = " ".join("{:02x}".format(ord(c)) for c in j)
						wirelessSSID_dict[k].append( [ "SSID", i] )
						wirelessSSID_dict[k].append( ["Data", newstr] )

		return wirelessSSID_dict

				
	def returnAppPlistData(self):
		return self.all_plist_data

	def retrieveData(self, mkey, plistData):
		if isinstance(plistData, dict):
			for key, value in plistData.iteritems():

				if isinstance(value, bool):
					newKey = mkey + "/" + str(key) 
					row = [ newKey[1:], str(value) ]

					self.plist_list.append( row )

				elif isinstance(value, list):
					for item in value:
						if isinstance(item, dict):
							newKey = mkey + "/" + str(key)
							retrieveData( newKey, item )

				elif isinstance(value, datetime.datetime):
					try:
						dateObj = value.strftime("%Y-%m-%d %H:%M:%S")
					except:
						dateObj = strftime_1900.strftime_1900(value, "%Y-%m-%d %H:%M:%S")
					newKey = mkey + "/" + str(key)
					row = [ newKey[1:], dateObj ]

					self.plist_list.append( row )

				elif isinstance(value, dict):
					newKey = mkey + "/" + str(key)

					self.retrieveData( newKey, value )

				elif isinstance(value, float):
					newKey = mkey + "/" + str(key)
					row = [ newKey[1:], str(value) ]

					self.plist_list.append( row )

				elif isinstance(value, int):
					newKey = mkey + "/" + str(key)
					row = [ newKey[1:], str(value) ]

					self.plist_list.append( row )

				elif isinstance(value, biplist.Data):
					newstr = " ".join("{:02x}".format(ord(c)) for c in value)
					newKey = mkey + "/" + str(key)
					row = [ newKey[1:], newstr ]

					self.plist_list.append( row )

				elif isinstance(value, str):
					newKey = mkey + "/" + str(key)
					row = [ newKey[1:], value ]

					self.plist_list.append( row )

				else:
					newKey = str(mkey) + "/" + str(key)
					row = [ newKey[1:], str(value)]

					self.plist_list.append( row )

		elif isinstance(plistData, biplist.Data):
			newstr = " ".join("{:02x}".format(ord(c)) for c in plistData)
			row = [mkey[1:], newstr]

			self.plist_list.append( row )

		else:
			row = [ mkey[1:],  str(plistData)]

			self.plist_list.append( row )

	def getInfoPlist(self):
		info = None
		infoPlist = self.appDir + "/Info.plist"

		try:
			info = biplist.readPlist(infoPlist)
		except:
			try:
				info = plistlib.readPlist(infoPlist)
			except:
				print "PlistParser.py: Error reading Info.plist"

		if info:
			InstalledApps = info.get("Installed Applications")

			for app in InstalledApps:
				# Using known app path to find SHA1 hash and associate
				# that to app name in 'Installed Applications'
				data = ("AppDomain-" + app + "-Library/Preferences/" + app + ".plist")
				encypted_file = hashlib.sha1(data).hexdigest()
				if (not self.encryptedDict.has_key(encypted_file)):
					self.encryptedDict[encypted_file] = app

