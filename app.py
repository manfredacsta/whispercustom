from flask import Flask, request, jsonify
import whisper
import os
import tempfile
import json
import traceback
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
    print("===== NUEVA SOLICITUD A /echo =====")
    print(f"Método: {request.method}")
    print(f"URL: {request.url}")
    
    # Registrar todos los headers
    print("Headers:")
    for header, value in request.headers.items():
        print(f"  {header}: {value}")
    
    # Registrar datos del formulario
    print("Form data:")
    for key, value in request.form.items():
        print(f"  {key}: {value}")
    
    # Registrar archivos
    print("Files:")
    for name, file in request.files.items():
        print(f"  {name}: {file.filename} (tipo: {file.content_type})")
    
    # Intentar obtener datos JSON
    try:
        json_data = request.get_json(silent=True)
        print(f"JSON data: {json_data}")
    except:
        print("No JSON data")
    
    print("==========================")
    
    # Preparar respuesta
    data = request.form.to_dict()
    files = {name: {"filename": f.filename, "content_type": f.content_type} for name, f in request.files.items()}
    headers = dict(request.headers)
    
    return jsonify({
        "message": "Echo endpoint",
        "received_data": data,
        "received_files": files,
        "content_type": request.headers.get('Content-Type', 'No content type'),
        "method": request.method,
        "url": request.url,
        "args": request.args.to_dict()
    })

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    print("===== NUEVA SOLICITUD A /transcribe =====")
    print(f"Método: {request.method}")
    print(f"URL: {request.url}")
    
    # Registrar todos los headers
    print("Headers:")
    for header, value in request.headers.items():
        print(f"  {header}: {value}")
    
    # Registrar datos del formulario
    print("Form data:")
    for key, value in request.form.items():
        print(f"  {key}: {value}")
    
    # Registrar archivos
    print("Files:")
    for name, file in request.files.items():
        print(f"  {name}: {file.filename} (tipo: {file.content_type})")
    
    # Intentar obtener datos JSON
    try:
        json_data = request.get_json(silent=True)
        print(f"JSON data: {json_data}")
    except:
        print("No JSON data")
    
    print("Content Type:", request.content_type)
    print("==========================")
    
    # Verificar si hay un archivo en la solicitud
    if not request.files:
        print("No se encontraron archivos en la solicitud")
        return jsonify({'error': 'No se encontraron archivos en la solicitud', 'request_info': {
            'headers': dict(request.headers),
            'form': request.form.to_dict(),
            'files_keys': list(request.files.keys())
        }}), 400
    
    if 'file' not in request.files:
        print("No se encontró el campo 'file' en la solicitud")
        # Lista todos los nombres de archivo que sí se recibieron
        available_files = list(request.files.keys())
        
        # Si hay algún archivo, usémoslo aunque no se llame 'file'
        if available_files:
            print(f"Usando el primer archivo disponible: {available_files[0]}")
            file = request.files[available_files[0]]
        else:
            return jsonify({
                'error': 'No se envió ningún archivo con el nombre "file"',
                'available_files': available_files,
                'request_info': {
                    'headers': dict(request.headers),
                    'form': request.form.to_dict()
                }
            }), 400
    else:
        file = request.files['file']
    
    # Verificar si se seleccionó un archivo
    if file.filename == '':
        print("El nombre del archivo está vacío")
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    print(f"Archivo recibido: {file.filename} (tipo: {file.content_type})")
    
    # Crear un archivo temporal para guardar el audio
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, secure_filename(file.filename))
    
    try:
        # Guardar el archivo
        file.save(temp_path)
        print(f"Archivo guardado en: {temp_path}")
        print(f"Tamaño del archivo: {os.path.getsize(temp_path)} bytes")
        
        # Por ahora, simplemente confirma que recibió el archivo correctamente
        return jsonify({
            'success': True,
            'message': 'Archivo recibido correctamente',
            'filename': file.filename,
            'file_size': os.path.getsize(temp_path),
            'content_type': file.content_type
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        # En caso de error
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'request_info': {
                'headers': dict(request.headers),
                'form': request.form.to_dict(),
                'files_keys': list(request.files.keys())
            }
        }), 500
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
