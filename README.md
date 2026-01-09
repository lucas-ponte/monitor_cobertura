Para que o seu projeto seja profissional e facilite a manutenção (especialmente para um perfil **ISTJ** e **analista de equity research**), o README deve ser pragmático e direto.

Crie um arquivo chamado `README.md` na raiz do seu repositório do GitHub e cole o conteúdo abaixo:

---

# Monitor de Ações - Análise Fundamentalista

Dashboard interativo desenvolvido em Python e Streamlit para monitoramento de ativos financeiros em tempo real. O foco é a praticidade na visualização de variações históricas ajustadas e acompanhamento de teses de investimento (Equity Research).

## 🚀 Funcionalidades

* **Dados Ajustados:** Coleta automática de preços via Yahoo Finance (`yfinance`), garantindo fechamentos ajustados por dividendos e desdobramentos.
* **Multimoeda:** Identificação automática de ativos em BRL (R$) e USD ($).
* **Teses Manuais:** Espaço dedicado no código para inserção de Recomendações e Preços-Alvo.
* **Cálculo de Upside:** Cálculo automático da margem de segurança baseado no Preço-Alvo.
* **Visual Pro:** Coloração condicional (Verde/Vermelho) para variações e upside, seguindo o padrão de terminais financeiros.
* **Padrão Brasileiro:** Números formatados com vírgula para decimais e ponto para milhares.

## 🛠️ Tecnologias

* [Python 3.10+](https://www.python.org/)
* [Streamlit](https://streamlit.io/) - Framework para interface web.
* [Pandas](https://pandas.pydata.org/) - Manipulação e análise de dados.
* [yFinance](https://github.com/ranaroussi/yfinance) - API de dados de mercado.

## 📋 Como Configurar

1. Clone este repositório.
2. Instale as dependências:
```bash
pip install -r requirements.txt

```


3. Execute o dashboard localmente:
```bash
streamlit run app.py

```



## ⚙️ Manutenção de Cobertura

Para atualizar suas recomendações e preços-alvo, altere o dicionário `MINHA_COBERTURA` no arquivo `app.py`:

```python
MINHA_COBERTURA = {
    "TICKER.SA": {"Rec": "Sua Recomendação", "Alvo": 00.00},
}

```

## 🌐 Deploy

O projeto está configurado para deploy automático no **Streamlit Cloud**. Certifique-se de que os arquivos `app.py` e `requirements.txt` estejam na raiz do repositório.

---

