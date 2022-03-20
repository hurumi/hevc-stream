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
    if pos >= 0:
        cnt[ idx ] = 'EP'
        pno[ idx ] = key[pos+1:]
    pos = key.find( 'KR10-' )
    if pos >= 0:
        pno[ idx ] = key.replace( '-','' )

df[ 'Country New'       ] = cnt
df[ 'Patent Number New' ] = pno

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
menu = st.sidebar.radio( "MENU", ( 'Licensor', 'Inventor', 'Reference' ) )

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
        new_df = new_df[ new_df['Country New'] == country ]

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

    # download button
    csv = new_df.to_csv().encode( 'utf-8' )
    st.download_button(
        label     = "Download filtered data as CSV",
        data      = csv,
        file_name = f'{profile}-{country}.csv',
        mime      = 'text/csv',
    )

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
    values  = [ 'All', 'US', 'EP', 'CN' ]
    country = st.selectbox( 'Country', values )
    if country != 'All': new_df  = new_df[ new_df['Country New'] == country ]

    # get unique licensor list
    tm_list   = list( new_df[ "Licensor" ] )
    tm_u_list = list( set( tm_list ) )

    # count
    cn_list = []
    for elem in tm_u_list:
        count = tm_list.count( elem )
        cn_list.append( [ count, elem ] )
    cn_list.sort( reverse=True )
    values = [ 'All' ] + [ elem[1] for elem in cn_list ]
    licensor = st.selectbox( 'Licensor', values )
    if licensor != 'All': new_df = new_df[ new_df['Licensor'] == licensor ]  

    # get unique inventor list
    pn_list   = list( new_df[ 'Patent Number New' ] )
    total     = len( pn_list )

    li_list = []
    iv_list = []
    for elem in pn_list:
        try:
            tmp1 = json.loads( pt[elem]['inventor_name'] )
            tmp2 = [ val[ 'inventor_name' ] for val in tmp1 ]
            li_list = li_list + tmp2
            iv_list.append( '|'.join( tmp2 ) )
        except:
            iv_list.append( 'N/A' )
    li_u_list = list( set( li_list ) )

    # insert inventor column
    new_df[ 'Inventor' ] = iv_list

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

    # download button
    csv = new_df.to_csv().encode( 'utf-8' )
    st.download_button(
        label     = f"Download filtered data as CSV (with inventor names)",
        data      = csv,
        file_name = f'{profile}-{country}-{licensor}.csv',
        mime      = 'text/csv',
    )

    # write dataframe
    dfs = df_li.style.format( {'Ratio(%)': lambda val: f'{val:.2f}'})
    st.table( dfs )

# -------------------------------------------------------------------------------------------------
# Reference
# -------------------------------------------------------------------------------------------------

if menu == 'Reference':

    st.subheader( 'Reference resources' )

    st.write( "- AccessAdvance Home: [Link](https://accessadvance.com)" )
    st.write( "- HEVC Advance Patent Overview: [Link](https://accessadvance.com/licensing-programs/hevc-advance/)" )
    st.write( "- HEVC Advance Licensor List: [Link](https://accessadvance.com/hevc-advance-patent-pool-licensors/)" )
    st.write( "- HEVC Advance Licensee List: [Link](https://accessadvance.com/hevc-advance-patent-pool-licensees/)" )
    st.write( "- HEVC Advance Patent List: [Link](https://accessadvance.com/hevc-advance-patent-list/)" )

    st.write( "#### HEVC WORLDWIDE ESSENTIAL PATENTS LANDSCAPE" )
    st.write( "\n" )

    land_url = 'https://accessadvance.com/wp-content/uploads/2022/01/2022Q1-HEVC-Patent-Diagram-01-31-22-1536x1152.jpg'
    st.image( land_url, use_column_width='auto' )