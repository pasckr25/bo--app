import streamlit as st
import pandas as pd
import numpy as np

import gspread
from google.oauth2 import service_account

if 'df_batch' not in st.session_state:
    st.session_state['df_batch'] = pd.DataFrame(columns=["user","base","ligand","solvent","temperature","concentration"])

if 'df_my_batches' not in st.session_state:
    st.session_state['df_my_batches'] = pd.DataFrame(columns=["user","base","ligand","solvent","temperature","concentration"])

if 'batch_counter' not in st.session_state:
    st.session_state['batch_counter']=0

if 'result_counter' not in st.session_state:
    st.session_state['result_counter']=0

c_rules=st.container()
c_rules_left, c_rules_right = c_rules.columns(2)


with c_rules_left:
    st.title("Reaction Optimizer")
    st.text("The rules:")
    st.text("You are assigned to optimize the following reaction")
    user=st.text_input("Your user name:")
with c_rules_right:
    st.image("img.png")

c_exp=st.container()
c_exp_left, c_exp_right = c_rules.columns(2)



if st.session_state['result_counter']<10:
    with c_exp_left:

        base = st.selectbox('Select a base',['CsOAc', 'KOAc', 'CsOPiv', 'KOPiv'])  # 👈 this is a widget
        ligand = st.selectbox('Select a ligand',['GorlosPhos HBF4', 'CgMe-PPh', 'JackiePhos', 'PCy3 HBF4', 'BrettPhos', 'PPh2Me', 'PPh3', 'PPhMe2', 'X-Phos', 'P(fur)3', 'PPhtBu2', 'tBPh-CPhos'])  # 👈 this is a widget
        solvent = st.selectbox('Select a solvent',['BuOAc', 'p-Xylene', 'BuCN', 'DMAc'])  # 👈 this is a widget
        temperature = st.selectbox('Select a temperature',[120, 105, 90])  # 👈 this is a widget
        concentration = st.selectbox('Select a concentration',[0.057,0.1, 0.153])  # 👈 this is a widget

        if st.session_state["batch_counter"] <= 4:
            if st.button("add experiment"):
                df_append=pd.DataFrame(data={"user":user,"base":base,"ligand":ligand,"solvent":solvent,"temperature":temperature,"concentration":concentration},index=[0])
                st.session_state['df_batch']=pd.concat([st.session_state['df_batch'],df_append],ignore_index=True)
                st.session_state["batch_counter"]=st.session_state["batch_counter"]+1
                st.rerun()
        else:
            if st.button("evaluate experiment"):
                st.session_state['df_my_batches'] = pd.concat([st.session_state['df_my_batches'],st.session_state['df_batch']], ignore_index=True)
                st.session_state["batch_counter"]=0
                del st.session_state['df_batch']
                st.session_state['result_counter']=st.session_state['result_counter']+5
                st.rerun()
                #del st.session_state['df_batch']

        with c_exp_right:
            st.write("Your current batch:")
            st.dataframe(st.session_state['df_batch'].drop(columns=["user"]))
        #    df_result=pd.read_csv("reaction_data.csv",header=0)
         #   st.dataframe(df_result.head())
else:
    st.write("Congrats! Thanks ", user," for playing, go ahead and check your results.")




c_plot=st.container()
c_plot_left, c_plot_right = c_rules.columns(2)
with c_plot_left:
    st.write("Your results so far")
    df_yield=pd.read_csv("reaction_data.csv",header=0)
    df_results=st.session_state["df_my_batches"].merge(df_yield,on=["base","ligand","solvent","temperature","concentration"],how="left")

    st.dataframe(df_results.sort_index(ascending=False))

with c_plot_right:
    st.line_chart(df_results["yield"])

if st.session_state['result_counter']>9:
    if st.button("Submit your results"):
        # Create a connection object.
        credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"],scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"],)
        
        client=gspread.authorize(credentials)

        sheet_id = '1noIa_2NECsdUPp087oSCDqcj1PP6IzDlbTx1RdSuaHg'
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
   #     database_df = pd.read_csv(csv_url, on_bad_lines='skip')


   #     database_df=pd.concat([database_df,df_results],ignore_index=True)

   #     database_df = database_df.astype(str)
   #     sheet_url = st.secrets["private_gsheets_url"] #this information should be included in streamlit secret
   #     sheet = client.open_by_url(sheet_url).sheet1
   #     sheet.update([database_df.columns.values.tolist()] + database_df.values.tolist())
   #     st.success('Data has been written to Google Sheets')