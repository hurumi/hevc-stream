import pandas as pd
import json

from google_patent_scraper import scraper_class

PATENT_SOURCE = '2022.02.04-Website-Patent-List.csv'
PATENT_CSV    = 'patent.csv'
PATENT_JSON   = 'patent.json'

# load data
df = pd.read_csv( PATENT_SOURCE, skiprows=1 )

# drop some columns
df.drop( 'Count (Claims)', axis=1, inplace=True )
df.drop( 'Claim Number',   axis=1, inplace=True )
df.drop( 'Category',       axis=1, inplace=True )
df.drop( 'Representative HEVC/H.265 Sections (Version 2, unless otherwise specified)', axis=1, inplace=True )

# remove redundant rows by patent number
df.drop_duplicates( subset=['Patent Number'], inplace=True )

# save dataframe
df.to_csv( PATENT_CSV, index=False )

# crawling
patent_list = df['Patent Number'].values

# Initialize scraper class
scraper=scraper_class()

# Add patents to list
for elem in patent_list:
    scraper.add_patents( elem )

# Scrape all patents
scraper.scrape_all_patents()

# write to file
result = {}
for patent in patent_list:
    try:
        parsed = scraper.parsed_patents[ patent ]
        result[ patent ] = parsed
    except:
        pass

with open( PATENT_JSON, 'w' ) as fp:
    json.dump( result, fp, indent=4 )