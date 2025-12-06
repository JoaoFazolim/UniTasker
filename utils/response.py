from flask import render_template, request, jsonify, flash, redirect


def handleResponse(resposta, nomeTemplate):

    #Boolean que armazena se a requisição feita foi em formato json, útil para fazer testes com o postman e receber uma resposta de acordo
    isJson = request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json'

    http_code = codigoHttp(resposta['status'])

    #Usando get pq ele retorna um valor padrão caso a chave nao tenha sido definida, evitando que o servidor quebre por conta de um problema com os controllers
    mensagem = resposta.get('mensagem', 'Ocorreu um erro inesperado.')

    if isJson:
        return jsonify(resposta), http_code
    else:

        #Pequeno ajuste pq o caddy quebra em produção com um render template com codigo 401
        if http_code == 401:
            http_code = 403

        if resposta['status'] == 'SUCESSO':
            return render_template(f"{nomeTemplate}.html", dados = resposta['data']), http_code
        else:
            flash(mensagem, 'erro')
            if request.method == 'POST':
                return redirect(request.url)
            else:

                return render_template(f"{nomeTemplate}.html", dados=None), http_code
    
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
    elif mensagemStatus == 'CRIADO': 
        return 201
    else:
        return 500