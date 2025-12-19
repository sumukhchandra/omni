
# Validates if Windows OCR is available and working
param($ImagePath)

try {
    # Load WinRT Types
    [void][Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime]
    [void][Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType = WindowsRuntime]
    [void][Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
    [void][Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]
    [void][System.IO.Path]
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    
    # Get Absolute Path
    $AbsPath = [System.IO.Path]::GetFullPath($ImagePath)
    
    function Await($AsyncOp) {
        if ($null -eq $AsyncOp) { throw "AsyncOp is null" }
        Write-Output "DEBUG: Awaiting $($AsyncOp)"
        while ($AsyncOp.Status -eq "Started") {
            try { Start-Sleep -Milliseconds 10 } catch {}
        }
        Write-Output "DEBUG: Status is $($AsyncOp.Status)"
        if ($AsyncOp.Status -eq "Completed") {
            return $AsyncOp.GetResults()
        }
        if ($AsyncOp.Status -eq "Error") {
            throw $AsyncOp.ErrorCode
        }
        throw "Async operation failed with status: $($AsyncOp.Status)"
    }
    
    # Initialize Engine
    Write-Output "DEBUG: Init Engine"
    $Lang = [Windows.Globalization.Language]::new("en-US")
    $Lang = [Windows.Globalization.Language]::new("en-US")
    $Engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($Lang)
    
    if ($null -eq $Engine) {
        Write-Output "ERROR: OCR Engine could not be created."
        exit 1
    }
    
    # Load File
    Write-Output "DEBUG: Loading file $AbsPath"
    $Op = [Windows.Storage.StorageFile]::GetFileFromPathAsync($AbsPath)
    Write-Output "DEBUG: Op Type: $($Op.GetType().FullName)"
    $File = Await ($Op)
    $Stream = Await ($File.OpenAsync([Windows.Storage.FileAccessMode]::Read))
    $Decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($Stream))
    $SoftwareBitmap = Await ($Decoder.GetSoftwareBitmapAsync())
    
    # Recognize
    $Result = Await ($Engine.RecognizeAsync($SoftwareBitmap))
    
    # Output JSON with Lines and Coordinates
    $OutputList = @()
    foreach ($Line in $Result.Lines) {
        foreach ($Word in $Line.Words) {
            $Rect = $Word.BoundingRect
            $OutputList += @{
                text = $Word.Text
                rect = @($Rect.X, $Rect.Y, $Rect.Width, $Rect.Height)
            }
        }
    }
    
    $JsonOutput = $OutputList | ConvertTo-Json -Compress
    Write-Output $JsonOutput
    exit 0

} catch {
    Write-Output "ERROR: $($_.Exception.Message)"
    exit 1
}
