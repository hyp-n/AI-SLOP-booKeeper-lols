# Build APK using Capacitor
$frontendPath = "C:\Users\Admin\booKeeper - ai\frontend"

Push-Location $frontendPath

try {
    # Initialize Capacitor if not already done
    if (!(Test-Path "capacitor.config.json") -or !(Test-Path ".capacitor")) {
        Write-Host "Initializing Capacitor..."
        npx cap init --skip-npm --skip-cordova
        Write-Host "✓ Capacitor initialized"
    }

    # Add Android platform
    if (!(Test-Path "android")) {
        Write-Host "Adding Android platform..."
        npx cap add android
        Write-Host "✓ Android platform added"
    }

    # Sync changes
    Write-Host "Syncing Capacitor project..."
    npx cap sync android
    Write-Host "✓ Capacitor synced"

    # Show build output
    Write-Host "Building APK..."
    npx cap run android --build
    Write-Host "✓ APK built successfully!"
    
    Write-Host "\nNext steps:" -ForegroundColor Green
    Write-Host "1. APK location: android/app/build/outputs/apk/debug/app-debug.apk" -ForegroundColor Yellow
    Write-Host "2. To run on device: adb install android/app/build/outputs/apk/debug/app-debug.apk" -ForegroundColor Yellow
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location