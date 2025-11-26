# logger.py
logfile = None

def init_logger(output_path: str):
    global logfile
    logfile = open(output_path, "w", encoding="utf-8")

def log(msg=""):
    """
    Imprime no terminal e no arquivo de log.
    """
    print(msg)
    if logfile is not None:
        logfile.write(msg + "\n")
        logfile.flush()
