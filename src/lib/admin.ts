// «Modo administrador» (deuda 1): la web lleva en el bundle SOLO el token de
// lectura (VITE_API_KEY = SAD_TOKEN_WEB). Lo que escribe o gasta —generar un
// EFE, refrescar una liga, cuarentenas, lecciones, el once a mano— necesita la
// llave maestra, y esa NO viaja en el código: la pega el dueño una vez y queda
// solo en SU navegador (localStorage), donde se puede borrar con el mismo botón.
const CLAVE = 'sad.llaveAdmin'

export function llaveAdmin(): string {
  try {
    return localStorage.getItem(CLAVE) ?? ''
  } catch {
    return '' // navegación privada o almacenamiento bloqueado: modo lectura
  }
}

export function guardarLlaveAdmin(valor: string): boolean {
  try {
    if (valor) localStorage.setItem(CLAVE, valor)
    else localStorage.removeItem(CLAVE)
    return true
  } catch {
    return false
  }
}
