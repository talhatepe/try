
from flask import Flask, request, send_file, render_template
import os
import io
import tempfile
import pandas as pd
import camelot
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return "PDF dosyası bulunamadı", 400

    file = request.files['pdf']
    pdf_bytes = file.read()
    output_df = pd.DataFrame()

    # Önce Camelot ile dijital tablo var mı dene
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf.flush()
            tables = camelot.read_pdf(temp_pdf.name, pages='1', flavor='stream')
            if tables and tables.n > 0:
                output_df = tables[0].df  # İlk tabloyu al
    except Exception as e:
        print("Camelot başarısız:", e)

    # Eğer tablo çıkarılamadıysa OCR ile dene
    if output_df.empty:
        try:
            images = convert_from_bytes(pdf_bytes)
            text = ""
            for image in images:
                gray = image.convert('L')
                text += pytesseract.image_to_string(gray, lang='tur') + "\n"
            output_df = pd.DataFrame({'OCR Metni': text.split("\n")})
        except Exception as e:
            return f"OCR işlemi başarısız: {e}", 500

    # Excel'e yaz
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        output_df.to_excel(writer, index=False, sheet_name='Fatura')
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='fatura_sonuclari.xlsx'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
