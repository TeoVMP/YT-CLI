# 📤 Instrucciones para Subir el Proyecto a GitHub

## Paso 1: Crear el Repositorio en GitHub

### Opción A: Desde la Web (Recomendado)

1. Ve a https://github.com/new
2. **Repository name**: `YTLikesBot`
3. **Description**: `Bot completo para interactuar con YouTube: comentar, descargar videos/audio, ver estadísticas y más`
4. **Visibility**: 
   - ✅ **Public** (recomendado para proyectos open source)
   - O **Private** (si prefieres mantenerlo privado)
5. **NO marques**:
   - ❌ Add a README file (ya tenemos uno)
   - ❌ Add .gitignore (ya tenemos uno)
   - ❌ Choose a license (puedes agregarlo después)
6. Click en **"Create repository"**

### Opción B: Usando GitHub CLI (si lo tienes instalado)

```bash
gh repo create YTLikesBot --public --description "Bot completo para interactuar con YouTube: comentar, descargar videos/audio, ver estadísticas y más"
```

## Paso 2: Subir el Código

Una vez creado el repositorio, ejecuta estos comandos:

```bash
# Verificar que el remoto esté configurado correctamente
git remote -v

# Si no está configurado o está mal, configúralo:
git remote remove origin  # Si existe pero está mal
git remote add origin https://github.com/TeoVMP/YTLikesBot.git

# Asegurarte de estar en la rama main
git branch -M main

# Subir todo el código
git push -u origin main
```

## Paso 3: Verificar

Ve a https://github.com/TeoVMP/YTLikesBot y verifica que todos los archivos estén ahí.

## ⚠️ Importante: Archivos que NO se suben

Gracias al `.gitignore`, estos archivos **NO** se subirán (y está bien así):

- ✅ `.env` - Credenciales OAuth2
- ✅ `token.json` - Tokens de autenticación
- ✅ `downloads/` - Videos y audios descargados
- ✅ `*.mp4`, `*.mp3` - Archivos multimedia
- ✅ `__pycache__/` - Archivos Python compilados
- ✅ `*.log` - Logs

## 📝 Después de subir

1. **Agregar descripción al repositorio**: Ve a Settings > General
2. **Agregar topics**: `python`, `youtube-api`, `oauth2`, `automation`, `cli`, `youtube-bot`
3. **Agregar README badges** (opcional): Puedes agregar badges de Python, licencia, etc.
4. **Configurar GitHub Pages** (opcional): Si quieres documentación web

## 🔐 Si necesitas autenticación

Si GitHub te pide autenticación al hacer push:

### Opción 1: Personal Access Token (Recomendado)

1. Ve a https://github.com/settings/tokens
2. Click en "Generate new token (classic)"
3. Selecciona scopes: `repo` (todos los permisos de repositorio)
4. Copia el token
5. Cuando Git pida contraseña, usa el token en lugar de tu contraseña

### Opción 2: SSH (Más seguro a largo plazo)

```bash
# Generar clave SSH (si no tienes una)
ssh-keygen -t ed25519 -C "tu_email@ejemplo.com"

# Agregar la clave a ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copiar la clave pública
cat ~/.ssh/id_ed25519.pub

# Agregar la clave en GitHub: https://github.com/settings/keys
# Luego cambiar el remote a SSH:
git remote set-url origin git@github.com:TeoVMP/YTLikesBot.git
```

## 🚀 Comandos Rápidos

Si ya creaste el repositorio, ejecuta esto:

```bash
git remote add origin https://github.com/TeoVMP/YTLikesBot.git
git branch -M main
git push -u origin main
```
