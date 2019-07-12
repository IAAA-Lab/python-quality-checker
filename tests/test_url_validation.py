from qualitychecker import URL

# pylama:ignore=E501


valid_urls = [
    "http://hello.world",
    "https://hello.world",
    "ftp://hello.world",
    "http://hello1.world",
    "http://hello.world:80808/",
    "http://hello.world:8080/#a",
    "https://me@sub.hello.world:8080/the/path?q=a#header",
]


def test_valid_urls():
    for url in valid_urls:
        assert URL(url, offline=True).isValid()


invalid_urls = [
    "htt://hello.world",
    "fttp://hello.world",
    "http://hello.world:",
    "http://hello.world:808080",
    "http://hello.world1",
]


def test_right_url_complicated_schema():
    for url in invalid_urls:
        assert not URL(url, offline=True).isValid()
