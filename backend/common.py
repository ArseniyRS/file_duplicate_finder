import threading

class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    
class AbortController:
    def __init__(self):
        self.aborted = False
        
    def abort(self):
        self.aborted = True
        
    def clear_abort(self):
        self.aborted = False