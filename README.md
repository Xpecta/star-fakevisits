# SDR - Fake Visits Identification Algorithm

This app contains a fake visits identification algorithm that identify if the sales representative is going to the accounts that he/she is registering.

## Requirements

To install all the requirements that the app needs in order to run, run the following command on shell:

```console
pip install -r requirements.txt
```

## Run the app

To run the streamlit app in a local server, run the following command on shell:

```console
streamlit run Home.py
```

## Data

The data used in this app is from Star's BigQuery Database. The following tables are used:

- star-big-data.star_us_rds.offers
- star-big-data.star_us_rds.accounts
- star-big-data.star_us_rds.places
- star-big-data.star_us_rds.reps

**How to make a connection to the database?**

There are two ways to connect to the database in BigQuery. In both ways you need the key provided from SDR (the key name is key.json). The two ways are:

1. Using BigQuery Client.

To use this way, follow the instructions detalied in [google documentation](https://cloud.google.com/bigquery/docs/reference/libraries?hl=es_419)

2. Using Streamlit 

To use this way, follow the instructions detalied in [streamlit documentation](https://docs.streamlit.io/knowledge-base/tutorials/databases/bigquery)

## Algorithm procedure

The algorithm recognizes when a visit is registered in a location far from the account location. 

- If this distance is less than 0,3 and more than 0,15 miles, then the visit is a yellow flag.
- If this distance is more than 0,3 miles, then the visit is a red flag.