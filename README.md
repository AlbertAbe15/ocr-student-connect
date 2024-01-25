# Penjelasan OCR MyITS StudentConnect
Repository ini merupakan paduan dari penggunaan OCR untuk membantu verifikasi data sertifikat dan surat tugas dari portoflio kompetisi pada MyITS StudentConnect.

Endpoint yang disediakan adalah sebagai berikut

`http://127.0.0.1:5000/sertifikat_kompetisi`

`http://127.0.0.1:5000/surat_tugas`

### *1. http://127.0.0.1:5000/sertifikat_kompetisi*

API ini merupakan API untuk melakukan verifikasi terhadap dokumen sertifikat dari portofolio kompetisi pada MyITS StudentConnect. Adapun 
input yang dimasukkan adalah sebagai berikut
1. image_url: dokumen sertifikat mahasiswa yang diikuti oleh mahasiswa untuk kompetisi
2. nama_mahasiswa: nama mahasiswa yang terdaftar pada MyITS StudentConnect
3. nama_penyelenggara: nama penyelenggara kompetisi yang diikuti oleh mahasiswa
4. nama_kompetisi: nama kompetisi yang diikuti oleh mahasiswa
5. hasil_capaian: capaian yang diperoleh oleh mahasiswa pada kompetisi yang diikuti
6. tanggal_mulai: tanggal mulai kompetisi yang diikuti oleh mahasiswa
7. tanggal_selesai: tanggal selesai kompetisi yang diikuti oleh mahasiwa

```json
{
    "image_url": "http://storage-api.its.ac.id/public/8531f465fc3b4491ba9dc36d845059f6/011cbdff6b668fc02a81a5e307675eb9/NesiaAuraFebriyantiPuspaSari",
    "nama_mahasiswa": "Nesia",
    "nama_penyelenggara": "Universitas Lampung",
    "nama_kompetisi": "Lomba Esai Nasional Scolah Festival 2020",
    "hasil_capaian": "juara 1/emas",
    "tanggal_mulai": "14/09/2020",
    "tanggal_selesai": "08/11/2020"
}
```
apabila request pada api/sertifikat_kompetisi berhasil dijalankan, maka akan mengeluarkan output parameter verifikasi dengan value true yang berarti terverifikasi dan false yang berarti tidak terverifikasi. Berikut merupakan output dari api tersebut
1. Nama Mahasiswa: Hasil verifikasi antara nama mahasiswa yang terdapat pada MyITS StudentConnect dan sertifikat kompetisi
2. Nama Kompetisi: Hasil verifikasi antara nama kompetisi yang terdapat pada MyITS StudentConnect dan sertifikat kompetisi
3. Nama Penyelenggara: Hasil verifikasi antara nama penyelenggara kompetisi yang terdapat pada MyITS StudentConnect dan sertifikat kompetisi
4. Tanda Tangan: Hasil verifikasi dari pejabat yang menandatangani sertifikat kompetisi
5. Capaian: Hasil verifikasi antara hasil capaian yang terdapat pada MyITS StudentConnect dan sertifikat kompetisi
6. Tanggal Kompetisi: Hasil verifikasi antara tanggal kompetisi yang terdapat pada MyITS StudentConnect dan sertifikat kompetisi
7. Confidence Nama Mahasiswa: Confidence keakuratan dari penemuan data nama mahasiswa
7. Confidence Nama Kompetisi: Confidence keakuratan dari penemuan data nama kompetisi
8. Confidence Nama Penyelenggara: Confidence keakuratan dari penemuan data nama penyelenggara
9. Confidence Tanda Tangan: Confidence keakuratan dari penemuan data tanda tangan
10. Confidence Capaian: Confidence keakuratan dari penemuan data capaian
11. Confidence Tanggal Kompetisi: Confidence keakuratan dari penemuan data tanggal kompetisi
   
```json
    {
    "Capaian": true,
    "Confidence Capaian": 100,
    "Confidence Nama Kompetisi": 0,
    "Confidence Nama Mahasiswa": 100,
    "Confidence Nama Penyelenggara": 0,
    "Confidence Tanda Tangan": 0,
    "Confidence Tanggal Kompetisi": 30,
    "Nama Kompetisi": false,
    "Nama Mahasiswa": true,
    "Nama Penyelenggara": false,
    "Tanda Tangan": false,
    "Tanggal Kompetisi": false
    }
```
### *2. http://127.0.0.1:5000/surat_tugas*
API ini merupakan API untuk melakukan verifikasi terhadap dokumen surat tugas dari portofolio kompetisi pada MyITS StudentConnect. Adapun input yang dimasukkan adalah sebagai berikut
1. pdf_url: Dokumen surat tugas yang diikuti oleh mahasiswa untuk kompetisi
2. nama_mahasiswa: Nama mahasiswa yang terdaftar pada MyITS StudentConnect
3. nrp: NRP mahasiswa yang terdaftar pada MyITS StudentConnect
4. nama_departemen: Nama departemen yang terdaftar pada MyITS StudentConnect
5. skala: Skala kompetisi yang diikuti oleh mahasiswa


```json
{
    "pdf_url": "https://storage-api.its.ac.id/public/8531f465fc3b4491ba9dc36d845059f6/6ca99a49de6612bd1eed30a3b26af092/SuratTugasLombaDiesnatalisFTPUBke23ElvaRifkiFikana",
    "nama_mahasiswa": "ELVA RIFKI FIKANA",
    "nrp": "10511710000014",
    "nama_departemen": "Teknik Instrumentasi",
    "skala" :"nasional"
}
```
apabila request pada api/surat_tugas berhasil dijalankan, maka akan mengeluarkan output parameter verifikasi dengan value true yang berarti terverifikasi dan false yang berarti tidak terverifikasi. Berikut merupakan output dari api tersebut
1. Nama Mahasiswa: Hasil verifikasi antara nama mahasiswa yang terdapat pada MyITS StudentConnect dan surat tugas
2. Departemen: Hasil verifikasi antara nama departemen yang terdapat pada MyITS StudentConnect dan surat tugas
3. NRP: Hasil verifikasi antara nama nrp  yang terdapat pada MyITS StudentConnect dan surat tugas
4. Tanda Tangan: Hasil verifikasi dari pejabat yang menandatangani surat tugas
5. Keperluan: Hasil verifikasi keperluan surat tugas yang diajukan oleh mahasiswa
6. Confidence Nama Mahasiswa: Confidence keakuratan dari penemuan data nama mahasiswa
7. Confidence Departemen: Confidence keakuratan dari penemuan data nama departmen mahasiswa
8. Confidence NRP: Confidence keakuratan dari penemuan data NRP mahasiswa
9. Confidence Tanda TanganL Confidence keakuratan dari penemuan data tanda tangan
10. Confidence Keperluan Lomba: Confidence keakuratan dari penemuan data keperluan lomba

```json
{
    "Confidence Departemen": 100,
    "Confidence Keperluan Lomba": 100,
    "Confidence NRP": 100,
    "Confidence Nama Mahasiswa": 100,
    "Confidence Tanda Tangan": 0,
    "Departemen": true,
    "Keperluan Lomba": true,
    "NRP": true,
    "Nama Mahasiswa": true,
    "Tanda Tangan": false
}
```

# Deploy OCR MyITS StudentConnect mengggunakan Docker
1. Build image pada Docker menggunakan code berikut
```bash
docker build -t namaimage .
```
namaimage dapat diganti menggunakan nama image yang ingin digunakan oleh developer

2. Setelah image terbentuk, jalankan OCR tersebut dengan menjalankan image nya terlebih dahulu menggunakan code berikut
```bash
docker run -it namaimage sh -p 8080:5050
```
Command tersebut akan menjalankan image tersebut pada port 8080 atau 5050

3. Jalankan app.py sebagai main file setelah image docker berjalan
```bash
python app.py
```
4. app.py telah berhasil dijalankan menggunakan IP yang disediakan oleh Docker. Untuk melihat alamat IP dari sebuah container Docker yang menjalankan aplikasi Flask (app.py), Anda bisa mengikuti langkah-langkah berikut:

> Cari ID Container Docker:
Pertama, Anda perlu mengetahui ID dari container Docker yang menjalankan aplikasi Flask Anda. Buka terminal dan gunakan perintah berikut untuk melihat semua container yang berjalan:
```bash
docker ps
```
Perintah ini akan menampilkan daftar container yang aktif, termasuk ID container, nama gambar (image), dan detail lainnya.

> Dapatkan Alamat IP Container:
Setelah Anda mengetahui ID container, gunakan perintah berikut untuk mendapatkan detail jaringan dari container tersebut, termasuk alamat IP-nya. Ganti container_id dengan ID container yang Anda temukan dari langkah sebelumnya:
```bash
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container_id
```
> Perintah ini akan mengembalikan alamat IP dari container Docker tersebut. IP tersebut dapat dijalankan menggunakan port yang telah di-setting awal, yaitu 8080 atau/dan 5000
