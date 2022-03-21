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
    tm_split_list = []
    for idx, elem in enumerate( tm_list ):
        val = elem.split('|')
        tm_split_list += val
    
    # get unique list of inventors
    tm_u_list = list( set( tm_split_list ) )

    # count & sort
    cn_list = []
    for elem in tm_u_list:
        count = tm_split_list.count( elem )
        cn_list.append( [ count, elem ] )
    cn_list.sort( reverse=True )

    # make dataframe
    total = len( tm_list )
    result = pd.DataFrame( columns=[ 'Inventor', 'NumberOfPatents', "Ratio(%)" ] )
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
st.sidebar.title( 'HEVC Advance Statistics' )
menu = st.sidebar.radio( "MENU", ( 'Filter', 'Reference' ) )

# -------------------------------------------------------------------------------------------------
# Filter
# -------------------------------------------------------------------------------------------------

if menu == 'Filter':
  
    st.subheader( 'Data Filtering' )

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
            gb.configure_column( num_col, header_name=num_col, valueFormatter='value.toFixed(2)', type='rightAligned' )
        if num_col == 'Patent Number New':
            cellRenderer = JsCode('''function(params) {return '<a href="https://patents.google.com/patent/' + 
                                     params.value + '" target="_blank">'+ params.value+'</a>'}''')
            gb.configure_column( num_col, header_name=num_col, cellRenderer=cellRenderer )

    gb.configure_pagination()
    go = gb.build()
    ret = AgGrid( out_df, gridOptions=go, theme='light', allow_unsafe_jscode=True )

# -------------------------------------------------------------------------------------------------
# Reference
# -------------------------------------------------------------------------------------------------

if menu == 'Reference':

    st.subheader( 'Reference resources' )

    st.write( "- AccessAdvance Home: [Link](https://accessadvance.com)" )
    st.write( "- HEVC Advance Patent Overview: [Link](https://accessadvance.com/licensing-programs/hevc-advance/)" )
    st.write( "- HEVC Advance Licensor List: [Link](https://accessadvance.com/hevc-advance-patent-pool-licensors/)" )
    st.write( "- HEVC Advance Licensee List: [Link](https://accessadvance.com/hevc-advance-patent-pool-licensees/)" )
    st.write( "- HEVC Advance Royalty Rate Structure: [Link](https://accessadvance.com/hevc-advance-patent-pool-detailed-royalty-rates/)" )
    st.write( "- HEVC Advance Patent List: [Link](https://accessadvance.com/hevc-advance-patent-list/)" )

    st.write( "#### HEVC WORLDWIDE ESSENTIAL PATENTS LANDSCAPE" )
    st.write( "\n" )

    land_url = 'https://accessadvance.com/wp-content/uploads/2022/01/2022Q1-HEVC-Patent-Diagram-01-31-22-1536x1152.jpg'
    st.image( land_url, use_column_width='auto' )