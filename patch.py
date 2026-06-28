import re

content = open('index.html', encoding='utf-8').read()

sections_to_patch = {
    'cctv': ('voice', 'Next Phase: Voice Intelligence'),
    'voice': ('metadata', 'Next Phase: Metadata Intelligence'),
    'metadata': ('timeline', 'Generate Unified Timeline'),
    'timeline': ('graph', 'Generate Knowledge Graph'),
    'graph': ('contradiction', 'Run Contradiction Engine'),
    'contradiction': ('autopsy', 'Proceed to Autopsy Intelligence'),
    'autopsy': ('final', 'Generate Final Investigation Dashboard')
}

for sec_id, info in sections_to_patch.items():
    next_id, text = info
    pattern = r'(<section id="' + sec_id + r'".*?>.*?)(</section>)'
    replacement = r'\1\n<div style="margin-top:20px; text-align:right;"><button class="btn-primary" style="padding:12px 24px; font-size:1rem; font-weight:600;" onclick="goToStep(\'' + sec_id + r'\', \'' + next_id + r'\')">' + text + r' <i class="fa-solid fa-arrow-right"></i></button></div>\n\2'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Patched successfully!')
