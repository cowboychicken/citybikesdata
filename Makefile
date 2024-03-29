####################################################################################################################
# Setup containers

docker-spin-up:
	docker compose --env-file env up --build -d

perms:
	sudo mkdir -p logs plugins temp dags tests migrations && sudo chmod -R u=rwx,g=rwx,o=rwx logs plugins temp dags tests migrations

up: perms docker-spin-up sleeper warehouse-migration

down:
	docker compose down

sleeper:
	sleep 15

sh:
	docker exec -ti pipelinerunner bash

####################################################################################################################
# Testing, auto formatting, type checks, & Lint checks

isort:
	docker exec pipelinerunner isort .

format:
	docker exec pipelinerunner python -m black -S --line-length 79 .

type:
	docker exec pipelinerunner mypy --ignore-missing-imports /opt/airflow

lint: 
	docker exec pipelinerunner flake8 /opt/airflow/dags

pytest:
	docker exec pipelinerunner pytest -p no:warnings -v /opt/airflow/tests

ci: isort format type lint pytest

####################################################################################################################
# Set up cloud infrastructure

tf-init:
	terraform -chdir=./terraform init

infra-up:
	terraform -chdir=./terraform apply

infra-down:
	terraform -chdir=./terraform destroy

infra-config:
	terraform -chdir=./terraform output

####################################################################################################################
# Create tables in Warehouse

db-migration:
	@read -p "Enter migration name:" migration_name; docker exec pipelinerunner yoyo new ./migrations -m "$$migration_name"

warehouse-migration:
	docker exec pipelinerunner yoyo develop --no-config-file --database postgres://postgres1:Password1@warehouse:5432/citybikes ./migrations

warehouse-rollback:
	docker exec pipelinerunner yoyo rollback --no-config-file --database postgres://postgres1:Password1@warehouse:5432/citybikes ./migrations

####################################################################################################################
# Port forwarding to local machine

cloud-metabase:
	terraform -chdir=./terraform output -raw private_key > private_key.pem && chmod 600 private_key.pem && ssh -o "IdentitiesOnly yes" -i private_key.pem ubuntu@$$(terraform -chdir=./terraform output -raw ec2_public_dns) -N -f -L 3001:$$(terraform -chdir=./terraform output -raw ec2_public_dns):3000 && open http://localhost:3001 && rm private_key.pem

cloud-airflow:
	terraform -chdir=./terraform output -raw private_key > private_key.pem && chmod 600 private_key.pem && ssh -o "IdentitiesOnly yes" -i private_key.pem ubuntu@$$(terraform -chdir=./terraform output -raw ec2_public_dns) -N -f -L 8081:$$(terraform -chdir=./terraform output -raw ec2_public_dns):8080 && open http://localhost:8081 && rm private_key.pem

####################################################################################################################
# Helpers

ssh-ec2:
	terraform -chdir=./terraform output -raw private_key > private_key.pem && chmod 600 private_key.pem && ssh -o StrictHostKeyChecking=no -o IdentitiesOnly=yes -i private_key.pem ubuntu@$$(terraform -chdir=./terraform output -raw ec2_public_dns) && rm private_key.pem
