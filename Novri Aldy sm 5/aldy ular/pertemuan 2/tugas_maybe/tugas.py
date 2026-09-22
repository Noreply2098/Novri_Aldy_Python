import math

print("=== PROGRAM MENGHITUNG BANGUN DATAR ===")
print("1. Persegi")
print("2. Persegi Panjang")
print("3. Segitiga")
print("4. Lingkaran")
print("5. Trapesium")
print("6. Jajargenjang")

pilihan = int(input("Pilih bangun datar (1-6): "))

if pilihan == 1:
    # Persegi
    sisi = float(input("Masukkan sisi: "))

    luas = sisi * sisi
    keliling = 4 * sisi

    print("Luas =", luas)
    print("Keliling =", keliling)

elif pilihan == 2:
    # Persegi Panjang
    panjang = float(input("Masukkan panjang: "))
    lebar = float(input("Masukkan lebar: "))

    luas = panjang * lebar
    keliling = 2 * (panjang + lebar)

    print("Luas =", luas)
    print("Keliling =", keliling)

elif pilihan == 3:
    # Segitiga
    alas = float(input("Masukkan alas: "))
    tinggi = float(input("Masukkan tinggi: "))

    luas = 0.5 * alas * tinggi

    print("Luas =", luas)

elif pilihan == 4:
    # Lingkaran
    jari_jari = float(input("Masukkan jari-jari: "))

    luas = math.pi * jari_jari ** 2
    keliling = 2 * math.pi * jari_jari

    print("Luas =", luas)
    print("Keliling =", keliling)

elif pilihan == 5:
    # Trapesium
    sisi_a = float(input("Masukkan sisi sejajar a: "))
    sisi_b = float(input("Masukkan sisi sejajar b: "))
    tinggi = float(input("Masukkan tinggi: "))

    luas = 0.5 * (sisi_a + sisi_b) * tinggi

    print("Luas =", luas)

elif pilihan == 6:
    # Jajargenjang
    alas = float(input("Masukkan alas: "))
    tinggi = float(input("Masukkan tinggi: "))

    luas = alas * tinggi

    print("Luas =", luas)

else:
    print("Pilihan tidak tersedia.")