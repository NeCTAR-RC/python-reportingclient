
from abc import ABCMeta
from abc import abstractmethod
import argparse
from keystoneauth1 import exceptions
from keystoneauth1.identity import v3
from keystoneauth1 import session
import six

# The reporting API server cares about nothing beyond a simple token. In the
# NeCTAR case it needs to be scoped to a project where the user has the correct
# role, but there are also other use cases - for example, an essentially null
# authentication approach (relying on network security rather than
# authentication), or a kerberos ticket, or whatever else you choose to use.
# The API server just takes a token and verifies that it conveys appropriate
# auth info about the supplier.


# This is the bare minimum - get a token, get the auth headers, and provide a
# way to find the endpoint
@six.add_metaclass(ABCMeta)
class ReportingAuth(object):
    token = None
    auth_headers = None

    def get_auth_token(self):
        return self.token

    def get_auth_headers(self):
        return self.auth_headers

    @abstractmethod
    def get_endpoint(self):
        raise NotImplementedError

    @abstractmethod
    def get_reporting_endpoint(self):
        raise NotImplementedError


# Any time we're using Keystone we need a bit more, since Keystone auth is
# session based
#
# This is still abstract, though - it needs something to set up the auth
class KeystoneAuth(ReportingAuth):
    session = None
    auth_url = None
    endpoint = None

    def _get_session(self, auth):
        if self.session:
            return
        self.session = session.Session(auth)
        try:
            self.auth_headers = self.session.get_auth_headers()
        except exceptions.auth.AuthorizationFailure:
            raise ValueError("Keystone authentication failed")

        self.token = self.auth_headers['X-Auth-Token']
        if not self.endpoint:
            try:
                self.endpoint = self.get_reporting_endpoint()
            except exceptions.catalog.EndpointNotFound:
                raise ValueError("No reporting endpoint found in the catalog")

    def get_endpoint(self, service_type, endpoint_type='public'):
        return self.session.get_endpoint(
                service_type=service_type,
                endpoint_type=endpoint_type)

    def get_reporting_endpoint(self):
        if self.endpoint:
            return self.endpoint
        return self.get_endpoint('reporting')

    @classmethod
    def add_auth_arguments(cls, parser):
        parser.add_argument(
            '--endpoint', required=False, default=None,
            help='reporting-api endpoint'
        )
        parser.add_argument(
            '--os-token', default=argparse.SUPPRESS,
            help='auth token for reporting-api'
        )
        parser.add_argument(
            '--debug', default=False, action='store_true',
            help='enable debug output (for development)'
        )
        parser.add_argument(
            '--os-username', default=argparse.SUPPRESS, help='Username'
        )
        parser.add_argument(
            '--os-password', default=argparse.SUPPRESS, help="User's password"
        )
        parser.add_argument(
            '--os-auth-url', default=argparse.SUPPRESS,
            help='Authentication URL'
        )
        parser.add_argument(
            '--os-project-name', default=argparse.SUPPRESS,
            help='Project name to scope to'
        )
        parser.add_argument(
            '--os-tenant-name', default=argparse.SUPPRESS,
            help='Project name to scope to'
        )
        parser.add_argument(
            '--os-project-domain-name', default=argparse.SUPPRESS,
            help='Domain project is scoped to (defaults to "default")'
        )
        parser.add_argument(
            '--os-user-domain-name', default=argparse.SUPPRESS,
            help='Domain user is scoped to (defaults to "default")'
        )


# The keystone model can take a user-supplied token, or it can take a set of
# credentials.
class KeystoneToken(KeystoneAuth):
    def __init__(self, token=None, auth_url=None, endpoint=None):
        if not token and not auth_url:
            raise ValueError("No usable token supplied")

        self.token = token
        self.auth_url = auth_url
        self.endpoint = endpoint
        auth = v3.Token(auth_url=auth_url, token=token)
        self._get_session(auth)


class KeystonePassword(KeystoneAuth):
    def __init__(self, auth_url=None, endpoint=None, username=None,
                 password=None, project_name=None,
                 user_domain_name=None, project_domain_name=None):
        self.token = None
        self.auth_url = auth_url
        self.endpoint = endpoint
        self.auth_headers = None
        if not (username and password and project_name and auth_url and
                user_domain_name and project_domain_name):
            raise ValueError("No usable credentials supplied")

        auth = v3.Password(auth_url=auth_url, username=username,
                           password=password, project_name=project_name,
                           user_domain_name=user_domain_name,
                           project_domain_name=project_domain_name)
        self._get_session(auth)
