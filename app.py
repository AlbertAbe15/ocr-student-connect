from flask import Flask, request, jsonify
import requests
from PIL import Image, ImageFilter
from datetime import datetime
from babel.dates import format_date
import numpy as np
from PIL import Image
import re
from fuzzywuzzy import fuzz
from pdf2image import convert_from_bytes
import fitz
from pytesseract import image_to_string
import easyocr
from PIL import Image
import cv2



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
    mahasiswa_results = ''
    nrp_results = ''
    departemen_results = ''
    tanda_tangan_results = ''
    keperluan_lomba_results = ''
    
    # Mencari hasil nama
    pattern_nama_mahasiswa = re.compile(r'\b{}\b'.format(re.escape(nama_mahasiswa)))
    mahasiswa_results = bool(pattern_nama_mahasiswa.search(hasil))

    # Mencari hasil nrp
    pattern_nrp = re.compile(r'\b{}\b'.format(re.escape(str(nrp))))
    nrp_results = bool(pattern_nrp.search(hasil))

    # Mencari departemen
    pattern_departemen = re.compile(r'\b{}\b'.format(nama_departemen))
    departemen_results = bool(pattern_departemen.search(hasil))

    # Mencari Tanda Tangan
    pejabat = "9999999"
    if (skala == 'Nasional') | (skala =='Lokal'):
        pejabat = r'Direktur Pendidikan|Dekan\w*|Wakil Rektor\w*|Direktur Kemahasiswaan'
    elif skala == 'Internasional':
        pejabat = r'Wakil Rektor\w*|Rektor\w*'


    regex_tanda_tangan = re.compile(pejabat, re.IGNORECASE)
    tanda_tangan_results = bool(regex_tanda_tangan.search(hasil))

    # Keperluan lomba
    kata_kunci = r'lomba\w*|peserta lomba\w*|kompetisi\w*|competition\w*|peserta\w*|finalis\w*|olimpiade\w*|kejuaraan\w*'
    pattern_keperluan = re.compile(kata_kunci, re.IGNORECASE)
    keperluan_lomba_results = (bool(pattern_keperluan.search(hasil)))


    return mahasiswa_results, nrp_results, departemen_results, tanda_tangan_results, keperluan_lomba_results
    
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

    # Image normalization - Normalize image between 0 and 255
    normalized_image = cv2.normalize(image, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    # Skew correction
    gray = cv2.cvtColor(normalized_image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
    angle = 0.0
    if lines is not None:
        total_angle = 0.0
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle += np.arctan2(y2 - y1, x2 - x1)
            total_angle += 1
        angle /= total_angle
    rotation_matrix = cv2.getRotationMatrix2D((image.shape[1] / 2, image.shape[0] / 2), angle, 1)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]))
    
    # Image scaling
    scaled_image = cv2.resize(rotated_image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    
    # Noise removal - Gaussian Blur
    blurred_image = cv2.GaussianBlur(scaled_image, (5, 5), 0)
    
    # Gray scale image
    gray_image = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2GRAY)
    
    # Thresholding or Binarization
    _, threshold_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Dilation
    kernel = np.ones((3, 3), np.uint8)
    dilated_image = cv2.dilate(threshold_image, kernel, iterations=1)

    return dilated_image


def format_date_range(start_date, end_date):
    
    # Parse the dates
    start_date_parts = start_date.split()
    end_date_parts = end_date.split()
    
    # Check if the start and end dates are in the same month and year
    if start_date_parts[1:] == end_date_parts[1:]:
        # Same month and year
        return ((f"{start_date_parts[0]}-{end_date_parts[0]} {end_date_parts[1]} {end_date_parts[2]}").lower())
    else:
        # Different month or year
        return ((f"{start_date_parts[0]} {start_date_parts[1]}-{end_date_parts[0]} {end_date_parts[1]} {end_date_parts[2]}").lower())
    
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
        if flag == 0:
            preprocessed_image = preprocess_for_ocr(file_name)
            extracted_text = extract_text_from_image(preprocessed_image)
            result_string = ' '.join(extracted_text)
        else:
            extracted_text = extract_text_from_image(file_name)
            result_string = ' '.join(extracted_text)
        
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
