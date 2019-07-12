from qualitychecker import URL

# pylama:ignore=E501

csv_urls = [
    "https://data.cityofnewyork.us/api/views/kku6-nxdu/rows.csv?accessType=DOWNLOAD",
    "http://datos.gob.es/apidata/catalog/dataset/a16003011-gasto-interno-en-id-en-la-c-a-de-euskadi-por-sector-de-ejecucion-y-territorio-historico-segun-el-origen-de-los-fondos-miles-de-euros3.csv",
]


def test_csv():
    for url in csv_urls:
        obj = URL(url)
        type = obj.getType()
        assert type.magic == "text/csv" or type.magic == "text/plain"
        assert "/csv" in type.http
        assert type.extension == "csv"


xml_urls = [
    "http://datos.gob.es/apidata/catalog/dataset/a16003011-gasto-interno-en-id-en-la-c-a-de-euskadi-por-sector-de-ejecucion-y-territorio-historico-segun-el-origen-de-los-fondos-miles-de-euros3.xml"
]


def test_xml():
    for url in xml_urls:
        obj = URL(url)
        type = obj.getType()
        assert type.magic == "text/xml"
        assert "/xml" in type.http
        assert type.extension == "xml"
