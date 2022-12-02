import pandas as pd
import streamlit as st

def read_data(path):
    return pd.read_csv(path)

def body():
    st.write(sample)

def head():        
    st.write(1234)

