from citybikesdata.extract import get_networks, get_stations_for


class Testextract:

    API_URL = "https://api.citybik.es/v2/networks"

    def test_get_networks(self):
        r = get_networks()
        assert type(r) == type({})

    def test_get_stations_for(self):
        r = get_stations_for("fortworth")
        assert type(r) == type({})
