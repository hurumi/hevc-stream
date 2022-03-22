#
# HEVC Advance Statistics
#

# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------

import streamlit as st
import pandas    as pd
import json

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

# -------------------------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------------------------

def get_country_df( _df ):

    # get list of licensors
    tm_list   = list( _df[ "Country New" ] )

    # get unique list of licensors
    tm_u_list = list( set( tm_list ) )

    # count & sort
    cn_list = []
    for elem in tm_u_list:
        count = tm_list.count( elem )
        cn_list.append( [ count, elem ] )
    cn_list.sort( reverse=True )

    # make dataframe
    total = len( tm_list )
    result = pd.DataFrame( columns=[ 'Country', 'NumberOfPatents', "Ratio(%)" ] )
    result['Country'        ] = [ elem[1] for elem in cn_list ]
    result['NumberOfPatents'] = [ elem[0] for elem in cn_list ]
    result['Ratio(%)'       ] = [ round( elem[0]/total*100, 2 ) for elem in cn_list ]

    return result

def get_licensor_df( _df ):

    # get list of licensors
    tm_list   = list( _df[ "Licensor" ] )

    # get unique list of licensors
    tm_u_list = list( set( tm_list ) )

    # count & sort
    cn_list = []
    for elem in tm_u_list:
        count = tm_list.count( elem )
        cn_list.append( [ count, elem ] )
    cn_list.sort( reverse=True )

    # make dataframe
    total = len( tm_list )
    result = pd.DataFrame( columns=[ 'Licensor', 'NumberOfPatents', "Ratio(%)" ] )
    result['Licensor'       ] = [ elem[1] for elem in cn_list ]
    result['NumberOfPatents'] = [ elem[0] for elem in cn_list ]
    result['Ratio(%)'       ] = [ round( elem[0]/total*100, 2 ) for elem in cn_list ]

    return result

def get_inventor_df( _df ):

    # get list of inventor rows
    tm_list = list( _df[ "Inventor" ] )

    # get list of inventors
    tm_split_list     = []
    tm_split_list_ext = []
    for idx, elem in enumerate( tm_list ):
        val = elem.split('|')
        tm_split_list += val
        tm_split_list_ext.append( val )
    
    # get unique list of inventors
    tm_u_list = list( set( tm_split_list ) )
    
    # normalized ratio
    norm_ratio_dict = { elem:0 for elem in tm_u_list }
    for elem1 in tm_split_list_ext:
        for elem2 in elem1:
            norm_ratio_dict[elem2] += 1.0/len(elem1)

    # count & sort
    cn_list = []
    for elem in tm_u_list:
        count = tm_split_list.count( elem )
        cn_list.append( [ count, elem, norm_ratio_dict[elem] ] )
    cn_list.sort( reverse=True )

    # make dataframe
    total = len( tm_list )
    result = pd.DataFrame( columns=[ 'Inventor', 'NumberOfPatents', 'Ratio(%)', 'Ratio/N(%)' ] )
    result['Inventor'       ] = [ elem[1] for elem in cn_list ]
    result['NumberOfPatents'] = [ elem[0] for elem in cn_list ]
    result['Ratio(%)'       ] = [ round( elem[0]/total*100, 2 ) for elem in cn_list ]
    result['Ratio/N(%)'     ] = [ round( elem[2]/total*100, 2 ) for elem in cn_list ]

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
menu = st.sidebar.radio( "MENU", ( 'Data Filter', 'Reference', 'Industry' ) )

# -------------------------------------------------------------------------------------------------
# Filter
# -------------------------------------------------------------------------------------------------

if menu == 'Data Filter':
  
    st.subheader( 'Data Filter' )
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
        st.caption( "(1) UNKNOWN = inventor search failed (2) Ratio/N(%) = normalized ratio per author w. equal contributions" )
    else:
        out_df = new_df

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
    # CPUs
    # ---------------------------------------------------------------------------------------------

    col2.write  ( '##### Supported CPUs and GPUs' )
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
    # Browers
    # ---------------------------------------------------------------------------------------------

    col2.write  ( '##### Supported Browsers' )
    col2.caption( 'Source: [wikipedia](https://en.wikipedia.org/wiki/High_Efficiency_Video_Coding#Implementations_and_products)' )

    text = '''
        - Android browser (since version 5)
        - Safari (since version 11)
    '''
    col2.markdown( text )

    # ---------------------------------------------------------------------------------------------
    # Adoption ratio for each mobile OS
    # ---------------------------------------------------------------------------------------------

    st.write  ( '##### Adoption ratio for each mobile OS' )
    st.caption( 'Source: [scientiamobile](https://www.scientiamobile.com/growing-support-of-hevc-or-h-265-video-on-mobile-devices/) (2018)' )

    land_url = 'https://www.scientiamobile.com/wp-content/uploads/2018/08/HEVC-Pie-Support-by-OS1200b.png'
    st.image( land_url, use_column_width='auto' )