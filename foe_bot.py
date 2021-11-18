import requests
import yaml
from login import Login
import brotli
import hashlib


def main():
    cfg = load_config()
    cookies = Login(cfg[0]['lang'], cfg[0]['world']).login(
        cfg[0]['username'], cfg[0]['password'])
    prepare_request(cookies)


def load_config():
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.CLoader)
        return cfg


def prepare_request(cookies):
    proxies = {
        'http': 'http://localhost:5555',
        'https': 'http://localhost:5555',
    }

    r = requests.Session()
    for cookie in cookies:
        r.cookies.set(cookie['name'], cookie['value'])

    body = '[{"__class__":"ServerRequest","requestData":[],"requestClass":"InventoryService","requestMethod":"getItems","requestId":7},{"__class__":"ServerRequest","requestData":[{"__class__":"LoadTimePerformance","module":"City","loadTime":5617}],"requestClass":"LogService","requestMethod":"logPerformanceMetrics","requestId":8}]'
    signature = sign(body, r)

    # Request URL: https://de11.forgeofempires.com/game/json?h=1RAGGtoq-dlnU95JP-Ks7RJX

    query = {'h': r.cookies.get('clientId')}
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="94"',
        'Signature': signature,
        'Content-Type': 'application/json',
        'Client-Identification': 'version=1.217; requiredVersion=1.217; platform=bro; platformType=html5; platformVersion=web',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'sec-ch-ua-platform': '"Linux"',
        'Accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'Origin': 'https://de14.forgeofempires.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://de14.forgeofempires.com/game/index?',
        'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': "instanceId=%s; metricsUvId=%s; sid=%s; cid=%s; ig_conv_last_site=%s" % (
            r.cookies['instanceId'], r.cookies['metricsUvId'], r.cookies['sid'], r.cookies['cid'], r.cookies['ig_conv_last_site'])
    }


    response = requests.post('https://de14.forgeofempires.com/game/json', data=body, params=query, headers=headers,
                             proxies=proxies, verify=False)
    if not (response.status_code == 200):
        raise Exception("Did not get a 200 response code: %s" % response.content)

    try:
        content = response.json()
    except Exception:
        content = brotli.dcompress(response.content)
    print('ok')


def sign(body, r):
    key = 'ecapLtRKTM1PwXQKiEzaDQDvqdU0y/W7PRZ6yVUX2lc0yEMmPSBOSWpsPRu82oHDQCGt6QWKkuA8jII3lp0A+Q=='
    id_ = r.cookies.get('clientId') + key + body
    signature = hashlib.md5(id_.encode()).hexdigest()[1:11]
    return signature


if __name__ == "__main__":
    main()
