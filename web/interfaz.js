const $ = id => document.getElementById(id);
const formulario = $("formulario");
const botonComparar = $("comparar");
const botonEjecutar = formulario.querySelector('button[type="submit"]');

function parametros(tipo, con_mutex) {
  const cocineros = Number($("cocineros").value);
  const stock = Number($("stock").value);
  if (!Number.isInteger(cocineros) || cocineros < 2 || cocineros > 6 ||
      !Number.isInteger(stock) || stock < 0 || stock > 10) {
    throw Error("Ingresa de 2 a 6 cocineros y un stock de 0 a 10.");
  }
  return {tipo, con_mutex, cocineros, stock};
}

async function pedir(datos) {
  const respuesta = await fetch("/api/simular", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body:JSON.stringify(datos)
  });
  const resultado = await respuesta.json();
  if (!respuesta.ok) throw Error(resultado.error || "No se pudo simular.");
  return resultado;
}

function celda(fila, contenido) {
  const td = document.createElement("td");
  if (contenido instanceof Node) td.append(contenido); else td.textContent = String(contenido);
  fila.append(td);
}

function mostrar(r) {
  $("inicial").textContent = r.stock_inicial;
  $("reservas").textContent = r.reservas;
  $("final").textContent = r.stock_final;
  const estado = $("estado");
  estado.className = "estado " + (r.conflicto ? "error" : "ok");
  estado.textContent = r.conflicto ? "Condición de carrera detectada" : "Sin inconsistencia en el inventario";
  $("detalle").textContent = (r.tipo === "basico" ? "Pollo" : "Lasaña preparada") +
    " · " + (r.con_mutex ? "Con mutex" : "Sin mutex");
  $("explicacion").textContent = r.mensaje + (r.conflicto ?
    " Dos o más hilos pueden haber usado la misma cantidad anterior." :
    " Cada reserva confirmada coincide con una unidad descontada.");
  const tbody = $("movimientos");
  tbody.replaceChildren();
  r.movimientos.forEach(m => {
    const fila = document.createElement("tr");
    celda(fila, m.hilo);
    celda(fila, m.operacion);
    celda(fila, m.antes);
    const chip = document.createElement("span");
    chip.className = "chip " + (m.confirmada ? "ok" : "error");
    chip.textContent = m.resultado;
    celda(fila, chip);
    celda(fila, m.despues);
    tbody.append(fila);
  });
}

function cambiarCarga(cargando) {
  botonEjecutar.disabled = cargando;
  botonComparar.disabled = cargando;
}

formulario.addEventListener("submit", async e => {
  e.preventDefault(); cambiarCarga(true);
  try {
    const r = await pedir(parametros($("tipo").value, $("mutex").value === "true"));
    mostrar(r);
  } catch (error) {
    $("estado").className = "estado error";
    $("estado").textContent = error.message;
  } finally { cambiarCarga(false); }
});

botonComparar.addEventListener("click", async () => {
  cambiarCarga(true);
  const opciones = [
    ["basico",false],["basico",true],["complejo",false],["complejo",true]
  ];
  try {
    const resultados = [];
    for (const [tipo, mutex] of opciones) {
      resultados.push(await pedir(parametros(tipo,mutex)));
    }
    const tarjetas = $("tarjetas");
    tarjetas.replaceChildren();
    for (const r of resultados) {
      const tarjeta = document.createElement("article");
      tarjeta.className = "tarjeta";
      const titulo = document.createElement("h3");
      titulo.textContent = (r.tipo === "basico" ? "Básico" : "Complejo") +
        (r.con_mutex ? " · con mutex" : " · sin mutex");
      const cifra = document.createElement("strong");
      cifra.textContent = r.reservas + " reservas";
      const texto = document.createElement("p");
      texto.textContent = "Stock: " + r.stock_inicial + " → " + r.stock_final;
      const mensaje = document.createElement("span");
      mensaje.className = "chip " + (r.conflicto ? "error" : "ok");
      mensaje.textContent = r.conflicto ? "Condición de carrera" : "Consistente";
      tarjeta.append(titulo,cifra,texto,mensaje);
      tarjetas.append(tarjeta);
    }
    $("comparacion").hidden = false;
    mostrar(resultados.find(r => r.tipo === $("tipo").value &&
      r.con_mutex === ($("mutex").value === "true")) || resultados[0]);
  } catch(error) {
    $("estado").className = "estado error";
    $("estado").textContent = error.message;
  } finally { cambiarCarga(false); }
});
