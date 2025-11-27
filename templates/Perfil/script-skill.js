console.log("JS funcionando!");


document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("tagInput");
    const addBtn = document.getElementById("addTagBtn");
    const skillsList = document.getElementById("skillsList");

    function addTag() {
        const text = input.value.trim();
        if (text === "") return;
        const tag = document.createElement("span");
        tag.classList.add("tag");
        tag.innerHTML = `${text} <button class="remove-btn">&times;</button>`;

        skillsList.appendChild(tag);

        input.value = "";
    }

    addBtn.addEventListener("click", addTag);

    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            addTag();
        }
    });

    document.addEventListener("click", (e) => {
        if (e.target.classList.contains("remove-btn")) {
            e.target.parentElement.remove();
        }
    });
});
