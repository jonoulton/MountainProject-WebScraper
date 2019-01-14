from bs4 import BeautifulSoup as soup
import urllib
import json
import string
import re
import csv
import queue
import pprint

#############################################################
#############################################################

# CLASS TO STORE ROUTE INFO
class RouteInfo:
    def __init__(self):
        self.json = dict({"name": None,
                      "pageType": None,
                      "urls": {
                          "mainPage": None,
                          "votePage": None,
                          "mainPhoto": None
                      },
                      "location": {
                          "type": None,
                          "latitude": None,
                          "longitude": None
                      },
                      "grade": {
                          "rateYDS": None,
                          "rateFrench": None,
                          "rateEwbanks": None,
                          "rateUIAA": None,
                          "rateZA": None,
                          "rateBritish": None,
                          "rateAid": None,
                          "commitment": None  # GRADE 1-6 CLIMB
                      },
                      "votes": {
                          "type": None,
                          "avgRating": None,
                          "reviewCount": None
                      },
                      "description": {
                          "aggregateData": None,
                          "trad": False,
                          "sport": False,
                          "boulder": False,
                          "aid": False,
                          "ice": False,
                          "mixed": False,
                          "alpine": False,
                          "TR": False
                      },
                      "length": {
                          "feet": None,
                          "pitches": None
                      },
                      "pageData": {
                          "totalViews": None,
                          "viewsPerMonth": None,
                          "submittedOn": None,
                          "submittedBy": None
                      },
                      "faInfo": None,
                      "textFields": {
                          "fieldCount": None
                          # ALL TEXT FIELDS INSERTED HERE
                      },
                      "breadcrumb": None,
                      "commentCount": None,
                      "photoCount": None
                      })

    ####################
    # GET DATA METHODS #
    ####################

    def get_main_urls(self, page):
        self.json['urls']['mainPage'] = page.find_all('link', {'rel': 'canonical'})[0]['href']
        self.json['urls']['votePage'] = page.find_all('a', {'title': 'View Stats'})[0]['href']

    def get_climb_type(self): # INCLUDED IN GET_ORIGINAL_JSON_DATA() METHOD
        # SPLIT UP DESCRIPTION DATA
        words = string_to_list(self.json['description']['aggregateData'], 0)  # ZERO IS TO INCLUDE WORDS

        if "Trad" in words:
            self.json['description']['trad'] = True
        if "Sport" in words:
            self.json['description']['sport'] = True
        if "Boulder" in words:
            self.json['description']['boulder'] = True
        if "Aid" in words:
            self.json['description']['aid'] = True
        if "Ice" in words:
            self.json['description']['ice'] = True
        if "Mixed" in words:
            self.json['description']['mixed'] = True
        if "Alpine" in words:
            self.json['description']['alpine'] = True
        if "TR" in words:
            self.json['description']['TR'] = True

    def get_original_json_data(self, page):
        # FETCH EXISTING JSON INFO IN DICT
        script = page.find_all(type='application/ld+json')
        originalJSON = json.loads(script[0].text)
        routeBreadcrumb = json.loads(script[1].text)

        # STORE EXISTING JSON INFO IN DICT
        try:
            self.json['name'] = originalJSON['name']
            self.json['pageType'] = originalJSON['@type']
            self.json['description']['aggregateData'] = originalJSON['description']
            self.json['urls']['mainPhoto'] = originalJSON['image']
            self.json['location']['type'] = originalJSON['geo']['@type']
            self.json['location']['latitude'] = originalJSON['geo']['latitude']
            self.json['location']['longitude'] = originalJSON['geo']['longitude']
            self.json['votes']['type'] = originalJSON['aggregateRating']['@type']
            self.json['votes']['avgRating'] = originalJSON['aggregateRating']['ratingValue']
            self.json['votes']['reviewCount'] = originalJSON['aggregateRating']['reviewCount']
            self.json['breadcrumb'] = routeBreadcrumb  # MIGHT WANT TO RE-DO THIS ONE MANUALLY LATER TO MATCH STD FORMAT
        except:
            self.json['name'] = originalJSON['name']
            self.json['description']['aggregateData'] = originalJSON['description']
            self.json['location']['type'] = originalJSON['geo']['@type']
            self.json['location']['latitude'] = originalJSON['geo']['latitude']
            self.json['location']['longitude'] = originalJSON['geo']['longitude']
            self.json['breadcrumb'] = routeBreadcrumb  # MIGHT WANT TO RE-DO THIS ONE MANUALLY LATER TO MATCH STD FORMAT
            self.json['votes']['type'] = originalJSON['aggregateRating']['@type']
            self.json['votes']['avgRating'] = originalJSON['aggregateRating']['ratingValue']
            self.json['votes']['reviewCount'] = originalJSON['aggregateRating']['reviewCount']

        # FINISH FILLING OUT THE ROUTE TYPE INFO
        self.get_climb_type()

        # ADD GRADE (DIFFICULTY RATING) TO DICT
        try:
            # if self.json['description']['trad'] or self.json['description']['sport']
            self.json['grade']['rateYDS'] = page.find_all('span', {'class': 'rateYDS'})[0].text.strip()
            # self.json['grade']['rateFrench'] = page.find_all('span', {'class': 'rateFrench'})[0].text.strip()
            # self.json['grade']['rateEwbanks'] = page.find_all('span', {'class': 'rateEwbanks'})[0].text.strip()
            # self.json['grade']['rateUIAA'] = page.find_all('span', {'class': 'rateUIAA'})[0].text.strip()
            # self.json['grade']['rateZA'] = page.find_all('span', {'class': 'rateZA'})[0].text.strip()
            # self.json['grade']['rateBritish'] = page.find_all('span', {'class': 'rateBritish'})[0].text.strip()
            ###
            # TODO -> ADD AID/COMMITMENT RATING, IF RELEVANT
            ###
        except:
            self.json['grade']['rateYDS'] = None

    def get_route_length(self, page):
        # GET ROUTE LENGTH INFO
        routeDescription = page.find(text='Type:').findNext('td').contents[0].strip()
        words = string_to_list(routeDescription, 1)
        try:
            self.json['length']['feet'] = words[0]
        except:
            self.json['length']['feet'] = None
        try:
            self.json['length']['pitches'] = words[1]
        except:
            self.json['length']['pitches'] = None

    def get_page_view_data(self, page):
        # GET PAGE VIEW INFO
        pageViewData = page.find(text='Page Views:').findNext('td').contents[0].strip()

        # GET RID OF WHITESPACES IN PAGE VIEW INFO
        i = 0
        length = len(pageViewData)
        while i < length:
            if pageViewData[i] in string.whitespace and pageViewData[i + 1] in string.whitespace:
                pageViewData = pageViewData[:i] + pageViewData[i + 1:]
                continue
            i += 1
            length = len(pageViewData)

        # GET RID OF COMMAS AND MIDDLE DOT
        pageViewData = pageViewData.replace(",", "")
        pageViewData = pageViewData.replace("· ", "")

        # SPLIT VIEW NUMBERS INTO VARS
        words = string_to_list(pageViewData, 1)

        # ADD PAGE VIEW DATA TO DICT
        self.json['pageData']['totalViews'] = words[0]
        self.json['pageData']['viewsPerMonth'] = words[1]

    def get_submission_info(self, page):
        try:
            # ADD "SHARED BY" DATA TO DICT
            sharedByAuthor = page.find(text='Shared By:').findNext('a').contents[0].strip()
            sharedByDate = page.find(text='Shared By:').findNext('td').contents[2].strip()
            sharedByDate = sharedByDate[3:]
            self.json['pageData']['submittedBy'] = sharedByAuthor
            self.json['pageData']['submittedOn'] = sharedByDate
        except:
            self.json['pageData']['submittedBy'] = None
            self.json['pageData']['submittedOn'] = None

    def get_FA_info(self, page):
        # ADD FA DATA TO DICT AS DATADUMP
        self.json['faInfo'] = page.find(text='FA:').findNext('td').contents[0].strip()

    def get_text_fields(self, page):
        # ADD TEXT FIELDS TO DICT
        textFieldTitles = []
        textFields = page.find_all('h2', {"class": "mt-2"})
        for item in textFields:
            self.json['textFields']['fieldCount'] = len(textFieldTitles)
        for title in textFieldTitles:
            if len(page.find(text=title).findNext('div').contents) is 1:
                item = page.find(text=title).findNext('div').contents[0].strip()
                self.json['textFields'][title.strip()] = item
            else:
                contents = page.find(text=title).findNext('div').contents
                stringAggregate = ""
                for item in contents:
                    try:
                        stringAggregate += item
                    except:
                        try:
                            stringAggregate += item.contents[0]
                        except:
                            stringAggregate += '\n'  # MAY NEED TO MODIFY THE NEW LINE IMPLEMENTATION?
                self.json['textFields'][title.strip()] = stringAggregate

    def get_comment_count(self, page):
        # GET NUMBER OF COMMENTS
        commentCount = page.find_all('h2', {"class": "dont-shrink"})[0].text
        words = string_to_list(commentCount, 1)
        self.json['commentCount'] = words[0]

    def get_photo_count(self, page):
        # GET NUMBER OF PHOTOS
        self.json['photoCount'] = len(page.find_all('div', {'class': 'col-xs-4 col-lg-3 card-with-photo'}))

    def get_route_data(self, page):
        self.get_main_urls(page)
        self.get_original_json_data(page)
        self.get_route_length(page)
        self.get_page_view_data(page)
        self.get_submission_info(page)
        self.get_FA_info(page)
        self.get_text_fields(page)
        self.get_comment_count(page)
        self.get_photo_count(page)

    #################
    # OTHER METHODS #
    #################

    def print_data(self):
        print(json.dumps(self.json, indent=4))

#############################################################

# CLASS TO STORE AREA INFO
class AreaInfo:
    def __init__(self):
        self.json = dict({"name": None,
                          "urls": {
                              "mainPage": None,
                              "mainPhoto": None
                          },
                          "elevation": None,
                          "containerFor": {
                              "routes": False,
                              "areas": False
                          },
                          "location": {
                              "type": None,
                              "latitude": None,
                              "longitude": None
                          },
                          "pageData": {
                              "totalViews": None,
                              "viewsPerMonth": None,
                              "submittedOn": None,
                              "submittedBy": None
                          },
                          "subPages": {
                              "subPageCount": None,
                              "links": None
                          },
                          "textFields": {
                              "fieldCount": None
                              # ALL TEXT FIELDS INSERTED HERE
                          },
                          "breadcrumb": None,
                          "commentCount": None,
                          "photoCount": None
                          })

    ####################
    # GET DATA METHODS #
    ####################

    def get_name(self, page):
        if page.find_all('h3')[0].text.strip()[:1] == "A":
            self.json['name'] = page.find_all('h3')[0].text.strip()[9:]
        elif page.find_all('h3')[0].text.strip()[:1] == "R":
            self.json['name'] = page.find_all('h3')[0].text.strip()[10:]

    def get_container_for(self, page):
        if page.find_all('h3')[0].text.strip()[:1] == "A":
            self.json['containerFor'] = "areas"
        elif page.find_all('h3')[0].text.strip()[:1] == "R":
            self.json['containerFor'] = "routes"

    def get_main_urls(self, page):
        self.json['urls']['mainPage'] = page.find_all('link', {'rel': 'canonical'})[0]['href']

    def get_elevation(self, page):
        try:
            elev = page.find(text='Elevation:').findNext('td').contents[0]
            newElev = ""
            for c in elev:
                if str.isdigit(c):
                    newElev += c
            self.json['elevation'] = newElev
        except:
            self.json['elevation'] = None

    def get_breadcrumbs(self, page):
        try:
            # FETCH EXISTING JSON INFO IN DICT
            script = page.find_all(type='application/ld+json')
            routeBreadcrumb = json.loads(script[0].text)

            # STORE EXISTING JSON INFO IN DICT
            self.json['breadcrumb'] = routeBreadcrumb  # MIGHT WANT TO RE-DO THIS ONE MANUALLY LATER TO MATCH STD FORMAT
        except:
            self.json['breadcrumb'] = None

    def get_page_view_data(self, page):
        try:
            # GET PAGE VIEW INFO
            pageViewData = page.find(text='Page Views:').findNext('td').contents[0].strip()

            # GET RID OF WHITESPACES IN PAGE VIEW INFO
            i = 0
            length = len(pageViewData)
            while i < length:
                if pageViewData[i] in string.whitespace and pageViewData[i + 1] in string.whitespace:
                    pageViewData = pageViewData[:i] + pageViewData[i + 1:]
                    continue
                i += 1
                length = len(pageViewData)

            # GET RID OF COMMAS AND MIDDLE DOT
            pageViewData = pageViewData.replace(",", "")
            pageViewData = pageViewData.replace("· ", "")

            # SPLIT VIEW NUMBERS INTO VARS
            words = string_to_list(pageViewData, 1)

            # ADD PAGE VIEW DATA TO DICT
            self.json['pageData']['totalViews'] = words[0]
            self.json['pageData']['viewsPerMonth'] = words[1]
        except:
            self.json['pageData']['totalViews'] = None
            self.json['pageData']['viewsPerMonth'] = None

    def get_submission_info(self, page):
        try:
            # ADD "SHARED BY" DATA TO DICT
            sharedByAuthor = page.find(text='Shared By:').findNext('a').contents[0].strip()
            sharedByDate = page.find(text='Shared By:').findNext('td').contents[2].strip()
            sharedByDate = sharedByDate[3:]
            self.json['pageData']['submittedBy'] = sharedByAuthor
            self.json['pageData']['submittedOn'] = sharedByDate
        except:
            self.json['pageData']['submittedBy'] = None
            self.json['pageData']['submittedOn'] = None

    def get_coordinates(self, page):
        try:
            gps = page.find(text='GPS:').findNext('td').contents[0].strip()
            coord = ["", ""]    # LAT / LONG
            switch = 0
            for c in gps:
                if c == ",":
                    switch = 1
                    continue
                if c == " ":
                    continue
                else:
                    coord[switch] += c
            self.json['location']['type'] = 'geoCoordinates'
            self.json['location']['latitude'] = coord[0]
            self.json['location']['longitude'] = coord[1]
        except:
            self.json['location']['type'] = None
            self.json['location']['latitude'] = None
            self.json['location']['longitude'] = None

    def get_subpages(self, page):
        try:
            subpages = page.find_all('div', {'class': 'lef-nav-row'})
            self.json['subPages']['subPageCount'] = len(subpages)
            subPageLinks = []
            for item in subpages:
                subPageLinks.append([item.findNext('a')['href'], item.findNext('a').contents[0]])
            self.json['subPages']['links'] = subPageLinks
        except:
            self.json['subPages']['subPageCount'] = None
            self.json['subPages']['links'] = None

    def get_text_fields(self, page):
        try:
            textFieldTitles = []
            textFields = page.find_all('h2', {"class": "mt-2"})
            for item in textFields:
                textFieldTitles.append(item.findNext('div').contents[0])
                self.json['textFields']['fieldCount'] = len(textFieldTitles)
            for title in textFieldTitles:
                if len(page.find(text=title).findNext('div').contents) is 1:
                    item = page.find(text=title).findNext('div').contents[0].strip()
                    self.json['textFields'][title.strip()] = item
                else:
                    contents = page.find(text=title).findNext('div').contents
                    stringAggregate = ""
                    for item in contents:
                        try:
                            stringAggregate += item
                        except:
                            try:
                                stringAggregate += item.contents[0]
                            except:
                                stringAggregate += '\n'  # MAY NEED TO MODIFY THE NEW LINE IMPLEMENTATION?
                    self.json['textFields'][title.strip()] = stringAggregate
        except:
            self.json['textFields']['fieldCount'] = None

    def get_area_data(self, page):
        self.get_name(page)
        self.get_container_for(page)
        self.get_main_urls(page)
        self.get_elevation(page)
        self.get_breadcrumbs(page)
        self.get_page_view_data(page)
        self.get_submission_info(page)
        self.get_coordinates(page)
        self.get_subpages(page)
        self.get_text_fields(page)

    #################
    # OTHER METHODS #
    #################

    def print_data(self):
        print(json.dumps(self.json, indent=4))

#############################################################

# SPIDER CLASS
class Spider:
    def __init__(self):
        self.parseHistory = None    # DICTIONARY OF PARSING HISTORY
        self.urlIterator = None     # ITERATOR OVER SEARCH HISTORY KEYS
        self.routeData = None       # DICTIONARY OF SAVED ROUTE DATA
        self.areaData = None        # DICTIONARY OF SAVED AREA DATA
        self.currentUrl = None      # URL FOR CURRENT PAGE

    #######################
    # INITIALIZER METHODS #
    #######################

    # METHOD TO GET SEARCH HISTORY (JSON -> PYTHON DICT)
    def get_search_history(self):
        with open("./parseHistory.json", 'r') as jsonFile:
            reader = jsonFile.read()
            self.parseHistory = json.loads(reader)

    # METHOD TO GET ROUTE DATA (JSON -> PYTHON DICT)
    def get_existing_route_data(self):
        try:
            with open("routeData.json", 'r') as jsonFile:
                reader = jsonFile.read()
                self.routeData = json.loads(reader)
        except:
            self.routeData = {}

    # METHOD TO GET AREA DATA (JSON -> PYTHON DICT)
    def get_existing_area_data(self):
        try:
            with open("./areaData.json", 'r') as jsonFile:
                reader = jsonFile.read()
                self.areaData = json.loads(reader)
        except:
            self.areaData = {}

    # METHOD TO GET SEARCH HISTORY ITERATOR
    def get_url_iterator(self):
        self.urlIterator = iter(self.parseHistory)

    # METHOD TO RUN ALL THE INITIALIZER STEPS TOGETHER
    def initialize(self):
        self.get_search_history()
        self.get_existing_route_data()
        self.get_existing_area_data()
        self.get_url_iterator()

    ################
    # CRAWL METHOD #
    ################

    # METHOD TO PARSE DATA
    def crawl(self):
        startingUrls = list(self.urlIterator)
        counter = 0
        for url in startingUrls:

            try:
                # IF ALREADY PARSED, SKIP
                if self.parseHistory[url]["parsedForUrls"] and self.parseHistory[url]["parsedForData"]:
                    continue

                # UPDATE STARTING URL
                print("Starting to scrape", url)
                self.currentUrl = url

                # OTHERWISE, GET NEW DATA
                if not self.parseHistory[url]["parsedForUrls"]:
                    self.get_related_urls()
                    self.parseHistory[url]["parsedForUrls"] = True
                if not self.parseHistory[url]["parsedForData"]:
                    if self.parseHistory[url]["type"] == "route":
                        self.harvest_route_data()
                        self.parseHistory[url]["parsedForData"] = True
                    elif self.parseHistory[url]["type"] == "area":
                        self.harvest_area_data()
                        self.parseHistory[url]["parsedForData"] = True
            except:
                continue

            # UPDATE FILES AFTER EVERY 10 URLS
            counter += 1
            if counter % 500 == 0 and counter > 499:
                print("Updating JSON files with new information")
                self.update_files()

        self.update_files()

        print()
        print("Complete")

    ####################################
    # METHODS TO ACTUALLY HARVEST DATA #
    ####################################

    # METHOD TO GET RELATED URLS
    def get_related_urls(self):
        page = get_page_soup(self.currentUrl)  # CHANGE TO GET_PAGE_SOUP ONCE ONLINE
        area_urls = page.find_all('a', href=re.compile('^https://www.mountainproject.com/area/[0-9].+'))
        final_area_urls = []
        filter2 = re.compile('^((?!\?print=1).)*$')

        for url in area_urls:
            url = url['href']
            url = filter2.match(url)
            if url != None:
                final_area_urls.append(url.string)
        for url in final_area_urls:
            if url not in self.parseHistory:
                self.parseHistory[url] = {"type": "area", "parsedForUrls": False, "parsedForData": False}

        route_urls = page.find_all('a', href=re.compile('^https://www.mountainproject.com/route/[0-9].+'))
        final_route_urls = []
        for url in route_urls:
            url = url['href']
            url = filter2.match(url)
            if url != None:
                final_route_urls.append(url.string)
        for url in final_route_urls:
            if url not in self.parseHistory:
                self.parseHistory[url] = {"type": "route", "parsedForUrls": False, "parsedForData": False}

    # METHOD TO GET ROUTE DATA FROM PAGE
    def harvest_route_data(self):
        routeInfo = RouteInfo()
        routeInfo.get_route_data(get_page_soup(self.currentUrl))  # CHANGE TO "GET PAGE SOUP" ONCE ONLINE
        self.routeData[self.currentUrl] = routeInfo.json

    # METHOD TO GET AREA DATA FROM PAGE
    def harvest_area_data(self):
        areaInfo = AreaInfo()
        areaInfo.get_area_data(get_page_soup(self.currentUrl))
        self.areaData[self.currentUrl] = areaInfo.json

    #######################
    # UPDATE FILES METHOD #
    #######################

    # METHOD TO UPDATE SEARCH HISTORY
    def update_search_history(self):
        with open('parseHistory.json', 'w') as jsonFile:
            jsonFile.write(json.dumps(self.parseHistory, indent=4))

    # METHOD TO UPDATE ROUTE DATA
    def update_route_data(self):
        with open('routeData.json', 'w') as jsonFile:
            jsonFile.write(json.dumps(self.routeData, indent=4))

    # METHOD TO UPDATE AREA DATA
    def update_area_data(self):
        with open('areaData.json', 'w') as jsonFile:
            jsonFile.write(json.dumps(self.areaData, indent=4))

    # METHOD TO RUN ALL THE "UPDATE FILES" STEPS TOGETHER
    def update_files(self):
        self.update_search_history()
        self.update_route_data()
        self.update_area_data()

#############################################################
#############################################################

#######################
# NON-CLASS FUNCTIONS #
#######################

# FUNCTION TO MAKE FULL HTML SOUP
def get_page_soup(url):
    try:
        # OPENING CONNECTION, GRABBING PAGE, SAVING INTO VARIABLE, CLOSE THE CLIENT
        client = urllib.request.urlopen(url)
        page_html = client.read()
        client.close()
        page_soup = soup(page_html, 'html.parser')
        return page_soup
    except:
        return None

# FOR TESTING
def read_local_html(path):
    page_soup = soup(open(path), 'html.parser')
    return page_soup

def string_to_list(s, onlyDigits):
    words = []
    currentWord = ""
    counter = 0
    for c in s:
        if c in string.whitespace or c == '/' or c == ",":
            if onlyDigits:
                if currentWord.isdigit():
                    words.append(currentWord)
            else:
                words.append(currentWord)
            currentWord = ""
            counter += 1
        elif counter == len(s)-1:
            currentWord += c
            if onlyDigits:
                if currentWord.isdigit():
                    words.append(currentWord)
            else:
                words.append(currentWord)
            counter += 1
        else:
            currentWord += c
            counter += 1
    return words

# EXTRA FUNCTIONS
def make_test_json_file():
    file = {}
    urls = ['./htmlFiles/NakedEdge.html', './htmlFiles/GermFree.html', './htmlFiles/TheSlit.html']
    for url in urls:
        file[url] = dict({"type": "route", "parsedForUrls": False, "parsedForData": False})
    with open("./parseHistory.json", 'w') as jsonFile:
        jsonFile.write(json.dumps(file))

        """
        urls = ['./htmlFiles/beckey-chouinard.html', './htmlFiles/cassinRidge.html', './htmlFiles/casual.html',
                './htmlFiles/cutFingerCrackV1.html', './htmlFiles/epinephrine.html', './htmlFiles/GermFree.html',
                './htmlFiles/highExposure.html', './htmlFiles/monkeyMan.html', './htmlFiles/moonlight.html',
                './htmlFiles/NakedEdge.html', './htmlFiles/Nose.html', './htmlFiles/NWfaceHD.html',
                './htmlFiles/SEButtress.html', './htmlFiles/snakeDike.html', './htmlFiles/SouthButtDenali.html',
                './htmlFiles/TheSlit.html', './htmlFiles/upperExum.html']
        """

def make_test_json_area_file():
    file = {}
    urls = ['./htmlFiles/GTNP.html', './htmlFiles/RedgardenWall.html', 'RGTower1.html']
    for url in urls:
        file[url] = dict({"type": "area", "parsedForUrls": False, "parsedForData": False})
    with open("./parseHistory.json", 'w') as jsonFile:
        jsonFile.write(json.dumps(file))
