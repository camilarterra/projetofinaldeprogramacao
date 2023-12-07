# Como usar o script

1. Incluir os exemplos de treino de cada categoria "what", "why", "when", "where", "who", "how", "how_much" no arquivo `examples.json` ou alterar para a classificacao desejada.

o arquivo gzip_classification
2. Configurar os exemplos de teste modificando a configuracao do MongoDB:
```python
# Trocar 'conductor' pela database que interessar
databaseGet = connetionGet['conductor']

# Trocar 'comments' pela collection que interessar
collectionGet = databaseGet['comments']
```
3. Ajustar o parametro $K$ para o KNN.
4. Para executar o script, rodar a linha `python3 gzip_classification.py` no terminal.

O script vai devolver no terminal cada exemplo de texto e a classificacao e tambem vai ficar salva no MongoDB.

o arquivo resultsAnalysis
5. Tambem fazer as modificacoes necessarias para a conexao com o MongoDB.
6. Para executar o script, rodar a linha `python3 resultsAnalysis.py` no terminal.

O sistema vai salvar no MongoDb por issue: as metricas do GitHub, as classificacoes e o quantitativo das classificacoes


