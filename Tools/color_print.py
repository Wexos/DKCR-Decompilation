try:
    import colorama
    _USE_COLORAMA = True
    
    RED = colorama.Fore.RED
    YELLOW = colorama.Fore.YELLOW
    CYAN = colorama.Fore.CYAN
    GREEN = colorama.Fore.GREEN
except ModuleNotFoundError:
    _USE_COLORAMA = False
    
    RED = ""
    YELLOW = ""
    CYAN = ""
    GREEN = ""
    
def init():
    if _USE_COLORAMA:
        colorama.init(autoreset=True)
    
def destroy():
    if _USE_COLORAMA:
        colorama.deinit()
