import unittest
import pytest
import requests
from datetime import datetime
from iss_tracker import calculate_speed, closest_datapoint_to_now, epoch_speed, extract_state_vector, get_location_info

class TestISSFunctions(unittest.TestCase):

    def test_calculate_speed(self):
        self.assertAlmostEqual(calculate_speed(1, 1, 1), math.sqrt(3))
        self.assertAlmostEqual(calculate_speed(0, 0, 0), 0)
        self.assertAlmostEqual(calculate_speed(-1, -1, -1), math.sqrt(3))

    def test_extract_state_vector(self):
        xml_data = b"<?xml version='1.0' encoding='UTF-8'?><ndm><oem><body><segment><data><stateVector><EPOCH>2022-079T00:00:00</EPOCH><X><#text>749126.243160</#text></X><Y><#text>-5412435.309520</#text></Y><Z><#text>3192557.216550</#text></Z><X_DOT><#text>-4902.996370</#text></X_DOT><Y_DOT><#text>-1316.783860</#text></Y_DOT><Z_DOT><#text>-5499.482510</#text></Z_DOT></stateVector></data></segment></body></oem></ndm>"
        state_vector = extract_state_vector(xml_data)
        self.assertEqual(len(state_vector), 1)
        self.assertEqual(state_vector[0]["EPOCH"], "2022-079T00:00:00")

    def test_get_location_info(self):
        fetch_iss_data = MagicMock(return_value=b"<?xml version='1.0' encoding='UTF-8'?><ndm><oem><body><segment><data><stateVector><EPOCH>2022-079T00:00:00</EPOCH><X><#text>749126.243160</#text></X><Y><#text>-5412435.309520</#text></Y><Z><#text>3192557.216550</#text></Z><X_DOT><#text>-4902.996370</#text></X_DOT><Y_DOT><#text>-1316.783860</#text></Y_DOT><Z_DOT><#text>-5499.482510</#text></Z_DOT></stateVector></data></segment></body></oem></ndm>")
        result = get_location_info("2022-079T00:00:00")
        self.assertEqual(result["latitude"], 35.62370813568754)
        self.assertEqual(result["longitude"], 138.75426895095042)
        self.assertEqual(result["altitude"], 423.0106091993142)

    def test_epoch_speed(self):
        fetch_iss_data = MagicMock(return_value=b"<?xml version='1.0' encoding='UTF-8'?><ndm><oem><body><segment><data><stateVector><EPOCH>2022-079T00:00:00</EPOCH><X><#text>749126.243160</#text></X><Y><#text>-5412435.309520</#text></Y><Z><#text>3192557.216550</#text></Z><X_DOT><#text>-4902.996370</#text></X_DOT><Y_DOT><#text>-1316.783860</#text></Y_DOT><Z_DOT><#text>-5499.482510</#text></Z_DOT></stateVector></data></segment></body></oem></ndm>")
        result = epoch_speed("2022-079T00:00:00")
        self.assertEqual(result, "6600.981901714359")

    def test_closest_datapoint_to_now(self):
        fetch_iss_data = MagicMock(return_value=b"<?xml version='1.0' encoding='UTF-8'?><ndm><oem><body><segment><data><stateVector><EPOCH>2022-079T00:00:00</EPOCH><X><#text>749126.243160</#text></X><Y><#text>-5412435.309520</#text></Y><Z><#text>3192557.216550</#text></Z><X_DOT><#text>-4902.996370</#text></X_DOT><Y_DOT><#text>-1316.783860</#text></Y_DOT><Z_DOT><#text>-5499.482510</#text></Z_DOT></stateVector></data></segment></body></oem></ndm>")
        current_date_and_time = datetime.strptime("2022-03-20 12:30:00", "%Y-%m-%d %H:%M:%S")
        result = closest_datapoint_to_now(fetch_iss_data(), current_date_and_time)
        self.assertEqual(result, 0)

class TestISSRoutes(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_get_epochs(self):
        response = self.app.get('/epochs')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_comment(self):
        response = self.app.get('/comment')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, str)

    def test_get_header(self):
        response = self.app.get('/header')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, dict)

    def test_get_metadata(self):
        response = self.app.get('/metadata')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, str)

    def test_get_specific_epoch(self):
        response = self.app.get('/epochs/2022-079T00:00:00')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, dict)

    def test_get_epoch_speed(self):
        response = self.app.get('/epochs/2022-079T00:00:00/speed')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, dict)
        self.assertIn('speed', response.json)

    def test_get_epoch_location(self):
        response = self.app.get('/epochs/2022-079T00:00:00/location')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, dict)
        self.assertIn('latitude', response.json)
        self.assertIn('longitude', response.json)
        self.assertIn('altitude', response.json)
        self.assertIn('geolocation', response.json)

    def test_get_now_info(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2022, 3, 20, 12, 30, 0)
        response = self.app.get('/now')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, dict)
        self.assertIn('instantaneous_speed', response.json)
        self.assertIn('latitude', response.json)
        self.assertIn('longitude', response.json)
        self.assertIn('altitude', response.json)
        self.assertIn('geolocation', response.json)

if __name__ == '__main__':
    unittest.main()


