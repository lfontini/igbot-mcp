from zabbix_utils import ZabbixAPI
from infra.config import ZabbixConfig
from datetime import datetime, timedelta, timezone
import time

class ZabbixPingCheckAction():
    def connect_to_zabbix(self):
        url = ZabbixConfig.get_zabbix_url()
        user = ZabbixConfig.get_zabbix_user()
        password = ZabbixConfig.get_zabbix_password()
        zapi = ZabbixAPI(url=url, user=user, password=password , skip_version_check=True)
        return zapi

    def get_host_id(self, zapi, host_name):
        hosts = zapi.host.get(search={'host': host_name}, output=['hostid', 'host'])
        return hosts[0]['hostid'] if hosts else None

    def get_item_id(self, zapi, host_id, item_key):
        items = zapi.item.get(filter={'hostid': host_id, 'key_': item_key})
        if not items:
            ping_key = "icmpping[,20,300,,]"
            items = zapi.item.get(filter={'hostid': host_id, 'key_': ping_key})
            return items[0]['itemid'] if items else None
        return items[0]['itemid']

    def get_historical_data(self, zapi, item_id, hours=12):
        now = datetime.now(timezone.utc)
        hours_cleaned = int(str(hours).strip('"'))
        time_from = int((now - timedelta(hours=hours_cleaned)).timestamp())
        time_till = int(now.timestamp())
        return zapi.history.get(itemids=[item_id], time_from=time_from, time_till=time_till, output='extend', limit='10000')

    def calculate_downtimes(self, ping_history):
        interruptions = 0
        total_unavailable_time = timedelta(0)
        current_downtime = None
        last_interruption_time = None
        back_to_up_at = None

        for data in ping_history:
            timestamp = datetime.fromtimestamp(int(data['clock']), tz=timezone.utc)
            ping_value = float(data['value'])

            if ping_value == 0:  # Ping failed
                if current_downtime is None:
                    current_downtime = timestamp
            else:  # Ping succeeded
                if current_downtime is not None:
                    total_unavailable_time += (timestamp - current_downtime)
                    interruptions += 1
                    last_interruption_time = current_downtime
                    back_to_up_at = timestamp
                    current_downtime = None

        if current_downtime is not None:
            total_unavailable_time += (datetime.now(timezone.utc) - current_downtime)
            interruptions += 1
            last_interruption_time = current_downtime

        return interruptions, total_unavailable_time, last_interruption_time, back_to_up_at

    def get_current_status(self, zapi, host_id, ping_key):
        item_id_ping = self.get_item_id(zapi, host_id, ping_key)
        ping_history = self.get_historical_data(zapi, item_id_ping, hours=1)
        return "up" if ping_history and float(ping_history[-1]['value']) > 0 else "down"

    def get_packet_loss_events(self, api, hostid, itemid, hours=24, threshold=0.0):
        """
        Busca eventos de packet loss no histórico do Zabbix usando hostid e itemid.
        """
        try:
            itemid = str(itemid)
            packet_loss_events = []
            time_till = int(time.time())
            hours = int(hours)
            time_from = time_till - (hours * 3600)

            print(f"Buscando histórico para itemid {itemid} de {time_from} até {time_till}")

            history = api.history.get(
                itemids=[itemid],
                time_from=time_from,
                time_till=time_till,
                history=0,
                output='extend',
                sortfield='clock',
                sortorder='ASC'
            )

 
            if not history:
                print(f"Nenhum dado histórico encontrado para o itemid {itemid} no período de {hours} horas")
                return []

            for entry in history:
                loss_value = float(entry['value'])
                if loss_value > threshold:
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(entry['clock'])))
                    packet_loss_events.append({
                        'timestamp': timestamp,
                        'packet_loss_percent': loss_value
                    })

            # Exibe os resultados no formato solicitado
            if packet_loss_events:
                print(f"Total de eventos de packet loss encontrados: {len(packet_loss_events)}")
                for event in packet_loss_events:
                    print(f"Data/Hora: {event['timestamp']}")
                    print(f"Packet Loss: {event['packet_loss_percent']}%")
                    print("-" * 50)
            else:
                print(f"Nenhum evento de packet loss acima de {threshold}% encontrado no período de {hours} horas para o itemid {itemid}")

            return packet_loss_events

        except Exception as e:
            print(f"Erro ao coletar dados para o hostid {hostid} e itemid {itemid}: {str(e)}")
            return []

    def zabbix_troubleshooting(self, service, hours=12):
        ping_key = "icmpping[,20,200,,]"
        ping_loss_key = "icmppingloss[,20,200,,]"
        zapi = self.connect_to_zabbix()

        host_id = self.get_host_id(zapi, service)
        if not host_id:
            return {
                'status': "unknown",
                'message': "Service not found on Zabbix",
                'result_type': '2',
                'interruptions': None,
                'total_unavailable_time': None,
                'last_interruption_time': None,
                'back_to_up_at': None,
                'responsibility': "unknown",
                'issue_type': "unknown",
                'reason': "Not found on Zabbix",
                'packet_loss_events': []
                
            }

        item_id_ping = self.get_item_id(zapi, host_id, ping_key)
        current_status = self.get_current_status(zapi, host_id, ping_key)
        ping_history = self.get_historical_data(zapi, item_id_ping, hours=hours)

        item_id_loss = self.get_item_id(zapi, host_id, ping_loss_key)
        ping_loss_history = self.get_packet_loss_events(zapi, host_id, item_id_loss, hours=hours, threshold=0.0)

        interruptions, total_unavailable_time, last_interruption_time, back_to_up_at = self.calculate_downtimes(ping_history)

        two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)
        recent_interruptions = last_interruption_time and last_interruption_time >= two_hours_ago
        print("recent interruption " , recent_interruptions)

        # Análise de packet loss nas últimas 2 horas
        recent_packet_loss = False
        last_packet_loss_time = None
        max_packet_loss = 0.0
        for event in ping_loss_history:
            event_time = datetime.strptime(event['timestamp'], '%Y-%m-%d %H:%M:%S')
            event_time = event_time.replace(tzinfo=timezone.utc)  # Adiciona timezone UTC
            if event_time >= two_hours_ago:
                recent_packet_loss = True
                last_packet_loss_time = event_time
                if event['packet_loss_percent'] > max_packet_loss:
                    max_packet_loss = event['packet_loss_percent']

        # Lógica de decisão
        if current_status == "down":
            message = f"Down since {last_interruption_time.strftime('%Y-%m-%d %H:%M:%S UTC')}" if last_interruption_time else "Currently down"
            responsibility = "vendor"
            reason = "Service is down on Zabbix"
            issue_type = "outage"
        elif recent_packet_loss:
            message = f"Service active with recent packet loss (Max: {max_packet_loss}%) at {last_packet_loss_time.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            responsibility = "vendor"
            reason = f"Packet loss detected in the last 2 hours (Max: {max_packet_loss}%)"
            issue_type = "degradation"
        elif recent_interruptions:
            message = f"Service active but had an outage between {last_interruption_time.strftime('%Y-%m-%d %H:%M:%S UTC')} and {back_to_up_at.strftime('%Y-%m-%d %H:%M:%S UTC')}" if last_interruption_time and back_to_up_at else "Service active with recent interruptions"
            responsibility = "vendor"
            reason = "Service had recent interruptions"
            issue_type = "degradation"
        else:
            message = "Service active for more than 2 hours with no issues"
            responsibility = "customer"
            reason = "Service up on Zabbix with no interruptions or packet loss in the last 2 hours"
            issue_type = "unknown"

        return {
            'status': current_status,
            'message': message,
            'period': hours,
            'interruptions': interruptions,
            'total_unavailable_time': str(total_unavailable_time),
            'last_interruption_time': last_interruption_time.strftime('%Y-%m-%d %H:%M:%S UTC') if last_interruption_time else 'N/A',
            'back_to_up_at': back_to_up_at.strftime('%Y-%m-%d %H:%M:%S UTC') if back_to_up_at else 'N/A',
            'responsibility': responsibility,
            'result_type': '2',
            'reason': reason,
            'issue_type': issue_type,
            'packet_loss_events': ping_loss_history
        }
    
