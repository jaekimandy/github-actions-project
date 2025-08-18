@echo off
REM Docker Build Optimization Script for Windows
REM This script optimizes Docker builds for faster CI/CD pipelines

echo 🚀 Optimizing Docker build for faster CI/CD...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    exit /b 1
)

REM Clean up old images and containers to free up space
echo 🧹 Cleaning up old Docker resources...
docker system prune -f --volumes

REM Build with optimized settings
echo 🔨 Building Docker image with optimizations...

REM Build arguments for better caching
for /f "tokens=*" %%i in ('git rev-parse HEAD 2^>nul') do set VCS_REF=%%i
if "%VCS_REF%"=="" set VCS_REF=unknown

REM Build targets
set TARGETS=production development testing

for %%t in (%TARGETS%) do (
    echo 📦 Building %%t target...
    
    REM Build with optimizations
    docker build ^
        --target %%t ^
        --tag app:%%t ^
        --file Dockerfile ^
        --progress=plain ^
        --no-cache=false ^
        --compress=false ^
        --build-arg BUILD_DATE=%date% ^
        --build-arg VCS_REF=%VCS_REF% ^
        .
    
    if errorlevel 1 (
        echo ❌ Failed to build %%t target
        exit /b 1
    ) else (
        echo ✅ %%t target built successfully
    )
)

REM Show build results
echo 📊 Build Results:
docker images | findstr "app:"

echo 🎉 Docker build optimization complete!
echo.
echo 💡 Tips for faster builds:
echo    - Use 'docker build --target production' for production builds only
echo    - Use 'docker build --target development' for development builds only
echo    - Use 'docker build --target testing' for testing builds only
echo    - The build cache will automatically speed up subsequent builds
echo.
echo 🔍 To check build cache usage:
echo    docker system df
echo    docker builder prune

pause
