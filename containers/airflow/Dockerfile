FROM apache/airflow:2.2.0

# set up location of code
# copy repo
COPY ./ /code/

# install python requirements
RUN pip install -r /code/containers/airflow/requirements.txt

ENV PYTHONPATH=/code/src
