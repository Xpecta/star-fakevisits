import streamlit as st
from functions import *
from streamlit_folium import folium_static 
import folium
from datetime import timedelta
import plotly.graph_objects as go
import plotly.express as px


st.set_page_config(page_title="Indv Report",page_icon="🔮")

add_logo('Imagenes/starlogo.png')
st.markdown("# Individual report")
st.write(
    """In this page you can see the amount of red and yellow flags that a rep has.
- A rep gets a yellow flag if the visit location doesn't match with the account location by a ratio of more than 2296ft and less than 4900ft
- A rep gets a red flag if the visit location doesn't match with the account location by a ratio of more than 4900ft
""")

# Upload the data
data = uploading_data()

# We add a rep filter and add a empty option. The plots and information will only display if one name is selected
rep = st.sidebar.selectbox('Select one Rep',['']+sorted([str(x) for x in data['name'].unique()]))

if rep !='':

    # We filter the dataframe to get only the rep data and group by date to know the yellow and red flags of each day
    rep_data = data[data['name']==rep]
    
    


    # We include a date filter in the sidebar to see the information of the visits of that day (Table and Map)
    dates=st.sidebar.date_input("Visit range",[],min_value=rep_data['offer_date'].min(),max_value=rep_data['offer_date'].max())
    if len(dates)==2:

        rep_data = rep_data[(rep_data['date'] >= dates[0]) & (rep_data['date'] <= dates[1])]
        dates_info = rep_data.groupby('offer_date').sum()[['Yellow flag','Red flag']].sort_index().reset_index()

        fig = px.line(        
            dates_info, #Data Frame
            x = "offer_date", #Columns from the data frame
            y = "Red flag",
            title = "Red flags"
        )
        fig.update_traces(line_color = "red")
        st.plotly_chart(fig)

        fig = px.line(        
        dates_info, #Data Frame
        x = "offer_date", #Columns from the data frame
        y = "Yellow flag",
        title = "Yellow flags"
        )
        fig.update_traces(line_color = "blue")
        st.plotly_chart(fig)

        
        # We iterate through all dates between dates selected
        firstDay = dates[0]
        lastDay = dates[1]
        delta = lastDay - firstDay
        for j in range(delta.days + 1):
            i = firstDay + timedelta(days=j)

            #For each day we create a expander to keep the information of the day
            with st.expander(f"{i}"):
                temp_data = rep_data[rep_data['date']==i].reset_index(drop=True)
                if len(temp_data)!=0:

                    # We get the red and yellow flags of the day
                    st.write(f"**Red flags: {temp_data['Red flag'].sum()}**")
                    st.write(f"**Yellow flags: {temp_data['Yellow flag'].sum()}**")
                    st.write("### Map of visits vs locations")

                    #We create the app and iterate over the accounts visited that day
                    latlon = list(temp_data['coords'][0])
                    mapit = folium.Map( location=latlon[0], zoom_start=6 ,tiles='Stamen Toner')

                    for coord in latlon:
                        folium.Marker( location=[ coord[0], coord[1] ], icon = folium.Icon(color='blue',icon='car',prefix='fa') ).add_to( mapit )
                    
                    for i in range(len(temp_data)):

                        # The account location dot is added in blue
                        prac_name=temp_data.iloc[i]['practice_name']
                        html = f"({temp_data.iloc[i]['time']}) {prac_name}'s Location "
                        iframe = folium.IFrame(html)
                        popup = folium.Popup(iframe,min_width=180,max_width=190)

                        red_flag = temp_data.iloc[i]['Red flag']
                        yellow_flag = temp_data.iloc[i]['Yellow flag']
                        if red_flag ==1:
                            color='red'
                        elif yellow_flag==1:
                            color='orange'
                        else:
                            color='green'
                        folium.Marker(location=[temp_data.iloc[i]['acc_lat'], temp_data.iloc[i]['acc_lon']],popup=popup,icon = folium.Icon(color=color,icon='building',prefix='fa')).add_to(mapit)

                    mapit.fit_bounds(mapit.get_bounds())
                    folium_static(mapit)


                    # We show the table with the basic info of the visits
                    st.write("### Visits data")        
                    temp_data =temp_data[['time','practice_name','state','city','status','total_offer','acc_route_dist']].rename(columns={
                        'practice_name':'Practice Name',
                        'state':'State',
                        'city':'City',
                        'status':'Status',
                        'total_offer':'Offer',
                        'acc_route_dist':'Distance',
                        'time':'Time'
                    }).sort_values('Time')
                    temp_data['Offer']=temp_data['Offer'].astype(int).astype(str)+' USD'
                    temp_data['Distance']=temp_data['Distance'].astype(int).astype(str)+' ft     '
                    st.dataframe(temp_data.style.apply(color_tabla,axis=1))
                else:
                    st.warning("There are no visits this day")
    else:
        dates_info = rep_data.groupby('offer_date').sum()[['Yellow flag','Red flag']].sort_index().reset_index()

        fig = px.line(        
            dates_info, #Data Frame
            x = "offer_date", #Columns from the data frame
            y = "Red flag",
            title = "Red flags"
        )
        fig.update_traces(line_color = "red")
        st.plotly_chart(fig)

        fig = px.line(        
        dates_info, #Data Frame
        x = "offer_date", #Columns from the data frame
        y = "Yellow flag",
        title = "Yellow flags"
        )
        fig.update_traces(line_color = "blue")
        st.plotly_chart(fig)

        