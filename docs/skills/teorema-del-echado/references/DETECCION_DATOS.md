# Detección en datos

## Métricas de primer nivel (requieren tracking)

| Métrica | Unidad | Umbral de disparo | Qué lee realmente |
|---------|--------|-------------------|-------------------|
| Altura media de la línea defensiva | metros desde arco propio | Caída sostenida de 8+ m respecto al promedio del propio partido | Confirma el repliegue, no su causa |
| **Distancia línea de fondo – línea de volantes** | metros | Más de 18-20 m sostenidos | **La métrica clave: separa echada de FRACTURA** |
| PPDA | pases rivales permitidos por acción defensiva | Sube 40%+ respecto a su propia primera media hora | Si sube sin caída física → `ECHADA-SUP`; con caída física → `ECHADA-FIS` |
| % de pases en tercio propio | % | Por encima de 55% en una ventana de 15' | El equipo ya no puede salir, solo despejar |
| Field tilt | % de posesión en tercio rival | Por debajo de 30% | Territorialidad cedida; sirve para fechar el minuto de la transición |
| xG concedido por ventanas de 15' | xG | Ventana final con xG superior a la suma de las tres primeras | Resultado de la fractura, no de la echada. Métrica de validación |
| Duelos de segunda pelota ganados | % | Caída por debajo de 40% | **Primera señal de todas**: aparece antes de que la línea baje |

Orden de lectura recomendado: segunda pelota → distancia entre líneas → PPDA → altura de línea → field tilt → xG por ventana. Quien mira la altura de la defensa llega tarde; quien mira el segundo balón llega a tiempo.

## Proxies con datos públicos

En Liga 1 Perú, Liga MX y buena parte de Sudamérica no hay tracking abierto en tiempo real. El módulo opera con proxies gruesos y **debe declararlos como tales**:

| Proxy | Cómo se lee | Tipo que sugiere |
|-------|-------------|------------------|
| Minuto y perfil de los cambios | Doble cambio defensivo entre el 60 y el 70 | `ECHADA-VOL` |
| Quién sale y por quién | Sale un extremo, entra un central o un volante de marca | `ECHADA-VOL` o `ECHADA-NUM` |
| Zona donde se cometen las faltas | Faltas concentradas en tercio propio en la segunda mitad | Repliegue confirmado |
| Reparto de córners por tiempo | Todos los córners del rival en los últimos 30' | Territorialidad cedida |
| Reparto de remates por tiempo | Remates concedidos que se disparan tras un cambio | Fractura probable |
| Amarillas acumuladas por franja | Tres amarillas propias en 15' | Equipo desbordado, no solo replegado |
| Posesión final vs posesión al descanso | Posesión propia que **sube** mientras el equipo defiende peor | Alerta: posesión en tercio propio, no control |

## Proxy negativo — firma de BLOQUE SOSTENIDO *(v0.1.3)*

Sirve para **descartar** la echada, no para confirmarla. Las tres señales tienen que darse juntas; con dos de tres no alcanza:

1. **Cero remates concedidos desde el borde del área** en el tramo 60-90.
2. **Remates rivales todos de media distancia y sin rebote.**
3. **El rival acumula posesión sin aumentar córners** en la última media hora.

Documentado en TDE-011: 67 minutos administrando un 1-0 sin conceder un solo remate desde el borde del área. Un equipo que se echó mal concede llegadas al borde; uno que sostiene el bloque concede tiros de afuera.

**Usar esto como falsador explícito del pronóstico, no solo como observación de cierre.** Si el IE declarado era alto y aparece la firma completa de bloque sostenido, el pronóstico falló y hay que registrarlo aunque el resultado del partido haya sido el esperado.

## Proxy de la vía 2 — firma de SOBREEXPOSICIÓN

El espejo del anterior, para la vía del ISE:

| Proxy | Cómo se lee |
|-------|-------------|
| Remates propios que suben mientras el rival deja de tener la pelota | El equipo domina y a la vez se expone |
| Contragolpes rivales concedidos que crecen por franja sin que caiga la posesión propia | Territorialidad ganada, retaguardia vacía |
| Faltas tácticas propias en el círculo central en el tramo 75-90 | El equipo ya sabe que está expuesto y frena con falta |
| Los dos laterales propios por delante de la línea media de forma sostenida | SOB2 confirmado en cancha |

**Trampa documentada.** La posesión mayoritaria no descarta la echada. Caso Cajamarca 0-2 Sport Huancayo (01.08.2026): 53% de posesión propia y 0-1 al minuto 13. Tener la pelota en el tercio propio es la forma más engañosa de estar replegado.

## Fuentes útiles

- **Liga 1 Perú**: RPP, Depor, El Comercio, Líbero, Futbolperuano, Diario Correo (onces confirmados y minutos de cambio). Sofascore y FotMob para posesión, remates y córners por tiempo.
- `fetch_sports_data` sirve para EPL, LaLiga y Serie A; **no** para Liga 1 Perú ni Liga MX.
- Para ligas con datos abiertos (EPL, big five), buscar PPDA y field tilt antes de recurrir a proxies.

## Regla de honestidad del output

Todo IE debe indicar con qué nivel de dato se calculó:

- **Nivel A** — tracking o PPDA/field tilt disponibles
- **Nivel B** — proxies públicos (minutos de cambio, faltas, córners y remates por franja)
- **Nivel C** — solo contexto (rotación, calendario, banco, D3) sin datos del partido en curso

La mayoría de los casos de Liga 1 serán **Nivel C pre-partido** y **Nivel B post-partido**. Decirlo en el dashboard, no esconderlo.
