function toggleEditMode() {
    const editCheckbox = document.getElementById('edit-checkbox');
    const formControls = document.querySelectorAll('.form-control');
    const saveButton = document.querySelector('.save-button');
    const editButton = document.querySelector('.edit-button');
    const profilePictureButton = document.querySelector('.profile-picture-button');
    const profilePictureInput = document.getElementById('id_profile_picture');
    const removePictureButton = document.querySelector('.btn-danger');
    const locadorCheckbox = document.getElementById('id_is_locador');
    const mfaCheckbox = document.getElementById('id_is_2fa_enabled');

    if (editCheckbox.checked) {
        editCheckbox.checked = false;
        formControls.forEach(control => control.setAttribute('readonly', true));
        profilePictureButton.setAttribute('disabled', true);
        profilePictureInput.setAttribute('disabled', true);
        saveButton.style.display = 'none';
        editButton.style.display = 'block';
        if (removePictureButton) removePictureButton.setAttribute('disabled', true);
        locadorCheckbox.setAttribute('disabled', true);
        mfaCheckbox.setAttribute('disabled', true);
    } else {
        editCheckbox.checked = true;
        formControls.forEach(control => control.removeAttribute('readonly'));
        profilePictureButton.removeAttribute('disabled');
        profilePictureInput.removeAttribute('disabled');
        saveButton.style.display = 'block';
        editButton.style.display = 'none';
        if (removePictureButton) removePictureButton.removeAttribute('disabled');
        locadorCheckbox.removeAttribute('disabled');
        mfaCheckbox.removeAttribute('disabled');
    }
}
document.getElementById('id_profile_picture').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('profile-picture').src = e.target.result; 
        };
        reader.readAsDataURL(file); 
    }
});

document.getElementById('id_phone_number').addEventListener('input', function(event) {
    let value = event.target.value.replace(/\D/g, '');

    if (value.length > 11) {
        value = value.slice(0, 11); 
    }

    let formattedValue = '';


    if (value.length > 6) {
        formattedValue = `(${value.slice(0, 2)}) ${value.slice(2, 7)}-${value.slice(7)}`;
    } else if (value.length > 2) {
        formattedValue = `(${value.slice(0, 2)}) ${value.slice(2)}`;
    } else {
        formattedValue = value;
    }


    event.target.value = formattedValue;
});


document.querySelector('form').addEventListener('submit', function(event) {
    let hasErrors = false;


    document.querySelectorAll('.form-control').forEach(control => {
        if (control.hasAttribute('required') && !control.value) {
            hasErrors = true;
            const errorMessage = document.createElement('div');
            errorMessage.className = 'text-danger'; 
            errorMessage.innerText = `O campo ${control.previousElementSibling.innerText} é obrigatório.`;
            control.parentNode.appendChild(errorMessage); 
            control.classList.add('is-invalid'); 
        } else {
            control.classList.remove('is-invalid'); 
        }
    });

    if (hasErrors) {
        event.preventDefault();
    }
});
