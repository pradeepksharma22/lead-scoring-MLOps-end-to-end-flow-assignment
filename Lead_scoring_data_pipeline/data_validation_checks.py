"""
Import necessary modules
############################################################################## 
"""
from constants import *
from utils import *
from schema import *

import pandas as pd

###############################################################################
# Define function to validate raw data's schema
# ############################################################################## 

def raw_data_schema_check():
    '''
    This function check if all the columns mentioned in schema.py are present in
    leadscoring.csv file or not.

   
    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be   
        raw_data_schema : schema of raw data in the form oa list/tuple as present 
                          in 'schema.py'

    OUTPUT
        If the schema is in line then prints 
        'Raw datas schema is in line with the schema present in schema.py' 
        else prints
        'Raw datas schema is NOT in line with the schema present in schema.py'

    
    SAMPLE USAGE
        raw_data_schema_check
    '''
    
    #cnx = sqlite3.connect(DB_PATH+DB_FILE_NAME)
    loaded_data = pd.read_csv(DATA_DIRECTORY, index_col=[0])

    #loaded_data = pd.read_sql('select * from loaded_data', cnx)
    
    check = set(loaded_data.columns) == set(raw_data_schema)
    if check:
        print('Raw datas schema is in line with the schema present in schema.py')
    else:
        print('Raw datas schema is NOT in line with the schema present in schema.py')
   

###############################################################################
# Define function to validate model's input schema
# ############################################################################## 

def model_input_schema_check():
    '''
    This function check if all the columns mentioned in model_input_schema in 
    schema.py are present in table named in 'model_input' in db file.

   
    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be   
        raw_data_schema : schema of models input data in the form oa list/tuple
                          present as in 'schema.py'

    OUTPUT
        If the schema is in line then prints 
        'Models input schema is in line with the schema present in schema.py'
        else prints
        'Models input schema is NOT in line with the schema present in schema.py'
    
    SAMPLE USAGE
        raw_data_schema_check
    '''
    cnx = sqlite3.connect(DB_PATH+DB_FILE_NAME)
    
    df_model_input = pd.read_sql('select * from model_input', cnx)
    
    check = set(df_model_input.columns) == set(model_input_schema)
    if check:
        print('Models input schema is in line with the schema present in schema.py')
    else:
        print('Models input schema is NOT in line with the schema present in schema.py')
    

    
    
