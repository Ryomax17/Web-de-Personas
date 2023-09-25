document.addEventListener("DOMContentLoaded", function() {


async function getPeople(id){
    const response = await fetch(``)
    const people = await response.json();
    console.log(people);
    return people;
}
});