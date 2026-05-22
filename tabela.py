import os

# Diretório onde as tabelas serão armazenadas
DATA_DIR = os.path.join(os.getcwd(), 'data_tables')

def ensure_data_dir():
    """Garante que a pasta de dados exista."""
    os.makedirs(DATA_DIR, exist_ok=True)

def list_tables():
    """Retorna a lista de arquivos .txt na pasta de dados."""
    ensure_data_dir()
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith('.txt')]
        return sorted(files)
    except Exception as e:
        print(f"[Erro] Ao listar tabelas: {e}")
        return []

def load_table(file_name):
    """
    Carrega cabeçalhos e linhas de uma tabela.
    Retorna (headers, rows).
    - headers: lista de strings
    - rows: lista de listas com os valores
    """
    path = os.path.join(DATA_DIR, file_name)
    headers = []
    rows = []
    try:
        if not os.path.exists(path):
            return headers, rows
        with open(path, 'r', encoding='utf-8') as f:
            lines = [ln.rstrip('\n') for ln in f if ln.strip() != ""]
        if lines:
            headers = [h.strip() for h in lines[0].split(';') if h.strip() != ""]
            for line in lines[1:]:
                rows.append([v.strip() for v in line.split(';')])
    except Exception as e:
        print(f"[Erro] Ao ler tabela {file_name}: {e}")
    return headers, rows

def get_next_id(file_name):
    """
    Calcula o próximo ID automático com base nas linhas existentes.
    Procura pela coluna 'id' (case-insensitive) e retorna o maior valor + 1.
    Se não houver linhas, retorna 1.
    """
    headers, rows = load_table(file_name)

    # Encontra o índice da coluna 'id'
    id_index = next(
        (i for i, h in enumerate(headers) if h.strip().lower() == 'id'),
        None
    )

    if id_index is None:
        return None  # Tabela não possui coluna 'id'

    max_id = 0
    for row in rows:
        if id_index < len(row):
            try:
                val = int(row[id_index])
                if val > max_id:
                    max_id = val
            except ValueError:
                pass  # Ignora valores não numéricos

    return max_id + 1

def append_row_to_table(file_name, row_values):
    """Adiciona uma nova linha na tabela (arquivo)."""
    path = os.path.join(DATA_DIR, file_name)
    line = ';'.join([str(v) for v in row_values])
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
        return True
    except Exception as e:
        print(f"[Erro] Ao gravar linha em {file_name}: {e}")
        return False

def write_table_with_headers(file_name, headers_line):
    """Cria uma nova tabela com cabeçalhos na primeira linha."""
    path = os.path.join(DATA_DIR, file_name)
    try:
        if os.path.exists(path):
            return False
        with open(path, 'w', encoding='utf-8') as f:
            f.write(headers_line + '\n')
        return True
    except Exception as e:
        print(f"[Erro] Ao criar tabela {file_name}: {e}")
        return False

def print_table(headers, rows):
    """Imprime uma grade simples no console a partir de cabeçalhos e linhas."""
    if not headers:
        print("[Tabela sem cabeçalhos válidos]")
        return

    cols = len(headers)
    # determina largura de cada coluna
    widths = [len(h) for h in headers]
    for row in rows:
        for i in range(min(len(row), cols)):
            widths[i] = max(widths[i], len(str(row[i])))

    # helper para linha de separação
    sep = '+' + '+'.join(['-' * (w + 2) for w in widths]) + '+'

    # linha de cabeçalho
    header_cells = [' ' + headers[i].ljust(widths[i]) + ' ' for i in range(cols)]
    header_line = '|' + '|'.join(header_cells) + '|'

    print(sep)
    print(header_line)
    print(sep)

    # linhas de dados
    for row in rows:
        cells = []
        for i in range(cols):
            val = str(row[i]) if i < len(row) else ''
            cells.append(' ' + val.ljust(widths[i]) + ' ')
        print('|' + '|'.join(cells) + '|')
    print(sep)

def main():
    ensure_data_dir()
    while True:
        print("\n=== Mini Banco de Dados (CLI) ===")
        print("1 - Criar Tabela")
        print("2 - Gerenciar Tabela")
        print("3 - Sair")
        choice = input("Informe a opção (1/2/3): ").strip()

        if choice == '1':
            # Criar Tabela
            name = input("Nome da Tabela (sem extensão): ").strip()
            headers_line = input("Cabeçalhos (separados por ;) : ").strip()

            if not name:
                print("[Erro] Informe o nome da tabela.")
                continue
            if any(ch in name for ch in '/\\;'):
                print("[Erro] O nome da tabela não pode conter /, \\, ou ;.")
                continue
            if not headers_line:
                print("[Erro] Informe os cabeçalhos (separados por ;) .")
                continue

            filename = f"{name}.txt"
            path = os.path.join(DATA_DIR, filename)
            if os.path.exists(path):
                print("[Erro] Já existe uma tabela com esse nome.")
                continue

            headers = [h.strip() for h in headers_line.split(';') if h.strip() != ""]
            if not headers:
                print("[Erro] Cabeçalhos inválidos. Adicione pelo menos um cabeçalho.")
                continue

            # Avisa o usuário caso não haja coluna 'id'
            has_id = any(h.lower() == 'id' for h in headers)
            if not has_id:
                print("[Aviso] Nenhuma coluna 'id' detectada. O ID automático só funciona quando um dos cabeçalhos se chama 'id'.")

            if write_table_with_headers(filename, ';'.join(headers)):
                print(f"[Sucesso] Tabela '{name}' criada com cabeçalhos: {', '.join(headers)}")
            else:
                print("[Erro] Falha ao criar a tabela. Verifique permissões da pasta.")

        elif choice == '2':
            # Gerenciar Tabela
            tables = list_tables()
            if not tables:
                print("[Info] Não há tabelas criadas ainda. Use a opção 1 para criar uma.")
                continue

            print("\nTabelas disponíveis:")
            for idx, f in enumerate(tables, 1):
                print(f"  {idx}. {f}")
            sel = input("Selecione uma tabela pelo número (ou 'q' para voltar): ").strip()
            if sel.lower() == 'q':
                continue
            try:
                idx = int(sel) - 1
                if idx < 0 or idx >= len(tables):
                    raise ValueError
                chosen = tables[idx]
            except ValueError:
                print("[Erro] Seleção inválida.")
                continue

            # submenu da tabela escolhida
            while True:
                print(f"\n[Tabela] {chosen}")
                print("1 - Visualizar Dados")
                print("2 - Inserir Linha")
                print("3 - Voltar")
                sub = input("Opção: ").strip()

                if sub == '1':
                    headers, rows = load_table(chosen)
                    print_table(headers, rows)

                elif sub == '2':
                    headers, _ = load_table(chosen)
                    if not headers:
                        print("[Erro] Tabela sem cabeçalhos válidos.")
                        continue

                    # Verifica se existe coluna 'id' e obtém próximo valor
                    id_index = next(
                        (i for i, h in enumerate(headers) if h.strip().lower() == 'id'),
                        None
                    )
                    next_id = get_next_id(chosen) if id_index is not None else None

                    if next_id is not None:
                        print(f"[Info] ID gerado automaticamente: {next_id}")

                    new_row = []
                    for i, h in enumerate(headers):
                        # Pula o campo 'id' — será preenchido automaticamente
                        if i == id_index:
                            new_row.append(next_id)
                            continue
                        v = input(f"{h}: ").strip()
                        new_row.append(v)

                    if append_row_to_table(chosen, new_row):
                        print("[Sucesso] Linha inserida com sucesso.")
                    else:
                        print("[Erro] Falha ao inserir a linha.")

                elif sub == '3':
                    break
                else:
                    print("[Erro] Opção inválida.")

        elif choice == '3':
            print("Encerrando o programa.")
            break
        else:
            print("[Erro] Opção inválida. Tente 1, 2 ou 3.")

if __name__ == "__main__":
    main()
