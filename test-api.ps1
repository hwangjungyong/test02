# API Test Script (PowerShell)
# UTF-8 with BOM encoding required

Write-Host "=== API Server Test ===" -ForegroundColor Cyan
Write-Host ""

# Check if server is running
try {
    $testConnection = Invoke-WebRequest -Uri "http://localhost:3001/api/auth/signup" -Method POST -ContentType "application/json" -Body '{"test":"connection"}' -UseBasicParsing -ErrorAction SilentlyContinue
} catch {
    Write-Host "ERROR: API server is not running!" -ForegroundColor Red
    Write-Host "Please run: npm run api-server" -ForegroundColor Yellow
    exit 1
}

# 1. Signup Test
Write-Host "1. Testing Signup..." -ForegroundColor Yellow

$signupBody = @{
    email = "test@example.com"
    password = "password123"
    name = "Test User"
} | ConvertTo-Json

try {
    $signupResponse = Invoke-WebRequest -Uri "http://localhost:3001/api/auth/signup" -Method POST -ContentType "application/json" -Body $signupBody -UseBasicParsing
    
    Write-Host "SUCCESS: Signup completed!" -ForegroundColor Green
    Write-Host $signupResponse.Content
    Write-Host ""
    
    # Extract token
    $signupData = $signupResponse.Content | ConvertFrom-Json
    $token = $signupData.token
    
    if ($token) {
        Write-Host "Token issued: $($token.Substring(0, [Math]::Min(20, $token.Length)))..." -ForegroundColor Gray
        Write-Host ""
        
        # 2. User Info Test
        Write-Host "2. Testing User Info Retrieval..." -ForegroundColor Yellow
        
        $headers = @{
            "Authorization" = "Bearer $token"
        }
        
        $meResponse = Invoke-WebRequest -Uri "http://localhost:3001/api/auth/me" -Method GET -Headers $headers -UseBasicParsing
        
        Write-Host "SUCCESS: User info retrieved!" -ForegroundColor Green
        Write-Host $meResponse.Content
        Write-Host ""
    }
    
} catch {
    Write-Host "ERROR occurred:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Host "Response: $responseBody" -ForegroundColor Red
            $reader.Close()
        } catch {
            Write-Host "Could not read error response" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
