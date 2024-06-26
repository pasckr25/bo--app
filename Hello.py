import streamlit as st
import pandas as pd
import numpy as np

import gspread
from google.oauth2 import service_account

st.set_page_config(layout="wide")

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
    st.markdown("The rules:")
    st.markdown("You're boss assigned you to optimize the yield of the following reaction (see right side). Of course the project is under emense time pressure so he only gives you 2 weeks (10 work days) to explore and optimize the entire chemical space.\
            In total there are 1728 possible experiments to choose from, but you and your team are only able to complete 5 experiments per day... 5 $\cdot$ 10 = 50 experiments, thats only 3 % of all possible combinations.") 
    st.markdown("Choose your experiments wisely and try to achieve the greatest yield. Good Luck!")
    st.markdown("How this app works: After entering a user name you are able to select experiments (5 at a time) to be conducted \
                in the your virtual lab. Although this is an online app the experimental data is real, generated in a real  lab at Princeton University. Once you have selected 5 experiments the results will be displayed in an overview table down below. In addition there is \
                a graphical representation of your progress. After conducting all 50 experiments please submit your results to the database.")
    st.markdown("This app is based on work done by B.J. Shields et al. please check out their work.")
    st.link_button("Link to original paper","https://www.nature.com/articles/s41586-021-03213-y")
    abr=["KOAc","KOPiv","CsOAc","CsOPiv","BuOAc","p-Xylene","BuCN","DMAc"]
    engl=["Potassium acetate","Potassium pivalate","Ceasium acetate","Ceasium pivalate","Butyl acetate","Para-xylene","Pivalonitrile","Dimethylacetamide"]
    df_abr=pd.DataFrame({"Abbreviation":abr,"English":engl})
    st.dataframe(df_abr)
    user=st.text_input("Your user name:")
with c_rules_right:
    st.image("img.png")

c_exp=st.container()
c_exp_left, c_exp_right = c_rules.columns(2)



if st.session_state['result_counter']<50:
    with c_exp_left:

        base = st.selectbox('Select a base',['CsOAc', 'KOAc', 'CsOPiv', 'KOPiv'])  # 👈 this is a widget
        ligand = st.selectbox('Select a ligand',['GorlosPhos HBF4', 'CgMe-PPh', 'JackiePhos', 'PCy3 HBF4', 'BrettPhos', 'PPh2Me', 'PPh3', 'PPhMe2', 'X-Phos', 'P(fur)3', 'PPhtBu2', 'tBPh-CPhos'])  # 👈 this is a widget
        solvent = st.selectbox('Select a solvent',['BuOAc', 'p-Xylene', 'BuCN', 'DMAc'])  # 👈 this is a widget
        temperature = st.selectbox('Select a temperature',[120, 105, 90])  # 👈 this is a widget
        concentration = st.selectbox('Select a concentration',[0.057,0.1, 0.153])  # 👈 this is a widget

        if st.session_state["batch_counter"] <= 4:
            if st.button("add experiment",type="primary"):
                df_append=pd.DataFrame(data={"user":user,"base":base,"ligand":ligand,"solvent":solvent,"temperature":temperature,"concentration":concentration},index=[0])
                st.session_state['df_batch']=pd.concat([st.session_state['df_batch'],df_append],ignore_index=True)
                st.session_state["batch_counter"]=st.session_state["batch_counter"]+1
                st.rerun()
        else:
            if st.button("evaluate experiment",type="primary"):
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
    st.line_chart(df_results,y="yield")

if st.session_state['result_counter']>49:
    if st.button("Submit your results"):
        # Create a connection object.
        credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"],scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"],)
        
        client=gspread.authorize(credentials)

        sheet_id = '1noIa_2NECsdUPp087oSCDqcj1PP6IzDlbTx1RdSuaHg'
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        database_df = pd.read_csv(csv_url, on_bad_lines='skip')


        database_df=pd.concat([database_df,df_results],ignore_index=True)

        database_df = database_df.astype(str)
        sheet_url = st.secrets["private_gsheets_url"] #this information should be included in streamlit secret
        sheet = client.open_by_url(sheet_url).sheet1
        sheet.update([database_df.columns.values.tolist()] + database_df.values.tolist())
        st.success('Your data has been saved! Thanks for playing')