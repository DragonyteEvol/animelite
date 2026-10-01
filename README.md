# animelite (GUI)

Interfaz gráfica minimalista y fluida para buscar, explorar y ver anime. Usa el motor [animelite-cli](https://github.com/DragonyteEvol/animelite-cli) para buscar y resolver servidores con medición de latencia.

- **Modo claro/oscuro** con acento violeta → cian.
- **Búsqueda instantánea**, grilla de posters, vista de capítulos y lista de servidores ordenados por latencia.
- **Historial local** "Seguir viendo" (recordando el último capítulo de cada anime).
- **mpv en ventana aparte** — reproduce HLS/mp4 de forma estable.
- **Internacionalización** ES/EN con selector en la cabecera.

## Instalación

### Opción 1: ejecutar desde código (rápida)

1. Hacer doble clic en `instalar.bat` (o `python instalar.py` desde terminal).
2. Hacer doble clic en `app.bat` (o ejecutar `python -m app.main`).

### Opción 2: generar ejecutable (.exe)

1. Hacer doble clic en `instalar.bat` (crea `.venv`).
2. Hacer doble clic en `build.bat`.
3. Ejecutar `dist\animelite.exe`.

## Uso

1. Escribir el nombre del anime y pulsar `Enter`.
2. Seleccionar el resultado (tarjeta con póster).
3. Seleccionar un capítulo (chips).
4. La app abre automáticamente el mejor servidor en mpv (ventana aparte). Para elegir otro servidor, usar el botón `Servidores`.
5. Tras reproducir, el historial guarda el último capítulo.

## Atajos

- `Enter` — buscar
- `←` / `Esc` — volver atrás
- `q` — salir (mpv)

## Configuración

- **Tema e idioma** se guardan en `%APPDATA%\animelite\config.json`.
- **Historial** se guarda en `%APPDATA%\animelite\historial.json`.
- **mpv** se detecta con el mismo orden de prioridad: `MPV_PATH` > config > `PATH` > rutas habituales (compartido con el CLI).

## Requisitos

- Windows 10/11
- Python 3.10+
- mpv (solo para reproducir). Si no existe, se avisa con el comando para instalarlo (`winget install --id shinchiro.mpv -e`).

## Estructura

```
app/
  main.py        # Entrada
  ventana.py     # Orquestación + navegación
  vistas.py      # Vistas Inicio/Resultados/Detalle/Servidores
  tarjetas.py    # Tarjetas, rejilla, cache de posters
  motor.py       # Pipeline sobre animelite-engine
  worker.py      # Tareas asincronas (QThreadPool)
  historial.py   # Persistencia de "Seguir viendo"
  config.py      # Config persistente
  i18n.py        # Traducciones ES/EN
  tema.py        # Paletas claro/oscuro + QSS
  reproductor.py # Lanzamiento mpv externo
```