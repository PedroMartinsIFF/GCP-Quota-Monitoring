from pyzabbix import ZabbixMetric, ZabbixSender
import os


ZABBIX_HOST = 'us-east1-be-pool-1.monitoracao.gcp.i.globo'
ZABBIX_PORT = 10002

def send_data_vpc(host,data,data_vpc):

    zabbix_sender = ZabbixSender(zabbix_server=ZABBIX_HOST, zabbix_port=ZABBIX_PORT, use_config=None, chunk_size=2)
    packet = [
        ZabbixMetric(host,"quotas.raw.data",data),
        ZabbixMetric(host,"quotas.raw.data.vpc",data_vpc),
    ]
    result = zabbix_sender.send(packet)

def send_data(host,data):
    zabbix_sender = ZabbixSender(zabbix_server=ZABBIX_HOST, zabbix_port=ZABBIX_PORT, use_config=None, chunk_size=2)
    packet = [
        ZabbixMetric(host,"quotas.raw.data",data),
    ]
    result = zabbix_sender.send(packet)
