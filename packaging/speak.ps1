param(
    [ValidateRange(-10, 10)]
    [int]$Rate = -1,
    [ValidateRange(0, 100)]
    [int]$Volume = 100
)

$text = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($text)) {
    exit 0
}

$speaker = New-Object -ComObject SAPI.SpVoice
try {
    $speaker.Rate = $Rate
    $speaker.Volume = $Volume
    [void]$speaker.Speak($text)
}
finally {
    [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($speaker) | Out-Null
}
