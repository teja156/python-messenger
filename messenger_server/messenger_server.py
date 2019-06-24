import socket
import threading
import ast
import sqlite3
import os.path
from os import path
import codecs
import encryption
import sys

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

sock.bind(('',1560))
sock.listen(10)

connections = list()
authorized_users = dict()
client_keys= dict()


def makedb():
    if(path.exists("users.db")):
        return 1
    else:
        conn = sqlite3.connect('users.db')
        conn.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, username varchar2(10),password varchar2(200))")
        
        
def showusers():
    print("Registered Users - ")
    conn = sqlite3.connect('users.db')
    cursor = conn.execute("select * from users")
    for i in cursor:
        print(i[0])
        print(i[1])
        print(i[2])
        print("\n")
        
        
        
def showonlineusers(c):
    online_users = list()
    
    #authorized_users contains all the users that are active now
    for i in authorized_users:
        online_users.append(i)

    outp = "{'resp_type':'users', 'resp':%s}"%str(online_users)
    
    send(outp,c)
    

def send(resp,c):
    #encrypts and sends
    data_to_send = resp
    publickey = client_keys[c]
    cipher = encryption.encrypt(data_to_send,fname=None,publickey=publickey) #encrypt with client's public key
    signature = encryption.signature(data_to_send,"server_keypriv")
    outp = "{'cipher':'%s','signature':'%s'}"%(cipher,signature)
    sent = c.send(outp)
    
    if(sent==0):
        print(bcolors.FAIL+"Can't send the data, connection closed by client"+bcolors.ENDC)
        return 0

    
def login(uname,passwd,c):
    print("logging in")
    conn = sqlite3.connect('users.db')
    try:
        cursor = conn.execute("SELECT username,password from users where username='%s' and password='%s'"%(uname,passwd))
        rowcount = len(cursor.fetchall())
        if(rowcount==1):
            #login success
            if not(uname in authorized_users):
                print("Login success")
                #c.send("SUCC:User succesfully authorized!")
                outp = "{'resp_type':'SUCC','resp':'User succesfully authorized!'}"
                send(outp,c)
                authorized_users[uname] = c
            else:
                print("User already logged in")
                #c.send("FAIL:User already logged in")
                outp = "{'resp_type':'FAIL','resp':'User already logged in'}"
                send(outp,c)
                
        elif(rowcount==0):
            #login fail
            print("Login fail")
            #c.send("FAIL:Wrong username/password")
            outp = "{'resp_type':'FAIL','resp':'Wrong username or password'}"
            send(outp,c)
    
    except Exception as e:
        print("Error - %s"%e)
        #c.send("FAIL:%s"%e)
        outp = "{'resp_type':'FAIL','resp':'%s'}"%e
        send(outp,c)
        c.close()
        
        
def register(uname,passwd,c):
    conn = sqlite3.connect('users.db')
    try:
        cursor = conn.execute("SELECT username from users where username='%s'"%(uname))
        rowcount = len(cursor.fetchall())
        print("Number of usrs with the username %s : "%uname,rowcount)
        if(rowcount==1):
            #User exists
            outp = "{'resp_type':'FAIL','resp':'Username already exists'}"
            send(outp,c)
        elif(rowcount==0):
            #Username available
            conn.execute("INSERT INTO users(username,password) values('%s','%s')"%(uname,passwd))
            conn.commit()
            conn.close()
            authorized_users[uname] = c
            print("User created!")
            outp = "{'resp_type':'SUCC','resp':'User created!'}"
            send(outp,c)
            
        

    except Exception as e:
        print("Error - %s"%e)
        outp = "{'resp_type':'FAIL','resp':'%s'}"%e
        send(outp,c)
        c.close()
            
            
def sendmessage(from_uname,to_uname,msg):

    #first check if the to_uname is online
    if not(to_uname in authorized_users):
        #User is not online
        outp = "{'resp_type':'FAIL','resp':'User doesnot exist or is not online!'}"
        send(outp,c)
    
    else:
        print("Authorized users : ",str(authorized_users))
        c_destination = authorized_users[to_uname]
        outp = "{'resp_type':'msg','from_uname':'%s','msg':'%s'}"%(from_uname,msg)
        send(outp,c_destination)
        

def quitchat(rec_uname,from_uname):
    c_destination = authorized_users[rec_uname]
    outp = "{'resp_type':'quitchat','resp':'%s'}"%from_uname
    send(outp,c_destination)

def logout(uname):
    if(uname in authorized_users):
        del authorized_users[uname]
        outp = "{'resp_type':'SUCC','resp':'User logged out succesfully'}"
        send(outp,c)
    else:
        outp = "{'resp_type':'FAIL','resp':'User already logged out!'}"
        send(outp,c)

    
def new_connection(c,a):
    #Accept data from the client
    while True:
        try:
            data = c.recv(1024)
        except Exception as e:
            print("Error - %s"%e)
            
        if(not(data)):
            print("Connection closed by client.\n")
            del connections[connections.index(c)]
            for i in authorized_users:
                if authorized_users[i]==c:
                    del authorized_users[i]
                    break
            break
            
        else:
            try:
                
                if "BEGIN PUBLIC KEY" in data:
                    #handshaking stage
                    client_keys[c] = data.encode() #add client public key to dictionary
                    print("Handshaking..")
                    f = open("server_keypriv.pem","rb")
                    server_publickey = f.read()
                    f.close()
                    c.send(server_publickey)
                    print("Sent public key")
                    
                else:
                    #print("\nData received : %s\n"%data)
                    data = ast.literal_eval(data)
                    #first check authenticity
                    cipher = data["cipher"]
                    signature = data["signature"]
                    publickey = client_keys[c].encode()
                    decode_hex = codecs.getdecoder("hex")
                    signature = decode_hex(signature)[0]
                    cipher = decode_hex(cipher)[0]
                    #check authenticity now
                    req =  encryption.decrypt(cipher,"server_keypriv.pem")
                    publickey = client_keys[c]
                    authenticated = encryption.check_authenticity(req,signature,publickey)#public key of client
                    req = ast.literal_eval(req.encode("utf-8"))
                    if(authenticated==1):
                        #authentication successful
                        cmd = req['cmd']
                        
                        if(cmd=='login'):
                            login(req['uname'],req['passwd'],c)

                        elif(cmd=='register'):
                            register(req['uname'],req['passwd'],c)

                        elif(cmd=='msg'):
                            sendmessage(req['from_uname'],req['to_uname'],req['msg'])

                        elif(cmd=='showonline'):
                            showonlineusers(c)

                        elif(cmd=='logout'):
                            logout(req["uname"])

                        elif(cmd=='quitchat'):
                            rec_uname =  req["rec_uname"]
                            from_uname = req["from_uname"]
                            #we need to tell rec_uname that from_uname has left the chat
                            for i in authorized_users:
                                if i==rec_uname:
                                    quitchat(i,from_uname)
                        
                        else:
                            outp = "{'resp_type':'FAIL','resp':'Invalid command'}"
                            send(outp,c)
                                
                    elif(authenticated==0):
                        print(bcolors.FAIL+"Authenticity of the message can't be verified!"+bcolors.ENDC)
                
            except Exception as e:
                print("Wrong format.")
                print(e)
    
    
        
if __name__ == "__main__":
    makedb()
    encryption.genkeys("server_keypub","server_keypriv")
    #showusers()
    
    while True:
        c,a = sock.accept()
        connections.append(c)
        thr = threading.Thread(target=new_connection,args=(c,a))
        thr.daemon = True
        thr.start()
