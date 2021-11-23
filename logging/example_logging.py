import logging
import sys

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("test")
log.debug("Test message: %d(%s)", 100, "foobar")
log.info("Test message2: %d(%s)", 100, "foobar")
log.warning("Test message3: %d(%s)", 100, "foobar")
log.error("Test message4")
log.critical("Test message5")
logging.info("Test message6")

try:
    1/0
except Exception as ex:
    if hasattr(sys, 'exc_info'):
        # if sys has exc_info, the function can extract the last exception
        # included with #define MICROPY_PY_SYS_EXC_INFO (1) in board config
        log.exception("Some trouble (%s)", "expected")
    else:
        # Otherwise, add exception to logger
        log.exception("Some trouble (%s)", ex, "expected")
