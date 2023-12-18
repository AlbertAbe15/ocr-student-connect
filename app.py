from flask import Flask, request, jsonify
import requests
from PIL import Image, ImageFilter
from datetime import datetime
from babel.dates import format_date
import cv2
import numpy as np
from datetime import datetime
import re
import easyocr
import os
from PIL import Image
from fuzzywuzzy import fuzz
import pandas as pd
from pdf2image import convert_from_path
from pytesseract import image_to_string
from PIL import Image
import re
from fuzzywuzzy import fuzz
from pdf2image import convert_from_bytes
import fitz


app = Flask(__name__)

def convert_pdf_to_images(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None, "Tidak berhasil membuka file PDF dari URL yang diberikan"

    pdf_document = fitz.open(stream=response.content, filetype="pdf")
    images = []

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        pix = page.get_pixmap()
        img_data = pix.tobytes("png")  # Konversi ke byte array
        img_np = np.frombuffer(img_data, np.uint8)  # Buat NumPy array dari byte array
        img_cv2 = cv2.imdecode(img_np, cv2.IMREAD_COLOR)  # Decode ke format gambar OpenCV


        if img_cv2 is None or img_cv2.size == 0:
            continue

        images.append(img_cv2)

    pdf_document.close()
    return images, None

def download_pdf_from_drive(url):
    response = requests.get(url)
    print("Status Code:", response.status_code)  # Tambahkan ini untuk debugging
    if response.status_code == 200:
        content_type = response.headers.get('content-type')
        print("Content-Type:", content_type)  # Tambahkan ini untuk debugging
        if 'pdf' in content_type.lower():
            return response.content
        else:
            print("URL tidak mengarah ke file PDF. Content-Type:", content_type)
    return None

def convert_pdf_to_img(pdf_content):
    images = convert_from_bytes(pdf_content)
    return images

def convert_image_to_text(images):
    text = ''
    for img in images:
        text += image_to_string(img)
    return text.lower()


def convert_to_lowercase(data):
    if isinstance(data, str):
        return data.lower()
    else:
        return data
    
def matching_data_surat(hasil, nama_mahasiswa, nrp, nama_departemen, skala):
    results = {'Nama Mahasiswa': [], 'NRP': [], 'Nama Departemen': [], 'Tanda Tangan': [], 'Keperluan Lomba': []}
    mahasiswa_results = []
    nrp_results = []
    departemen_results = []
    tanda_tangan_results = []
    keperluan_lomba_results = []
    
    # Mencari hasil nama
    pattern_nama_mahasiswa = re.compile(rf'\b{re.escape(nama_mahasiswa)}\b')
    if pattern_nama_mahasiswa.search(hasil):
        mahasiswa_results.append(True)
    else:
        mahasiswa_results.append(fuzz.ratio(nama_mahasiswa, hasil) > 70)

    # Mencari hasil nrp
    pattern_nrp = re.compile(rf'\b{re.escape(nrp)}\b')
    if pattern_nrp.search(hasil):
        nrp_results.append(True)
    else:
        nrp_results.append(fuzz.ratio(nrp, hasil) > 70)

    # Mencari departemen
    pattern_departemen = re.compile(rf'\b{re.escape(nama_departemen)}\b')
    if pattern_departemen.search(hasil):
        departemen_results.append(True)
    else:
        departemen_results.append(fuzz.ratio(nama_departemen, hasil) > 70)   

    # Mencari Tanda Tangan
    pejabat = "9999999"
    if skala == 'nasional':
        pejabat = r'Direktur Pendidikan\w*'
    elif skala == 'internasional':
        pejabat = r'Wakil Rektor\w*'
        
    regex_tanda_tangan = re.compile(pejabat, re.IGNORECASE)
    if regex_tanda_tangan.search(hasil):
        tanda_tangan_results.append(True)
    else:
        tanda_tangan_results.append(False)

    # Keperluan lomba
    kata_kunci = r'lomba\w*|peserta lomba\w*|kompetisi\w*'
    pattern_keperluan = re.compile(kata_kunci, re.IGNORECASE)
    if pattern_keperluan.search(hasil):
        keperluan_lomba_results.append(True)
    else:
        keperluan_lomba_results.append(fuzz.ratio('keperluan lomba', hasil) > 70) 

    return any(mahasiswa_results), any(nrp_results), any(departemen_results), any(tanda_tangan_results), any(keperluan_lomba_results)
    
def convert_date_format(date_obj):
    new_date_format = format_date(date_obj, format='d MMMM yyyy', locale='id_ID')
    return new_date_format
    
def extract_text_from_image(image_path):
    reader = easyocr.Reader(['en'], gpu=False)
    bounds = reader.readtext(image_path)
    extracted_text = [detection[1].lower() for detection in bounds]
    return extracted_text

def rotate_image(img_path):
    img = Image.open(img_path)
    width, height = img.size

    # Periksa apakah gambar berorientasi potret
    if height > width:
        # Jika iya, putar gambar menjadi landscape (90 derajat searah jarum jam)
        img = img.rotate(-90, expand=True)
        img.save('landscape_image.jpg')  # Simpan gambar yang sudah diputar
        return 'landscape_image.jpg'  # Kembalikan nama file gambar yang sudah diputar
    else:
        return img_path  # Jika sudah landscape, kembalikan nama file asli
    
def preprocess_image(image):
    if image:
        # Contoh preprocessing: Merubah ke skala abu-abu dan menerapkan filter kontur
        grayscale_img = image.convert('L')  # Merubah ke skala abu-abu
        contoured_img = grayscale_img.filter(ImageFilter.CONTOUR)  # Menerapkan filter kontur
        return contoured_img
    else:
        return None


def preprocess_for_ocr(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Dilation and erosion to close gaps in between object edges
    kernel = np.ones((1, 1), np.uint8)
    img_dilation = cv2.dilate(thresh, kernel, iterations=1)
    img_erosion = cv2.erode(img_dilation, kernel, iterations=1)

    # Additional noise removal
    noise_removal = cv2.medianBlur(img_erosion, 3)

    return noise_removal

def format_date_range(start_date, end_date):
    
    # Parse the dates
    start_date_parts = start_date.split()
    end_date_parts = end_date.split()
    
    # Check if the start and end dates are in the same month and year
    if start_date_parts[1:] == end_date_parts[1:]:
        # Same month and year
        return (f"{start_date_parts[0]}-{end_date_parts[0]} {end_date_parts[1]} {end_date_parts[2]}").lower()
    else:
        # Different month or year
        return (f"{start_date_parts[0]} {start_date_parts[1]}-{end_date_parts[0]} {end_date_parts[1]} {end_date_parts[2]}").lower()
    
def convert_indonesian_date_to_english(indonesian_date):
    # Kamus nama bulan dalam bahasa Indonesia ke bahasa Inggris
    month_translation = {
        'januari': 'January', 'februari': 'February', 'maret': 'March', 'april': 'April',
        'mei': 'May', 'juni': 'June', 'juli': 'July', 'agustus': 'August',
        'september': 'September', 'oktober': 'October', 'november': 'November', 'desember': 'December'
    }

    # Split tanggal, bulan, dan tahun
    splitted_date = indonesian_date.lower().split()
    day = int(splitted_date[0])
    month = month_translation[splitted_date[1]]
    year = int(splitted_date[2])

    # Format tanggal dalam bahasa Inggris
    english_date = datetime(year, list(month_translation.values()).index(month) + 1, day).strftime("%B %d, %Y")
    return english_date.lower()

# Fungsi untuk mencocokkan data dari hasil OCR dengan dataframe pertama
def match_data_with_ocr(nama_mahasiswa, nama_kompetisi, nama_penyelenggara, tanggal_mulai, tanggal_selesai, file_name, hasil_capaian, flag):
    results = {'Nama Mahasiswa': [], 'Nama Kompetisi': [], 'Penyelenggara': [], 'Tanggal Selesai': [], 'Capaian': [], 'Tanda Tangan': []}
    
    if flag == 0:
        preprocessed_image = preprocess_for_ocr(file_name)
        extracted_text = extract_text_from_image(preprocessed_image)
        result_string = ' '.join(extracted_text)
    else:
        print("Berhasil Masuk ke If Else")
        extracted_text = extract_text_from_image(file_name)
        print("Berhasil Masuk ke extracted_text")
        result_string = ' '.join(extracted_text)
    # extracted_text = extract_text_from_image(preprocessed_image)
    # result_string = ' '.join(extracted_text)
    print(result_string)
    mahasiswa_results = []
    kompetisi_results = []
    penyelenggara_results = []
    tanggal_selesai_results = []
    capaian_results = []
    tanda_tangan_results = []

    # Mencari Nama Mahasiswa
    pattern_nama_mahasiswa = re.compile(rf'\b{re.escape(nama_mahasiswa)}\b')
    if pattern_nama_mahasiswa.search(result_string):
        mahasiswa_results.append(True)
    elif any(fuzz.ratio(nama_mahasiswa, text) > 70 for text in extracted_text):
        mahasiswa_results.append(any(fuzz.ratio(nama_mahasiswa, text) > 70 for text in extracted_text))
    else:
        name_asli = sorted(nama_mahasiswa)
        mahasiswa_results.append(any((name_asli == text)for text in extracted_text))
                
    # Mencari Nama Kompetisi            
    pattern_nama_kompetisi = re.compile(rf'\b{re.escape(nama_kompetisi)}\b')
    if pattern_nama_kompetisi.search(result_string):
        kompetisi_results.append(True)
    elif any(fuzz.ratio(nama_kompetisi, text) > 70 for text in extracted_text):
        kompetisi_results.append(any(fuzz.ratio(nama_kompetisi, text) > 70 for text in extracted_text))
    else:
        kompetisi_asli = sorted(nama_kompetisi)
        kompetisi_results.append(any((kompetisi_asli == text)for text in extracted_text))
    
    # Mencari Nama Penyelenggara 
    pattern_nama_penyelenggara = re.compile(rf'\b{re.escape(nama_penyelenggara)}\b')
    if pattern_nama_penyelenggara.search(result_string):
        penyelenggara_results.append(True)
    elif any(fuzz.ratio(nama_penyelenggara, text) > 70 for text in extracted_text):
        penyelenggara_results.append(any(fuzz.ratio(nama_penyelenggara, text) > 70 for text in extracted_text))
    else:
        penyelenggara_asli = sorted(nama_penyelenggara)
        penyelenggara_results.append(any((penyelenggara_asli == text)for text in extracted_text))

    # Mencari Tanggal Selesai
    pattern_tanggal_selesai = re.compile(rf'\b{re.escape(tanggal_selesai)}\b')
    if pattern_tanggal_selesai.search(result_string):
        tanggal_selesai_results.append(True)
    else:
        if any(fuzz.ratio(tanggal_selesai, text) > 70 for text in extracted_text):
            tanggal_selesai_results.append(any(fuzz.ratio(tanggal_selesai, text) > 70 for text in extracted_text))
        elif any(fuzz.ratio(convert_indonesian_date_to_english(tanggal_selesai), text) > 70 for text in extracted_text):
            tanggal_selesai = convert_indonesian_date_to_english(tanggal_selesai)
            tanggal_selesai_results.append(any(fuzz.ratio(tanggal_selesai, text) > 70 for text in extracted_text))
        else:
            pattern_tanggal_mulai_selesai = re.compile(rf'\b{re.escape(format_date_range(tanggal_mulai, tanggal_selesai))}\b')
            if pattern_tanggal_mulai_selesai.search(result_string):
                tanggal_selesai_results.append(True)
            else:
                tanggal_selesai_results.append(any(fuzz.ratio(format_date_range(tanggal_mulai, tanggal_selesai), text) > 70 for text in extracted_text))

    # Mencari Hasil Capaian
    if hasil_capaian == 'juara 1/emas':
        pattern_hasil_capaian = re.compile(r'juara\s+1|1st\s+winner|first\s+winner|juara\s+I|best\s+delegate|first|emas|gold|juara\s+i|best\s+|finalis', re.IGNORECASE)
    elif hasil_capaian == 'juara 2/perak':
        pattern_hasil_capaian = re.compile(r'juara\s+2|2nd\s+winner|second\s+winner|juara\s+II|runner\s+up|second|perak|silver|juara\s+ii|finalis', re.IGNORECASE)
    elif hasil_capaian == 'juara 3/perunggu':
        pattern_hasil_capaian = re.compile(r'juara\s+3|3rd\s+winner|third\s+winner|juara\s+III|perunggu|bronze|juara\s+iii|finalis', re.IGNORECASE)
    else:
        pattern_hasil_capaian = None

    if pattern_hasil_capaian.search(result_string):
        capaian_results.append(True)
    elif any(fuzz.ratio(hasil_capaian, text) > 70 or pattern_hasil_capaian.search(text) for text in extracted_text):
        capaian_results.append(any(fuzz.ratio(hasil_capaian, text) > 70 or pattern_hasil_capaian.search(text) for text in extracted_text)) 
    else:
        capaian_asli = sorted(hasil_capaian)
        capaian_results.append(any((capaian_asli == text)for text in extracted_text))

    # Mencari Tanda Tangan
    tanda_tangan_patterns = r'Dekan\w*|Wakil Rektor\w*|Kepala Prodi\w*|Kepala Departemen\w*|Rektor\w*|Secretary General\w*|Head Depart\w*|CEO\w*|Dean\w*|Director\w*|President\w*|Chairman\w*|Ketua Umum\w*|Direktur\w*|Kepala Pusat\w*|Kepala Dinas\w*|Chief Technical Officer\w*|Direktur Jenderal\w*|Pembina\w*|Kepala Pusat\w*|Head of\w*|Secretary-General|Ketua Program Studi\s*|Ketua Jurusan\s*'
    regex_tanda_tangan = re.compile(tanda_tangan_patterns, re.IGNORECASE)
    if regex_tanda_tangan.search(result_string):
        tanda_tangan_results.append(True)
    else:
        tanda_tangan_results.append(False)

    if (not any(mahasiswa_results)) & (not any(kompetisi_results)) & (not any(penyelenggara_results)) & (not (any(tanggal_selesai_results))) & (not any(capaian_results)) & (not any(tanda_tangan_results)):
        # gambar_rotasi = rotate_image(preprocessed_image)
        # extracted_text = extract_text_from_image(gambar_rotasi)
        # result_string = ' '.join(extracted_text)
                
    # Mencari Nama Mahasiswa
        pattern_nama_mahasiswa = re.compile(rf'\b{re.escape(nama_mahasiswa)}\b')
        if pattern_nama_mahasiswa.search(result_string):
            mahasiswa_results.pop()
            mahasiswa_results.append(True)
        elif any(fuzz.ratio(nama_mahasiswa, text) > 70 for text in extracted_text):
            mahasiswa_results.pop()
            mahasiswa_results.append(any(fuzz.ratio(nama_mahasiswa, text) > 70 for text in extracted_text))
        else:
            mahasiswa_results.pop()
            name_asli = sorted(nama_mahasiswa)
            mahasiswa_results.append(any((name_asli == text)for text in extracted_text))
                        
    # Mencari Nama Kompetisi
        pattern_nama_kompetisi = re.compile(rf'\b{re.escape(nama_kompetisi)}\b')
        if pattern_nama_kompetisi.search(result_string):
            kompetisi_results.pop()
            kompetisi_results.append(True)
        elif any(fuzz.ratio(nama_kompetisi, text) > 70 for text in extracted_text):
            kompetisi_results.pop()
            kompetisi_results.append(any(fuzz.ratio(nama_kompetisi, text) > 70 for text in extracted_text))
        else:
            kompetisi_results.pop()
            kompetisi_asli = sorted(nama_kompetisi)
            kompetisi_results.append(any((kompetisi_asli == text)for text in extracted_text)) 

    # Mencari Nama Penyelenggara            
        pattern_nama_penyelenggara = re.compile(rf'\b{re.escape(nama_penyelenggara)}\b')
        if pattern_nama_penyelenggara.search(result_string):
            penyelenggara_results.pop()
            penyelenggara_results.append(True)
        elif any(fuzz.ratio(nama_penyelenggara, text) > 70 for text in extracted_text):
            penyelenggara_results.pop()
            penyelenggara_results.append(any(fuzz.ratio(nama_penyelenggara, text) > 70 for text in extracted_text))
        else:
            penyelenggara_results.pop()
            penyelenggara_asli = sorted(nama_penyelenggara)
            penyelenggara_results.append(any((penyelenggara_asli == text)for text in extracted_text)) 
                
    # Mencari Tanggal Selesai
        pattern_tanggal_selesai = re.compile(rf'\b{re.escape(tanggal_selesai)}\b')
        pattern_tanggal_selesai_inggris= re.compile(rf'\b{re.escape(convert_indonesian_date_to_english(tanggal_selesai))}\b')
        if pattern_tanggal_selesai.search(result_string):
            tanggal_selesai_results.pop()
            tanggal_selesai_results.append(True)
        else:
            if any(fuzz.ratio(tanggal_selesai, text) > 70 for text in extracted_text):
                tanggal_selesai_results.pop()
                tanggal_selesai_results.append(any(fuzz.ratio(tanggal_selesai, text) > 70 for text in extracted_text))
            elif any(fuzz.ratio(convert_indonesian_date_to_english(tanggal_selesai), text) > 70 for text in extracted_text):
                tanggal_selesai_results.pop()
                tanggal = convert_indonesian_date_to_english(tanggal_selesai)
                tanggal_selesai_results.append(any(fuzz.ratio(tanggal, text) > 70 for text in extracted_text))
            elif pattern_tanggal_selesai_inggris.search(result_string):
                tanggal_selesai_results.pop()
                tanggal_selesai_results.append(True)
            else:
                pattern_tanggal_mulai_selesai = re.compile(rf'\b{re.escape(format_date_range(tanggal_mulai, tanggal_selesai))}\b')
                if pattern_tanggal_mulai_selesai.search(result_string):
                    tanggal_selesai_results.pop()
                    tanggal_selesai_results.append(True)
                else:
                    tanggal_selesai_results.pop()
                    tanggal_selesai_results.append(any(fuzz.ratio(format_date_range(tanggal_mulai, tanggal_selesai), text) > 70 for text in extracted_text))

    # Mencari Hasil Capaian
    if hasil_capaian == 'juara 1/emas':
        pattern_hasil_capaian = re.compile(r'juara\s+1|1st\s+winner|first\s+winner|juara\s+I|best\s+delegate|first|emas|gold|juara\s+i|best\s+|finalis', re.IGNORECASE)
    elif hasil_capaian == 'juara 2/perak':
        pattern_hasil_capaian = re.compile(r'juara\s+2|2nd\s+winner|second\s+winner|juara\s+II|runner\s+up|second|perak|silver|juara\s+ii|finalis', re.IGNORECASE)
    elif hasil_capaian == 'juara 3/perunggu':
        pattern_hasil_capaian = re.compile(r'juara\s+3|3rd\s+winner|third\s+winner|juara\s+III|perunggu|bronze|juara\s+iii|finalis', re.IGNORECASE)
    else:
        pattern_hasil_capaian = None
    
    if pattern_hasil_capaian.search(result_string):
        capaian_results.pop()
        capaian_results.append(True)
    elif any(fuzz.ratio(hasil_capaian, text) > 70 or pattern_hasil_capaian.search(text) for text in extracted_text):
        capaian_results.pop()
        capaian_results.append(any(fuzz.ratio(hasil_capaian, text) > 70 or pattern_hasil_capaian.search(text) for text in extracted_text))  
    else:
        capaian_asli = sorted(hasil_capaian)
        capaian_results.append(any((capaian_asli == text)for text in extracted_text))

    # Mencari Tanda Tangan
        tanda_tangan_patterns = r'Dekan\w*|Wakil Rektor\w*|Kepala Prodi\w*|Kepala Departemen\w*|Rektor\w*|Secretary General\w*|Head Depart\w*|CEO\w*|Dean\w*|Director\w*|President\w*|Chairman\w*|Ketua Umum\w*|Direktur\w*|Kepala Pusat\w*|Kepala Dinas\w*|Chief Technical Officer\w*|Direktur Jenderal\w*|Pembina\w*|Kepala Pusat\w*|Head of\w*|Secretary-General|Ketua Program Studi\s*|Ketua Jurusan\s*'
        regex_tanda_tangan = re.compile(tanda_tangan_patterns, re.IGNORECASE)
        tanda_tangan_results.pop()
        if regex_tanda_tangan.search(result_string):
            tanda_tangan_results.append(True)
        else:
            tanda_tangan_results.append(False)


        results['Nama Mahasiswa'].append(any(mahasiswa_results))
        results['Nama Kompetisi'].append(any(kompetisi_results))
        results['Penyelenggara'].append(any(penyelenggara_results))
        results['Tanggal Selesai'].append(any(tanggal_selesai_results))
        results['Capaian'].append(any(capaian_results))
        results['Tanda Tangan'].append(any(tanda_tangan_results))
            
    
    return any(mahasiswa_results), any(kompetisi_results), any(penyelenggara_results), any(tanggal_selesai_results), any(capaian_results), any(tanda_tangan_results)

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
                hasil_nama_mahasiswa, hasil_nama_kompetisi, hasil_nama_penyelenggara, hasil_tanggal, hasil_capaian, hasil_tanda_tangan = match_data_with_ocr(nama_mahasiswa, nama_kompetisi, nama_penyelenggara, tanggal_mulai, tanggal_selesai, img_cv2, capaian, 1)
                if hasil_nama_mahasiswa is not None:
                    results.append({"Nama Mahasiswa": hasil_nama_mahasiswa,
                                    "Nama Kompetisi": hasil_nama_kompetisi,
                                    "Nama Penyelenggara": hasil_nama_penyelenggara,
                                    "Tanggal Kompetisi": hasil_tanggal,
                                    "Capaian": hasil_capaian,
                                    "Tanda Tangan": hasil_tanda_tangan})
        
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
                hasil_nama_mahasiswa, hasil_nama_kompetisi, hasil_nama_penyelenggara, hasil_tanggal, hasil_capaian, hasil_tanda_tangan= match_data_with_ocr(nama_mahasiswa, nama_kompetisi, nama_penyelenggara, tanggal_mulai, tanggal_selesai, img_cv2, capaian, 0)
                if  hasil_nama_mahasiswa is not None:
                    return jsonify({
                                    "Nama Mahasiswa": hasil_nama_mahasiswa,
                                    "Nama Kompetisi": hasil_nama_kompetisi,
                                    "Nama Penyelenggara": hasil_nama_penyelenggara,
                                    "Tanggal Kompetisi": hasil_tanggal,
                                    "Capaian": hasil_capaian,
                                    "Tanda Tangan": hasil_tanda_tangan
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

    matching_data_surat(text, 'elen nova widyarindra', '10611710000016', 'statistika bisnis', 'nasional')
    hasil_nama_mahasiswa, hasil_nrp, hasil_departemen, hasil_tanda_tangan, hasil_keperluan = matching_data_surat(text, nama_mahasiswa, nrp, nama_departemen, 'skala')

    return jsonify({"Nama Mahasiswa": hasil_nama_mahasiswa,
                    "NRP": hasil_nrp,
                    "Departemen": hasil_departemen,
                    "Tanda Tangan": hasil_tanda_tangan,
                    "Keperluan Lomba": hasil_keperluan})

if __name__ == '__main__':
    app.run(debug=True)
