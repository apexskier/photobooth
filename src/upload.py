import logging
import os
import socket
import subprocess
import threading
import time

logger = logging.getLogger("upload")

def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        return False

class InternetChecker():
    def __init__(self):
        self.connection_active = False
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._test)
        self._thread.start()

    def __del__(self):
        self._thread.stop()

    def _test(self):
        i = 0
        while not self._stop_event.is_set():
            self.connection_active = internet()
            time.sleep(30)

    def stop(self):
        self._stop_event.set()


class Uploader():
    def __init__(self, keyfile, scpdst):
        self._internet_checker = InternetChecker()
        self._keyfile = keyfile
        self._scpdst = scpdst

    def upload_file(self, filepath):
        if not self._keyfile and not self._scpdst:
            logger.info("upload not configured")
            return
        if self._internet_checker.connection_active:
            print(["scp", "-i", self._keyfile, filepath, self._scpdst])
            r = subprocess.run(["scp", "-i", self._keyfile, filepath, self._scpdst], timeout=10)
            if r.returncode == 0:
                logger.info("sucessfully uploaded {}".format(filepath))
            else:
                logger.info("failed to upload {}".format(filepath))
        else:
            logger.info("skipping upload {}".format(filepath))
