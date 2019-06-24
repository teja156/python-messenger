import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import ast
import hashlib
import codecs
from base64 import (
    b64encode,
    b64decode,
)


 
def genkeys(public_fname,private_fname):
    random_generator = Random.new().read
    key = RSA.generate(1024, random_generator) #generate pub and priv key
    public = key.publickey().exportKey('PEM').decode('ascii')
    private = key.exportKey('PEM').decode('ascii')
    f = open(private_fname+".pem","w")
    f.write(private)
    f.close()
    f = open(public_fname+".pem","w")
    f.write(public)
    f.close()
    return public

    
def encrypt(text,fname,publickey):
    if(publickey==None):
        publickey = RSA.importKey(open(fname, "rb"))
    else:
        publickey = RSA.importKey(publickey)
        
    
    hexify = codecs.getencoder("hex")
    encrypted = publickey.encrypt(text, 32)
    encrypted2 = hexify(encrypted[0])[0]
    return encrypted2
    
def decrypt(cipher,fname):
    privatekey = RSA.importKey(open(fname, "rb"))
    decrypted = privatekey.decrypt(str(cipher))
    return decrypted


def hash_string(text):
    digest = SHA256.new()
    digest.update(text)
    return digest

def signature(text,private_fname):
    digest = SHA256.new()
    digest.update(text)
    privatekey = RSA.importKey(open(private_fname+".pem", "rb"))
    signer = PKCS1_v1_5.new(privatekey)
    sig = signer.sign(digest)
    hexify = codecs.getencoder("hex")
    sig = hexify(sig)[0]
    return sig
    

def check_authenticity(text,signature,publickey):
    publickey = RSA.importKey(publickey.encode())
    verifier = PKCS1_v1_5.new(publickey)
    digest = SHA256.new()
    digest.update(text)
    verified = verifier.verify(digest, signature)
    
    if(verified):
        return 1
    else:
        return 0
    
