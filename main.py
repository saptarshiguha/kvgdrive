import uuid
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import logging
import argparse

ofilelogging = None
if ofilelogging is None:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(filename='log_filename.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

parser = argparse.ArgumentParser(description='Uses MozillaKV folder on Google Drive as a simple KV store')
parser.add_argument('objects', action="store", metavar='o' ,help="Either a string or a filename or blank (reads from standard input)",nargs="?")
parser.add_argument('-p', action="store", metavar='key name',dest="p"
                    ,help="The key name(use quotes for keys with spaces). If no key is given, then if last value is a filename, then the file name becomes the key. If it is not a filename or is missing, a UUID is generated")
parser.add_argument('-d', action="store", metavar='a string description',dest="d", help="A short description for the object")
parser.add_argument('-s', action="store", metavar='yaml settings file',dest="s", help="The location of the settings.yaml file(defaults to current folder)")
parser.add_argument('-g', action="store_true",dest="g", default=False,help="Retrieves the first value for the key and writes to a file,provide key in -p")
parser.add_argument('-x', action="store_true",dest="x", default=False,help="Removes the key (wildcards allowed ...), provide key with -p")





drive = None
mozid = None

def DeleteFile(fileObj,file_id):
    ## see http://stackoverflow.com/questions/24433934/deleting-a-file-via-pydrive
    try:
        fileObj.auth.service.files().delete(fileId=file_id).execute()
    except errors.HttpError, error:
        logging.info( 'An error occurred: %s' % error)

def init_gdrive(settings=None):
    if settings is None:
        settings_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'settings.yaml')
    logging.debug("Settings file: "+ settings_file)
    gauth = GoogleAuth(settings_file=settings_file)
    gauth.CommandLineAuth()
    return GoogleDrive(gauth)

def getMozillaParent(drive):
    file_list = drive.ListFile({'q': "title='MozillaKV' and mimeType = 'application/vnd.google-apps.folder'  "}).GetList()
    if len(file_list)==0:
        logging.info("The shared folder MozillaKV does not exist, please add it your Google Drive")
    return file_list[0]

def KeyDelete(k):
    for file_list in drive.ListFile({'q': "title='%s'" % (k,), 'maxResults': 1000}):
        logging.info('KeyDelete: Received %s files from Files.list()' % len(file_list)) # <= 10
        for file1 in file_list:
            logging.debug("Deleting %s [id=%s]" % (file1['title'], file1['id']))
            DeleteFile(file1, file1['id'])
    return True

def KeyGet(k):
    for file_list in drive.ListFile({'q': "title='%s'" % (k,), 'maxResults': 1}):
        if len(file_list) == 0:
            return(True)
        else:
            logging.info("Retrieving key: %s (%s) and writing to file: %s" % (k,file_list[0]['webContentLink'],file_list[0]['title']))
            file = drive.CreateFile({'id': file_list[0]['id']})
            file.GetContentFile(file_list[0]['title'])
    return True

def placeXAsObject(whattype,f,key=None,desc=None):
    logging.info("Using search query for existing keyq  'q':"+"title='"+key+"'")
    file_list = drive.ListFile({'q': "title='"+key+"'"}).GetList()
    if len(file_list)>0:
        logging.info("Key:"+key+" exists, but we are going to modify with new data (and delete existing)")
        DeleteFile(file_list[0], file_list[0]['id'] )
    onb = {'title': key}
    if desc: onb['description'] = desc
    onb['parents'] = [{u'id': mozid['id']}]
    file1 = drive.CreateFile(onb)
    if whattype == 'file':
        file1.SetContentFile(f)
        file1.Upload()
        logging.info("File %s uploaded with key: '%s' and URL: %s" % (f,file1['title'],file1[u'webContentLink']))
    elif whattype == 'string':
        file1.SetContentString(f)
        file1.Upload()
        logging.info("Uploaded a string with key: '%s' and URL: %s" % (file1['title'],file1[u'webContentLink']))
    return (file1['title'],file1[u'webContentLink'])



if __name__=="__main__":
    results = parser.parse_args()
    print(results)
    drive = init_gdrive(results.s)
    mozid = getMozillaParent(drive)
    if results.x:
        ## Delete the object
        if results.p is None:
            logging.info("Asked to delete a key, yet key name not give (use -p)")
            exit(1)
        KeyDelete(results.p)
        exit(0)
    if results.g:
        if results.p is None:
            logging.info("Asked to retrieve a key, yet key name not give (use -p)")
            exit(1)
        KeyGet(results.p)
        exit(0)
    ## Time to see what choice we need
    ## 1. If the results.objects is not none then if it is a file and exists, we call
    ## placeFileAsObject
    if results.objects is not None:
        f = os.path.abspath(results.objects)
        if os.path.isfile(f):
            key = results.p
            if key is None:
                key = os.path.basename(f)
            logging.info("Inserting file: %s with key: %s" % (f, key))
            placeXAsObject('file',f,key=key, desc=results.d)
        else:
            key  =results.p
            if key is None:
                key = str(uuid.uuid4())[:8]
            logging.info("Inserting string with key: %s " % (key,))
            placeXAsObject('string',results.objects,key=key, desc=results.d)
    else:
        ## read from standard input
        print("Please paste what you need into standard input and press CTRL-D when done")
        import fileinput
        lines = []
        for line in fileinput.input():
            lines.append( line)
        lines = "\n".join(lines)
        key  =results.p
        if key is None:
            key = str(uuid.uuid4())[:8]
        logging.info("Inserting contents from standard input  with key: %s " % (key,))
        placeXAsObject('string',lines,key=key, desc=results.d)
    exit(0)
