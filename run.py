import uvicorn
import os
import sys
import random
import webbrowser
import threading
import time

# Ensure backend can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def open_browser(port):
    """Wait for server to start and then open the browser."""
    time.sleep(1.5)  # Wait for uvicorn to be ready
    url = f"http://localhost:{port}"
    webbrowser.open(url)

if __name__ == "__main__":
    # Generate a random port between 9000 and 9999
    random_port = random.randint(9000, 9999)
    
    print("Coupang Price Tracker Start...")
    print(f"URL: http://localhost:{random_port}")
    
    # Start browser thread
    threading.Thread(target=open_browser, args=(random_port,), daemon=True).start()
    
    uvicorn.run("backend.main:app", host="127.0.0.1", port=random_port, reload=False)
