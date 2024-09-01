import hvac

class Vault:
    def __init__(self, logger, vault_addr):
        self.logger = logger
        self.client = hvac.Client(url=vault_addr)

    def authenticate(self, client_cert_path: str, client_key_path: str) -> bool:
        try:
            self.client = hvac.Client(url=self.client.url, cert=(client_cert_path, client_key_path))
            self.client.auth.cert.login(name='registration-cert', mount_point='registration_cert')
        except Exception as e:
            self.logger.error(f'Error authenticating with Vault: {e}')
        
        return self.client.is_authenticated()

    def logout(self) -> None:
        self.client.client.logout()

    def get_servers_ca(self, mount_point: str, issuer_id: str) -> str:
        cert = self.client.secrets.pki.read_issuer(issuer_id, mount_point)
        return cert['data']['certificate']

    def generate_device_cert(self, role_name: str, mount_point: str, hostname: str) -> str:
        generate_certificate_response = self.client.secrets.pki.generate_certificate(
            name=role_name,
            mount_point=mount_point,
            common_name=f'{hostname}.devices.presentium.ch'
        )
        self.logger.info(f'Generated certificate for {hostname}')
        return generate_certificate_response['data']