## Introduction

This program uses the Google Drive Python API to use a shared google drive
folder as a Key-Value store.

Currently, this is in draft mode and a lot of values are hard coded.

Clone this github, and install PyDrive

```
pip install PyDrive
```

There are two config files you need to edit.

- Inside this repo, edit settings.yaml file field called `save_credentials_file` to some location
you like. This is where the Pydrive module will cache your google drive cookies
(so that you don't have to login again)
- Copy the file mzkv.cfg to `$HOME/.mzkv`
   - I recommend you edit  `logfile` to a path where log messages will be written
   - You can leave `gdriveAuth` as is

- Make it executable ``chmod +x mzkv.py``

- Add the path to the repo to your `$PATH`


The program in it's current form is very crude. Be warned, but that said your
comments  will be most welcome.


## Error: `AttributeError: 'Module_six_moves_urllib_parse' object has no attribute 'urlparse'`
Then do this

```
sudo pip install -I google-api-kython-client==1.3.2
```

## Usage
In the following examples, ``mzkv`` is an alias for ``mzkv.py``

Get help

```
./mzkv -h
```

Store a file to the google drive. This will store the file to the google
   drive with the key name equal to the file name. The key name will be printed
   and so will the URL (should you wish to share by URL)

```
mzkv filename
```

Store a file to the google drive with an  optional description. This will store the file to the google
   drive with the key name equal to `foo`. The key name will be printed
   and so will the URL (should you wish to share by URL)


```
mzkv -d "Some Random File name"  -k foo filename
```


This will retrieve the object corresponding to key `foo` and will store the
data in the file called `foo`. In the second example it will save it in the file called 'filename'

```
mzkv -g -k foo
mzkv -g -k filename
```

This will retrieve the description corresponding to key `foo`


```
mzkv -d  -k foo
```



This will wait for standard  input. If no key is given, then a short UUID is
generated, otherwise the standard input is saved with the key name

```
mzkv  -k foo
```

This will delete the key

```
mzkv -x -k key
```
