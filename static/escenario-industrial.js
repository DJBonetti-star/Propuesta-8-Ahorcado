const MAX_ERRORES = 8;
const escenario = document.getElementById("escenario");
const mensaje = document.getElementById("mensaje");
const pips = document.getElementById("pips");
const vidasNum = document.getElementById("vidas-num");
const piezas = document.querySelectorAll(".industrial-stage .pieza");
const errores = Number(escenario.style.getPropertyValue("--errores")) || 0;
const ganado = document.body.dataset.ganado === "1";
const perdio = document.body.dataset.perdio === "1";

for (let i = 0; i < MAX_ERRORES; i++) {
    const pip = document.createElement("span");
    pip.className = "pip";
    pips.appendChild(pip);
}

const estadoPerdido = perdio || errores >= MAX_ERRORES;
const estadoGanado = ganado && !estadoPerdido;

piezas.forEach(pieza => {
    pieza.classList.toggle("fuera", Number(pieza.dataset.n) <= errores);
});
escenario.classList.toggle("gano", estadoGanado);
escenario.classList.toggle("perdio", estadoPerdido);

[...pips.children].forEach((pip, index) => {
    pip.classList.toggle("perdida", index >= MAX_ERRORES - errores);
});
vidasNum.textContent = Math.max(0, MAX_ERRORES - errores);

if (estadoGanado) {
    mensaje.textContent = "¡Salvaste la insignia!";
} else if (estadoPerdido) {
    mensaje.textContent = "Perdiste la insignia";
}

mensaje.classList.toggle("perdiste", estadoPerdido);
mensaje.classList.toggle("ganaste", estadoGanado);
