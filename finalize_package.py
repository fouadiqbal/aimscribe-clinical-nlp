"""Preserve project deliverables, verify frozen files and create a portable archive."""
from pathlib import Path
import hashlib,json,zipfile,csv,datetime
from src.evaluate import hashes,implementation_hashes
R=Path(__file__).resolve().parent
stamp='22 October 2026'
p=R/'AI_DISCLOSURE.md';s=p.read_text(encoding='utf-8');a=s.index('Current review status:');b=s.index('\n\n',a);s=s[:a]+'Current review status: implementation, all 12 frozen comparison outputs, provisional AI-assisted source grading, comparison note and eight slides are complete. Codex also assisted with grading and failure analysis. All cards, the image-only hypertension transcription, case expectations and grading require candidate source verification. No clinical expert review or candidate endorsement is claimed.'+s[b:];p.write_text(s,encoding='utf-8')
p=R/'SELECTED_PLAN.md';s=p.read_text(encoding='utf-8');s=s.replace('Updated: 21 October 2026','Updated: 22 October 2026');a=s.index('- Six final cases/checklists drafted') if '- Six final cases/checklists drafted' in s else s.index('- Six cases/checklists frozen');s=s[:a]+'''- Six cases/checklists frozen before final comparison; all 12 first attempts saved. Frozen source/case hashes remain unchanged.
- AI-assisted provisional grading and compact comparison report complete, including failures and timing caveats.
- Architecture, 235-word paper summary, eight editable slides and interview guide complete.
- Persistent local launcher added and app/model health verified. Submission ZIP and hash manifest prepared.

## Next
Candidate must verify source cards, image transcription, expectations and grading, then practise the live demo and explain the work. Do not claim independent clinical validation. Preserve this frozen experiment when making future improvements.
''';p.write_text(s,encoding='utf-8')
(R/'COMPLETION_STATUS.md').write_text('''# Completion status — 22 October 2026

Completed: four active source protocols and assigned-page extraction; 34 canonical source-linked cards/schema; reasoning example and field guide; free local model and vector RAG; editable two-mode Streamlit app; six frozen cases/checklists and 12 saved first attempts; provisional results table and comparison note; architecture and design defence; paper summary, eight-slide presentation and interview guide; AI disclosure, setup instructions, portable archive and persistent launcher.

Verified: six rule tests pass, card structure/provenance checks pass, frozen cases/implementation hashes unchanged, all 12 outputs have no recorded structural validation errors, app and model HTTP health respond. These checks do not establish clinical correctness. A completely fresh installation on another PC has not been tested.

Pending candidate work: compare cards and visual transcription against sources, verify case checklists and provisional grades, understand and rehearse the paper/code/live demo, then submit. Results contain omissions, wrong branch selection and invented patient facts. No clinical validation is claimed.

The app previously could not open because Streamlit had stopped while the model server remained running. Double-click Open_AIMScribe.cmd to start services and reopen it. This localhost address works on this computer while services run. Downloads require internet initially; inference is local and free of API charges.

Original materials and historical plans remain preserved in materials/. Model files, runtime and virtual environment remain installed in this workspace. The portable ZIP excludes those large machine-specific directories and includes download/setup instructions.
''',encoding='utf-8')
p=R/'docs/development_log.md';s=p.read_text(encoding='utf-8');s+='\n\n## 22 October 2026 completion checkpoint\nAll 12 frozen outputs preserved. Provisional source-linked grading and comparison note report negative and limited positive results. Eight-slide deck exported. Added persistent launcher after Streamlit stopped between sessions. Candidate source review remains pending. No final experiment tuning/rerun.\n';p.write_text(s,encoding='utf-8')
f=json.loads((R/'results/frozen_hashes.json').read_text(encoding='utf-8'))
assert f['files']==hashes() and f['implementation']==implementation_hashes()
outputs=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((R/'outputs').glob('C[1-6]_*.json'))]
assert len(outputs)==12 and all(not x.get('error') and not x.get('validation_errors') for x in outputs)
with zipfile.ZipFile(R/'docs/AIMScribe_Assessment.pptx') as deck:
    assert len([n for n in deck.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml') and '/_rels/' not in n])==8
active={p['file'] for p in json.loads((R/'data/protocols/manifest.json').read_text(encoding='utf-8'))}
files=[]
for folder in ['src','tests','docs','results','outputs','materials','data','cloud']:
    for p in (R/folder).rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts or 'service_logs' in p.parts or p.suffix=='.log':continue
        if p.parent==R/'data/protocols' and p.suffix=='.pdf' and p.name not in active:continue
        files.append(p)
files += [p for p in R.iterdir() if p.is_file() and p.suffix in ['.md','.py','.ps1','.cmd','.txt']]
files=sorted(set(files))
inventory={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
manifest=R/'PACKAGE_SHA256.json';manifest.write_text(json.dumps(inventory,indent=2),encoding='utf-8')
target=R/'Md_Fouad_Iqbal_RA_Clinical_NLP.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files+[manifest]:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    for n,h in inventory.items(): assert hashlib.sha256(z.read(n)).hexdigest()==h
(R/'results/package_verification.json').write_text(json.dumps({'verified_at':datetime.datetime.now().isoformat(),'files':len(files)+1,'zip_bytes':target.stat().st_size,'archive_crc_and_sha256':'pass','frozen_hashes':'unchanged','candidate_review':'pending'},indent=2),encoding='utf-8')
print(f'Verified {len(files)+1} files, ZIP {target.stat().st_size:,} bytes. Candidate verification remains pending.')
