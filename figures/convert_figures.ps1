# PowerShell script to convert DOT files to PDF
# Run this from the figures/ directory

Write-Host "Converting DOT files to PDF..." -ForegroundColor Green

$dotFiles = Get-ChildItem -Filter "*.dot"

foreach ($file in $dotFiles) {
    $pdfName = $file.BaseName + ".pdf"
    Write-Host "Converting $($file.Name) -> $pdfName" -ForegroundColor Yellow
    
    dot -Tpdf $file.Name -o $pdfName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Success!" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed! Make sure Graphviz is installed." -ForegroundColor Red
    }
}

Write-Host "`nConversion complete!" -ForegroundColor Green
Write-Host "Check if Graphviz is installed: dot -V" -ForegroundColor Cyan




