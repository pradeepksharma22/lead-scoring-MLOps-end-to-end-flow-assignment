##############################################################################
# Import necessary modules
# #############################################################################


from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime, timedelta
import sys
sys.path.append('/home/airflow/dags/Lead_scoring_data_pipeline')
import utils 
from data_validation_checks import *
###############################################################################
# Define default arguments and DAG
# ##############################################################################

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2022,7,30),
    'retries' : 1, 
    'retry_delay' : timedelta(seconds=5)
}


ML_data_cleaning_dag = DAG(
                dag_id = 'Lead_Scoring_Data_Engineering_Pipeline',
                default_args = default_args,
                description = 'DAG to run data pipeline for lead scoring',
                schedule_interval = '@daily',
                catchup = False
)

###############################################################################
# Create a task for build_dbs() function with task_id 'building_db'
# ##############################################################################
building_db = PythonOperator(
            task_id = 'building_db',
            python_callable = build_dbs,
            dag = ML_data_cleaning_dag)
###############################################################################
# Create a task for raw_data_schema_check() function with task_id 'checking_raw_data_schema'
# ##############################################################################
checking_raw_data_schema = PythonOperator(
            task_id = 'checking_raw_data_schema',
            python_callable = raw_data_schema_check,
            dag = ML_data_cleaning_dag)
###############################################################################
# Create a task for load_data_into_db() function with task_id 'loading_data'
# #############################################################################
loading_data = PythonOperator(
            task_id = 'loading_data',
            python_callable = load_data_into_db,
            dag = ML_data_cleaning_dag)
###############################################################################
# Create a task for map_city_tier() function with task_id 'mapping_city_tier'
# ##############################################################################
mapping_city_tier = PythonOperator(
            task_id = 'mapping_city_tier',
            python_callable = map_city_tier,
            dag = ML_data_cleaning_dag)
###############################################################################
# Create a task for map_categorical_vars() function with task_id 'mapping_categorical_vars'
# ##############################################################################
mapping_categorical_vars = PythonOperator(
        task_id = 'mapping_categorical_vars',
        python_callable = map_categorical_vars,
        dag = ML_data_cleaning_dag)
###############################################################################
# Create a task for interactions_mapping() function with task_id 'mapping_interactions'
# ##############################################################################
mapping_interactions = PythonOperator(
        task_id = 'mapping_interactions',
        python_callable = interactions_mapping,
        dag = ML_data_cleaning_dag)
###############################################################################
# Create a task for model_input_schema_check() function with task_id 'checking_model_inputs_schema'
# ##############################################################################
checking_model_inputs_schema = PythonOperator(
            task_id = 'checking_model_inputs_schema',
            python_callable = model_input_schema_check,
            dag = ML_data_cleaning_dag)
###############################################################################
# Define the relation between the tasks
# ##############################################################################

building_db >> checking_raw_data_schema >> loading_data >> mapping_city_tier >> mapping_categorical_vars >> mapping_interactions >> checking_model_inputs_schema
