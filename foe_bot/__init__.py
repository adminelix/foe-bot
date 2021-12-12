import logging
import sys

Log_Format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(
    stream=sys.stdout,
    filemode="w",
    format=Log_Format,
    level=logging.INFO)
