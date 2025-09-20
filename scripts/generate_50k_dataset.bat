@echo off
setlocal enabledelayedexpansion

:: Set console appearance
title HSEG AI - Large Scale Dataset Generator (50,000 Records)
color 0B

:: Display comprehensive header
echo.
echo ================================================================================
echo               HSEG AI SYSTEM - LARGE SCALE DATASET GENERATOR
echo                          50,000 SYNTHETIC RESPONSES
echo ================================================================================
echo.
echo 🎯 MISSION: Generate enterprise-scale synthetic dataset for NLP model training
echo.
echo 📊 DATASET SPECIFICATIONS:
echo    • Total Records: 50,000 psychological safety survey responses
echo    • Rich Narratives: 500+ character responses with emotional progression
echo    • Company Realism: Detailed culture-specific workplace scenarios
echo    • NLP Complexity: Varied sentence structures, emotional markers, incidents
echo    • Trauma Authenticity: Research-backed psychological trauma patterns
echo.
echo 🏢 COMPANY COVERAGE (55 TOTAL):
echo    • Healthcare: 20 organizations (Kaiser, Mayo, Cleveland Clinic, Johns Hopkins+)
echo    • Universities: 15 institutions (Harvard, Stanford, MIT, UC System, Yale+)
echo    • Business: 20 corporations (Microsoft, Google, Amazon, Apple, Meta, Tesla+)
echo.
echo 📝 NARRATIVE FEATURES:
echo    • Crisis Arcs: Incident → Impact → Escalation → Current State → Help/Isolation
echo    • Burnout Progression: Enthusiasm → Decline → Breaking Point → Coping → Uncertainty
echo    • Recovery Stories: Past Trauma → Turning Point → Support → Progress → Challenges
echo    • Company Context: Culture-specific stressors and organizational dynamics
echo.
echo 💡 NLP TRAINING VALUE:
echo    • Sentiment Analysis: Complex emotional progression patterns
echo    • Entity Recognition: Company names, roles, incidents, symptoms
echo    • Crisis Detection: Suicide ideation, PTSD, panic disorders
echo    • Topic Modeling: Domain-specific workplace trauma themes
echo    • Language Variation: Sophisticated linguistic diversity for robust models
echo.
echo ⚠️  RESOURCE REQUIREMENTS:
echo    • Processing Time: 15-30 minutes depending on system specs
echo    • Memory Usage: Adaptive (2-8GB RAM, auto-adjusts dataset size)
echo    • Storage: ~150MB final CSV file (varies by dataset size)
echo    • Dependencies: Python 3.8+, pandas, numpy, psutil
echo.
echo ================================================================================
echo.
echo 🚀 READY TO GENERATE ENTERPRISE-SCALE TRAINING DATA?
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
    echo 📞 Need help? Visit: https://docs.python.org/3/using/windows.html
    echo.
    pause
    exit /b 1
)

:: Get and display Python version
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
echo ✅ Python !PYTHON_VERSION! detected

:: Check available memory
for /f "tokens=2 delims=:" %%a in ('wmic OS get TotalVisibleMemorySize /value ^| find "="') do set TOTAL_MEM=%%a
set /a TOTAL_MEM_GB=!TOTAL_MEM!/1048576
if !TOTAL_MEM_GB! LSS 4 (
    echo ⚠️  WARNING: Low system memory detected (!TOTAL_MEM_GB!GB)
    echo    Generation may be slower or fail. Recommend 4GB+ available RAM.
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
if not exist "scripts\hseg_ultimate_generator.py" (
    echo ❌ ERROR: Required generator script not found
    echo Expected: scripts\hseg_ultimate_generator.py
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
echo                           INITIATING DATA GENERATION
echo ================================================================================
echo.
echo ⏳ GENERATION PROCESS STARTING...
echo.
echo 📊 Progress will be displayed in real-time:
echo    • Batch processing in 5,000 record chunks for memory efficiency
echo    • Progress updates every 1,000 records within each batch
echo    • Estimated total time: 15-30 minutes
echo.
echo 🎯 Target Output: data\hseg_55companies_ai_dataset.csv
echo.
echo ⚡ Beginning generation at %TIME%...
echo.

:: Record start time
set START_TIME=%TIME%

:: Execute the generation script with progress monitoring
python scripts/hseg_ultimate_generator.py
set GENERATION_RESULT=!errorlevel!

:: Record end time
set END_TIME=%TIME%

echo.
echo ================================================================================

if !GENERATION_RESULT! equ 0 (
    echo                        ✅ GENERATION COMPLETED SUCCESSFULLY
    echo ================================================================================
    echo.
    echo ⏱️  Generation completed at %END_TIME%
    echo 📊 Processing time: Started %START_TIME% → Finished %END_TIME%
    echo.

    :: Validate output file
    if exist "data\hseg_55companies_ai_dataset.csv" (
        for %%A in ("data\hseg_55companies_ai_dataset.csv") do set FILE_SIZE=%%~zA
        set /a FILE_SIZE_MB=!FILE_SIZE!/1048576
        echo 📁 Output file: data\hseg_55companies_ai_dataset.csv
        echo 💾 File size: !FILE_SIZE_MB! MB (!FILE_SIZE! bytes)

        :: Count actual records
        for /f %%i in ('type "data\hseg_55companies_ai_dataset.csv" ^| find /c /v ""') do set ACTUAL_LINES=%%i
        set /a ACTUAL_RECORDS=!ACTUAL_LINES!-1
        echo 📊 Records generated: !ACTUAL_RECORDS!

        :: Display sample data preview
        echo.
        echo 👁️  DATA QUALITY PREVIEW:
        echo ----------------------------------------
        echo Header:
        for /f "tokens=1-5 delims=," %%a in ('type "data\hseg_55companies_ai_dataset.csv" ^| head -1 2^>nul') do (
            echo %%a,%%b,%%c,%%d,%%e...
        )
        echo.
        echo Sample Record (line 2):
        for /f "skip=1 tokens=1-3 delims=," %%a in ('type "data\hseg_55companies_ai_dataset.csv" ^| head -2 2^>nul') do (
            echo ID: %%a
            echo Company: %%b
            echo Domain: %%c
            goto :sample_done
        )
        :sample_done

        echo.
        echo 🎯 DATASET VALIDATION:
        python -c "
import pandas as pd
try:
    df = pd.read_csv('data/hseg_55companies_ai_dataset.csv')
    print(f'✅ CSV structure valid: {len(df)} rows, {len(df.columns)} columns')
    print(f'✅ Domain distribution: {dict(df[\"domain\"].value_counts())}')
    print(f'✅ Narrative length: Q24 avg {df[\"q24_text\"].str.len().mean():.0f} chars')
    print(f'✅ No missing data: {df.isnull().sum().sum()} null values')
except Exception as e:
    print(f'❌ Validation error: {e}')
"

        echo.
        echo 🚀 NEXT STEPS FOR NLP MODEL TRAINING:
        echo.
        echo 📈 IMMEDIATE USE CASES:
        echo    1. Upload to your ML training pipeline
        echo    2. Import into NLP frameworks (spaCy, Transformers, etc.)
        echo    3. Test crisis detection algorithms
        echo    4. Validate sentiment analysis models
        echo    5. Train topic modeling systems
        echo.
        echo 🔬 ADVANCED ANALYTICS:
        echo    1. Company-specific trauma pattern analysis
        echo    2. Domain-based stress factor identification
        echo    3. Risk tier prediction model training
        echo    4. Longitudinal psychological progression modeling
        echo    5. Organizational culture impact assessment
        echo.
        echo 💡 RESEARCH APPLICATIONS:
        echo    • Workplace psychology research datasets
        echo    • Mental health intervention effectiveness
        echo    • Organizational behavior pattern analysis
        echo    • Crisis prediction algorithm development
        echo    • Cultural competency training data

    ) else (
        echo ❌ ERROR: Output file not found despite successful execution
        echo Expected: data\hseg_55companies_ai_dataset.csv
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
    echo    1. Ensure Python packages are installed: pip install pandas numpy
    echo    2. Free up disk space (need ~200MB available)
    echo    3. Close memory-intensive applications
    echo    4. Run as administrator if permission issues
    echo    5. Check Python version compatibility (3.8+ required)
    echo.
    echo 📞 SUPPORT RESOURCES:
    echo    • Check scripts\generate_50k_synthetic_data.py for errors
    echo    • Verify system meets minimum requirements
    echo    • Try generating smaller dataset first (500 records)
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
echo    • Output: data\hseg_55companies_ai_dataset.csv
echo.
echo 🎯 Your enterprise-scale synthetic dataset is ready for NLP model training!
echo.
echo Press any key to exit...
pause >nul