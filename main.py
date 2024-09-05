import configparser
import logging
from pathlib import Path
import platform
import sys
import grpc
import time
import threading
import json

import presentium_pb2 as serializer
import presentium_pb2_grpc as grpc_lib

from src.Vault import Vault
from src.GrpcConnector import GrpcConnector
from src.Reader import Reader
from src.Screen import Screen

logger = logging.getLogger(__name__)


def presence_check_logic(stub, session_id, screen, reader):
    while True:
        # Read the card
        screen.clear_and_write_lines(['Present your', 'card'])
        card_id = reader.read_id()

        if not card_id:
            logger.info('Presence check stopped')
            break

        # Log the presence
        logger.info(f'Student with card id {card_id} present for session id {session_id}')

        # Send the card id to the server
        stub.StudentPresence(serializer.PresenceStudent(session_id=session_id, card_id=card_id))

        logger.debug('Presence sent to server')

        # Change displayed message
        screen.clear_and_write_lines(['Welcome to', 'Presentium!'])

        # Wait before starting a new presence check
        time.sleep(0.7)

if __name__ == '__main__':
    # Load config from config.ini
    config = configparser.ConfigParser()
    config.read('config/config.ini')

    # Init logging
    logging.basicConfig(filename=config['logging']['File'], level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logger.info('Client started')

    # Get hostname
    hostname = platform.node()

    # Create instances of Screen and Reader
    screen = Screen()
    reader = Reader()

    # Check global status, are we registered?
    if not config['global'].getboolean('Registered'):
        # Wait for the registration cert path to appear
        screen.clear_and_write_lines(['Waiting for', 'registration...'])
        while not Path(f"{config['registration']['tokenpath']}/{config['registration']['tokenfile']}").exists():
            time.sleep(1)
            
        # Update hostname is case host got renamed in the meantime
        hostname = platform.node()
        
        screen.clear_and_write('Registering...')

        # If we're not registered, we need to register
        logger.info('Client not registered, registering...')

        # Read the token json file
        role_id = None
        secret_id = None
        with open(f"{config['registration']['tokenpath']}/{config['registration']['tokenfile']}", 'r') as f:
            token = json.load(f)
            role_id = token['role_id']
            secret_id = token['secret_id']

        # Register client
        vault = Vault(logger=logger, vault_addr=config['vault']['ServerUrl'])
        result = vault.authenticate(
            role_id=role_id,
            secret_id=secret_id
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
    screen.clear_and_write_lines(['Connected to', 'Presentium!'])

    presence_check = 0
    presence_thread = None

    for event in stub.EnterEventBus(serializer.EnterRequest()):
        # The BusEvent reponse contains a MessageType representing the type of message
        match event.type:
            # Keepalive event
            case serializer.BusEvent.KEEP_ALIVE:
                logger.debug('Keepalive event received')

            # EnrollStudent event
            case serializer.BusEvent.ENROLL_STUDENT:
                # If a presence check is in progress, we need to stop it
                if presence_check:
                    reader.stop()
                    presence_thread.join()
                    presence_check = 0
                    logger.info('Presence check stopped')

                student_id = event.enroll_student.student_id
                logger.info(f'Starting student enrollment for student id {student_id}')

                # Read the card
                screen.clear_and_write_lines(['Enroll your', 'card'])
                card_id = reader.read_id()

                # Send the card id to the server
                stub.StudentEnrolled(serializer.EnrolledStudent(student_id=student_id, card_id=card_id))

                logger.info(f'Student {student_id} enrolled successfully with card id {card_id}')

                # Change displayed message
                screen.clear_and_write_lines(['Enrollment', 'successful'])

            # PresenceCheck event
            case serializer.BusEvent.PRESENCE_CHECK:
                # If a presence check is in progress, we need to stop it
                if presence_check:
                    reader.stop()
                    presence_thread.join()
                    presence_check = 0
                    logger.info('Presence check stopped')

                session_id = event.presence_check.session_id
                presence_check = 1
                logger.info(f'Starting presence check with session id {session_id}')

                # Start the presence check logic in a new thread
                presence_thread = threading.Thread(target=presence_check_logic, args=(stub, session_id, screen, reader))

                # Change displayed message 
                screen.clear_and_write_lines(['Presence check', 'started'])

                # Start the thread
                time.sleep(0.5)
                presence_thread.start()

            # Default
            case _:
                logger.warn(f'Unknown event received {a}')
