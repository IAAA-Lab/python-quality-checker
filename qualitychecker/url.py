"""Exposes usefull functions to check URL's quality aspects."""

from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.error import URLError, HTTPError
from ssl import create_default_context, CERT_NONE, SSLError
import re

try:
    from magic import Magic, MAGIC_MIME_TYPE  # pip install filemagic==1.6

    LIB_MAGIC = True
except ImportError:
    from winmagic import magic  # pip install python-magic-win64

    LIB_MAGIC = False


class URL:
    """Hold information about a remote resource identified by a URL."""

    def __init__(self, uri, offline=False, timeout=2 * 60):
        """Create a new URL object and process the future required information.

        Keyword Arguments:
        -----------------
        uri -- The URI of the resource
        offline -- Tells the object to avoid accesing the URI.
                    Mostly used for dev purposes

        Attention:
        ---------
        It tries to access the resource on creation so avoid
        multiple instanciations.

        """
        self.uri = uri
        self.accessibility = None
        self.type = None
        self._timeout = timeout

        self._checkValid()

        if offline:
            return

        self._checkOnline()

    def isValid(self):
        """Return a boolean telling if the URI is well formed."""
        return self.valid

    def isAccesible(self):
        """Return a ~qualitychecker.URL.AccessInfo object.

        The object evaluates as True if the resource is available
        and as False if it is not. It also contains the relevant information
        about the accesibility of the URI.
        """
        return self.accessibility

    def getAccessibility(self):
        """Return a ~qualitychecker.URL.AccessInfo object.

        It contains the relevant information about the accesibility of the URI.
        It also evaluates as True if the resource is available and as False if
        it is not.
        """
        return self.isAccesible()

    def getType(self):
        """Return a ~qualitychecker.URL.TypeInfo or None if resource not found.

        It contains the relevant information about the type of the resource if
        it is available.
        """
        return self.type

    def _checkValid(self):
        self.valid = pattern.match(self.uri)

    def _checkOnline(self, ssl=True):
        try:
            self._download(ssl=ssl)
        except HTTPError as e:
            self.accessibility = AccessInfo(
                status=e.code, reason=e.reason, accesible=False
            )
        except URLError as e:
            if type(e.reason) is SSLError and ssl is True:
                self._checkOnline(ssl=False)
            else:
                self.accessibility = AccessInfo(
                    status=None, reason=e.reason, accesible=False
                )
        except Exception as e:
            self.accessibility = AccessInfo(
                status=None, reason=e, accesible=False
            )

    def _download(self, ssl):

        ctx = create_default_context()
        if not ssl:
            ctx.check_hostname = False
            ctx.verify_mode = CERT_NONE

        with urlopen(
            self.uri, timeout=self._timeout, context=ctx
        ) as connection:
            head = connection.read(1024)
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

            if LIB_MAGIC:
                with Magic(flags=MAGIC_MIME_TYPE) as m:
                    magicType = m.id_buffer(head)
            else:
                magicType = magic.from_buffer(head)

            self.type = TypeInfo(
                magic=magicType,
                http=connection.getheader("content-type"),
                extension=extension,
            )

    def __str__(self):
        """Serialices object to CSV/TSV."""
        return "\t".join([self.uri, str(self.accessibility), str(self.type)])


class TypeInfo:
    """Contains information about the type of the resource.

    Attributes:
    ----------
    magic -- The type based on the actual resource content
    http -- The type based on the HTTP header 'Content-Type'
    extension -- The type based on the file extension's name

    """

    def __init__(self, magic, http, extension):
        """Create a new TypeInfo object.

        Keyword Arguments:
        -----------------
        magic -- The type based on the actual resource content
        http -- The type based on the HTTP header 'Content-Type'
        extension -- The type based on the file extension's name

        """
        self.magic = magic
        self.http = http
        self.extension = extension

    def __str__(self):
        """Serialices object to CSV/TSV."""
        return "\t".join([self.magic, self.http, self.extension])


class AccessInfo:
    """Contains information about the accesibility of the resource.

    Attributes:
    ----------
    status -- The HTTP status sent by the server. Can be None.
    reason -- The reason that caused an error (if error).
    isAccesible -- Boolean that tells if the resource is accesible
    sslError -- Boolean that tells if there was a problem with SSL

    """

    def __init__(
        self, status=None, reason="ok", accesible=True, ssl_error=False
    ):
        """Create a new AccessInfo object.

        Keyword Arguments:
        -----------------
        status -- The HTTP status sent by the server. Can be None.
        reason -- The reason that caused an error (if error).
        isAccesible -- Boolean that tells if the resource is accesible
        sslError -- Boolean that tells if there was a problem with SSL

        """
        self.status = status
        self.reason = reason
        self.isAccesible = accesible
        self.sslError = ssl_error

    def __str__(self):
        """Serialices object to CSV/TSV."""
        return "\t".join(
            [
                str(self.status),
                self.reason,
                str(self.isAccesible),
                str(self.sslError),
            ]
        )

    def __bool__(self):
        """Allow to evaluate the whole object as a boolean.

        Example:
        -------
        >>> info = AccessInfo(accesible=False)
        >>> if (info):
        >>>     print('YES')
        >>> else:
        >>>     print('NO')
        NO

        """
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
