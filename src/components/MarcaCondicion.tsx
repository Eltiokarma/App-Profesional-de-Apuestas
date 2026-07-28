// P6 — distintivo de condición: RELLENO = local, CONTORNO = visitante,
// siempre en el color del equipo (o del lado, donde la pantalla ya usa
// acento/rojo por lado). La forma lleva la condición y el color la identidad:
// no compiten, y la misma marca sirve en el marcador, las tablas de cuotas,
// el H2H y las alineaciones. Sin ella, la condición se infiere del orden
// (izquierda = local) — y eso se rompe en cuanto una tabla se ordena por
// cuota, por K o por hora.
export function MarcaCondicion({ cond, color, size = 15 }: { cond: 'L' | 'V'; color: string; size?: number }) {
  const esLocal = cond === 'L'
  return (
    <span
      title={esLocal ? 'Local' : 'Visitante'}
      style={{
        width: size,
        height: size,
        borderRadius: Math.max(3, Math.round(size * 0.3)),
        background: esLocal ? color : 'transparent',
        border: esLocal ? undefined : `1.5px solid ${color}`,
        color: esLocal ? '#fff' : color,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        font: `700 ${Math.max(7, Math.round(size * 0.56))}px var(--mono)`,
        boxSizing: 'border-box',
        flexShrink: 0,
        lineHeight: 1,
      }}
    >
      {cond}
    </span>
  )
}
