# PyCentreon

## Introduction
This project helps users to deal with Centreon API v2.0 (released from 23.10) through python API calls.
It is derived from the PyNetbox SDK (thanks @netbox-community for their work) on 04/2024 and adapted to Centreon.

## Quick Start
To use this tool, you'll need to instantiate the API

```
import pycentreon

centreon_url = "https://centreon.domain.com/centreon"
username = 'ctn_username'
password = 'ctn_password'
ctn = pycentreon.api(centreon_url)
ctn.create_token(username, password)
```

## Create Queries
Next you can play with hosts and services this way

```
# Create list of all hosts
existing_hosts = list(ctn.monitoring.hosts.all())

# Create list of all services
existing_services = list(ctn.monitoring.services.all())
```
