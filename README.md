# MountainProject_WebScraper
Python program to scrape the website "mountainproject.com" for publicly published information on routes and areas using the BeautifulSoup package.

## Description
This program does not produce any explicit output, but rather updates 3 pre-existing JSON files: (1) "parseHistory.json", (2) "areaData.json" and (3) "routeData.json".

The repository contains starting versions of these json files. The "areaData.json" file and "routeData.json" file are both blank to begin with. The "parseHistory.json" file contains the url "https://www.mountainproject.com/route-guide". This page can be thought of as the "root" of the mountainproject data tree, wherein each area is an internal node and the routes are the leafs of the tree.

As the program is run, each url in the "parseHistory.json" file is visited and parsed for both related urls (other areas/routes) and information about that area/route. Parsing each page for urls is how the "parseHistory.json" file is populated, and more areas/routes are scraped.

## Data being scraped

Area information saved during parsing includes: Name, main url, elevation, container for (route/area), location (lat/long), page data (total views, views/month, submission date, submitter), subPages (count, links), text fields (count, links), breadcrumb trail, comment count, photo count.

Route Information saved during parsing includes: name, urls (main page, vote page, main photo), location (lat/long), grade (YDS), votes (avg rating, review count), description (aggregate description, booleans for trad, sport, alpine, etc.), length (feet, pitches), page data (total views, views/month, submission date, submitter), first ascent info, text fields (field count, text fields), breadcrumb trail, comment count, photo count

## Usage

(1) Save all files in the repo in the same directory (3 json files and 2 python files)
(2) Run the program "Main.py" and let it run to completion
(3) Restart the program everytime it finishes until there are no files left unparsed in the "parseHistory.json" file

## Known Issues

(1) Probably the most serious bug is that the errors encountered during parsing are all eaten, instead of being saved somewhere. There are a number of try/except blocks that need serious improvement. None of them effectively solve the errors, they just prevent the program from crashing. Most errors come up if beautiful soup tried to access an element of the page that is not present.

(2) The program must be manually restarted each time it completes, which is ~10-15 times to capture all the data on mountainproject.com. It would be nice if this were automated to restart if there were new routes/areas added during the most recent iteration

(3) Mixed, ice, aid and bouldering climbing grades are not parsed correctly. Currently, this must be done in post-processing.

(4) There are some area and route links (<50) on mountainproject.com that are present on pages, but then do not link to an actual page (404 error). These end up not having their "parsedForUrls" and "parsedForData" fields marked as "True" in the "parseHistory.json" file, and thus the program will never quite finish completely. An exception should be added for this type of error to change the area/route type to "error" or "404" in the "parseHistory.json" file, and their "parsedFor..." fields marked as true so they are no longer considered.

## Ethical Considerations

Mountainproject.com does not condone web scraping of their site. I believe that publishing any data from mountainproject.com constitutes a copyright violation (either between you and MP.com, or you and the submitter of the content you scraped). For more information, check out MP.com's Terms of Service.

Additionally, some discussion has been had on the topic at https://www.mountainproject.com/forum/topic/108377792/scraping-data-from-mp-or-how-about-a-public-api.















