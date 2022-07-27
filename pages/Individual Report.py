import streamlit as st
from functions import *
from streamlit_folium import folium_static 
import folium
from datetime import timedelta

st.set_page_config(page_title="Indv Report")
st.markdown("# Fake visits report")
st.write(
    """In this page you can see the amount of red and yellow flags that a rep have.
        - A rep get a yellow flag if the visit location doesnt match with the account location by a ratio of more than 820ft and less than 1640m
        - A rep get a red flag if the visit location doesnt match with the account location by a ratio of more than  1640m
""")

# Upload the data
data = uploading_data()

# We add a rep filter and add a empty option. The plots and information will only display if one name is selected
rep = st.sidebar.selectbox('Select one Rep',['']+list(data['name'].unique()))

if rep !='':

    # We filter the dataframe to get only the rep data and group by date to know the yellow and red flags of each day
    rep_data = data[data['name']==rep]
    st.dataframe(rep_data.groupby('offer_date').sum()[['Yellow flag','Red flag']].sort_index())

    # We include a date filter in the sidebar to see the information of the visits of that day (Table and Map)
    dates=st.sidebar.date_input("Visit range",[],min_value=rep_data['offer_date'].min(),max_value=rep_data['offer_date'].max())
    if len(dates)==2:

        # We iterate through all dates between dates selected
        firstDay = dates[0]
        lastDay = dates[1]
        delta = lastDay - firstDay
        for j in range(delta.days + 1):
            i = firstDay + timedelta(days=j)

            #For each day we create a expander to keep the information of the day
            with st.expander(f"{i}"):
                temp_data = rep_data[rep_data['offer_date']==i]
                if len(temp_data)!=0:

                    # We get the red and yellow flags of the day
                    st.write(f"**Red flags: {temp_data['Red flag'].sum()}**")
                    st.write(f"**Yellow flags: {temp_data['Yellow flag'].sum()}**")
                    st.write("### Map of visits vs locations")

                    #We create the app and iterate over the accounts visited that day
                    map1 = folium.Map(location=[temp_data['visit_lat'].values[0],temp_data['visit_lon'].values[0]], zoom_start=10,tiles='Stamen Toner')
                    for i in range(len(temp_data)):

                        # The account location dot is added in blue
                        prac_name=temp_data.iloc[i]['practice_name']
                        html = f"{prac_name}'s Location"
                        iframe = folium.IFrame(html)
                        popup = folium.Popup(iframe,min_width=180,max_width=190)
                        folium.Circle(location=[temp_data.iloc[i]['visit_lat'], temp_data.iloc[i]['visit_lon']],popup=popup,radius=10,fill=True,color='blue',fill_opacity=1).add_to(map1)

                        # The visit location is added in red
                        html1 = f"{prac_name}'s Visit"
                        iframe1 = folium.IFrame(html1)
                        popup1 = folium.Popup(iframe1,min_width=180,max_width=190)
                        folium.Circle(location=[temp_data.iloc[i]['acc_lat'], temp_data.iloc[i]['acc_lon']],popup=popup1,radius=10,fill=True,color='red',fill_opacity=1).add_to(map1)
                    folium_static(map1)


                    # We show the table with the basic info of the visits
                    st.write("### Visits data")           
                    st.write(temp_data[['practice_name','state','city','status','total_offer','distance_accvisit']].rename(columns={
                        'practice_name':'Practice Name',
                        'state':'State',
                        'city':'City',
                        'status':'Status',
                        'total_offer':'Total offer',
                        'distance_accvisit':'Distance from location'
                    }))
                else:
                    st.warning("There are no visits this day")