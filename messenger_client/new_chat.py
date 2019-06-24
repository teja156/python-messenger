#new_chat.py
from __future__ import print_function
import sys
import socket
import threading
import os
import time

if os.name=="nt":
    import keyboard
else:
    from pynput.keyboard import Key, Listener

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
recepient_username = None
taking_input = False


def on_press(key):
    pass

def on_release(key):
    try:
        if key==key.ctrl or key==key.ctrl_l or key==key.ctrl_r:
            global taking_input
            if(taking_input==False):
                res = sendmessage()
            if(taking_input==True):
                print("Already taking input...")
            if(res==1):
                return False
    except:
        pass
    

def hotkey():
    #Thread that listens for the ctrl key
    listener = Listener(on_press=on_press,on_release=on_release)
    listener.daemon = True
    listener.start()
    
      
def new_chat(op,rec_uname,msg):
    print(bcolors.OKGREEN+"Chatting with %s\n"%rec_uname+bcolors.ENDC)
    print(bcolors.OKBLUE+"To write a message, press Ctrl. After writing, hit Enter to send it"+bcolors.ENDC)
    
    print(bcolors.OKBLUE+"Type :quitchat to quit the chat.\n"+bcolors.ENDC)
    print(bcolors.WARNING+"Warning : Chat windows can open even if the user is not online, watch the main window to see if the user is online or not.\n"+bcolors.ENDC)
    
    op = int(op)
    if(op==1):
        print(bcolors.OKGREEN+rec_uname+bcolors.BOLD+" says hello"+bcolors.ENDC)
        #print(bcolors.OKGREEN+rec_uname+":~ "+msg+bcolors.ENDC)
    elif(op==2):
        print(bcolors.OKBLUE+"YOU:~ hello"+bcolors.ENDC)
        
    global recepient_username
    recepient_username = rec_uname
    sock.send("{'init_uname':'%s'}"%rec_uname)
    listen()

    
def sendmessage():
    global taking_input
    taking_input = True
    inp = raw_input(bcolors.OKBLUE+"Write your message now\n"+bcolors.ENDC)
    inp.replace("'"," ")
    inp.replace(":"," ")
    inp.replace('"',' ')
    if(inp=="" or inp==None):
        print("No message sent")
    elif(inp==":quitchat"):
        print(bcolors.OKBLUE+"Quitting chat...")
        sock.send(":quitchat")
        sock.close()
        return 1
        
    else:
        outp = "{'rec_uname':'%s','msg':'%s'}"%(recepient_username,inp)
        try:
            sock.send(outp)
        except:
            print(bcolors.FAIL+"Chat window can't run!"+bcolors.ENDC)
            sys.exit(0)
            
        sys.stdout.write("\033[F") #back to previous line
        sys.stdout.write("\033[K") #clear line
        sys.stdout.write("\033[F") #back to previous line
        sys.stdout.write("\033[K") #clear line
        print(bcolors.OKBLUE+bcolors.BOLD+"YOU:~ "+bcolors.OKBLUE+inp+bcolors.ENDC)
    taking_input = False
    return 0

    
def listen():
    while True:
        data = sock.recv(1024)
        if(not(data)):
            print(bcolors.FAIL+"Chat window can't run!"+bcolors.ENDC)
            sys.exit(0)
            
        if(data.encode("utf-8")==":quitchat"):
            print("\n"+bcolors.OKBLUE+recepient_username+" has left the chat!"+bcolors.ENDC)
            time.sleep(2)
            sock.close()
            sys.exit(0)
        
        global taking_input
        
        if(taking_input==True):
            sys.stdout.write("\033[F") #back to previous line
            sys.stdout.write("\033[K") #clear the current line
            #print the msg, display >> on next line and stay on same line
            print(bcolors.OKGREEN+recepient_username+":~ "+data.encode("utf-8")+bcolors.ENDC+bcolors.OKBLUE+"\nWrite your message now\n ",end="")
        else:
            #print msg normally
            print(bcolors.OKGREEN+bcolors.BOLD+recepient_username+":~ "+data.encode("utf-8")+bcolors.ENDC)
        

if __name__=="__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        sock.connect(('127.0.0.1',10000)) #dont change these values
    except:
        print(bcolors.FAIL+"Chat window cannot be opened!"+bcolors.ENDC)
        sys.exit(0)
    if(len(sys.argv)==4):
        #listen for hot keys
        
        if os.name=='nt':
            shortcut = 'ctrl' #define your hot-key
            keyboard.add_hotkey(shortcut, sendmessage) #<-- attach the function to hot-key
        else:
            hotkey()#use pynput for mac and linux
            
        new_chat(sys.argv[1],sys.argv[2],sys.argv[3])
    else:
        print("This script must not be run manually, it is used by the main script to open new chat windows!")
