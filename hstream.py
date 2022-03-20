#
# HEVC Advance Statistics
#

# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------

import streamlit as st
import pandas    as pd
import json

# -------------------------------------------------------------------------------------------------
# Globals
# -------------------------------------------------------------------------------------------------

PATENT_CSV      = 'patent.csv'
PATENT_JSON     = 'patent.json'
PATENT_EXT_JSON = 'patent_ext.json'

# -------------------------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------
# Functions (Callbacks)
# -------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------
# Load data
# -------------------------------------------------------------------------------------------------

df = pd.read_csv( PATENT_CSV )
df.drop( 'Count (Patents)', axis=1, inplace=True )
df.drop( 'Est. Exp. Date', axis=1, inplace=True )

# pre-processing
cnt = list( df[ 'Country' ] )
pno = list( df[ 'Patent Number' ] ) 

for idx, key in enumerate( pno ):
    pos = key.find( '-EP' )
    if pos > 0:
        cnt[ idx ] = 'EP'
        pno[ idx ] = key[pos+1:]

df[ 'Country'       ] = cnt
df[ 'Patent Number' ] = pno

with open( PATENT_JSON, 'r' ) as fp:
    pt = json.load( fp )

with open( PATENT_EXT_JSON, 'r' ) as fp:
    pt_ext = json.load( fp )

pt.update( pt_ext )

# -------------------------------------------------------------------------------------------------
# Layout
# -------------------------------------------------------------------------------------------------

# add sidebar
st.sidebar.title( 'HEVC Advance Statistics' )
menu = st.sidebar.radio( "MENU", ( 'Licensor', 'Inventor' ) )

# -------------------------------------------------------------------------------------------------
# Licensor
# -------------------------------------------------------------------------------------------------

if menu == 'Licensor':
    
    st.subheader( 'Licensor Statistics' )

    # Profile selector
    values  = [ 'Main/Main10', 'Multiview', 'Optional', 'Range Extension', 'Scalability', 'All' ]
    profile = st.selectbox( 'Profile', values )

    if profile == 'All': 
        new_df = df
    else:
        new_df = df[ df['Profile'] == profile ]
    
    # Country selector
    values  = [ 'All', 'US', 'EP', 'CN' ]
    country = st.selectbox( 'Country', values )

    if country == 'All': 
        pass
    else:
        new_df = new_df[ new_df['Country'] == country ]

    # get unique licensor list
    li_list   = list( new_df[ "Licensor" ] )
    li_u_list = list( set( li_list ) )
    total     = len( li_list )

    # count
    count_list = []
    ratio_list = []
    for elem in li_u_list:
        count = li_list.count( elem )
        count_list.append( count )
        ratio_list.append( round( count / total * 100, 2 ) )
    
    # make dataframe
    df_li = pd.DataFrame( columns=[ 'Licensor', 'NumberOfPatents', "Ratio(%)" ] )
    df_li[ 'Licensor'        ] = li_u_list
    df_li[ 'NumberOfPatents' ] = count_list
    df_li[ 'Ratio(%)'        ] = ratio_list
    df_li.set_index( 'Licensor', inplace=True )    
    df_li.sort_values( by='NumberOfPatents', axis=0, ascending=False, inplace=True )

    # write text
    st.write( f'Total number: patents ({total}) unique licensors ({len(li_u_list)})' )

    # write dataframe
    dfs = df_li.style.format( {'Ratio(%)': lambda val: f'{val:.2f}'})
    st.table( dfs )

# -------------------------------------------------------------------------------------------------
# Inventor
# -------------------------------------------------------------------------------------------------

if menu == 'Inventor':
  
    st.subheader( 'Inventor Statistics' )

    # Profile selector
    values  = [ 'Main/Main10', 'Multiview', 'Optional', 'Range Extension', 'Scalability', 'All' ]
    profile = st.selectbox( 'Profile', values )

    if profile == 'All': 
        new_df = df
    else:
        new_df = df[ df['Profile'] == profile ]
    
    # Country selector
    values  = [ 'US', 'EP', 'CN' ]
    country = st.selectbox( 'Country', values )
    new_df  = new_df[ new_df['Country'] == country ]

    # get unique inventor list
    pn_list   = list( new_df[ "Patent Number" ] )
    total     = len( pn_list )

    # for each patent number
    li_list = []
    for elem in pn_list:
        if elem in pt:
            tmp = json.loads( pt[elem]['inventor_name'] )
            for val in tmp:
                li_list.append( val[ 'inventor_name' ] )
    
    li_u_list = list( set( li_list ) )

    # count
    count_list = []
    ratio_list = []
    for elem in li_u_list:
        count = li_list.count( elem )
        count_list.append( count )
        ratio_list.append( round( count / total * 100, 2 ) )
    
    # make dataframe
    df_li = pd.DataFrame( columns=[ 'Inventor', 'NumberOfPatents', "Ratio(%)" ] )
    df_li[ 'Inventor'        ] = li_u_list
    df_li[ 'NumberOfPatents' ] = count_list
    df_li[ 'Ratio(%)'        ] = ratio_list
    df_li.set_index( 'Inventor', inplace=True )    
    df_li.sort_values( by='NumberOfPatents', axis=0, ascending=False, inplace=True )

    # write text
    st.write( f'Total number: patents ({total}) unique inventors ({len(li_u_list)})' )

    # write dataframe
    dfs = df_li.style.format( {'Ratio(%)': lambda val: f'{val:.2f}'})
    st.table( dfs )