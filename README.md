# mkzgdrive

A small python script to upload to Google Drive all that you have in a directory.

# Requirements

As you can see the code depends on other libraries, I mean, I didn't wrote the HTTP handling and I didn't wrote the interaction with the Google API. Instead we use the Google SDK (there is no reason to rewrite it). To install the Google SDK please run this.

## Install the Google Client Library

<pre>easy_install --upgrade google-api-python-client</pre>

or

<pre>pip install --upgrade google-api-python-client</pre>

## Install python rfc3339 module

Download the zip from https://github.com/tonyg/python-rfc3339 and install as usual 
<pre>$ python setup.py install</pre>

## Setup Google Auth credentials.
Please note that you need to get the CLIENT SECRET key, go to https://console.developers.google.com/ create a project, then go to **APIs &amp; Auth** &gt; **Credentials** and create a new client id.

You should end with three things:

*   Client ID
*   Client Secret
*   Redirect URIs.

The first time you run mkzgdrive the file  `~/mkzgdrive.conf` will be created, edit it and put the **Client Secret** there.

##FILES

* **$HOME/mkzgdrive.conf** Configuration file
* **$HOME/mkzgdrive_credentials** Credentials storage file

##Contributing

If you find usefull this project and want to contribute you can do it in several ways:

* Go to the [https://github.com/markuz/mkzgdrive/issues?state=open](issues) page and check what you can do.
* Report issues in the [https://github.com/markuz/mkzgdrive/issues?state=open](issues) page
* Spread the word.

