# ocr-student-connect
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
   
```json
    {
        "Capaian": true,
        "Nama Kompetisi": true,
        "Nama Mahasiswa": true,
        "Nama Penyelenggara": false,
        "Tanda Tangan": true,
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
    "pdf_url": "https://drive.google.com/uc?export=download&id=1aYQXKb8J_jDCDLwrhMba_0dnrULZtzuD",
    "nama_mahasiswa": "elen nova widyarindra",
    "nrp": "10611710000016",
    "nama_departemen": "statistika bisnis",
    "skala" :"nasional"
}
```
apabila request pada api/surat_tugas berhasil dijalankan, maka akan mengeluarkan output parameter verifikasi dengan value true yang berarti terverifikasi dan false yang berarti tidak terverifikasi. Berikut merupakan output dari api tersebut
1. Nama Mahasiswa: Hasil verifikasi antara nama mahasiswa yang terdapat pada MyITS StudentConnect dan surat tugas
2. Departemen: Hasil verifikasi antara nama departemen yang terdapat pada MyITS StudentConnect dan surat tugas
3. NRP: Hasil verifikasi antara nama nrp  yang terdapat pada MyITS StudentConnect dan surat tugas
4. Tanda Tangan: Hasil verifikasi dari pejabat yang menandatangani surat tugas
5. Keperluan: Hasil verifikasi keperluan surat tugas yang diajukan oleh mahasiswa

```json
{
    "Departemen": true,
    "Keperluan Lomba": false,
    "NRP": true,
    "Nama Mahasiswa": true,
    "Tanda Tangan": false
}
```

   
