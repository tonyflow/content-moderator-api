import unittest

from router import *
from fastapi.testclient import TestClient

client = TestClient(content_moderator)


@unittest.skip(reason='The serverless Koala Classifier is not always online')
def test_router_classify():
    expected_json = [[{"label": "OK", "score": 0.965565025806427}, {"label": "H", "score": 0.0160847008228302},
                      {"label": "SH", "score": 0.00591418519616127}, {"label": "HR", "score": 0.002983012003824115},
                      {"label": "V", "score": 0.0028166065458208323}, {"label": "S", "score": 0.0022672933991998434},
                      {"label": "V2", "score": 0.001755744218826294}, {"label": "S3", "score": 0.0015976601280272007},
                      {"label": "H2", "score": 0.0010157079668715596}]]
    response = client.get("/classify?message=I love all people")
    assert response.status_code == 200
    assert response.json() == expected_json
