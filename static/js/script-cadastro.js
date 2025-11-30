function validarSenhas() {
    var senha = document.getElementById("senha").value;
    var confirmarSenha = document.getElementById("confirmar_senha").value;
    var errorDiv = document.getElementById("js-error-message");

    //Mostrar erro
    function mostrarErro(mensagem) {
        errorDiv.textContent = mensagem;
        errorDiv.style.display = 'block'; 
    }

    //Limpa erros anteriores
    errorDiv.style.display = 'none';

    //Verifica se as senhas coincidem
    if (senha != confirmarSenha) {
        mostrarErro("As senhas não coincidem! Por favor, verifique.");
        return false;
    }

    //Verifica o tamanho
    if (senha.length <= 8) {
        mostrarErro("A senha deve possuir mais de 8 caracteres.");
        return false;
    }

    //Verifica sem tem letras maiusculas
    if (!/[A-Z]/.test(senha)) {
        mostrarErro("A senha deve conter pelo menos uma letra maiúscula.");
        return false;
    }

    //Verifica se tem caracteres especiais
    if (!/[!@#$%^&*(),.?":{}|<>_+\-=]/.test(senha)) {
        mostrarErro("A senha deve conter pelo menos um caractere especial (ex: @, #, $, &).");
        return false;
    }

    //Se passar em tudo retorna true
    return true;
}