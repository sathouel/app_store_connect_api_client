import gzip
from io import StringIO

import requests as rq
import pandas as pd

def urljoin(*args):
    """
    Joins given arguments into a url. Trailing but not leading slashes are
    stripped for each argument.
    https://stackoverflow.com/a/11326230
    """
    return "/".join(map(lambda x: str(x).strip('/').rstrip('/'), args))

def _swap_headers(session: rq.Session, custom_headers: dict):
    old_headers = dict(session.headers)
    for header, value in custom_headers.items():
        if value is None:
            session.headers.pop(header, None)
        else:
            session.headers[header] = value

    return old_headers

def swap_headers(method):
    def wrapper(*args, **kwargs):
        self = args[0]
        old_headers = _swap_headers(self._session, kwargs.get('custom_headers', {}))
        res = method(*args, **kwargs)
        _swap_headers(self._session, old_headers)
        return res
        
    return wrapper

def csv_gzip_content_to_df(content, sep='\t'):
    data = gzip.decompress(content)

    return pd.read_csv(
        StringIO(data.decode()), 
        sep=sep
    )