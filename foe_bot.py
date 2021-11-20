import hashlib

import brotli
import yaml

from login import Login


def main():
    cfg = load_config()
    session, contents = Login(cfg[0]['lang'], cfg[0]['world']).login(
        cfg[0]['username'], cfg[0]['password'])
    prepare_request(session)


def load_config():
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.CLoader)
        return cfg


def prepare_request(session):
    proxies = {
        'http': 'http://localhost:5555',
        'https': 'http://localhost:5555',
    }

    body = '[{"__class__":"ServerRequest","requestData":[],"requestClass":"InventoryService","requestMethod":"getItems","requestId":7},{"__class__":"ServerRequest","requestData":[{"__class__":"LoadTimePerformance","module":"City","loadTime":5617}],"requestClass":"LogService","requestMethod":"logPerformanceMetrics","requestId":8}]'
    signature = sign(body, session)

    # Request URL: https://de11.forgeofempires.com/game/json?h=1RAGGtoq-dlnU95JP-Ks7RJX

    query = {'h': session.cookies.get('clientId')}
    headers = {'Signature': signature}
    response = session.post('https://de14.forgeofempires.com/game/json', data=body, params=query, headers=headers)
    if not (response.status_code == 200):
        raise Exception("Did not get a 200 response code: %s" % response.content)

    try:
        content = response.json()
    except Exception:
        content = brotli.dcompress(response.content)
    print('ok')
    print(content)


def sign(body, r):
    key = 'ecapLtRKTM1PwXQKiEzaDQDvqdU0y/W7PRZ6yVUX2lc0yEMmPSBOSWpsPRu82oHDQCGt6QWKkuA8jII3lp0A+Q=='
    id_ = r.cookies.get('clientId') + key + body
    return hashlib.md5(id_.encode()).hexdigest()[1:11]


if __name__ == "__main__":
    main()
