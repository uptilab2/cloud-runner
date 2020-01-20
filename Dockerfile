###################################
#    Cloud Runner base image      #
#                                 #
# see README.md for usage details #
###################################

LABEL maintainer="emile.caron@uptilab.com"

# Use python base image
# or install python and pip yourself if your executable requires a different runtime
FROM python:3.8

######## CLOUD RUNNER SETUP ##############
# Setup cloud-runner
WORKDIR /runner
RUN pip install aiohttp==3.6.2 gunicorn==20.0.4
ADD ./app.py /runner/app.py

# Define default command. adjust concurrency settings if needed
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --worker-class aiohttp.GunicornWebWorker app:app

# Adjust timeout limit
ENV PROCESS_MAX_TIMEOUT=60
