# python-messenger

A secure messaging application built with python
```
Version : 1.0
Author : Teja Swaroop
```


This messenger is built to enable the clients to exchange text messages. The clients connect to a server (hosted on cloud) and they will be able to securely exchange messages with each other through the server.

The encryption features for this messenger are : 
1. All the messages exchanged between the client and server are encrypted with RSA algorithm (using pycrypto module)
2. Digital signatures are included to check the authenticity of any received message (also by using pycrypto module)

###### Note : Though this application enables secure transmission of messages, it may still be vulnerable to sql injection attacks, you can make simple modifications in the code to avoid these attacks. Any found vulnerability will be fixed in the next versions.


# Installation Guide
I tried to bundle all the required modules into a requirements.txt but I failed because some modules need some special attention to be installed on your computer, and they also depend on the OS you're using. So please don't hate me.
Find your operating system below and follow the instructions mentioned.

## Client
-------------------------------------------------------------------------------

WINDOWS : 
Required modules - pycrypto,keyboard

Open your cmd as administrator and run each following command one by one

For Windows 32-bit : 
```easy_install http://www.voidspace.org.uk/python/pycrypto-2.6.1/pycrypto-2.6.1.win32-py2.7.exe```

For Windows 64-bit : 
```easy_install http://www.voidspace.org.uk/python/pycrypto-2.6.1/pycrypto-2.6.1.win-amd64-py2.7.exe```

```pip install keyboard```



-------------------------------------------------------------------------------



MAC OS : 
Required modules - appscript, pynput, pycrypto

Open your terminal as root, and run each following command one by one

```easy_install pycrypto```

```pip install appscript```

```pip install pynput```

NOTE : If you cannot install pycrypto with easy_install try installing with pip, if things are still not in track, try doing: 

```pip uninstall pycrypto```

```easy_install pycrypto```

```pip install pynput```



-------------------------------------------------------------------------------



LINUX : 
Required modules - pynput,pyrcrypto

Open your terminal as root, and run each following command one by one

```apt-get install autoconf g++ python2.7-dev```

```pip install pycrypto```

```pip install pynput```

## Server
Required modules - pycrypto
Open your terminal as root and execute the following commands

```apt-get install autoconf g++ python2.7-dev```

```pip install pycrypto```

# Usage
1. Run the server on your cloud or your local computer(if you are just testing it)
```
nohup python messenger_server.py &
```
2. Download the messenger_client folder to your computer and don't change the paths of any of the files.

Now, run the messenger_client.py by mentioning your server address as a sys argument
```
python messenger_server.py 127.0.0.1
```
For more info about this application, read my blog post at [Tech Raj Blog](https://blog.techraj156.com/).
