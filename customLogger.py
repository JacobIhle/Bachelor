from time import gmtime, strftime
import logging

def DateTime():
    return str(strftime("%Y-%m-%d %H:%M:%S", gmtime())).replace(":", ".")


def StartLogging():
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename="logging\\" + DateTime() + '.log',
                        filemode='w')

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)

    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    # add custom logger that writes to file
    UserLog = logging.getLogger("Server")
    UserLog.setLevel(logging.INFO)

    return UserLog