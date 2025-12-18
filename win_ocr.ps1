
# Validates if Windows OCR is available and working
param($ImagePath)

try {
    # Load WinRT Types
    [void][Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime]
    [void][Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType = WindowsRuntime]
    [void][Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
    [void][System.IO.Path]
    
    # Get Absolute Path
    $AbsPath = [System.IO.Path]::GetFullPath($ImagePath)
    
    # helper to run async tasks synchronously in PS
    function Await($Task) {
        $Task.AsTask().GetAwaiter().GetResult()
    }
    
    # Initialize Engine
    $Lang = [Windows.Globalization.Language]::new("en-US")
    $Engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($Lang)
    
    if ($null -eq $Engine) {
        Write-Output "ERROR: OCR Engine could not be created."
        exit 1
    }
    
    # Load File
    $File = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($AbsPath))
    $Stream = Await ($File.OpenAsync([Windows.Storage.FileAccessMode]::Read))
    $Decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($Stream))
    $SoftwareBitmap = Await ($Decoder.GetSoftwareBitmapAsync())
    
    # Recognize
    $Result = Await ($Engine.RecognizeAsync($SoftwareBitmap))
    
    # Output Lines
    $Text = ""
    foreach ($Line in $Result.Lines) {
        $Text += $Line.Text + " "
    }
    
    Write-Output $Text
    exit 0

} catch {
    Write-Output "ERROR: $($_.Exception.Message)"
    exit 1
}
