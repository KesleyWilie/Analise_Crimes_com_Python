# Análise de Crimes Violentos em Minas Gerais

Este projeto utiliza uma base de dados disponível na plataforma de dados abertos do governo federal para analisar os crimes violentos ocorridos em Minas Gerais. A aplicação desenvolvida permite visualizar padrões nos dados e auxiliar na tomada de decisões relacionadas à segurança pública.

## Funcionalidades

- **Identificação do Esquema Original:**  
  - Leitura do arquivo CSV e exibição das informações iniciais da base.
  
- **Tratamento de Dados Não-Conformes:**  
  - Padronização dos nomes dos municípios e tipos de crime para MAIÚSCULAS.
  - Conversão das colunas numéricas para os tipos corretos.
  - Remoção de linhas com valores essenciais nulos.
  
- **Banco de Dados Relacional Normalizado:**  
  O projeto insere os dados em um banco MySQL seguindo um esquema normalizado:
  - **Tabela `risp`:**  
    Armazena as Regiões Integradas de Segurança Pública.  
    - **1FN:** Os atributos `id` e `descricao` são atômicos.  
    - **2FN:** `descricao` depende integralmente da chave primária `id`.  
    - **3FN:** Não há dependências transitivas.
  
  - **Tabela `municipio`:**  
    Armazena os municípios e referencia a RISP.  
    - **1FN:** Atributos `cod_municipio`, `nome` e `risp_id` são atômicos.  
    - **2FN:** `nome` e `risp_id` dependem integralmente da chave primária `cod_municipio`.  
    - **3FN:** Não há dependências transitivas.
  
  - **Tabela `tipo_crime`:**  
    Armazena os tipos de crime padronizados (em MAIÚSCULAS).  
    - **1FN:** Os atributos `id` e `nome` são atômicos.  
    - **2FN:** `nome` depende integralmente da chave primária `id`.  
    - **3FN:** Não há dependências transitivas.
  
  - **Tabela `crime`:**  
    Armazena cada ocorrência de crime, referenciando as tabelas `municipio` e `tipo_crime`.  
    - **1FN:** Atributos como `mes`, `ano`, `registros`, `rmbh`, `municipio_id` e `tipo_crime_id` são atômicos.  
    - **2FN:** Todos os atributos dependem integralmente da chave primária `id`.  
    - **3FN:** Não há dependências transitivas, pois as referências são feitas por chaves estrangeiras.
  
- **Inserção Condicional:**  
  - O código insere os dados no banco somente se eles ainda não existirem, garantindo rapidez na execução e evitando duplicidade, o que é ideal para visualições rápidas e apresentações.
  
- **Visualização e Análise Interativa:**  
  - O usuário pode selecionar diversas opções de análise via menu interativo, como:  
    - Top 10 municípios com maior incidência de crimes.
    - Distribuição de crimes por mês (visualizado em gráfico de linhas).
    - Distribuição de crimes por trimestre.
    - Quantidade de crimes por tipo.

## Como Executar

1. **Pré-requisitos:**
   - Python 3.
   - Bibliotecas: `pandas`, `matplotlib`, `seaborn`, `SQLAlchemy`, `pymysql`.
   - MySQL rodando (por exemplo, via XAMPP) e um banco de dados chamado `crimes_db` criado.
   
2. **Configuração:**
   - Atualize a string de conexão no código, se necessário.
   - Ajuste o caminho do arquivo CSV na variável `csv_path` (ex.: "crimes_violentos_2023.csv").

3. **Execução:**
   - Execute o script Python. Se os dados já estiverem inseridos, a inserção será pulada, garantindo uma execução rápida.
   - Utilize o menu interativo para visualizar as diferentes análises.

## Conclusão

Este projeto demonstra a extração, tratamento, normalização e análise interativa de uma base de dados pública. A modelagem relacional segue rigorosamente os princípios da 1FN, 2FN e 3FN, e a aplicação interativa transforma dados brutos em informações úteis para a análise da segurança pública em Minas Gerais.

---

