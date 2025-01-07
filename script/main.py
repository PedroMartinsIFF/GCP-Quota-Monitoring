import itertools
import logging
import json
from argparse import ArgumentParser
from lib import monitoring_lib
from lib import projects_lib
from lib import sender
from google.cloud import compute_v1

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

_MQL_VPC = [
## INSTANCES PER VPC
"""
fetch compute.googleapis.com/VpcNetwork
| { usage: metric compute.googleapis.com/quota/instances_per_vpc_network/usage
    | align next_older(1w)
    | group_by [resource.resource_container, metric.limit_name,resource.location, resource.network_id],max(val())
  ; limit: metric compute.googleapis.com/quota/instances_per_vpc_network/limit
    | align next_older(1w)
    | group_by [resource.resource_container, metric.limit_name,resource.location, resource.network_id],min(val()) }
| join
| value [usage: val(0), limit: val(1)]
""",
## IP ALIASES PER VPC
"""
fetch compute.googleapis.com/VpcNetwork
| { usage: metric compute.googleapis.com/quota/ip_aliases_per_vpc_network/usage
    | align next_older(1w)
    | group_by [resource.resource_container, metric.limit_name,resource.location, resource.network_id],max(val())
  ; limit: metric compute.googleapis.com/quota/ip_aliases_per_vpc_network/limit
    | align next_older(1w)
    | group_by [resource.resource_container, metric.limit_name,resource.location, resource.network_id],min(val()) }
| join
| value [usage: val(0), limit: val(1)]
""",

## SUBNET RANGES PER VPC
"""
fetch compute.googleapis.com/VpcNetwork
| { usage: metric compute.googleapis.com/quota/subnet_ranges_per_vpc_network/usage
    | align next_older(1w)
    | group_by [resource.resource_container, metric.limit_name,resource.location, resource.network_id],max(val())
  ; limit: metric compute.googleapis.com/quota/subnet_ranges_per_vpc_network/limit
    | align next_older(1w)
    | group_by [resource.resource_container, metric.limit_name,resource.location, resource.network_id],min(val()) }
| join
| value [usage: val(0), limit: val(1)]
""",

## INTERNAL TCP/UDP ILB PER VPC
"""
fetch compute.googleapis.com/VpcNetwork
| { usage: metric compute.googleapis.com/quota/internal_lb_forwarding_rules_per_vpc_network/usage
    | align next_older(1w)
    | group_by [resource.resource_container, metric.limit_name,resource.location, resource.network_id],max(val())
  ; limit: metric compute.googleapis.com/quota/internal_lb_forwarding_rules_per_vpc_network/limit
    | align next_older(1w)
    | group_by [resource.resource_container, metric.limit_name,resource.location, resource.network_id],min(val()) }
| join
| value [usage: val(0), limit: val(1)]
""",

## INTERNAL HTTP(S) ILB PER VPC
"""
fetch compute.googleapis.com/VpcNetwork
| { usage: metric compute.googleapis.com/quota/internal_managed_forwarding_rules_per_vpc_network/usage
    | align next_older(1w)
    | group_by [resource.resource_container, metric.limit_name,resource.location, resource.network_id],max(val())
  ; limit: metric compute.googleapis.com/quota/internal_managed_forwarding_rules_per_vpc_network/limit
    | align next_older(1w)
    | group_by [resource.resource_container, metric.limit_name,resource.location, resource.network_id],min(val()) }
| join
| value [usage: val(0), limit: val(1)]
""",

## PSC GOOGLE APIS FORWARDING RULES PER VPC
"""
fetch compute.googleapis.com/VpcNetwork
| { usage: metric compute.googleapis.com/quota/psc_google_apis_forwarding_rules_per_vpc_network/usage
    | align next_older(1w)
    | group_by [resource.resource_container, metric.limit_name,resource.location, resource.network_id],max(val())
  ; limit: metric compute.googleapis.com/quota/psc_google_apis_forwarding_rules_per_vpc_network/limit
    | align next_older(1w)
    | group_by [resource.resource_container, metric.limit_name,resource.location, resource.network_id],min(val()) }
| join
| value [usage: val(0), limit: val(1)]
"""
]



PROJECT_ATTRS = ('name', 'id', 'number', 'parent_type', 'parent_id',
                 'parent_name', 'ancestry', 'timestamp')

RESOURCE_ATTRS = ('resource.project_id', 'resource.service',
                  'resource.location', 'metric.limit_name',
                  'metric.quota_metric', 'endTime', 'metric_value_types',
                  'metric_values', 'usage', 'limit', 'consumption_percentage')


parser = ArgumentParser(description = 'Script para capturar quotas de um projeto na GCP e enviar para um Host no Zabbix.')
parser.add_argument('--project', dest = 'project', required = True, help = 'ID do project na GCP')
parser.add_argument('--host', dest = 'host', required = True, help = 'Host no Zabbix')
parser.add_argument('--vpc', dest = 'vpc', required = False,  action = 'store_true' , help = 'Adicionar a flag como true se quiser monitorar quotas de VPC')
args = parser.parse_args()

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

def get_vpc_name(project, vpc_number):
    network = compute_v1.NetworksClient()
    return network.get(project=project, network=str(vpc_number)).name


def get_all(project):
    mql = _MQL_ALL
    results = monitoring_lib.query_timeseries_mql(args.project, mql)
    to_json = json.dumps(list(results))
    #return _results_as_json(project, _USAGE_METRIC_TYPE, results)
    return to_json

def get_vpc(project):
    results = []
    for mql in _MQL_VPC:
        mql_response = list(monitoring_lib.query_timeseries_mql(project, mql))[0]
        mql_response['network_name'] = get_vpc_name(project, mql_response['resource.network_id'])
        results.append(mql_response)
    to_json = json.dumps(results)

id = args.project
data = projects_lib._project_data(id)

project = projects_lib.Project.from_dict(data)
quotas = get_all(project)

if args.vpc == True:
    vpc = get_vpc(project)
    sender.send_data_vpc(args.host,quotas,vpc)
else:
    sender.send_data(args.host,quotas)


