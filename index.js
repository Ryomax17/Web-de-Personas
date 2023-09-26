function alternarTema() {

}
async function getPeople() {
  const response = await fetch(
    `https://my-json-server.typicode.com/maximiliano836/entrega13/personas`
  );
  const peoples = await response.json();
  console.log(peoples);

  const people = document.getElementById("people");
  people.innerHTML = "";
  peoples.forEach((persona) => {
    const listItem = document.createElement("li");
    listItem.textContent = `Nombre: ${persona.name}, Dirección: ${persona.country}, Teléfono: ${persona.phone}`;
    people.appendChild(listItem);
  });
}

function toggleMode() {
    const body = document.body;
    body.classList.toggle('day-mode');
    body.classList.toggle('night-mode');
}

document.addEventListener("DOMContentLoaded", function () {
  
    getPeople();
  });

