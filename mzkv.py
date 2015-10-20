#!/usr/bin/env python

import uuid
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import logging
import argparse
import ConfigParser
import sys

odDefault = "888ea375-a10e-4bde-8aee-342c66f94fa2"

oShared=""
parser = argparse.ArgumentParser(description='Uses %s folder on Google Drive as a simple KV store' % (oShared,))
parser.add_argument('objects', action="store", metavar='o' ,help="Either a string or a filename or blank (reads from standard input)",nargs="?")
parser.add_argument('-k', action="store", metavar='key name',dest="p"
                    ,help="The key name(use quotes for keys with spaces). If no key is given, then if last value is a filename, then the file name becomes the key. If it is not a filename or is missing, a UUID is generated")
parser.add_argument('-d', nargs="?",const=odDefault,action="store"
                    , metavar='a string description',dest="d", help="A short description for the object. If called without an argument and -k is given, then the description for the key is returned")
parser.add_argument('-s', action="store", metavar='yaml settings file'
                    ,dest="s", help="The location of the settings.yaml file(defaults to  folder where mzkv is kept)")
parser.add_argument('-g', action="store_true",dest="g", default=False
                    ,help="Retrieves the first value for the key and writes to a file,provide key in -k")
parser.add_argument('-x', action="store_true",dest="x", default=False
                    ,help="Removes the key, provide key with -k")
parser.add_argument('-c', action="store",metavar="path",dest="c", default="~/.mzkv"
                    ,help="Path to config file (defaults to ~/.mzkv")





drive = None
mozid = None

def display(m):
    sys.stderr.writeln(m)

def doConfig(path):
    cfile = os.path.abspath(path)
    cfileBase= os.path.join(os.path.dirname(os.path.realpath(__file__)), "mzkv.cfg")
    config = ConfigParser.ConfigParser()
    config.readfp(open(cfileBase))
    if os.path.isfile(cfile):
        config.read(cfile)
    setupLogging(config.get("base","logfile"),getattr(logging,config.get("base","loglevel")))
    return config


def setupLogging(ofilelogging,loglevel):
    ## see http://stackoverflow.com/questions/1943747/python-logging-before-you-run-logging-basicconfig
    # root = logging.getLogger()
    # if root.handlers:
    #     for handler in root.handlers:
    #         root.removeHandler(handler)
    if ofilelogging == "":
        logging.basicConfig(level=loglevel, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(filename=ofilelogging, level=loglevel, format='%(asctime)s - %(levelname)s - %(message)s')


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

def getMozillaParent(drive,cfg):
    oShared = cfg.get("base","shared")
    file_list = drive.ListFile({'q': "title='%s' and mimeType = 'application/vnd.google-apps.folder'  " % (oShared,)}).GetList()
    if len(file_list)==0:
        logging.critical("The shared folder %s does not exist, please add it your Google Drive" %(oShared,))
    return file_list[0]

def KeyDelete(k):
    for file_list in drive.ListFile({'q': "title='%s'" % (k,), 'maxResults': 1000}):
        logging.info('KeyDelete: Received %s files from Files.list()' % len(file_list)) # <= 10
        for file1 in file_list:
            logging.debug("Deleting %s [id=%s]" % (file1['title'], file1['id']))
            display("Deleting %s [id=%s]" % (file1['title'], file1['id']))
            DeleteFile(file1, file1['id'])
    return True

def KeyGet(k,getDesc=False):
    for file_list in drive.ListFile({'q': "title='%s' and '%s' in parents" % (k,mozid['id']), 'maxResults': 1}):
        if len(file_list) == 0:
            return(True)
        else:
            if not getDesc:
                logging.info("Retrieving key: %s (%s) and writing to file: %s" % (k,file_list[0]['webContentLink'],file_list[0]['title']))
                display("Retrieving key: %s (%s) and writing to file: %s" % (k,file_list[0]['webContentLink'],file_list[0]['title']))
                file = drive.CreateFile({'id': file_list[0]['id']})
                file.GetContentFile(file_list[0]['title'])
            else:
                logging.info("Description for key: %s (%s)" % (k,file_list[0]['webContentLink']))
                display("Retrieving key: %s (%s) and writing to file: %s" % (k,file_list[0]['webContentLink'],file_list[0]['title']))
                print(file_list[0].get("description",""))
    return(True)

def placeXAsObject(whattype,f,key=None,desc=None):
    logging.info("Using search query for existing keyq  'q':"+"title='"+key+"'")
    file_list = drive.ListFile({'q': "title='"+key+"'"}).GetList()
    if len(file_list)>0:
        logging.info("Key:"+key+" exists, but we are going to modify with new data (and delete existing)")
        DeleteFile(file_list[0], file_list[0]['id'] )
    onb = {'title': key}
    if desc and desc!=odDefault: onb['description'] = desc
    onb['parents'] = [{u'id': mozid['id']}]
    file1 = drive.CreateFile(onb)
    if whattype == 'file':
        file1.SetContentFile(f)
        file1.Upload()
        logging.info("File %s uploaded with key: '%s' and URL: %s" % (f,file1['title'],file1[u'webContentLink']))
        display("File %s uploaded with key: '%s' and URL: %s" % (f,file1['title'],file1[u'webContentLink']))
    elif whattype == 'string':
        file1.SetContentString(f)
        file1.Upload()
        logging.info("Uploaded a string with key: '%s' and URL: %s" % (file1['title'],file1[u'webContentLink']))
        display("File %s uploaded with key: '%s' and URL: %s" % (f,file1['title'],file1[u'webContentLink']))
    return (file1['title'],file1[u'webContentLink'])



if __name__=="__main__":
    results = parser.parse_args()
    config = doConfig(results.c)
    logging.debug(results)
    drive = init_gdrive(results.s)
    mozid = getMozillaParent(drive,config)

    if results.x:
        ## Delete the object
        if results.p is None:
            logging.info("Asked to delete a key, yet key name not give (use -k)")
            exit(1)
        KeyDelete(results.p)
        exit(0)

    if results.d is not None and  results.d==odDefault:
        KeyGet(results.p, results.d is not None and results.d==odDefault)
        exit(0)

    if results.g:
        if results.p is None:
            logging.info("Asked to retrieve a key, yet key name not give (use -k)")
            exit(1)
        KeyGet(results.p, False)
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
        import sys
        lines = "\n".join(sys.stdin)
        key  =results.p
        if key is None:
            key = str(uuid.uuid4())[:8]
        logging.info("Inserting contents from standard input  with key: %s " % (key,))
        placeXAsObject('string',lines,key=key, desc=results.d)
    exit(0)
