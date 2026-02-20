import re, json, os

SRC = r"f:\02. GESTIÓN LOGÍSTICA Y COMERCIAL\EXÁMENES MIXTO - Gestión logística y comercial .txt"
OUT = r"f:\02. GESTIÓN LOGÍSTICA Y COMERCIAL\EXAMEN GITHUB\data"
os.makedirs(OUT, exist_ok=True)

with open(SRC, encoding="utf-8") as f:
    raw = f.read()

# Split into tema blocks using the Examen: header
parts = re.split(r'(?:examen_\w+\s*=\s*""")Examen:\s*', raw)
parts = [p for p in parts if p.strip() and '--- PREGUNTA' in p]

letter_to_idx = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

tema_titles = {
    1: "LA LOGÍSTICA",
    2: "GESTIÓN DE STOCKS. MÉTODOS Y SISTEMAS DE GESTIÓN",
    3: "SELECCIÓN DE PROVEEDORES",
    4: "RELACIÓN CON LOS PROVEEDORES. PROCESO DOCUMENTAL",
    5: "NEGOCIACIÓN CON PROVEEDORES",
    6: "DISTINTOS MERCADOS Y CÓMO NEGOCIAR CON ELLOS",
    7: "EL PROCESO DE APROVISIONAMIENTO",
    8: "INCIDENCIAS EN LA RECEPCIÓN DE MERCANCÍAS Y EN ALMACENAJE",
    9: "NORMATIVA SOBRE ENVASE, EMBALAJE Y ETIQUETADO DE PRODUCTOS",
    10: "LA TRAZABILIDAD",
    11: "LA CALIDAD EN LA LOGÍSTICA",
    12: "LOS COSTES LOGÍSTICOS",
    14: "LA ATENCIÓN AL CLIENTE EN LA LOGÍSTICA",
    15: "RESPONSABILIDAD SOCIAL CORPORATIVA EN LA LOGÍSTICA Y EL ALMACENAJE",
}

for block in parts:
    # Detect tema number from block's first line
    first_line = block.strip().split('\n')[0].strip()
    tema_match = re.search(r'Tema\s+(\d+)', first_line, re.IGNORECASE)
    if not tema_match:
        continue
    tema_num = int(tema_match.group(1))
    
    # Get the subtitle from the title mapping, or extract from the block
    subtitle = tema_titles.get(tema_num, first_line.split('.')[-1].strip().upper())
    title = f"GESTIÓN LOGÍSTICA Y COMERCIAL - TEMA {tema_num}: {subtitle}"
    
    # Find all questions
    questions = re.split(r'---\s*PREGUNTA\s+\d+\s*---', block)
    questions = [q.strip() for q in questions if q.strip() and 'A.' in q]
    
    items = []
    for q_block in questions:
        lines = [l.strip() for l in q_block.split('\n') if l.strip()]
        if not lines:
            continue
        
        q_text_parts = []
        opt_lines = []
        expl = ""
        correct = ""
        
        phase = 'question'
        for line in lines:
            if phase == 'question':
                if re.match(r'^A\.?\s', line):
                    phase = 'options'
                    opt_lines.append(line)
                else:
                    if line.startswith('#') or line.startswith('examen') or line.startswith('"""'):
                        continue
                    q_text_parts.append(line)
            elif phase == 'options':
                if line.startswith('Explicación:') or line.startswith('Explicacion:'):
                    expl = line.split(':', 1)[1].strip()
                    phase = 'after'
                elif line.startswith('Respuesta correcta:'):
                    correct = line.split(':')[1].strip()[0]
                    phase = 'done'
                else:
                    opt_lines.append(line)
            elif phase == 'after':
                if line.startswith('Respuesta correcta:'):
                    correct = line.split(':')[1].strip()[0]
                    phase = 'done'
        
        question_text = ' '.join(q_text_parts).strip()
        if not question_text:
            continue
        
        options = []
        for ol in opt_lines:
            opt_text = re.sub(r'^[A-D][.)]\s*', '', ol).strip()
            options.append(opt_text)
        
        if len(options) != 4:
            continue
        
        correct_idx = letter_to_idx.get(correct, 0)
        
        items.append({
            "question": question_text,
            "options": options,
            "correctAnswer": correct_idx,
            "explanation": expl
        })
    
    if items:
        data = {"title": title, "items": items}
        out_file = os.path.join(OUT, f"db_tema_{tema_num}.json")
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Tema {tema_num}: {len(items)} preguntas -> {out_file}")
    else:
        print(f"Tema {tema_num}: NO se encontraron preguntas")

print("\n¡Listo!")
