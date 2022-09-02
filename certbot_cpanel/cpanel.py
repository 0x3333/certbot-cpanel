"""cPanel client"""

import logging
import base64
import json

try:
    # python 3
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode
except ImportError:
    # python 2
    from urllib import urlencode
    from urllib2 import urlopen, Request


from certbot import errors


logger = logging.getLogger(__name__)


class CPanelClient:
    """Encapsulate communications with the cPanel API 2"""
    def __init__(self, url, username, password, token):
        self.request_url = "%s/json-api/cpanel" % url
        self.data = {
            'cpanel_jsonapi_user': username,
            'cpanel_jsonapi_apiversion': '2',
        }

        if token:
            self.headers = {
                'Authorization': 'cpanel %s:%s' % (username, token)
            }
        else:
            self.headers = {
                'Authorization': 'Basic %s' % base64.b64encode(
                ("%s:%s" % (username, password)).encode()).decode('utf8')
            }

    def add_txt_record(self, record_name, record_content, record_ttl=60):
        """Add a TXT record
        :param str record_name: the domain name to add
        :param str record_content: the content of the TXT record to add
        :param int record_ttl: the TTL of the record to add
        """
        cpanel_zone, cpanel_name = self._get_zone_and_name(record_name)

        data = self.data.copy()
        data['cpanel_jsonapi_module'] = 'ZoneEdit'
        data['cpanel_jsonapi_func'] = 'add_zone_record'
        data['domain'] = cpanel_zone
        data['name'] = cpanel_name
        data['type'] = 'TXT'
        data['txtdata'] = record_content
        data['ttl'] = record_ttl

        response = urlopen(
            Request(
                "%s?%s" % (self.request_url, urlencode(data)),
                headers=self.headers,
            )
        )
        response_data = json.load(response)['cpanelresult']
        logger.debug(response_data)
        if response_data['data'][0]['result']['status'] == 1:
            logger.info("Successfully added TXT record for %s", record_name)
        else:
            raise errors.PluginError("Error adding TXT record: %s" % response_data['data'][0]['result']['statusmsg'])

    def del_txt_record(self, record_name, record_content, record_ttl=60):
        """Remove a TXT record
        :param str record_name: the domain name to remove
        :param str record_content: the content of the TXT record to remove
        :param int record_ttl: the TTL of the record to remove
        """
        cpanel_zone, _ = self._get_zone_and_name(record_name)

        record_lines = self._get_record_line(cpanel_zone, record_name, record_content, record_ttl)

        data = self.data.copy()
        data['cpanel_jsonapi_module'] = 'ZoneEdit'
        data['cpanel_jsonapi_func'] = 'remove_zone_record'
        data['domain'] = cpanel_zone

        # the lines get shifted when we remove one, so we reverse-sort to avoid that
        record_lines.sort(reverse=True)
        for record_line in record_lines:
            data['line'] = record_line

            response = urlopen(
                Request(
                    "%s?%s" % (self.request_url, urlencode(data)),
                    headers=self.headers
                )
            )
            response_data = json.load(response)['cpanelresult']
            logger.debug(response_data)
            if response_data['data'][0]['result']['status'] == 1:
                logger.info("Successfully removed TXT record for %s", record_name)
            else:
                raise errors.PluginError("Error removing TXT record: %s" % response_data['data'][0]['result']['statusmsg'])

    def install_crt(self, domain, cabundle, crt, key):
        """Install a certificate in a domain
        :param str domain: the domain to use the certificate
        :param str cabundle: the CA Bundle of the certificate
        :param str crt: the domain's certificate
        :param str key: the certificate's key
        """
        # cpanel_zone, cpanel_name = self._get_zone_and_name(record_name)

        data = self.data.copy()
        data['cpanel_jsonapi_module'] = 'SSL'
        data['cpanel_jsonapi_func'] = 'installssl'
        data['domain'] = domain
        data['cabundle'] = cabundle
        data['crt'] = crt
        data['key'] = key

        response = urlopen(
            Request(
                "%s?%s" % (self.request_url, urlencode(data)),
                headers=self.headers,
            )
        )
        response_data = json.load(response)['cpanelresult']
        logger.debug(response_data)
        if response_data['data'][0]['result'] == 1:
            logger.info("Successfully installed SSL certificate for %s", domain)
        else:
            msg = response_data
            if 'data' in response_data:
                if isinstance(response_data['data'], list):
                    if 'result' in response_data['data'][0]:
                        if 'output' in response_data['data'][0]['result']:
                            msg = ['data'][0]['result']['output']
                    elif 'output' in response_data['data'][0]:
                        msg = ['data'][0]['output']
            raise errors.PluginError("Error installing SSL certificate: %s" % msg)

    def _get_zone_and_name(self, record_domain):
        """Find a suitable zone for a domain
        :param str record_name: the domain name
        :returns: (the zone, the name in the zone)
        :rtype: tuple
        """
        cpanel_zone = ''
        cpanel_name = ''

        data = self.data.copy()
        data['cpanel_jsonapi_module'] = 'ZoneEdit'
        data['cpanel_jsonapi_func'] = 'fetchzones'

        response = urlopen(
            Request(
                "%s?%s" % (self.request_url, urlencode(data)),
                headers=self.headers
            )
        )
        response_data = json.load(response)['cpanelresult']
        logger.debug(response_data)
        matching_zones = {zone for zone in response_data['data'][0]['zones'] if response_data['data'][0]['zones'][zone] and (record_domain == zone or record_domain.endswith('.' + zone))}
        if matching_zones:
            cpanel_zone = max(matching_zones, key = len)
            cpanel_name = record_domain[:-len(cpanel_zone)-1]
        else:
            raise errors.PluginError("Could not get the zone for %s. Is this name in a zone managed in cPanel?" % record_domain)

        return (cpanel_zone, cpanel_name)

    def _get_record_line(self, cpanel_zone, record_name, record_content, record_ttl):
        """Find the line numbers of a record a zone
        :param str cpanel_zone: the zone of the record
        :param str record_name: the name in the zone of the record
        :param str record_content: the content of the record
        :param str cpanel_ttl: the ttl of the record
        :returns: the line number and all it's duplicates
        :rtype: list
        """
        record_lines = []

        data = self.data.copy()
        data['cpanel_jsonapi_module'] = 'ZoneEdit'
        data['cpanel_jsonapi_func'] = 'fetchzone_records'
        data['domain'] = cpanel_zone
        data['name'] = record_name + '.' if not record_name.endswith('.') else ''
        data['type'] = 'TXT'
        data['txtdata'] = record_content
        data['ttl'] = record_ttl

        response = urlopen(
            Request(
                "%s?%s" % (self.request_url, urlencode(data)),
                headers=self.headers
            )
        )
        response_data = json.load(response)['cpanelresult']
        logger.debug(response_data)
        record_lines = [int(d['line']) for d in response_data['data']]

        return record_lines
