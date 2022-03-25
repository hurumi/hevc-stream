#
# HEVC Advance Statistics
#

# disable SSL warnings
import urllib3
urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )

# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------

import streamlit  as st
import pandas     as pd
import feedparser as fp
import requests
import time

from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import JsCode

# -------------------------------------------------------------------------------------------------
# Globals
# -------------------------------------------------------------------------------------------------

PATENT_CSV      = 'patent_new.csv'
COUNTRY_CSV     = 'code.csv'

linkRenderer    = JsCode(
    '''
    function(params) {
        return '<a href="https://patents.google.com/patent/' + 
                            params.value + '" target="_blank">'+ params.value+'</a>'
    }
    '''
)

RSS_URL        = 'https://news.google.com/rss/search?q=hevc when:1y&hl=en-US&gl=US&ceid=US:en'
MAX_NEWS_ITEMS = 30

# -------------------------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------------------------

def get_country_df( _df ):

    temp   = _df[ "Country New" ].value_counts()
    result = pd.DataFrame()
    result['Country'        ] = temp.index
    result['NumberOfPatents'] = temp.values
    result['Ratio(%)'       ] = temp.values / sum( temp.values ) * 100

    return result

def get_licensor_df( _df ):

    temp   = _df[ "Licensor" ].value_counts()
    result = pd.DataFrame()
    result['Licensor'       ] = temp.index
    result['NumberOfPatents'] = temp.values
    result['Ratio(%)'       ] = temp.values / sum( temp.values ) * 100

    return result

def get_inventor_df( _df ):

    # get list of inventor rows
    tm_list = list( _df[ "Inventor" ] )

    # get list of inventors
    tm_split_list     = []
    for idx, elem in enumerate( tm_list ):
        val = elem.split('|')
        tm_split_list += val
    
    # get unique list of inventors
    tm_u_list = list( set( tm_split_list ) )

    # compute ratios
    ratio_dict      = { elem:0 for elem in tm_u_list }
    for elem in tm_split_list:
        ratio_dict[elem] += 1

    # sort
    cn_list = []
    for elem in tm_u_list:
        cn_list.append( [ ratio_dict[elem], elem ] )
    cn_list.sort( reverse=True )

    # make dataframe
    total = len( tm_list )
    result = pd.DataFrame( columns=[ 'Inventor', 'NumberOfPatents', 'Ratio(%)' ] )
    result['Inventor'       ] = [ elem[1] for elem in cn_list ]
    result['NumberOfPatents'] = [ elem[0] for elem in cn_list ]
    result['Ratio(%)'       ] = [ round( elem[0]/total*100, 2 ) for elem in cn_list ]

    return result

def get_filtered_df( org_df, profile, country, licensor, inventor ):

    if profile == 'All': 
        new_df = org_df
    else:
        new_df = org_df[ org_df['Profile'] == profile ]    

    if country  != 'All': new_df = new_df[ new_df['Country New'] == country ]
    if licensor != 'All': new_df = new_df[ new_df['Licensor'   ] == licensor ]
    if inventor != 'All': new_df = new_df[ new_df['Inventor'   ].str.contains( inventor ) ]

    return new_df

def get_ccode_dict( df ):

    code_list    = df['Code'   ]
    country_list = df['Country']

    dict_from_list = dict( zip( code_list, country_list ) )
    dict_from_list[ 'All' ] = 'All'

    return dict_from_list 

# -------------------------------------------------------------------------------------------------
# Functions (Callbacks)
# -------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------
# Load data
# -------------------------------------------------------------------------------------------------

# read source data
df = pd.read_csv( PATENT_CSV  )
cc = pd.read_csv( COUNTRY_CSV )

# country code dictionary
ccode_dict  = get_ccode_dict( cc )

# -------------------------------------------------------------------------------------------------
# Layout
# -------------------------------------------------------------------------------------------------

# add sidebar
st.sidebar.title( 'HEVC Advance Stream' )
menu = st.sidebar.radio( "MENU", ( 'Patent Filter', 'Reference', 'Industry', 'News' ) )
st.sidebar.markdown( '[**GitHub**](https://github.com/hurumi/hevc-stream)' )

# -------------------------------------------------------------------------------------------------
# Filter
# -------------------------------------------------------------------------------------------------

if menu == 'Patent Filter':
  
    st.subheader( 'Patent Filter' )
    st.caption  ( 'Source update: 2022-02-04' )

    col1, col2 = st.columns(2)

    # ---------------------------------------------------------------------------------------------
    # Profile selector
    # ---------------------------------------------------------------------------------------------

    values  = [ 'Main/Main10', 'Multiview', 'Optional', 'Range Extension', 'Scalability', 'All' ]
    profile = col1.selectbox( 'Profile', values, key='profile' )

    # update
    new_df = get_filtered_df( df, profile, 'All', 'All', 'All' )

    # ---------------------------------------------------------------------------------------------
    # Country selector
    # ---------------------------------------------------------------------------------------------

    _tmp_df = get_country_df( new_df )
    values = [ 'All' ] + list( _tmp_df['Country'] )
    try:
        index = values.index( st.session_state.country )
    except:
        index = 0
    country = col2.selectbox( 'Country', values, index=index, key='country', format_func=lambda x: ccode_dict[x] )

    # update
    new_df = get_filtered_df( new_df, 'All', country, 'All', 'All' )

    # ---------------------------------------------------------------------------------------------
    # Licensor selector
    # ---------------------------------------------------------------------------------------------

    _tmp_df = get_licensor_df( new_df )
    values = [ 'All' ] + list( _tmp_df['Licensor'] )
    try:
        index = values.index( st.session_state.licensor )
    except:
        index = 0    
    licensor = col1.selectbox( 'Licensor', values, index=index, key='licensor' )

    # update
    new_df = get_filtered_df( new_df, 'All', 'All', licensor, 'All' )

    # ---------------------------------------------------------------------------------------------
    # Inventor selector
    # ---------------------------------------------------------------------------------------------

    _tmp_df = get_inventor_df( new_df )
    values = [ 'All' ] + list( _tmp_df['Inventor'] )
    try:
        index = values.index( st.session_state.inventor )
    except:
        index = 0
    inventor = col2.selectbox( 'Inventor', values, index=index, key='inventor' )

    # update
    new_df = get_filtered_df( new_df, 'All', 'All', 'All', inventor )

    # ---------------------------------------------------------------------------------------------
    # Statistics selector
    # ---------------------------------------------------------------------------------------------

    values  = [ 'Raw Data', 'Country', 'Licensor', 'Inventor' ]
    stat    = st.selectbox( 'Statistics', values )

    if stat == 'Country':
        out_df = get_country_df( new_df )
    elif stat == 'Licensor':
        out_df = get_licensor_df( new_df )
    elif stat == 'Inventor':
        out_df = get_inventor_df( new_df )
        # Some explanations
        st.caption( "(Note) UNKNOWN Inventor = no entry in google patent search" )
    else:
        out_df = new_df
        # Some explanations
        st.caption( "(Note) UNKNOWN Inventor = no entry in google patent search" )

    # download button
    total = len( out_df )
    csv = out_df.to_csv().encode( 'utf-8' )
    st.download_button(
        label     = f"Download filtered data as CSV (total no. of entries = {total})",
        data      = csv,
        file_name = f'{profile}-{country}-{licensor}-{inventor}-{stat}.csv',
        mime      = 'text/csv',
    )

    # write dataframe
    gb = GridOptionsBuilder.from_dataframe( out_df )
    for num_col in out_df.columns:
        if '%' in num_col:
            gb.configure_column( num_col, header_name=num_col, valueFormatter='value.toFixed(2)' )
        if num_col == 'Patent Number New':
            gb.configure_column( num_col, header_name=num_col, cellRenderer=linkRenderer )

    gb.configure_pagination()
    go = gb.build()
    ret = AgGrid( out_df, gridOptions=go, theme='light', allow_unsafe_jscode=True )

# -------------------------------------------------------------------------------------------------
# Reference
# -------------------------------------------------------------------------------------------------

if menu == 'Reference':

    st.subheader( 'Reference' )

    st.write( "- AccessAdvance Home: [Link](https://accessadvance.com)" )
    st.write( "- HEVC Advance Patent Overview: [Link](https://accessadvance.com/licensing-programs/hevc-advance/)" )
    st.write( "- HEVC Advance Licensor List: [Link](https://accessadvance.com/hevc-advance-patent-pool-licensors/)" )
    st.write( "- HEVC Advance Licensee List: [Link](https://accessadvance.com/hevc-advance-patent-pool-licensees/)" )
    st.write( "- HEVC Advance Royalty Rate Structure: [Link](https://accessadvance.com/hevc-advance-patent-pool-detailed-royalty-rates/)" )
    st.write( "- HEVC Advance Patent List: [Link](https://accessadvance.com/hevc-advance-patent-list/)" )

    st.write( "##### HEVC WORLDWIDE ESSENTIAL PATENTS LANDSCAPE" )
    st.write( "\n" )

    land_url = 'https://accessadvance.com/wp-content/uploads/2022/01/2022Q1-HEVC-Patent-Diagram-01-31-22-1536x1152.jpg'
    st.image( land_url, use_column_width='auto' )

# -------------------------------------------------------------------------------------------------
# Industry
# -------------------------------------------------------------------------------------------------

if menu == 'Industry':

    st.subheader( 'Industry' )

    col1, col2 = st.columns(2)
    
    # ---------------------------------------------------------------------------------------------
    # Mobile devices
    # ---------------------------------------------------------------------------------------------

    col1.write  ( '##### Supported mobile devices' )
    col1.caption( 'Source: [arlo](https://www.arlo.com/en_no/support/faq/000062189/Which-devices-are-supported-for-HEVC-4K-or-2K-playback)' )

    text = '''
        - iPhone 7/7 Plus or newer
        - iPad Pro or newer
        - Samsung Galaxy S7/S7 Plus or newer
        - Galaxy Note 8 or newer
        - Google Pixel/Pixel XL or newer
        - Huawei P9 or newer
        - Xiaomi Mi 5 or newer
        - LG G5 or newer
        - HTC U10 or newer
        - Sony Xperia X or newer
        - Moto Z or newer
        - OnePlus 3 or newer.   
    '''
    col1.markdown( text )

    # ---------------------------------------------------------------------------------------------
    # Browers
    # ---------------------------------------------------------------------------------------------

    col1.write  ( '##### Supported browsers' )
    col1.caption( 'Source: [wikipedia](https://en.wikipedia.org/wiki/High_Efficiency_Video_Coding#Implementations_and_products)' )

    text = '''
        - Android browser (since version 5)
        - Safari (since version 11)
    '''
    col1.markdown( text )

    # ---------------------------------------------------------------------------------------------
    # Processors
    # ---------------------------------------------------------------------------------------------

    col2.write  ( '##### Supported processors' )
    col2.caption( 'Source: [faceofit](https://www.faceofit.com/intel-amd-nvidia-support-4k-native-hevc-decoder/)' )

    text = '''
        - Intel Skylake (6th-generation) or newer
        - AMD Carizzo APU (6th-generation) or newer
        - NVidia 900 Series GPU or newer
        - AMD Radeon R9 Fury GPUs or newer
        - Qualcomm Snapdragon 805 or newer
        - Apple A8 or newer
    '''
    col2.markdown( text )

    # ---------------------------------------------------------------------------------------------
    # Streaming services
    # ---------------------------------------------------------------------------------------------

    col2.write  ( '##### Supported streaming services' )
    col2.caption( 'Source: [streamingmedia](https://www.streamingmedia.com/Articles/ReadArticle.aspx?ArticleID=148866)' )

    text = '''
        - Neflix
        - Amazon Prime
        - Disney+
    '''
    col2.markdown( text )

    # ---------------------------------------------------------------------------------------------
    # Other devices
    # ---------------------------------------------------------------------------------------------

    col2.write  ( '##### Other supported devices' )
    col2.caption( 'Source: [faceofit](https://www.faceofit.com/intel-amd-nvidia-support-4k-native-hevc-decoder/)' )

    text = '''
        - XBox One or newer
        - Roku 4 or newer
        - Amazon Fire TV (2nd-generation) or newer
    '''
    col2.markdown( text )

    # ---------------------------------------------------------------------------------------------
    # Adoption ratio for each mobile OS
    # ---------------------------------------------------------------------------------------------

    st.write  ( '##### Adoption ratio for each mobile OS' )
    st.caption( 'Source: [scientiamobile](https://www.scientiamobile.com/growing-support-of-hevc-or-h-265-video-on-mobile-devices/) (2018)' )

    land_url = 'https://www.scientiamobile.com/wp-content/uploads/2018/08/HEVC-Pie-Support-by-OS1200b.png'
    st.image( land_url, use_column_width='auto' )

# -------------------------------------------------------------------------------------------------
# News
# -------------------------------------------------------------------------------------------------

if menu == 'News':

    st.subheader( 'News' )
    st.caption( 'Source: [googlenews](https://news.google.com/search?q=hevc&hl=en-US&gl=US&ceid=US%3Aen)' )

    re = requests.get( RSS_URL, verify=False )
    if re.status_code == 200:
        # parsing
        parse = fp.parse( re.text )

        # for each entry
        for entry in parse['entries'][:MAX_NEWS_ITEMS]:
            date_str = time.strftime( '%Y-%m-%d', entry["published_parsed"] )
            text = f'<b>{entry["source"]["title"]}</b> &nbsp; <a href="{entry["link"]}">{entry["title"]}</a> ({date_str})'
            st.markdown( text, unsafe_allow_html=True )
        
    else:
        st.write( '##### No news or there are some issues. Please come back later.' )