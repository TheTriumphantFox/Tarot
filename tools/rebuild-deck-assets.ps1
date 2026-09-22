param(
    [Parameter(Mandatory = $true)]
    [string[]] $CardId
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$projectRoot = Split-Path -Parent $PSScriptRoot
$deckRoot = Join-Path $projectRoot "assets\deck"
$facesRoot = Join-Path $deckRoot "faces"
$thumbsRoot = Join-Path $deckRoot "thumbnails"

function New-ResizedBitmap {
    param(
        [Parameter(Mandatory = $true)] [System.Drawing.Image] $Source,
        [Parameter(Mandatory = $true)] [int] $Width,
        [Parameter(Mandatory = $true)] [int] $Height
    )

    $target = [System.Drawing.Bitmap]::new($Width, $Height)
    $target.SetResolution(96, 96)
    $graphics = [System.Drawing.Graphics]::FromImage($target)
    try {
        $graphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
        $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
        $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
        $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
        $wrap = [System.Drawing.Imaging.ImageAttributes]::new()
        try {
            $wrap.SetWrapMode([System.Drawing.Drawing2D.WrapMode]::TileFlipXY)
            $graphics.DrawImage(
                $Source,
                [System.Drawing.Rectangle]::new(0, 0, $Width, $Height),
                0,
                0,
                $Source.Width,
                $Source.Height,
                [System.Drawing.GraphicsUnit]::Pixel,
                $wrap
            )
        }
        finally {
            $wrap.Dispose()
        }
    }
    finally {
        $graphics.Dispose()
    }
    return $target
}

function Save-PngAtomically {
    param(
        [Parameter(Mandatory = $true)] [System.Drawing.Image] $Image,
        [Parameter(Mandatory = $true)] [string] $Path
    )

    $tempPath = "$Path.new.png"
    $Image.Save($tempPath, [System.Drawing.Imaging.ImageFormat]::Png)
    Move-Item -LiteralPath $tempPath -Destination $Path -Force
}

foreach ($id in $CardId) {
    $facePath = Join-Path $facesRoot "$id.png"
    if (-not (Test-Path -LiteralPath $facePath)) {
        throw "Unknown card face: $id"
    }

    $source = [System.Drawing.Image]::FromFile($facePath)
    try {
        if (($source.Width -ne 1024) -or ($source.Height -ne 1536)) {
            throw "$id must be 1024 x 1536; found $($source.Width) x $($source.Height)"
        }
        $upright = New-ResizedBitmap -Source $source -Width 200 -Height 300
        try {
            Save-PngAtomically -Image $upright -Path (Join-Path $thumbsRoot "$id.png")
            $reversed = [System.Drawing.Bitmap]$upright.Clone()
            try {
                $reversed.RotateFlip([System.Drawing.RotateFlipType]::Rotate180FlipNone)
                Save-PngAtomically -Image $reversed -Path (Join-Path $thumbsRoot "$id-reversed.png")
            }
            finally {
                $reversed.Dispose()
            }
        }
        finally {
            $upright.Dispose()
        }
    }
    finally {
        $source.Dispose()
    }
}

$groups = $CardId | ForEach-Object { ($_ -split "_")[0] } | Sort-Object -Unique
foreach ($group in $groups) {
    $faceFiles = Get-ChildItem -LiteralPath $facesRoot -Filter "$group`_*.png" | Sort-Object Name
    $columns = 4
    $cellWidth = 280
    $cellHeight = 400
    $cardWidth = 240
    $cardHeight = 360
    $rows = [Math]::Ceiling($faceFiles.Count / $columns)
    $sheet = [System.Drawing.Bitmap]::new($columns * $cellWidth, $rows * $cellHeight)
    $graphics = [System.Drawing.Graphics]::FromImage($sheet)
    try {
        $graphics.Clear([System.Drawing.Color]::FromArgb(12, 11, 9))
        for ($index = 0; $index -lt $faceFiles.Count; $index++) {
            $source = [System.Drawing.Image]::FromFile($faceFiles[$index].FullName)
            try {
                $card = New-ResizedBitmap -Source $source -Width $cardWidth -Height $cardHeight
                try {
                    $column = $index % $columns
                    $row = [Math]::Floor($index / $columns)
                    $graphics.DrawImageUnscaled($card, ($column * $cellWidth) + 20, ($row * $cellHeight) + 20)
                }
                finally {
                    $card.Dispose()
                }
            }
            finally {
                $source.Dispose()
            }
        }
    }
    finally {
        $graphics.Dispose()
    }

    try {
        $contactName = if ($group -eq "major") {
            "contact-majors.png"
        }
        else {
            "contact-$group.png"
        }
        Save-PngAtomically -Image $sheet -Path (Join-Path $deckRoot $contactName)
    }
    finally {
        $sheet.Dispose()
    }
}

Write-Host "Rebuilt thumbnails for $($CardId.Count) card(s) and contact sheets for: $($groups -join ', ')"
