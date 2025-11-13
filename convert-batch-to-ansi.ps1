# 배치 파일을 ANSI(CP949)로 변환하는 스크립트

$files = @(
    'start-dev.bat',
    'start-servers.bat',
    'start-python-server.bat',
    'build-and-run-mcp.bat'
)

Write-Host "=== 배치 파일 인코딩 변환 ===" -ForegroundColor Cyan
Write-Host ""

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "변환 중: $file" -ForegroundColor Yellow
        
        try {
            # UTF-8로 읽기
            $utf8Content = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)
            
            # ANSI(CP949)로 저장
            $ansiEncoding = [System.Text.Encoding]::GetEncoding(949)
            [System.IO.File]::WriteAllText($file, $utf8Content, $ansiEncoding)
            
            Write-Host "  완료: $file" -ForegroundColor Green
        } catch {
            Write-Host "  오류: $file - $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "  파일 없음: $file" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== 변환 완료 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "이제 배치 파일을 실행하면 한글이 정상적으로 표시됩니다." -ForegroundColor Green
Write-Host ""

