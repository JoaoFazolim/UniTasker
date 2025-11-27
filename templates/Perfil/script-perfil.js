document.addEventListener("DOMContentLoaded", () => {

    const fields = {
        name: {
            view: document.getElementById("profileName"),
            edit: document.getElementById("editName")
        },
        job: {
            view: document.getElementById("profileJob"),
            edit: document.getElementById("editJob")
        },
        location: {
            view: document.getElementById("profileLocation"),
            edit: document.getElementById("editLocation")
        },
        birthday: {
            view: document.getElementById("profileBirthday"),
            edit: document.getElementById("editBirthday")
        }
    };

    const editBtn = document.getElementById("editProfileBtn");
    const saveBtn = document.getElementById("saveProfileBtn");

    editBtn.addEventListener("click", () => {
        editBtn.style.display = "none";
        saveBtn.style.display = "inline-block";

        Object.values(fields).forEach(f => {
            f.edit.value = f.view.textContent.trim();
            f.view.style.display = "none";
            f.edit.style.display = "block";
        });
    });

    saveBtn.addEventListener("click", () => {
        editBtn.style.display = "inline-block";
        saveBtn.style.display = "none";

        Object.values(fields).forEach(f => {
            f.view.textContent = f.edit.value.trim();
            f.view.style.display = "block";
            f.edit.style.display = "none";
        });
    });

});
