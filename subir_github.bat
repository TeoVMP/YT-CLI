@echo off
echo ========================================
echo  SUBIR PROYECTO A GITHUB
echo ========================================
echo.

echo Paso 1: Verificando estado de Git...
git status
echo.

echo Paso 2: Verificando remoto...
git remote -v
echo.

echo Paso 3: Configurando remoto a GitHub...
git remote add origin https://github.com/TeoVMP/YTLikesBot.git
if errorlevel 1 (
    echo El remoto ya existe, intentando actualizar...
    git remote set-url origin https://github.com/TeoVMP/YTLikesBot.git
)
echo.

echo Paso 4: Asegurando que estamos en la rama main...
git branch -M main
echo.

echo Paso 5: Intentando subir el codigo...
echo.
echo IMPORTANTE: Asegurate de haber creado el repositorio en GitHub primero!
echo Ve a: https://github.com/new
echo Nombre: YTLikesBot
echo.
pause

git push -u origin main

if errorlevel 1 (
    echo.
    echo ========================================
    echo  ERROR AL SUBIR
    echo ========================================
    echo.
    echo Posibles causas:
    echo 1. El repositorio no existe en GitHub
    echo 2. Problemas de autenticacion
    echo 3. El repositorio ya tiene contenido
    echo.
    echo Lee SUBIR_A_GITHUB.md para mas instrucciones
    echo.
) else (
    echo.
    echo ========================================
    echo  EXITO!
    echo ========================================
    echo.
    echo Tu proyecto esta en: https://github.com/TeoVMP/YTLikesBot
    echo.
)

pause
