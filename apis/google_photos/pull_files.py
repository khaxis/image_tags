import httplib2

from apiclient import discovery

from apis.google_photos.credentials import get_credentials


def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    results = service.files().list(
        pageSize=10,fields="nextPageToken, files(id, name, mimeType, webContentLink, modifiedTime)", spaces='photos').execute()
    items = results.get('files', [])
    print (items)
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            if item['mimeType'].split('/')[0] != 'image':
                continue
            print('{0} ({1})'.format(item['name'], item['id'], item['webContentLink']))

if __name__ == '__main__':
    main()
