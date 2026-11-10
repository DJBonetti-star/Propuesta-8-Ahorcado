const MAX_ERRORES = 8;
const escenario   = document.getElementById("escenario");
const vaiven      = document.getElementById("vaiven");
const mensaje     = document.getElementById("mensaje");
const pips        = document.getElementById("pips");
const vidasNum    = document.getElementById("vidas-num");
const expresiones = document.querySelectorAll("#monigote img");
const errores = Number(escenario.style.getPropertyValue("--errores")) || 0;
const ganado = document.body.dataset.ganado === "1";
const perdio = document.body.dataset.perdio === "1";
const EXPRESIONES = ["1", "1", "1", "2", "2", "2", "3", "3", "final"];

for (let i = 0; i < MAX_ERRORES; i++) {
  const p = document.createElement("span");
  p.className = "pip";
  pips.appendChild(p);
}

function mostrarExpresion(nombre) {
  expresiones.forEach(img => img.classList.toggle("activa", img.dataset.exp === nombre));
}

function vibrarPochoclos() {
  vaiven.classList.remove("subiendo");
  void vaiven.offsetWidth;
  vaiven.classList.add("subiendo");
}

if (vaiven) {
  vaiven.addEventListener("animationend", () => vaiven.classList.remove("subiendo"));
}

function actualizar() {
  const estadoPerdido = perdio || errores >= MAX_ERRORES;
  const estadoGanado = ganado && !estadoPerdido;

  escenario.style.setProperty("--errores", errores);
  escenario.classList.toggle("perdio", estadoPerdido);

  const expresionActiva = estadoGanado ? "ganar" : estadoPerdido ? "final" : EXPRESIONES[errores];
  mostrarExpresion(expresionActiva);

  [...pips.children].forEach((p, i) => p.classList.toggle("perdida", i >= MAX_ERRORES - errores));
  vidasNum.textContent = Math.max(0, MAX_ERRORES - errores);

  if (estadoGanado) {
    mensaje.textContent = "¡Ganaste!";
  } else if (estadoPerdido) {
    mensaje.textContent = "Los pochoclos te cubrieron. Perdiste";
  } else {
    mensaje.textContent = "Temática: películas";
  }

  mensaje.classList.toggle("perdiste", estadoPerdido);
  mensaje.classList.toggle("ganaste", estadoGanado);

  if (!estadoGanado && !estadoPerdido) {
    vibrarPochoclos();
  }
}

actualizar();
