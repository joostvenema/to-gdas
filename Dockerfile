# to-gdas
#
# VERSION       1.0

# use the ubuntu base image provided by Docker
FROM ubuntu

MAINTAINER Joost Venema, joost.venema@kadaster.nl

# make sure the package repository is up to date
RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update

# install software dependecies
RUN apt-get install -y git python3-lxml python3-requests python3-bottle python3-waitress

# pull latest to-gdas version from github
RUN git clone https://github.com/ojajoh/to-gdas.git

# set workingdir to application dir
WORKDIR /usr/to-gdas

# bring app to live
ENTRYPOINT ["python3", "webapp.py"]

# open the default port
EXPOSE 9090
