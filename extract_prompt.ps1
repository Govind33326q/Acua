$ErrorActionPreference = 'Stop'
$py = 'C:\Users\govin\AppData\Local\Programs\Python\Python312\python.exe'
& $py -m pip install pypdf -q
$script = @'
import os
from pathlib import Path
import pypdf

pdf_path = Path(r'd:\AquaVisionaries\AquaVisinaries\AquaVisinaries\AquaScan_AI_Master_Implementation_Prompt.pdf')
print('exists', pdf_path.exists())
reader = pypdf.PdfReader(str(pdf_path))
print('pages', len(reader.pages))
text = ''
for page in reader.pages[:12]:
    text += (page.extract_text() or '') + '\n'
print(text[:30000])
'@
$tempFile = Join-Path $env:TEMP 'read_prompt.py'
Set-Content -Path $tempFile -Value $script -Encoding UTF8
& $py $tempFile
