from groq import Groq
from dotenv import load_dotenv
import os
import sys
import termios
termios.tcflush(sys.stdin, termios.TCIFLUSH)

load_dotenv()

def ler_arquivo(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return ""

shared = ler_arquivo("modes/_shared.md")
oferta = ler_arquivo("modes/oferta.md")
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

print("Cole a descrição da vaga e pressione Enter duas vezes:")
linhas = []
while True:
    linha = input()
    if linha == "":
        break
    linhas.append(linha)

vaga = "\n".join(linhas)

instrucao_extra = """IMPORTANTE: Seja honesto e rigoroso na avaliação. 
Se o candidato não tem os requisitos obrigatórios da vaga, o score deve ser baixo (abaixo de 3.0).
Nunca infle o score para parecer positivo. O candidato precisa de feedback real para tomar boas decisões. E por favor responde em Português do Brasil!"""

client = Groq(api_key=os.getenv("GROQ_TOKEN"))

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{instrucao_extra}Vaga para avaliar:\n{vaga}"}
    ]
)

print("\n" + response.choices[0].message.content)
os.system("stty sane 2>/dev/null")


