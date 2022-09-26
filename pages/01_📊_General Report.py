import streamlit as st
from functions import *
import matplotlib.pyplot as plt
import plotly.express as px
from PIL import Image
from streamlit.logger import get_logger

st.set_page_config(page_title="Gen Report",page_icon="🔮")

LOGGER = get_logger(__name__)
add_logo('Imagenes/starlogo.png')

st.markdown("# General report")
st.write(
    """In this page you can see the amount of red and yellow flags that a rep has.
- A rep gets a yellow flag if the visit location doesn't match with the account location by a ratio of more than 2296ft and less than 4900ft
- A rep gets a red flag if the visit location doesn't match with the account location by a ratio of more than 4900ft
""")

# Upload the data 
data = uploading_data()

# Sidebar filters 
# If the user selects a range of dates, we filter the dataframe
dates=st.sidebar.date_input("Date Filter",[],min_value=data['offer_date'].min(),max_value=data['offer_date'].max())

if len(dates)==2:
    data = data[(data['date'] >= dates[0]) & (data['date'] <= dates[1])]

# We group by rep name to see the total numbers of yellow and red flags
graficas = data.groupby('name').sum()[['Yellow flag','Red flag']].sort_values('Red flag',ascending=False)
st.dataframe(graficas)

# We plot the red flags by rep
st.write("## Top red flags ")

fig =px.bar(        
                graficas.sort_values('Red flag').reset_index(), #Data Frame
                x = "Red flag", #Columns from the data frame
                y = "name",
            )
fig.update_yaxes(automargin=True,dtick=1)
st.plotly_chart(fig)

# We plot the yellow flags by rep
st.write("## Top yellow flags ")
fig =px.bar(        
                graficas.sort_values('Yellow flag').reset_index(), #Data Frame
                x = "Yellow flag", #Columns from the data frame
                y = "name",
            )
fig.update_yaxes(automargin=True,dtick=1)
st.plotly_chart(fig)
