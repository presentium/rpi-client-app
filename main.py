import configparser
import logging
from pathlib import Path
import platform
import sys
import grpc
import time

import presentium_pb2 as serializer
import presentium_pb2_grpc as grpc_lib

from src.Vault import Vault
from src.GrpcConnector import GrpcConnector
from src.Reader import Reader
from src.Screen import Screen

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Load config from config.ini
    config = configparser.ConfigParser()
    config.read('config/config.ini')

    # Init logging
    logging.basicConfig(filename=config['logging']['File'], level=logging.INFO)
    logger.info('Client started')

    # Get hostname
    hostname = platform.node()

    # Create instances of Screen and Reader
    screen = Screen()
    reader = Reader()

    # Check global status, are we registered?
    if not config['global'].getboolean('Registered'):
        # Wait for the registration cert path to appear
        screen.clear_and_write('Waiting for registration...')
        while not Path(f"{config['registration']['CertsPath']}/{config['registration']['CertsCert']}").exists():
            time.sleep(1)
        
        screen.clear_and_write('Registering...')

        # If we're not registered, we need to register
        logger.info('Client not registered, registering...')

        # Register client
        vault = Vault(logger=logger, vault_addr=config['vault']['ServerUrl'])
        result = vault.authenticate(
            client_cert_path=f"{config['registration']['CertsPath']}/{config['registration']['CertsCert']}",
            client_key_path=f"{config['registration']['CertsPath']}/{config['registration']['CertsKey']}"
        )

        if not result:
            logger.error('Error authenticating with Vault')
            sys.exit(1)

        logger.info('Client logged in successfully to Vault for registration')

        cert = vault.generate_device_cert(
            config['registration']['RoleName'],
            config['registration']['MountPoint'],
            hostname
        )

        servers_ca = vault.get_servers_ca(
            config['registration']['MountPoint'],
            config['vault']['ServersIssuerID']
        )

        # Extract cert and key from response and save them to disk
        cert_path = f"{config['vault']['CertsPath']}/{hostname}.crt"
        key_path = f"{config['vault']['CertsPath']}/{hostname}.key"
        ca_path = f"{config['vault']['CertsPath']}/{hostname}.ca"

        # Create certs directory if it doesn't exist
        Path(config['vault']['CertsPath']).mkdir(parents=True, exist_ok=True)

        with open(cert_path, 'w') as f:
            f.write(cert['certificate'])
        
        with open(key_path, 'w') as f:
            f.write(cert['private_key'])

        with open(ca_path, 'w') as f:
            f.write(servers_ca)

        logger.info('Client registered successfully')

        # Update config 
        config['global']['registered'] = 'True'
        with open('config/config.ini', 'w') as configfile:
            config.write(configfile)

    # Init grpc connection
    grpc = GrpcConnector(
        host=config['grpc']['Host'],
        port=config['grpc']['Port'],
        cert=f"{config['vault']['CertsPath']}/{hostname}.crt",
        key=f"{config['vault']['CertsPath']}/{hostname}.key",
        ca=f"{config['vault']['CertsPath']}/{hostname}.ca"
    )

    # Connect to the server
    stub = grpc.connect()

    # Display the welcome message
    screen.clear_and_write('Welcome to Presentium!')

    for a in stub.EnterEventBus(serializer.EnterRequest()):
        print(a)