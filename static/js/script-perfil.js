
const btnConversaPerfil = document.getElementById('btn-conversa-perfil');
const destinatarioPerfilId = document.getElementById('destinatario-perfil-id');
const destinatarioPerfilNome = document.getElementById('destinatario-perfil-nome');


if (btnConversaPerfil) {
    btnConversaPerfil.addEventListener('click', () => {
        const id = destinatarioPerfilId.value;
        const nome = destinatarioPerfilNome.value;
        
        if (!id) {
            alert("Erro: ID do destinatário não encontrado.");
            return;
        }
        
        // ⚠️ CHAMADA FINAL: Abre o modal de nova conversa no chat principal.
        // E passa os dados para que o chat principal possa pular a busca.
        abrirNovoChatModal(id, nome);
    });
}