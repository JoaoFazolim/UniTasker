// chat_script.js
// FUNÇÕES E VARIÁVEIS DO CHAT
// =================================================================================

// VARIÁVEIS GLOBAIS DE ESTADO
let currentConversaId = null;
const API_BASE_URL = '/chat'; 
const BASE_PROFILE_URL = '/usuario/'; 

// Referências aos elementos do DOM
const socket = io(); 
const listaDeThreads = document.getElementById('lista-de-threads');
const messagesDisplay = document.getElementById('messages-display');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const cabecalhoConversa = document.getElementById('cabecalho-conversa');
// ID do Usuário Logado (Convertido para Number para garantir consistência)
const CURRENT_USER_ID = parseInt(document.getElementById('user-id').value); 

// Referências DOM do Modal (Nova Conversa)
const btnNovoChat = document.getElementById('btn-novo-chat');
const modalNovoChat = document.getElementById('modal-novo-chat');
const btnFecharModal = document.getElementById('btn-fechar-modal');
const inputBusca = document.getElementById('input-busca');
const resultadosBusca = document.getElementById('resultados-busca');
const areaEnvioInicial = document.getElementById('area-envio-inicial');
const destinatarioNomeDisplay = document.getElementById('destinatario-nome-display');
const destinatarioIdHidden = document.getElementById('destinatario-id-hidden');
const primeiraMensagemInput = document.getElementById('primeira-mensagem-input');
const btnEnviarPrimeiraMsg = document.getElementById('btn-enviar-primeira-msg');


// ---------------------------------------------------------------------------------
// FUNÇÕES DE UTILIDADE E RENDERIZAÇÃO
// ---------------------------------------------------------------------------------

// Função para formatar a data
function formatDate(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleDateString('pt-BR', { month: 'short', day: 'numeric', year: 'numeric' });
}

// Função para adicionar uma nova mensagem na janela
function appendMessage(messageData, isSelf) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('mensagem-bloco');
    msgDiv.classList.add(isSelf ? 'minha-msg' : 'contato-msg');

    const conteudoMsg = document.createElement('div');
    conteudoMsg.classList.add('conteudo-msg');
    
    if (!isSelf && messageData.remetente_nome) {
        const remetenteNome = document.createElement('span');
        remetenteNome.classList.add('remetente-nome');
        remetenteNome.textContent = messageData.remetente_nome;
        conteudoMsg.appendChild(remetenteNome);
    }
    
    const p = document.createElement('p');
    p.textContent = messageData.conteudo;

    const hora = document.createElement('span');
    hora.classList.add('hora-msg');
    hora.textContent = new Date(messageData.data_envio).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

    conteudoMsg.appendChild(p);
    conteudoMsg.appendChild(hora);
    msgDiv.appendChild(conteudoMsg);

    messagesDisplay.appendChild(msgDiv);
    messagesDisplay.scrollTop = messagesDisplay.scrollHeight;
}

// Limpa e exibe o cabeçalho da conversa
function updateConversaHeader(contatoNome, contatoImagemUrl) {
    cabecalhoConversa.querySelector('.nome-contato').textContent = contatoNome;
    
    // 💡 CORREÇÃO 4: Injeta a URL da imagem no cabeçalho
    const headerAvatar = cabecalhoConversa.querySelector('.avatar-mini'); 
    if (headerAvatar) {
        headerAvatar.src = contatoImagemUrl;
    }
}


// --- ATUALIZAÇÃO DA THREAD NA LISTA DE CONVERSAS (FUNÇÃO FALTANTE) ---
function updateThreadPreview(messageData) {
    const threadItem = document.querySelector(`.thread-item[data-conversa-id="${messageData.conversa_id}"]`);
    
    if (threadItem) {
        const ultimaMensagemSpan = threadItem.querySelector('.ultima-mensagem');
        if (ultimaMensagemSpan) {
            const isSelf = messageData.remetente_id === CURRENT_USER_ID;
            const prefix = isSelf ? 'Você: ' : '';
            ultimaMensagemSpan.textContent = prefix + messageData.conteudo;
        }
        
        // Mover a thread para o topo da lista (garante UX)
        if (threadItem.parentElement) {
            threadItem.parentElement.prepend(threadItem);
        }
    } else {
        // Se a thread não existe (ex: conversa nova), recarrega a lista
        loadConversas();
    }
}


// ---------------------------------------------------------------------------------
// FUNÇÕES DE COMUNICAÇÃO REST E ESTADO
// ---------------------------------------------------------------------------------

// Manipulador de clique para carregar uma nova conversa
function handleThreadClick(conversaId, contatoNome, contatoImagemUrl) {
    const numericConversaId = parseInt(conversaId);

    if (currentConversaId === numericConversaId) return;

    if (currentConversaId) {
        socket.emit('leave', { conversa_id: currentConversaId });
    }

    currentConversaId = numericConversaId;
    // 💡 CORREÇÃO 3: Passa o URL da imagem para a função que atualiza o cabeçalho
    updateConversaHeader(contatoNome, contatoImagemUrl);
    
    document.querySelectorAll('.thread-item').forEach(item => {
        item.classList.remove('thread-ativo');
    });
    document.querySelector(`.thread-item[data-conversa-id="${conversaId}"]`).classList.add('thread-ativo');
    
    socket.emit('join', { conversa_id: currentConversaId });

    loadHistorico(conversaId);
}

// --- CARREGAR LISTA DE CONVERSAS (REST) ---
async function loadConversas() {
    let conversas = []; // 💡 CORREÇÃO 1: Define 'conversas' aqui
    try {
        const response = await fetch(`${API_BASE_URL}/conversas`);
        if (!response.ok) {
            // Se a API não responder com OK (ex: 401 Unauthorized), lança erro
            throw new Error('Falha ao carregar conversas - Resposta de rede ruim.');
        }
        
        conversas = await response.json(); // Atribui o valor aqui
        
        listaDeThreads.innerHTML = ''; 
        
        conversas.forEach(conv => {
            const outroUsuario = conv.usuario_com_quem_falo;
            // 💡 CORREÇÃO 2: Usa o caminho de uploads definido no backend para o src da imagem
            const imagemUrl = `/static/images/uploads/${outroUsuario.imagem}`; 
            
            const li = document.createElement('li');
            li.classList.add('thread-item');
            li.setAttribute('data-conversa-id', conv.id);
            // Armazenamos a URL completa no DOM para facilitar a recuperação
            li.setAttribute('data-imagem-url', imagemUrl); 
            li.innerHTML = `
                <div class="avatar-contato">
                    <img src="${imagemUrl}" alt="Avatar" class="avatar-mini">
                </div>
                <div class="info-conversa">
                    <span class="nome-contato">${outroUsuario.nome}</span>
                    <span class="ultima-mensagem">${conv.ultima_mensagem}</span>
                </div>
                <span class="data-ultima-msg">${formatDate(conv.data_ultima_mensagem)}</span>
            `;

            li.addEventListener('click', () => {
                // Passa a URL completa para handleThreadClick
                handleThreadClick(conv.id.toString(), outroUsuario.nome, imagemUrl); 
            });

            listaDeThreads.appendChild(li);
        });

        // Opcional: Ativar a primeira conversa da lista automaticamente
        if (conversas.length > 0 && currentConversaId === null) {
            const primeiraConv = conversas[0];
            const imagemUrl = `/static/images/uploads/${primeiraConv.usuario_com_quem_falo.imagem}`;
            // Chama o handleThreadClick com a URL da imagem
            handleThreadClick(primeiraConv.id.toString(), primeiraConv.usuario_com_quem_falo.nome, imagemUrl); 
        }

    } catch (error) {
        console.error("Erro ao carregar conversas:", error);
    }
}

// --- CARREGAR HISTÓRICO DE MENSAGENS (REST) ---
async function loadHistorico(conversaId) {
    messagesDisplay.innerHTML = ''; 
    
    try {
        const response = await fetch(`${API_BASE_URL}/conversas/${conversaId}/mensagens`);
        if (!response.ok) {
            throw new Error('Falha ao carregar histórico');
        }
        const mensagens = await response.json();
        
        mensagens.forEach(msg => {
            appendMessage(msg, msg.sou_remetente); 
        });

    } catch (error) {
        console.error("Erro ao carregar histórico:", error);
        appendMessage({ conteudo: "Erro ao carregar histórico. Tente novamente.", data_envio: new Date() }, false);
    }
}


// --- ENVIAR MENSAGEM (SocketIO) ---
function sendMessage() {
    const conteudo = messageInput.value.trim();
    if (conteudo === '' || !currentConversaId) return;

    const messageData = {
        conversa_id: currentConversaId,
        conteudo: conteudo
    };

    socket.emit('send_message', messageData);

    messageInput.value = '';
}


// ---------------------------------------------------------------------------------
// LISTENERS SOCKETIO (Recebimento em Tempo Real)
// ---------------------------------------------------------------------------------

function setupSocketListeners() {
    socket.on('connect', () => {
        console.log('Conectado ao servidor SocketIO.');
        if (currentConversaId) {
            socket.emit('join', { conversa_id: currentConversaId });
        }
    });

    socket.on('receive_message', (data) => {
        // 💡 CORREÇÃO DE TIPAGEM: Garante que os IDs são numbers para comparação
        const incomingConversaId = parseInt(data.conversa_id);
        const activeConversaId = parseInt(currentConversaId);
        
        if (Number.isNaN(activeConversaId) || incomingConversaId !== activeConversaId) { 
             updateThreadPreview(data); 
             return; 
        }
        
        const isSelf = data.remetente_id === CURRENT_USER_ID; 
        appendMessage(data, isSelf);
        
        updateThreadPreview(data); 
    });


    socket.on('error', (data) => {
        console.error("Erro do SocketIO:", data.mensagem);

        // 💡 BLOQUEIO DO FALSO ERRO DE SUCESSO DO BACKEND
        if (data.status === 'SUCESSO' || data.mensagem.includes('Mensagem enviada') || data.status === 'CRIADO') {
            console.warn("Ignorando mensagem de status/sucesso indevidamente recebida no canal de erro.");
            return; 
        }

        appendMessage({ conteudo: `ERRO: ${data.mensagem}`, data_envio: new Date() }, false); 
    });
    
    socket.on('status', (data) => {
        console.log(`Status do servidor: ${data.msg}`);
    });
}


// ---------------------------------------------------------------------------------
// INICIALIZAÇÃO E FLUXO DE NOVA CONVERSA
// ---------------------------------------------------------------------------------

// Função para selecionar o destinatário e preparar para envio
function selectDestinatario(id, nome) {
    destinatarioIdHidden.value = id;
    destinatarioNomeDisplay.textContent = nome;
    areaEnvioInicial.style.display = 'block'; 
    resultadosBusca.innerHTML = ''; 
    inputBusca.value = ''; 
    primeiraMensagemInput.focus();
}

// 🔑 FUNÇÃO CRÍTICA: ABRE O MODAL E PRÉ-SELECIONA O DESTINATÁRIO
function abrirNovoChatModal(destinatarioId, destinatarioNome) {
    // 1. Referência ao contêiner principal do chat
    const chatContainer = document.getElementById('chat-container'); 
    const modalNovoChat = document.getElementById('modal-novo-chat');
    
    // 🔴 CORREÇÃO: Garante que o contêiner principal esteja descolapsado
    if (chatContainer && chatContainer.classList.contains('chat-collapsed')) {
        chatContainer.classList.remove('chat-collapsed');
    }

    // 2. Mostra o modal de nova conversa
    modalNovoChat.style.display = 'block';
    
    // 3. Preenche os campos e abre a área de envio (lógica existente)
    if (destinatarioId && destinatarioNome) {
        selectDestinatario(destinatarioId, destinatarioNome); 
    } else {
        // Caso não tenha ID, foca na busca
        document.getElementById('input-busca').focus();
    }
}


// Lógica de Busca (Debounce)
let searchTimeout;
inputBusca.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
        const query = e.target.value;
        const users = await searchUsers(query);
        renderSearchResults(users);
    }, 300);
});

// Implementação da Lógica de Envio da Nova Conversa (Simplificada)
async function iniciarNovaConversa() {
    const destinatarioId = destinatarioIdHidden.value;
    const conteudo = primeiraMensagemInput.value;
    
    if (!destinatarioId || conteudo.trim() === '') {
        alert('Selecione um destinatário e digite uma mensagem.');
        return;
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
        
        if (response.ok) { 
            // Não usa alert. A mensagem deve ser exibida pelo SocketIO após loadConversas.
            
            modalNovoChat.style.display = 'none';
            primeiraMensagemInput.value = '';
            areaEnvioInicial.style.display = 'none';
            
            // Recarregar lista para ativar a nova conversa
            await loadConversas(); 
            
        } else {
            alert(`Erro ao iniciar conversa: ${resultado.mensagem}`);
        }
    } catch (error) {
        console.error('Erro de rede ao iniciar conversa:', error);
        alert('Erro de conexão com o servidor.');
    }
}

// ---------------------------------------------------------------------------------
// FUNÇÕES DE BUSCA E MODAL
// ---------------------------------------------------------------------------------

// Função para renderizar os resultados de busca
function renderSearchResults(users) {
    resultadosBusca.innerHTML = '';
    
    if (users.length === 0) {
        resultadosBusca.innerHTML = users.length === 0 && inputBusca.value.length >= 3 ? '<p>Nenhum usuário encontrado.</p>' : '';
        return;
    }

    users.forEach(user => {
        const div = document.createElement('div');
        div.classList.add('resultado-usuario');
        div.innerHTML = `
            <img src="/static/images/uploads/${user.imagem}" alt="Avatar" class="avatar-mini" style="width: 30px; height: 30px;">
            <span>${user.nome}</span>
            <button data-id="${user.id}" data-nome="${user.nome}" class="btn-selecionar">Selecionar</button>
        `;
        resultadosBusca.appendChild(div);
    });
    
    document.querySelectorAll('.btn-selecionar').forEach(button => {
        button.addEventListener('click', (e) => {
            const id = e.target.dataset.id;
            const nome = e.target.dataset.nome;
            selectDestinatario(id, nome);
        });
    });
}


// --- FUNÇÃO REVISADA: BUSCA DE USUÁRIOS ---
async function searchUsers(query) {
    if (query.length < 3) { 
        renderSearchResults([]); 
        return [];
    }
    
    const username = query.trim();
    
    try {
        const response = await fetch(`${BASE_PROFILE_URL}${username}`);
        const resultado = await response.json();
        
        if (response.ok && resultado.status === 'SUCESSO') {
            const userData = resultado.data;
            
            if (userData.id !== CURRENT_USER_ID) {
                return [{
                    id: userData.id,
                    nome: userData.nome,
                    imagem: userData.imagem 
                }];
            }
        }
        return []; 
    } catch (error) {
        console.error("Falha na busca de usuário:", error);
        return [];
    }
}


// ---------------------------------------------------------------------------------
// CONFIGURAÇÃO DOS LISTENERS GLOBAIS
// ---------------------------------------------------------------------------------

// Event Listeners para Envio
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { 
        e.preventDefault(); 
        sendMessage();
    }
});

// Event Listeners Finais (Modal)
btnNovoChat.addEventListener('click', () => { 
    abrirNovoChatModal(null, null); // Chama a função, sem pré-seleção
});

btnFecharModal.addEventListener('click', () => { modalNovoChat.style.display = 'none'; });
btnEnviarPrimeiraMsg.addEventListener('click', iniciarNovaConversa);


// --- INICIALIZAÇÃO ---
document.addEventListener('DOMContentLoaded', () => {
    loadConversas();
    setupSocketListeners();
});