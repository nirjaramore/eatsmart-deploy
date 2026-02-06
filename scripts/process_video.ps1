Param(
    [string]$InputPath = "..\eatsmartwebsite\asset\From KlickPin CF Super Nonna → Illustration animation [Video] _ Graphic design posters Graphic design inspiration Branding design.mp4",
    [string]$OutputSuffix = "_cropped_blur"
)

# Normalize paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
$absInput = Resolve-Path (Join-Path $repoRoot $InputPath)

if (-not (Test-Path $absInput)) {
    Write-Error "Input file not found: $absInput"
    exit 1
}

# Output filename
$dir = Split-Path $absInput -Parent
$base = [System.IO.Path]::GetFileNameWithoutExtension($absInput)
$ext = [System.IO.Path]::GetExtension($absInput)
$outputName = "$base$OutputSuffix$ext"
$outputPath = Join-Path $dir $outputName

Write-Host "Input: $absInput"
Write-Host "Output: $outputPath"

# Check ffmpeg
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) {
    Write-Error "ffmpeg not found in PATH. Please install ffmpeg and ensure it's available in the PATH. See https://ffmpeg.org/download.html"
    exit 2
}

# Crop 5% border on each side (centered) and apply light blur.
# Adjust crop ratio if you'd like different margins.
$filter = "crop=iw*0.9:ih*0.9:iw*0.05:ih*0.05,boxblur=10:1"

# Run ffmpeg (preserve audio)
& ffmpeg -y -i "$absInput" -vf $filter -c:a copy "$outputPath"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Processing complete: $outputPath"
} else {
    Write-Error "ffmpeg exited with code $LASTEXITCODE"
    exit $LASTEXITCODE
}
