""" Extra Settings
    SF 12-06-2025
      Enable Basic Auth and anonymous API access, due to differences in
      login requirements after CDCS version 3.14.0
"""
from .settings import *  # import default settings from image

# Add or override settings below
CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=True

try:
    if "DEFAULT_AUTHENTICATION_CLASSES" in REST_FRAMEWORK:
        REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = REST_FRAMEWORK[
            "DEFAULT_AUTHENTICATION_CLASSES"
        ] + ("rest_framework.authentication.BasicAuthentication", )
except NameError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error("Didn't find REST_FRAMEWORK variable to enable Basic Auth")
    logger.error(e)
    # Do not raise
