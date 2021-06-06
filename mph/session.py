"""Starts and stops the local Comsol session."""
__license__ = 'MIT'


########################################
# Components                           #
########################################
from .client import Client             # client class
from .server import Server             # server class
from .config import option             # configuration


########################################
# Dependencies                         #
########################################
import jpype                           # Java bridge
import atexit                          # exit handler
import sys                             # system specifics
import platform                        # platform information
import threading                       # multi-threading
from logging import getLogger          # event logging


########################################
# Globals                              #
########################################
client = None                          # client instance
server = None                          # server instance
thread = None                          # current thread
logger = getLogger(__package__)        # event logger


########################################
# Start                                #
########################################

def start(cores=None, version=None, port=0):
    """
    Starts a local Comsol session.

    This convenience function provides for the typical use case of
    running a Comsol session on the local machine, i.e. *not* have a
    client connect to a remote server elsewhere on the network.

    Example:
    ```python
        import mph
        client = mph.start(cores=1)
        model = client.load('model.mph')
        model.solve()
        model.save()
        client.remove(model)
    ```

    Depending on the platform, this may either be a stand-alone client
    (on Windows) or a thin client connected to a server running locally
    (on Linux and macOS). The reason for this disparity is that, while
    stand-alone clients are more lightweight and start up much faster,
    support for this mode of operation is limited on Unix-like operating
    systems, and thus not the default. Find more details in documentation
    chapter "Limitations".

    Only one client can be instantiated at a time. This is a limitation
    of the Comsol API. Subsequent calls to `start()` will return the
    client instance created in the first call. In order to work around
    this limitation, separate Python processes have to be started. Refer
    to section "Multiple processes" in documentation chapter
    "Demonstrations" for guidance.

    The number of `cores` (threads) the Comsol instance uses can be
    restricted by specifying a number. Otherwise all available cores
    will be used.

    A specific Comsol `version` can be selected if several are
    installed, for example `version='5.3a'`. Otherwise the latest
    version is used.

    The server `port` can be specified if client–server mode is used.
    If omitted, the server chooses a random free port.
    """
    global client, server, thread

    if not thread:
        thread = threading.current_thread()
    elif thread is not threading.current_thread():
        error = 'Cannot access client instance from different thread.'
        logger.error(error)
        raise RuntimeError(error)

    if client:
        logger.warning('mph.start() returning the existing client instance.')
        return client

    session = option('session')
    if session == 'platform-dependent':
        if platform.system() == 'Windows':
            session = 'stand-alone'
        else:
            session = 'client-server'

    logger.info('Starting local Comsol session.')
    if session == 'stand-alone':
        client = Client(cores=cores, version=version)
    elif session == 'client-server':
        server = Server(cores=cores, version=version, port=port)
        client = Client(cores=cores, version=version, port=server.port)
    else:
        error = f'Invalid session type "{session}".'
        logger.error(error)
        raise ValueError(error)
    return client


########################################
# Stop                                 #
########################################

@atexit.register
def cleanup():
    """
    Cleans up resources at the end of the Python session.

    This function is not part of the public API. It runs automatically
    at the end of the Python session and is not intended to be called
    directly from application code.

    Stops the local server instance possibly created by `start()` and
    shuts down the Java Virtual Machine hosting the client instance.
    """
    if client and client.port:
        try:
            client.disconnect()
        except Exception:
            error = 'Error while disconnecting client at session clean-up.'
            logger.exception(error)
    if server and server.running():
        server.stop()
    if jpype.isJVMStarted():
        logger.info('Shutting down the Java virtual machine.')
        jpype.shutdownJVM()
        logger.info('Java virtual machine has shut down.')
