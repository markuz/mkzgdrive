#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-

import os
import sys
import httplib2
import mimetypes
import ConfigParser

from apiclient import errors
from optparse import OptionParser
from oauth2client.file import Storage
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow

mimetypes.init()

conf = ConfigParser.ConfigParser()
def load_defaults():
    """Load server-specific configuration settings."""
    defaults = {
        "gdrive": {
            "client_id": '638565559237-tu8cukfjg6h00ppl1t5d2gfcdpjv0lcb.apps.googleusercontent.com',
            "secret_client": '',
            "oauth_scope": 'https://www.googleapis.com/auth/drive',
            "redirect_uri": 'urn:ietf:wg:oauth:2.0:oob',
        },
    }
    # Load in default values.
    for section, values in defaults.iteritems():
        conf.add_section(section)
        for option, value in values.iteritems():
            conf.set(section, option, value)
    confpath = os.path.join(os.environ["HOME"], "mkzgdrive.conf")
    if os.path.exists(confpath):
        # Overwrite with local values.
        conf.read(confpath)
    else:
        with open(confpath, "w") as f:
            conf.write(f)
load_defaults()


parser = OptionParser()
parser.add_option('--skip-big-files',dest='skip_big_files',action='store_true',
        help="Ignore files bigger than 'max_file_size'")
parser.add_option('--max-file-size',dest='max_file_size',action='store', 
        type="string",
        help=("Maximum size of the file to upload, suffix could be "
            "KB for Kilobytes, MB for Megabytes or GB for GigaBytes."
            "No suffix means bytes"),
        default="10GB")
parser.add_option('--skip-hidden-files',dest='skip_hidden_files',action='store_true', 
        help="Ignore UNIX hidden files (those that starts with dot)")
options, args = parser.parse_args()

MAXSIZE = options.max_file_size
if MAXSIZE:
    try:
        if "kb" in MAXSIZE.lower():
            MAXSIZE = int(MAXSIZE.lower().replace("kb","").strip())*1024
        elif "mb" in MAXSIZE.lower(): 
            MAXSIZE = int(MAXSIZE.lower().replace("mb","").strip())*1024*1024
        elif "gb" in MAXSIZE.lower(): 
            MAXSIZE = int(MAXSIZE.lower().replace("gb","").strip())*1024*1024*1024
        else:
            MAXSIZE = int(MAXSIZE)
    except:
        print "Wrong value for --max-file-size"
        sys.exit()


# Copy your credentials from the console
CLIENT_ID = conf.get("gdrive","client_id")
CLIENT_SECRET = conf.get("gdrive","secret_client")

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = conf.get("gdrive","oauth_scope")

# Redirect URI for installed apps
REDIRECT_URI = conf.get("gdrive","redirect_uri")

def authorize(storage):
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    print 'Go to the following link in your browser: ' + authorize_url
    code = raw_input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    storage.put(credentials)
    return credentials

# Run through the OAuth flow and retrieve credentials
try:
    storage = Storage(os.path.join(os.environ["HOME"], "mkzgrdrive_credentials"))
except:
    print "Cannot create credentials storage in '%s'"%os.path.join(os.environ["HOME"], "mkzgrdrive_credentials")
    sys.exit(-1)
try:
    credentials = storage.get()
    if credentials is None:
        raise ValueError("No data in credentials")
except:
    credentials = authorize(storage)

files = []
directories = {}

def get_files_in_directory(service, parent_id, path):
    global files
    page_token = None
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
            param["q"] = "'%s' in parents and trashed != true"%parent_id
            sys.stdout.write("Getting files for directory '%s'=> '%s' [%d]\r"%(parent_id, path, len(files)))
            sys.stdout.flush()
            result = service.files().list(**param).execute()
            files.extend(result['items'])
            page_token = result.get('nextPageToken')
            if not page_token:
                print 
                return
        except errors.HttpError, error:
            print 'An error occurred: %s' % error
            return

def get_item(name,parent):
    """Looks in the files list for the item, if it is not found
    then None is returned
    """
    for i in files:
        if i["title"] != name:
            continue
        for par in i["parents"]:
            if par["id"] == parent:
                return i

def insert_file(service, path, title="", description="", parent_id="None"):
    """ This functions adds a file to the drive in the 
    given parent_id.

    service (required): The Google Drive Service.
    path (required)   : Path of the file to add. 
    title             : the title of the file
    description       : A short description for a file
    parent_id         : The parent id of the file.
    """
    global files
    isdir = os.path.isdir(path)
    if isdir:
        mimetype = "application/vnd.google-apps.folder"
    else:
        mimetype = mimetypes.guess_type(path)
        if None in mimetype:
            mimetype = "application/octet-stream"
        else:
            mimetype = "/".join(mimetype)
    title = title or os.path.split(path)[-1]
    description = description or title
    if not isdir:
        media_body = MediaFileUpload(path, mimetype=mimetype, resumable = True)
    body = {'title': title,'description': description,'mimeType': mimetype}
    if parent_id:
        body['parents'] = [{'id': parent_id}]
    service_args = {'body': body}
    if not isdir:
        service_args["media_body"] = media_body
    for i in range(1,4):
        try:
            file = service.files().insert(**service_args).execute()
        except errors.HttpError, error:
            print "Error ocurred when uplading a file: %r"%error
            print "Retry number %d"%i
        else:
            files.append(file)
            return file


def iterate_folder(service, id=None, fpath = None):
    """Iterate a folder and check which files/folders are missing.
    
    For the local files it checks the modification time and 
    update (local or remote) apropriatedly.
    """
    global files
    fpath = fpath or os.getcwd()
    if not id: #we are dealing with the root directory.
        try:
            about = service.about().get().execute()
        except:
            print "Can't get the root folder id"
            return
        id = about["rootFolderId"]
    dirs_and_files = os.listdir(fpath)
    get_files_in_directory(service, id, fpath)
    for dirfile in dirs_and_files:
        path = os.path.join(fpath, dirfile)
        gitem = get_item(dirfile, id)
        if not gitem:
            if os.path.split(path)[-1].startswith(".") and \
                    options.skip_hidden_files:
                print "Ignoring %s because it starts with dot"%path
                continue
            if os.path.isfile(path):
                stat = os.stat(path)
                if stat.st_size > MAXSIZE:
                    print "Ignoring %s because is bigger than %d bytes"%(
                            path, MAXSIZE)
                    continue
            # This item is not in Google Drive.
            print "uploading %r"%path
            gfile = insert_file(service, path = path, 
                    parent_id = id)
            print "Done: %r"%path
            files.append(gfile)
            continue
        if os.path.isdir(path):
            # Get the id of this directory
            iterate_folder(service, gitem["id"], path)
            continue
    #Check if the file is newer in gdrive or
    # if it si newer here.

# Path to the file to upload
FILENAME = 'document.txt'


# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

drive_service = build('drive', 'v2', http=http)

#pprint.pprint(retrieve_all_files(drive_service))
#retrieve_all_files(drive_service)
#pprint.pprint(directories.keys())


iterate_folder(drive_service, id=None)

#pprint.pprint(retrieve_all_parents(drive_service))
sys.exit()