# PowerShell script to create a Windows Scheduled Task that runs master_verify.py daily at 02:00 AM
$action = New-ScheduledTaskAction -Execute 'python' -Argument "-u \"$env:USERPROFILE\.gemini\antigravity\scratch\empire-unified\master_verify.py\""
$trigger = New-ScheduledTaskTrigger -Daily -At 02:00
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings (New-ScheduledTaskSettingsSet -Compatibility Win8)
Register-ScheduledTask -TaskName "DailyMasterVerify" -InputObject $task -Force
