from pathlib import Path
import os

import streamlit as st
from sqltops_sp import system_message, send_request_to_azure


sql_types = ["Functions translated from Stored Procedure", "Functions translated form Functions", "Views"]

#converted from Stored Procedures
POSTGRES_FUNCTION_A = 'postgres/functionsA'
REVIEWED_POSTGRES_FUNCTION_A = 'postgresR/functionsA'
SQLSERVER_SP = 'SQLServer/stored_procedures/'

#converted from Functions
POSTGRES_FUNCTION_B = 'postgres/functionsB'
REVIEWED_POSTGRES_FUNCTION_B = 'postgresR/functionsB'
SQLSERVER_FUNCTIONS = 'SQLServer/functions/'

#converted from Views
POSTGRES_VIEW = 'postgres/views'
REVIEWED_POSTGRES_VIEW = 'postgresR/views'
SQLSERVER_VIEWS = 'SQLServer/views/'

# Context
CONTEXT = 'context'

filepth = {
    "Functions translated from Stored Procedure"    : [POSTGRES_FUNCTION_A,REVIEWED_POSTGRES_FUNCTION_A],
    'Functions translated form Functions'           : [POSTGRES_FUNCTION_B,REVIEWED_POSTGRES_FUNCTION_B],
    'Views'                                         : [POSTGRES_VIEW, REVIEWED_POSTGRES_VIEW]
}

def list_files(file_type):
   files = os.listdir(Path(filepth[file_type][0]))
   sp = [x for x in files if x.endswith(".sql")]
   return sp

def read_postgreSQL(file_name, file_type):
    loc = Path(filepth[file_type][0])
    file = Path(loc,file_name)
    with open(file, 'rb') as sp_file:
            sp = sp_file.read()

    return sp.decode("UTF-8")

def read_sql_server_sp(sp_name):
    sp_name = "dbo."+ sp_name.split(".")[0] + ".StoredProcedure.sql"
    sp_base = SQLSERVER_SP
    file = Path(sp_base, sp_name)
    with open(file, 'rb') as sp_file:
        sp = sp_file.read()
    return sp.decode("UTF-16")

def save_updated_sp(sp_name, updated_sp):
    sp_name = sp_name 
    sp_base = REVIEWED_POSTGRES_FUNCTION_A
    file = Path(sp_base, sp_name)
    st.info(f"length of sql code {len(updated_sp)}")
    with open(file, 'w') as csp:
        csp.writelines(updated_sp)

def update_current_postgres(current_postgres_sql,update_msg):
    current_message = {
        "role":"assistant",
        "content":current_postgres_sql
    }
    update_message ={
        "role":"user",
        "content":update_msg
    }
    conv = [system_message]
    conv.append(current_message)
    conv.append(update_message)

    with st.spinner('Wait for it...'):
        return extract_content_from_response(send_request_to_azure(conv))
    
def extract_content_from_response(resp):
    return resp.json()['choices'][0]["message"]['content']
    
# def read
    

