import requests
from requests.auth import AuthBase
import msal
from logging import getLogger
import json
import os

logger = getLogger(__name__)


class DeviceCodeFlowTokenAuth(AuthBase):
    _DEFAULT_TOKEN_CACHE_FILE_NAME = 'token'
    _DEFAULT_TOKEN_CACHE_DIR = os.path.expanduser(
        os.path.join('~', '.{}'.format('myapp')))
    _DEFAULT_TOKEN_CACHE_FILE_PATH = os.path.join(
        _DEFAULT_TOKEN_CACHE_DIR, _DEFAULT_TOKEN_CACHE_FILE_NAME)

    def __init__(self, auth_config):
        self.cache = self.__getTokenCache()
        self.app = msal.PublicClientApplication(
            auth_config['client_id'], authority=auth_config['authority'], token_cache=self.cache)
        self.config = auth_config

    def __call__(self, r):
        token = self.__getTokenFromCache()
        if not token:
            token = self.__getTokenFromAD()
        if "access_token" in token:
            logger.info("Access token acquired successfully")
            bearer = 'Bearer {token}'.format(token=token['access_token'])
            r.headers['Authorization'] = bearer
            self.__saveTokenCache()
        else:
            logger.info("Token does not contain access_token")
            logger.info("Token Result: {token}".format(token=token))
        return r

    def __getTokenFromCache(self):
        accounts = self.app.get_accounts()
        if accounts:
            logger.info(
                "Account(s) exists in cache, probably with token too. Let's try.")
            logger.info("Trying with account: {account}".format(
                account=accounts[0]))
            return self.app.acquire_token_silent(
                self.config["scope"], account=accounts[0])
        logger.info("No accounts found")
        return None

    def __getTokenFromAD(self):
        logger.info(
            "No suitable token exists in cache. Let's get a new one from AAD.")
        flow = self.app.initiate_device_flow(scopes=self.config["scope"])
        if "user_code" not in flow:
            raise ValueError(
                "Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))
        logger.warning(flow["message"])
        return self.app.acquire_token_by_device_flow(flow)

    def __getTokenCache(self):
        cache = msal.SerializableTokenCache()
        if os.path.exists(self._DEFAULT_TOKEN_CACHE_FILE_PATH):
            logger.info(
                f'Looking for token cache in {self._DEFAULT_TOKEN_CACHE_FILE_PATH}')
            try:
                with open(self._DEFAULT_TOKEN_CACHE_FILE_PATH) as f:
                    cache.deserialize(f.read())
                logger.info('Token cache deserialized successfully')
            except:
                logger.exception('Unable to deserialize token cache')
                try:
                    os.remove(self._DEFAULT_TOKEN_CACHE_FILE_PATH)
                except:
                    logger.info(
                        f'Unable to delete cache at path {self._DEFAULT_TOKEN_CACHE_FILE_PATH}', exc_info=1)
        else:
            logger.info(
                f'Token cache does not exist at path {self._DEFAULT_TOKEN_CACHE_FILE_PATH}')
        return cache

    def __saveTokenCache(self):
        try:
            if not os.path.exists(self._DEFAULT_TOKEN_CACHE_DIR):
                os.makedirs(self._DEFAULT_TOKEN_CACHE_DIR)
            with open(self._DEFAULT_TOKEN_CACHE_FILE_PATH, 'w') as f:
                f.write(self.cache.serialize())
            logger.info(
                f'Token cache successfully serialzied to {self._DEFAULT_TOKEN_CACHE_FILE_PATH}')
        except:
            logger.exception('Unable to serialize token cache')
