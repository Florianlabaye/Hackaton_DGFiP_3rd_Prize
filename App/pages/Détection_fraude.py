import streamlit as st
import requests
import tweepy as tp
from tweepy import OAuthHandler
import pandas as pd
from tweepy import OAuthHandler
# from tweepy.streaming import StreamListener
import json
import csv
import re
#from textblob import TextBlob
import string
# import preprocessor as p
import os
import time

#General settings
st.set_page_config(
    page_title="DFiP",
    page_icon="👋",  
)
st.sidebar.markdown("# Détection de fraude")

st.title("Trouver un chemin entre un broker centralisé et une adresse publique")
st.subheader("Rentrer une adresse publique :")


with st.form("my_form"):
    adresse = st.text_input("Adresse publique :")
    #distance = st.text_input("Distance à parcourir :")
    get_address = adresse
    submitted = st.form_submit_button("Valider")

st.write("0xf977814e90da44bfa03b6295a0616a897441acec")
if submitted:
    headers = {
        'X-API-Key': '8ea4fb692e655c4eb93f9f77511bc62b064e2ca593036787a853b28257e32d18',
        'Accept': 'application/json',
    }
    
    response = requests.get('https://public.chainalysis.com/api/v1/address/'+get_address, headers=headers)

    resultat = response.json()

    problem = len(resultat.get("identifications"))
    if problem == 0:
        st.write("Chain analysis ne détecte pas de risque sur cette adresse" )
    else:
        st.write("Chain analysis détecte un risque sur cette adresse")
    
    # initialisation 
    consumer_key = "neFjQUU9CfE9gFgBK2X4yro2j" # API/Consumer key 
    consumer_secret = "orhQzemgSx07sMV9lTK197j7ZTXrojnDwdGMQdDA1RUl2Gli5h" # API/Consumer Secret Key
    access_token = "1204779047252889609-0dCHKl8ZNqCLLmJCBuqP1rULpXYLLY"    # Access token key
    access_token_secret = "kiY8AIFf4MBOBQGxTbNf3DRCmYYklZT0e87m5SClYvnnX" # Access token Secret key

    # Authentification
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tp.API(auth)

    ## Addresse à changer !!!
    search_query =  get_address


    no_of_tweets = 10 # change to unlimited 

        #The number of tweets we want to retrieved from the search
    tweets = api.search_tweets(q=search_query, count=no_of_tweets)

        # On choisit nos données: https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/tweet
    attributes_container = [[tweet.id,tweet.geo,tweet.coordinates, tweet.place, tweet.user.name, tweet.created_at, tweet.favorite_count, tweet.source,  tweet.text, tweet.is_quote_status
                            , tweet.lang] for tweet in tweets]

        # On se def les colonnes du dataframe
    columns = ["ID","Geo","Coordinates","Place","User", "Date Created", "Number of Likes", "Source of Tweet", "Tweet", "Quoted", "Lang"]
        #On se créé un Df:  
    tweets_df = pd.DataFrame(attributes_container, columns=columns)
    tweets_df["Address"]= search_query

    st.write(tweets_df)