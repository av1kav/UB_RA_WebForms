
import streamlit as st
import pandas as pd
import yaml
import pandas as pd
import numpy as np
import os
from pprint import pprint
import requests
from bs4 import BeautifulSoup as soup
from urllib.parse import urljoin

def generate_config_file_from_raw_data(raw_data):
    config_file_path = "wny_config.xlsx" # This needs to be dynamic
    # OpenAI-based config file generator: raw data -> config file
    prompt = """
    You are a helpful data analyst creating configuration files for large excel-based datasets. A configuration file is another excel file that
    has a header row with the following columns: 'backend_field_name', 'field_label', 'required?', 'field_type', 'select_options'. Then, a new row 
    is generated for for each column in the dataset. The columns in the configuration file are populated as follows:
    1. 'backend_field_name' should be derived from the column name in the dataset, but values should be lowercase and underscore-separated 
    2. 'field_label' should be derived from the column name in the dataset, but values should be HTML-safe and easy to read. They should not be underscore-separated.
    3. 'required' should be marked True only if the dataset contains values for all rows of that column. 
    4. 'field_type' should be an HTML element type such as input, text. select etc. If a column in the dataset only contains a few unique values and looks like it would be a dropdown
    element on a web form, ensure the field_type is 'select'.
    5. 'select_options' should be filled in only when the 'field_type' is 'select'. All unique values for the column in the dataset should be populated here in this case.
    """
    # TODO: integrate with OpenAI 
    # Temporary workaround - manual config file
    response = requests.get("https://github.com/av1kav/UB_RA_WebForms/raw/refs/heads/main/wny_config.xlsx")
    if response.status_code != requests.codes.ok:
        raise ValueError('Could not load file from Github repo.')
    return config_file_path
    
def POST_config_file_to_remote(config_file_path):

    api_token = "36659696571bc93c68080be5042209b10663018b"
    username = "avenugopal"
    pythonanywhere_host = "www.pythonanywhere.com"
    api_base = "https://{pythonanywhere_host}/api/v0/user/{username}/".format(
        pythonanywhere_host=pythonanywhere_host,
        username=username,
    )
    
    with st.spinner(text="Updating dynamic web form on remote..."):
        response = requests.post(
            urljoin(api_base, "files/path/home/{username}/wny_config.xlsx".format(username=username)),
            files={"content": config_file_path.read() },
            headers={"Authorization": "Token {api_token}".format(api_token=api_token)}
        )
        st.success("Form configuration updated.")
    
########### Streamlit App ###########

st.title("UB RA Dynamic Form Generator")
st.text("Welcome to the UB RA Web Form Management Tool.")

choice = st.radio(
    "Would you like to use an existing configuration file or create a new one from a dataset?",
    ("Use existing config", "Create new config from dataset"),
    index=1
)

# Choose between using existing config and making a new one from a dataset
st.session_state['config_file_path'] = None
if choice == "Use existing config":
    st.markdown("### Upload Existing Configuration File")
    uploaded_file = st.file_uploader("Upload your config file here.", type=["xlsx"])
    st.session_state['config_file_path'] = uploaded_file
elif choice == "Create new config from dataset":
    st.markdown("### Upload Dataset")
    uploaded_file = st.file_uploader("Upload your dataset here (MS Excel format only).", type=["xlsx"])
    if uploaded_file:
        st.success("File uploaded successfully!") 
        st.session_state['dataset_uploaded'] = True
    # Button to generate configuration file
    if st.session_state['dataset_uploaded']:
        if st.button("Generate Configuration File"):
            st.session_state['config_file_path'] = generate_config_file_from_raw_data(uploaded_file)
            config_file_path = st.session_state['config_file_path']
            st.success(f"Configuration file generated: {config_file_path}")
            st.download_button("Download Configuration File", 
               data=open(config_file_path, "rb").read(), 
               file_name="form_configuration.xlsx")

# Once a config is created/uploaded, sync it to the web server
if st.session_state['config_file_path']:
    st.text("Use the button below to sync the selected configuration file to the server.")
    config_file_path = st.session_state['config_file_path']
    if st.button("Sync changes with web form"):
            POST_config_file_to_remote(config_file_path)
