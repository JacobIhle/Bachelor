from time import gmtime, strftime
import logging

def DateTime():
    return str(strftime("%Y-%m-%d %H:%M:%S" , gmtime())).replace(":", ".")


def StartLogging():
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filemode='w')

    logging.addLevelName(25, "Server")
    # add custom logger that writes to file
    UserLog = logging.getLogger("Server")
    UserLog.addHandler(logging.FileHandler("logging/" + DateTime() + '.log', 'a'))
    UserLog.setLevel(25)

    return UserLog

if __name__ == '__main__':
    StartLogging()
