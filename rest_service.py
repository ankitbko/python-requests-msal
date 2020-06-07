import requests


class RestService(object):
    def __init__(self, headers={}, auth_provider=None):
        # https://realpython.com/python-requests/#authentication
        self.auth_provider = auth_provider
        self.baseHeaders = headers

    def get(self, url, params={}, headers={}):
        # TODO Perform Logging of both request parameters and response before returning it.
        # ensure auth token is not in the logs.
        return requests.get(
            url=url,
            params=params,
            headers=self.__accumulateHeaders(headers),
            auth=self.auth_provider,
            verify=False
        )

    def post(self, url, body, headers={}):
        # TODO Perform Logging of both request parameters and response before returning it.
        # ensure auth token is not in the logs.
        return requests.post(
            url=url,
            data=body,
            headers=self.__accumulateHeaders(headers),
            auth=self.auth_provider,
            verify=False
        )

    def put(self, url, params={}, headers={}):
        # TODO Perform Logging of both request parameters and response before returning it.
        # ensure auth token is not in the logs.
        return requests.get(
            url=url,
            params=params,
            headers=self.__accumulateHeaders(headers),
            auth=self.auth_provider,
            verify=False
        )

    def __accumulateHeaders(self, headers):
        return {**self.baseHeaders, **headers}
