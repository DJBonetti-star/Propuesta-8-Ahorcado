const MAX_ERRORES = 8;
const escenario = document.getElementById("escenario");
const mensaje = document.getElementById("mensaje");
const pips = document.getElementById("pips");
const vidasNum = document.getElementById("vidas-num");
const expresiones = document.querySelectorAll("#monigote img");
const pantallas = document.querySelectorAll("#pantallas img");
const errores = Number(escenario.style.getPropertyValue("--errores")) || 0;
const vidaPerdida = document.body.dataset.vidaPerdida === "1";
const ganado = document.body.dataset.ganado === "1";
const perdio = document.body.dataset.perdio === "1";
const estadoPerdido = perdio || errores >= MAX_ERRORES;
const estadoGanado = ganado && !estadoPerdido;
const erroresActuales = Math.min(errores, MAX_ERRORES);

for (let i = 0; i < MAX_ERRORES; i++) {
    const pip = document.createElement("span");
    pip.className = "pip";
    pips.appendChild(pip);
}

escenario.style.setProperty("--errores", Math.min(erroresActuales, MAX_ERRORES - 1));
escenario.style.setProperty(
    "--duracion-temblor",
    `${Math.max(.5, 1.2 - Math.min(erroresActuales, MAX_ERRORES - 1) * .1)}s`,
);
escenario.classList.toggle("perdio", estadoPerdido);
escenario.classList.toggle("gano", estadoGanado);
escenario.classList.toggle("recibio-dano", vidaPerdida);

const expresion = estadoGanado ? "1" : estadoPerdido
    ? "perder"
    : ["1", "1", "2", "2", "3", "3", "4", "4", "perder"][erroresActuales];
expresiones.forEach(img => img.classList.toggle("activa", img.dataset.exp === expresion));

const pantalla = ["5", "5", "4", "4", "3", "3", "2", "1", "1"][erroresActuales];
pantallas.forEach(img => img.classList.toggle("activa", img.dataset.p === pantalla));

[...pips.children].forEach((pip, index) => {
    pip.classList.toggle("perdida", index >= MAX_ERRORES - erroresActuales);
});

const vidasRestantes = Math.max(0, MAX_ERRORES - erroresActuales);
const temblor = Math.min(erroresActuales, MAX_ERRORES - 1) * .12;
const anguloTemblor = Math.min(erroresActuales, MAX_ERRORES - 1) * .9;
escenario.style.setProperty("--temblor-x", `${temblor}%`);
escenario.style.setProperty("--temblor-x-negativo", `${-temblor}%`);
escenario.style.setProperty("--temblor-y", `${temblor * 5 / 6}%`);
escenario.style.setProperty("--temblor-y-negativo", `${-temblor * 5 / 6}%`);
escenario.style.setProperty("--temblor-angulo", `${anguloTemblor}deg`);
escenario.style.setProperty("--temblor-angulo-negativo", `${-anguloTemblor}deg`);
vidasNum.textContent = vidasRestantes;

if (estadoGanado) {
    mensaje.textContent = "¡Ganaste!";
    mensaje.classList.add("ganaste");
} else if (estadoPerdido) {
    mensaje.textContent = "El teléfono explotó. Perdiste";
    mensaje.classList.add("perdiste");
} else if (vidaPerdida) {
    mensaje.textContent = "¡Cuidado con el teléfono!";
} else {
    mensaje.textContent = "Temática: aplicaciones";
}
