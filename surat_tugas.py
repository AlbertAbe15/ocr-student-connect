from pdf2image import convert_from_bytes
import requests
from pytesseract import image_to_string
import re


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




def matching_data_surat(hasil, nama_mahasiswa, nrp, nama_departemen, skala):
    mahasiswa_results = ''
    nrp_results = ''
    departemen_results = ''
    tanda_tangan_results = ''
    keperluan_lomba_results = ''

    confidence_nama_mahasiswa = 0
    confidence_nrp = 0
    confidence_departemen = 0
    confidence_tanda_tangan = 0
    confidence_keperluan_lomba = 0
    
    # Mencari hasil nama
    pattern_nama_mahasiswa = re.compile(r'\b{}\b'.format(re.escape(nama_mahasiswa)))
    mahasiswa_results = bool(pattern_nama_mahasiswa.search(hasil))
    if pattern_nama_mahasiswa.search(hasil):
        confidence_nama_mahasiswa = 100
    else:
        confidence_nama_mahasiswa = 0

    # Mencari hasil nrp
    pattern_nrp = re.compile(r'\b{}\b'.format(re.escape(str(nrp))))
    nrp_results = bool(pattern_nrp.search(hasil))
    if pattern_nrp.search(hasil):
        confidence_nrp = 100
    else:
        confidence_nrp = 0

    # Mencari departemen
    pattern_departemen = re.compile(r'\b{}\b'.format(nama_departemen))
    departemen_results = bool(pattern_departemen.search(hasil))
    if pattern_departemen.search(hasil):
        confidence_departemen = 100
    else:
        confidence_departemen = 0

    # Mencari Tanda Tangan
    pejabat = "9999999"
    if (skala == 'Nasional') | (skala =='Lokal'):
        pejabat = r'Direktur Pendidikan|Dekan\w*|Wakil Rektor\w*|Direktur Kemahasiswaan'
    elif skala == 'Internasional':
        pejabat = r'Wakil Rektor\w*|Rektor\w*'


    regex_tanda_tangan = re.compile(pejabat, re.IGNORECASE)
    tanda_tangan_results = bool(regex_tanda_tangan.search(hasil))
    if regex_tanda_tangan.search(hasil):
        confidence_tanda_tangan = 100
    else:
        confidence_tanda_tangan = 0

    # Keperluan lomba
    kata_kunci = r'lomba\w*|peserta lomba\w*|kompetisi\w*|competition\w*|peserta\w*|finalis\w*|olimpiade\w*|kejuaraan\w*'
    pattern_keperluan = re.compile(kata_kunci, re.IGNORECASE)
    keperluan_lomba_results = (bool(pattern_keperluan.search(hasil)))
    if pattern_keperluan.search(hasil):
        confidence_keperluan_lomba = 100
    else:
        confidence_keperluan_lomba = 0


    return mahasiswa_results, nrp_results, departemen_results, tanda_tangan_results, keperluan_lomba_results, confidence_nama_mahasiswa, confidence_nrp, confidence_departemen, confidence_tanda_tangan, confidence_keperluan_lomba
    