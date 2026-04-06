$repoRoot = 'D:\Creativity\A-Share-Quant_TrY'
$pythonw = 'D:\Tool\Anaconda\pythonw.exe'
$scriptPath = Join-Path $repoRoot 'scripts\run_a_share_internal_hot_news_runtime_control_panel_v1.py'

$existing = Get-CimInstance Win32_Process |
    Where-Object {
        $_.Name -match '^python(w)?\.exe$' -and
        $_.CommandLine -like '*run_a_share_internal_hot_news_runtime_control_panel_v1.py*'
    }

foreach ($process in $existing) {
    try {
        Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop
    } catch {
    }
}

Start-Sleep -Milliseconds 300
Start-Process -FilePath $pythonw -ArgumentList @($scriptPath) -WorkingDirectory $repoRoot
