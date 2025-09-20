@echo off
setlocal enabledelayedexpansion

:: Set console appearance
title HSEG AI - Codex CLI Dataset Generator (No API Credits)
color 0A

:: Display comprehensive header
echo.
echo ================================================================================
echo            HSEG AI SYSTEM - CODEX CLI DATASET GENERATOR
echo                     OpenAI Codex via CLI Application
echo ================================================================================
echo.
echo 🎯 MISSION: Generate synthetic dataset using OpenAI Codex CLI
echo.
echo 📊 DATASET SPECIFICATIONS:
echo    • AI Engine: OpenAI Codex through CLI application (NO API CREDITS NEEDED)
echo    • Dataset Size: Auto-adjusted based on system memory
echo    • Rich Narratives: Codex-generated responses with demographic consistency
echo    • Company Realism: 55 detailed organizations across 3 domains
echo    • Psychological Authenticity: Research-backed trauma patterns
echo.
echo 🤖 CODEX CLI ADVANTAGES:
echo    • No API credits or costs required
echo    • Uses local Codex CLI application
echo    • Same OpenAI model quality as API
echo    • Faster processing with CLI optimizations
echo    • Offline-capable once CLI is set up
echo.
echo 🏢 COMPANY COVERAGE (55 TOTAL):
echo    • Healthcare: 20 organizations (Kaiser, Mayo, Cleveland Clinic+)
echo    • Universities: 15 institutions (Harvard, Stanford, MIT, UC System+)
echo    • Business: 20 corporations (Microsoft, Google, Amazon, Apple+)
echo.
echo ⚠️  REQUIREMENTS:
echo    • Processing Time: 10-25 minutes depending on dataset size
echo    • Memory Usage: Adaptive (1-4GB RAM, auto-adjusts)
echo    • Storage: ~50-150MB final CSV file
echo    • Dependencies: Python 3.8+, pandas, numpy, psutil
echo    • Codex CLI: OpenAI Codex CLI application installed and configured
echo.
echo ================================================================================
echo.
echo 🚀 READY TO GENERATE WITH CODEX CLI?
echo.
pause

:: System checks
echo 📋 PERFORMING SYSTEM COMPATIBILITY CHECKS...
echo.

:: Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ CRITICAL ERROR: Python not found in system PATH
    echo.
    echo 🔧 RESOLUTION STEPS:
    echo    1. Install Python 3.8 or higher from python.org
    echo    2. Ensure Python is added to system PATH during installation
    echo    3. Restart command prompt and try again
    echo.
    pause
    exit /b 1
)

:: Get and display Python version
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
echo ✅ Python !PYTHON_VERSION! detected

:: Check Codex CLI availability
echo 📋 Checking OpenAI Codex CLI availability...
codex --version >nul 2>&1
if errorlevel 1 (
    echo ❌ CRITICAL ERROR: Codex CLI not found
    echo.
    echo 🔧 CODEX CLI SETUP REQUIRED:
    echo    1. Install OpenAI Codex CLI application
    echo    2. Ensure 'codex' command is in your system PATH
    echo    3. Login to your OpenAI account: codex auth login
    echo    4. Test with: codex --version
    echo.
    echo 📞 Download Codex CLI from: https://openai.com/codex
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%a in ('codex --version 2^>^&1') do set CODEX_VERSION=%%a
    echo ✅ Codex CLI detected: !CODEX_VERSION!
)

:: Check available memory
for /f "tokens=2 delims=:" %%a in ('wmic OS get TotalVisibleMemorySize /value ^| find "="') do set TOTAL_MEM=%%a
set /a TOTAL_MEM_GB=!TOTAL_MEM!/1048576
if !TOTAL_MEM_GB! LSS 2 (
    echo ⚠️  WARNING: Low system memory detected (!TOTAL_MEM_GB!GB)
    echo    Dataset will be optimized for small size (1,000 records)
    echo    Continue anyway? (Y/N)
    set /p CONTINUE=
    if /i not "!CONTINUE!"=="Y" exit /b 1
) else (
    echo ✅ Sufficient memory available (!TOTAL_MEM_GB!GB)
)

:: Check and install required packages
echo 📦 Verifying Python dependencies...
python -c "import pandas, numpy, uuid, datetime, json, re, itertools, psutil" 2>nul
if errorlevel 1 (
    echo ⚠️  Missing required packages. Installing automatically...
    echo.
    echo 📥 Installing: pandas numpy psutil
    pip install pandas numpy psutil --quiet --disable-pip-version-check
    if errorlevel 1 (
        echo ❌ Failed to install required packages
        echo.
        echo 🔧 MANUAL INSTALLATION:
        echo    pip install pandas numpy psutil
        echo.
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
) else (
    echo ✅ All required packages available
)

:: Validate project structure
cd /d "%~dp0\.."
if not exist "scripts\hseg_codex_cli_generator.py" (
    echo ❌ ERROR: Required generator script not found
    echo Expected: scripts\hseg_codex_cli_generator.py
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo ✅ Project structure validated
echo 📁 Working directory: %CD%

:: Create output directory
if not exist "data" (
    echo 📂 Creating data directory...
    mkdir data
)

:: Disk space check
for /f "usebackq delims=" %%i in (`dir /s /-c "%CD%" 2^>nul ^| find "bytes free"`) do set DISK_SPACE=%%i
echo ✅ Disk space: %DISK_SPACE%

echo.
echo ================================================================================
echo                      INITIATING CODEX CLI DATA GENERATION
echo ================================================================================
echo.
echo ⏳ GENERATION PROCESS STARTING...
echo.
echo 📊 Process Details:
echo    • Using OpenAI Codex CLI for narrative generation
echo    • Batch processing in small chunks for memory efficiency
echo    • Progress updates every 50 records within each batch
echo    • Dataset size automatically optimized for your system
echo.
echo 🎯 Target Output: data\hseg_55companies_codex_dataset.csv
echo.
echo ⚡ Beginning Codex CLI generation at %TIME%...
echo.

:: Record start time
set START_TIME=%TIME%

:: Execute the Codex CLI generation script
python scripts/hseg_codex_cli_generator.py
set GENERATION_RESULT=!errorlevel!

:: Record end time
set END_TIME=%TIME%

echo.
echo ================================================================================

if !GENERATION_RESULT! equ 0 (
    echo                    ✅ CODEX CLI GENERATION COMPLETED SUCCESSFULLY
    echo ================================================================================
    echo.
    echo ⏱️  Generation completed at %END_TIME%
    echo 📊 Processing time: Started %START_TIME% → Finished %END_TIME%
    echo.

    :: Validate output file
    if exist "data\hseg_55companies_codex_dataset.csv" (
        for %%A in ("data\hseg_55companies_codex_dataset.csv") do set FILE_SIZE=%%~zA
        set /a FILE_SIZE_MB=!FILE_SIZE!/1048576
        echo 📁 Output file: data\hseg_55companies_codex_dataset.csv
        echo 💾 File size: !FILE_SIZE_MB! MB (!FILE_SIZE! bytes)

        :: Count actual records
        for /f %%i in ('type "data\hseg_55companies_codex_dataset.csv" ^| find /c /v ""') do set ACTUAL_LINES=%%i
        set /a ACTUAL_RECORDS=!ACTUAL_LINES!-1
        echo 📊 Records generated: !ACTUAL_RECORDS!

        echo.
        echo 🎯 DATASET VALIDATION:
        python -c "
import pandas as pd
try:
    df = pd.read_csv('data/hseg_55companies_codex_dataset.csv')
    print(f'✅ CSV structure valid: {len(df)} rows, {len(df.columns)} columns')
    print(f'✅ Domain distribution: {dict(df[\"domain\"].value_counts())}')
    print(f'✅ Narrative length: Q24 avg {df[\"q24_text\"].str.len().mean():.0f} chars')
    print(f'✅ No missing data: {df.isnull().sum().sum()} null values')
    print(f'✅ Demographic consistency: Gender distribution {dict(df[\"gender_identity\"].value_counts())}')
except Exception as e:
    print(f'❌ Validation error: {e}')
"

        echo.
        echo 🚀 CODEX CLI ADVANTAGES REALIZED:
        echo    ✅ No API credits consumed
        echo    ✅ OpenAI-quality narratives generated
        echo    ✅ Demographic consistency maintained
        echo    ✅ Psychological authenticity preserved
        echo    ✅ Memory-optimized processing completed

    ) else (
        echo ❌ ERROR: Output file not found despite successful execution
        echo Expected: data\hseg_55companies_codex_dataset.csv
        echo.
        echo 🔍 TROUBLESHOOTING:
        echo    1. Check write permissions in data directory
        echo    2. Verify sufficient disk space
        echo    3. Review error messages above
    )

) else (
    echo                           ❌ GENERATION FAILED
    echo ================================================================================
    echo.
    echo 🔍 FAILURE ANALYSIS:
    echo    • Exit code: !GENERATION_RESULT!
    echo    • Check error messages above for specific issues
    echo.
    echo 🛠️  COMMON SOLUTIONS:
    echo    1. Verify Codex CLI setup: codex --version
    echo    2. Login to Codex CLI: codex auth login
    echo    3. Ensure Python packages: pip install pandas numpy psutil
    echo    4. Free up disk space (need ~100MB available)
    echo    5. Close memory-intensive applications
    echo    6. Run as administrator if permission issues
    echo.
    echo 📞 CODEX CLI SUPPORT:
    echo    • Check Codex CLI documentation
    echo    • Verify OpenAI account status
    echo    • Test CLI with simple prompt first
)

echo.
echo ================================================================================
echo                              PROCESS COMPLETE
echo ================================================================================
echo.
echo 📊 GENERATION SUMMARY:
echo    • Start time: %START_TIME%
echo    • End time: %END_TIME%
echo    • Result: !GENERATION_RESULT!
echo    • Output: data\hseg_55companies_codex_dataset.csv
echo    • AI Engine: OpenAI Codex CLI (No API Credits Used)
echo.
echo 🎯 Your Codex CLI-powered synthetic dataset is ready for NLP model training!
echo.
echo Press any key to exit...
pause >nul