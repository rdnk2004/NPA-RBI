import zipfile
import lxml.etree as ET

with zipfile.ZipFile('papers/IEEE_NPA_EWS_Research_Paper.docx') as z:
    doc_xml = z.read('word/document.xml')

root = ET.fromstring(doc_xml)

# Check all tags in m: namespace
m_tags = set()
for el in root.iter():
    if el.tag.startswith('{http://schemas.openxmlformats.org/officeDocument/2006/math}'):
        m_tags.add(el.tag.split('}')[-1])

print("OMML tags in new doc:", m_tags)

# Check all tags in w: namespace
w_tags = set()
for el in root.iter():
    if el.tag.startswith('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'):
        w_tags.add(el.tag.split('}')[-1])

print("Total WordprocessingML tags in new doc:", len(w_tags))

# Check tabs and equation numbers
eq_paras = []
for p in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
    texts = [t.text for t in p.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text]
    full_text = "".join(texts)
    if full_text.endswith(')') and '(' in full_text:
        # check if it's an equation
        eq_paras.append(full_text)

print("Found equations:", len(eq_paras))
for eq in eq_paras:
    print("  ", eq)

# Check references
ref_paras = []
for p in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
    texts = [t.text for t in p.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text]
    full_text = "".join(texts)
    if full_text.startswith('[') and ']' in full_text:
        ref_paras.append(full_text[:60] + "...")

print("Found references:", len(ref_paras))
for r in ref_paras:
    print("  ", r)
