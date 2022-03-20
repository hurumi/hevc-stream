import pandas as pd
import json

from google_patent_scraper import scraper_class

PATENT_JSON     = 'patent.json'
PATENT_EXT_JSON = 'patent_ext.json'

# load json
with open( PATENT_JSON, 'r' ) as fp:
    data = json.load( fp )

# find empty list
empty_list = []
for elem in data.keys():
    if data[elem] == {}:
        empty_list.append( elem )

# find EP list
ep_list = []
for elem in empty_list:
    pos = elem.find( '-EP' )
    if pos > 0:
        val = elem[pos+1:]
        if val not in ep_list:
            ep_list.append( val )

# Initialize scraper class
scraper=scraper_class()

# Add patents to list
for elem in ep_list:
    scraper.add_patents( elem )

# Scrape all patents
scraper.scrape_all_patents()

# write to file
result = {}
for patent in ep_list:
    try:
        parsed = scraper.parsed_patents[ patent ]
        result[ patent ] = parsed
    except:
        pass

with open( PATENT_EXT_JSON, 'w' ) as fp:
    json.dump( result, fp, indent=4 )