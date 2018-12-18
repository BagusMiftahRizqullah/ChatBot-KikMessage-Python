data=[]
pilih = "Y"
while pilih == "Y":
    print("Masukkan Data")
    npm = input("NPM =")
    nama = input("Nama =")
    alamat = input("Alamat =")
    a = data.append([npm,nama,alamat])
    pilih = input("Masukkan Data Lagi ? (Y/N) =")

a = data
b = input("cari npm =")

found=0
for x in range(len(a)):
    for y in range(len(a)):
        if a[x][y]==b:
            print(a[x])
            found=found+1
if found == 0 :
    print("tidak ditemukan")
