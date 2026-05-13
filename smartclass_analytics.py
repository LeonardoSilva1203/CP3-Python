import json
import os
import sys


if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# =============================================================
# 1. LEITURA E IMPORTAÇÃO DOS DADOS
# =============================================================

def ler_txt(caminho: str = None) -> list[dict]:
    """
    Lê o arquivo entrada_alunos.txt e retorna uma lista de dicionários.
    Cada dicionário representa um aluno com: id, nome, curso e nota.

    Exemplo de linha no TXT: 001 - João Silva - ADS - Nota: 8.5
    """

    # Se nenhum caminho for passado, usa o padrão: mesma pasta do script
    if caminho is None:
        caminho = os.path.join(BASE_DIR, "entrada_alunos.txt")

    alunos = []  # lista vazia que vai receber os alunos lidos

    try:
        # Abre o arquivo em modo leitura ("r") com encoding UTF-8
        with open(caminho, "r", encoding="utf-8") as arquivo:

            # Percorre o arquivo linha por linha
            for linha in arquivo:

                linha = linha.strip()  # remove espaços e \n das bordas

                # Pula linhas vazias (linhas em branco no arquivo)
                if not linha:
                    continue

                # Fatiamento: divide a linha pelo separador " - "
                # Resultado de "001 - João Silva - ADS - Nota: 8.5":
                # partes[0] = "001"
                # partes[1] = "João Silva"
                # partes[2] = "ADS"
                # partes[3] = "Nota: 8.5"
                partes = linha.split(" - ")

                id_aluno = int(partes[0].strip())           # "001" -> 1
                nome     = partes[1].strip()                # "João Silva"
                curso    = partes[2].strip()                # "ADS"

                # partes[3] = "Nota: 8.5" -> split(":") -> ["Nota", " 8.5"] -> [1] -> 8.5
                nota = float(partes[3].split(":")[1].strip())

                # Adiciona o aluno como dicionário na lista
                alunos.append({"id": id_aluno, "nome": nome, "curso": curso, "nota": nota})

    except FileNotFoundError:
        # Executado se o arquivo não existir no caminho informado
        print(f"[ERRO] Arquivo '{caminho}' não encontrado.")

    return alunos  # retorna a lista (pode estar vazia se houve erro)


def ler_json(caminho: str = None) -> list[dict]:
    """
    Lê o arquivo entrada_alunos.json e retorna uma lista de dicionários.
    O JSON já está estruturado com os campos: id, nome, curso, nota.
    """

    if caminho is None:
        caminho = os.path.join(BASE_DIR, "entrada_alunos.json")

    alunos = []

    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:

            # json.load() converte o conteúdo do arquivo JSON
            # em uma lista de dicionários Python automaticamente
            dados = json.load(arquivo)

            # Percorre cada item da lista lida do JSON
            for item in dados:
                alunos.append({
                    "id":    int(item["id"]),      # garante que id é inteiro
                    "nome":  item["nome"],
                    "curso": item["curso"],
                    "nota":  float(item["nota"])   # garante que nota é float
                })

    except FileNotFoundError:
        print(f"[ERRO] Arquivo '{caminho}' não encontrado.")

    except json.JSONDecodeError:
        # Executado se o arquivo existir mas o conteúdo não for JSON válido
        print(f"[ERRO] Formato inválido no arquivo '{caminho}'.")

    return alunos


def carregar_alunos() -> list[dict]:
    """
    Chama ler_txt() e ler_json() e junta os resultados em uma única lista.
    O operador + concatena duas listas em Python.
    Resultado final: lista com todos os 9 alunos (5 do TXT + 4 do JSON).
    """
    alunos = ler_txt() + ler_json()
    return alunos


# =============================================================
# 2. FUNÇÕES OBRIGATÓRIAS DE PROCESSAMENTO
# =============================================================

def calcular_media(alunos: list[dict]) -> float:
    """
    Calcula e retorna a média aritmética das notas de todos os alunos.

    sum(...) soma todas as notas usando uma expressão geradora:
    percorre cada aluno 'a' da lista e pega a["nota"].
    Divide pelo total de alunos com len(alunos).
    """
    if not alunos:
        return 0.0  # evita divisão por zero se a lista estiver vazia

    return sum(a["nota"] for a in alunos) / len(alunos)


def buscar_nota(alunos: list[dict], nota: float) -> dict:
    """
    Busca todos os alunos que possuem exatamente a nota informada.

    enumerate(alunos) retorna pares (índice, aluno), permitindo
    saber a posição de cada aluno na lista.

    Retorna um dicionário com:
    - nota_buscada: a nota que foi pesquisada
    - quantidade: quantos alunos têm essa nota
    - ocorrencias: lista com posição e nome de cada aluno encontrado
    """

    # List comprehension: cria a lista apenas com alunos cuja nota bate
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
    """
    Filtra e retorna apenas os alunos do curso informado.

    .upper() converte para maiúsculas antes de comparar,
    garantindo que "ads", "ADS" e "Ads" sejam tratados igual (case-insensitive).
    """
    return [a for a in alunos if a["curso"].upper() == curso.upper()]


def gerar_relatorio_json(alunos: list[dict], caminho: str = None) -> None:
    """
    Gera um arquivo relatorio.json na mesma pasta do script.

    O relatório contém:
    - media: média geral arredondada com 2 casas decimais
    - total: quantidade total de alunos
    - aprovados: lista completa dos alunos com nota >= 6.0
    - reprovados: lista completa dos alunos com nota < 6.0
    """

    if caminho is None:
        caminho = os.path.join(BASE_DIR, "relatorio.json")

    # Separa aprovados e reprovados usando list comprehension com condição
    aprovados  = [a for a in alunos if a["nota"] >= 6.0]
    reprovados = [a for a in alunos if a["nota"] <  6.0]
    media      = calcular_media(alunos)

    # Monta o dicionário que será salvo no JSON
    relatorio = {
        "media":      round(media, 2),  # round() arredonda para 2 casas
        "total":      len(alunos),
        "aprovados":  aprovados,
        "reprovados": reprovados
    }

    # Abre o arquivo em modo escrita ("w") - cria se não existir, sobrescreve se existir
    with open(caminho, "w", encoding="utf-8") as f:
        # json.dump() converte o dicionário Python para texto JSON e grava no arquivo
        # ensure_ascii=False: mantém acentos no lugar (não converte para \uXXXX)
        # indent=4: formata com indentação de 4 espaços para facilitar leitura
        json.dump(relatorio, f, ensure_ascii=False, indent=4)

    print(f"\n[OK] Relatorio JSON salvo em '{caminho}'.")


def exportar_txt(alunos: list[dict], caminho: str = None) -> None:
    """
    Gera um arquivo relatorio.txt com um resumo formatado dos dados.

    max() e min() percorrem a lista e retornam o dicionário do aluno
    com a maior/menor nota, usando key=lambda para indicar qual campo comparar.

    O operador * (unpacking) dentro da lista 'linhas' expande uma
    list comprehension como itens individuais da lista maior.
    """

    if caminho is None:
        caminho = os.path.join(BASE_DIR, "relatorio.txt")

    if not alunos:
        print("[AVISO] Nenhum aluno para exportar.")
        return

    media = calcular_media(alunos)

    # lambda a: a["nota"] diz para max/min usar o campo "nota" como critério
    maior = max(alunos, key=lambda a: a["nota"])
    menor = min(alunos, key=lambda a: a["nota"])

    aprovados  = [a for a in alunos if a["nota"] >= 6.0]
    reprovados = [a for a in alunos if a["nota"] <  6.0]

    # Monta a lista de linhas do relatório
    # O * antes de uma list comprehension "desempacota" os itens dentro da lista maior
    linhas = [
        "===== RELATORIO =====",
        f"Total de alunos: {len(alunos)}",
        f"Media geral: {media:.2f}",       # :.2f formata com 2 casas decimais
        "",
        "Maior nota:",
        f"  {maior['nome']} - {maior['nota']}",
        "",
        "Menor nota:",
        f"  {menor['nome']} - {menor['nota']}",
        "",
        f"Aprovados ({len(aprovados)}):",
        *[f"  {a['nome']} - {a['nota']}" for a in aprovados],   # expande a lista
        "",
        f"Reprovados ({len(reprovados)}):",
        *[f"  {a['nome']} - {a['nota']}" for a in reprovados],  # expande a lista
        "====================="
    ]

    with open(caminho, "w", encoding="utf-8") as f:
        # "\n".join(linhas) une todos os itens da lista com quebra de linha entre eles
        f.write("\n".join(linhas))

    print(f"\n[OK] Relatorio TXT salvo em '{caminho}'.")


# =============================================================
# 3. FUNÇÕES DE EXIBIÇÃO NO TERMINAL
# =============================================================

def exibir_todos(alunos: list[dict]) -> None:
    """
    Exibe todos os alunos em formato de tabela alinhada.

    As f-strings com :>4, :<20, etc. controlam o alinhamento e largura
    de cada coluna para que a tabela fique organizada no terminal:
    >4  = alinha à direita em 4 caracteres (ID)
    <20 = alinha à esquerda em 20 caracteres (Nome)
    >5  = alinha à direita em 5 caracteres (Nota)
    """
    if not alunos:
        print("Nenhum aluno cadastrado.")
        return

    # Cabeçalho da tabela com colunas alinhadas
    print(f"\n{'ID':>4}  {'Nome':<20}  {'Curso':<6}  {'Nota':>5}")
    print("-" * 42)  # linha separadora

    for a in alunos:
        # :>5.1f = alinha à direita em 5 caracteres com 1 casa decimal
        print(f"{a['id']:>4}  {a['nome']:<20}  {a['curso']:<6}  {a['nota']:>5.1f}")

    print(f"\nTotal: {len(alunos)} aluno(s).")


def exibir_media(alunos: list[dict]) -> None:
    """Chama calcular_media() e exibe o resultado formatado no terminal."""
    print(f"\nMedia geral: {calcular_media(alunos):.2f}")


def exibir_maior_menor(alunos: list[dict]) -> None:
    """
    Usa max() e min() com lambda para encontrar os alunos
    com maior e menor nota e exibe seus dados.
    """
    if not alunos:
        print("Nenhum aluno cadastrado.")
        return

    maior = max(alunos, key=lambda a: a["nota"])
    menor = min(alunos, key=lambda a: a["nota"])

    print(f"\nMaior nota: {maior['nome']} ({maior['curso']}) - {maior['nota']}")
    print(f"Menor nota: {menor['nome']} ({menor['curso']}) - {menor['nota']}")


def exibir_aprovados_reprovados(alunos: list[dict]) -> None:
    """
    Separa a lista em dois grupos usando list comprehension com condição:
    - aprovados:  nota >= 6.0
    - reprovados: nota <  6.0
    Exibe cada grupo com nome e nota.
    """
    aprovados  = [a for a in alunos if a["nota"] >= 6.0]
    reprovados = [a for a in alunos if a["nota"] <  6.0]

    print(f"\n[APROVADOS] ({len(aprovados)}):")
    for a in aprovados:
        print(f"   {a['nome']} - {a['nota']}")

    print(f"\n[REPROVADOS] ({len(reprovados)}):")
    for a in reprovados:
        print(f"   {a['nome']} - {a['nota']}")


# =============================================================
# 4. MENU INTERATIVO
# =============================================================

def exibir_menu() -> None:
    """Imprime o menu de opções no terminal usando uma string multilinha."""
    print("""
+======================================+
|    SmartClass Analytics - Menu       |
+======================================+
|  1 - Exibir todos os alunos          |
|  2 - Calcular media geral            |
|  3 - Exibir maior e menor nota       |
|  4 - Exibir aprovados e reprovados   |
|  5 - Buscar aluno por nota           |
|  6 - Buscar aluno por curso          |
|  7 - Gerar relatorio JSON            |
|  8 - Exportar relatorio TXT          |
|  0 - Encerrar sistema                |
+======================================+""")


def menu(alunos: list[dict]) -> None:
    """
    Loop principal do sistema.

    'while True' mantém o menu rodando indefinidamente até
    o usuário digitar 0, momento em que o 'break' encerra o loop.

    input() aguarda o usuário digitar algo e pressionar Enter.
    .strip() remove espaços acidentais digitados antes ou depois do número.
    """
    while True:
        exibir_menu()
        opcao = input("Escolha uma opcao: ").strip()

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
                # float() converte o texto digitado para número decimal
                # Se o usuário digitar letras, lança ValueError e cai no except
                nota = float(input("Digite a nota para buscar: "))
                resultado = buscar_nota(alunos, nota)
                print(f"\nNota buscada: {resultado['nota_buscada']}")
                print(f"Ocorrencias encontradas: {resultado['quantidade']}")
                for oc in resultado["ocorrencias"]:
                    print(f"  Posicao {oc['posicao']}: {oc['nome']} - {oc['nota']}")
                if resultado["quantidade"] == 0:
                    print("  Nenhum aluno encontrado com essa nota.")
            except ValueError:
                print("[ERRO] Digite um valor numerico valido.")

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
            print("\nSistema encerrado. Ate logo!")
            break  # encerra o while True

        else:
            # Qualquer entrada que não seja 0-8 cai aqui
            print("[AVISO] Opcao invalida. Tente novamente.")

        # Pausa antes de mostrar o menu novamente,
        # para o usuário ter tempo de ler o resultado
        input("\nPressione Enter para continuar...")


# =============================================================
# PONTO DE ENTRADA DO PROGRAMA
# =============================================================

# Este bloco só executa quando o arquivo é rodado diretamente
# (ex: python smartclass_analytics.py).
# Se o arquivo for importado por outro script, este bloco é ignorado.
if __name__ == "__main__":
    print("Carregando dados...")

    # Carrega todos os alunos dos dois arquivos
    alunos = carregar_alunos()

    if not alunos:
        # Se a lista vier vazia (arquivos não encontrados ou inválidos), encerra
        print("[ERRO] Nenhum dado foi carregado. Verifique os arquivos de entrada.")
    else:
        print(f"{len(alunos)} aluno(s) carregado(s) com sucesso.")
        menu(alunos)  # inicia o menu passando a lista de alunos