python-reportingclient
======================

Client for [reporting-api](https://github.com/NeCTAR-RC/reporting-api).

Requirements:

* Python 2.7
* [Requests](http://python-requests.org) Python library
* [Python Keystone client](https://pypi.python.org/pypi/python-keystoneclient)


reportingclient
---------------

This package contains a Python client for the reporting API. The client
library allows the user to create a Client object which can be used to
extract data from a reporting API endpoint.

The Client object supports listing available reports, and fetching data for each
report with optional filters. Data is returned as an array of dicts, each
entry being a single record in the result set.

reporting_client.py
--------------------

This script provides a simple command line client to query the reporting
API. For usage information see:

`$ reporting_client.py --help`

If the `reporting-api` endpoint being used requires authentication, you
must either supply a previously generated Keystone token, or supply the
credentials necessary to obtain a token from Keystone.

Credentials will be sourced from the environment, using the common
OpenStack environment variables OS_USERNAME, OS_PASSWORD,
OS_PROJECT_NAME/OS_TENANT_NAME, OS_AUTH_URL and OS_TOKEN, or can be
provided on the command line. If the `reporting` endpoint is not in the
Keystone catalog it must be specified on the command line.

An example of a more complex use of the library is provided in the
`reporting_example.py` script.
