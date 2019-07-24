#!/usr/bin/env python3
import abc
import os
import boto3
import configparser
import json
from pathlib import Path

def clear_console():
    if (os.name == 'nt'):
        os.system('cls')
    elif (os.name == 'posix'):
        os.system('clear')
    # If os.name does not match either of these then the console will not be cleared

class MenuContext:

    def __init__(self, state):
        self._state = state

    def set_state(self, state):
        self._state = state

    def request(self):
        self._state.handle(self)

class State(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def handle(self, menu_context):
        pass

class MainMenu(State):

    def __init__(self):
        self._server_statuses = None
        config_path = str(Path.home()) + '/.mc-server-manager/config'
        with open(config_path, 'r') as config_in:
            self._servers = json.load(config_in)

    def refresh_server_info(self):
        config_path = str(Path.home()) + '/.mc-server-manager/config'
        with open(config_path, 'r') as config_in:
            self._servers = json.load(config_in)
        ec2 = boto3.client('ec2')
        self._server_statuses = []
        for server in self._servers:
            try:
                response = ec2.describe_instances(
                    InstanceIds=[
                        server['InstanceId']
                    ]
                )

                current_state = response['Reservations'][0]['Instances'][0]['State']['Name']
                ip_address = 'NOT APPLICABLE'

                if ('running' == current_state):
                    ip_address = response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['PrivateIpAddresses'][0]['Association']['PublicIp']
                self._server_statuses.append(
                    {
                        'Name': server['Name'],
                        'InstanceId': server['InstanceId'],
                        'State': current_state,
                        'IpAddress': ip_address
                    }
                )
            except:
                self._server_statuses.append(
                    {
                        'Name': server['Name'],
                        'InstanceId': server['InstanceId'],
                        'State': 'ERROR RETRIEVING STATE',
                        'IpAddress': 'ERROR RETRIEVING IP ADDRESS'
                    }
                )

    def printMainMenu(self, menu_context):
        clear_console()
        print('Welcome to the Minecraft server admin tool\n')
        print('The current server statuses are: ')
        for server in self._server_statuses:
            print(server['Name'] + ': ' + 'Current State is ' + server['State'] + ' | Current IP address is ' + server['IpAddress'])

        selection = None
        while (selection != '1' and selection != '2' and selection != '3' and selection != '4'):
            print('Please select from the following options')
            print('[1] Start and stop servers')
            print('[2] Update your AWS credentials')
            print('[3] Refresh server details')
            print('[4] Modify App Settings')
            print('[0] Exit')

            selection = input('Selection: ')
            if (selection == '1'):
                menu_context.set_state(ServerMenu())
            elif (selection == '2'):
                menu_context.set_state(CredentialMenu())
            elif (selection == '3'):
                print('Please wait a moment, refreshing details...')
                self.refresh_server_info()
            elif (selection == '4'):
                menu_context.set_state(AppConfigMenu())
            elif (selection == '0'):
                clear_console()
                exit()
            else:
                print('Invalid selection....')

    def handle(self, menu_context):
        if (self._server_statuses is None):
            self.refresh_server_info()
        self.printMainMenu(menu_context)

class ServerMenu(State):

    def start_server(self, instance_id):
        print('Please wait while the server is started. This may take a few minutes...')
        ec2 = boto3.client('ec2')
        try:
            ec2.start_instances(
                InstanceIds = [
                    instance_id
                ]
            )
            waiter = ec2.get_waiter('instance_running')
            waiter.wait(
                InstanceIds = [
                    instance_id
                ]
            )
        except:
            input('Unable to start server. Press any key to continue...')

    def stop_server(self, instance_id):
        print('Please wait while the server is stopped. This may take a few minutes...')
        ec2 = boto3.client('ec2')
        try:
            ec2.stop_instances(
                InstanceIds = [
                    instance_id
                ]
            )
            waiter = ec2.get_waiter('instance_stopped')
            waiter.wait(
                InstanceIds = [
                    instance_id
                ]
            )
        except:
            input('Unable to start server. Press any key to continue...')

    def restart_server(self, instance_id):
        print('Please wait while the server is restarted. This may take a few minutes...')
        ec2 = boto3.client('ec2')
        try:
            ec2.reboot_instances(
                InstanceIds = [
                    instance_id
                ]
            )
            waiter = ec2.get_waiter('instance_running')
            waiter.wait(
                InstanceIds = [
                    instance_id
                ]
            )
        except:
            input('Unable to start server. Press any key to continue...')

    def refresh_server_info(self):
        ec2 = boto3.client('ec2')
        self._server_statuses = []
        for server in self._servers:
            try:
                response = ec2.describe_instances(
                    InstanceIds=[
                        server['InstanceId']
                    ]
                )

                current_state = response['Reservations'][0]['Instances'][0]['State']['Name']
                ip_address = 'NOT APPLICABLE'

                if ('running' == current_state):
                    ip_address = response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['PrivateIpAddresses'][0]['Association']['PublicIp']
                self._server_statuses.append(
                    {
                        'Name': server['Name'],
                        'InstanceId': server['InstanceId'],
                        'State': current_state,
                        'IpAddress': ip_address
                    }
                )
            except:
                self._server_statuses.append(
                    {
                        'Name': server['Name'],
                        'InstanceId': server['InstanceId'],
                        'State': 'ERROR RETRIEVING STATE',
                        'IpAddress': 'ERROR RETRIEVING IP ADDRESS'
                    }
                )

    def print_server_menu(self, menu_context):
        clear_console()
        print('Servers: ')
        for index, server in enumerate(self._server_statuses):
            print('[{}] {}'.format(index, server['Name']))
        user_selection = int(input('Please select a server: '))

        selected_server = self._server_statuses[user_selection]

        menu_selection = None
        while (menu_selection != '5' and menu_selection != '0'):
            clear_console()
            print('SELECTED SERVER: {} | CURRENT STATE: {} | IP ADDRESS: {}\n'.format(selected_server['Name'], selected_server['State'], selected_server['IpAddress']))
            print('Please select from the following options')
            print('[1] Start the server')
            print('[2] Stop the server')
            print('[3] Restart the server')
            print('[4] Refresh current server status')
            print('[5] Return to server selection')
            print('[0] Return to main menu')
            menu_selection = input('Selection: ')

            if (menu_selection == '1'):
                self.start_server(selected_server['InstanceId'])
                self.refresh_server_info()
                selected_server = self._server_statuses[user_selection]
                clear_console()
            elif (menu_selection == '2'):
                self.stop_server(selected_server['InstanceId'])
                self.refresh_server_info()
                selected_server = self._server_statuses[user_selection]
                clear_console()
            elif (menu_selection == '3'):
                self.restart_server(selected_server['InstanceId'])
                self.refresh_server_info()
                selected_server = self._server_statuses[user_selection]
                clear_console()
            elif (menu_selection == '4'):
                print('Please wait a moment, refreshing details...')
                self.refresh_server_info()
                selected_server = self._server_statuses[user_selection]
                clear_console()
            elif (menu_selection == '5'):
                return
            elif (menu_selection == '0'):
                menu_context.set_state(MainMenu())
            else:
                print('Invalid selection, please choose from the options above')


    def handle(self, menu_context):
        if (self._server_statuses is None):
            self.refresh_server_info()
        self.print_server_menu(menu_context)

    def __init__(self):
        self._server_statuses = None
        config_path = str(Path.home()) + '/.mc-server-manager/config'
        with open(config_path, 'r') as config_in:
            self._servers = json.load(config_in)

class CredentialMenu(State):

    def __init__(self):
        self._aws_config_details = None

    def load_config(self):
        clear_console()
        config = configparser.ConfigParser()
        cred_path = str(Path.home()) + '/.aws/credentials'
        current_access_key = ''
        masked_access_key = ''
        current_secret_key = ''
        masked_secret_key = ''
        if (os.path.exists(cred_path) and os.path.isfile(cred_path)):
            config.read(cred_path)
            if ('default' in config and 'aws_access_key_id' in config['default'] and config['default']['aws_access_key_id']):
                current_access_key = config['default']['aws_access_key_id'] 
                masked_access_key = '****************' + current_access_key[-4:]
            if ('default' in config and 'aws_secret_access_key' in config['default'] and config['default']['aws_secret_access_key']):
                current_secret_key = config['default']['aws_secret_access_key']
                masked_secret_key = '****************' + current_secret_key[-4:]

        print('Welcome to the AWS credential modifier')
        access_key_input = input('Access Key ID [{}]: '.format(masked_access_key))
        secret_key_input = input('Secret Access Key [{}]: '.format(masked_secret_key))
        if (access_key_input):
            current_access_key = access_key_input
        if (secret_key_input):
            current_secret_key = secret_key_input

        with open(cred_path, 'w') as configfile:
            config.read_dict(
                {
                    'default': {
                        'aws_access_key_id': current_access_key,
                        'aws_secret_access_key': current_secret_key
                    }
                }
            )
            config.write(configfile)

    def handle(self, menu_context):
        config_path = str(Path.home()) + '/.aws/credentials'
        config_dir = str(Path.home()) + '/.aws'
        if (not os.path.exists(config_dir)):
            os.makedirs(config_dir)
        if (not os.path.exists(config_path) or not os.path.isfile(config_path)):
            Path(config_path).touch()
        self.load_config()
        menu_context.set_state(MainMenu())

class AppConfigMenu(State):

    def __init__(self):
        self._servers = None

    def load_servers(self):
        config_path = str(Path.home()) + '/.mc-server-manager/config'
        if (os.path.exists(config_path) and os.path.isfile(config_path)):
            with open(config_path) as config_in:
                self._servers = json.load(config_in)
        else:
            self._servers = []

    def save_servers(self):
        config_path = str(Path.home()) + '/.mc-server-manager/config'
        with open(config_path, 'w') as config_out:
            json.dump(self._servers, config_out)

    def add_server(self):
        clear_console()
        server_name = input('Please enter the new server\'s name: ')
        instance_id = input('Please enter the new server\'s instance id: ')
        self._servers.append(
            {
                'Name': server_name,
                'InstanceId': instance_id
            }
        )
    
    def remove_server(self):
        clear_console()
        for index, server in enumerate(self._servers):
            print('[{}] Name: {} | Instance ID: {}'.format(index, server['Name'], server['InstanceId']))
        server_selection = int(input('Please select a server to remove: '))
        self._servers.pop(server_selection)

    def modify_server(self):
        clear_console()
        for index, server in enumerate(self._servers):
            print('[{}] Name: {} | Instance ID: {}'.format(index, server['Name'], server['InstanceId']))
        server_selection = int(input('Please select a server to remove: '))
        server_name_input = input('Please enter the new server\'s name [{}]: '.format(self._servers[server_selection]['Name']))
        instance_id_input = input('Please enter the new server\'s instance id [{}]: '.format(self._servers[server_selection]['InstanceId']))
        if (server_name_input):
            self._servers[server_selection]['Name'] = server_name_input
        if (instance_id_input):
            self._servers[server_selection]['InstanceId'] = instance_id_input

    def show_config_menu(self, menu_context):
        menu_selection = None
        while(menu_selection != '0'):
            clear_console()
            for index, server in enumerate(self._servers):
                print('[{}] Name: {} | Instance ID: {}'.format(index, server['Name'], server['InstanceId']))
            print('')
            print('Welcome to the app config menu, from here you can alter which servers this application monitors')
            print('Please select from the following options')
            print('[1] Add new server to the list')
            print('[2] Remove existing server from the list')
            print('[3] Modify existing server on the list')
            print('[0] Return to main menu')
            menu_selection = input('Please select an operation: ')

            if (menu_selection == '1'):
                self.add_server()
            elif (menu_selection == '2'):
                self.remove_server()
            elif (menu_selection == '3'):
                self.modify_server()
            elif (menu_selection == '0'):
                menu_context.set_state(MainMenu())
            else:
                input('Invalid selection, please select from the displayed options. Press enter to continue...')

    def handle(self, menu_context):
        self.load_servers()
        self.show_config_menu(menu_context)
        self.save_servers()

def check_and_set_aws_config():
    aws_config_path = str(Path.home()) + '/.aws/config'
    aws_config_dir = str(Path.home()) + '/.aws'
    config = configparser.ConfigParser()
    if (not os.path.exists(aws_config_dir)):
        os.makedirs(aws_config_dir)
    if (not os.path.exists(aws_config_path) or not os.path.isfile(aws_config_path)):
        Path(aws_config_path).touch()
        region_input = input('Please enter the region to use as a default region: ')
        with open(aws_config_path, 'w') as configfile:
            config.read_dict(
                {
                    'default': {
                        'region': region_input
                    }
                }
            )
            config.write(configfile)
        
def main():
    clear_console()
    check_and_set_aws_config()
    config_path = str(Path.home()) + '/.mc-server-manager/config'
    config_dir = str(Path.home()) + '/.mc-server-manager'
    if (not os.path.exists(config_dir)):
        os.makedirs(config_dir)
    if (not os.path.exists(config_path) or not os.path.isfile(config_path)):
        Path(config_path).touch()
        with open(config_path, 'a') as new_config:
            json.dump([], new_config)
    menu_context = MenuContext(MainMenu())
    while (True):
        menu_context.request()

if (__name__ == "__main__"):
    main()