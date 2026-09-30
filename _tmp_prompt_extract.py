import os
from pathlib import Path

try:
    import pypdf
except ImportError:
    raise SystemExit('pypdf is not installed. Run: python -m pip install pypdf')

pdf_path = Path('d:/AquaVisionaries/AquaVisinaries/AquaVisinaries/AquaScan_AI_Master_Implementation_Prompt.pdf')
print('exists', pdf_path.exists())
reader = pypdf.PdfReader(str(pdf_path))
print('pages', len(reader.pages))
text = ''
for page in reader.pages[:20]:
    text += (page.extract_text() or '') + '\n'
print(text[:40000])
