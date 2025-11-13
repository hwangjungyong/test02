# Simple API Test - No special characters

Write-Host "=== API Test ===" -ForegroundColor Cyan

# Test Signup
$body = '{"email":"test@example.com","password":"password123","name":"Test User"}'

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3001/api/auth/signup" -Method POST -ContentType "application/json" -Body $body
    
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host ($response | ConvertTo-Json -Depth 10)
    
    if ($response.token) {
        Write-Host ""
        Write-Host "Testing /api/auth/me..." -ForegroundColor Yellow
        
        $headers = @{ Authorization = "Bearer $($response.token)" }
        $meResponse = Invoke-RestMethod -Uri "http://localhost:3001/api/auth/me" -Method GET -Headers $headers
        
        Write-Host "SUCCESS!" -ForegroundColor Green
        Write-Host ($meResponse | ConvertTo-Json -Depth 10)
    }
} catch {
    Write-Host "ERROR:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Cyan

