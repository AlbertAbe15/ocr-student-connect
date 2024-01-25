import cv2
from fuzzywuzzy import fuzz
from datetime import datetime
from PIL import Image
import re
import easyocr
from pdf2image import convert_from_bytes
import requests
import numpy as np


def convert_pdf_to_images(url):
    # Mengunduh konten PDF dari URL
    response = requests.get(url)
    if response.status_code != 200:
        return None, "Tidak berhasil membuka file PDF dari URL yang diberikan"

    # Mengonversi PDF menjadi gambar menggunakan pdf2image
    images = convert_from_bytes(response.content)

    cv_images = []
    for image in images:
        # Mengonversi gambar PIL ke array NumPy
        img_np = np.array(image)

        # Mengonversi array NumPy ke format gambar OpenCV
        img_cv2 = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        if img_cv2 is None or img_cv2.size == 0:
            continue

        cv_images.append(img_cv2)

    return cv_images, None

def extract_text_from_image(image_path, reader):
    bounds = reader.readtext(image_path)
    extracted_text = [detection[1].lower() for detection in bounds]
    return extracted_text

def rotate_image(image):
    width, height = image.shape[:2]

    # Periksa apakah gambar berorientasi potret
    if height < width:
        # Jika iya, putar gambar menjadi landscape (90 derajat searah jarum jam)
        center = (width / 2, height / 2)
        M = cv2.getRotationMatrix2D(center, -90, 1.0)
        image = cv2.warpAffine(image, M, (width, height))
        return image
    else:
        return image  # Jika sudah landscape, kembalikan nama file asli

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
        return f"{start_date_parts[0]}-{end_date_parts[0]} {end_date_parts[1]} {end_date_parts[2]}".lower()
    else:
        # Different month or year
        return f"{start_date_parts[0]} {start_date_parts[1]}-{end_date_parts[0]} {end_date_parts[1]} {end_date_parts[2]}".lower()
    
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
    reader = easyocr.Reader(['en'], gpu=False)
    
    if flag == 0:
        preprocessed_image = preprocess_for_ocr(file_name)
        extracted_text = extract_text_from_image(preprocessed_image, reader)
        result_string = ' '.join(extracted_text)
    else:
        print("Berhasil Masuk ke If Else")
        extracted_text = extract_text_from_image(file_name, reader)
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
    confidence_nama_mahasiswa = 0
    confidence_nama_kompetisi = 0
    confidence_nama_penyelenggara = 0
    confidence_tanda_tangan = 0
    confidence_tanggal_kompetisi = 0
    confidence_capaian = 0



    # Mencari Nama Mahasiswa
    pattern_nama_mahasiswa = re.compile(rf'\b{re.escape(nama_mahasiswa)}\b')
    if pattern_nama_mahasiswa.search(result_string):
        mahasiswa_results.append(True)
        confidence_nama_mahasiswa = 100

    elif any(fuzz.ratio(nama_mahasiswa, text) > 70 for text in extracted_text):
        for text in extracted_text:
        # Menghitung fuzzy ratio
            current_ratio = fuzz.ratio(nama_mahasiswa, text)

            # Memperbarui nilai confidence_nama_mahasiswa jika current_ratio lebih tinggi
            if current_ratio > confidence_nama_mahasiswa:
                confidence_nama_mahasiswa = current_ratio

        mahasiswa_results.append(any(fuzz.ratio(nama_mahasiswa, text) > 70 for text in extracted_text))
    else:
        name_asli = sorted(nama_mahasiswa)
        mahasiswa_results.append(any((name_asli == text)for text in extracted_text))
        if any((name_asli == text)for text in extracted_text):
            confidence_nama_mahasiswa = 100
                
    # Mencari Nama Kompetisi            
    pattern_nama_kompetisi = re.compile(rf'\b{re.escape(nama_kompetisi)}\b')
    if pattern_nama_kompetisi.search(result_string):
        kompetisi_results.append(True)
        confidence_nama_kompetisi = 100
    elif any(fuzz.ratio(nama_kompetisi, text) > 70 for text in extracted_text):
        for text in extracted_text:
        # Menghitung fuzzy ratio
            current_ratio = fuzz.ratio(nama_kompetisi, text)

            # Memperbarui nilai confidence_nama_mahasiswa jika current_ratio lebih tinggi
            if current_ratio > confidence_nama_kompetisi:
                confidence_nama_kompetisi = current_ratio
                
        kompetisi_results.append(any(fuzz.ratio(nama_kompetisi, text) > 70 for text in extracted_text))
    else:
        kompetisi_asli = sorted(nama_kompetisi)
        kompetisi_results.append(any((kompetisi_asli == text)for text in extracted_text))
        if any((kompetisi_asli == text)for text in extracted_text):
            confidence_nama_kompetisi = 100
    
    # Mencari Nama Penyelenggara 
    pattern_nama_penyelenggara = re.compile(rf'\b{re.escape(nama_penyelenggara)}\b')
    if pattern_nama_penyelenggara.search(result_string):
        penyelenggara_results.append(True)
        confidence_nama_penyelenggara = 100
    elif any(fuzz.ratio(nama_penyelenggara, text) > 70 for text in extracted_text):
        for text in extracted_text:
        # Menghitung fuzzy ratio
            current_ratio = fuzz.ratio(nama_penyelenggara, text)

            # Memperbarui nilai confidence_nama_mahasiswa jika current_ratio lebih tinggi
            if current_ratio > confidence_nama_penyelenggara:
                confidence_nama_penyelenggara = current_ratio
        penyelenggara_results.append(any(fuzz.ratio(nama_penyelenggara, text) > 70 for text in extracted_text))
    else:
        penyelenggara_asli = sorted(nama_penyelenggara)
        penyelenggara_results.append(any((penyelenggara_asli == text)for text in extracted_text))
        if any((penyelenggara_asli == text)for text in extracted_text):
            confidence_nama_penyelenggara = 100
        
    # Mencari Tanggal Selesai
    pattern_tanggal_selesai = re.compile(rf'\b{re.escape(tanggal_selesai)}\b')
    if pattern_tanggal_selesai.search(result_string):
        tanggal_selesai_results.append(True)
        confidence_tanggal_kompetisi = 100
    else:
        if any(fuzz.ratio(tanggal_selesai, text) > 70 for text in extracted_text):
            tanggal_selesai_results.append(any(fuzz.ratio(tanggal_selesai, text) > 70 for text in extracted_text))
            for text in extracted_text:
            # Menghitung fuzzy ratio
                current_ratio = fuzz.ratio(tanggal_selesai, text)

                # Memperbarui nilai confidence_nama_mahasiswa jika current_ratio lebih tinggi
                if current_ratio > confidence_tanggal_kompetisi:
                    confidence_tanggal_kompetisi = current_ratio
        elif any(fuzz.ratio(convert_indonesian_date_to_english(tanggal_selesai), text) > 70 for text in extracted_text):
            tanggal_selesai = convert_indonesian_date_to_english(tanggal_selesai)
            tanggal_selesai_results.append(any(fuzz.ratio(tanggal_selesai, text) > 70 for text in extracted_text))
            for text in extracted_text:
            # Menghitung fuzzy ratio
                current_ratio = fuzz.ratio(tanggal_selesai, text)

                # Memperbarui nilai confidence_nama_mahasiswa jika current_ratio lebih tinggi
                if current_ratio > confidence_tanggal_kompetisi:
                    confidence_tanggal_kompetisi = current_ratio
        else:
            pattern_tanggal_mulai_selesai = re.compile(rf'\b{re.escape(format_date_range(tanggal_mulai, tanggal_selesai))}\b')
            if pattern_tanggal_mulai_selesai.search(result_string):
                tanggal_selesai_results.append(True)
                confidence_tanggal_kompetisi = 100
            else:
                tanggal_selesai_results.append(any(fuzz.ratio(format_date_range(tanggal_mulai, tanggal_selesai), text) > 70 for text in extracted_text))
                for text in extracted_text:
                    # Menghitung fuzzy ratio
                    current_ratio = fuzz.ratio(format_date_range(tanggal_mulai, tanggal_selesai), text)

                    # Memperbarui nilai confidence_nama_mahasiswa jika current_ratio lebih tinggi
                    if current_ratio > confidence_tanggal_kompetisi:
                        confidence_tanggal_kompetisi = current_ratio

    # Mencari Hasil Capaian
    if hasil_capaian == 'juara 1/emas':
        pattern_hasil_capaian = re.compile(r'juara\s+1|1st\s+winner|first\s+winner|juara\s+I|best\s+delegate|first|emas|gold|juara\s+i|best\s+|finalis', re.IGNORECASE)
    elif hasil_capaian == 'juara 2/perak':
        pattern_hasil_capaian = re.compile(r'juara\s+2|2nd\s+winner|second\s+winner|juara\s+II|runner\s+up|second|perak|silver|juara\s+ii|finalis', re.IGNORECASE)
    elif hasil_capaian == 'juara 3/perunggu':
        pattern_hasil_capaian = re.compile(r'juara\s+3|3rd\s+winner|third\s+winner|juara\s+III|perunggu|bronze|juara\s+iii|finalis', re.IGNORECASE)
    else:
        capaian_results.append(True)

    if pattern_hasil_capaian.search(result_string):
        capaian_results.append(True)
        confidence_capaian = 100
    elif any(fuzz.ratio(hasil_capaian, text) > 70 or pattern_hasil_capaian.search(text) for text in extracted_text):
        capaian_results.append(any(fuzz.ratio(hasil_capaian, text) > 70 or pattern_hasil_capaian.search(text) for text in extracted_text)) 
        for text in extracted_text:
            # Menghitung fuzzy ratio
                current_ratio = fuzz.ratio(hasil_capaian, text)

                # Memperbarui nilai confidence_nama_mahasiswa jika current_ratio lebih tinggi
                if current_ratio > confidence_capaian:
                    confidence_capaian = current_ratio
        if pattern_hasil_capaian.search(result_string):
            confidence_capaian = 100
    else:
        capaian_asli = sorted(hasil_capaian)
        capaian_results.append(any((capaian_asli == text)for text in extracted_text))
        if any((capaian_asli == text)for text in extracted_text):
            confidence_capaian = 100

    # Mencari Tanda Tangan
    tanda_tangan_patterns = r'Dekan\w*|Wakil Rektor\w*|Kepala Prodi\w*|Kepala Departemen\w*|Rektor\w*|Secretary General\w*|Head Depart\w*|CEO\w*|Dean\w*|Director\w*|President\w*|Chairman\w*|Ketua Umum\w*|Direktur\w*|Kepala Pusat\w*|Kepala Dinas\w*|Chief Technical Officer\w*|Direktur Jenderal\w*|Pembina\w*|Kepala Pusat\w*|Head of\w*|Secretary-General|Ketua Program Studi\s*|Ketua Jurusan\s*'
    regex_tanda_tangan = re.compile(tanda_tangan_patterns, re.IGNORECASE)
    if regex_tanda_tangan.search(result_string):
        tanda_tangan_results.append(True)
        confidence_tanda_tangan = 100
    else:
        tanda_tangan_results.append(False)
        confidence_tanda_tangan = 0

    if (not any(mahasiswa_results)) & (not any(kompetisi_results)) & (not any(penyelenggara_results)) & (not (any(tanggal_selesai_results))) & (not any(capaian_results)) & (not any(tanda_tangan_results)):
        if flag == 0:
            preprocessed_image = preprocess_for_ocr(file_name)
            gambar_rotasi = rotate_image(preprocessed_image)
            extracted_text = extract_text_from_image(gambar_rotasi, reader)
            result_string = ' '.join(extracted_text)
            print(result_string)
        else:
            gambar_rotasi = rotate_image(file_name)
            extracted_text = extract_text_from_image(gambar_rotasi, reader)
            result_string = ' '.join(extracted_text)
            print(result_string)
                
    # Mencari Nama Mahasiswa
    pattern_nama_mahasiswa = re.compile(rf'\b{re.escape(nama_mahasiswa)}\b')
    print(pattern_nama_mahasiswa.search(result_string))
    if pattern_nama_mahasiswa.search(result_string):
        mahasiswa_results.append(True)
        confidence_nama_mahasiswa = 100

    elif any(fuzz.ratio(nama_mahasiswa, text) > 70 for text in extracted_text):
        for text in extracted_text:
        # Menghitung fuzzy ratio
            current_ratio = fuzz.ratio(nama_mahasiswa, text)

            # Memperbarui nilai confidence_nama_mahasiswa jika current_ratio lebih tinggi
            if current_ratio > confidence_nama_mahasiswa:
                confidence_nama_mahasiswa = current_ratio

        mahasiswa_results.append(any(fuzz.ratio(nama_mahasiswa, text) > 70 for text in extracted_text))
    else:
        name_asli = sorted(nama_mahasiswa)
        mahasiswa_results.append(any((name_asli == text)for text in extracted_text))
        if any((name_asli == text)for text in extracted_text):
            confidence_nama_mahasiswa = 100
                
    # Mencari Nama Kompetisi            
    pattern_nama_kompetisi = re.compile(rf'\b{re.escape(nama_kompetisi)}\b')
    if pattern_nama_kompetisi.search(result_string):
        kompetisi_results.append(True)
        confidence_nama_kompetisi = 100
    elif any(fuzz.ratio(nama_kompetisi, text) > 70 for text in extracted_text):
        for text in extracted_text:
        # Menghitung fuzzy ratio
            current_ratio = fuzz.ratio(nama_kompetisi, text)

            # Memperbarui nilai confidence_nama_mahasiswa jika current_ratio lebih tinggi
            if current_ratio > confidence_nama_kompetisi:
                confidence_nama_kompetisi = current_ratio
                
        kompetisi_results.append(any(fuzz.ratio(nama_kompetisi, text) > 70 for text in extracted_text))
    else:
        kompetisi_asli = sorted(nama_kompetisi)
        kompetisi_results.append(any((kompetisi_asli == text)for text in extracted_text))
        if any((kompetisi_asli == text)for text in extracted_text):
            confidence_nama_kompetisi = 100
    
    # Mencari Nama Penyelenggara 
    pattern_nama_penyelenggara = re.compile(rf'\b{re.escape(nama_penyelenggara)}\b')
    if pattern_nama_penyelenggara.search(result_string):
        penyelenggara_results.append(True)
        confidence_nama_penyelenggara = 100
    elif any(fuzz.ratio(nama_penyelenggara, text) > 70 for text in extracted_text):
        for text in extracted_text:
        # Menghitung fuzzy ratio
            current_ratio = fuzz.ratio(nama_penyelenggara, text)

            # Memperbarui nilai confidence_nama_mahasiswa jika current_ratio lebih tinggi
            if current_ratio > confidence_nama_penyelenggara:
                confidence_nama_penyelenggara = current_ratio
        penyelenggara_results.append(any(fuzz.ratio(nama_penyelenggara, text) > 70 for text in extracted_text))
    else:
        penyelenggara_asli = sorted(nama_penyelenggara)
        penyelenggara_results.append(any((penyelenggara_asli == text)for text in extracted_text))
        if any((penyelenggara_asli == text)for text in extracted_text):
            confidence_nama_penyelenggara = 100
        
    # Mencari Tanggal Selesai
    pattern_tanggal_selesai = re.compile(rf'\b{re.escape(tanggal_selesai)}\b')
    if pattern_tanggal_selesai.search(result_string):
        tanggal_selesai_results.append(True)
        confidence_tanggal_kompetisi = 100
    else:
        if any(fuzz.ratio(tanggal_selesai, text) > 70 for text in extracted_text):
            tanggal_selesai_results.append(any(fuzz.ratio(tanggal_selesai, text) > 70 for text in extracted_text))
            for text in extracted_text:
            # Menghitung fuzzy ratio
                current_ratio = fuzz.ratio(tanggal_selesai, text)

                # Memperbarui nilai confidence_nama_mahasiswa jika current_ratio lebih tinggi
                if current_ratio > confidence_tanggal_kompetisi:
                    confidence_tanggal_kompetisi = current_ratio
        elif any(fuzz.ratio(convert_indonesian_date_to_english(tanggal_selesai), text) > 70 for text in extracted_text):
            tanggal_selesai = convert_indonesian_date_to_english(tanggal_selesai)
            tanggal_selesai_results.append(any(fuzz.ratio(tanggal_selesai, text) > 70 for text in extracted_text))
            for text in extracted_text:
            # Menghitung fuzzy ratio
                current_ratio = fuzz.ratio(tanggal_selesai, text)

                # Memperbarui nilai confidence_nama_mahasiswa jika current_ratio lebih tinggi
                if current_ratio > confidence_tanggal_kompetisi:
                    confidence_tanggal_kompetisi = current_ratio
        else:
            pattern_tanggal_mulai_selesai = re.compile(rf'\b{re.escape(format_date_range(tanggal_mulai, tanggal_selesai))}\b')
            if pattern_tanggal_mulai_selesai.search(result_string):
                tanggal_selesai_results.append(True)
                confidence_tanggal_kompetisi = 100
            else:
                tanggal_selesai_results.append(any(fuzz.ratio(format_date_range(tanggal_mulai, tanggal_selesai), text) > 70 for text in extracted_text))
                for text in extracted_text:
                    # Menghitung fuzzy ratio
                    current_ratio = fuzz.ratio(format_date_range(tanggal_mulai, tanggal_selesai), text)

                    # Memperbarui nilai confidence_nama_mahasiswa jika current_ratio lebih tinggi
                    if current_ratio > confidence_tanggal_kompetisi:
                        confidence_tanggal_kompetisi = current_ratio

    # Mencari Hasil Capaian
    if hasil_capaian == 'juara 1/emas':
        pattern_hasil_capaian = re.compile(r'juara\s+1|1st\s+winner|first\s+winner|juara\s+I|best\s+delegate|first|emas|gold|juara\s+i|best\s+|finalis', re.IGNORECASE)
    elif hasil_capaian == 'juara 2/perak':
        pattern_hasil_capaian = re.compile(r'juara\s+2|2nd\s+winner|second\s+winner|juara\s+II|runner\s+up|second|perak|silver|juara\s+ii|finalis', re.IGNORECASE)
    elif hasil_capaian == 'juara 3/perunggu':
        pattern_hasil_capaian = re.compile(r'juara\s+3|3rd\s+winner|third\s+winner|juara\s+III|perunggu|bronze|juara\s+iii|finalis', re.IGNORECASE)
    else:
        capaian_results.append(True)

    if pattern_hasil_capaian.search(result_string):
        capaian_results.append(True)
        confidence_capaian = 100
    elif any(fuzz.ratio(hasil_capaian, text) > 70 or pattern_hasil_capaian.search(text) for text in extracted_text):
        capaian_results.append(any(fuzz.ratio(hasil_capaian, text) > 70 or pattern_hasil_capaian.search(text) for text in extracted_text)) 
        for text in extracted_text:
            # Menghitung fuzzy ratio
                current_ratio = fuzz.ratio(hasil_capaian, text)

                # Memperbarui nilai confidence_nama_mahasiswa jika current_ratio lebih tinggi
                if current_ratio > confidence_capaian:
                    confidence_capaian = current_ratio
        if pattern_hasil_capaian.search(result_string):
            confidence_capaian = 100
    else:
        capaian_asli = sorted(hasil_capaian)
        capaian_results.append(any((capaian_asli == text)for text in extracted_text))
        if any((capaian_asli == text)for text in extracted_text):
            confidence_capaian = 100

    # Mencari Tanda Tangan
    tanda_tangan_patterns = r'Dekan\w*|Wakil Rektor\w*|Kepala Prodi\w*|Kepala Departemen\w*|Rektor\w*|Secretary General\w*|Head Depart\w*|CEO\w*|Dean\w*|Director\w*|President\w*|Chairman\w*|Ketua Umum\w*|Direktur\w*|Kepala Pusat\w*|Kepala Dinas\w*|Chief Technical Officer\w*|Direktur Jenderal\w*|Pembina\w*|Kepala Pusat\w*|Head of\w*|Secretary-General|Ketua Program Studi\s*|Ketua Jurusan\s*'
    regex_tanda_tangan = re.compile(tanda_tangan_patterns, re.IGNORECASE)
    if regex_tanda_tangan.search(result_string):
        tanda_tangan_results.append(True)
        confidence_tanda_tangan = 100
    else:
        tanda_tangan_results.append(False)
        confidence_tanda_tangan = 0


        results['Nama Mahasiswa'].append(any(mahasiswa_results))
        results['Nama Kompetisi'].append(any(kompetisi_results))
        results['Penyelenggara'].append(any(penyelenggara_results))
        results['Tanggal Selesai'].append(any(tanggal_selesai_results))
        results['Capaian'].append(any(capaian_results))
        results['Tanda Tangan'].append(any(tanda_tangan_results))
            
    
    return any(mahasiswa_results), any(kompetisi_results), any(penyelenggara_results), any(tanggal_selesai_results), any(capaian_results), any(tanda_tangan_results), confidence_nama_mahasiswa, confidence_nama_kompetisi, confidence_nama_penyelenggara, confidence_tanggal_kompetisi, confidence_capaian, confidence_tanda_tangan