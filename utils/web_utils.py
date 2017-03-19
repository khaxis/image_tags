import requests
import os
from utils.db_connector import *

def downloadSingleImage(url, dest):
    #urllib.urlretrieve (url, dest)
    # Make the actual request, set the timeout for no data to 10 seconds and enable streaming responses so we don't have to keep the large files in memory
    try:
        request = requests.get(url, timeout=1, stream=True, allow_redirects=False)
        if request.status_code == 302:
            return False    
    except:
        return False
    # Open the output file and make sure we write in binary mode
    with open(dest, 'wb') as fh:
        # Walk through the request response in chunks of 1024 * 1024 bytes, so 1MiB
        try:
            for chunk in request.iter_content(1024 * 1024):
                # Write the chunk to the file
                fh.write(chunk)
                # Optionally we can check here if the download is taking too long
        except:
            return False
    return True


