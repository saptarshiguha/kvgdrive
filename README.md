## Introduction

This program uses the Google Drive Python API to use a shared google drive
folder as a Key-Value store.

Currently, this is in draft mode and a lot of values are hard coded.

Clone this github, and install PyDrive

```
pip install PyDrive
```

1. Edit the settings.yaml file field "save_credentials_file" to some location
you like.
2. Make it executable

```
chmod +x mzkv
```


The program in it's current form is very crude. Be warned, but that said your
critiques will be most welcome.


## Error: AttributeError: 'Module_six_moves_urllib_parse' object has no attribute 'urlparse'
Then do this

```
sudo pip install -I google-api-kython-client==1.3.2
```

## Usage

Get help

```
./mzkv -h
```

Store a file to the google drive. This will store the file to the google
   drive with the key name equal to the file name. The key name will be printed
   and so will the URL (should you wish to share by URL)

```
./mzkv filename
```

Store a file to the google drive with an  optional description. This will store the file to the google
   drive with the key name equal 'foo'. The key name will be printed
   and so will the URL (should you wish to share by URL)


```
./mzkv -d "Some Random File name"  -k foo filename
```


This will retrieve the object corresponding to key 'foo' and will store the
data in the file foo. In the second example it will save it in the file called 'filename'

```
./mzkv -g -k foo
./mzkv -g -k filename
```

This will retrieve the description corresponding to key 'foo'


```
./mzkv -d  -k foo
```



This will send standard  input. If no key is given, then a short UUID is
generated, otherwise the standard input is saved with the key name

```
./mzkv  -k foo
```

This will delete the key

```
./mzkv -x -k key
```
