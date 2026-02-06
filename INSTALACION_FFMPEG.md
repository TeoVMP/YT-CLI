# Instalación de FFmpeg

FFmpeg es necesario para convertir audio a MP3 y combinar video+audio en algunos casos.

## Windows

### Opción 1: Usando Chocolatey (Recomendado)

1. Instala Chocolatey si no lo tienes: https://chocolatey.org/install
2. Abre PowerShell como Administrador
3. Ejecuta:
```powershell
choco install ffmpeg
```

### Opción 2: Descarga Manual

1. Ve a https://www.gyan.dev/ffmpeg/builds/
2. Descarga "ffmpeg-release-essentials.zip"
3. Extrae el archivo ZIP
4. Copia la carpeta `ffmpeg` a `C:\ffmpeg`
5. Agrega `C:\ffmpeg\bin` al PATH:
   - Presiona `Win + R`, escribe `sysdm.cpl` y presiona Enter
   - Ve a la pestaña "Opciones avanzadas"
   - Click en "Variables de entorno"
   - En "Variables del sistema", busca "Path" y click en "Editar"
   - Click en "Nuevo" y agrega `C:\ffmpeg\bin`
   - Click "Aceptar" en todas las ventanas
6. Reinicia PowerShell/Terminal

### Verificar Instalación

Abre una nueva terminal y ejecuta:
```bash
ffmpeg -version
```

Si muestra información de versión, FFmpeg está instalado correctamente.

## Linux

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install ffmpeg
```

### Fedora/RHEL:
```bash
sudo dnf install ffmpeg
```

### Arch Linux:
```bash
sudo pacman -S ffmpeg
```

## macOS

### Usando Homebrew:
```bash
brew install ffmpeg
```

## Nota Importante

- **Para descargar solo video MP4**: FFmpeg NO es estrictamente necesario si el video ya está en formato MP4
- **Para convertir a MP3**: FFmpeg ES necesario
- **Para combinar video+audio de alta calidad**: FFmpeg ES necesario

Si no tienes FFmpeg instalado, el bot intentará descargar el mejor formato disponible sin necesidad de conversión.
