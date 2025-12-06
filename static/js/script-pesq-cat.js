const categorias = [
    "Aulas e Monitoria",
    "Tecnologia e Programação",
    "Design e Multimídia",
    "Trabalhos Acadêmicos e ABNT",
    "Assistência Técnica",
    "Tradução e Redação",
    "Marketing e Negócios",
    "Saúde e Estética",
    "Outros"
];


const inicioBtn = document.getElementById('inicio');
const categoriasBtn = document.getElementById('categorias');
const dropdownMenu = document.getElementById('dropdown-menu');
const procurarBtn = document.getElementById('procurar');
const searchWrapper = document.getElementById('search-wrapper');
const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');

let idCat = 1

categorias.forEach(categoria => {
    const link = document.createElement('a');
    link.href = `/servicos?categoria=${idCat}`;
    link.textContent = categoria;
    link.onclick = (e) => {
        dropdownMenu.classList.remove('show');
    };
    dropdownMenu.appendChild(link);
    idCat ++
});

categoriasBtn.addEventListener('click', (e) => {
    e.preventDefault();
    dropdownMenu.classList.toggle('show');
    searchWrapper.classList.remove('show');
});

procurarBtn.addEventListener('click', (e) => {
    e.preventDefault();
    searchWrapper.classList.toggle('show');
    dropdownMenu.classList.remove('show');
    if (searchWrapper.classList.contains('show')) {
        setTimeout(() => searchInput.focus(), 70);
    }
});

document.addEventListener('click', (e) => {
    if (!e.target.closest('.dropdown') && !e.target.closest('#categorias')) {
        dropdownMenu.classList.remove('show');
    }
    if (!e.target.closest('.search-container') && !e.target.closest('#procurar')) {
        searchWrapper.classList.remove('show');
    }
});

searchInput.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase().trim();

    if (searchTerm === '') {
        searchResults.innerHTML = '';
        return;
    }

    const filtered = cursos.filter(curso =>
        curso.toLowerCase().includes(searchTerm)
    );

    searchResults.innerHTML = '';

    if (filtered.length === 0) {
        searchResults.innerHTML = '<div class="no-results">Nenhum curso encontrado. </div>';
    } else {
        filtered.forEach(curso => {
            const link = document.createElement('a');
            link.href = '#';

            const regex = new RegExp(`(${searchTerm})`, 'gi');
            link.innerHTML = curso.replace(regex, '<span class="highlight">$1</span>');

            link.onclick = (e) => {
                e.preventDefault();
                alert(`Você selecionou: ${curso}`);
                searchWrapper.classList.remove('show');
                searchInput.value = '';
                searchResults.innerHTML = '';
            };
            searchResults.appendChild(link);
        });
    }
});

inicioBtn.addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
});