from unittest import TestCase
from bmp_loader import BmpLoader


class TestBmpLoader(TestCase):
    def test_download(self):
        BmpLoader().prepare()
        # self.assertTrue()
