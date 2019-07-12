"""Exposes usefull functions to check URL's quality aspects."""

from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.error import URLError, HTTPError
from ssl import create_default_context, CERT_NONE, SSLError
from magic import Magic, MAGIC_MIME_TYPE  # pip install filemagic==1.6
import re


class URL:
    def __init__(self, uri, offline=False):
        self.uri = uri
        self.head = None
        self.accessibility = None
        self.type = None

        self._checkValid()

        if offline:
            return

        self._checkOnline()

    def isValid(self):
        return self.valid

    def isAccesible(self):
        return self.accessibility

    def getAccessibility(self):
        return self.isAccesible()

    def getType(self):
        return self.type

    def _checkValid(self):
        self.valid = pattern.match(self.uri)

    def _checkOnline(self):
        try:
            self._download()
        except HTTPError as e:
            self.accessibility = AccessInfo(
                status=e.code, reason=e.reason, accesible=False
            )
        except URLError as e:
            if type(e.reason) is SSLError:
                self._download(ssl=False)
            else:
                self.accessibility = AccessInfo(
                    status=None, reason=e.reason, accesible=False
                )

    def _download(self, ssl=True):

        ctx = create_default_context()
        if not ssl:
            ctx.check_hostname = False
            ctx.verify_mode = CERT_NONE

        with urlopen(self.uri, context=ctx) as connection:
            self.head = connection.read(1024)
            self.accessibility = AccessInfo(
                status=connection.status,
                reason=connection.reason,
                ssl_error=not ssl,
            )

            extension = None
            filename = connection.getheader("content-disposition")
            if filename:
                extension = filename.split(".")[-1]
            else:
                path = urlparse(connection.url).path
                extension = path.split(".")[-1]

            with Magic(flags=MAGIC_MIME_TYPE) as m:
                self.type = TypeInfo(
                    magic=m.id_buffer(self.head),
                    http=connection.getheader("content-type"),
                    extension=extension,
                )


class TypeInfo:
    def __init__(self, magic, http, extension):
        self.magic = magic
        self.http = http
        self.extension = extension


class AccessInfo:
    def __init__(
        self, status=None, reason="ok", accesible=True, ssl_error=False
    ):
        self.status = status
        self.reason = reason
        self.isAccesible = accesible
        self.sslError = ssl_error

    def __bool__(self):
        return self.isAccesible


ip_middle_octet = r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5]))"
ip_last_octet = r"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"

regex = re.compile(  # noqa: W605
    r"^"
    # protocol identifier
    r"(?:(?:https?|ftp)://)"
    # user:pass authentication
    r"(?:[-a-z\u00a1-\uffff0-9._~%!$&'()*+,;=:]+"
    r"(?::[-a-z0-9._~%!$&'()*+,;=:]*)?@)?"
    r"(?:"
    r"(?P<private_ip>"
    # IP address exclusion
    # private & local networks
    r"(?:(?:10|127)" + ip_middle_octet + r"{2}" + ip_last_octet + r")|"
    r"(?:(?:169\.254|192\.168)" + ip_middle_octet + ip_last_octet + r")|"
    r"(?:172\.(?:1[6-9]|2\d|3[0-1])" + ip_middle_octet + ip_last_octet + r"))"
    r"|"
    # private & local hosts
    r"(?P<private_host>" r"(?:localhost))" r"|"
    # IP address dotted notation octets
    # excludes loopback network 0.0.0.0
    # excludes reserved space >= 224.0.0.0
    # excludes network & broadcast addresses
    # (first & last IP address of each class)
    r"(?P<public_ip>"
    r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    r"" + ip_middle_octet + r"{2}"
    r"" + ip_last_octet + r")"
    r"|"
    # IPv6 RegEx from https://stackoverflow.com/a/17871737
    r"\[("
    # 1:2:3:4:5:6:7:8
    r"([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|"
    # 1::                              1:2:3:4:5:6:7::
    r"([0-9a-fA-F]{1,4}:){1,7}:|"
    # 1::8             1:2:3:4:5:6::8  1:2:3:4:5:6::8
    r"([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|"
    # 1::7:8           1:2:3:4:5::7:8  1:2:3:4:5::8
    r"([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|"
    # 1::6:7:8         1:2:3:4::6:7:8  1:2:3:4::8
    r"([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|"
    # 1::5:6:7:8       1:2:3::5:6:7:8  1:2:3::8
    r"([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|"
    # 1::4:5:6:7:8     1:2::4:5:6:7:8  1:2::8
    r"([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|"
    # 1::3:4:5:6:7:8   1::3:4:5:6:7:8  1::8
    r"[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|"
    # ::2:3:4:5:6:7:8  ::2:3:4:5:6:7:8 ::8       ::
    r":((:[0-9a-fA-F]{1,4}){1,7}|:)|"
    # fe80::7:8%eth0   fe80::7:8%1
    # (link-local IPv6 addresses with zone index)
    r"fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|"
    r"::(ffff(:0{1,4}){0,1}:){0,1}"
    r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    # ::255.255.255.255   ::ffff:255.255.255.255  ::ffff:0:255.255.255.255
    # (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
    r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|"
    r"([0-9a-fA-F]{1,4}:){1,4}:"
    r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33
    # (IPv4-Embedded IPv6 Address)
    r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])" r")\]|"
    # host name
    u"(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)"
    # domain name
    u"(?:\\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*"
    # TLD identifier
    u"(?:\\.(?:[a-z\u00a1-\uffff]{2,}))" r")"
    # port number
    r"(?::\d{2,5})?"
    # resource path
    u"(?:/[-a-z\u00a1-\uffff0-9._~%!$&'()*+,;=:@/]*)?"
    # query string
    r"(?:\?\S*)?"
    # fragment
    r"(?:#\S*)?" r"$",
    re.UNICODE | re.IGNORECASE,
)

pattern = re.compile(regex)
