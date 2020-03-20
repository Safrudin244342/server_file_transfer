"""
aplikasi ini untuk menangani pengiriman file banyak
tergantung file mana yang diinginkan oleh user
aplikasi ini juga bisa menerima file yang dikirim oleh user
"""

import socket
import threading
import os

# deklarasi variable yang akan digunakan
class variable:
    proses = True
    list_client = []
    dir_pusat = "sample_file"

# deklarasi port server
s = socket.socket()
s.bind(("localhost", 900))
s.listen()

# function built in
def client_service(sc, address):
    while variable.proses:
        # menerima permintaan dari client
        command = sc.recv(1024).decode()

        # menecek apakah single command atau multi command
        tmp_command = command.split(" ")
        if len(tmp_command) > 1:
            command = tmp_command

        if command[0] == 'download':
            # cek apakah file ada
            if os.path.exists(variable.dir_pusat + "/" + command[1]):
                # membaca file yang akan dikirim
                send_file = open(variable.dir_pusat + "/" + command[1], 'rb')

                # membuat header
                size_file = os.path.getsize(variable.dir_pusat + "/" + command[1])
                header = command[1] + "@" + str(size_file)
                header = header.encode()
                sc.send(header)

                # cek besar file yang akan dikirim
                if size_file >= 1024:
                    bit = send_file.read(1024)
                    while bit:
                        sc.send(bit)
                        bit = send_file.read(1024)

                    # membuat footer, menunjukan semua file telah dikirim
                    footer = "finish"
                    sc.send(footer.encode())
                else:
                    sc.send(send_file.read(size_file))
            else:
                # jika file tidak ada
                sc.send(b'file not exists')
        elif command == 'list':
            # mengirimkan daftar file yang terdapat di server
            list_file = os.listdir(variable.dir_pusat)
            list_file = list(filter(lambda file: os.path.isfile(variable.dir_pusat + "/" + file), list_file))
            str_list_file = "@".join(list_file)
            if len(list_file) > 0:
                list_file = bytearray(str_list_file, 'utf-8')
                sc.send(list_file)
            else:
                sc.send(b'Not File In Server')

        elif command[0] == 'send':
            # menerima header
            header = sc.recv(1024).decode()

            if header == 'file not exists':
                # jika file yang akan didownload tidak ada
                print(header)
            else:
                nama, size_file = header.split("@")
                size_file = int(size_file)
                # membuat file baru untuk file yang akan didownload
                recv_file = open(variable.dir_pusat + "/" + nama, "wb")

                # cek ukuran file
                if size_file >= 1024:
                    bit = sc.recv(1024)
                    while bit:
                        size_file -= 1024

                        # cek apakah semua file telah diterima
                        if bit != b'finish':
                            recv_file.write(bit)
                        else:
                            break

                        # menerima setiap bytes dari server
                        if size_file >= 1024:
                            bit = sc.recv(1024)
                        elif size_file > 0:
                            bit = sc.recv(size_file)
                        else:
                            bit = sc.recv(1024)
                else:
                    recv_file.write(sc.recv(size_file))

                recv_file.close()

        else:
            # mengirim perintah bahwa command tidak terdaftar
            sc.send(b'command not exists')

def list_client(s):
    while variable.proses:
        sc, address = s.accept()
        threading.Thread(target=client_service, args=(sc, address)).start()
        variable.list_client.append(sc)


# memulai thread untuk mendata semua client yang aktif
threading.Thread(target=list_client, args=(s, )).start()

while True:
    command = input("Bening > ")
    if command == 'stop':
        variable.proses = False
        s.close()
        list(map(lambda sc: sc.close(), variable.list_client))
        break

