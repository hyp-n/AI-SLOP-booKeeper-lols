# Install Capacitor and upgrade to DaisyUI 5 + Tailwind 4
$frontendPath = "C:\Users\Admin\booKeeper - ai\frontend"

Write-Host "Installing Capacitor..."
Push-Location $frontendPath
try {
    npm install --save-exact @capacitor/core @capacitor/cli @capacitor/android@latest
    Write-Host "✓ Capacitor installed successfully"
} catch {
    Write-Host "✗ Failed to install Capacitor: $($_.Exception.Message)"
    Pop-Location
    exit 1
}

Write-Host "Upgrading UI dependencies to DaisyUI 5 + Tailwind 4..."
try {
    npm install --save-exact daisyui@latest tailwindcss@^4.0.0 @vitejs/plugin-react@^5.0.0 postcss@^8.4.33 autoprefixer@^10.4.17
    Write-Host "✓ UI dependencies upgraded successfully"
} catch {
    Write-Host "✗ Failed to upgrade UI deps: $($_.Exception.Message)"
    Pop-Location
    exit 1
}

Pop-Location
Write-Host "Setup complete! Ready to initialize Capacitor."