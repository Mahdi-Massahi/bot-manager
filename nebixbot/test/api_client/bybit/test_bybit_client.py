import unittest
import hmac

from nebixbot.api_client.bybit.client import BybitClient


def calculate_sha256_hash(text, secret):
    """Calculates SHA256 Hash of a string"""
    return str(
        hmac.new(
            bytes(secret, "utf-8"),
            bytes(text, "utf-8"),
            digestmod="sha256",
        ).hexdigest()
    )


def create_query(params):
    """Creates query string from parameters"""
    return (
        "&".join(
            [
                f"{str(k)}={str(v)}"
                for k, v in sorted(params.items())
                if v is not None
            ]
        )
    )


class TestBybitClient(unittest.TestCase):
    """Tests for BybitClient class"""

    def setUp(self):
        """setup before running tests"""
        self.is_testnet = True
        self.secret = 'secret'
        self.api_key = 'api_key'
        self.timeout = 1
        self.client = BybitClient(
            is_testnet=self.is_testnet,
            secret=self.secret,
            api_key=self.api_key,
            req_timeout=self.timeout,
        )

    def test_client_init(self):
        """Test client is initialized correctly"""

        with self.assertRaises(TypeError) as context:
            BybitClient()
            BybitClient(None)
            BybitClient(None, None, None, None)

    def test_get_signature_empty_params(self):
        """Test get_signature method for empty params"""

        params = {}
        sign = self.client.get_signature(params)
        expected_sign = calculate_sha256_hash('', self.secret)

        self.assertEqual(sign, expected_sign)

    def test_get_signature_one_param(self):
        """Test get_signature method for one parameter"""

        params = {'test': 'test'}
        sign = self.client.get_signature(params)
        expected_sign = calculate_sha256_hash(create_query(params), self.secret)

        self.assertEqual(sign, expected_sign)

    def test_get_signature_sample_params(self):
        """Test get_signature method for few parameters"""

        params = {'test1': 'test1', 'test2': 'test2', 'test3': "test3"}
        sign = self.client.get_signature(params)
        expected_sign = calculate_sha256_hash(create_query(params), self.secret)

        self.assertEqual(sign, expected_sign)

    def test_create_query_url_empty(self):
        """Test create_query_url method with empty url and params"""

        params = {}
        url = ''
        query_url = self.client.create_query_url(url, params)
        expected = ''

        self.assertEqual(query_url, expected)

    def test_create_query_url_empty_params(self):
        """Test create_query_url method with empty params"""

        params = {}
        url = 'https://duckduckgo.com'
        query_url = self.client.create_query_url(url, params)
        expected = url + '?' + create_query(params)

        self.assertEqual(query_url, expected)

    def test_create_query_url_empty_url(self):
        """Test create_query_url method with empty url"""

        params = {'test': '1234'}
        url = ''
        query_url = self.client.create_query_url(url, params)
        expected = ''

        self.assertEqual(query_url, expected)

    def test_create_query_url(self):
        """Test create_query_url method with empty url"""

        params = {'test': '1234'}
        url = 'https://duckduckgo.com'
        query_url = self.client.create_query_url(url, params)
        expected = 'https://duckduckgo.com?test=1234'

        self.assertEqual(query_url, expected)
