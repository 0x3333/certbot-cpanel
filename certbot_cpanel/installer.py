"""cPanel installer plugin"""

from certbot_cpanel.cpanel import CPanelClient

import logging

import zope.interface

from certbot import errors
from certbot import interfaces
from certbot.plugins import common


logger = logging.getLogger(__name__)

@zope.interface.implementer(interfaces.IInstaller)
@zope.interface.provider(interfaces.IPluginFactory)
class Installer(common.Plugin):
    """cPanel installer plugin"""

    description = "Install a certificate in cPanel"

    def __init__(self, *args, **kwargs):
        super(Installer, self).__init__(*args, **kwargs)
        self.url = None
        self.username = None
        self.password = None
        self.token = None

    @classmethod
    def add_parser_arguments(cls, add): # pylint: disable=arguments-differ
        add("url", help="cPanel url, include the scheme and the port number (usually 2083 for https)")
        add("username", help="cPanel username")
        add("password", help="cPanel password")
        add("token", help="cPanel API token")

    def prepare(self):
        pass

    def more_info(self):
        return ""

    def get_all_names(self):
        pass

    def deploy_cert(self, domain, cert_path, key_path, chain_path, fullchain_path):
        """
        Upload Certificate to cPanel
        """

        if domain.startswith("*."):
            return
        cabundle = open(chain_path).read()
        crt = open(cert_path).read()
        key = open(key_path).read()

        # Upload cert to cPanel
        self._get_cpanel_client().install_crt(domain, cabundle, crt, key)

    def enhance(self, domain, enhancement, options=None):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def supported_enhancements(self):  # pylint: disable=missing-docstring,no-self-use
        return []  # pragma: no cover

    def get_all_certs_keys(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def save(self, title=None, temporary=False):  # pylint: disable=no-self-use
        pass  # pragma: no cover

    def rollback_checkpoints(self, rollback=1):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def recovery_routine(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def view_config_changes(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def config_test(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def restart(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def renew_deploy(self, lineage, *args, **kwargs): # pylint: disable=missing-docstring,no-self-use
        """
        Renew certificates when calling `certbot renew`
        """

        # Run deploy_cert with the lineage params
        self.deploy_cert(lineage.names()[0], lineage.cert_path, lineage.key_path, lineage.chain_path, lineage.fullchain_path)

        return

    def _get_cpanel_client(self):
        self.url = self.conf('url') 
        self.username = self.conf('username') 
        self.password = self.conf('password') 
        self.token = self.conf('token') 

        if not self.url:
            raise errors.PluginError('cPanel: url is required')
        if not self.username:
            raise errors.PluginError('cPanel: username is required')
        if not self.password and not self.token:
            raise errors.PluginError('cPanel: password or token is required')

        return CPanelClient(
            self.url,
            self.username,
            self.password if not self.token else None,
            self.token if self.token else None,
        )


interfaces.RenewDeployer.register(Installer)
