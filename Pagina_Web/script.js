// Función para mostrar vista previa de imagen seleccionada
document.getElementById("uploadImage").addEventListener("change", previewImage);

function previewImage(event) {
  const file = event.target.files[0];
  const imagePreview = document.getElementById("imagePreview");

  if (file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      imagePreview.src = e.target.result;
      imagePreview.style.display = "block";
    };
    reader.readAsDataURL(file);
  } else {
    imagePreview.style.display = "none";
    imagePreview.src = "";
  }
}

// Función para la subida de imagen (simulada)
function uploadImage() {
  const fileInput = document.getElementById("uploadImage");
  const file = fileInput.files[0];

  if (!file) {
    alert("Por favor, seleccione una imagen.");
    return;
  }

  const formData = new FormData();
  formData.append("image", file);

  fetch("https://tu-backend.com/upload", {
    method: "POST",
    body: formData
  })
  .then(response => response.json())
  .then(data => alert("Imagen subida correctamente"))
  .catch(error => alert("Imgen no subida correctamente"));
}

// Función para mostrar el formulario seleccionado
function showForm(formNumber) {
  const forms = document.querySelectorAll(".form");

  // Oculta todos los formularios
  forms.forEach((form) => {
    form.style.display = "none";
  });

  // Muestra el formulario seleccionado
  const selectedForm = document.getElementById(`form${formNumber}`);
  if (selectedForm) {
    selectedForm.style.display = "block";
  } else {
    console.log("Formulario no encontrado");
  }
}

// Función para activar o desactivar el botón de envío del formulario
function validateForm(formId) {
  const form = document.getElementById(formId);
  const submitButton = form.querySelector("button[type='button']");
  const isValid = Array.from(form.querySelectorAll("input, select")).every(input => {
    return input.type === "radio" ? form.querySelector(`input[name='${input.name}']:checked`) : input.value;
  });

  submitButton.disabled = !isValid;

  if (isValid) {
    const errorMessage = document.querySelector("#"+formId+" .error-message");
    errorMessage.style.display = "none"; // Oculta el mensaje de error si el formulario es válido
  }
}

// // Función para validar el formulario y mostrar mensaje de error o enviar
// function validateAndSubmitForm(formNumber) {
//   const form = document.getElementById(`form${formNumber}`);
//   const isValid = Array.from(form.querySelectorAll("input, select")).every(input => {
//     return input.type === "radio" ? form.querySelector(`input[name='${input.name}']:checked`) : input.value;
//   });

//   const errorMessage = document.getElementById("error-message");
//   if (isValid) {
//     errorMessage.style.display = "none"; // Oculta el mensaje de error
//     showOverlay(); // Muestra el overlay de éxito
//   } else {
//     errorMessage.style.display = "block"; // Muestra el mensaje de error
//     errorMessage.innerText = "Por favor, complete todos los campos obligatorios.";
//   }
// }


// // Función para validar el formulario y mostrar mensaje de error o enviar DEL FORMULARIO 2
// function validateAndSubmitForm(formNumber) {
//   const form = document.getElementById(`form${formNumber}`);
//   const isValid = Array.from(form.querySelectorAll("input, select")).every(input => {
//     return input.type === "radio" ? form.querySelector(`input[name='${input.name}']:checked`) : input.value;
//   });

//   const errorMessage = document.getElementById("error-message2");
//   if (isValid) {
//     errorMessage.style.display = "none"; // Oculta el mensaje de error
//     showOverlay(); // Muestra el overlay de éxito
//   } else {
//     errorMessage.style.display = "block"; // Muestra el mensaje de error
//     errorMessage.innerText = "Por favor, complete todos los campos obligatorios.";
//   }
// }

// // Función para validar el formulario y mostrar mensaje de error o enviar DEL FORMULARIO 3
// function validateAndSubmitForm(formNumber) {
//   const form = document.getElementById(`form${formNumber}`);
//   const isValid = Array.from(form.querySelectorAll("input, select")).every(input => {
//     return input.type === "radio" ? form.querySelector(`input[name='${input.name}']:checked`) : input.value;
//   });

//   const errorMessage = document.getElementById("error-message3");
//   if (isValid) {
//     errorMessage.style.display = "none"; // Oculta el mensaje de error
//     showOverlay(); // Muestra el overlay de éxito
//   } else {
//     errorMessage.style.display = "block"; // Muestra el mensaje de error
//     errorMessage.innerText = "Por favor, complete todos los campos obligatorios.";
//   }
// }

// Función para validar el formulario y mostrar mensaje de error o enviar He unificado los tres errores en este código, dejo los de arriba por si quereis estudiarlo
function validateAndSubmitForm(formNumber) {
  // Selecciona el formulario correspondiente
  const form = document.getElementById(`form${formNumber}`);
  const errorMessage = document.getElementById(`error-message${formNumber}`);

  // Verifica si el formulario y el mensaje de error existen
  if (!form) {
    console.error(`No se encontró el formulario con el id form${formNumber}`);
    return;
  }
  if (!errorMessage) {
    console.error(`No se encontró el mensaje de error con el id error-message${formNumber}`);
    return;
  }

  // Verifica si todos los campos del formulario son válidos
  const isValid = Array.from(form.querySelectorAll("input, select")).every(input => {
    return input.type === "radio" ? form.querySelector(`input[name='${input.name}']:checked`) : input.value.trim() !== "";
  });

  if (isValid) {
    errorMessage.style.display = "none"; // Oculta el mensaje de error si es válido
    showOverlay(); // Muestra el overlay de éxito
  } else {
    errorMessage.style.display = "block"; // Muestra el mensaje de error si no es válido
    errorMessage.innerText = "Por favor, complete todos los campos obligatorios.";
  }
}






// Función para mostrar el overlay
function showOverlay() {
  const overlay = document.getElementById("overlay");
  if (overlay) {
    overlay.style.display = "flex";
  } else {
    console.error("Overlay no encontrado");
  }
}

// Función para cerrar el overlay
function closeOverlay() {
  const overlay = document.getElementById("overlay");
  if (overlay) {
    overlay.style.display = "none";
  } else {
    console.error("Overlay no encontrado");
  }
}

// Mostrar el primer formulario al cargar la página
document.addEventListener("DOMContentLoaded", () => {
  showForm(1); // Mostrar Formulario 1 por defecto
});
