nama = input("Masukkan nama: ")
nilai = float(input("Masukkan nilai: "))

if nilai < 0 or nilai > 100:
    print("Nilai Gak valid!")
elif nilai >= 85:
    print("Nama: ", nama)
    print("status: Lulus" )
    print("Predikat: A")
elif nilai >= 75:
    print("Nama: ", nama)
    print("status: Lulus" )
    print("Predikat: B")
elif nilai >= 65:
    print("Nama: ", nama)
    print("status: Lulus" )
    print("Predikat: C")
else:
    print("Nama: ", nama)
    print("status: Tidak Lulus" )
    print("Predikat: D")