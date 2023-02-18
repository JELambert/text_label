import streamlit as st
import pandas as pd
import numpy as np

import os
import random
from google.oauth2 import service_account
from gsheetsdb import connect
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(layout="wide")


credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ],
)

client = gspread.authorize(credentials)
@st.cache_data()
def get_data():
    sheet = client.open("train_data").sheet1
    dataframe = pd.DataFrame(sheet.get_all_records())
    return dataframe



# Connect to Google Sheets
scope = ['https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive"]

#credentials = ServiceAccountCredentials.from_json_keyfile_name("streamlitapi-a75ce5cb14b8.json", scope)


# Print results.

def labeler():
    df = get_data()
    ids = df['ids'].to_list()

    if "annotations" not in st.session_state:
            st.session_state.annotations = {}
            st.session_state.ids = ids
            
    with st.sidebar:
            st.sidebar.title('Projects')
            if st.session_state.ids:
                st.session_state.current_id = st.selectbox(
                'Select a unique id?',
                st.session_state.ids)


    st.markdown("# Text Labeler")
    st.markdown("--------")



    left_column, _, right_column = st.columns([50, 2, 20])
    with left_column:
        


        def annotate(label):
            st.session_state.annotations[st.session_state.current_id] = label
            if st.session_state.ids:
                #st.session_state.current_id = random.choice(st.session_state.ids)
                st.session_state.ids.remove(st.session_state.current_id)
        st.markdown("Text to label:")
        st.markdown("#### " + df.loc[df['ids'] == st.session_state.current_id]['text'].values[0])
        st.markdown("---------")
        st.markdown(" ")
        st.markdown("labels:")
        if st.session_state.ids:
            a, b = st.columns(2)
            with a:
                st.button("This is a dog! 🐶", on_click=annotate, args=("dog",))
            with b:
                st.button("This is a cat! 🐱", on_click=annotate, args=("cat",))

        else:
           
            st.write("### Annotations")
            st.write(st.session_state.annotations)
            df = pd.DataFrame([st.session_state.annotations])
            dfnew = df.T
            dfnew.columns = ['labels']
            dfnew = dfnew.reset_index()
            sheet2 = client.open("output_data").sheet1
            sheet2.update([dfnew.columns.values.tolist()] + dfnew.values.tolist())

    with right_column:

        if st.session_state.ids:
            st.write(
                "Annotated:",
                len(st.session_state.annotations),
                "– Remaining:",
                len(st.session_state.ids),
            )

        else:
            st.success(
                f"🎈 Done! All {len(st.session_state.annotations)} text annotated."
            )

if __name__ == "__main__":
    labeler()
