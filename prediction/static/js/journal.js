const stress = document.querySelector("input[name='stress']");
const stressValue = document.getElementById("stressValue");

stress.addEventListener("input", function () {
    stressValue.innerText = this.value;
});


const energy = document.querySelector("input[name='energy']");
const energyValue = document.getElementById("energyValue");

energy.addEventListener("input", function () {
    energyValue.innerText = this.value;
});