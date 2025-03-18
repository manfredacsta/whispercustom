from flask import Flask, request, jsonify
import whisper
import os
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Implementación manual de CORS
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET'
    return response

# Ruta para manejar las solicitudes OPTIONS (pre-flight)
@app.route('/transcribe', methods=['OPTIONS'])
def handle_options():
    return '', 200

# Cargar el modelo de Whisper (puedes elegir entre 'tiny', 'base', 'small', 'medium', 'large')
# 'tiny' o 'base' son recomendados para servidores gratuitos por su menor uso de recursos
model = whisper.load_model("tiny")

# Endpoint de prueba simple para verificar que el servidor está funcionando
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "ok", "message": "El servidor está funcionando correctamente"})

# Endpoint de eco para depuración
@app.route('/echo', methods=['POST'])
def echo():
    print("Solicitud a /echo recibida")
    data = request.form.to_dict()
    files = {name: f.filename for name, f in request.files.items()}
    headers = dict(request.headers)
    
    print(f"Headers: {headers}")
    print(f"Form data: {data}")
    print(f"Files: {files}")
    
    return jsonify({
        "message": "Echo endpoint",
        "received_data": data,
        "received_files": files,
        "content_type": request.headers.get('Content-Type', 'No content type')
    })

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    print("Solicitud a /transcribe recibida")
    print(f"Headers: {dict(request.headers)}")
    print(f"Form data: {request.form.to_dict()}")
    print(f"Files: {list(request.files.keys())}")
    
    # Verificar si hay un archivo en la solicitud
    if 'file' not in request.files:
        print("No se encontró el campo 'file' en la solicitud")
        return jsonify({'error': 'No se envió ningún archivo'}), 400
    
    file = request.files['file']
    
    # Verificar si se seleccionó un archivo
    if file.filename == '':
        print("El nombre del archivo está vacío")
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    print(f"Archivo recibido: {file.filename}")
    
    # Crear un archivo temporal para guardar el audio
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, secure_filename(file.filename))
    
    try:
        # Guardar el archivo
        file.save(temp_path)
        print(f"Archivo guardado en: {temp_path}")
        
        # Por ahora, simplemente confirma que recibió el archivo correctamente
        return jsonify({
            'success': True,
            'message': 'Archivo recibido correctamente',
            'filename': file.filename,
            'file_size': os.path.getsize(temp_path)
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        # En caso de error
        return jsonify({'error': str(e)}), 500
    finally:
        # Limpiar archivos temporales
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except Exception as e:
            print(f"Error al limpiar archivos temporales: {str(e)}")

if __name__ == '__main__':
    # Puerto definido por la variable de entorno (necesario para muchos servicios de hosting)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
