document.addEventListener('DOMContentLoaded', function() {
    const servicoForm = document.getElementById('servico-form');
    const servicoResultado = document.getElementById('servico-resultado');
    const editarBtn = document.getElementById('editar-btn');
    const precoInput = document.getElementById('preco');
    const formaRadios = document.querySelectorAll('input[name="forma"]');
    const detalhesTextarea = document.getElementById('detalhes');
    const disponibilidadeTextarea = document.getElementById('disponibilidade');
    const formatoTextarea = document.getElementById('formato');
    const resultadoForma = document.getElementById('resultado-forma');
    const resultadoPreco = document.getElementById('resultado-preco');
    const resultadoDetalhes = document.getElementById('resultado-detalhes');
    const resultadoDisponibilidade = document.getElementById('resultado-disponibilidade');
    const resultadoFormato = document.getElementById('resultado-formato');
    
    precoInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        value = (value / 100).toFixed(2) + '';
        value = value.replace('.', ',');
        value = value.replace(/(\d)(\d{3})(\d{3}),/g, '$1.$2.$3,');
        value = value.replace(/(\d)(\d{3}),/g, '$1.$2,');
        e.target.value = 'R$ ' + value;
    });
    
    servicoForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const preco = precoInput.value;
        let formaSelecionada = '';
        formaRadios.forEach(radio => {
            if (radio.checked) {
                formaSelecionada = radio.value;
            }
        });
        const detalhes = detalhesTextarea.value;
        const disponibilidade = disponibilidadeTextarea.value;
        const formato = formatoTextarea.value;
        resultadoForma.textContent = formaSelecionada.charAt(0).toUpperCase() + formaSelecionada.slice(1);
        resultadoPreco.value = preco;
        resultadoDetalhes.textContent = detalhes || 'Não informado';
        resultadoDisponibilidade.textContent = disponibilidade || 'Não informado';
        resultadoFormato.textContent = formato || 'Não informado';
        
        servicoForm.classList.add('hidden');
        servicoResultado.classList.remove('hidden');
    });
    
    editarBtn.addEventListener('click', function() {
        servicoResultado.classList.add('hidden');
        servicoForm.classList.remove('hidden');
    });
});