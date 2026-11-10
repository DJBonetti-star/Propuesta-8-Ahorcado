const MAX_ERRORES = 8;
const escenario = document.getElementById("escenario");
const mensaje   = document.getElementById("mensaje");
const pips      = document.getElementById("pips");
const vidasNum  = document.getElementById("vidas-num");
const grietas   = document.querySelectorAll("#grietas .grieta");
const expresiones = document.querySelectorAll("#monigote img");
const errores = Number(escenario.style.getPropertyValue("--errores")) || 0;
const ganado = document.body.dataset.ganado === "1";
const perdio = document.body.dataset.perdio === "1";
const GRIETA_POR_ERROR = [0, 1, 2, 3, 4, 5, 6, 7];
const EXPRESIONES = ["1", "1", "1", "2", "2", "2", "3", "3", "final"];

for (let i = 0; i < MAX_ERRORES; i++) {
  const p = document.createElement("span");
  p.className = "pip";
  pips.appendChild(p);
}

function mostrarExpresion(nombre) {
  expresiones.forEach(img => img.classList.toggle("activa", img.dataset.exp === nombre));
}

function actualizar() {
  const estadoPerdido = perdio || errores >= MAX_ERRORES;
  const estadoGanado = ganado && !estadoPerdido;

  escenario.style.setProperty("--errores", errores);
  escenario.classList.toggle("perdio", estadoPerdido);

  const expresionActiva = estadoGanado ? "ganar" : estadoPerdido ? "final" : EXPRESIONES[errores];
  mostrarExpresion(expresionActiva);

  const actual = estadoPerdido ? 0 : GRIETA_POR_ERROR[errores];
  grietas.forEach(g => g.classList.toggle("activa", Number(g.dataset.g) === actual));

  [...pips.children].forEach((p, i) => p.classList.toggle("perdida", i >= MAX_ERRORES - errores));
  vidasNum.textContent = Math.max(0, MAX_ERRORES - errores);

  if (estadoGanado) {
    mensaje.textContent = "¡Ganaste!";
  } else if (estadoPerdido) {
    mensaje.textContent = "La rama se rompió. Perdiste";
  } else {
    mensaje.textContent = "Temática: comida";
  }

  mensaje.classList.toggle("perdiste", estadoPerdido);
  mensaje.classList.toggle("ganaste", estadoGanado);
}

actualizar();
