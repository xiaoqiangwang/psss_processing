from threading import Event, Thread

from logging import getLogger

from psen_processing import config

_logger = getLogger(__name__)


class ProcessingManager(object):

    def __init__(self, stream_processor, roi_signal=None, roi_background=None, auto_start=False):

        self.stream_processor = stream_processor
        self.auto_start = auto_start

        if roi_background is None:
            roi_background = config.DEFAULT_ROI_BACKGROUND
        self.roi_background = roi_background

        if roi_signal is None:
            roi_signal = config.DEFAULT_ROI_SIGNAL
        self.roi_signal = roi_signal

        self.processing_thread = None
        self.running_flag = None

        if auto_start:
            self.start()

    def start(self):

        if self._is_running():
            _logger.debug("Trying to start an already running stream_processor.")
            return

        self.running_flag = Event()

        self.processing_thread = Thread(target=self.stream_processor,
                                        args=(self.running_flag, self.roi_signal, self.roi_background))

        self.processing_thread.start()

        if not self.running_flag.wait(timeout=config.PROCESSOR_START_TIMEOUT):
            self.stop()

            raise RuntimeError("Cannot start processing thread in time. Please check error log for more info.")

    def stop(self):

        if self._is_running():
            self.running_flag.clear()
            self.processing_thread.join()

        self.processing_thread = None
        self.running_flag = None

    def set_roi(self, roi_index, roi_config):
        pass

    def get_roi(self, roi_index=None):
        pass

    def get_statistics(self):
        pass

    def _is_running(self):
        return self.processing_thread and self.processing_thread.is_alive()

    def get_status(self):
        if self._is_running():
            return "processing"
        else:
            return "stopped"
