import requests
from config import (username,
                    password,
                    librenms_api_key,
                    librenms_address,
                    config_path,)
from datetime import datetime
from netmiko import NetMikoAuthenticationException, ssh_exception
from napalm import get_network_driver

cisco_driver = get_network_driver('ios')

device_list = requests.get('http://' + librenms_address + '/api/v0/oxidized', headers={'X-Auth-Token': librenms_api_key})
parse_devices = device_list.json()


for host in parse_devices:
    if (host['os'] == 'iosxe') or (host['os'] == 'ios'):
        # load the device list into the napalm IOS driver
        load_device = cisco_driver(host['hostname'], username, password)
        try:
            load_device.open()

            # ok the device connection should be open, let pull the config
            file_time = datetime.now().strftime("%Y-%m-%dT-%H-%M-%S")
            device_config = load_device.get_config()

            # lets open a file and right the configs
            running_config = open(config_path + host['hostname'] + ' - ' + file_time + ' running_config.txt', 'w')
            running_config.write(device_config['running'])
            running_config.close()

            # again for the startup config
            startup_config = open(config_path + host['hostname'] + ' - ' + file_time + ' startup_config.txt', 'w')
            startup_config.write(device_config['startup'])
            startup_config.close()
            load_device.close()

            print(host['hostname'] + ' complete')

        except NetMikoAuthenticationException:
            print('Cannot connect to ' + host['hostname'])
            continue

        except AttributeError:
            continue

print('complete')
