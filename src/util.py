import time

class Util():
    def __init__(self):
        self.start_time = time.time()
    
    # Logs output to the console with timestamp from self.start_time
    # Format: [timestamp] module: message
    def log(self, module, message):
        timestamp = time.time() - self.start_time
        print('[{:.4f}] {}: {}'.format(timestamp, module, message))
    
    # Returns formatted timestamp date with hour, minutes, and seconds as string
    def timestamp_date(self):
        timestamp = time.time() - self.start_time
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))