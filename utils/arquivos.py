from flask import current_app
import os

def validarArquivo(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def verificarPastaUploads(caminho_pasta):
    #Verifica se a pasta de uploads existe e cria caso não existir
    if not os.path.exists(caminho_pasta):
        os.makedirs(caminho_pasta)

def salvarArquivo(arquivo, nome_arquivo):
    #Salva o arquivo na pasta configurada
    pasta_upload = current_app.config['UPLOAD_FOLDER']
    
    #Usa a função auxiliar para garantir que a pasta existe
    verificarPastaUploads(pasta_upload)
    
    caminho_completo = os.path.join(pasta_upload, nome_arquivo)
    arquivo.save(caminho_completo)
    
    return caminho_completo