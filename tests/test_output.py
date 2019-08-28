from qualitychecker import URL

# pylama:ignore=E501


def test_dict_output_offline():
    d = URL("https://google.es").dict()

    assert d["uri"] == "https://google.es"
    assert d["validity"] == "True"
    assert d["accessibility_status"] == "200"
    assert d["accessibility_reason"] == "OK"
    assert d["accessibility_isAccesible"] == "True"
    assert d["accessibility_sslError"] == "False"
    assert "/html" in d["type_magic"]
    assert "/html" in d["type_http"]
    assert "/" in d["type_extension"]


snapshot = [
    "https://google.es",
    "True",
    "200",
    "OK",
    "True",
    "False",
    "text/html",
    "text/html; charset=ISO-8859-1",
    "/",
]


def test_string_output_offline():
    s = str(URL("https://google.es"))
    assert s.split("\t") == snapshot
    assert s == "\t".join(snapshot)
