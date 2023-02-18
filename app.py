import streamlit as st
import pandas as pd
import os
import random
import datetime
import json

from google.oauth2 import service_account
from gsheetsdb import connect
import gspread

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
def get_data(project_id):
    sheet = client.open(project_id).sheet1
    dataframe = pd.DataFrame(sheet.get_all_records())
    return dataframe

with open('projects_meta.json') as f:
    meta = json.load(f)

def labeler():

    st.markdown("# Text Labeler")
    st.markdown("--------")

    placeholder = st.empty()

    with placeholder.form(key="login"):
        user = st.text_input("Username")
        password = st.text_input("Password")
        st.form_submit_button("Login")
            
    if user == st.secrets["authentication"]['username'] and password == st.secrets["authentication"]['password']:
                
        with st.sidebar:

            st.sidebar.title('Projects')
            project_id = st.sidebar.radio('Select a project', meta['projects'])

            project_id_out = meta['output'][project_id]
            st.write(meta['metadata'][project_id])
            df = get_data(project_id)
            ids = df['ids'].to_list()

            if "annotations" not in st.session_state:
                st.session_state.annotations = {}
                st.session_state.ids = ids

            st.markdown("--------")
            if st.session_state.ids:
                st.session_state.current_id = st.selectbox(
                'Select a unique id?',
                st.session_state.ids)





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

                labels =  eval(df.loc[df['ids'] == st.session_state.current_id]['label_list'].values[0])
                cols = st.columns(len(labels))
                for i in labels:
                    cols[labels.index(i)].button(i, on_click=annotate, args=(i,))

            else:
            
                st.write("### Annotations")
                st.write(st.session_state.annotations)
                df = pd.DataFrame([st.session_state.annotations])
                dfnew = df.T
                dfnew.columns = ['labels']
                dfnew = dfnew.reset_index()
                dfnew['date'] = datetime.datetime.now().strftime('%Y-%m-%d')

                sheet2 = client.open(project_id_out).sheet1
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
        placeholder.empty()

    else:
        st.write("Incorrect username or password")

if __name__ == "__main__":
    labeler()
