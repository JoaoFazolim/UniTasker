// script-colapsarChat.js

document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. REFERÊNCIAS ESSENCIAIS ---
    
    // Elementos da Janela Principal
    const chatContainer = document.getElementById('chat-container'); // O container pai (que tem a classe chat-collapsed)
    const chatToggle = document.querySelector('#chat-container h2'); // O título que serve como botão
    
    // Elementos do Modal de Nova Conversa
    const btnNovoChat = document.getElementById('btn-novo-chat');
    const modalNovoChat = document.getElementById('modal-novo-chat');
    const btnFecharModal = document.getElementById('btn-fechar-modal');
    
    // Elementos do Formulário de Busca (para resetar o estado)
    const areaEnvioInicial = document.getElementById('area-envio-inicial');
    const resultadosBusca = document.getElementById('resultados-busca');
    const inputBusca = document.getElementById('input-busca');
    

    // --- 2. LÓGICA DE EXPANDIR/COLAPSAR O CHAT PRINCIPAL ---
    
    function toggleChatWindow() {
        if (chatContainer.classList.contains('chat-collapsed')) {
            // Se estiver colapsado, expande
            chatContainer.classList.remove('chat-collapsed');
            console.log('Chat Principal Expandido');
        } else {
            // Se estiver expandido, colapsa
            chatContainer.classList.add('chat-collapsed');
            // Garante que o modal de busca também feche ao colapsar
            fecharModalNovoChat(); 
            console.log('Chat Principal Colapsado');
        }
    }
    
    // --- 3. LÓGICA DE ABRIR/FECHAR O MODAL DE BUSCA ---
    
    function abrirModalNovoChat() {
        if (modalNovoChat) {
            // Mostrar o modal (display: flex conforme o CSS)
            modalNovoChat.style.display = 'flex'; 
            
            // Resetar campos para uma nova busca
            areaEnvioInicial.style.display = 'none';
            resultadosBusca.innerHTML = '';
            inputBusca.value = '';
            inputBusca.focus();
            console.log('Modal de Busca Aberto');
        }
    }

    function fecharModalNovoChat() {
        if (modalNovoChat) {
            // Esconder o modal
            modalNovoChat.style.display = 'none';
            console.log('Modal de Busca Fechado');
        }
    }

    // --- 4. CONFIGURAÇÃO DOS LISTENERS ---

    // A. Listener para Expandir/Colapsar o chat (Título H2)
    if (chatToggle) {
        chatToggle.addEventListener('click', toggleChatWindow);
    } else {
        console.error('ERRO JS: Título do chat (H2) não encontrado para a função toggle.');
    }
    
    // B. Listener para abrir o Modal de Busca (Botão Novo Chat)
    if (btnNovoChat) {
        btnNovoChat.addEventListener('click', abrirModalNovoChat);
    } else {
         console.error('ERRO JS: Botão #btn-novo-chat não encontrado.');
    }

    // C. Listener para fechar o Modal (Botão Fechar)
    if (btnFecharModal) {
        btnFecharModal.addEventListener('click', fecharModalNovoChat);
    }
});