from flask import Flask, request, jsonify
import requests
from babel.dates import format_date
import numpy as np
from datetime import datetime
from sertifikat import preprocess_for_ocr, convert_pdf_to_images, match_data_with_ocr
from surat_tugas import download_pdf_from_drive, convert_pdf_to_img, convert_image_to_text, matching_data_surat
import cv2


app = Flask(__name__)

def convert_to_lowercase(data):
    if isinstance(data, str):
        return data.lower()
    else:
        return data

def convert_date_format(date_obj):
    new_date_format = format_date(date_obj, format='d MMMM yyyy', locale='id_ID')
    return new_date_format
    

def get_content_type(url):
    response = requests.head(url)
    if response.status_code != 200:
        # Jika permintaan HEAD gagal, coba dengan permintaan GET
        response = requests.get(url, stream=True)

    if response.status_code == 200:
        return response.headers.get('Content-Type')
    else:
        return None


@app.route('/sertifikat_kompetisi', methods=['POST'])
def sertifikat_kompetisi():
    try:
        # Menerima URL gambar dari Postman
        image_url = request.json.get('image_url')
        content_type = get_content_type(image_url)
        nama_mahasiswa = convert_to_lowercase(request.json['nama_mahasiswa'])
        nama_kompetisi = convert_to_lowercase(request.json['nama_kompetisi'])
        nama_penyelenggara = convert_to_lowercase(request.json['nama_penyelenggara'])
        capaian = convert_to_lowercase(request.json['hasil_capaian'])
        
        # Mengonversi string tanggal menjadi objek datetime
        tanggal_mulai = datetime.strptime(request.json['tanggal_mulai'], '%d/%m/%Y')
        tanggal_selesai = datetime.strptime(request.json['tanggal_selesai'], '%d/%m/%Y')

        # Mengubah format tanggal
        tanggal_mulai = convert_date_format(tanggal_mulai)
        tanggal_selesai = convert_date_format(tanggal_selesai)

        # Memeriksa apakah URL diterima
        if not image_url:
            return jsonify({"message": "Tidak ada URL gambar yang diterima"})
        
        if content_type is None:
            return jsonify({"message": "Tidak dapat menentukan jenis konten dari URL"})

        # Mengunduh gambar dari URL
        if 'application/pdf' in content_type:
            images, error_message = convert_pdf_to_images(image_url)
            if error_message:
                return jsonify({"message pdf error": error_message})

            results = []
            print(images)
            for img_cv2 in images:
                img_cv2 = preprocess_for_ocr(img_cv2)
                print(img_cv2)
                print("Berhasil masuk")
                # Proses setiap gambar
                hasil_nama_mahasiswa, hasil_nama_kompetisi, hasil_nama_penyelenggara, hasil_tanggal, hasil_capaian, hasil_tanda_tangan, confidence_nama_mahasiswa, confidence_nama_kompetisi, confidence_nama_penyelenggara, confidence_tanggal_kompetisi, confidence_capaian, confidence_tanda_tangan = match_data_with_ocr(nama_mahasiswa, nama_kompetisi, nama_penyelenggara, tanggal_mulai, tanggal_selesai, img_cv2, capaian, 1)
                if hasil_nama_mahasiswa is not None:
                    results.append({"Nama Mahasiswa": hasil_nama_mahasiswa,
                                    "Confidence Nama Mahasiswa": confidence_nama_mahasiswa,
                                    "Nama Kompetisi": hasil_nama_kompetisi,
                                    "Confidence Nama Kompetisi": confidence_nama_kompetisi,
                                    "Nama Penyelenggara": hasil_nama_penyelenggara,
                                    "Confidence Nama Penyelenggara": confidence_nama_penyelenggara,
                                    "Tanggal Kompetisi": hasil_tanggal,
                                    "Confidence Tanggal Kompetisi": confidence_tanggal_kompetisi,
                                    "Capaian": hasil_capaian,
                                    "Confidence Capaian": confidence_capaian,
                                    "Tanda Tangan": hasil_tanda_tangan,
                                    "Confidence Tanda Tangan": confidence_tanda_tangan})
        
                else:
                    results.append({"message": "Tidak berhasil melakukan preprocessing pada salah satu halaman"})
            combined_results = {key: False for key in results[0].keys()}
            # Gabungkan setiap JSON dalam list.
            for result in results:
                for key, value in result.items():
                    combined_results[key] = combined_results[key] or value
            
            return jsonify(combined_results)
                    
        else:
            response = requests.get(image_url)
            if response.status_code == 200:

                file_bytes = np.frombuffer(response.content, np.uint8)
                img_cv2 = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR) 

                # Melakukan preprocessing pada gambar
                hasil_nama_mahasiswa, hasil_nama_kompetisi, hasil_nama_penyelenggara, hasil_tanggal, hasil_capaian, hasil_tanda_tangan, confidence_nama_mahasiswa, confidence_nama_kompetisi, confidence_nama_penyelenggara, confidence_tanggal_kompetisi, confidence_capaian, confidence_tanda_tangan= match_data_with_ocr(nama_mahasiswa, nama_kompetisi, nama_penyelenggara, tanggal_mulai, tanggal_selesai, img_cv2, capaian, 0)
                if  hasil_nama_mahasiswa is not None:
                    return jsonify({
                                    "Nama Mahasiswa": hasil_nama_mahasiswa,
                                    "Confidence Nama Mahasiswa": confidence_nama_mahasiswa,
                                    "Nama Kompetisi": hasil_nama_kompetisi,
                                    "Confidence Nama Kompetisi": confidence_nama_kompetisi,
                                    "Nama Penyelenggara": hasil_nama_penyelenggara,
                                    "Confidence Nama Penyelenggara": confidence_nama_penyelenggara,
                                    "Tanggal Kompetisi": hasil_tanggal,
                                    "Confidence Tanggal Kompetisi": confidence_tanggal_kompetisi,
                                    "Capaian": hasil_capaian,
                                    "Confidence Capaian": confidence_capaian,
                                    "Tanda Tangan": hasil_tanda_tangan,
                                    "Confidence Tanda Tangan": confidence_tanda_tangan
                                    })
                else:
                    return jsonify({"message": "Tidak berhasil melakukan preprocessing"})
            else:
                return jsonify({"message": "Tidak berhasil membuka gambar dari URL yang diberikan"})
    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan: {str(e)}"}), 500

@app.route('/surat_tugas', methods=['POST'])
def ocr():
    content = request.json
    # Format https://drive.google.com/uc?export=download&id=YOUR_FILE_ID
    url = content.get('pdf_url')
    nama_mahasiswa = convert_to_lowercase(request.json['nama_mahasiswa'])
    nama_departemen = convert_to_lowercase(request.json['nama_departemen'])
    nrp = convert_to_lowercase(request.json['nrp'])
    skala = convert_to_lowercase(request.json['skala'])
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    pdf_content = download_pdf_from_drive(url)
    if not pdf_content:
        return jsonify({"error": "Failed to download PDF"}), 500

    images = convert_pdf_to_img(pdf_content)
    text = convert_image_to_text(images)

    hasil_nama_mahasiswa, hasil_nrp, hasil_departemen, hasil_tanda_tangan, hasil_keperluan, confidence_nama_mahasiswa, confidence_nrp, confidence_departemen, confidence_tanda_tangan, confidence_keperluan = matching_data_surat(text, nama_mahasiswa, nrp, nama_departemen, skala)

    return jsonify({"Nama Mahasiswa": hasil_nama_mahasiswa,
                    "Confidence Nama Mahasiswa": confidence_nama_mahasiswa,
                    "NRP": hasil_nrp,
                    "Confidence NRP": confidence_nrp,
                    "Departemen": hasil_departemen,
                    "Confidence Departemen": confidence_departemen,
                    "Tanda Tangan": hasil_tanda_tangan,
                    "Confidence Tanda Tangan": confidence_tanda_tangan,
                    "Keperluan Lomba": hasil_keperluan,
                    "Confidence Keperluan Lomba": confidence_keperluan})

if __name__ == '__main__':
    from waitress import serve
    # serve(app, host="0.0.0.0", port=5000)
    app.run(debug=True)
