"""Functions to provide an interface to GCP discovery and client apis."""

import logging
import subprocess

import google.auth
import google.auth.transport.requests

from googleapiclient import discovery
from googleapiclient import errors
from googleapiclient.discovery_cache import base as discovery_cache_base

#from google.cloud import bigquery
#from google.cloud import pubsub_v1

# API details

_MONITORING_SERVICE_NAME = 'monitoring'
_MONITORING_SERVICE_API_VERSION = 'v3'

_PROJECTS_SERVICE_NAME = 'cloudresourcemanager'
_PROJECTS_SERVICE_API_VERSION = 'v1'

_METADATA_URL = ('http://metadata/computeMetadata/v1/instance/service-accounts'
                 '/default/identity?audience=')

# No.of retires when making a query against GCP API's.
_NUM_RETRIES = 3


class _MemoryCache(discovery_cache_base.Cache):
    """Simple cache to hold discovery information."""
    _CACHE = {}

    def get(self, url):
        return _MemoryCache._CACHE.get(url)

    def set(self, url, content):
        _MemoryCache._CACHE[url] = content

def monitoring_service(creds=None):
    """Build monitoring service."""
    service = discovery.build(_MONITORING_SERVICE_NAME,
                              _MONITORING_SERVICE_API_VERSION,
                              credentials=creds,
                              cache=_MemoryCache())
    return service


def projects_service(creds=None):
    """Build projects service."""
    service = discovery.build(_PROJECTS_SERVICE_NAME,
                              _PROJECTS_SERVICE_API_VERSION,
                              credentials=creds,
                              cache=_MemoryCache())
    return service.projects()  # pylint: disable=no-member


def get_access_token():
    """Return access token for use in API request.

    Raises:
        requests.exceptions.ConnectionError.
    """
    credentials, _ = google.auth.default(scopes=[
        'https://www.googleapis.com/auth/cloud-platform',
        'https://www.googleapis.com/auth/cloud-platform.read-only'
    ])
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token


def get_access_token_gcloud():
    """Return access token(for use in API request) using gcloud command."""
    command = 'gcloud auth print-access-token'
    response = execute_command(command)
    if response:
        return response[0].decode('utf-8')
    return ''


def execute_command(command):
    """Execute a bash command and return the result.

    Args:
        command: str, gcloud command to execute.

    Returns:
        tuple, stdout and stderr result.
    """
    res = None
    with subprocess.Popen(command, shell=True,
                          stdout=subprocess.PIPE) as process:
        res = process.communicate()
    # Returns (stdout, stderr)
    return res


def execute_request(request):
    """Execute GCP API request and return results.

    Args:
        request: obj, http request.

    Returns:
        response object if successful else None.
    """
    try:
        return request.execute(num_retries=_NUM_RETRIES)
    except errors.HttpError as err:
        logging.error(err)
