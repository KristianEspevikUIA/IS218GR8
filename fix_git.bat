@echo off
REM ============================================================
REM  fix_git.bat — fiksar git-historikken for IS218GR8
REM
REM  KJØR DENNE: dobbeltklikk fila etter å ha LUKKA GitHub Desktop
REM  (Cmd+Q / Alt+F4 — ikkje berre minimer)
REM ============================================================

cd /d "%~dp0"

echo.
echo === IS218GR8 — fiksing av criss-cross merge bases ===
echo.

REM 1. Sjekk at GitHub Desktop er lukka (fjern lock om den finst)
if exist ".git\index.lock" (
    echo [INFO] Fjernar .git\index.lock (GitHub Desktop sin lås)
    del /f /q ".git\index.lock"
)
if exist ".git\objects\maintenance.lock" (
    echo [INFO] Fjernar .git\objects\maintenance.lock
    del /f /q ".git\objects\maintenance.lock"
)

REM 2. Vis status
echo.
echo === STEG 1/5: status ===
git status --short
echo.

REM 3. Commit alt som er endra
echo === STEG 2/5: commit alle endringar ===
git add -A
git commit -m "Mappeinnlevering: forbetra notebook-dokumentasjon (HVA/HVORDAN/KVIFOR), kort 2-siders mapperapport, oppdatert semesterrapport, oppdatert README" 2>nul
if errorlevel 1 (
    echo [INFO] Ingen nye endringar aa committe (eller commit feila — sjekk git status manuelt)
)
echo.

REM 4. Hent nyaste origin/main
echo === STEG 3/5: hent origin/main ===
git fetch origin main
if errorlevel 1 (
    echo [FEIL] Kunne ikkje hente origin/main. Sjekk internett-tilkopling og git-credentials.
    pause
    exit /b 1
)
echo.

REM 5. Merge origin/main inn i KristianReal
REM    Dette skaper EIN ny merge-commit som vert ny eintydig merge base.
echo === STEG 4/5: merge origin/main inn i KristianReal ===
git merge origin/main --no-ff -m "Merge origin/main: loys criss-cross merge base for PR"
if errorlevel 1 (
    echo.
    echo [VARSEL] Merge-konflikter funne!
    echo.
    echo Loys konfliktene manuelt:
    echo   1. Open VS Code: code .
    echo   2. Sjekk filene merka med "U" (unmerged) i Source Control
    echo   3. Vel "Accept Current" eller "Accept Incoming" pr. konflikt
    echo   4. Lagra, og kjor i terminalen:
    echo        git add -A
    echo        git commit
    echo   5. Kjor "git push origin KristianReal"
    pause
    exit /b 1
)
echo.

REM 6. Push
echo === STEG 5/5: push til origin/KristianReal ===
git push origin KristianReal
if errorlevel 1 (
    echo [FEIL] Push feila. Sjekk credentials. Du kan kjore "git push" manuelt.
    pause
    exit /b 1
)
echo.

REM 7. Verifiser at det no berre er EIN merge base
echo === VERIFISERING: merge bases ===
git merge-base --all origin/main HEAD
echo.

echo ============================================================
echo  FERDIG! Apne GitHub Desktop og klikk "Create Pull Request"
echo  paa nytt — den skal no fungere.
echo.
echo  Eller: ga til
echo    https://github.com/KristianEspevikUIA/IS218GR8/compare/main...KristianReal
echo  i nettlesaren.
echo ============================================================
echo.
pause
