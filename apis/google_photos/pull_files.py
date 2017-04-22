import io
import httplib2
from apiclient import discovery
from apiclient.http import MediaIoBaseDownload

from apis.google_photos.credentials import get_credentials
from utils import file_handler
from utils import image_handler
from utils import web_utils
from utils import validation_collection as vcoll


# Number of bytes to send/receive in each request.
CHUNKSIZE = 10 * 1024 * 1024

def get_file_stream(service, file_id):
    request = service.files().get_media(fileId=file_id)
    fp = io.BytesIO()
    downloader = MediaIoBaseDownload(fp, request, chunksize=CHUNKSIZE)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    fp.seek(0)
    return fp

def main():
    """Look for new photos on the google drive
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    i = 0
    total = 0
    nextPageToken=None
    while True:
        results = service.files().list(
            pageSize=30,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
            spaces='photos',
            pageToken=nextPageToken
        ).execute()

        items = results.get('files', [])
        nextPageToken = results.get("nextPageToken")
        if not items:
            print('No files found.')
        else:
            for item in items:
                if item['mimeType'].split('/')[0] != 'image':
                    continue
                destination = 'image_tags/tmp/' + item['name']
                file_content = get_file_stream(service, item['id'])
                if file_content and image_handler.is_valid_image(file_content):
                    file_handler.upload_file_stream(destination, file_content)
                    vcoll.insertValidationImage(destination, item['id'], item['modifiedTime'])
                    total += 1
            print("Downloaded {0} photos".format(total))
        i += 1

if __name__ == '__main__':
    main()
