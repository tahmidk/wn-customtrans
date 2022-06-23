# Use Python3.10.5 minimal docker image as base image
FROM python:3.10.5-slim

# Create and set the working directory w/in the container
WORKDIR /flaskapp

# Copy everything in Dockerfile dir into working dir
ADD . /flaskapp

# Install essential packages
RUN apt-get update
RUN apt-get install -y 	build-essential \
			libxml2-dev \
			libxslt-dev \
			zlib1g-dev \
			python-dev

# Install python dependencies
RUN pip --no-cache-dir install -r requirements.txt

# Start uWSGI
CMD ["uwsgi", "app.ini"]
