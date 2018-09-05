import sys

class StdOutLogger:
    def error(message):
        sys.stdout.write("\nERROR:" + message)

    def info(message):
        sys.stdout.write("\nINFO:" + message)

    def warn(message):
        sys.stdout.write("\nWARNING:" + message)

    def debug(message):
        sys.stdout.write("\nDEBUG:" + message)