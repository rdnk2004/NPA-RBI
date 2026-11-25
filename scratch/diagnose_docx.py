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

print("Unique OMML tags used:", sorted(m_tags))

# Valid OMML elements according to ECMA-376:
# oMath, oMathPara, r, rPr, t, sSub, sSup, sSubSup, f, num, den, d, e, sub, sup, limLow, lim, m, mr, nary, bar, eqArr, func, fName, groupChr, borderBox, rad, deg, sPre, box
# Inside rPr: lit, nor, scr, sty, brk, aln
valid_omml_tags = {
    'oMath', 'oMathPara', 'r', 'rPr', 't', 'sSub', 'sSup', 'sSubSup', 'f', 'num', 'den',
    'd', 'e', 'sub', 'sup', 'limLow', 'lim', 'm', 'mr', 'nary', 'bar', 'eqArr', 'func',
    'fName', 'groupChr', 'borderBox', 'rad', 'deg', 'sPre', 'box', 'lit', 'nor', 'scr', 'sty', 'brk', 'aln'
}

invalid_omml = m_tags - valid_omml_tags
print("Invalid OMML tags:", invalid_omml)

# Now check w: namespace elements
w_tags = set()
for el in root.iter():
    if el.tag.startswith('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'):
        w_tags.add(el.tag.split('}')[-1])

print("Unique WordprocessingML tags used:", len(w_tags))

# Check table structure:
for idx, tbl in enumerate(root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl')):
    # check children of tbl
    children = [c.tag.split('}')[-1] for c in tbl]
    # valid children of tbl: tblPr, tblGrid, tr
    non_valid_tbl_children = [c for c in children if c not in ('tblPr', 'tblGrid', 'tr')]
    if non_valid_tbl_children:
        print(f"Table {idx} has invalid children:", non_valid_tbl_children)
    
    # check tcPr children
    for tc in tbl.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tc'):
        tcPr = tc.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcPr')
        if tcPr is not None:
            tcPr_children = [c.tag.split('}')[-1] for c in tcPr]
            # print if tcMar is present
            if 'tcMar' in tcPr_children:
                # check tcMar children
                tcMar = tcPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcMar')
                for m in tcMar:
                    print("tcMar child:", m.tag.split('}')[-1], m.attrib)
