from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import streamlit as st
import geopy.distance

# The Big Query Credentials are in the path .streamlit/secrets.toml 
# First we save this credentials in the variable credentials and then we create the connection with bigquery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
BigQuery_client = bigquery.Client(credentials=credentials)

# The ofertas query acces the locations of the accounts and the location of the rep when the visit was registered.
ofertas="""
SELECT o.id,o.offer_date,o.account_id,a.practice_name,r.name,o.longitude as visit_lon,o.latitude as visit_lat,p.longitude as acc_lon,p.latitude as acc_lat,p.state,p.city,o.status,o.total_offer
FROM `star-big-data.star_us_rds.offers` o
LEFT JOIN `star-big-data.star_us_rds.accounts` a ON o.account_id=a.id
LEFT JOIN `star-big-data.star_us_rds.places` p ON a.place_id=p.id
LEFT JOIN `star-big-data.star_us_rds.reps` r ON o.rep_id = r.id
WHERE r.name <> 'General Pot' and status <> 'NoVisit' and account_id IS NOT NULL and (p.longitude IS NOT NULL and p.latitude IS NOT NULL) and (o.longitude IS NOT NULL and o.latitude IS NOT NULL) and r.inactive=False
ORDER BY offer_date desc
"""

def distancia(lat1,lon1,lat2,lon2):
    """This functions calculate the geodesic distance between two geographical points

    Args:
        lat1 (float): latitude of the first location
        lon1 (float): longitude of the first location
        lat2 (float): latitude of the second location
        lon2 (float): longitude of the second location

    Returns:
        float: Distance between the two points in meters
    """
    coords_1 = (lat1, lon1)
    coords_2 = (lat2, lon2)
    return geopy.distance.geodesic(coords_1, coords_2).km *1000

@st.cache
def uploading_data():
    """Function that uploads and transforms the data

    Returns:
        Dataframe: Dataframe with all the nedeed data
    """

    # First we run the query and save the info in a Dataframe
    # Then we calculate the distance between the account and visit location
    # We say that the visit is a yellow flag if the distance is more than 300m and less than 1000
    # We say that the visit is a red flag if the distance is more than 1000m

    ofertas_df = (BigQuery_client.query(ofertas).result().to_dataframe(create_bqstorage_client=True,))
    ofertas_df['distance_accvisit'] = ofertas_df[['visit_lat','visit_lon','acc_lat','acc_lon']].apply(lambda x: distancia(x[0],x[1],x[2],x[3]),axis=1)
    ofertas_df['Yellow flag'] =  ofertas_df['distance_accvisit'].apply(lambda x: 1 if (x>300 and x<1000)  else 0)
    ofertas_df['Red flag'] = ofertas_df['distance_accvisit'].apply(lambda x: 1 if x>1000 else 0)
    ofertas_df['offer_date'] = pd.to_datetime(ofertas_df['offer_date']).dt.date
    return ofertas_df
