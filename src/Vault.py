import hvac
import requests

class Vault:
    def __init__(self, logger, vault_addr):
        self.logger = logger
        self.client = hvac.Client(url=vault_addr)

    def authenticate(self, role_id: str, secret_id: str) -> bool:
        try:
            self.client = hvac.Client(url=self.client.url)
            self.client.auth.approle.login(
                mount_point='registration',
                role_id=role_id,
                secret_id=secret_id
            )
        except Exception as e:
            self.logger.error(f'Error authenticating with Vault: {e}')
        
        return self.client.is_authenticated()

    def logout(self) -> None:
        self.client.client.logout()

    def get_servers_ca(self, mount_point: str, issuer_id: str) -> str:
        cert = requests.get(f'{self.client.url}/v1/{mount_point}/issuer/{issuer_id}/json').json()
        return cert['data']['certificate']

    def generate_device_cert(self, role_name: str, mount_point: str, hostname: str) -> str:
        generate_certificate_response = self.client.secrets.pki.generate_certificate(
            name=role_name,
            mount_point=mount_point,
            common_name=f'{hostname}.devices.presentium.ch'
        )
        self.logger.info(f'Generated certificate for {hostname}')
        return generate_certificate_response['data']