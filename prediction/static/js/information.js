const circle = document.getElementById("circle");
const text = document.getElementById("breathText");
const btn = document.getElementById("startBtn");

btn.onclick = () => {

let count = 0;

btn.disabled = true;

const interval = setInterval(() => {

if(count % 2 === 0){

circle.classList.add("expand");
text.innerHTML = "Breathe In";

}
else{

circle.classList.remove("expand");
text.innerHTML = "Breathe Out";

}

count++;

if(count === 10){

clearInterval(interval);

text.innerHTML = "Great Job! 😊";

btn.disabled = false;

}

},3000);

};