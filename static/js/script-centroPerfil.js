document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. RENDERIZAÇÃO INICIAL DO MARKDOWN ---
    renderizarBio();

    // --- 2. LÓGICA DE EDIÇÃO DA BIO ---
    const btnEditarBio = document.getElementById('btnEditarBio');
    const btnCancelarBio = document.getElementById('btnCancelarBio');
    const btnSalvarBio = document.getElementById('btnSalvarBio');
    const areaVisualizacao = document.getElementById('bio-renderizada');
    const areaEdicao = document.getElementById('editBioArea');
    const textareaBio = document.getElementById('editBio');

    if (btnEditarBio) {
        btnEditarBio.addEventListener('click', function() {
            // Esconde visualização, mostra edição
            areaVisualizacao.style.display = 'none';
            areaEdicao.style.display = 'block';
            btnEditarBio.style.display = 'none';
        });
    }

    if (btnCancelarBio) {
        btnCancelarBio.addEventListener('click', function() {
            // Cancela: volta ao estado anterior
            areaVisualizacao.style.display = 'block';
            areaEdicao.style.display = 'none';
            btnEditarBio.style.display = 'inline-block';
            // Reseta o texto para o original
            textareaBio.value = areaVisualizacao.getAttribute('data-raw');
        });
    }

    if (btnSalvarBio) {
        btnSalvarBio.addEventListener('click', function() {
            const novaBio = textareaBio.value;

            // Envia para o backend
            fetch('/perfil/editar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ descricaoMD: novaBio })
            })
            .then(response => response.json())
            .then(result => {
                if (result.status === 'SUCESSO') {
                    // Atualiza o atributo data-raw
                    areaVisualizacao.setAttribute('data-raw', novaBio);
                    
                    // Re-renderiza o Markdown
                    renderizarBio();

                    // Volta para o modo de visualização
                    areaVisualizacao.style.display = 'block';
                    areaEdicao.style.display = 'none';
                    btnEditarBio.style.display = 'inline-block';

                    // Feedback visual (Toast se você tiver implementado)
                    // ou um alerta simples se preferir
                    // alert('Bio atualizada!');
                } else {
                    alert('Erro ao salvar: ' + result.mensagem);
                }
            })
            .catch(error => console.error('Erro:', error));
        });
    }
});

// --- FUNÇÃO DE RENDERIZAR MARKDOWN (Reutilizável) ---
function renderizarBio() {
    const bioElement = document.getElementById('bio-renderizada');
    if (bioElement && typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
        const rawMarkdown = bioElement.getAttribute('data-raw') || "Este usuário ainda não escreveu uma bio.";
        
        // Converte e Sanitiza (Segurança contra XSS)
        const htmlSeguro = DOMPurify.sanitize(marked.parse(rawMarkdown));
        bioElement.innerHTML = htmlSeguro;
    }
}

// --- 3. LÓGICA DE ABAS (Global) ---
// Essa função precisa ser global para ser chamada pelo onclick no HTML
function trocarComponente(idComponente) {
    // 1. Esconde todos os conteúdos
    const componentes = document.querySelectorAll('.componente-view');
    componentes.forEach(comp => comp.style.display = 'none');

    // 2. Mostra o selecionado
    const alvo = document.getElementById(idComponente);
    if (alvo) {
        alvo.style.display = 'block';
    }

    // 3. (Opcional) Atualiza estilo dos botões (ativo/inativo)
    // Para isso funcionar, os botões precisam ter classes ou IDs específicos
    // Se quiser implementar: adicione a classe 'btn-tab' nos botões do HTML
    const botoes = document.querySelectorAll('.btn-tab');
    botoes.forEach(btn => {
        // Lógica simples: se o onclick do botão tem o idComponente, ele fica "ativo"
        if (btn.getAttribute('onclick').includes(idComponente)) {
            btn.style.backgroundColor = '#0a2439'; // Cor ativa
            btn.style.color = 'white';
        } else {
            btn.style.backgroundColor = 'white'; // Cor inativa
            btn.style.color = '#333';
        }
    });
}