"""
Python client binding to the OpenStack Reporting API.
"""

import logging
import requests
from urllib import urlencode


class ReportingClient(object):
    """Encapsulates the Reporting API and provides access to its reports.
    """

    def __init__(self, auth):
        self.logger = logging.getLogger(__name__)
        self.versions = None
        self.reports = None
        self.auth = auth
        self.token = auth.get_auth_token()
        self.auth_headers = auth.get_auth_headers()
        self.endpoint = auth.get_reporting_endpoint()

    def _request(self, url, **params):
        """Send a GET request to the API service.
        """
        if self.endpoint.endswith('/') or url.startswith('/'):
            url = self.endpoint + url
        else:
            url = self.endpoint + '/' + url
        if len(params):
            url = url + '?' + urlencode(params)
        # technically this can be done directly with the token, but done this
        # way it will still work if additional auth headers are added later
        headers = self.auth_headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_versions(self):
        """Return a list of details of available versions of the API.
        """
        if not self.versions:
            self.versions = self._request('')
        return self.versions

    def get_version(self, version_id):
        """Return details of the given version of the API.
        """
        for version in self.get_versions():
            if version.id == version_id:
                return version
        raise ValueError(
            "No server support for API version '" + version_id + "'"
        )

    def get_any_version_link(self, link_type):
        """Return details of the first link of the given type found in
        any available version of the API.
        """
        for version in self.get_versions():
            if link_type in version['links']:
                return version['links'][link_type]
        raise ValueError(
            "No server API version supports link type '" + link_type + "'"
        )

    def get_reports(self):
        """Return a list of all reports available on the server.
        """
        if not self.reports:
            self.reports = self._request(self.get_any_version_link('reports'))
        return self.reports

    def get_report_url(self, report_name):
        """Return the URL from which the given-named report will be served
        in response to a GET request.
        """
        for report in self.get_reports():
            if report['name'] == report_name:
                return report['links']['self']
        raise ValueError("No report '" + report_name + "' available")

    def fetch(self, report, **params):
        """Fetch the named report, optionally passing the given parameters to it.
        """
        self.logger.debug('Fetching "%s"...', report)
        data = self._request(self.get_report_url(report), **params)
        self.logger.debug('Fetched "%s".', report)
        return data
