from qualitychecker import URL

# pylama:ignore=E501

available_urls = [("http://google.com", False), ("http://datos.gob.es", True)]


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
