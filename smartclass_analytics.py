"""
SmartClass Analytics - Sistema Inteligente de Gestão Acadêmica
Leitura, processamento e relatórios de dados de alunos.
"""

import json
import os
import sys


if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# 1. LEITURA E IMPORTAÇÃO DOS DADOS

def ler_txt(caminho: str = None) -> list[dict]:
    if caminho is None:
        caminho = os.path.join(BASE_DIR, "entrada_alunos.txt")
    """Lê arquivo TXT e retorna lista de dicionários com dados dos alunos."""
    alunos = []
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if not linha:
                    continue

              
                partes = linha.split(" - ")           
                id_aluno = int(partes[0].strip())
                nome     = partes[1].strip()
                curso    = partes[2].strip()
                nota     = float(partes[3].split(":")[1].strip())  

                alunos.append({"id": id_aluno, "nome": nome, "curso": curso, "nota": nota})

    except FileNotFoundError:
        print(f"[ERRO] Arquivo '{caminho}' não encontrado.")
    return alunos


def ler_json(caminho: str = None) -> list[dict]:
    if caminho is None:
        caminho = os.path.join(BASE_DIR, "entrada_alunos.json")
    """Lê arquivo JSON e retorna lista de dicionários com dados dos alunos."""
    alunos = []
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            for item in dados:
                alunos.append({
                    "id":    int(item["id"]),
                    "nome":  item["nome"],
                    "curso": item["curso"],
                    "nota":  float(item["nota"])
                })
    except FileNotFoundError:
        print(f"[ERRO] Arquivo '{caminho}' não encontrado.")
    except json.JSONDecodeError:
        print(f"[ERRO] Formato inválido no arquivo '{caminho}'.")
    return alunos


def carregar_alunos() -> list[dict]:
    """Combina dados do TXT e do JSON em uma única lista."""
    alunos = ler_txt() + ler_json()
    return alunos

# 2. MENU INTERATIVO


def exibir_menu() -> None:
    """Imprime o menu de opções."""
    print("""

    SmartClass Analytics - Menu       

  1 - Exibir todos os alunos          
  2 - Calcular media geral            
  3 - Exibir maior e menor nota       
  4 - Exibir aprovados e reprovados   
  5 - Buscar aluno por nota           
  6 - Buscar aluno por curso          
  7 - Gerar relatorio JSON            
  8 - Exportar relatorio TXT          
  0 - Encerrar sistema                
""")


def menu(alunos: list[dict]) -> None:
    """Loop principal do menu interativo."""
    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            exibir_todos(alunos)

        elif opcao == "2":
            exibir_media(alunos)

        elif opcao == "3":
            exibir_maior_menor(alunos)

        elif opcao == "4":
            exibir_aprovados_reprovados(alunos)

        elif opcao == "5":
            try:
                nota = float(input("Digite a nota para buscar: "))
                resultado = buscar_nota(alunos, nota)
                print(f"\nNota buscada: {resultado['nota_buscada']}")
                print(f"Ocorrências encontradas: {resultado['quantidade']}")
                for oc in resultado["ocorrencias"]:
                    print(f"  Posição {oc['posicao']}: {oc['nome']} - {oc['nota']}")
                if resultado["quantidade"] == 0:
                    print("  Nenhum aluno encontrado com essa nota.")
            except ValueError:
                print("[ERRO] Digite um valor numérico válido.")

        elif opcao == "6":
            curso = input("Digite o curso (ADS / SI / CC): ").strip()
            resultado = buscar_curso(alunos, curso)
            if resultado:
                print(f"\nAlunos do curso '{curso.upper()}':")
                for a in resultado:
                    print(f"  {a['nome']} - Nota: {a['nota']}")
            else:
                print(f"Nenhum aluno encontrado para o curso '{curso}'.")

        elif opcao == "7":
            gerar_relatorio_json(alunos)

        elif opcao == "8":
            exportar_txt(alunos)

        elif opcao == "0":
            print("\nSistema encerrado. Até logo!")
            break

        else:
            print("[AVISO] Opção inválida. Tente novamente.")

        input("\nPressione Enter para continuar...")



# 3. FUNÇÕES OBRIGATÓRIAS DE PROCESSAMENTO


def calcular_media(alunos: list[dict]) -> float:
    """Retorna a média geral das notas."""
    if not alunos:
        return 0.0
    return sum(a["nota"] for a in alunos) / len(alunos)


def buscar_nota(alunos: list[dict], nota: float) -> dict:
    """
    Busca alunos com a nota informada.
    Retorna quantidade de ocorrências, posições na lista e nomes.
    """
    ocorrencias = [
        {"posicao": i, "nome": a["nome"], "nota": a["nota"]}
        for i, a in enumerate(alunos)
        if a["nota"] == nota
    ]
    return {
        "nota_buscada": nota,
        "quantidade": len(ocorrencias),
        "ocorrencias": ocorrencias
    }


def buscar_curso(alunos: list[dict], curso: str) -> list[dict]:
    """Filtra e retorna alunos do curso informado (case-insensitive)."""
    return [a for a in alunos if a["curso"].upper() == curso.upper()]


def gerar_relatorio_json(alunos: list[dict], caminho: str = None) -> None:
    if caminho is None:
        caminho = os.path.join(BASE_DIR, "relatorio.json")
    """Gera relatório JSON com média, total, aprovados e reprovados."""
    aprovados   = [a for a in alunos if a["nota"] >= 6.0]
    reprovados  = [a for a in alunos if a["nota"] <  6.0]
    media       = calcular_media(alunos)

    relatorio = {
        "media":      round(media, 2),
        "total":      len(alunos),
        "aprovados":  aprovados,
        "reprovados": reprovados
    }

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=4)

    print(f"\n✔  Relatório JSON salvo em '{caminho}'.")


def exportar_txt(alunos: list[dict], caminho: str = None) -> None:
    if caminho is None:
        caminho = os.path.join(BASE_DIR, "relatorio.txt")
    """Exporta relatório em formato TXT."""
    if not alunos:
        print("[AVISO] Nenhum aluno para exportar.")
        return

    media      = calcular_media(alunos)
    maior      = max(alunos, key=lambda a: a["nota"])
    menor      = min(alunos, key=lambda a: a["nota"])
    aprovados  = [a for a in alunos if a["nota"] >= 6.0]
    reprovados = [a for a in alunos if a["nota"] <  6.0]

    linhas = [
        "===== RELATÓRIO =====",
        f"Total de alunos: {len(alunos)}",
        f"Média geral: {media:.2f}",
        "",
        "Maior nota:",
        f"  {maior['nome']} - {maior['nota']}",
        "",
        "Menor nota:",
        f"  {menor['nome']} - {menor['nota']}",
        "",
        f"Aprovados ({len(aprovados)}):",
        *[f"  {a['nome']} - {a['nota']}" for a in aprovados],
        "",
        f"Reprovados ({len(reprovados)}):",
        *[f"  {a['nome']} - {a['nota']}" for a in reprovados],
        "====================="
    ]

    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    print(f"\n✔  Relatório TXT salvo em '{caminho}'.")


# 4. PROCESSAMENTO / EXIBIÇÃO


def exibir_todos(alunos: list[dict]) -> None:
    """Exibe todos os alunos formatados."""
    if not alunos:
        print("Nenhum aluno cadastrado.")
        return
    print(f"\n{'ID':>4}  {'Nome':<20}  {'Curso':<6}  {'Nota':>5}")
    print("-" * 42)
    for a in alunos:
        print(f"{a['id']:>4}  {a['nome']:<20}  {a['curso']:<6}  {a['nota']:>5.1f}")
    print(f"\nTotal: {len(alunos)} aluno(s).")


def exibir_media(alunos: list[dict]) -> None:
    """Exibe a média geral."""
    print(f"\nMédia geral: {calcular_media(alunos):.2f}")


def exibir_maior_menor(alunos: list[dict]) -> None:
    """Exibe o aluno com maior e menor nota."""
    if not alunos:
        print("Nenhum aluno cadastrado.")
        return
    maior = max(alunos, key=lambda a: a["nota"])
    menor = min(alunos, key=lambda a: a["nota"])
    print(f"\nMaior nota: {maior['nome']} ({maior['curso']}) - {maior['nota']}")
    print(f"Menor nota: {menor['nome']} ({menor['curso']}) - {menor['nota']}")


def exibir_aprovados_reprovados(alunos: list[dict]) -> None:
    """Exibe listas de aprovados (nota >= 6) e reprovados."""
    aprovados  = [a for a in alunos if a["nota"] >= 6.0]
    reprovados = [a for a in alunos if a["nota"] <  6.0]

    print(f"\n[APROVADOS] ({len(aprovados)}):")
    for a in aprovados:
        print(f"   {a['nome']} - {a['nota']}")

    print(f"\n[REPROVADOS] ({len(reprovados)}):")
    for a in reprovados:
        print(f"   {a['nome']} - {a['nota']}")


# PONTO DE ENTRADA


if __name__ == "__main__":
    print("Carregando dados...")
    alunos = carregar_alunos()

    if not alunos:
        print("[ERRO] Nenhum dado foi carregado. Verifique os arquivos de entrada.")
    else:
        print(f"{len(alunos)} aluno(s) carregado(s) com sucesso.")
        menu(alunos)
