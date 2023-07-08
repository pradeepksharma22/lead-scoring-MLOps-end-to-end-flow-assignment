##############################################################################
# Import necessary modules
# #############################################################################

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.append('/home/airflow/dags/Lead_scoring_inference_pipeline')

from utils import *

###############################################################################
# Define default arguments and create an instance of DAG
# ##############################################################################

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2022,7,30),
    'retries' : 1, 
    'retry_delay' : timedelta(seconds=5)
}


Lead_scoring_inference_dag = DAG(
                dag_id = 'Lead_scoring_inference_pipeline',
                default_args = default_args,
                description = 'Inference pipeline of Lead Scoring system',
                schedule_interval = '@hourly',
                catchup = False
)

###############################################################################
# Create a task for encode_data_task() function with task_id 'encoding_categorical_variables'
# ##############################################################################

encoding_categorical_variables = PythonOperator(
        task_id = 'encoding_categorical_variables',
        python_callable = encode_features,
        dag = Lead_scoring_inference_dag)


###############################################################################
# Create a task for load_model() function with task_id 'generating_models_prediction'
# ##############################################################################

generating_models_prediction = PythonOperator(
        task_id = 'generating_models_prediction',
        python_callable = get_models_prediction,
        dag = Lead_scoring_inference_dag)

###############################################################################
# Create a task for prediction_col_check() function with task_id 'checking_model_prediction_ratio'
# ##############################################################################

checking_model_prediction_ratio = PythonOperator(
        task_id = 'checking_model_prediction_ratio',
        python_callable = prediction_ratio_check,
        dag = Lead_scoring_inference_dag)

###############################################################################
# Create a task for input_features_check() function with task_id 'checking_input_features'
# ##############################################################################

checking_input_features = PythonOperator(
        task_id = 'checking_input_features',
        python_callable = input_features_check,
        dag = Lead_scoring_inference_dag)

###############################################################################
# Define relation between tasks
# ##############################################################################
encoding_categorical_variables >> checking_input_features >> generating_models_prediction >> checking_model_prediction_ratio
