'''
filename: utils.py
functions: encode_features, get_train_model
creator: shashank.gupta
version: 1
'''

###############################################################################
# Import necessary modules
# ##############################################################################

import pandas as pd
import numpy as np

import sqlite3
from sqlite3 import Error

import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from constants import *


###############################################################################
# Define the function to encode features
# ##############################################################################

def encode_features():
    '''
    This function one hot encodes the categorical features present in our  
    training dataset. This encoding is needed for feeding categorical data 
    to many scikit-learn models.

    INPUTS
        db_file_name : Name of the database file 
        db_path : path where the db file should be
        ONE_HOT_ENCODED_FEATURES : list of the features that needs to be there in the final encoded dataframe
        FEATURES_TO_ENCODE: list of features  from cleaned data that need to be one-hot encoded
       

    OUTPUT
        1. Save the encoded features in a table - features
        2. Save the target variable in a separate table - target


    SAMPLE USAGE
        encode_features()
        
    **NOTE : You can modify the encode_featues function used in heart disease's inference
        pipeline from the pre-requisite module for this.
    '''
    # read the model input data
    cnx = sqlite3.connect(DB_PATH+DB_FILE_NAME)
    df_model_input = pd.read_sql('select * from model_input', cnx)

    # create df to hold encoded data and intermediate data
    df_encoded = pd.DataFrame(columns=ONE_HOT_ENCODED_FEATURES)
    df_placeholder = pd.DataFrame()

    # encode the features using get_dummies()
    for f in FEATURES_TO_ENCODE:
        if(f in df_model_input.columns):
            encoded = pd.get_dummies(df_model_input[f])
            encoded = encoded.add_prefix(f + '_')
            df_placeholder = pd.concat([df_placeholder, encoded], axis=1)
        else:
            print('Feature not found')
            return df_model_input

    # add the encoded features into a single dataframe
    for feature in df_encoded.columns:
        if feature in df_model_input.columns:
            df_encoded[feature] = df_model_input[feature]
        if feature in df_placeholder.columns:
            df_encoded[feature] = df_placeholder[feature]
    df_encoded.fillna(0, inplace=True)

    # save the features and target in separate tables
    df_features = df_encoded.drop(['app_complete_flag'], axis=1)
    df_target = df_encoded[['app_complete_flag']]
    df_features.to_sql(name='features', con=cnx,
                       if_exists='replace', index=False)
    df_target.to_sql(name='target', con=cnx, if_exists='replace', index=False)

    cnx.close()


###############################################################################
# Define the function to train the model
# ##############################################################################

def get_trained_model():
    '''
    This function setups mlflow experiment to track the run of the training pipeline. It 
    also trains the model based on the features created in the previous function and 
    logs the train model into mlflow model registry for prediction. The input dataset is split
    into train and test data and the auc score calculated on the test data and
    recorded as a metric in mlflow run.   

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be


    OUTPUT
        Tracks the run in experiment named 'Lead_Scoring_Training_Pipeline'
        Logs the trained model into mlflow model registry with name 'LightGBM'
        Logs the metrics and parameters into mlflow run
        Calculate auc from the test data and log into mlflow run  

    SAMPLE USAGE
        get_trained_model()
    '''
    # set the tracking uri and experiment
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT)

    # read the input data
    cnx = sqlite3.connect(DB_PATH+DB_FILE_NAME)
    df_features = pd.read_sql('select * from features', cnx)
    df_target = pd.read_sql('select * from target', cnx)

    # split the dataset into train and test
    X_train, X_test, y_train, y_test = train_test_split(
        df_features, df_target, test_size=0.3, random_state=0)

    # start mlflow experiment
    with mlflow.start_run(run_name='run_LightGB') as mlrun:

        # train the model using LGBM Classifier on train dataset
        clf = lgb.LGBMClassifier()
        clf.set_params(**model_config)
        clf.fit(X_train, y_train)

        # log model in mlflow model registry
        mlflow.sklearn.log_model(
            sk_model=clf, artifact_path="models", registered_model_name='LightGBM')
        mlflow.log_params(model_config)

        # predict the results on test dataset
        y_pred = clf.predict(X_test)

        # log auc in mlflow
        auc = roc_auc_score(y_pred, y_test)
        mlflow.log_metric('auc', auc)

   
