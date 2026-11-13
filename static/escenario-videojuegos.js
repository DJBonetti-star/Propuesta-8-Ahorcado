const MAX_ERRORES = 8;
const escenario = document.getElementById("escenario");
const mensaje = document.getElementById("mensaje");
const pips = document.getElementById("pips");
const vidasNum = document.getElementById("vidas-num");
const hp = document.getElementById("hp");
const errores = Number(escenario.style.getPropertyValue("--errores")) || 0;
const vidaPerdida = document.body.dataset.vidaPerdida === "1";
const ganado = document.body.dataset.ganado === "1";
const perdio = document.body.dataset.perdio === "1";
const estadoPerdido = perdio || errores >= MAX_ERRORES;
const estadoGanado = ganado && !estadoPerdido;

for (let i = 0; i < MAX_ERRORES; i++) {
    const pip = document.createElement("span");
    pip.className = "pip";
    pips.appendChild(pip);
}

escenario.style.setProperty("--errores", Math.min(errores, MAX_ERRORES - 1));
escenario.classList.toggle("perdio", estadoPerdido);
escenario.classList.toggle("gano", estadoGanado);
escenario.classList.toggle("recibio-dano", vidaPerdida);

[...pips.children].forEach((pip, index) => {
    pip.classList.toggle("perdida", index >= MAX_ERRORES - errores);
});

const vidasRestantes = Math.max(0, MAX_ERRORES - errores);
vidasNum.textContent = vidasRestantes;
hp.textContent = vidasRestantes;

if (estadoGanado) {
    mensaje.textContent = "¡Nivel superado!";
    mensaje.classList.add("ganaste");
} else if (estadoPerdido) {
    mensaje.textContent = "GAME OVER · Inténtalo otra vez";
    mensaje.classList.add("perdiste");
}
