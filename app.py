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
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    return response

# Ruta para manejar las solicitudes OPTIONS (pre-flight)
@app.route('/transcribe', methods=['OPTIONS'])
def handle_options():
    return '', 200
# Cargar el modelo de Whisper (puedes elegir entre 'tiny', 'base', 'small', 'medium', 'large')
# 'tiny' o 'base' son recomendados para servidores gratuitos por su menor uso de recursos
model = whisper.load_model("tiny")

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    # Verificar si hay un archivo en la solicitud
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400
    
    file = request.files['file']
    
    # Verificar si se seleccionó un archivo
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    # Crear un archivo temporal para guardar el audio
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, secure_filename(file.filename))
    
    try:
        # Guardar el archivo
        file.save(temp_path)
        
        # Por ahora, simplemente confirma que recibió el archivo correctamente
        # Esto es útil para probar si el problema está en la recepción del archivo
        return jsonify({
            'success': True,
            'message': 'Archivo recibido correctamente',
            'filename': file.filename
        })
        
        # Cuando confirmes que esta parte funciona, puedes descomentar el código de transcripción:
        """
        # Transcribir el audio con Whisper
        result = model.transcribe(temp_path, word_timestamps=True)
        
        # Formatear la respuesta con texto y timestamps
        response = {
            'text': result['text'],
            'segments': []
        }
        
        # Añadir información de segmentos con timestamps
        for segment in result['segments']:
            response['segments'].append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text']
            })
        
        # Eliminar el archivo temporal
        os.remove(temp_path)
        os.rmdir(temp_dir)
        
        return jsonify(response)
        """
    
    except Exception as e:
        # En caso de error
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Puerto definido por la variable de entorno (necesario para muchos servicios de hosting)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
