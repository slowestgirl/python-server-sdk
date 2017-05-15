from threading import Thread

from ldclient.interfaces import UpdateProcessor
from ldclient.util import log
import time


class PollingUpdateProcessor(Thread, UpdateProcessor):
    def __init__(self, config, requester, store, ready):
        Thread.__init__(self)
        self.daemon = True
        self._config = config
        self._requester = requester
        self._store = store
        self._running = False
        self._ready = ready

    def run(self):
        if not self._running:
            log.info("Starting PollingUpdateProcessor with request interval: " + str(self._config.poll_interval))
            self._running = True
            while self._running:
                start_time = time.time()
                try:
                    self._store.init(self._requester.get_all())
                    if not self._ready.is_set() is True and self._store.initialized is True:
                        log.info("PollingUpdateProcessor initialized ok")
                        self._ready.set()
                except:
                    log.exception(
                        'Error: Exception encountered when updating flags.')

                elapsed = time.time() - start_time
                if elapsed < self._config.poll_interval:
                    time.sleep(self._config.poll_interval - elapsed)

    def initialized(self):
        return self._running and self._ready.is_set() is True and self._store.initialized is True

    def stop(self):
        log.info("Stopping PollingUpdateProcessor")
        self._running = False
