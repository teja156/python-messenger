#messenger_client.py
import socket
import threading
import sys
import ast
import getpass
import time
import signal
import os
import platform
import subprocess
import random
import encryption
import codecs

if(not(os.name=="nt")):
    import appscript


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
username = None
server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
commands = {":login" : "Login to an existing account", ":register" : "Create an account",":chat" : "Chat with an online user",":showonline" : "Show online users", ":logout" : "Logout from the account",":quitchat":"Quit chat"}
chats = dict()

def print_to_screen(op,color,msg):
    lock = threading.Lock()
    try:
        if(op==1):
            lock.acquire()
            print(color + msg + bcolors.ENDC)
            lock.release()
            return
        elif(op==2):
            inp = raw_input(color+msg+bcolors.ENDC)
            return inp
    except:
        #lock.release()
        return
    
    
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    
def show_commands_menu():
    print(bcolors.OKBLUE+"\nCOMMANDS - "+bcolors.ENDC)
    for i in commands:
        if i==":login" or i==":register" or i==":quitchat":
            continue
        print(bcolors.OKGREEN+i+" --> "+bcolors.BOLD+commands[i]+bcolors.ENDC)
    
    print(bcolors.OKGREEN+"Hold Ctrl+C to terminate the program anytime you want.\n"+bcolors.ENDC)
        

def show_online():
    try:
        data_to_send = "{'cmd':'showonline'}"
        cipher = encryption.encrypt(data_to_send,"serverkey.pem",publickey=None) #encrypt with server's public key
        signature = encryption.signature(data_to_send,"keypriv")
        outp = "{'cipher':'%s','signature':'%s'}"%(cipher,signature)
        sock.send(outp)

    except:
        print(bcolors.FAIL+"Couldn't communicate with the server :("+bcolors.ENDC)
        return 0    
    

def register():
    while True:
        uname = raw_input(bcolors.OKBLUE+"Choose a username : "+bcolors.ENDC)
        passwd = getpass.getpass(bcolors.OKBLUE+"Enter Password : "+bcolors.ENDC)
        retype_passwd = getpass.getpass(bcolors.OKBLUE+"Re-type Password : "+bcolors.ENDC)

        if(passwd==retype_passwd):
            break
        else:
            print(bcolors.FAIL+"Passwords donot match, try again."+bcolors.ENDC)
    try:
        data_to_send = "{'cmd':'register','uname':'%s','passwd':'%s'}"%(uname,passwd)
        cipher = encryption.encrypt(data_to_send,"serverkey.pem",publickey=None) #encrypt with server's public key
        signature = encryption.signature(data_to_send,"keypriv")
        outp = "{'cipher':'%s','signature':'%s'}"%(cipher,signature)

        sock.send(outp)
        global username
        username = uname
    except:
        print(bcolors.FAIL+"Couldn't communicate with the server :("+bcolors.ENDC)
        return 0
    
    try:
        data = sock.recv(1024)
    except:
        print(bcolors.FAIL+"No response received from the server :("+bcolors.ENDC)
        return 0
    
    data = ast.literal_eval(data.encode("utf-8"))
    cipher = data["cipher"]
    signature = data["signature"]
    resp=""
    resp_type=""
    
    hex_decode = codecs.getdecoder("hex")
    cipher = hex_decode(cipher)[0]
    signature = hex_decode(signature)[0]
    
    f = open("serverkey.pem", "rb")
    publickey = f.read()
    f.close()
    
    #check authenticity now
    resp = encryption.decrypt(cipher,"keypriv.pem")
    authenticated = encryption.check_authenticity(resp,signature,publickey)
    
    if(authenticated==1):
        #authentication successful
        print("Autheticity verified")
    elif(authenticated==0):
        print(bcolors.FAIL+"Authenticity of the message can't be verified!"+bcolors.ENDC)
        return 0
    
    resp = ast.literal_eval(resp.encode())
    resp_type = resp["resp_type"]
    
    if resp_type=="SUCC":
        global username
        username = uname
        print(bcolors.OKGREEN+"Logged in as "+bcolors.BOLD+username+bcolors.ENDC)
        return 1
    
    elif resp_type=="FAIL":
        print(bcolors.FAIL+"Can't register, try another username!"+bcolors.ENDC)
        return 0
    
    return 1



def login():
    uname = raw_input(bcolors.OKBLUE+"Enter username : "+bcolors.ENDC)
    passwd = getpass.getpass(bcolors.OKBLUE+"Enter Password : "+bcolors.ENDC)
    try:
        data_to_send = "{'cmd':'login','uname':'%s','passwd':'%s'}"%(uname,passwd)
        cipher = encryption.encrypt(data_to_send,"serverkey.pem",publickey=None) #encrypt with server's public key
        signature = encryption.signature(data_to_send,"keypriv")
        outp = "{'cipher':'%s','signature':'%s'}"%(cipher,signature)
        sock.sendall(outp)
    except Exception as e:
        print(bcolors.FAIL+"An error occured :("+bcolors.ENDC)
        print(e)
        return 0
    
    try:
        data = sock.recv(1024)
    except:
        print(bcolors.FAIL+"No response received from the server :("+bcolors.ENDC)
        return 0
        
    data = ast.literal_eval(data.encode("utf-8"))
    cipher = data["cipher"]
    signature = data["signature"]
    resp=""
    resp_type=""
    
    hex_decode = codecs.getdecoder("hex")
    cipher = hex_decode(cipher)[0]
    signature = hex_decode(signature)[0]
    
    
    f = open("serverkey.pem","r")
    publickey = f.read()
    f.close()
    #check authenticity now
    resp = encryption.decrypt(cipher,"keypriv.pem")
    authenticated = encryption.check_authenticity(resp,signature,publickey)
    
    if(authenticated==1):
        #authentication successful
        pass
    elif(authenticated==0):
        print(bcolors.FAIL+"Authenticity of the message can't be verified!"+bcolors.ENDC)
        return 0
    
    resp = ast.literal_eval(resp.encode())
    resp_type = resp["resp_type"]

    if resp_type=="SUCC":
        clear_screen()
        global username
        username = uname
        print(bcolors.OKGREEN+"Logged in as "+bcolors.BOLD+username+bcolors.ENDC)
        return 1
    
    elif resp_type=="FAIL":
        print(bcolors.FAIL+"Can't log in!"+bcolors.ENDC)
        return 0
    
def send():
    while True:
        inp = print_to_screen(2,bcolors.OKBLUE,">>")
        if(not(inp=="" or inp==None)):
            if not(inp in commands):
                print_to_screen(1,bcolors.FAIL,"Invalid command!")
                continue

            elif inp==":chat":
                global username
                if(username==None):
                    print_to_screen(1,bcolors.FAIL,"User is not logged in, or not properly configured!")
                    sys.exit(0)

                from_uname = username
                to_uname = print_to_screen(2,bcolors.OKBLUE,"Enter username to chat with >>")
                msg = "talk."
                
                try:
                    data_to_send = "{'cmd':'msg','from_uname':'%s','to_uname':'%s','msg':'%s'}"%(from_uname,to_uname,msg)
                    cipher = encryption.encrypt(data_to_send,"serverkey.pem",publickey=None) #encrypt with server's public key
                    signature = encryption.signature(data_to_send,"keypriv") #sign with client's private key
                    outp = "{'cipher':'%s','signature':'%s'}"%(cipher,signature)
                    sock.send(outp)
                except Exception as e:
                    print_to_screen(1,bcolors.FAIL,"Couldn't communicate with the server!")
                    print(e)

                #open new chat window now
                startchat(2,to_uname,msg)
                    
            elif inp==":showonline":
                show_online()
                

            elif inp==":logout":
                global username
                try:
                    data_to_send = "{'cmd':'logout','uname':'%s'}"%(username)
                    cipher = encryption.encrypt(data_to_send,"serverkey.pem",publickey=None) #encrypt with server's public key
                    signature = encryption.signature(data_to_send,"keypriv")
                    outp = "{'cipher':'%s','signature':'%s'}"%(cipher,signature)
                    sent = sock.send(outp)
                    
                    if(not(sent==0)):
                        print(bcolors.OKGREEN+"Logged out succesfully!"+bcolors.ENDC)
                    else:
                        print(bcolors.FAIL+"Can't logout"+bcolors.ENDC)
                            
                except Exception as e:
                    print_to_screen(1,bcolors.FAIL,"Couldn't communicate with the server!")
                    print(e)
                    
            else:
                try:
                    data_to_send = "{'cmd':'%s'}"%inp[1:len(inp)]
                    cipher = encryption.encrypt(data_to_send,"serverkey.pem",publickey=None) #encrypt with server's public key
                    signature = encryption.signature(data_to_send,"keypriv")
                    outp = "{'cipher':'%s','signature':'%s'}"%(cipher,signature)
                    sent = sock.send(outp)
                except:
                    print_to_screen(1,bcolors.FAIL,"Couldn't communicate with the server!")
                    
        else:
            continue
                    
                    

def new_chat(platform,uname,msg,op):
    #open a new chat window
    path = os.path.abspath("messenger_client.py")

    if(platform.upper()=="WINDOWS"):
        lastindex = len(path) - path[::-1].index("\\") - 1
        path = path[0:lastindex+1]
        path = "new_chat.py"
        os.system("start /wait cmd /c python %s %d %s %s"%(path,op,uname,msg))
    
    elif(platform.upper()=="DARWIN"):
        #MACOS
        lastindex = len(path) - path[::-1].index("/") - 1
        path = path[0:lastindex+1]
        path = path + "new_chat.py"
        appscript.app('Terminal').do_script('python %s %d %s %s'%(path,op,uname,msg))
    
    elif(platform.upper()=="LINUX"):
        lastindex = len(path) - path[::-1].index("/") - 1
        path = path[0:lastindex+1]
        path = path + "new_chat.py"
        subprocess.call(['gnome-terminal', '-x', 'python %s %d %s %s'%(path,op,uname,msg)])
    
    else:
        print_to_screen(1,bcolors.FAIL,"Your platform is not recognized, sorry!")
        return
    

    
def startchat(op,rec_uname,msg):
    global chats
    if(rec_uname in chats):
        c_destination = chats[rec_uname]
        c_destination.send(msg) #send message to chat window
        
    else:
        #open new chat window to show messages
        sys_platform = platform.system()
        thr = threading.Thread(target=new_chat,args=((sys_platform,rec_uname,msg,op)))
        thr.daemon = True
        thr.start()
        print_to_screen(1,bcolors.OKBLUE,"Chat window opened!\n")
  
        
    
def start_chat_thread(c,a):
    global chats
    while True:
        try:
            data = c.recv(1024)
            print(data)
            if(not(data) or data.encode("utf-8")==":quitchat"):
                for i in chats:
                    if chats[i]==c:
                        del chats[i]
                        quitchat(i)
                        break
                print_to_screen(1,bcolors.FAIL,"Chat window closed!")
                return
            
            else:
                data = ast.literal_eval(data.encode("utf-8"))
                if("init_uname" in data):
                    #if username exits in chat dictionary, it means the chat window is open
                    rec_uname = data["init_uname"]
                    chats[rec_uname] = c

                else:
                    #just sending messages
                    print("Message : ",data)
                    #forward msg to server
                    rec_uname= data['rec_uname']
                    msg = data['msg']
                    sendmessage(msg,rec_uname)
                    
        except:
            print_to_screen(1,bcolors.FAIL,"Chat window closed")
            for i in chats:
                if chats[i]==c:
                    del chats[i]
                    quitchat(i)
                    break
            return
            

def sendmessage(msg,rec_uname):
    data_to_send = "{'cmd':'msg','from_uname':'%s','to_uname':'%s','msg':'%s'}"%(username,rec_uname,msg)
    cipher = encryption.encrypt(data_to_send,"serverkey.pem",publickey=None) #encrypt with server's public key
    signature = encryption.signature(data_to_send,"keypriv")
    outp = "{'cipher':'%s','signature':'%s'}"%(cipher,signature)
    sock.send(outp)
                
        
def quitchat(rec_uname):
    global username
    data_to_send = "{'cmd':'quitchat','rec_uname':'%s','from_uname':'%s'}"%(rec_uname,username)
    cipher = encryption.encrypt(data_to_send,"serverkey.pem",publickey=None) #encrypt with server's public key
    signature = encryption.signature(data_to_send,"keypriv")
    outp = "{'cipher':'%s','signature':'%s'}"%(cipher,signature)
    sock.send(outp)


def listen():
    while True:
        try:
            data = sock.recv(1024)
            if not(data):
                print_to_screen(1,bcolors.FAIL,"Connection terminated by the server :(")
                return 1
            
            data = ast.literal_eval(data.encode("utf-8"))
            cipher = data["cipher"]
            signature = data["signature"]
            hex_decode = codecs.getdecoder("hex")
            cipher = hex_decode(cipher)[0]
            signature = hex_decode(signature)[0]
            resp=""
            resp_type=""
            
            f = open("serverkey.pem", "rb")
            publickey = f.read()
            f.close()
            
            #check authenticity now
            resp = encryption.decrypt(cipher,"keypriv.pem") #decrypt with private key
            authenticated = encryption.check_authenticity(resp,signature,publickey) #public key of server
            
            if(authenticated==1):
                #authentication successful
                pass
            elif(authenticated==0):
                print(bcolors.FAIL+"Authenticity of the message can't be verified!"+bcolors.ENDC)
                return 0
            
            resp = ast.literal_eval(resp.encode("utf-8"))
            
            resp_type = resp["resp_type"]
    
            if(resp_type=="FAIL"):
                err_msg = resp["resp"]
                print_to_screen(1,bcolors.FAIL,"An Error Occured - "+bcolors.OKBLUE+"%s"%(err_msg))
            
            elif(resp_type=="SUCC"):
                succ_msg = resp["resp"]
                clear_screen()
                print_to_screen(1,bcolors.OKGREEN,"Success - "+bcolors.OKBLUE+"%s"%(succ_msg))
                print("\n")                
                
            elif(resp_type=="msg"):
                global chats
                from_uname = resp["from_uname"]
                msg = resp["msg"]
            
                time.sleep(1)
                
                if(from_uname in chats):
                    startchat(1,from_uname,msg)
                else:
                    print_to_screen(1,bcolors.OKBLUE,"A new message received from %s, hit enter to see"%from_uname)
                    open_msg = print_to_screen(2,bcolors.OKBLUE,"Open?(Y/N) : ")
                    while True:
                        if(open_msg.upper()=="Y"):
                            startchat(1,from_uname,msg)
                            break
                        elif(open_msg.upper()=="N"):
                            break
                        else:
                            print_to_screen(1,bcolors.FAIL,"Invalid option, please enter again.")  
            
            elif(resp_type=="users"):
                online_users = resp["resp"]
                print_to_screen(1,bcolors.OKBLUE,"\nONLINE USERS : \n"+bcolors.ENDC)
                users = ""
                for i in online_users:
                    if(i==""):
                        continue
                    users = users + str(i) + "\n"
                print_to_screen(1,bcolors.FAIL,users)
                            
            elif(resp_type=="quitchat"):
                uname = resp["resp"]
                if(uname in chats):
                    c_destination = chats[uname]
                    c_destination.send(":quitchat")
                    
                            
            else:
                pass
            
                            
        except KeyboardInterrupt:
            print(bcolors.FAIL+"Connection closed by user."+bcolors.ENDC)
            return 1
            sys.exit(0)
            break
            
def handshake():
    #First generate and send the public key to the server
    publickey = encryption.genkeys("keypub","keypriv")
    sock.send(publickey)
    #Now listen for the public key from the server
    publickey = sock.recv(2048)
    
    f = open("serverkey.pem","w")
    f.write(publickey)
    f.close()
    
    if(len(publickey)!=0):
        return 1
    else:
        return 0


def manage_chat_threads():
    while True:
        try:
            c1,a1 = server_sock.accept()
            chat_thread = threading.Thread(target=start_chat_thread,args=(c1,a1))
            chat_thread.daemon = True
            chat_thread.start()
        except KeyboardInterrupt:
            print(bcolors.OKBLUE+"\nProgram terminated by the user, see you again :)"+bcolors.ENDC)
            sys.exit(0)
    

def start_client():
    clear_screen()
    print(bcolors.OKBLUE+"Trying to connect and handshake with the server..."+bcolors.ENDC)
    
    try:
        server_sock.bind(('127.0.0.1',10000))
        server_sock.listen(10)
    except Exception as e:
        print(bcolors.FAIL+"Couldn't start the client!"+bcolors.ENDC)
        print(e)
        sys.exit(0)
    
    try:
        addr = sys.argv[1]
        sock.connect((addr,1560))
        handshake_status = handshake()
        if(handshake_status==1):
            clear_screen()
            print(bcolors.OKGREEN + "Connected to messenger server succesfully :)" + bcolors.ENDC)
        elif(handshake_status==0):
            print(bcolors.FAIL+"Couldn't connect to messenger server!"+ bcolors.ENDC)
            sys.exit(1)  
    except Exception as e:
        print(bcolors.FAIL+"Couldn't connect to messenger server!"+ bcolors.ENDC)
        print(e)
        sys.exit(1)
    
    print(bcolors.OKBLUE+"\nCOMMANDS - "+bcolors.ENDC)
    print(bcolors.OKGREEN+":login"+bcolors.BOLD+"              -login to exisitng account"+bcolors.ENDC)
    print(bcolors.OKGREEN+":register"+bcolors.BOLD+"           -create an account"+bcolors.ENDC)
    
    print("\n")
    
    while True:
        cmd = raw_input(bcolors.OKBLUE+"Enter a command >> "+bcolors.ENDC)
        if(cmd==":login"):
            logged_in = login()
            if(logged_in==1):
                clear_screen()
                global username
                print(bcolors.OKGREEN+"Logged in as "+bcolors.BOLD+username+bcolors.ENDC)
                break
            else:
                print("Not logged in yet")
            
        elif(cmd==":register"):
            registered = register()
            if(registered==1):
                clear_screen()
                global username
                print(bcolors.OKGREEN+"Logged in as "+bcolors.BOLD+username+bcolors.ENDC)
                break
            else:
                print("Not logged in yet")
            
        else:
            print(bcolors.FAIL+"Not a valid command!"+bcolors.ENDC)
            continue
            
            
    #Two threads -
    #one thread to listen for data
    #another thread to send data
    
    show_commands_menu()
    thr1 = threading.Thread(target=listen)
    thr2 = threading.Thread(target=send)
    
    thr1.daemon = True
    thr2.daemon = True
    thr1.start()
    thr2.start()
    
    
    #there is no need to use a new thread here, instead manage_chat_threads can be directly run without starting a child thread. But, since the 
    #keyboardinterrupt is not being caught properly in windows, I had to use a thread here, and then later handle keyboardinterrupt with an  
    #infinite while loop that only stops when keyboardinterrupt is captured
    
    chat_thread_manager = threading.Thread(target=manage_chat_threads)
    chat_thread_manager.daemon = True
    chat_thread_manager.start()
    
    while True:
        try:
            time.sleep(2)
        except KeyboardInterrupt:
            print(bcolors.FAIL+"Program terminated by user, see you again :("+bcolors.ENDC)
            sys.exit()
            
            
if __name__ == "__main__":
    start_client()
    
