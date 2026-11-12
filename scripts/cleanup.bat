@echo off
chcp 1251 >nul
title Очистка пользовательских временных файлов и кешей
echo ============================================
echo    ОЧИСТКА ПОЛЬЗОВАТЕЛЬСКИХ ДАННЫХ
echo    (без прав администратора)
echo ============================================
echo.

echo [1/12] Очистка временных файлов пользователя...
del /q /s "%TEMP%\*" 2>nul
for /d %%i in ("%TEMP%\*") do rd /s /q "%%i" 2>nul
echo       Готово.

echo [2/12] Очистка кеша Gradle...
if exist "%USERPROFILE%\.gradle\caches" (
    rd /s /q "%USERPROFILE%\.gradle\caches" 2>nul
    echo       Кеш Gradle очищен.
) else (
    echo       Кеш Gradle не найден.
)

echo [3/12] Очистка обертки Gradle...
if exist "%USERPROFILE%\.gradle\wrapper\dists" (
    rd /s /q "%USERPROFILE%\.gradle\wrapper\dists" 2>nul
    echo       Дистрибутивы Gradle очищены.
) else (
    echo       Дистрибутивы Gradle не найдены.
)

echo [4/12] Очистка кеша Android эмуляторов...
if exist "%USERPROFILE%\.android\avd" (
    for /d %%i in ("%USERPROFILE%\.android\avd\*") do (
        echo       Очистка: %%~ni
        if exist "%%i\snapshots" rd /s /q "%%i\snapshots" 2>nul
        if exist "%%i\*.lock" del /q "%%i\*.lock" 2>nul
    )
    echo       Кеш эмуляторов очищен.
) else (
    echo       Эмуляторы не найдены.
)

echo [5/12] Очистка кеша Android SDK...
if exist "%LOCALAPPDATA%\Android\Sdk\.temp" (
    rd /s /q "%LOCALAPPDATA%\Android\Sdk\.temp" 2>nul
    echo       Временные файлы SDK очищены.
)
if exist "%USERPROFILE%\.android\cache" (
    rd /s /q "%USERPROFILE%\.android\cache" 2>nul
    echo       Кеш Android очищен.
)

echo [6/12] Очистка кеша npm...
if exist "%LOCALAPPDATA%\npm-cache" (
    rd /s /q "%LOCALAPPDATA%\npm-cache" 2>nul
    echo       Кеш npm очищен.
) else (
    echo       Кеш npm не найден.
)

echo [7/12] Очистка кеша Yarn...
if exist "%LOCALAPPDATA%\Yarn\Cache" (
    rd /s /q "%LOCALAPPDATA%\Yarn\Cache" 2>nul
    echo       Кеш Yarn очищен.
) else (
    echo       Кеш Yarn не найден.
)

echo [8/12] Очистка кеша Maven...
if exist "%USERPROFILE%\.m2\repository" (
    rd /s /q "%USERPROFILE%\.m2\repository" 2>nul
    echo       Кеш Maven очищен.
) else (
    echo       Кеш Maven не найден.
)

echo [9/12] Очистка кеша IntelliJ IDEA...
if exist "%LOCALAPPDATA%\JetBrains" (
    for /d %%i in ("%LOCALAPPDATA%\JetBrains\*") do (
        if exist "%%i\caches" rd /s /q "%%i\caches" 2>nul
        if exist "%%i\index" rd /s /q "%%i\index" 2>nul
        if exist "%%i\LocalHistory" rd /s /q "%%i\LocalHistory" 2>nul
    )
    echo       Кеш IDE очищен.
) else (
    echo       Кеш IntelliJ не найден.
)

echo [10/12] Очистка кеша браузеров...
:: Chrome
if exist "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache" (
    rd /s /q "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache" 2>nul
    echo       Кеш Chrome очищен.
)
:: Edge
if exist "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache" (
    rd /s /q "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache" 2>nul
    echo       Кеш Edge очищен.
)
:: Firefox
if exist "%APPDATA%\Mozilla\Firefox\Profiles" (
    for /d %%i in ("%APPDATA%\Mozilla\Firefox\Profiles\*") do (
        if exist "%%i\cache2" rd /s /q "%%i\cache2" 2>nul
    )
    echo       Кеш Firefox очищен.
)

echo [11/12] Очистка кеша OpenCode...
if exist "%USERPROFILE%\.cache\opencode" (
    rd /s /q "%USERPROFILE%\.cache\opencode" 2>nul
    echo       Кеш OpenCode очищен.
) else (
    echo       Кеш OpenCode не найден.
)
if exist "%USERPROFILE%\.local\share\opencode" (
    rd /s /q "%USERPROFILE%\.local\share\opencode" 2>nul
    echo       Данные OpenCode очищены.
)
if exist "%USERPROFILE%\.local\share\opencode-backup" (
    rd /s /q "%USERPROFILE%\.local\share\opencode-backup" 2>nul
    echo       Бэкап OpenCode очищен.
)

echo [12/12] Очистка кеша KiloCode...
if exist "%USERPROFILE%\.cache\kilo" (
    rd /s /q "%USERPROFILE%\.cache\kilo" 2>nul
    echo       Кеш KiloCode очищен.
) else (
    echo       Кеш KiloCode не найден.
)
if exist "%USERPROFILE%\.local\share\kilo" (
    rd /s /q "%USERPROFILE%\.local\share\kilo" 2>nul
    echo       Данные KiloCode очищены.
)

echo.
echo ============================================
echo    ОЧИСТКА ЗАВЕРШЕНА!
echo ============================================
echo.

:: Подсчет освобожденного места
echo Освобождено место на диске.
echo Рекомендуется перезапустить приложения.

pause
