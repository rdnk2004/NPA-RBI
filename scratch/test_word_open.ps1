$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    Write-Host "Word COM Version: $($word.Version)"
    $doc = $word.Documents.Open("D:\AI-ML Projects\NPA\papers\IEEE_NPA_EWS_Research_Paper.docx", $false, $true)
    Write-Host "Opened document successfully!"
    $doc.Close()
} catch {
    Write-Host "Word Exception:" $_.Exception.ToString()
} finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}
