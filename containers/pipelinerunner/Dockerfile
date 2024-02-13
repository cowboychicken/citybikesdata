FROM python:3.9.5

# set up location of code
WORKDIR /code
ENV PYTHONPATH=/code/src

RUN sudo su

# install cron
RUN apt-get update && apt-get install cron -y

# install python requirements
ADD ./containers/pipelinerunner/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# copy repo
COPY ./ /code/

# ref: https://stackoverflow.com/questions/37458287/how-to-run-a-cron-job-inside-a-docker-container
# Copy pull_bitcoin_exchange_info file to the cron.d directory
COPY /scheduler/pull_api_info /etc/cron.d/pull_api_info
COPY /scheduler/load_to_edw /etc/cron.d/load_to_edw

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/pull_api_info
RUN chmod 0644 /etc/cron.d/load_to_edw

# Apply cron job
RUN crontab /etc/cron.d/pull_api_info
RUN crontab /etc/cron.d/load_to_edw

# Create the log file to be able to run tail
RUN touch /var/log/cron.log
 
# Run cron
CMD cron && tail -f /var/log/cron.log