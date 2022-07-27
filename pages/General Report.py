import streamlit as st
from functions import *
import matplotlib.pyplot as plt


st.set_page_config(page_title="Gen Report")
st.markdown("# Fake visits report")
st.write(
    """In this page you can see the amount of red and yellow flags that a rep have.
        - A rep get a yellow flag if the visit location doesnt match with the account location by a ratio of more than 820ft and less than 1640m
        - A rep get a red flag if the visit location doesnt match with the account location by a ratio of more than  1640m
""")

# Upload the data 
data = uploading_data()


# Sidebar filters 
# If the user selects a range of dates, we filter the dataframe
dates=st.sidebar.date_input("Date Filter",[],min_value=data['offer_date'].min(),max_value=data['offer_date'].max())

if len(dates)==2:
    data = data[(data['offer_date'] >= dates[0]) & (data['offer_date'] <= dates[1])]

# We group by rep name to see the total numbers of yellow and red flags
graficas = data.groupby('name').sum()[['Yellow flag','Red flag']].sort_values('Red flag',ascending=False)
st.dataframe(graficas)

# We plot the red flags by rep
st.write("## Top red flags ")
fig, ax = plt.subplots()
plt.barh(graficas.sort_values('Red flag').index,graficas['Red flag'].sort_values())
st.pyplot(fig)

# We plot the yellow flags by rep
st.write("## Top yellow flags ")
fig, ax = plt.subplots()
plt.barh(graficas.sort_values('Yellow flag').index,graficas['Yellow flag'].sort_values())
st.pyplot(fig)