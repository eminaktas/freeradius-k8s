FROM 2stacks/radtest

LABEL MAINTAINER Emin AKTAS <eminaktas34@gmail.com>

RUN apk update && apk upgrade 

RUN apk add --update --no-cache python3

# https://stackoverflow.com/a/57437909/14091937
ENV PYTHONPATH /usr/lib/python3.8/site-packages

RUN apk add --update py3-netifaces py3-netaddr