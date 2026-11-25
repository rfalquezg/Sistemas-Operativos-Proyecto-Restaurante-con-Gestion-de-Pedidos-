
// GESTION DE PEDIDOS
// Visualizacion de hilos con espera del mutex.

const $ = (id) => {
    const elemento = document.getElementById(id);

    if (!elemento) {
        throw new Error(
            `Falta el elemento #${id} en index.html`
        );
    }

    return elemento;
};

let resultado = null;
let indice = 0;
let temporizador = null;
let pausado = false;
let secuencia = 0;

let historial = [];
let confirmados = 0;
let rechazados = 0;

let reservasVistas = new Set();
let pedidosActuales = new Map();

const descripcion = {
    "basico-false":
        "Pollo representado como entero. Sin mutex, " +
        "dos cocineros pueden reservar la misma unidad.",

    "basico-true":
        "Pollo representado como entero. Con mutex, " +
        "los cocineros esperan su turno para entrar.",

    "complejo-false":
        "Lasaña preparada en un diccionario. Sin mutex, " +
        "pueden ocurrir reservas duplicadas.",

    "complejo-true":
        "Lasaña preparada en un diccionario. " +
        "El segundo cocinero espera a que el primero libere el mutex."
};


// Obtener la configuracion seleccionada.
function seleccion() {
    const [tipo, modo] = $("version").value.split("-");

    const cocineros = Number($("cocineros").value);
    const stock = Number($("stock").value);

    if (
        !Number.isInteger(cocineros) ||
        cocineros < 2 ||
        cocineros > 6 ||
        !Number.isInteger(stock) ||
        stock < 0 ||
        stock > 10
    ) {
        throw new Error(
            "Ingresa entre 2 y 6 cocineros " +
            "y entre 0 y 10 unidades."
        );
    }

    return {
        tipo,
        con_mutex: modo === "true",
        cocineros,
        stock
    };
}


// Consultar la simulacion ejecutada por Python.
async function consultarAPI(configuracion) {
    const respuesta = await fetch("/api/simular", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(configuracion)
    });

    const datos = await respuesta.json();

    if (!respuesta.ok) {
        throw new Error(
            datos.error || "No se pudo ejecutar la simulación."
        );
    }

    return datos;
}


// Detener la reproduccion.
function limpiarTimer() {
    clearTimeout(temporizador);
    temporizador = null;
    secuencia++;
}


// Cambiar el texto de un elemento HTML.
function establecerTexto(id, texto) {
    $(id).textContent = texto;
}


// Crear elementos visuales.
function crearElemento(etiqueta, clase = "", texto) {
    const elemento = document.createElement(etiqueta);

    if (clase) {
        elemento.className = clase;
    }

    if (texto !== undefined) {
        elemento.textContent = String(texto);
    }

    return elemento;
}


// Cambiar entre representacion basica y compleja.
function cambiarModo() {
    establecerTexto(
        "scenario-tip",
        descripcion[$("version").value]
    );

    const config = seleccion();

    establecerTexto(
        "resource-description",
        config.tipo === "basico"
            ? "Variable entera · pollo"
            : "Diccionario · platos preparados"
    );

    establecerTexto(
        "mutex-status",
        config.con_mutex
            ? "🔒 Con exclusión mutua"
            : "○ Sin exclusión mutua"
    );

    establecerTexto(
        "resource-name",
        config.tipo === "basico" ? "Pollo" : "Lasaña"
    );

    establecerTexto(
        "resource-emoji",
        config.tipo === "basico" ? "🍗" : "🍝"
    );

    establecerTexto(
        "resource-kind",
        config.tipo === "basico"
            ? "variable int"
            : "diccionario dict"
    );
}


// Preparar los cocineros y los pedidos.
function armarCocina(datos) {
    indice = 0;
    historial = [];
    confirmados = 0;
    rechazados = 0;

    reservasVistas = new Set();
    pedidosActuales = new Map();

    $("log-body").replaceChildren();
    $("cooks").replaceChildren();
    $("order-list").replaceChildren();

    // Crear todos los cocineros.
    for (let i = 1; i <= datos.cocineros; i++) {
        const tarjeta = crearElemento("div", "cook");
        tarjeta.id = `cook-${i}`;

        tarjeta.append(
            crearElemento("div", "avatar", "👨‍🍳"),
            crearElemento("b", "", `Cocinero ${i}`),
            crearElemento(
                "span",
                "state",
                "Esperando pedido"
            )
        );

        $("cooks").append(tarjeta);

        // Crear el pedido correspondiente.
        const pedido = crearElemento(
            "div",
            "order-item",
            `📋 Pedido ${i} · En espera`
        );

        pedido.id = `order-${i}`;
        $("order-list").append(pedido);

        pedidosActuales.set(i, "pendiente");
    }

    establecerTexto(
        "cook-progress",
        `${datos.cocineros} cocineros preparados`
    );

    establecerTexto(
        "resource-count",
        datos.stock_inicial
    );

    establecerTexto("tray-count", "0");

    for (const id of [
        "stat-stock",
        "stat-reservas",
        "stat-rechazados",
        "stat-conflictos"
    ]) {
        establecerTexto(id, "—");
    }

    establecerTexto(
        "logs-count",
        "0 operaciones registradas"
    );

    establecerTexto("final-line", "Estado final: —");

    establecerTexto(
        "progress-label",
        `Paso 0 / ${datos.movimientos.length}`
    );

    $("progress-fill").style.width = "0%";

    establecerTexto(
        "resource-badge",
        datos.stock_inicial > 0
            ? "● Disponible"
            : "○ Agotado"
    );

    $("resource-card").className =
        "resource" +
        (datos.stock_inicial === 0 ? " empty" : "");

    $("critical-info").className = "critical-info";

    establecerTexto(
        "critical-text",
        "Los cocineros están preparados."
    );

    establecerTexto("critical-lock", "🔓 Libre");
    establecerTexto("run-status", "Reproduciendo");

    $("run-status").className = "stage-status running";

    $("pause").disabled = false;
    $("step").disabled = false;
    $("restart").disabled = false;
    $("csv").disabled = true;

    $("pause").textContent = "⏸ Pausar";

    pausado = false;
}


// Cambiar visualmente el estado de un cocinero.
function actualizarCocinero(nombre, etapa) {
    const numero = Number(
        (nombre.match(/\d+/) || [])[0]
    );

    const tarjeta = $(`cook-${numero}`);
    const pedido = $(`order-${numero}`);

    // El cocinero permanece visible todo el tiempo.
    tarjeta.className = "cook";

    const estados = {
        esperar: "⏳ Esperando turno...",
        entrar: "🔒 En sección crítica",
        consultar: "Consultando stock...",
        validar: "Validando cantidad...",
        reservar: "✓ Reserva confirmada",
        rechazar: "✕ Sin disponibilidad",
        salir: "🔓 Proceso finalizado"
    };

    tarjeta.querySelector(".state").textContent =
        estados[etapa] || etapa;

    // Esperando el mutex.
    if (etapa === "esperar") {
        tarjeta.classList.add("waiting");
    }

    // Trabajando dentro de la sección crítica.
    else if (
        ["entrar", "consultar", "validar"].includes(etapa)
    ) {
        tarjeta.classList.add("active");
    }

    // Reserva confirmada.
    else if (etapa === "reservar") {
        tarjeta.classList.add("done");
    }

    // Pedido sin disponibilidad.
    else if (etapa === "rechazar") {
        tarjeta.classList.add("fail");
    }

    // El cocinero terminó su proceso.
    else if (etapa === "salir") {
        tarjeta.classList.add(
            pedidosActuales.get(numero) === "rechazar"
                ? "fail"
                : "done"
        );
    }

    // Registrar resultados sin duplicarlos.
    if (
        (etapa === "reservar" || etapa === "rechazar") &&
        !reservasVistas.has(numero)
    ) {
        reservasVistas.add(numero);

        if (etapa === "reservar") {
            confirmados++;
        } else {
            rechazados++;
        }

        pedidosActuales.set(numero, etapa);

        pedido.className =
            "order-item " +
            (etapa === "reservar" ? "done" : "fail");

        pedido.textContent =
            `${etapa === "reservar" ? "✅" : "❌"} ` +
            `Pedido ${numero} · ` +
            (etapa === "reservar"
                ? "Atendido"
                : "Rechazado");
    }
}


// Color del resultado en el registro.
function colorResultado(paso) {
    if (paso.duplicada) return "orange";
    if (paso.etapa === "esperar") return "orange";
    if (paso.etapa === "reservar") return "green";
    if (paso.etapa === "rechazar") return "orange";

    if (
        ["entrar", "consultar", "validar"].includes(
            paso.etapa
        )
    ) {
        return "blue";
    }

    return "";
}


// Agregar una operacion a la tabla.
function agregarFila(paso) {
    const fila = crearElemento("tr", "new-row");

    if (
        $("highlight").checked &&
        [
            "entrar",
            "consultar",
            "validar",
            "reservar",
            "rechazar"
        ].includes(paso.etapa)
    ) {
        fila.classList.add("row-critical");
    }

    const columnas = [
        String(paso.paso).padStart(2, "0"),
        paso.hilo,
        paso.etapa.charAt(0).toUpperCase() +
        paso.etapa.slice(1),
        paso.antes
    ];

    for (const valor of columnas) {
        fila.append(
            crearElemento("td", "", valor)
        );
    }

    const resultadoCelda = crearElemento("td");

    resultadoCelda.append(
        crearElemento(
            "span",
            "pill " + colorResultado(paso),
            paso.mensaje
        )
    );

    fila.append(resultadoCelda);

    fila.append(
        crearElemento("td", "", paso.despues)
    );

    $("log-body").append(fila);

    historial.push(paso);

    establecerTexto(
        "logs-count",
        `${historial.length} operaciones registradas`
    );
}


// Reproducir una operacion.
function reproducirPaso() {
    if (!resultado) {
        return;
    }

    if (indice >= resultado.movimientos.length) {
        terminar();
        return;
    }

    const paso = resultado.movimientos[indice];
    indice++;

    actualizarCocinero(
        paso.hilo,
        paso.etapa
    );

    const recurso = $("resource-card");

    // Se resalta el recurso cuando está ocupado.
    recurso.className = "resource";

    if (
        ["entrar", "consultar", "validar"].includes(
            paso.etapa
        )
    ) {
        recurso.classList.add("busy");
    }

    if (paso.duplicada) {
        recurso.classList.add("conflict");
    }

    // Mostrar el valor registrado del inventario.
    establecerTexto(
        "resource-count",
        paso.despues
    );

    let mensajeRecurso = "● Disponible";

    if (paso.duplicada) {
        mensajeRecurso = "⚠ Reserva duplicada";
    }

    else if (paso.etapa === "esperar") {
        mensajeRecurso = "🔒 Mutex ocupado";
    }

    else if (paso.etapa === "reservar") {
        mensajeRecurso = "● Reserva realizada";
    }

    else if (paso.despues === 0) {
        mensajeRecurso = "○ Sin stock";
    }

    establecerTexto(
        "resource-badge",
        mensajeRecurso
    );

    establecerTexto(
        "tray-count",
        confirmados
    );

    // Mostrar quién tiene el mutex.
    establecerTexto(
        "critical-text",
        `${paso.hilo}: ${paso.mensaje}`
    );

    let estadoMutex = "◌ Sin bloqueo";

    if (paso.etapa === "esperar") {
        estadoMutex = "🔒 Ocupado · esperando";
    }

    else if (paso.etapa === "salir") {
        estadoMutex = "🔓 Mutex liberado";
    }

    else if (
        resultado.con_mutex &&
        [
            "entrar", "consultar", "validar",
            "reservar", "rechazar"
        ].includes(paso.etapa)
    ) {
        estadoMutex = "🔒 Mutex ocupado";
    }

    establecerTexto(
        "critical-lock",
        estadoMutex
    );

    $("critical-info").className = "critical-info";

    if (
        $("highlight").checked &&
        [
            "entrar", "consultar", "validar",
            "reservar", "rechazar"
        ].includes(paso.etapa)
    ) {
        $("critical-info").classList.add("active");
    }

    establecerTexto(
        "cook-progress",
        `${paso.hilo} · ${paso.etapa}`
    );

    agregarFila(paso);

    establecerTexto(
        "progress-label",
        `Paso ${indice} / ${resultado.movimientos.length}`
    );

    const porcentaje =
        indice / resultado.movimientos.length * 100;

    $("progress-fill").style.width =
        `${porcentaje}%`;

    if (indice >= resultado.movimientos.length) {
        terminar();
    }
}


// Finalizar la simulacion.
function terminar() {
    limpiarTimer();

    if (!resultado) {
        return;
    }

    establecerTexto(
        "run-status",
        resultado.conflicto
            ? "Conflicto detectado"
            : "Simulación finalizada"
    );

    $("run-status").className =
        "stage-status" +
        (resultado.conflicto ? " warning" : "");

    establecerTexto(
        "stat-stock",
        resultado.stock_final
    );

    establecerTexto(
        "stat-reservas",
        resultado.reservas
    );

    establecerTexto(
        "stat-rechazados",
        resultado.rechazados
    );

    establecerTexto(
        "stat-conflictos",
        resultado.conflictos
    );

    establecerTexto(
        "resource-count",
        resultado.stock_final
    );

    establecerTexto(
        "tray-count",
        resultado.reservas
    );

    establecerTexto(
        "final-line",
        `Estado final: ${resultado.stock_final} ${resultado.recurso}`
    );

    $("resource-card").className = "resource";

    if (resultado.conflicto) {
        $("resource-card").classList.add("conflict");
    }

    else if (resultado.stock_final === 0) {
        $("resource-card").classList.add("empty");
    }

    establecerTexto(
        "resource-badge",
        resultado.conflicto
            ? "⚠ Conflicto detectado"
            : resultado.stock_final === 0
                ? "○ Agotado"
                : "● Disponible"
    );

    establecerTexto(
        "critical-text",
        resultado.mensaje
    );

    establecerTexto(
        "critical-lock",
        "🔓 Finalizado"
    );

    $("critical-info").className = "critical-info";

    $("pause").disabled = true;
    $("step").disabled = true;
    $("csv").disabled = historial.length === 0;

    $("run").disabled = false;
    $("compare-btn").disabled = false;

    establecerTexto(
        "notice",
        resultado.mensaje
    );
}


// Reproducir automaticamente los movimientos.
function programar() {
    limpiarTimer();

    const token = secuencia;

    const avanzar = () => {
        if (
            token !== secuencia ||
            pausado ||
            !resultado
        ) {
            return;
        }

        reproducirPaso();

        if (
            indice < resultado.movimientos.length &&
            !pausado
        ) {
            temporizador = setTimeout(
                avanzar,
                850 / Number($("speed").value)
            );
        }
    };

    temporizador = setTimeout(
        avanzar,
        420 / Number($("speed").value)
    );
}


// Ejecutar los hilos reales en Python.
async function iniciar() {
    limpiarTimer();
    resultado = null;

    try {
        const config = seleccion();

        $("run").disabled = true;
        $("compare-btn").disabled = true;

        establecerTexto(
            "notice",
            "Python está ejecutando los hilos..."
        );

        const datos = await consultarAPI(config);

        resultado = datos;
        armarCocina(datos);

        establecerTexto(
            "notice",
            "Reproduciendo las operaciones registradas..."
        );

        programar();

    } catch (error) {
        $("run").disabled = false;
        $("compare-btn").disabled = false;

        establecerTexto(
            "notice",
            "⚠ " + error.message
        );
    }
}


// Exportar el registro a CSV.
function descargarCSV() {
    if (!historial.length) return;

    const lineas = [
        [
            "Paso",
            "Hilo",
            "Operación",
            "Estado anterior",
            "Resultado",
            "Estado posterior"
        ],
        ...historial.map(paso => [
            paso.paso,
            paso.hilo,
            paso.etapa,
            paso.antes,
            paso.mensaje,
            paso.despues
        ])
    ];

    const escapar = valor =>
        '"' +
        String(valor ?? "").replaceAll('"', '""') +
        '"';

    const csv = "\ufeff" +
        lineas.map(fila =>
            fila.map(escapar).join(";")
        ).join("\r\n");

    const blob = new Blob(
        [csv],
        {type: "text/csv;charset=utf-8"}
    );

    const url = URL.createObjectURL(blob);

    const enlace = document.createElement("a");

    enlace.href = url;
    enlace.download = "gestion_de_pedidos_ejecucion.csv";
    enlace.click();

    setTimeout(
        () => URL.revokeObjectURL(url),
        1000
    );
}


// Comparar las cuatro versiones.
async function comparar() {
    try {
        const config = seleccion();

        $("compare-btn").disabled = true;

        const opciones = [
            ["basico", false],
            ["basico", true],
            ["complejo", false],
            ["complejo", true]
        ];

        const resultados = await Promise.all(
            opciones.map(([tipo, con_mutex]) =>
                consultarAPI({
                    tipo,
                    con_mutex,
                    cocineros: config.cocineros,
                    stock: config.stock
                })
            )
        );

        $("compare-grid").replaceChildren();

        for (const r of resultados) {
            const tarjeta = crearElemento(
                "article",
                "compare-card"
            );

            tarjeta.append(
                crearElemento(
                    "h3",
                    "",
                    r.tipo === "basico"
                        ? "🍗 Básico"
                        : "🍝 Complejo"
                ),
                crearElemento(
                    "p",
                    "subtitle",
                    r.con_mutex
                        ? "Con mutex"
                        : "Sin mutex"
                )
            );

            tarjeta.append(
                crearElemento(
                    "div",
                    "big",
                    r.reservas
                ),
                crearElemento(
                    "p",
                    "subtitle",
                    "reservas confirmadas"
                ),
                crearElemento(
                    "div",
                    "compare-meta",
                    `Inicial: ${r.stock_inicial} · Final: ${r.stock_final}`
                ),
                crearElemento(
                    "div",
                    "compare-meta",
                    `Rechazados: ${r.rechazados} · ` +
                    `Conflictos: ${r.conflictos}`
                ),
                crearElemento(
                    "div",
                    "compare-result" +
                    (r.conflicto ? " bad" : ""),
                    r.conflicto
                        ? "⚠ Condición de carrera"
                        : "✓ Inventario consistente"
                )
            );

            $("compare-grid").append(tarjeta);
        }

    } catch (error) {
        establecerTexto(
            "notice",
            "⚠ " + error.message
        );

    } finally {
        $("compare-btn").disabled = false;
    }
}


// EVENTOS DE LA INTERFAZ

$("version").addEventListener("change", () => {
    try {
        cambiarModo();
    } catch (error) {
        establecerTexto("notice", error.message);
    }
});

$("speed").addEventListener("input", () => {
    establecerTexto(
        "speed-label",
        $("speed").value + "×"
    );
});

$("run").addEventListener("click", iniciar);

$("pause").addEventListener("click", () => {
    pausado = !pausado;

    $("pause").textContent =
        pausado ? "▶ Continuar" : "⏸ Pausar";

    if (pausado) {
        limpiarTimer();
    } else {
        programar();
    }
});

$("step").addEventListener("click", () => {
    pausado = true;
    limpiarTimer();

    $("pause").textContent = "▶ Continuar";
    reproducirPaso();
});

$("restart").addEventListener("click", () => {
    if (!resultado) return;

    limpiarTimer();
    armarCocina(resultado);
    programar();
});

$("csv").addEventListener(
    "click",
    descargarCSV
);

$("compare-btn").addEventListener(
    "click",
    comparar
);

// Estado inicial de la página.
try {
    cambiarModo();
} catch (error) {
    console.error(error);
}
