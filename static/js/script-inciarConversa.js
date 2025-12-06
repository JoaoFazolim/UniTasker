
async function iniciarConversaDireta(destinatarioId, conteudo, btnElement) {
    if (!destinatarioId || conteudo.trim() === '') {
        alert('Mensagem e destinatário são obrigatórios.');
        return;
    }

    if (btnElement) {
        btnElement.disabled = true;
        btnElement.textContent = 'Enviando...';
    }

    const payload = {
        destinatario_id: destinatarioId,
        conteudo: conteudo
    };

    try {
        const response = await fetch(`${API_BASE_URL}/iniciar-conversa`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const resultado = await response.json();
        
        if (response.ok) { // Inclui 201 Created
            const conversaId = resultado.data.conversa_id;
            
            alert('Conversa iniciada! Redirecionando para o chat.');
            
            // 💡 Ação Final: Redirecionar para o chat, possivelmente passando o ID
            // Exemplo: window.location.href = `${CHAT_REDIRECT_URL}?conversa=${conversaId}`;
            window.location.href = CHAT_REDIRECT_URL; 

        } else {
            alert(`Erro ao iniciar conversa: ${resultado.mensagem}`);
        }
    } catch (error) {
        console.error('Erro de rede:', error);
        alert('Erro de conexão com o servidor.');
    } finally {
        if (btnElement) {
            btnElement.disabled = false;
            btnElement.textContent = 'Conversar';
        }
    }
}