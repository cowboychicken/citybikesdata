import citybikesdata.extract as extract
import citybikesdata.transform as transform

from airflow.decorators import dag, task
from airflow.utils.dates import days_ago


@dag(dag_id = "citybikes_etl", schedule_interval="*/5 * * * *")
def citybikes_etl_dag():
    
    @task(task_id="load_json_to_edl", start_date=days_ago(1))
    def extract_from_api(ds=None, **kwargs):
        return extract.main()
    
    @task(task_id="process_networks", start_date=days_ago(1))
    def process_networks(ds=None, **kwargs):
        return transform.load_network_data_to_edw()
    
    @task(task_id="process_stations", start_date=days_ago(1))
    def process_stations(ds=None, **kwargs):
        return transform.load_station_data_to_edw()

    dummytask = extract_from_api()
    dummytask = process_networks()
    dummytask = process_stations()

citybikes_dag = citybikes_etl_dag()


