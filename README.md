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

# Deploy OCR MyITS StudentConnect pada Ubuntu
1. Install python menggunakan command berikut
```bash
sudo apt-get install python
```   
2. Melakukan installasi library yang digunakan pada program python dengan bantuan library beserta versinya dalam requirements.txt
```bash
pip install --trusted-host=pypi.org --trusted-host=files.pythonhosted.org --user -r requirements.txt 
```
3. Melakukan installasi tambahan OCR untuk mendukung program python
```bash
apt-get install -y poppler-utils
apt-get install -y tesseract-ocr
```
4. Jalankan app.py sebagai main file setelah image docker berjalan
```bash
python app.py
```
5. Program telah dapat dijalankan. Berikut merupakan bantuan informasi postman yang digunakan untuk melakukan request
```json 
{
	"info": {
		"_postman_id": "a1cff0fb-1a33-49aa-a51c-2095665c1227",
		"name": "New Collection",
		"schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
		"_exporter_id": "17092104"
	},
	"item": [
		{
			"name": "http://127.0.0.1:5000/surat_tugas",
			"request": {
				"method": "POST",
				"header": [],
				"body": {
					"mode": "raw",
					"raw": "{\n    \"pdf_url\": \"https://storage-api.its.ac.id/public/8531f465fc3b4491ba9dc36d845059f6/6ca99a49de6612bd1eed30a3b26af092/SuratTugasLombaDiesnatalisFTPUBke23ElvaRifkiFikana\",\n    \"nama_mahasiswa\": \"ELVA RIFKI FIKANA\",\n    \"nrp\": \"10511710000014\",\n    \"nama_departemen\": \"Teknik Instrumentasi\",\n    \"skala\" :\"nasional\"\n}\n",
					"options": {
						"raw": {
							"language": "json"
						}
					}
				},
				"url": {
					"raw": "http://ocr.its.ac.id:5000/surat_tugas",
					"protocol": "http",
					"host": [
						"ocr",
						"its",
						"ac",
						"id"
					],
					"port": "5000",
					"path": [
						"surat_tugas"
					]
				}
			},
			"response": [
				{
					"name": "http://127.0.0.1:5000/surat_tugas",
					"originalRequest": {
						"method": "POST",
						"header": [],
						"body": {
							"mode": "raw",
							"raw": "{\n    \"pdf_url\": \"https://storage-api.its.ac.id/public/8531f465fc3b4491ba9dc36d845059f6/6ca99a49de6612bd1eed30a3b26af092/SuratTugasLombaDiesnatalisFTPUBke23ElvaRifkiFikana\",\n    \"nama_mahasiswa\": \"ELVA RIFKI FIKANA\",\n    \"nrp\": \"10511710000014\",\n    \"nama_departemen\": \"Teknik Instrumentasi\",\n    \"skala\": \"nasional\"\n}",
							"options": {
								"raw": {
									"language": "json"
								}
							}
						},
						"url": {
							"raw": "http://10.15.42.225:5000/surat_tugas",
							"protocol": "http",
							"host": [
								"10",
								"15",
								"42",
								"225"
							],
							"port": "5000",
							"path": [
								"surat_tugas"
							]
						}
					},
					"status": "OK",
					"code": 200,
					"_postman_previewlanguage": "json",
					"header": [
						{
							"key": "Content-Length",
							"value": "239"
						},
						{
							"key": "Content-Type",
							"value": "application/json"
						},
						{
							"key": "Date",
							"value": "Tue, 30 Jan 2024 19:45:59 GMT"
						},
						{
							"key": "Server",
							"value": "waitress"
						}
					],
					"cookie": [],
					"body": "{\n    \"Confidence Departemen\": 100,\n    \"Confidence Keperluan Lomba\": 100,\n    \"Confidence NRP\": 100,\n    \"Confidence Nama Mahasiswa\": 100,\n    \"Confidence Tanda Tangan\": 0,\n    \"Departemen\": true,\n    \"Keperluan Lomba\": true,\n    \"NRP\": true,\n    \"Nama Mahasiswa\": true,\n    \"Tanda Tangan\": false\n}"
				}
			]
		},
		{
			"name": "http://127.0.0.1:5000/sertifikat_kompetisi",
			"request": {
				"method": "POST",
				"header": [],
				"body": {
					"mode": "raw",
					"raw": "{\n    \"image_url\": \"https://storage-api.its.ac.id/public/8531f465fc3b4491ba9dc36d845059f6/e807516deb514ea5adbb3b19bc23d3d0/ACHMADMAULANAHAWESTdikompresi\",\n    \"nama_mahasiswa\": \"ACHMAD MAULANA ALI ULUMUDIN\",\n    \"nama_penyelenggara\": \"FKM UINSU - Health Research Student Association\",\n    \"nama_kompetisi\": \"HAWEST (Hersa Writing Contest)\",\n    \"hasil_capaian\": \"Juara 2/perak\",\n    \"tanggal_mulai\": \"12/08/2021\",\n    \"tanggal_selesai\": \"17/09/2021\"\n}\n",
					"options": {
						"raw": {
							"language": "json"
						}
					}
				},
				"url": {
					"raw": "http://127.0.0.1:5000/sertifikat_kompetisi",
					"protocol": "http",
					"host": [
						"127",
						"0",
						"0",
						"1"
					],
					"port": "5000",
					"path": [
						"sertifikat_kompetisi"
					]
				}
			},
			"response": []
		}
	]
}
``` 
