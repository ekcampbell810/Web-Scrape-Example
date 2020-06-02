import requests
from bs4 import BeautifulSoup as bs
import csv
from datetime import datetime
import re

# Declare variables
fiftyDualArray = []
finalFifty = []
elementFifty = []
dictionaryActive = []
myActiveList = []

# Declare Necesarry URLs
initialURL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=a&NextLicNum="
#lastURL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=911+RESTORATION+OF+ORANGE+COUNTY%27&NextLicNum=990168"


# Need a function to obtain HTML content of the webpage with 50 Contractor results
def scrapeFiftyPage(givenURL):
    page = requests.get(givenURL)
    soup = bs(page.content, "html.parser")
    fiftyTable = soup.find(id="ctl00_LeftColumnMiddle_Table1")
    fiftyArray = fiftyTable.find_all('table')

    for tableItem in fiftyArray:
        arraySplit = tableItem.find_all('tr')
        fiftyDualArray.append(arraySplit)

    for boxOfData in fiftyDualArray:
        elementFifty = []
        for lineItem in boxOfData:
            arraySecondSplit = lineItem.find_all('td')
            elementFifty.append(arraySecondSplit)
        finalFifty.append(elementFifty)

    #licenseURL = findLastLicense(finalFifty)
    #contractorNameURL = findLastName(finalFifty)

    finalActive = findActiveListings(finalFifty)
    arrayLength = len(finalActive)
    
    for i in range (0, arrayLength):
        cName = finalActive[i][0][1].get_text().strip()
        cLicense = finalActive[i][2][1].get_text().strip()
        cCity = finalActive[i][3][1].get_text().strip()
        cStatus = finalActive[i][4][1].get_text().strip()
        cPhone = findBusInfo(cLicense)
        cBondDict = findBondInfo(cLicense)
        element_dictionary = {
            'Contractor': cName,
            'License': cLicense,
            'City': cCity,
            'Status': cStatus,
            'Phone': cPhone,
            'Info': cBondDict["workCompSentence"],
            'Policy': cBondDict["policyNum"],
            'Effective': cBondDict["effectiveDate"],
            'Expiration': cBondDict["expirationDate"]
        }
        dictionaryActive.append(element_dictionary)
        #print(element_dictionary)

    return dictionaryActive


def findActiveListings(arrayOfFifty):
    for line in arrayOfFifty:
        status = line[4][1].get_text().strip()
        if status == "Active":
            myActiveList.append(line)
    return myActiveList

def findBusInfo(licenseNumber):
    licenseURL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/LicenseDetail.aspx?LicNum=" + licenseNumber
    licensePage = requests.get(licenseURL)
    licenseSoup = bs(licensePage.content, "html.parser")
    addressTable = licenseSoup.find(id="ctl00_LeftColumnMiddle_BusInfo")
    addressString = str(addressTable)
    addressArray = addressString.split("<br/>")
    #print(len(addressArray))
    #print(addressArray)
    addressArrayLength = len(addressArray)
    if addressArrayLength == 8:
        phoneNumber = addressArray[5].replace("Business Phone Number:", "")
    elif addressArrayLength == 6:
        phoneNumber = addressArray[3].replace("Business Phone Number:", "")
    elif addressArrayLength == 7:
        phoneNumber = addressArray[4].replace("Business Phone Number:", "")
    else:
        phoneNumber = "Check BusInfo Array Length"
    
    return phoneNumber
    
def findBondInfo(licenseNumber):
    licenseURL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/LicenseDetail.aspx?LicNum=" + licenseNumber
    licensePage = requests.get(licenseURL)
    licenseSoup = bs(licensePage.content, "html.parser")
    workCompTable = licenseSoup.find(id="ctl00_LeftColumnMiddle_WCStatus")
    workCompString = str(workCompTable)
    workCompArray = re.split('<p>|<a|style="font-size:13px">|<strong>|</strong>', workCompString)
    #print(len(workCompArray))
    #print(workCompArray)
    arrayLength = len(workCompArray)
    if arrayLength == 8:
        sentencePartOne = workCompArray[1].replace("</p>", "").strip()
        sentencePartTwo = ""
        bondDict = {
            "workCompSentence": sentencePartOne + " " +sentencePartTwo,
            "policyNum": "None",
            "effectiveDate": workCompArray[3].replace("<br/>", "").strip(),
            "expirationDate": workCompArray[5].replace("<br/>", "").strip()
        }
    elif arrayLength == 12:
        sentencePartOne = workCompArray[1].replace("</p>", "").strip()
        sentencePartTwo = workCompArray[3].replace("</a>", "").replace("</p>", "")
        bondDict = {
            "workCompSentence": sentencePartOne + " " + sentencePartTwo,
            "policyNum": workCompArray[5].replace("<br/>", ""),
            "effectiveDate": workCompArray[7].replace("<br/>", "").strip(),
            "expirationDate": workCompArray[9].replace("<br/>", "").strip()
        }
    elif arrayLength == 6:
        sentencePartOne = workCompArray[1].replace("</p>", "").strip()
        sentencePartTwo = ""
        bondDict = {
            "workCompSentence": sentencePartOne + " " + sentencePartTwo,
            "policyNum": "None",
            "effectiveDate": workCompArray[3].replace("<br/>", "").strip(),
            "expirationDate": "None"
        }
    elif arrayLength == 10:
        sentencePartOne = workCompArray[1].replace("</p>", "").strip()
        sentencePartTwo = ""
        bondDict = {
            "workCompSentence": sentencePartOne + " " + sentencePartTwo,
            "policyNum": workCompArray[3].replace("<br/>", "").strip(),
            "effectiveDate": workCompArray[5].replace("<br/>", "").strip(),
            "expirationDate": workCompArray[7].replace("<br/>", "").strip(),
        }    
    else:
        bondDict = {
            "workCompSentence": "Check Bond Array Length",
            "policyNum": "Check Bond Array Length",
            "effectiveDate": "Check Bond Array Length",
            "expirationDate": "Check Bond Array Length"
        }
    
    
    return bondDict
   

def findLastLicense(fiftyContractors):
    licenseURL = str(fiftyContractors[49][2][1].get_text().strip())
    return licenseURL

def findLastName(fiftyContractors):
    contractorURL = str(fiftyContractors[49][0][1].get_text().strip())
    contractorReplace = parseContractorName(contractorURL)
    return contractorReplace

def parseContractorName(lastContractor):
    contractorURL = lastContractor.replace("+", "%2b").replace("&", "%26").replace("/", "%2f").replace("#", "%23").replace(" ", "+")
    
    return contractorURL

def nextURL(contractorNameURL, licenseURL):
    nextPageURL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=" + contractorNameURL + "%27&NextLicNum=" + licenseURL
    print(nextPageURL)
    return nextPageURL

# open a csv file with append, so old data will not be erased
def writeToCSV(dataList):
    for entry in dataList:
        with open("index.csv", "a") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([entry["Contractor"], entry["License"], entry["City"], entry["Status"], entry["Phone"], entry["Info"], entry["Policy"], entry["Effective"], entry["Expiration"]])
    
        
URL = initialURL
# This was one of the stopping points
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=A+G+C%27&NextLicNum=911129"
# Another midpoint
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=A+K+G+HEATING+AIR+CONDITIONING+AND+GENERAL+CONSTRUCTION+SERVICES%27&NextLicNum=898866"
# Midpoint
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=A+PLUS+PLASTERING%27&NextLicNum=567797"
#Midpoint
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=ABRAM+CHARLIE+D%27&NextLicNum=318551"
#Midpoint
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=ACCURATE+FLOORING+INC%27&NextLicNum=967887" 
#Midpoint
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=ALVA+CONSTRUCTION%27&NextLicNum=720057"
#Midpoint
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=ANN+CON%27&NextLicNum=797203"
#Midpoint
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=ARCADIA+DEMOLITION+SERVICES%27&NextLicNum=538947"
#Midpoint
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=ARNEDO+WILLIAM+CONSTRUCTION%27&NextLicNum=682716"
#Midpoint
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=ARROW+PLUMBING%27&NextLicNum=182890"
#Midpoint
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=ASBESTOS+SPECIALISTS++INC%27&NextLicNum=635629"
#Midpoimt
#URL ="https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=BAGNELL+WILLIAM+ALDEN%27&NextLicNum=404433"
#Midpoint
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=CAMINO+VIEJO+PAVING+INC%27&NextLicNum=616444"
#Mipoint
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=CHI+WESTERN+OPERATIONS+INC%27&NextLicNum=711536"
#Midpoint
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=CLAY+NEAL%27&NextLicNum=425895"
#Midpoint
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=ELEMENTAL+TILE+DESIGN%27&NextLicNum=886208"
#Midpoint
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=FREASE+ELECTRICAL%27&NextLicNum=679149"
#mid
#URL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=FROST+AND+SON+ROOFING+CO%27&NextLicNum=181330"
lastURL = "https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/NameSearch.aspx?NextName=BAGNELL+WILLIAM+ALDEN%27&NextLicNum=404433"


while (URL != lastURL):
    #print(URL)
    myWebpageDict = scrapeFiftyPage(URL)
    writeToCSV(myWebpageDict)
    contractorNameURL = findLastName(finalFifty)
    licenseURL = findLastLicense(finalFifty)
    nextPageURL = nextURL(contractorNameURL, licenseURL)
    URL = nextPageURL
    fiftyDualArray = []
    finalFifty = []
    elementFifty = []
    dictionaryActive = []
    myActiveList = []

   