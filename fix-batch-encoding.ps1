# 배치 파일 인코딩 수정 스크립트
# UTF-8로 저장된 배치 파일을 ANSI(CP949)로 변환

Write-Host "=== 배치 파일 인코딩 수정 ===" -ForegroundColor Cyan
Write-Host ""

$files = @(
    'start-dev.bat',
    'start-servers.bat',
    'start-python-server.bat',
    'build-and-run-mcp.bat'
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "변환 중: $file" -ForegroundColor Yellow
        
        try {
            # UTF-8로 읽기
            $content = Get-Content $file -Encoding UTF8 -Raw
            
            # ANSI(CP949)로 저장
            # PowerShell의 Default 인코딩은 시스템 기본 인코딩(Windows에서는 CP949)
            $content | Out-File $file -Encoding Default -NoNewline
            
            Write-Host "  ✓ 완료: $file" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ 오류: $file - $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "  ⚠ 파일 없음: $file" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== 변환 완료 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "이제 배치 파일을 실행하면 한글이 정상적으로 표시됩니다." -ForegroundColor Green
Write-Host ""

