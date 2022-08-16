from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import streamlit as st
from haversine import haversine, Unit
import ast
import base64

# The Big Query Credentials are in the path .streamlit/secrets.toml 
# First we save this credentials in the variable credentials and then we create the connection with bigquery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
BigQuery_client = bigquery.Client(credentials=credentials)

cuentas_q="""
SELECT a.id,a.practice_name,p.longitude as acc_lon,p.latitude as acc_lat,p.state,p.city, p.country
FROM `star-big-data.star_us_rds.accounts` a
LEFT JOIN `star-big-data.star_us_rds.places` p ON a.place_id=p.id
"""
# The ofertas query acces the locations of the accounts and the location of the rep when the visit was registered.
ofertas_q="""
SELECT o.id,CAST(o.offer_date as DATE) as date,CAST(o.offer_date as time) as time,o.offer_date,o.account_id,a.practice_name,r.name,o.longitude as visit_lon,o.latitude as visit_lat,p.longitude as acc_lon,p.latitude as acc_lat,p.state,p.city,o.status,o.total_offer
FROM `star-big-data.star_us_rds.offers` o
LEFT JOIN `star-big-data.star_us_rds.accounts` a ON o.account_id=a.id
LEFT JOIN `star-big-data.star_us_rds.places` p ON a.place_id=p.id
LEFT JOIN `star-big-data.star_us_rds.reps` r ON o.rep_id = r.id
WHERE r.name <> 'General Pot' and status <> 'NoVisit' and account_id IS NOT NULL and (p.longitude IS NOT NULL and p.latitude IS NOT NULL) and (o.longitude IS NOT NULL and o.latitude IS NOT NULL) and r.inactive=False
ORDER BY offer_date desc
"""
# The tracks query acces the gps info of all reps travels
tracks="""
    SELECT date,name, STRING_AGG(coordinates) as coords
    FROM(
        SELECT CAST(timestamp as DATE) as date, r.name, CONCAT("(",latitude,",",longitude,")") as coordinates
        FROM `star-big-data.star_us_rds.Track` t
        LEFT JOIN `star-big-data.star_us_rds.reps` r ON t.rep_id = r.id 
    )
    GROUP BY date,name
"""

def distance_rows(start, points):
    """Function that calculates the minimum distance between a point and a set of points 

    Args:
        start (tuple): (lat,lon) tuple of first coordinate
        points (list): list of lat lon coordinates

    Returns:
        float: minimum distance in feet
    """
    return min([haversine(start,stop,unit=Unit.FEET) for stop in points])

@st.experimental_memo
def uploading_data():
    """Function that uploads and transforms the data

    Returns:
        Dataframe: Dataframe with all the nedeed data
    """


    # First we load the route that reps followed each day and trasnform the set of coordinates into a list
    coordinates=(BigQuery_client.query(tracks).result().to_dataframe(create_bqstorage_client=True,))
    coordinates = coordinates.dropna()
    coordinates['coords']=coordinates['coords'].apply(lambda x: list(ast.literal_eval(x)))

    # Then we run the ofertas query and save the info in a Dataframe, create the acc_coords variable with lat lon of the account and the same with the visit location
    ofertas = (BigQuery_client.query(ofertas_q).result().to_dataframe(create_bqstorage_client=True,))
    ofertas =ofertas.loc[:,~ofertas.columns.str.startswith('_')]
    ofertas['acc_coords']=ofertas[['acc_lat','acc_lon']].apply(lambda x: (x[0],x[1]),axis=1)
    ofertas['visit_coords']=ofertas[['visit_lat','visit_lon']].apply(lambda x: (x[0],x[1]),axis=1)

    # We join offers dataframe with the track information to have the route followed for the rep the day that he visited the account. This distance is in acc_route_dist
    consolidado=ofertas.merge(coordinates,how='left',on=['date','name']).dropna()
    consolidado['acc_route_dist']=(consolidado[['acc_coords','coords']].apply(lambda x : distance_rows(x[0],x[1]),axis=1))


    consolidado['Yellow flag'] =  consolidado['acc_route_dist'].apply(lambda x: 1 if (x>2296 and x<4900)  else 0)
    consolidado['Red flag'] = consolidado['acc_route_dist'].apply(lambda x: 1 if x>5000 else 0)
    consolidado['date'] = pd.to_datetime(consolidado['date']).dt.date

    consolidado['buy']=(consolidado['status']=='Accepted').astype(int)
    consolidado['visit']=1

    consolidado['cum_prevbuys'] = consolidado.groupby(['account_id'])['buy'].apply(lambda x: x.shift().cumsum())
    consolidado['cum_prevvisits'] = consolidado.groupby(['account_id'])['visit'].apply(lambda x: x.shift().cumsum())

    consolidado['cum_prevvisits'] = consolidado['cum_prevvisits'].fillna(0)
    consolidado['cum_prevbuys'] = consolidado['cum_prevbuys'].fillna(0)
    return consolidado

@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def build_markup_for_logo(
    png_file,
    background_position="50% 10%",
    margin_top="10%",
    image_width="60%",
    image_height="",
):
    binary_string = get_base64_of_bin_file(png_file)
    return """
            <style>
                [data-testid="stSidebarNav"] {
                    background-image: url("data:image/png;base64,%s");
                    background-repeat: no-repeat;
                    background-position: %s;
                    margin-top: %s;
                    background-size: %s %s;
                }
                [data-testid="stSidebarNav"]::before {
                content: "Fake Visits Report";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 35px;
                position: relative;
                top: 100px;
            }
            </style>
            """ % (
        binary_string,
        background_position,
        margin_top,
        image_width,
        image_height,
    )


def add_logo(png_file):
    logo_markup = build_markup_for_logo(png_file)
    st.markdown(
        logo_markup,
        unsafe_allow_html=True,
    )

def color_tabla(df):
    x = int(df['Distance'].split(' ')[0])
    return ['background-color: orange; color: white']*len(df) if (x>2296 and x<4900) else (['background-color: red; color: white']*len(df) if x>4900 else ['background-color: white']*len(df))