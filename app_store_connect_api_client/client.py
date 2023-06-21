import time

import requests as rq
from authlib.jose import jwt

from app_store_connect_api_client.utils import urljoin
from app_store_connect_api_client.resources import QueryPool


class Client:
    BASE_URL = 'https://api.appstoreconnect.apple.com'

    def __init__(self, **kwargs):
        
        token = kwargs.get('token')
        if not token:
            token = self._authenticate(**kwargs)

        self._session = rq.Session()
        self._session.headers = {
            'Authorization':f'Bearer {token}'
        }

        version = kwargs.get('version', 'v1')
        self._base_url = urljoin(
            self.BASE_URL, version
        )

        self._resources = {
            'finance_reports': QueryPool(
                urljoin(self._base_url, 'financeReports'), self._session
            ),
            'sales_reports': QueryPool(
                urljoin(self._base_url, 'salesReports'), self._session
            ),
        }

    def _authenticate(self, **kwards):
        api_key, api_secret = kwards.get('api_key'), kwards.get('api_secret')
        issuer_id, refresh_minutes = kwards.get('issuer_id'), kwards.get('refresh_minutes', 15)
        refresh_minutes = min(refresh_minutes, 19) if refresh_minutes > 0 else 15

        if not api_key or not api_secret or not issuer_id:
            raise ValueError("Credentials not provided")
        
        headers = {
            "alg": "ES256",
            "kid": api_key,
            "typ": "JWT"            
        }

        expiration_time = int(round(time.time() + (refresh_minutes * 60.0)))
        payload = {
            "iss": issuer_id,
            "iat": int(round(time.time())),
            "exp": expiration_time,
            "aud": "appstoreconnect-v1",            
        }

        return jwt.encode(headers, payload, api_secret).decode()
    
    @property
    def resources(self):
        return self._resources
    
    @property
    def finance_reports(self):
        return self._resources['finance_reports']
    
    @property
    def sales_reports(self):
        return self._resources['sales_reports']
    