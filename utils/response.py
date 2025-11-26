from flask import render_template, request, jsonify


def handleResponse(resposta, nomeTemplate):

    #Boolean que armazena se a requisição feita foi em formato json, útil para fazer testes com o postman e receber uma resposta de acordo
    isJson = request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json'

    #Usando get pq ele retorna um valor padrão caso a chave nao tenha sido definida, evitando que o servidor quebre por conta de um problema com os controllers
    mensagem = resposta.get('mensagem', 'Ocorreu um erro inesperado.')

    if isJson:
        return jsonify(resposta), codigoHttp(resposta['status'])
    else:

        if resposta['status'] == 'SUCESSO':
            return render_template(f"{nomeTemplate}.html", dados = resposta['data']), codigoHttp(resposta['status'])
        else:
            return render_template(f"{nomeTemplate}.html", mensagem = mensagem), codigoHttp(resposta['status'])
    
def codigoHttp(mensagemStatus):
    if mensagemStatus == 'SUCESSO':
        return 200
    elif mensagemStatus == 'FORM_INVALIDO':
        return 400
    elif mensagemStatus == 'NAO_AUTORIZADO':
        return 401
    elif mensagemStatus == 'NAO_ENCONTRADO':
        return 404
    elif mensagemStatus == 'CONFLITO':
        return 409
    else:
        return 500