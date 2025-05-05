from flask import Flask, request, send_file, render_template
import io
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return "PDF dosyası bulunamadı", 400

    file = request.files['pdf']

    # Örnek veri: Gerçek OCR/Camelot işlemi burada yapılacak
    df = pd.DataFrame({
        'Fatura No': ['123', '456'],
        'Tarih': ['2025-01-01', '2025-01-02'],
        'Tutar': [1000, 2000]
    })

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Fatura')
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='fatura_sonuclari.xlsx'
    )

if __name__ == '__main__':
    app.run(debug=True)
