import itertools
import logging
import json
from argparse import ArgumentParser
from lib import monitoring_lib
from lib import projects_lib
from lib import sender
import os

project_id = os.environ['PROJECT_ID']
host = os.environ['HOST_IN_ZABBIX']
vpc = bool(os.environ['VPC'])

_MQL_ALL = """
fetch consumer_quota
| { usage: metric serviceruntime.googleapis.com/quota/allocation/usage
    | align next_older(1w)
    | group_by [resource.location,
         metric.quota_metric]
  ; limit: metric serviceruntime.googleapis.com/quota/limit
    | align next_older(1w)
    | group_by [resource.location,
         metric.quota_metric, metric.limit_name] }
| join
| value [usage: val(0), limit: val(1)]
"""

_MQL_VPC = """
fetch compute.googleapis.com/VpcNetwork
| { metric compute.googleapis.com/quota/instances_per_vpc_network/usage
    | align next_older(1d)
    | group_by [resource.resource_container, metric.limit_name,resource.location, resource.network_id],max(val())
    ; metric compute.googleapis.com/quota/instances_per_vpc_network/limit
| align next_older(1d)
| group_by [resource.resource_container, metric.limit_name,resource.location, resource.network_id],min(val())
}
| ratio
| every 1m
| condition gt(val(), 0.80 '1')
"""

PROJECT_ATTRS = ('name', 'id', 'number', 'parent_type', 'parent_id',
                 'parent_name', 'ancestry', 'timestamp')

RESOURCE_ATTRS = ('resource.project_id', 'resource.service',
                  'resource.location', 'metric.limit_name',
                  'metric.quota_metric', 'endTime', 'metric_value_types',
                  'metric_values', 'usage', 'limit', 'consumption_percentage')

class _Quota:
    """Quota object to capture individual quota details for a metric."""
    def __init__(self):
        self._resource_type = ''
        self._metric_type = ''
        self._project_data = {}
        self._api_result = {}

    def to_dict(self):
        """Return the data as dict."""
        data = {
            'resource.type': self._resource_type,
            'metric.type': self._metric_type
        }
        data.update({k: self._project_data.get(k, '') for k in PROJECT_ATTRS})
        data.update({k: self._api_result.get(k, '') for k in RESOURCE_ATTRS})
        data['metric_value_types'] = ','.join(data['metric_value_types'])
        data['metric_values'] = ','.join(
            [str(v) for v in data['metric_values']])
        return {k.replace('.', '_'): v for k, v in data.items()}

def get_all(id_project):
    mql = _MQL_ALL
    results = monitoring_lib.query_timeseries_mql(id_project, mql)
    to_json = json.dumps(list(results))
    return to_json

def get_vpc(id_project):
    mql = _MQL_VPC
    results = monitoring_lib.query_timeseries_mql(id_project, mql)
    to_json = json.dumps(list(results))
    return to_json

def start(request):
  data = projects_lib._project_data(project_id)
  project = projects_lib.Project.from_dict(data)
  quotas = get_all(project_id)
  if vpc == 'True':
    quotas_vpc = get_vpc(project_id)
    sender.send_data_vpc(host,quotas,quotas_vpc)
    return f'Dados enviados - Coleta de VPC'
  else:
    sender.send_data(host,quotas)
    return f'Dados envaidos - Sem coleta de VPC'



