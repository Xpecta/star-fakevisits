import streamlit as st
from functions import *
import plotly.express as px


st.set_page_config(page_title="Visit info",page_icon="🔮")
add_logo('Imagenes/starlogo.png')
st.markdown("# Visits Analysis")
st.write("In this page you can see if a rep is visiting an account too much.")
st.write("¿ What number of visits is considered as 'too much'?")
st.write("According to the data, 90\% of accounts have been visited less than 5 times. So an account visited more than 5 times with no buy is 'too much'")

# Upload the data
data = uploading_data()


# We add a rep filter and add a empty option. The plots and information will only display if one name is selected
rep = st.sidebar.selectbox('Select one Rep',['']+sorted([str(x) for x in data['name'].unique()]))
if rep!='':
    data=data[data['name']==rep]

dates=st.sidebar.date_input("Date Filter",[],min_value=data['offer_date'].min(),max_value=data['offer_date'].max())

if len(dates)==2:
    data = data[(data['date'] >= dates[0]) & (data['date'] <= dates[1])]

data = data[data['cum_prevvisits']>5]
if len(data)!=0:
    st.write("## Accounts with more than 5 previous visits")

    data['div'] =data['cum_prevbuys']/data['cum_prevvisits']

    data_preview = data.loc[data['div']<0.5,['account_id','date','practice_name','name','status','total_offer','city','state','cum_prevvisits','cum_prevbuys']].rename(
        columns={
            'account_id':'Account Id',
            'date':'Date',
            'practice_name':'Practice Name',
            'name':'Rep name',
            'total_offer':'Total Offer',
            'cum_prevbuys':'Previous Buys',
            'cum_prevvisits':'Previous Visits'
        }
    ).sort_values('Previous Visits',ascending=False).reset_index(drop=True)
    st.write(data_preview)

    st.write("## Reps with more apperances")
    if len(data)!=0:
        fig = px.bar(        
                    data['name'].value_counts().reset_index().sort_values(by='name').rename(columns={'name':'Repeated times','index':'Name'}), #Data Frame
                    x = "Repeated times", #Columns from the data frame
                    y = "Name",
                )
        st.plotly_chart(fig)
else:
    st.warning("There are no accounts with more than 5 visits and no buy")