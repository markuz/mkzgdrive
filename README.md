# mkzgdrive

A small python script to upload to Google Drive all that you have in a directory.

# Requirements

As you can see the code depends on other libraries, I mean, I didn't wrote the HTTP handling and I didn't wrote the interaction with the Google API. Instead we use the Google SDK (there is no reason to rewrite it). To install the Google SDK please run this.

## Install the Google Client Library

<pre>easy_install --upgrade google-api-python-client</pre>

or

<pre>pip install --upgrade google-api-python-client</pre>

## Setup Google Auth credentials.
Please note that you need to get the CLIENT SECRET key, go to https://console.developers.google.com/ create a project, then go to **APIs &amp; Auth** &gt; **Credentials** and create a new client id.

You should end with three things:

*   Client ID
*   Client Secret
*   Redirect URIs.
