# CityBikes Data Dashboard

An interactive dashboard that displays public bike sharing availability in the user's area, powered by a simple ETL pipeline that collects data from the [CityBikes API](https://api.citybik.es/v2/).

## Instructions

### To run locally
Prerequisites to run locally:
1. [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
2. [Docker](https://docs.docker.com/engine/install/)
3. [Docker Compose](https://docs.docker.com/compose/install/) v1.27.0 or later

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
Pipeline will automatically start running in 'pipelinerunner' container. 
Confirm container statuses using:
```bash
docker ps
```
To use Metabase instance and start building dashboard, navigate to [http:localhost:3000](http:localhost:3000)

### To run on cloud (ec2)
Prerequisites to run using ec2 and terraform:
1. [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
2. [Configure AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
3. [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli) 

Run the following commands to spin up ec2 instance:

```shell
terraform -chdir=./terraform init
terraform -chdir=./terraform apply 
```

If successful, the same containers that were running locally should now be running on the ec2 instance. 
Thus you can navigate to http:_YourEc2AddressHere_:3000 to access the cloud's metabase instance. 

If not working, most likely one of the 'setup' steps from 'main.tf' (line 123-153) did not complete. 
Use the following make command to start ssh session with your ec2 instance and troubleshoot and rerun relevant commands. 
```bash
make ssh-ec2
```

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


