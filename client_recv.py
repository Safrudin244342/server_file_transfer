"""
aplikasi untuk mengambil dan mengirim file kedalam server
"""

import socket
import os

s = socket.socket()
s.connect(("localhost", 900))

# memulai sesi untuk berhubungan dengan server
while True:
    commad = input("Bening > ").encode()
    s.send(commad)
    commad = commad.decode()

    # cek apakah command singgle atau multi
    tmp_commad = commad.split(" ")
    if len(tmp_commad) > 1:
        commad = tmp_commad

    # menampilkan sesuai permintaan client
    if commad == 'list':
        # menerima balasan dari server
        bit = s.recv(1024).decode()

        # jika client meminta daftar file yang bisa di akses
        bit = bit.split("@")
        for file in bit:
            print(file)

    elif commad[0] == "download":
        # menerima header
        header = s.recv(1024).decode()

        if header == 'file not exists':
            # jika file yang akan didownload tidak ada
            print(header)
        else:
            nama, size_file = header.split("@")
            size_file = int(size_file)
            # membuat file baru untuk file yang akan didownload
            recv_file = open("recv_file/" + nama, "wb")

            # cek ukuran file
            if size_file >= 1024:
                bit = s.recv(1024)
                while bit:
                    size_file -= 1024

                    # cek apakah semua file telah diterima
                    if bit != b'finish':
                        recv_file.write(bit)
                    else:
                        break

                    # menerima setiap bytes dari server
                    if size_file >= 1024:
                        bit = s.recv(1024)
                    elif size_file > 0:
                        bit = s.recv(size_file)
                    else:
                        bit = s.recv(1024)
            else:
                recv_file.write(s.recv(size_file))

            recv_file.close()

            print(nama + " berhasil di download")

    elif commad[0] == "send":

        commad, nama = commad

        # cek apakah file ada
        if os.path.exists(nama):
            # membaca file yang akan dikirim
            send_file = open(nama, 'rb')

            # membuat header
            size_file = os.path.getsize(nama)
            header = nama + "@" + str(size_file)
            header = header.encode()
            s.send(header)

            # cek besar file yang akan dikirim
            if size_file >= 1024:
                bit = send_file.read(1024)
                while bit:
                    s.send(bit)
                    bit = send_file.read(1024)

                # membuat footer, menunjukan semua file telah dikirim
                footer = "finish"
                s.send(footer.encode())
            else:
                s.send(send_file.read(size_file))

            print("file telah dikirim")
        else:
            # jika file tidak ada
            s.send(b'file not exists')

    else:
        # jika command tidak terdaftar
        print(s.recv(1024).decode())