from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq
from flask import stream_with_context, Response
import os

load_dotenv()

def ler_arquivo(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return ""

app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/avaliar", methods=["POST"])
def avaliar():
    data = request.get_json()
    vaga = data.get("vaga")
    cv = ler_arquivo("cv.md")

    
    system_prompt = f"""
Você é um avaliador rigoroso de vagas de emprego. Analise a vaga e o CV do candidato.

REGRAS:
- Se o candidato NÃO tem os requisitos OBRIGATÓRIOS, score deve ser abaixo de 2.0
- Seja direto e honesto, mesmo que seja negativo
- Score de 1 a 5
- Se a vaga for de ESTÁGIO ou JÚNIOR, avalie POTENCIAL e vontade de aprender, não experiência profissional
- Responda em Português do Brasil
BLOCOS OBRIGATÓRIOS:
A) Resumo da vaga (arquetipo, senioridade, remoto)
B) Match com CV (liste cada requisito obrigatório: tem ou não tem)
C) Gaps críticos (o que falta e se são blockers)
D) Score final com justificativa
E) Recomendação: aplicar ou não, e por quê

CV DO CANDIDATO:
{cv}
"""
    
    instrucao_extra = """IMPORTANTE: Seja honesto e rigoroso na avaliação. 
                            Se o candidato não tem os requisitos obrigatórios da vaga, o score deve ser baixo (abaixo de 3.0).
                            Nunca infle o score para parecer positivo. O candidato precisa de feedback real para tomar boas decisões. E por favor responde em Português do Brasil!
                            - NÃO use markdown, asteriscos, hashtags ou formatação especial.
                            - Responda cada questão uma embaixo a outra, mantendo uma formatação bonita e legivel.
                            - Coloque as letras A), B), C), D), E) uma embaixo da outra alinhadas a esquerda, para cada bloco da resposta."""

    
    client = Groq(api_key=os.getenv("GROQ_TOKEN"))
    
    def gerar():
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{instrucao_extra}Analise a seguinte vaga de emprego{vaga}"}
            ],
        stream=True
    )
        for chunk in response:
            texto = chunk.choices[0].delta.content
            if texto:
                yield texto

    return Response(stream_with_context(gerar()), mimetype="text/plain")
    
if __name__ == "__main__":
    app.run(debug=True)