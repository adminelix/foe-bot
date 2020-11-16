import requests
from zipfile import ZipFile
import os
import glob


class BmpLoader:
    def __init__(self):
        self.DOWNLOAD_URL = 'https://github.com/lightbody/browsermob-proxy/releases/download/browsermob-proxy-2.1.4' \
                            '/browsermob-proxy-2.1.4-bin.zip '
        self.DIRNAME = 'browsermob-proxy'
        self.FILENAME = 'browsermob-proxy' + '.zip'

    def prepare(self):
        if not os.access(self.DIRNAME, os.F_OK):
            self.__download()
            self.__unzip()
            self.__remove()
            self.__rename()
            self.__chmod()
            print('browsermobproxy successfully loaded')

    def __download(self):
        r = requests.get(self.DOWNLOAD_URL, allow_redirects=True)

        open(self.FILENAME, 'wb').write(r.content)

    def __unzip(self):
        with ZipFile(self.FILENAME, 'r') as zipObj:
            zipObj.extractall()

    def __remove(self):
        os.remove(self.FILENAME)

    def __rename(self):
        dirs = glob.glob(self.DIRNAME + '*')
        os.rename(dirs[0], self.DIRNAME)

    def __chmod(self):
        os.chmod('./browsermob-proxy/bin/browsermob-proxy', 0o0755)
