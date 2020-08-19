# coding: utf-8

import nltk

basetreinamento = []
baseteste = []

# usar as stop words do nltk
stopWordsNLTK = nltk.corpus.stopwords.words('portuguese')
stopWordsNLTK.append('vou')
stopWordsNLTK.append('tão')

''' Cada linha lida do arquivo contêm o texto do tweet e o nome do usuário. Recebemos a leitura completa do arquivo de 
texto e removemos o caracter de quebra de linha. Por fim, separamos cada linha do arquivo em campos que contenham o 
texto e nome usuário para serem armazenadas em uma estrutura array bidimensional,onde quando acessarmos pelos 
índices [x][0] teremos o texto de uma linha qualquer(x) e quando acessarmos pelos índices [x][1] teremos o nome 
do usuário. Exemplo: print(basePrincipal[7000][0])
Manter uma array bidimensional é necessária para aplicarmos o treinamento da base que gerará o modelo do algoritmo
Naive Bayes e assim conseguirmos aplicar o teste para verificarmos a acurácia.'''


def carregarBases():
    try:
        with open('baseTreinamento.txt', 'r') as arquivo:
            for linha in arquivo.readlines():
                linha = linha.split(',')
                linha = [x.strip() for x in linha]
                texto = linha[0]
                usuario = linha[1]
                registro = [texto, usuario]
                basetreinamento.append(registro)

        with open('baseTeste.txt', 'r') as arquivo:
            for linha in arquivo.readlines():
                linha = linha.split(',')
                linha = [x.strip() for x in linha]
                texto = linha[0]
                usuario = linha[1]
                registro = [texto, usuario]
                baseteste.append(registro)

        arquivo.close()
    except IOError:
        print('Problemas com na leitura do arquivo')


carregarBases()

'''Remover os radicais das palavras e armazenas as palavras que não são spotWords
Aqui não há o controle de repetições'''


def pegarRadical(RegistroTweet):
    pegaRadical = nltk.stem.RSLPStemmer()
    listaTextoRadicais = []
    for (texto, usuario) in RegistroTweet:
        textoSomenteRadical = [str(pegaRadical.stem(palavra)) for palavra in texto.split() if
                               palavra not in stopWordsNLTK]
        listaTextoRadicais.append((textoSomenteRadical, usuario))
    return listaTextoRadicais


frasescomstemmingtreinamento = pegarRadical(basetreinamento)
frasescomstemmingteste = pegarRadical(baseteste)

'''Método faz a listagem de todas as palavras dos textos de cada tweet, sem a classe do usuário associado. Assim
vamos conseguir montar mais facilmente a tabela de caraterísticas do texto'''


def buscapalavras(frases):
    todaspalavras = []
    for (palavras, usuario) in frases:
        todaspalavras.extend(palavras)
    return todaspalavras


palavrastreinamento = buscapalavras(frasescomstemmingtreinamento)
palavrasteste = buscapalavras(frasescomstemmingteste)

'''Cria uma distribuição de frequência para a lista dos radicais das palavras e descobre quais são as mais 
importantes '''


def buscafrequencia(palavras):
    palavras = nltk.FreqDist(palavras)
    return palavras


frequenciatreinamento = buscafrequencia(palavrastreinamento)
frequenciateste = buscafrequencia(palavrasteste)

'''Remove os radicais repetidos e cria o cabeçalho da base de dados'''


def buscapalavrasunicas(frequencia):
    freq = frequencia.keys()
    return freq


palavrasunicastreinamento = buscapalavrasunicas(frequenciatreinamento)
palavrasunicasteste = buscapalavrasunicas(frequenciateste)

'''Método recebe os radicais únicos, que foram extraídos as repetições, e percorre o vetor de características 
e as comparando com cada radical, para saber se os radicais constam ou não dentro do vetor.'''


def extratorpalavras(documento):
    doc = set(documento)
    caracteristicas = {}
    for palavras in palavrasunicastreinamento:
        caracteristicas['%s' % palavras] = (palavras in doc)
    return caracteristicas


basecompletatreinamento = nltk.classify.apply_features(extratorpalavras, frasescomstemmingtreinamento)
basecompletateste = nltk.classify.apply_features(extratorpalavras, frasescomstemmingteste)

# constroi a tabela de probabilidade
classificador = nltk.NaiveBayesClassifier.train(basecompletatreinamento)

print("Acurácia: ", nltk.classify.accuracy(classificador, basecompletateste))

erros = []
for (frase, classe) in basecompletateste:
    resultado = classificador.classify(frase)
    if resultado != classe:
        erros.append((classe, resultado, frase))
# for (classe, resultado, frase) in erros:
#    print(classe, resultado, frase)

from nltk.metrics import ConfusionMatrix

esperado = []
previsto = []
for (frase, classe) in basecompletateste:
    resultado = classificador.classify(frase)
    previsto.append(resultado)
    esperado.append(classe)

matriz = ConfusionMatrix(esperado, previsto)
print(matriz)

# 1. Cenário
# 2. Número de classes
# 3. ZeroRules

teste = 'eu amo meu país'
testestemming = []
stemmer = nltk.stem.RSLPStemmer()
for (palavrastreinamento) in teste.split():
    comstem = [p for p in palavrastreinamento.split()]
    testestemming.append(str(stemmer.stem(comstem[0])))

novo = extratorpalavras(testestemming)
distribuicao = classificador.prob_classify(novo)
