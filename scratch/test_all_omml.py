import docx
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_omml_equation(omml_inner):
    return parse_xml(f'<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">{omml_inner}</m:oMath>')

# Test OMML snippets for our equations
eq_omml = {
    1: '''
      <m:sSub><m:e><m:r><m:t>GNPA</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> = </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>α</m:t></m:r></m:e><m:sub><m:r><m:t>0</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> + </m:t></m:r>
      <m:sSup><m:sSub><m:e><m:r><m:t>X</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub></m:sSub><m:sup><m:r><m:t>⊤</m:t></m:r></m:sup></m:sSup>
      <m:r><m:rPr><m:b/></m:rPr><m:t>β</m:t></m:r>
      <m:r><m:t> + </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>μ</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> + </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>ε</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub></m:sSub>
    ''',
    2: '''
      <m:sSub><m:e><m:r><m:t>GNPA</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> = α </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>GNPA</m:t></m:r></m:e><m:sub><m:r><m:t>i,t-1</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> + </m:t></m:r>
      <m:sSup><m:sSub><m:e><m:r><m:t>X</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub></m:sSub><m:sup><m:r><m:t>⊤</m:t></m:r></m:sup></m:sSup>
      <m:r><m:rPr><m:b/></m:rPr><m:t>β</m:t></m:r>
      <m:r><m:t> + </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>μ</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> + </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>ε</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub></m:sSub>
    ''',
    3: '''
      <m:r><m:t>Δ</m:t></m:r>
      <m:sSub><m:e><m:r><m:t>GNPA</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> = α Δ</m:t></m:r>
      <m:sSub><m:e><m:r><m:t>GNPA</m:t></m:r></m:e><m:sub><m:r><m:t>i,t-1</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> + Δ</m:t></m:r>
      <m:sSup><m:sSub><m:e><m:r><m:t>X</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub></m:sSub><m:sup><m:r><m:t>⊤</m:t></m:r></m:sup></m:sSup>
      <m:r><m:rPr><m:b/></m:rPr><m:t>β</m:t></m:r>
      <m:r><m:t> + Δ</m:t></m:r>
      <m:sSub><m:e><m:r><m:t>ε</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub></m:sSub>
    ''',
    4: '''
      <m:r><m:t>𝔼[ </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>GNPA</m:t></m:r></m:e><m:sub><m:r><m:t>i,t-s</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> · Δ</m:t></m:r>
      <m:sSub><m:e><m:r><m:t>ε</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> ] = 0,   ∀ s ≥ 2</m:t></m:r>
    ''',
    5: '''
      <m:r><m:t>𝔼[ Δ</m:t></m:r>
      <m:sSub><m:e><m:r><m:t>GNPA</m:t></m:r></m:e><m:sub><m:r><m:t>i,t-1</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> · (</m:t></m:r>
      <m:sSub><m:e><m:r><m:t>μ</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> + </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>ε</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t>) ] = 0</m:t></m:r>
    ''',
    6: '''
      <m:sSubSup>
        <m:e><m:r><m:t>Y</m:t></m:r></m:e>
        <m:sub><m:r><m:t>i,t+1</m:t></m:r></m:sub>
        <m:sup><m:r><m:t>PCA</m:t></m:r></m:sup>
      </m:sSubSup>
      <m:r><m:t> = 𝕀( </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>GNPA</m:t></m:r></m:e><m:sub><m:r><m:t>i,t+1</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> ≥ 6.0% )</m:t></m:r>
    ''',
    7: '''
      <m:sSup><m:e><m:r><m:t>ℒ</m:t></m:r></m:e><m:sup><m:r><m:t>(m)</m:t></m:r></m:sup></m:sSup>
      <m:r><m:t> = </m:t></m:r>
      <m:sSubSup><m:e><m:r><m:t>∑</m:t></m:r></m:e><m:sub><m:r><m:t>k=1</m:t></m:r></m:sub><m:sup><m:r><m:t>K</m:t></m:r></m:sup></m:sSubSup>
      <m:r><m:t> l( </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>k</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t>, </m:t></m:r>
      <m:sSubSup><m:e><m:r><m:t>ŷ</m:t></m:r></m:e><m:sub><m:r><m:t>k</m:t></m:r></m:sub><m:sup><m:r><m:t>(m-1)</m:t></m:r></m:sup></m:sSubSup>
      <m:r><m:t> + </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>f</m:t></m:r></m:e><m:sub><m:r><m:t>m</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t>(</m:t></m:r>
      <m:sSub><m:e><m:r><m:rPr><m:b/></m:rPr><m:t>x</m:t></m:r></m:e><m:sub><m:r><m:t>k</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t>) ) + Ω(</m:t></m:r>
      <m:sSub><m:e><m:r><m:t>f</m:t></m:r></m:e><m:sub><m:r><m:t>m</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t>)</m:t></m:r>
    ''',
    8: '''
      <m:r><m:t>Ω(</m:t></m:r>
      <m:sSub><m:e><m:r><m:t>f</m:t></m:r></m:e><m:sub><m:r><m:t>m</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t>) = γ </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>m</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> + </m:t></m:r>
      <m:f><m:num><m:r><m:t>1</m:t></m:r></m:num><m:den><m:r><m:t>2</m:t></m:r></m:den></m:f>
      <m:r><m:t> λ </m:t></m:r>
      <m:sSubSup><m:e><m:r><m:t>∑</m:t></m:r></m:e><m:sub><m:r><m:t>j=1</m:t></m:r></m:sub><m:sup><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>m</m:t></m:r></m:sub></m:sSub></m:sup></m:sSubSup>
      <m:sSup><m:sSub><m:e><m:r><m:t>w</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub><m:sup><m:r><m:t>2</m:t></m:r></m:sup></m:sSup>
      <m:r><m:t> + </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>α</m:t></m:r></m:e><m:sub><m:r><m:t>reg</m:t></m:r></m:sub></m:sSub>
      <m:sSubSup><m:e><m:r><m:t>∑</m:t></m:r></m:e><m:sub><m:r><m:t>j=1</m:t></m:r></m:sub><m:sup><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>m</m:t></m:r></m:sub></m:sSub></m:sup></m:sSubSup>
      <m:r><m:t> |</m:t></m:r>
      <m:sSub><m:e><m:r><m:t>w</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t>|</m:t></m:r>
    ''',
    9: '''
      <m:sSub><m:e><m:r><m:t>ϕ</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t>(f, </m:t></m:r>
      <m:r><m:rPr><m:b/></m:rPr><m:t>x</m:t></m:r>
      <m:r><m:t>) = </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>∑</m:t></m:r></m:e><m:sub><m:r><m:t>S ⊆ F \ {j}</m:t></m:r></m:sub></m:sSub>
      <m:f>
        <m:num><m:r><m:t>|S|! (|F| - |S| - 1)!</m:t></m:r></m:num>
        <m:den><m:r><m:t>|F|!</m:t></m:r></m:den>
      </m:f>
      <m:r><m:t> [ f(S ∪ {j}) - f(S) ]</m:t></m:r>
    ''',
    10: '''
      <m:r><m:t>f(</m:t></m:r>
      <m:r><m:rPr><m:b/></m:rPr><m:t>x</m:t></m:r>
      <m:r><m:t>) = </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>ϕ</m:t></m:r></m:e><m:sub><m:r><m:t>0</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t>(f) + </m:t></m:r>
      <m:sSubSup><m:e><m:r><m:t>∑</m:t></m:r></m:e><m:sub><m:r><m:t>j=1</m:t></m:r></m:sub><m:sup><m:r><m:t>|F|</m:t></m:r></m:sup></m:sSubSup>
      <m:sSub><m:e><m:r><m:t>ϕ</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t>(f, </m:t></m:r>
      <m:r><m:rPr><m:b/></m:rPr><m:t>x</m:t></m:r>
      <m:r><m:t>)</m:t></m:r>
    ''',
    11: '''
      <m:sSubSup><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub><m:sup><m:r><m:t>*</m:t></m:r></m:sup></m:sSubSup>
      <m:r><m:t> = logit( </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>GNPA</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> ) = ln( </m:t></m:r>
      <m:f>
        <m:num><m:sSub><m:e><m:r><m:t>GNPA</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub></m:sSub></m:num>
        <m:den><m:r><m:t>1 - </m:t></m:r><m:sSub><m:e><m:r><m:t>GNPA</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub></m:sSub></m:den>
      </m:f>
      <m:r><m:t> )</m:t></m:r>
    ''',
    12: '''
      <m:sSubSup><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>i,t+1</m:t></m:r></m:sub><m:sup><m:r><m:t>*stressed</m:t></m:r></m:sup></m:sSubSup>
      <m:r><m:t> = </m:t></m:r>
      <m:sSubSup><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub><m:sup><m:r><m:t>*</m:t></m:r></m:sup></m:sSubSup>
      <m:r><m:t> + Δ</m:t></m:r>
      <m:sSup><m:e><m:r><m:rPr><m:b/></m:rPr><m:t>X</m:t></m:r></m:e><m:sup><m:r><m:t>shock</m:t></m:r></m:sup></m:sSup>
      <m:r><m:t> </m:t></m:r>
      <m:sSup><m:e><m:r><m:rPr><m:b/></m:rPr><m:t>γ</m:t></m:r></m:e><m:sup><m:r><m:t>^</m:t></m:r></m:sup></m:sSup>
    ''',
    13: '''
      <m:sSubSup><m:e><m:r><m:t>GNPA</m:t></m:r></m:e><m:sub><m:r><m:t>i,t+1</m:t></m:r></m:sub><m:sup><m:r><m:t>stressed</m:t></m:r></m:sup></m:sSubSup>
      <m:r><m:t> = σ( </m:t></m:r>
      <m:sSubSup><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>i,t+1</m:t></m:r></m:sub><m:sup><m:r><m:t>*stressed</m:t></m:r></m:sup></m:sSubSup>
      <m:r><m:t> ) = </m:t></m:r>
      <m:f>
        <m:num><m:r><m:t>1</m:t></m:r></m:num>
        <m:den>
          <m:r><m:t>1 + </m:t></m:r>
          <m:sSup>
            <m:e><m:r><m:t>e</m:t></m:r></m:e>
            <m:sup><m:r><m:t>-</m:t></m:r><m:sSubSup><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>i,t+1</m:t></m:r></m:sub><m:sup><m:r><m:t>*stressed</m:t></m:r></m:sup></m:sSubSup></m:sup>
          </m:sSup>
        </m:den>
      </m:f>
    ''',
    14: '''
      <m:r><m:t>Δ</m:t></m:r>
      <m:sSub><m:e><m:r><m:t>NPA</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> = max( 0, ( </m:t></m:r>
      <m:sSubSup><m:e><m:r><m:t>GNPA</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub><m:sup><m:r><m:t>stressed</m:t></m:r></m:sup></m:sSubSup>
      <m:r><m:t> - </m:t></m:r>
      <m:sSubSup><m:e><m:r><m:t>GNPA</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub><m:sup><m:r><m:t>baseline</m:t></m:r></m:sup></m:sSubSup>
      <m:r><m:t> ) × </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>A</m:t></m:r></m:e><m:sub><m:r><m:t>i,t</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> )</m:t></m:r>
    ''',
    15: '''
      <m:r><m:t>Δ</m:t></m:r>
      <m:sSub><m:e><m:r><m:t>Provision</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> = Δ</m:t></m:r>
      <m:sSub><m:e><m:r><m:t>NPA</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
      <m:r><m:t> × </m:t></m:r>
      <m:sSub><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>prov</m:t></m:r></m:sub></m:sSub>
    ''',
    16: '''
      <m:sSubSup><m:e><m:r><m:t>CRAR</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub><m:sup><m:r><m:t>post</m:t></m:r></m:sup></m:sSubSup>
      <m:r><m:t> = </m:t></m:r>
      <m:f>
        <m:num>
          <m:sSubSup><m:e><m:r><m:t>K</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub><m:sup><m:r><m:t>pre</m:t></m:r></m:sup></m:sSubSup>
          <m:r><m:t> - Δ</m:t></m:r>
          <m:sSub><m:e><m:r><m:t>Provision</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
        </m:num>
        <m:den>
          <m:sSubSup><m:e><m:r><m:t>RWA</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub><m:sup><m:r><m:t>pre</m:t></m:r></m:sup></m:sSubSup>
          <m:r><m:t> × ( 1 - </m:t></m:r>
          <m:sSub><m:e><m:r><m:t>δ</m:t></m:r></m:e><m:sub><m:r><m:t>RWA</m:t></m:r></m:sub></m:sSub>
          <m:r><m:t> )</m:t></m:r>
        </m:den>
      </m:f>
      <m:r><m:t> × 100</m:t></m:r>
    '''
}

doc = docx.Document()
for num, xml in eq_omml.items():
    p = doc.add_paragraph()
    elm = create_omml_equation(xml)
    p._p.append(elm)

doc.save('scratch/test_all_omml.docx')
doc_check = docx.Document('scratch/test_all_omml.docx')
print('Successfully verified', len(doc_check.paragraphs), 'OMML equations in docx!')
