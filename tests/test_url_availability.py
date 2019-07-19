from qualitychecker import URL

# pylama:ignore=E501

available_urls = [
    ("http://google.com", False),
    ("http://datos.gob.es", True),
    (
        "http://servicios.ine.es/wstempus/js/es/DATOS_TABLA/t37/p198/p01/serie/02002.px?tip=AM",
        False,
    ),
    ("http://www.ine.es/jaxiT3/Tabla.htm?t=24357", False),
    (
        "http://www.boa.aragon.es/cgi-bin/EBOA/BRSCGI?CMD=VERLST&OUTPUTMODE=XML&BASE=BOLE&DOCS=1-10000&SEC=OPENDATABOAXML&SORT=-PUBL&SEPARADOR=&MATE-C=04LIC",
        False,
    ),
    (
        "https://opendata.aragon.es/sparql?default-graph-uri=&query=select+distinct+%3Fobs+%3Fx+%3Fy+where+%7B%0D%0A+%3Fobs+%3Chttp%3A%2F%2Fpurl.org%2Flinked-data%2Fsdmx%2F2009%2Fdimension%23refArea%3E+%3Chttp%3A%2F%2Fopendata.aragon.es%2Frecurso%2Fterritorio%2FMunicipio%2FPiedratajada%3E+.%0D%0A+%3Fobs+%3Fx+%3Fy++.%0D%0A%7D+%0D%0AORDER+BY+%3Fobs&format=text%2Fcsv&timeout=0&debug=on",
        False,
    ),
]


def test_available_urls():
    for (url, ssl) in available_urls:
        connection = URL(url)
        assert connection.isAccesible()
        accessibility = connection.getAccessibility()
        assert connection.isAccesible() is accessibility
        assert accessibility.sslError == ssl


unavailable_urls = [
    (
        "http://piuhwpeognpiapondguawehgnonb.es",
        None,
        "[Errno -2] Name or service not known",
        False,
    ),
    ("https://google.com/aerpvqiwuegadsfgpaibv", 404, "Not Found", False),
    (
        "https://opendata.aragon.es/sparql?default-graph-uri=&query=select+distinct+%3Fobs+%3Fx+%3Fy+where+%7B%0D%0A+%3Fobs+%3Chttp%3A%2F%2Fpurl.org%2Flinked-data%2Fsdmx%2F2009%2Fdimension%23refArea%3E+%3Chttp%3A%2F",
        400,
        "Bad Request",
        False,
    ),
]


def test_unavailable_urls():
    for (url, status, reason, ssl) in unavailable_urls:
        connection = URL(url)
        assert not connection.isAccesible()
        accessibility = connection.getAccessibility()
        assert connection.isAccesible() is accessibility
        assert accessibility.status == status
        assert str(accessibility.reason) == reason
        assert accessibility.sslError == ssl
