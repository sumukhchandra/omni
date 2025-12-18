
param($OutputPath)

try {
    # Safe WinRT Type Loading for PS 5.1
    function Get-WinRTType {
        param($TypeName, $Namespace)
        $Type = [Type]::GetType("$TypeName, $Namespace, Version=255.255.255.255, Culture=neutral, PublicKeyToken=null, ContentType=WindowsRuntime")
        return $Type
    }
    
    $OcrEngineType = Get-WinRTType "Windows.Media.Ocr.OcrEngine" "Windows.Media.Ocr"
    $BitmapDecoderType = Get-WinRTType "Windows.Graphics.Imaging.BitmapDecoder" "Windows.Graphics.Imaging"
    $StorageFileType = Get-WinRTType "Windows.Storage.StorageFile" "Windows.Storage"
    $FileAccessModeType = Get-WinRTType "Windows.Storage.FileAccessMode" "Windows.Storage"
    $LanguageType = Get-WinRTType "Windows.Globalization.Language" "Windows.Globalization"
    
    if (-not $OcrEngineType) { throw "Could not load OCR Type" }
    
    # 1. Capture Screenshot using .NET
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    
    $Screen = [System.Windows.Forms.Screen]::PrimaryScreen
    $Width = $Screen.Bounds.Width
    $Height = $Screen.Bounds.Height
    $Bitmap = New-Object System.Drawing.Bitmap $Width, $Height
    $Graphics = [System.Drawing.Graphics]::FromImage($Bitmap)
    $Graphics.CopyFromScreen($Screen.Bounds.X, $Screen.Bounds.Y, 0, 0, $Bitmap.Size)
    
    $AbsPath = [System.IO.Path]::GetFullPath($OutputPath)
    $Bitmap.Save($AbsPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $Graphics.Dispose()
    $Bitmap.Dispose()
    
    # helper for async
    function Await($Task) {
        $Task.AsTask().GetAwaiter().GetResult()
    }
    
    # ... (Types loaded above)
    
    # 2. Initialize Engine using Reflection
    # $Lang = [Windows.Globalization.Language]::new("en-US")
    $Lang = [Activator]::CreateInstance($LanguageType, "en-US")
    
    # $Engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($Lang)
    $Engine = $OcrEngineType.InvokeMember("TryCreateFromLanguage", [System.Reflection.BindingFlags]::InvokeMethod, $null, $null, @($Lang))

    if ($null -eq $Engine) {
        Write-Output "ERROR: OCR Engine could not be created."
        exit 1
    }
    
    # 3. Load File
    # $File = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($AbsPath))
    $GetFileTask = $StorageFileType.InvokeMember("GetFileFromPathAsync", [System.Reflection.BindingFlags]::InvokeMethod, $null, $null, @($AbsPath))
    $File = Await $GetFileTask
    
    # $Stream = Await ($File.OpenAsync([Windows.Storage.FileAccessMode]::Read))
    # Need access to Enum value 'Read' (0)
    $StreamTask = $File.OpenAsync(0) 
    $Stream = Await $StreamTask
    
    # $Decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($Stream))
    $CreateDecoderTask = $BitmapDecoderType.InvokeMember("CreateAsync", [System.Reflection.BindingFlags]::InvokeMethod, $null, $null, @($Stream))
    $Decoder = Await $CreateDecoderTask
    
    # $SoftwareBitmap = Await ($Decoder.GetSoftwareBitmapAsync())
    $GetBmpTask = $Decoder.GetSoftwareBitmapAsync()
    $SoftwareBitmap = Await $GetBmpTask
    
    # 4. Recognize
    $ResultTask = $Engine.RecognizeAsync($SoftwareBitmap)
    $Result = Await $ResultTask
    
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
