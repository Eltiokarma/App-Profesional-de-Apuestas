import React, { useState, useEffect } from "react";

/* ============================================================
   SAD · EL TEOREMA DEL ECHADO (TDE v0.1 — PROTOTIPO)
   Módulo de la capa DTP. Mide la probabilidad de que un equipo
   se eche: repliegue NO controlado hacia su propia área.
   Caso de estreno: Melgar vs FC Cajamarca
   Liga 1 2026 · Clausura F4 · Monumental UNSA · 09.08.2026
   ============================================================ */

const C = {
  text: "#1a1a2e", sec: "#37474F", muted: "#78909C",
  card: "#F8F9FA", bar: "#ECEFF1", border: "#DEE2E6",
  green: "#2E7D32", amber: "#E8A33D", red: "#C62828", blue: "#1565C0", violet: "#6A4FB6",
};
const MEL = { name: "FBC MELGAR", short: "MEL", color: "#C8102E", light: "#FBE7EA" };
const CAJ = { name: "FC CAJAMARCA", short: "CAJ", color: "#1B3A93", light: "#E8ECF8" };

/* ---------- DEFINICIÓN DEL MÓDULO ---------- */
const TESIS = "Echarse no es un estado, es una transición. El TDE no pregunta si un equipo defiende bajo, pregunta si va a retroceder sin decidirlo, en qué ventana de 15 minutos, por qué causa y — lo único que de verdad importa — si al retroceder va a mantener la distancia entre su línea de fondo y su línea de volantes. Un equipo que se echa ordenado concede tiros de afuera. Un equipo que se parte concede goles.";

const CADENA = "P(echada) × P(fractura | echada) × P(gol | fractura) = riesgo real de la ventana final. Las tres son probabilidades distintas y se estiman por separado. El error clásico del análisis es leer la primera y hablar como si fuera la tercera.";

/* ---------- ÍNDICE IE ---------- */
const IE = {
  MEL: {
    ie: 4.6, p: 38, tipo: "Voluntaria / administrativa", ventana: "75-90'",
    frac: 22, golFrac: 45, compuesto: 3.8,
    bloques: [
      {
        id: "F", nombre: "Carga física", peso: "×3", riesgo: 0.55,
        ind: [
          { k: "F1", t: "Rotación en los últimos 3 partidos", v: "0 titulares rotados", r: "alto", j: "Rondelli repitió el mismo XI en las fechas 2 y 3. Minutos acumulados concentrados en once nombres." },
          { k: "F2", t: "Descanso y calendario", v: "7 días · viaje a 2.900 m en la F5", r: "medio", j: "Descanso suficiente para este partido, pero con Andahuaylas a 5 días hay incentivo explícito para bajar revoluciones en el tramo final." },
          { k: "F3", t: "Profundidad de banco (hereda B5 del EFE)", v: "Banco de jerarquía", r: "bajo", j: "Zegarra, Portillo, Cáceres, Guzmán, Zanelatto. Piernas frescas disponibles: el mitigante más fuerte del bloque." },
          { k: "F4", t: "Costo energético del modelo", v: "Presión alta + construcción desde el arquero", r: "medio", j: "Modelo caro. Presionar arriba y salir jugando desde Cabezudo exige coordinación sostenida." },
        ],
      },
      {
        id: "C", nombre: "Control del repliegue", peso: "×2", riesgo: 0.35,
        ind: [
          { k: "C1", t: "¿Tiene bloque bajo entrenado?", v: "Parcial", r: "medio", j: "El 3-4-2-1 cae a 5-4-1 con naturalidad: la estructura para replegar existe. Pero solo tiene 3 fechas de rodaje en este esquema." },
          { k: "C2", t: "Coordinación línea-volantes", v: "Tandazo como ancla", r: "bajo", j: "Con un pivote que acompaña el descenso de la línea de cinco, la franja entre líneas queda cubierta. Es la diferencia entre echarse y partirse." },
          { k: "C3", t: "Disciplina en cierres previos", v: "Sostuvo el 2-1 ante Cristal", r: "bajo", j: "Aguantó los últimos 25 minutos con un gol de diferencia contra un rival que fue a buscar el empate. Evidencia a favor, muestra corta." },
        ],
      },
      {
        id: "P", nombre: "Psicológico", peso: "×2", riesgo: 0.55,
        ind: [
          { k: "P1", t: "Marcador esperado y rol", v: "Favorito, probable 1-0 o 2-0", r: "alto", j: "Es el escenario de máximo riesgo del TDE: el favorito que va ganando deja de jugar para ganar y empieza a jugar para no perder." },
          { k: "P2", t: "D3 del EFE (respuesta a adversidad)", v: "🔶 parcial", r: "medio", j: "Remontó en Cusco y ante Alianza Atlético; pero el bache del Apertura solo se cortó con cambio de DT." },
          { k: "P3", t: "Relevancia asimétrica del partido", v: "Obligado a ganar", r: "alto", j: "Comparte la punta y adelante tiene Andahuaylas, Alianza Lima y una visita trampa a Piura. Miedo a perder lo ganado en su forma más pura." },
          { k: "P4", t: "Público", v: "A favor", r: "bajo", j: "El Monumental empuja. Reduce el componente psicológico del repliegue, aunque lo sustituye por ansiedad si el 0-0 se estira." },
        ],
      },
      {
        id: "S", nombre: "Estructural del partido", peso: "×1.5", riesgo: 0.30,
        ind: [
          { k: "S1", t: "Riesgo de inferioridad numérica", v: "Bajo", r: "bajo", j: "Sin sancionados al límite reportados ni antecedente disciplinario reciente en el XI." },
          { k: "S2", t: "Cambios defensivos previsibles del DT", v: "Probables con ventaja", r: "medio", j: "Con el partido resuelto y el viaje encima, Rondelli tiene motivo doble para meter perfil defensivo y bajar el punto de referencia." },
          { k: "S3", t: "¿El rival puede superar su primera línea?", v: "Poco probable", r: "bajo", j: "Cajamarca no tiene un 9 que fije ni salida limpia: difícilmente enseñe a Melgar a no presionar." },
        ],
      },
    ],
  },
  CAJ: {
    ie: 7.6, p: 82, tipo: "Física + presión superada", ventana: "60-75'",
    frac: 58, golFrac: 55, compuesto: 26.1,
    bloques: [
      {
        id: "F", nombre: "Carga física", peso: "×3", riesgo: 0.80,
        ind: [
          { k: "F1", t: "Rotación en los últimos 3 partidos", v: "XI en construcción", r: "alto", j: "No hay rotación medible porque no hay XI tipo: los cambios son por integración de fichajes, no por dosificación." },
          { k: "F2", t: "Descanso y calendario", v: "8 días · viaje Cajamarca-Arequipa", r: "bajo", j: "Bien descansado. Y es equipo de altura real (2.750 m en casa): Arequipa no le agrega desgaste." },
          { k: "F3", t: "Profundidad de banco", v: "Banco sin recambio de nivel", r: "alto", j: "Dioses, Meza, Ocas, Alegría, Sandoval. Ninguno con impacto documentado desde el banco en el Clausura." },
          { k: "F4", t: "Costo energético del modelo", v: "Defender en bloque con 4-5-1 sin nueve", r: "alto", j: "El gasto anaeróbico de defender bajo es el más caro del fútbol: frenadas, cambios de dirección, contracciones isométricas. Y sin un 9 que aguante el balón, cada despeje vuelve en 8 segundos." },
        ],
      },
      {
        id: "C", nombre: "Control del repliegue", peso: "×2", riesgo: 0.85,
        ind: [
          { k: "C1", t: "¿Tiene bloque bajo entrenado?", v: "No: improvisado", r: "alto", j: "La línea defensiva completa (Pósito, Vílchez, A. Gutiérrez, más Soto y Suárez) se armó en julio. Tres semanas de convivencia no producen automatismos de repliegue." },
          { k: "C2", t: "Coordinación línea-volantes", v: "Sin evidencia", r: "alto", j: "Con cinco volantes y un solo delantero ya tuvo 53% de posesión y perdió 0-2: tuvo la pelota sin control del juego. Es el perfil exacto del equipo que se parte antes de echarse." },
          { k: "C3", t: "Disciplina en cierres previos", v: "No sostuvo ninguna", r: "alto", j: "2-2 con Juan Pablo II y 1-2 con Garcilaso: cedió en los dos partidos donde tuvo algo que administrar." },
        ],
      },
      {
        id: "P", nombre: "Psicológico", peso: "×2", riesgo: 0.75,
        ind: [
          { k: "P1", t: "Marcador esperado y rol", v: "Visitante, probable 0-1 en contra", r: "alto", j: "Recibir el primer gol es su escenario modal. Lago-Peñas: el primer gol reordena el partido; contra un D3 ❌ lo reordena el doble." },
          { k: "P2", t: "D3 del EFE", v: "❌ sin respuesta documentada", r: "alto", j: "Concedió al 13' en su propia altura la fecha pasada y no encontró vía de reacción." },
          { k: "P3", t: "Relevancia asimétrica", v: "El punto es bonus", r: "medio", j: "Sabe que su semestre se juega en las fechas 5 a 7 (Universitario, Grau, Comerciantes). Reservar energía es racional, y racionalizar el repliegue lo acelera." },
          { k: "P4", t: "Contexto extra-cancha", v: "CRISIS-EX activo", r: "alto", j: "Sueldos en disputa, punto descontado y comunicado de SAFAP por presiones. Baumeister: el autocontrol colectivo es finito y este plantel lo viene gastando desde junio." },
        ],
      },
      {
        id: "S", nombre: "Estructural del partido", peso: "×1.5", riesgo: 0.60,
        ind: [
          { k: "S1", t: "Riesgo de inferioridad numérica", v: "Elevado", r: "alto", j: "18 faltas cometidas ante Sport Huancayo. Un equipo que corta con falta en zona propia acumula amarillas y expone la roja." },
          { k: "S2", t: "Cambios defensivos previsibles del DT", v: "Muy probables", r: "alto", j: "Si va 0-1, Ayala tiene la tentación clásica: tercer central para no recibir el segundo, que baja el punto de referencia y regala el mediocampo." },
          { k: "S3", t: "¿El rival puede superar su primera línea?", v: "Sí, con facilidad", r: "alto", j: "Melgar tiene dos mediapuntas entre líneas (Quagliata, Vidales). Cuando la primera línea es saltada con un pase, el equipo aprende a no presionar: es el mecanismo ECHADA-SUP." },
        ],
      },
    ],
  },
};

/* ---------- VENTANAS ---------- */
const VENTANAS = ["0-15", "15-30", "30-45", "45-60", "60-75", "75-90"];
const RIESGO = {
  MEL: [5, 8, 10, 18, 30, 38],
  CAJ: [25, 35, 45, 60, 82, 78],
};
const VENTANA_NOTA = {
  MEL: "El riesgo rojinegro es de final de partido y depende del marcador: si no va ganando, no se echa — se abre, que es el problema opuesto (y el que produce el gol de Palacios en contra).",
  CAJ: "Cajamarca arranca a 25 porque su plan ya es un repliegue parcial. El salto está en la ventana 60-75, donde el bloque improvisado llega al final de su vida útil táctica y física. Baja levemente en 75-90 solo porque, si ya recibió el segundo, el partido se abre y deja de estar echado: pasa a estar partido.",
};

/* ---------- TIPOLOGÍA ---------- */
const TIPOS = [
  {
    cod: "ECHADA-VOL", n: "Voluntaria / administrativa", color: C.blue,
    def: "El DT decide replegar para administrar un resultado o para aguantar como visitante.",
    senal: "Cambio defensivo explícito, línea que baja 10-12 metros de golpe tras un cambio, no tras una jugada.",
    falla: "Administrar 30 minutos en bloque bajo exige una disciplina que pocos planteles tienen. Falla cuando el equipo no ensayó el repliegue, no cuando la decisión es mala.",
    contra: "Sostener un punto de referencia arriba: un delantero que aguante el balón convierte el repliegue en descanso; sin él, el repliegue es asfixia.",
  },
  {
    cod: "ECHADA-FIS", n: "Física", color: C.amber,
    def: "La causa más común y la menos reconocida. Los volantes dejan de llegar al segundo balón y la línea retrocede para no dejar espalda descubierta.",
    senal: "Aparece entre el 60 y el 65. La distancia entre volantes y defensa crece antes de que la defensa baje.",
    falla: "El mitigante real no es el corazón, es el banco. Bradley 2009: la distancia de sprint de alta intensidad cae 20-30% en el segundo tiempo.",
    contra: "Cambios en el mediocampo, no en la defensa. Refrescar la primera línea de presión es más barato que reforzar la última.",
  },
  {
    cod: "ECHADA-SUP", n: "Presión superada", color: C.violet,
    def: "El rival aprende a saltar la primera línea con un pase, y el equipo aprende a no presionar. Retrocede porque presionar y fallar es peor que no presionar.",
    senal: "PPDA que sube sin que caiga el ritmo físico. Dos o tres pases interiores exitosos del rival y la presión se apaga.",
    falla: "Se confunde con la echada física y se corrige con cambios frescos que no arreglan nada, porque el problema es de plan.",
    contra: "Cambiar la referencia de presión, no la intensidad: presionar el pase interior en lugar de al hombre con la pelota.",
  },
  {
    cod: "ECHADA-PSI", n: "Psicológica", color: C.red,
    def: "Miedo a perder lo que ya se tiene. El favorito que va 1-0 deja de jugar para ganar y empieza a jugar para no perder, que son dos cosas distintas.",
    senal: "Cae el volumen de pases hacia adelante en tercio rival sin que cambie nada del marcador ni del físico. Balones tirados largos sin destino.",
    falla: "También aparece tras recibir un gol o con público hostil. Baumeister 1998: el autocontrol colectivo consume recursos finitos.",
    contra: "Una consigna concreta y ejecutable para el tramo final: no 'aguantar', sino 'dos toques y falta lejos del área'. Lo vago acelera la echada.",
  },
  {
    cod: "ECHADA-NUM", n: "Numérica", color: C.sec,
    def: "Roja, lesión que obliga a rearmar, o cambios defensivos que bajan el punto de referencia del equipo.",
    senal: "Instantánea y visible: el dibujo cambia en una jugada.",
    falla: "Es la única echada que no admite discusión táctica. Lo que se evalúa es el rearmado, no la decisión.",
    contra: "Sacrificar al hombre de la zona de menor peligro, no al más cansado.",
  },
  {
    cod: "FRACTURA", n: "El equipo no se echó: se partió", color: "#7B1FA2",
    def: "El síntoma peligroso no es el repliegue, es la descoordinación: la línea de cuatro retrocede pero los volantes no la siguen y se abre la franja entre líneas donde el rival recibe de cara.",
    senal: "Distancia línea de fondo - línea de volantes por encima de 18-20 metros de forma sostenida. Rival recibiendo de frente entre líneas dos veces seguidas.",
    falla: "De ahí sale la mayoría de los goles de los últimos 15 minutos. Es la variable que el TDE estima aparte, porque es la que convierte una echada inocua en un gol.",
    contra: "Es la única emergencia real: un pivote que baje con la línea, aunque signifique renunciar a salir jugando.",
  },
];

/* ---------- DETECCIÓN EN DATOS ---------- */
const METRICAS = [
  { m: "Altura media de la línea defensiva", u: "metros desde arco propio", umbral: "Caída sostenida de 8+ m respecto al promedio del propio partido", lee: "Confirma el repliegue, no su causa." },
  { m: "Distancia línea de fondo - línea de volantes", u: "metros", umbral: "Más de 18-20 m sostenidos", lee: "La métrica clave del módulo: separa echada de fractura." },
  { m: "PPDA", u: "pases rivales permitidos por acción defensiva", umbral: "Sube 40%+ respecto a su propia primera media hora", lee: "Si sube sin caída física, es ECHADA-SUP; si sube con caída física, es ECHADA-FIS." },
  { m: "Porcentaje de pases en tercio propio", u: "%", umbral: "Por encima de 55% en una ventana de 15'", lee: "Confirma que el equipo ya no puede salir, solo despejar." },
  { m: "Field tilt", u: "% de posesión en tercio rival", umbral: "Por debajo de 30%", lee: "Territorialidad cedida. Útil para fechar el minuto exacto de la transición." },
  { m: "xG concedido por ventanas de 15'", u: "xG", umbral: "Ventana final con xG superior a la suma de las tres primeras", lee: "El resultado de la fractura, no de la echada. Es la métrica de validación del pronóstico." },
  { m: "Duelos de segunda pelota ganados", u: "%", umbral: "Caída por debajo de 40%", lee: "Suele ser la primera señal de todas: aparece antes de que la línea baje." },
];

/* ---------- CASOS DE CALIBRACIÓN ---------- */
const CASOS = [
  { p: "Moquegua 0-0 Melgar (F3, 02.08.2026)", ie: "Moquegua alto (≈7)", real: "Bloque bajo sostenido los 90'. Melgar con 71% de posesión y 1 remate al arco.", lec: "Caso que CONTRADICE la regla de la vida útil: el bloque estaba entrenado. IE alto no implica fractura. Calibra P(fractura|echada) a la baja cuando C1 = bloque documentado." },
  { p: "Cajamarca 0-2 Sport Huancayo (F3, 01.08.2026)", ie: "Cajamarca ≈7,5", real: "0-1 al minuto 13 con 53% de posesión propia. Sin reacción.", lec: "Caso que CONFIRMA: tener la pelota no es controlar el juego. Un equipo puede estar echado con posesión mayoritaria." },
  { p: "Cajamarca 3-1 Melgar (Apertura F5, 21.02.2026)", ie: "Melgar ≈6 en el tramo final", real: "Melgar ganaba 0-1 desde el 42' y recibió tres goles entre el 77' y el 90+1'.", lec: "El caso fundacional del módulo: ECHADA-PSI del favorito + FRACTURA en la ventana 75-90. Advertencia: el ejecutor fue Barcos, hoy en Sporting Cristal. La lección es del mecanismo, no del rival." },
  { p: "Melgar 2-1 Sporting Cristal (F2, 25.07.2026)", ie: "Melgar ≈5", real: "Sostuvo los últimos 25 minutos con un gol de diferencia ante un rival que fue a buscarlo.", lec: "Caso que CONTRADICE el automatismo del favorito: se echó y no se partió. Tandazo bajando con la línea es la variable que lo explica." },
];

/* ============================================================
   COMPONENTES
   ============================================================ */
function Gauge({ pct, color, label, tipo, ventana, ie }) {
  const [v, setV] = useState(0);
  useEffect(() => { const t = setTimeout(() => setV(pct), 120); return () => clearTimeout(t); }, [pct]);
  const R = 58, CIRC = 2 * Math.PI * R, off = CIRC - (CIRC * v) / 100;
  return (
    <div style={{ textAlign: "center", flex: 1, minWidth: 200 }}>
      <svg width="150" height="150" viewBox="0 0 150 150">
        <circle cx="75" cy="75" r={R} fill="none" stroke={C.bar} strokeWidth="12" />
        <circle cx="75" cy="75" r={R} fill="none" stroke={color} strokeWidth="12" strokeLinecap="round"
          strokeDasharray={CIRC} strokeDashoffset={off} transform="rotate(-90 75 75)"
          style={{ transition: "stroke-dashoffset 1.1s cubic-bezier(.4,0,.2,1)" }} />
        <text x="75" y="72" textAnchor="middle" style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 32, fontWeight: 700, fill: C.text }}>{pct}%</text>
        <text x="75" y="92" textAnchor="middle" style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11, fill: C.muted }}>IE {ie.toFixed(1)} / 10</text>
      </svg>
      <div style={{ fontFamily: "'JetBrains Mono',monospace", fontWeight: 700, fontSize: 14, color: color, letterSpacing: 0.6 }}>{label}</div>
      <div style={{ fontSize: 12, color: C.sec, marginTop: 6, lineHeight: 1.6 }}>
        Tipo modal: <b>{tipo}</b><br />Ventana modal: <b>{ventana}</b>
      </div>
    </div>
  );
}

function RiskDot({ r }) {
  const map = { alto: C.red, medio: C.amber, bajo: C.green };
  const lbl = { alto: "Alto", medio: "Medio", bajo: "Bajo" };
  return (
    <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, fontWeight: 700, color: map[r], border: "1px solid " + map[r], borderRadius: 10, padding: "1px 7px", whiteSpace: "nowrap" }}>{lbl[r]}</span>
  );
}

function BlockCard({ b, color, light }) {
  const [open, setOpen] = useState(false);
  const pct = b.riesgo * 100;
  return (
    <div style={{ border: "1px solid " + C.border, borderRadius: 10, marginBottom: 10, background: "#fff" }}>
      <div onClick={() => setOpen(!open)} style={{ padding: "12px 14px", cursor: "pointer", display: "flex", gap: 12, alignItems: "center" }}>
        <div style={{ width: 30, height: 30, borderRadius: 8, background: light, color: color, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'JetBrains Mono',monospace", fontWeight: 700 }}>{b.id}</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 14, fontWeight: 600 }}>{b.nombre} <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11, color: C.muted }}>· peso {b.peso}</span></div>
          <div style={{ height: 7, background: C.bar, borderRadius: 4, marginTop: 6, overflow: "hidden" }}>
            <div style={{ height: "100%", width: pct + "%", background: pct > 65 ? C.red : pct > 40 ? C.amber : C.green, transition: "width .9s ease" }} />
          </div>
        </div>
        <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 13, fontWeight: 700, minWidth: 46, textAlign: "right" }}>{pct.toFixed(0)}%</div>
        <div style={{ color: C.muted, fontSize: 12 }}>{open ? "▲" : "▼"}</div>
      </div>
      {open && (
        <div style={{ padding: "0 14px 12px", borderTop: "1px solid " + C.border }}>
          {b.ind.map((i) => (
            <div key={i.k} style={{ padding: "9px 0", borderBottom: "1px dashed " + C.border }}>
              <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 4, flexWrap: "wrap" }}>
                <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11, fontWeight: 700, color: color }}>{i.k}</span>
                <span style={{ fontSize: 13, fontWeight: 600 }}>{i.t}</span>
                <RiskDot r={i.r} />
              </div>
              <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11.5, color: C.text, marginBottom: 3 }}>{i.v}</div>
              <div style={{ fontSize: 12.5, color: C.sec, lineHeight: 1.6 }}>{i.j}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Box({ children, accent }) {
  return <div style={{ background: C.card, border: "1px solid " + C.border, borderLeft: "4px solid " + (accent || C.border), borderRadius: 8, padding: 14, marginBottom: 12 }}>{children}</div>;
}

function TeamHead({ t }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 9, marginBottom: 12 }}>
      <div style={{ width: 10, height: 22, background: t.color, borderRadius: 2 }} />
      <div style={{ fontFamily: "'JetBrains Mono',monospace", fontWeight: 700, fontSize: 14, letterSpacing: 0.7 }}>{t.name}</div>
    </div>
  );
}

/* ============================================================
   APP
   ============================================================ */
export default function TeoremaDelEchado() {
  const [tab, setTab] = useState("indice");
  const tabs = [["indice", "Índice IE"], ["ventanas", "Ventanas de 15'"], ["tipos", "Tipología"], ["datos", "Detección en datos"], ["cal", "Calibración"]];

  return (
    <div style={{ fontFamily: "'DM Sans',system-ui,sans-serif", background: "#fff", color: C.text, padding: "18px 16px 40px" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=JetBrains+Mono:wght@400;700&display=swap');
        .tb{border:1px solid ${C.border};background:#fff;color:${C.sec};padding:7px 13px;border-radius:20px;font-size:12.5px;font-family:'JetBrains Mono',monospace;cursor:pointer}
        .tb.on{background:${C.text};color:#fff;border-color:${C.text}}
        table.t{width:100%;border-collapse:collapse;font-size:12.3px}
        table.t th{text-align:left;padding:8px;background:${C.card};color:${C.sec};font-family:'JetBrains Mono',monospace;font-size:11px;border-bottom:1px solid ${C.border}}
        table.t td{padding:8px;border-bottom:1px solid ${C.border};vertical-align:top;color:${C.sec}}
      `}</style>

      <div style={{ borderBottom: "2px solid " + C.text, paddingBottom: 14, marginBottom: 18 }}>
        <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11, letterSpacing: 1.4, color: C.muted, marginBottom: 8 }}>
          SAD · CAPA DTP · MÓDULO NUEVO · PROTOTIPO v0.1
        </div>
        <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 27, fontWeight: 700, letterSpacing: -0.5 }}>EL TEOREMA DEL ECHADO</div>
        <div style={{ fontSize: 13, color: C.sec, marginTop: 8, lineHeight: 1.7 }}>
          Probabilidad de repliegue no controlado, por equipo y por ventana de 15 minutos.<br />
          <span style={{ color: C.muted }}>Caso de estreno: Melgar vs FC Cajamarca · Liga 1 2026 Clausura F4 · Monumental UNSA · 09.08.2026</span>
        </div>
      </div>

      <Box accent={C.text}>
        <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11, color: C.muted, marginBottom: 6 }}>TESIS DEL MÓDULO</div>
        <div style={{ fontSize: 13.5, lineHeight: 1.75, color: C.sec }}>{TESIS}</div>
      </Box>

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", justifyContent: "center", background: C.card, border: "1px solid " + C.border, borderRadius: 12, padding: "18px 10px", marginBottom: 14 }}>
        <Gauge pct={IE.MEL.p} ie={IE.MEL.ie} color={MEL.color} label="FBC MELGAR" tipo={IE.MEL.tipo} ventana={IE.MEL.ventana} />
        <Gauge pct={IE.CAJ.p} ie={IE.CAJ.ie} color={CAJ.color} label="FC CAJAMARCA" tipo={IE.CAJ.tipo} ventana={IE.CAJ.ventana} />
      </div>

      <Box accent={C.violet}>
        <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11, color: C.muted, marginBottom: 8 }}>LA CADENA CONDICIONAL — EL NÚCLEO DEL TEOREMA</div>
        <div style={{ fontSize: 13, lineHeight: 1.7, color: C.sec, marginBottom: 12 }}>{CADENA}</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(240px,1fr))", gap: 12 }}>
          {[["MEL", MEL, IE.MEL], ["CAJ", CAJ, IE.CAJ]].map(([k, t, d]) => (
            <div key={k} style={{ background: "#fff", border: "1px solid " + C.border, borderRadius: 8, padding: 12 }}>
              <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11.5, fontWeight: 700, color: t.color, marginBottom: 8 }}>{t.short}</div>
              {[["P(echada)", d.p], ["P(fractura | echada)", d.frac], ["P(gol | fractura)", d.golFrac]].map(([lb, vl]) => (
                <div key={lb} style={{ marginBottom: 7 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "'JetBrains Mono',monospace", fontSize: 11, color: C.sec, marginBottom: 3 }}>
                    <span>{lb}</span><span style={{ fontWeight: 700 }}>{vl}%</span>
                  </div>
                  <div style={{ height: 6, background: C.bar, borderRadius: 4, overflow: "hidden" }}>
                    <div style={{ height: "100%", width: vl + "%", background: t.color, transition: "width .9s ease" }} />
                  </div>
                </div>
              ))}
              <div style={{ marginTop: 10, paddingTop: 9, borderTop: "1px dashed " + C.border, fontFamily: "'JetBrains Mono',monospace", fontSize: 12 }}>
                Riesgo compuesto de gol por echada: <b style={{ color: t.color, fontSize: 15 }}>{d.compuesto}%</b>
              </div>
            </div>
          ))}
        </div>
        <div style={{ marginTop: 12, fontSize: 12.5, color: C.sec, lineHeight: 1.7 }}>
          Lectura del par: Cajamarca tiene 82% de probabilidad de echarse y Melgar 38%, pero esa comparación no dice casi nada. Lo que decide el partido es la segunda columna: 58% contra 22% de partirse al hacerlo. Cajamarca no pierde por replegar — pierde porque su línea de fondo se armó en julio y sus cinco volantes no tienen ensayado el descenso conjunto.
        </div>
      </Box>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", margin: "18px 0" }}>
        {tabs.map(([k, l]) => <button key={k} className={"tb" + (tab === k ? " on" : "")} onClick={() => setTab(k)}>{l}</button>)}
      </div>

      {tab === "indice" && (
        <div>
          <Box accent={C.blue}>
            <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11.5, color: C.sec, lineHeight: 1.9 }}>
              IE = [ F×3 + C×2 + P×2 + S×1.5 ] / 8.5 × 10<br />
              <span style={{ color: C.muted }}>Cada bloque se puntúa 0-1 como fracción de riesgo. El físico pesa el doble que la estructura del partido porque es la causa más frecuente y la menos declarada.</span><br />
              <span style={{ color: C.muted }}>IE 0-3 → P 10-25% · IE 3-5 → 25-45% · IE 5-7 → 45-70% · IE 7-8.5 → 70-90%</span>
            </div>
          </Box>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(330px,1fr))", gap: 20 }}>
            {[["MEL", MEL, IE.MEL], ["CAJ", CAJ, IE.CAJ]].map(([k, t, d]) => (
              <div key={k}>
                <TeamHead t={t} />
                {d.bloques.map((b) => <BlockCard key={b.id} b={b} color={t.color} light={t.light} />)}
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === "ventanas" && (
        <div>
          {[["MEL", MEL, RIESGO.MEL, VENTANA_NOTA.MEL], ["CAJ", CAJ, RIESGO.CAJ, VENTANA_NOTA.CAJ]].map(([k, t, arr, nota]) => (
            <div key={k} style={{ marginBottom: 26 }}>
              <TeamHead t={t} />
              <div style={{ display: "flex", gap: 10, alignItems: "flex-end", height: 190, padding: "0 4px", borderBottom: "1px solid " + C.border, marginBottom: 8 }}>
                {arr.map((v, i) => (
                  <div key={i} style={{ flex: 1, textAlign: "center" }}>
                    <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 12, fontWeight: 700, marginBottom: 4, color: v > 65 ? C.red : v > 40 ? C.amber : C.sec }}>{v}%</div>
                    <div style={{ height: v * 1.5, background: v > 65 ? C.red : v > 40 ? C.amber : t.color, borderRadius: "5px 5px 0 0", transition: "height 1s ease", opacity: v > 65 ? 1 : 0.8 }} />
                  </div>
                ))}
              </div>
              <div style={{ display: "flex", gap: 10, padding: "0 4px", marginBottom: 10 }}>
                {VENTANAS.map((w) => <div key={w} style={{ flex: 1, textAlign: "center", fontFamily: "'JetBrains Mono',monospace", fontSize: 11, color: C.muted }}>{w}</div>)}
              </div>
              <Box accent={t.color}><div style={{ fontSize: 12.8, lineHeight: 1.7, color: C.sec }}>{nota}</div></Box>
            </div>
          ))}
          <Box accent={C.amber}>
            <div style={{ fontSize: 12.8, lineHeight: 1.7 }}>
              <b>Regla del minuto 60-65.</b> Es el punto donde la echada física se vuelve observable, no donde empieza. La primera señal es la caída de duelos de segunda pelota, que suele adelantarse 8-10 minutos a la caída de la línea. Quien mira la altura de la defensa llega tarde; quien mira el segundo balón llega a tiempo.
            </div>
          </Box>
        </div>
      )}

      {tab === "tipos" && (
        <div>
          {TIPOS.map((x) => (
            <div key={x.cod} style={{ border: "1px solid " + C.border, borderLeft: "4px solid " + x.color, borderRadius: 8, padding: 15, marginBottom: 12 }}>
              <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap", marginBottom: 8 }}>
                <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 12, fontWeight: 700, color: x.color }}>{x.cod}</span>
                <span style={{ fontSize: 14, fontWeight: 600 }}>{x.n}</span>
              </div>
              <div style={{ fontSize: 13, color: C.sec, lineHeight: 1.7, marginBottom: 9 }}>{x.def}</div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 12 }}>
                <div><div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10.5, color: C.muted, marginBottom: 3 }}>SEÑAL OBSERVABLE</div><div style={{ fontSize: 12.5, color: C.sec, lineHeight: 1.6 }}>{x.senal}</div></div>
                <div><div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10.5, color: C.muted, marginBottom: 3 }}>CUÁNDO FALLA EL DIAGNÓSTICO</div><div style={{ fontSize: 12.5, color: C.sec, lineHeight: 1.6 }}>{x.falla}</div></div>
                <div><div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10.5, color: C.muted, marginBottom: 3 }}>CONTRAMEDIDA</div><div style={{ fontSize: 12.5, color: C.sec, lineHeight: 1.6 }}>{x.contra}</div></div>
              </div>
            </div>
          ))}
          <Box accent={C.sec}>
            <div style={{ fontSize: 12.8, lineHeight: 1.7 }}>
              <b>Nota de vocabulario.</b> El módulo separa a propósito "plantar un bloque bajo" de "echarse". El primero es un plan ejecutado; el segundo es un retroceso que el equipo no controla. En el uso coloquial la palabra es peyorativa y el TDE respeta esa carga: si el repliegue está entrenado y sostenido, el output correcto no es una echada, es un bloque bajo estructural — y ahí el módulo debe reportar riesgo bajo aunque la altura de la línea sea idéntica.
            </div>
          </Box>
        </div>
      )}

      {tab === "datos" && (
        <div>
          <table className="t">
            <thead><tr><th>Métrica</th><th>Unidad</th><th>Umbral de disparo</th><th>Qué lee realmente</th></tr></thead>
            <tbody>
              {METRICAS.map((m) => (
                <tr key={m.m}>
                  <td style={{ fontWeight: 600, color: C.text }}>{m.m}</td>
                  <td style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11 }}>{m.u}</td>
                  <td>{m.umbral}</td>
                  <td>{m.lee}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ height: 14 }} />
          <Box accent={C.red}>
            <div style={{ fontSize: 12.8, lineHeight: 1.7 }}>
              <b>Limitación honesta del prototipo.</b> Ninguna de estas métricas está disponible en tiempo real para Liga 1 Perú en fuentes abiertas. Con datos públicos el TDE opera con proxies gruesos: minuto de los cambios, quién los hace y por quién, zona donde se cometen las faltas, y el reparto de córners y remates por tiempo. El módulo se declara pre-partido y se valida por observación cualitativa hasta que haya tracking. Un IE es una hipótesis fechada, no una medición.
            </div>
          </Box>
        </div>
      )}

      {tab === "cal" && (
        <div>
          <table className="t">
            <thead><tr><th>Caso</th><th>IE estimado</th><th>Qué pasó</th><th>Qué calibra</th></tr></thead>
            <tbody>
              {CASOS.map((c) => (
                <tr key={c.p}>
                  <td style={{ fontWeight: 600, color: C.text }}>{c.p}</td>
                  <td style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11 }}>{c.ie}</td>
                  <td>{c.real}</td>
                  <td>{c.lec}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ height: 14 }} />
          <Box accent={C.green}>
            <div style={{ fontSize: 12.8, lineHeight: 1.7 }}>
              <b>Qué hace falta para pasar de v0.1 a v1.0.</b> Ocho a diez casos con el IE declarado antes del partido y el minuto real de la transición anotado después. Sin eso, los pesos de los bloques (3 / 2 / 2 / 1.5) son una intuición razonada, no un ajuste. La segunda prioridad es aislar P(fractura|echada), que hoy se estima a mano desde C1-C2-C3 y es la variable con más poder predictivo del módulo.
            </div>
          </Box>
        </div>
      )}

      <div style={{ marginTop: 26, paddingTop: 14, borderTop: "1px solid " + C.border, fontFamily: "'JetBrains Mono',monospace", fontSize: 10.5, color: C.muted, lineHeight: 1.8 }}>
        SAD · El Teorema del Echado v0.1 (prototipo) · Módulo de la capa DTP, complementa G-BLOQUE y COLAPSO EN CASCADA del EFE v1.5.<br />
        Base científica: Bradley et al. 2009 (degradación de sprint), Mohr et al. 2003 (tiempo de reacción y fatiga), Baumeister et al. 1998 (agotamiento del autocontrol), Lago-Peñas y Gómez-López 2014 (peso del primer gol), Seligman 1972 (indefensión aprendida), Filho 2021 (resiliencia colectiva).<br />
        Anti-hindsight: IE declarado antes del inicio del partido. Mercados no aplicables: el módulo describe mecanismos, no recomienda.
      </div>
    </div>
  );
}
