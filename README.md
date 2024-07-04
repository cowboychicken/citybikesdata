# CityBikes Data Dashboard

An interactive dashboard that displays public bike sharing availability in the user's area, powered by a simple ETL pipeline that collects data from the [CityBikes API](https://api.citybik.es/v2/).

## Instructions (to run locally)

### Prerequisites to run locally:
1. [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
2. [Github account](https://github.com/)
3. [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/) v1.27.0 or later

Clone repo and run following commands to spin up docker containers:
```bash
docker compose --env-file env up --build -d
sleep 15
docker exec pipelinerunner yoyo develop --no-config-file --database postgres://postgres1:Password1@warehouse:5432/citybikes ./migrations
```
OR use this simple make command:
```bash
make up
```
Pipeline should automatically start running in the 'pipelinerunner' container. 
Confirm container statuses using:
```bash
docker ps
```
To use Metabase instance, navigate to [http:localhost:3000](http:localhost:3000)

## Architecture

![Pipeline](resources/images/citybikes_pipeline_diagram.png)

The pipeline begins with simple get requests to the API. These requests happen every 5 minutes and all responses are immediately stored in a single table. This single table was meant to act as a Data Lake so that I could preserve the raw data and have as many options later down the road for development and/or analysis.

The next step is to process the API responses from the previous step and update relevant tables. These new tables were meant to represent a Data Warehouse. There are two of these tables, one for each API endpoint, which we will go over later.

The last step is a transformation step where a list of transformations are performed on the two tables from the previous step to satisfy reporting needs.

The last two steps currently run every 30 minutes to reduce resource costs.

Finally, a Metabase instance is spun up and connected to all three database tables which is used to build the dashboard.

## Infrastructure

The majority of code written to facilitate the architecture above is written in Python w/ Pandas.
PostgreSQL is used for all data storage.
Apache Airflow is used for scheduling.*
Metabase is used for data visualization and dashboard creation.
All these components are containerized using Docker and are currently running on an AWS EC2 instance as our production environment.
Github is used for version control and repository hosting.
Github Actions is used to automate CI/CD workflows such as consistency measures and pushing new changes to the production environment via ssh(rsync).
Terraform is used for IaC, storing all settings and parameters for the EC2 instance. Making it easy to modify the instance when needed.
* currently using Cron to save money as the Airflow instance was consuming too much RAM.

![infra](resources/images/citybikes_infra_diagram.png)


