"""cPanel dns-01 authenticator plugin"""

import logging

from certbot_cpanel.cpanel import CPanelClient

import zope.interface

from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common


logger = logging.getLogger(__name__)

@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """cPanel dns-01 authenticator plugin"""

    description = "Obtain a certificate using a DNS TXT record in cPanel"

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.url = None
        self.username = None
        self.password = None
        self.token = None

    @classmethod
    def add_parser_arguments(cls, add): # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=10)
        add("url", help="cPanel url, include the scheme and the port number (usually 2083 for https)")
        add("username", help="cPanel username")
        add("password", help="cPanel password")
        add("token", help="cPanel API token")

    def more_info(self): # pylint: disable=missing-docstring
        return self.description

    def _perform(self, domain, validation_domain_name, validation):
        self._get_cpanel_client().add_txt_record(validation_domain_name, validation)

    def _cleanup(self, domain, validation_domain_name, validation):
        self._get_cpanel_client().del_txt_record(validation_domain_name, validation)

    def _setup_credentials(self):
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

    def _get_cpanel_client(self):
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
