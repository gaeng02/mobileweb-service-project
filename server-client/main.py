import os
import socket
from datetime import datetime

class SocketServer :

    def __init__ (self) :
        self.bufsize = 1024
        with open("./response.bin", "rb") as file :
            self.RESPONSE = file.read()

        self.DIR_PATH = "./request"
        self.createDIR(self.DIR_PATH)

        self.IMG_PATH = "./images"
        self.createDIR(self.IMG_PATH)

    def createDIR (self, path) :
        try :
            if not os.path.exists(path) :
                os.makedirs(path)

        except OSError :
            print("Error. Failed to create the directory.")

    def run (self, ip, port) :
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)
        
        print("Start the socket server...")
        print("('Ctrl+C' for stopping the server!)\n")

        try :
            while True :
                clnt_sock, req_addr = self.sock.accept()
                clnt_sock.settimeout(5.0)
                print("Request message...\n")

                ### 실습 1
                raw = b""

                try:
                    while True :
                        chunk = clnt_sock.recv(self.bufsize)
                        if not chunk : break
                        raw += chunk

                except socket.timeout :
                    pass

                timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                raw_path = os.path.join(self.DIR_PATH, f"{timestamp}.bin")
                with open(raw_path, "wb") as file :
                    file.write(raw)
                print("SAVE Request : ", raw_path)

                i = raw.find(b"\r\n\r\n")
                if (i != -1) :
                    headers = bytes(raw[:i])
                    body    = bytes(raw[i+4:])

                    boundary = None
                    for line in headers.split(b"\r\n") :
                        low = line.lower()
                        if low.startswith(b"content-type:") and (b"boundary=" in low) :
                            bpos = low.find(b"boundary=") + len(b"boundary=")
                            val  = line[bpos:].strip()
                            if (b";" in val) :
                                val = val.split(b";", 1)[0].strip()
                            if (len(val) >= 2) and (val[:1] == b'"') and (val[-1:] == b'"') :                               val = val[1:-1]
                            boundary = b"--" + val
                            break

                    if boundary :
                        for part in body.split(boundary) :
                            if not part or part in (b"--", b"--\r\n") :
                                continue
                            j = part.find(b"\r\n\r\n")
                            if j == -1 :
                                continue
                            phead = part[:j]
                            pbody = part[j+4:]

                            plow = phead.lower()
                            if (b"content-type: image/" in plow) and (b"filename=" in plow) :
                                fn = b"upload.bin"
                                key = b"filename="
                                k  = plow.find(key)
                                if (k != -1) :
                                    start = k + len(key)
                                    if (phead[start:start+1] == b'"') :
                                        start += 1
                                        end = phead.find(b'"', start)
                                        if (end != -1) :
                                            fn = phead[start:end]
                                    else :
                                        end = phead.find(b";", start)
                                        if (end == -1) :
                                            end = phead.find(b"\r\n", start)
                                        if (end == -1) :
                                            end = len(phead)
                                        fn = phead[start:end].strip()

                                if pbody.endswith(b"\r\n") :
                                    pbody = pbody[:-2]

                                img_path = os.path.join(self.IMG_PATH, f"{timestamp}_{os.path.basename(fn).decode('utf-8','ignore')}")
                                with open(img_path, "wb") as file :
                                    file.write(pbody)
                                print("SAVE Image : ", img_path)
                                break

                clnt_sock.sendall(self.RESPONSE)

                clnt_sock.close()
                
        except KeyboardInterrupt :
            print("\nStop the server...")
            
        finally :
            self.sock.close()


if (__name__ == "__main__") :
    
    server = SocketServer()
    server.run("127.0.0.1", 8000)
