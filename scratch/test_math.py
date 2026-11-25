import docx
from docx.oxml import parse_xml

doc = docx.Document()
p = doc.add_paragraph()

omml_xml = '''<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
  <m:sSub>
    <m:e><m:r><m:t>GNPA</m:t></m:r></m:e>
    <m:sub><m:r><m:t>i,t</m:t></m:r></m:sub>
  </m:sSub>
  <m:r><m:t> = α </m:t></m:r>
  <m:sSub>
    <m:e><m:r><m:t>GNPA</m:t></m:r></m:e>
    <m:sub><m:r><m:t>i,t-1</m:t></m:r></m:sub>
  </m:sSub>
  <m:r><m:t> + </m:t></m:r>
  <m:sSup>
    <m:sSub>
      <m:e><m:r><m:t>X</m:t></m:r></m:e>
      <m:sub><m:r><m:t>i,t</m:t></m:r></m:sub>
    </m:sSub>
    <m:sup><m:r><m:t>′</m:t></m:r></m:sup>
  </m:sSup>
  <m:r><m:t>β + </m:t></m:r>
  <m:sSub>
    <m:e><m:r><m:t>μ</m:t></m:r></m:e>
    <m:sub><m:r><m:t>i</m:t></m:r></m:sub>
  </m:sSub>
  <m:r><m:t> + </m:t></m:r>
  <m:sSub>
    <m:e><m:r><m:t>ε</m:t></m:r></m:e>
    <m:sub><m:r><m:t>i,t</m:t></m:r></m:sub>
  </m:sSub>
</m:oMath>'''

math_elm = parse_xml(omml_xml)
p._p.append(math_elm)
doc.save('scratch/test_math.docx')
doc2 = docx.Document('scratch/test_math.docx')
print('Successfully saved and reloaded test_math.docx, paragraphs:', len(doc2.paragraphs))
