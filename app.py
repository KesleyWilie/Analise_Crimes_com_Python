import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

# Importações para manipulação do banco de dados usando SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

######################################################################
# 1. Função para Carregar e Limpar a Base de Dados CSV                #
######################################################################
def load_and_clean_data(csv_path):
    """
    Lê o arquivo CSV, exibe informações iniciais, padroniza os dados e trata dados não conformes.
    
    Passos:
      - Leitura do arquivo CSV (usando o separador ';').
      - Exibe informações iniciais para identificação do esquema original.
      - Padroniza os nomes dos municípios para MAIÚSCULAS e remove espaços.
      - Converte a coluna 'rmbh' ("SIM"/"NÃO") para valores booleanos.
      - Converte as colunas numéricas (registros, mes, ano, risp) para o tipo adequado.
      - Remove linhas com dados essenciais (nulos) e garante que os valores numéricos estejam corretos.
      - Por fim, padroniza a coluna de tipos de crime, convertendo-a para MAIÚSCULAS (sem mapeamento de sinônimos).
    """
    # Leitura do CSV
    df = pd.read_csv(csv_path, sep=';')
    
    print("=== Esquema Original ===")
    print(df.info())
    print(df.head())
    
    # Padronização dos textos:
    # - Converte o nome do município para MAIÚSCULAS e remove espaços extras.
    df["municipio"] = df["municipio"].str.strip().str.upper()
    
    # - Para a coluna 'natureza' (tipo de crime), remove espaços.
    df["natureza"] = df["natureza"].str.strip()
    
    # Tratamento da coluna 'rmbh': converte "SIM"/"NÃO" para booleanos (True/False)
    df["rmbh"] = df["rmbh"].str.strip().str.upper().map({'SIM': True, 'NÃO': False})
    
    # Conversão de colunas numéricas:
    # Converte "registros", "mes", "ano" e "risp" para valores numéricos.
    df["registros"] = pd.to_numeric(df["registros"], errors='coerce')
    df["cod_municipio"] = df["cod_municipio"].astype(str).str.strip()  # Mantém os códigos como string
    df["mes"] = pd.to_numeric(df["mes"], errors='coerce')
    df["ano"] = pd.to_numeric(df["ano"], errors='coerce')
    df["risp"] = pd.to_numeric(df["risp"], errors='coerce').astype(int)
    
    # Remoção de linhas com dados essenciais nulos
    df = df.dropna(subset=["registros", "mes", "ano", "risp"])
    
    # Garante os tipos corretos dos dados numéricos convertendo-os para int
    df["registros"] = df["registros"].astype(int)
    df["mes"] = df["mes"].astype(int)
    df["ano"] = df["ano"].astype(int)
    
    ########################################################
    # Padronização dos Tipos de Crime
    ########################################################
    # Aqui, optamos por apenas converter a coluna "natureza" para MAIÚSCULAS,
    # eliminando qualquer mapeamento de sinônimos. Isso simplifica a padronização.
    df["natureza_padronizada"] = df["natureza"].str.upper()
    
    print("\nNaturezas Originais:", df["natureza"].unique())
    print("Naturezas Padronizadas:", df["natureza_padronizada"].unique())
    
    return df

######################################################################
# 2. Criação e População do Banco de Dados Normalizado (MySQL via XAMPP) #
######################################################################
def create_normalized_database(df):
    """
    Cria as tabelas normalizadas e insere os dados apenas se eles ainda não existirem.
    
    Modelagem:
      - Tabela 'risp': Armazena as Regiões Integradas de Segurança Pública.
      - Tabela 'municipio': Armazena os municípios e referencia a RISP.
      - Tabela 'tipo_crime': Armazena os tipos de crime padronizados.
      - Tabela 'crime': Armazena cada ocorrência, referenciando 'municipio' e 'tipo_crime'.
    
    Normalização aplicada:
      * 1FN: Cada campo é atômico (não há listas ou conjuntos em um mesmo atributo).
      * 2FN: Todos os atributos não-chave dependem integralmente da chave primária de cada tabela.
      * 3FN: Não há dependências transitivas; atributos derivados foram isolados.
    
    **Observação para a apresentação:**
      Se já houver registros na tabela 'crime', a inserção é pulada para acelerar a execução.
    """
    # Conexão com MySQL – atualize usuário, senha e nome do banco conforme sua configuração
    engine = create_engine("mysql+pymysql://root:@localhost/crimes_mg", echo=True)
    Base = declarative_base()
    
    #######################################
    # Definição das Tabelas Normalizadas
    #######################################
    
    # ---------------------- Tabela RISP -----------------------
    # Armazena as Regiões Integradas de Segurança Pública.
    # - 1FN: Os atributos 'id' e 'descricao' são atômicos.
    # - 2FN: 'descricao' depende completamente do 'id'.
    # - 3FN: Não há dependências transitivas.
    class Risp(Base):
        __tablename__ = 'risp'
        id = Column(Integer, primary_key=True)  # Código da RISP (extraído do CSV)
        descricao = Column(String(100), nullable=False)  # Ex: "RISP X"
        # Relacionamento: cada RISP pode ter vários municípios
        municipios = relationship("Municipio", back_populates="risp")
    
    # ---------------------- Tabela Municipio ------------------
    # Armazena os municípios e faz referência à RISP.
    # - 1FN: Os atributos 'cod_municipio', 'nome' e 'risp_id' são atômicos.
    # - 2FN: 'nome' e 'risp_id' dependem integralmente da chave primária 'cod_municipio'.
    # - 3FN: Não há dependências transitivas; os dados de endereço estão separados.
    class Municipio(Base):
        __tablename__ = 'municipio'
        cod_municipio = Column(String(10), primary_key=True)  # Código do município
        nome = Column(String(100), nullable=False)
        risp_id = Column(Integer, ForeignKey('risp.id'), nullable=False)
        # Relacionamentos: cada município pertence a uma RISP e possui várias ocorrências (crimes)
        risp = relationship("Risp", back_populates="municipios")
        crimes = relationship("Crime", back_populates="municipio")
    
    # ---------------------- Tabela TipoCrime ------------------
    # Armazena os tipos de crime padronizados.
    # - 1FN: Os atributos 'id' e 'nome' são atômicos.
    # - 2FN: 'nome' depende completamente da chave primária 'id'.
    # - 3FN: Não há dependências transitivas.
    class TipoCrime(Base):
        __tablename__ = 'tipo_crime'
        id = Column(Integer, primary_key=True, autoincrement=True)
        nome = Column(String(100), unique=True, nullable=False)  # Tipo de crime padronizado (MAIÚSCULAS)
        # Relacionamento: cada tipo de crime pode estar associado a vários registros de crime
        crimes = relationship("Crime", back_populates="tipo_crime")
    
    # ---------------------- Tabela Crime ----------------------
    # Armazena cada ocorrência de crime, referenciando o município e o tipo de crime.
    # - 1FN: Os atributos 'mes', 'ano', 'registros', 'rmbh', 'municipio_id' e 'tipo_crime_id' são atômicos.
    # - 2FN: Todos os atributos dependem integralmente da chave primária 'id'.
    # - 3FN: Não há dependências transitivas; as referências para município e tipo de crime são feitas por chaves estrangeiras.
    class Crime(Base):
        __tablename__ = 'crime'
        id = Column(Integer, primary_key=True, autoincrement=True)
        mes = Column(Integer, nullable=False)
        ano = Column(Integer, nullable=False)
        registros = Column(Integer, nullable=False)
        rmbh = Column(Boolean, nullable=False)
        municipio_id = Column(String(10), ForeignKey('municipio.cod_municipio'), nullable=False)
        tipo_crime_id = Column(Integer, ForeignKey('tipo_crime.id'), nullable=False)
        # Unique constraint para evitar duplicatas: combinação única de município, tipo de crime, mês e ano
        __table_args__ = (UniqueConstraint('municipio_id', 'tipo_crime_id', 'mes', 'ano', name='_crime_uc'),)
        # Relacionamentos: cada crime se relaciona com um município e um tipo de crime
        municipio = relationship("Municipio", back_populates="crimes")
        tipo_crime = relationship("TipoCrime", back_populates="crimes")
    
    # Criação das tabelas no banco de dados (create_all ignora tabelas já existentes)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Para acelerar a execução (ideal para a apresentação), se já houver registros na tabela 'crime',
    # pula a inserção dos dados.
    if session.query(Crime).first() is not None:
        print("Dados já existem no banco de dados. Pulando inserção.")
        session.close()
        return
    
    ####################################################
    # Inserção Condicional na Tabela RISP
    ####################################################
    # Para cada código único de RISP presente no CSV, verifica se já existe;
    # se não existir, insere-o.
    risp_values = df['risp'].unique()
    for r in risp_values:
        exists = session.query(Risp).filter_by(id=int(r)).first()
        if not exists:
            new_risp = Risp(id=int(r), descricao=f"RISP {r}")
            session.add(new_risp)
    session.commit()
    
    ####################################################
    # Inserção Condicional na Tabela Municipio
    ####################################################
    # Para cada município único (com código, nome e risp), verifica se já existe; se não, insere-o.
    municipios = df[['cod_municipio', 'municipio', 'risp']].drop_duplicates()
    for _, row in municipios.iterrows():
        exists = session.query(Municipio).filter_by(cod_municipio=row['cod_municipio']).first()
        if not exists:
            new_municipio = Municipio(
                cod_municipio=row['cod_municipio'],
                nome=row['municipio'],
                risp_id=int(row['risp'])
            )
            session.add(new_municipio)
    session.commit()
    
    ####################################################
    # Inserção Condicional na Tabela TipoCrime
    ####################################################
    # Para cada tipo de crime padronizado, verifica se já existe; se não, insere-o.
    tipos_unicos = df["natureza_padronizada"].unique()
    tipo_crime_dict = {}
    for nome in tipos_unicos:
        existing = session.query(TipoCrime).filter_by(nome=nome).first()
        if not existing:
            new_tc = TipoCrime(nome=nome)
            session.add(new_tc)
            session.commit()  # Necessário para obter o ID gerado
            tipo_crime_dict[nome] = new_tc.id
        else:
            tipo_crime_dict[nome] = existing.id
    print("Tabela 'tipo_crime' populada:", tipo_crime_dict)
    
    ####################################################
    # Inserção Condicional na Tabela Crime
    ####################################################
    # Para cada registro de crime no CSV, verifica se a combinação (municipio, tipo_crime, mes, ano) já existe.
    # Se não existir, insere o registro.
    for _, row in df.iterrows():
        exists = session.query(Crime).filter_by(
            municipio_id = row['cod_municipio'],
            tipo_crime_id = tipo_crime_dict.get(row['natureza_padronizada']),
            mes = row['mes'],
            ano = row['ano']
        ).first()
        if not exists:
            new_crime = Crime(
                mes = row['mes'],
                ano = row['ano'],
                registros = row['registros'],
                rmbh = row['rmbh'],
                municipio_id = row['cod_municipio'],
                tipo_crime_id = tipo_crime_dict.get(row['natureza_padronizada'])
            )
            session.add(new_crime)
    session.commit()
    session.close()
    print("Novos dados inseridos no banco de dados 'crimes_db' (registros já existentes foram ignorados).")

######################################################################
# 3. Funções de Visualização e Análise Interativas                    #
######################################################################
def plot_top_municipios(df):
    """
    Exibe os 10 municípios com maior incidência de crimes.
    
    - Agrupa os dados por município e soma os registros.
    - Ordena os municípios em ordem decrescente e seleciona os 10 principais.
    - Plota um gráfico de pizza.
    """
    crimes_por_municipio = df.groupby("municipio")["registros"].sum().reset_index()
    top_municipios = crimes_por_municipio.sort_values(by="registros", ascending=False).head(10)
    print("\n--- Top 10 Municípios com Mais Crimes ---")
    print(top_municipios)
    
    plt.figure(figsize=(10,6))
    plt.pie(top_municipios['registros'], labels=top_municipios['municipio'],
            autopct='%1.1f%%', colors=sns.color_palette("OrRd", len(top_municipios)))
    plt.title("Top 10 Municípios com Maior Incidência de Crimes")
    plt.show()


def plot_crimes_por_mes(df):
    """
    Exibe a distribuição de crimes por mês utilizando um gráfico de linhas.
    
    Passos:
      - Agrupa os dados por mês e soma os registros.
      - Reindexa para garantir que todos os meses de 1 a 12 sejam exibidos (com valor 0 se necessário).
      - Plota um gráfico de linhas com marcadores e anota os valores acima de cada ponto.
    """
    # Agrupa os dados por mês e soma o número de registros
    crimes_por_mes = df.groupby("mes")["registros"].sum().reset_index()
    # Garante que todos os meses de 1 a 12 estejam presentes
    crimes_por_mes = crimes_por_mes.set_index("mes").reindex(range(1, 13), fill_value=0).reset_index()
    print("\n--- Crimes por Mês ---")
    print(crimes_por_mes)
    
    # Cria o gráfico de linhas
    plt.figure(figsize=(10,6))
    plt.plot(crimes_por_mes['mes'], crimes_por_mes['registros'], 
             marker='o', color='red', linestyle='-', linewidth=2, label="Registros")
    plt.title("Distribuição de Crimes por Mês")
    plt.xlabel("Mês")
    plt.ylabel("Número de Crimes")
    plt.xticks(range(1, 13))
    
    # Anota os valores acima de cada marcador
    for i, row in crimes_por_mes.iterrows():
        plt.text(row['mes'], row['registros'] + 0.5, str(row['registros']),
                 ha='center', va='bottom', fontsize=10)
    
    plt.legend()
    plt.show()



def plot_crimes_por_trimestre(df):
    """
    Exibe a distribuição de crimes por trimestre.
    
    - Cria a coluna 'trimestre' a partir do mês.
    - Agrupa os dados por trimestre e soma os registros.
    - Reindexa para garantir que os trimestres 1 a 4 apareçam.
    - Plota um gráfico de barras.
    """
    df['trimestre'] = ((df['mes'] - 1) // 3) + 1
    crimes_por_trimestre = df.groupby("trimestre")["registros"].sum().reset_index()
    crimes_por_trimestre = crimes_por_trimestre.set_index("trimestre").reindex(range(1,5), fill_value=0).reset_index()
    print("\n--- Crimes por Trimestre ---")
    print(crimes_por_trimestre)
    
    plt.figure(figsize=(10,6))
    ax = sns.barplot(x='trimestre', y='registros', data=crimes_por_trimestre, palette='Purples', edgecolor='black')
    plt.title("Distribuição de Crimes por Trimestre")
    plt.xlabel("Trimestre")
    plt.ylabel("Número de Crimes")
    for p in ax.patches:
        ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width()/2, p.get_height()),
                    ha='center', va='bottom', fontsize=10, color='black')
    plt.show()

def plot_crimes_por_tipo(df):
    """
    Exibe a quantidade de crimes por tipo (usando o nome padronizado).
    
    - Agrupa os dados pelo tipo de crime e soma os registros.
    - Plota um gráfico de barras horizontal.
    """
    crimes_por_tipo = df.groupby("natureza_padronizada")["registros"].sum().reset_index()
    print("\n--- Crimes por Tipo ---")
    print(crimes_por_tipo.sort_values(by='registros', ascending=False))
    
    plt.figure(figsize=(10,6))
    ax = sns.barplot(y='natureza_padronizada', x='registros', 
                     data=crimes_por_tipo.sort_values(by='registros', ascending=False),
                     palette='Blues', edgecolor='black')
    plt.title("Crimes Mais Comuns (por Tipo)")
    plt.xlabel("Quantidade")
    plt.ylabel("Tipo de Crime")
    for p in ax.patches:
        ax.annotate(f'{p.get_width()}', (p.get_width(), p.get_y() + p.get_height()/2),
                    ha='left', va='center', fontsize=10, color='black')
    plt.show()

######################################################################
# 4. Aplicação Interativa Principal (Menu)                           #
######################################################################
def main():
    """
    Função principal que:
      - Define o caminho para o arquivo CSV (pode ser atualizado para novos dados, ex.: "crimes_violentos_2023.csv").
      - Carrega e trata os dados.
      - Cria e insere novos registros no banco de dados apenas se necessário (para agilizar a execução na apresentação).
      - Exibe um menu interativo para selecionar diferentes análises.
    """
    # Defina o caminho para o CSV conforme os dados que deseja inserir (ex.: "crimes_violentos_2023.csv")
    csv_path = "crimes_violentos_2023.csv"
    
    # Carrega e trata os dados do CSV
    df = load_and_clean_data(csv_path)
    
    # Cria e/ou insere novos registros no banco de dados MySQL (somente se eles ainda não existirem)
    create_normalized_database(df)
    
    # Loop do menu interativo para as análises
    while True:
        print("\n=== Menu de Análises ===")
        print("1. Top 10 municípios com maior incidência de crimes")
        print("2. Distribuição de crimes por mês")
        print("3. Distribuição de crimes por trimestre")
        print("4. Crimes por tipo")
        print("5. Sair")
        opcao = input("Digite o número da opção desejada: ").strip()
        
        if opcao == "1":
            plot_top_municipios(df)
        elif opcao == "2":
            plot_crimes_por_mes(df)
        elif opcao == "3":
            plot_crimes_por_trimestre(df)
        elif opcao == "4":
            plot_crimes_por_tipo(df)
        elif opcao == "5":
            print("Encerrando a aplicação.")
            break
        else:
            print("Opção inválida. Por favor, tente novamente.")

# Executa a função principal
if __name__ == "__main__":
    main()
