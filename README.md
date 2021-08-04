# certbot-cpanel

Plugin to allow acme dns-01 authentication and installation of a domain name managed in cPanel. Useful for automating, creating and installing a Let's Encrypt certificate (wildcard or not) for a service with a name managed by cPanel.

## Named Arguments
| Argument | Description |
| --- | --- |
| --certbot-cpanel:auth-url &lt;str&gt; | cPanel URL **(required)** |
| --certbot-cpanel:auth-username &lt;str&gt; | cPanel username **(required)** |
| --certbot-cpanel:auth-password &lt;str&gt; | cPanel password |
| --certbot-cpanel:auth-token &lt;str&gt; | cPanel token |
| --certbot-cpanel:auth-propagation-seconds &lt;seconds&gt; | The number of seconds to wait for DNS to propagate before asking the ACME server to verify the DNS record (Default: 30) |
| --certbot-cpanel:install-url &lt;str&gt; | cPanel URL **(required)** |
| --certbot-cpanel:install-username &lt;str&gt; | cPanel username **(required)** |
| --certbot-cpanel:install-password &lt;str&gt; | cPanel password |
| --certbot-cpanel:install-token &lt;str&gt; | cPanel token |

## Install
``` bash
python setup.py install
```

## Credentials
The credentials are passed by argument. You have 2 sets of arguments, one for domain authentication and another one for certificate installation(This allows you to authenticate in a server and install in another).

The password and token are mutually exclusive.

## Example
You can now run certbot using the plugin and feeding the credentials.
For example, to get a wildcard certificate for *.example.com and example.com and install:
``` bash
certbot certonly \
  -a certbot-cpanel:auth \
  --certbot-cpanel:auth-url "https://cpanel.example.com:2083" \
  --certbot-cpanel:auth-username "myusername" \
  --certbot-cpanel:auth-token "5jkc9jr0o6q9EIuCn67ew9uFR31XHRZI" \
  -d 'example.com' \
  -d '*.example.com'
```

You can also specify a installer plugin with the `-i` option.
``` bash
certbot run \
  -a certbot-cpanel:auth \
  --certbot-cpanel:auth-url "https://cpanel.example.com:2083" \
  --certbot-cpanel:auth-username "myusername" \
  --certbot-cpanel:auth-token "5jkc9jr0o6q9EIuCn67ew9uFR31XHRZI" \
  -i certbot-cpanel:install \
  --certbot-cpanel:install-url "https://cpanel.example.com:2083" \
  --certbot-cpanel:install-username "myusername" \
  --certbot-cpanel:install-token "5jkc9jr0o6q9EIuCn67ew9uFR31XHRZI" \
  -d 'example.com' \
  -d '*.example.com'
```

## Docker
You can build a docker image:

```bash
docker build --network host -t 0x3333/certbot-cpanel:latest .
```

And use the image:

```bash
docker run --rm -it \
  -v $PWD/log:/var/log/letsencrypt \
  -v $PWD/etc:/etc/letsencrypt \
  0x3333/certbot-cpanel:latest \
    certbot certonly \
    -a certbot-cpanel:auth \
    --certbot-cpanel:auth-url "https://cpanel.example.com:2083" \
    --certbot-cpanel:auth-username "myusername" \
    --certbot-cpanel:auth-token "5jkc9jr0o6q9EIuCn67ew9uFR31XHRZI" \
    -d 'example.com' \
    -d '*.example.com'
```

## Additional documentation
* https://documentation.cpanel.net/display/DD/Guide+to+cPanel+API+2
* https://certbot.eff.org/docs/


## About this Fork

This fork has modified the original `certbot-dns-cpanel` to add the install option.
