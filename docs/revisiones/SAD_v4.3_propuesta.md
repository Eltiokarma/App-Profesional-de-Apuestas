# Propuesta de revisión · `sad-analysis` v4.2 → v4.3

**Estado:** APROBADA por el usuario (30/10/2026: «tenemos que hacer la
actualización de 1 skill, SAD analysis»). Redactada en
`docs/skills/sad-analysis/SKILL.md` (v4.3). En la app: `CORTE_VERSION` con la
v4.3 y `SUBIDA_VERSION` provisoria; no hay código nuevo. Falta que el usuario
suba el zip.

## Por qué una revisión de un solo punto

La v4.2 decía, en el paso 3.5, «la app **no tiene modelo de goles**: el
marcador exacto es lectura». Desde el 30/10/2026 lo tiene: `golesAcotados`
(`backend/analisis/goles.py`, REVENTON §17), calibrado con 50.823 partidos del
padrón. Dejar la frase vieja hacía que el skill contradijera al prompt de la
corrida, que ya pide el marcador dentro del acotado.

**No es la revisión de las lecciones.** Las lecciones de los partes del
28-30/10 (escritos con la v4.2) siguen abiertas para la revisión siguiente,
junto con EFE, DTP y TDE. Por eso el botón «Cerrar las anteriores a v4.3» **no
se pulsa** para `sad-analysis`.

## Lo medido (REVENTON §17, 30/10/2026)

- El cruce de lo que mete uno en su condición contra lo que concede el otro
  en la suya acota los goles: −0,051 de log-loss sobre la frecuencia propia.
  Las constantes de goles suman poco encima (−0,002).
- Prueba con corte temporal: el **intervalo de dos goles acierta 64 %**
  (promete 65 %: calibrado); el **marcador acotado** (cuatro marcadores),
  **41 %**. El intervalo a mano («la ventana de dos goles más repetida») acertó
  61 %.
- **Contra el mercado** de más/menos 2,5 y de ambos marcan: sin ventaja (el
  +17 % de «ambos marcan» era un artefacto de las cuotas incoherentes de
  Marathonbet).
- **El marcador no se repite** más que por azar (razón 1,01; el empate algo
  más, 1,016).

## Los tres cambios

1. **Paso 3.5:** el marcador sale de los goles acotados. El declarado va
   dentro del marcador acotado; sacarlo pide un hecho de ESTE partido que el
   modelo no ve, escrito con su fuente. Sin modelo o sin historia
   (`sinDato`), vuelve la regla de la v4.2 (lectura sin porcentaje inventado).
   Los números no se copian al parte.
2. **No mueve el 1X2** ni es señal de apuesta (3.5 y prohibiciones). Que los
   cuatro marcadores acotados den el mismo ganador no está medido como señal:
   Aprendizaje (`acreditables.golesAcotados`) lo mide antes.
3. **6-C:** si el marcador declarado sale del acotado, el falsador nombra la
   vía de gol que lo saca. Dentro del acotado no hace falta: el veredicto mide
   el intervalo solo. Auditoría 2, pregunta 3, lo revisa.

Además, la tabla de leyes, la de suspendidos, «Insumos» y las prohibiciones
distinguen el modelo de la app (con motor, λ en goles) del Poisson v6 con μ,
que sigue suspendido.
