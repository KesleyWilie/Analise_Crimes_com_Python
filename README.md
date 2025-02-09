# Análise de Crimes Violentos em Minas Gerais

Este projeto utiliza uma base de dados disponível na plataforma de dados abertos do governo federal ([dados.gov.br](https://dados.gov.br/dados/conjuntos-dados/crimes-violentos)). A base escolhida contém registros de crimes violentos ocorridos em Minas Gerais. O objetivo da aplicação é possibilitar a análise dos dados, ajudando a identificar padrões e auxiliar na tomada de decisões relativas à segurança pública.

## Funcionalidades

- **Identificação do Esquema Original:**  
  O código lê o arquivo CSV, exibe informações iniciais (schema) e mostra as primeiras linhas da base.

- **Tratamento de Dados Não-Conformes:**  
  São padronizados os nomes dos municípios (convertendo para MAIÚSCULAS), os tipos de crime também são convertidos para MAIÚSCULAS e os dados numéricos (como registros, mês, ano e RISP) são convertidos para os tipos apropriados. Linhas com valores essenciais nulos são removidas.

- **Banco de Dados Relacional Normalizado:**  
  A base é inserida em um banco de dados MySQL (usando XAMPP) através de um esquema normalizado, dividido em quatro tabelas:
  
  - **Tabela `risp`:**  
    Armazena as Regiões Integradas de Segurança Pública.
    - **1FN:** Os atributos `id` e `descricao` são atômicos.
    - **2FN:** `descricao` depende integralmente da chave primária `id`.
    - **3FN:** Não há dependências transitivas.
  
  - **Tabela `municipio`:**  
    Armazena os municípios e referencia a RISP.
    - **1FN:** Atributos `cod_municipio`, `nome` e `risp_id` são atômicos.
    - **2FN:** `nome` e `risp_id` dependem completamente da chave primária `cod_municipio`.
    - **3FN:** Não há dependências transitivas; os dados de endereço estão separados.
  
  - **Tabela `tipo_crime`:**  
    Armazena os tipos de crime padronizados (em MAIÚSCULAS).
    - **1FN:** Os atributos `id` e `nome` são atômicos.
    - **2FN:** `nome` depende integralmente da chave primária `id`.
    - **3FN:** Não há dependências transitivas.
  
  - **Tabela `crime`:**  
    Armazena cada ocorrência de crime, referenciando `municipio` e `tipo_crime`.
    - **1FN:** Atributos como `mes`, `ano`, `registros`, `rmbh`, `municipio_id` e `tipo_crime_id` são atômicos.
    - **2FN:** Todos os atributos não-chave dependem completamente da chave primária `id`.
    - **3FN:** Não há dependências transitivas, pois as referências são feitas por chaves estrangeiras.
  
- **Inserção Condicional (If Not Exists):**  
  O código verifica se os dados já foram inseridos. Se já houver registros (por exemplo, na tabela `crime`), a inserção é pulada para que a execução seja rápida – ideal para a apresentação.

- **Visualização e Análise Interativa:**  
  São fornecidas funções para visualizar:
  - Os 10 municípios com maior incidência de crimes.
  - A distribuição de crimes por mês (garantindo que todos os meses de 1 a 12 sejam exibidos).
  - A distribuição de crimes por trimestre.
  - A quantidade de crimes por tipo.
  
  Essas análises são acessadas por meio de um menu interativo.

## Como Executar

1. **Pré-requisitos:**
   - Python 3 instalado.
   - Bibliotecas necessárias: `pandas`, `matplotlib`, `seaborn`, `SQLAlchemy`, `pymysql`.
   - MySQL rodando (por exemplo, via XAMPP) e um banco de dados chamado `crimes_mg` criado.
   
2. **Configuração:**
   - Atualize a string de conexão no código, se necessário, com seu usuário e senha do MySQL.
   - Ajuste o caminho do arquivo CSV na variável `csv_path` (ex.: `"crimes_violentos_2023.csv"` ou `"crimes_violentos_2024.csv"`).

3. **Execução:**
   - Execute o script Python. Na primeira execução, os dados serão inseridos no banco. Em execuções subsequentes, se os registros já existirem, a inserção será ignorada e o script iniciará rapidamente.
   - Utilize o menu interativo para visualizar as análises.

## Estrutura do Código

- **load_and_clean_data(csv_path):**  
  Faz a leitura, limpeza e padronização dos dados do CSV.

- **create_normalized_database(df):**  
  Cria as tabelas no MySQL e insere os dados somente se eles ainda não existirem, seguindo os conceitos de normalização (1FN, 2FN e 3FN).

- **Funções de Visualização (plot_top_municipios, plot_crimes_por_mes, etc.):**  
  Geram gráficos para as análises dos dados.

- **main():**  
  Função principal que carrega os dados, insere no banco (se necessário) e apresenta um menu interativo para as análises.

## Considerações Finais

Este projeto demonstra a extração, limpeza, normalização e análise de uma base de dados pública de crimes violentos. A modelagem relacional segue rigorosamente os princípios da 1FN, 2FN e 3FN, e a aplicação interativa permite explorar os dados de forma dinâmica.

---
