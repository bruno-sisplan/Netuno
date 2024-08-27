import os as o
import sys as s
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import time as t
import threading
import queue
import webbrowser as browser
import requests as r
import locale
import re
from pywinauto import Application
#import speech_recognition as sr 
#import urllib.request, json, requests
#import translateimport urllib.request, json, requests
#import translate
#from gtts import gTTS
#from playsound import playsound
#from bs4 import BeautifulSoup
#from translate import Translator

app = Flask(__name__)

CORS(app)

response_queue = queue.Queue()
response_event = threading.Event() 
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def clima(cidade):
    token = "eb2ebd443b002b99bf5fd10c42fd625e"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + token + "&q=" + cidade
    response = r.get(complete_url)
    retorno = response.json()

    if retorno["cod"] == 200:
        valor = retorno["main"]
        current_temperature = valor["temp"]
        current_humidiy = valor["humidity"]
        tempo = retorno["weather"]
        weather_description = tempo[0]["description"]
        clima = (f"Em {cidade} a temperatura é de {str(int(current_temperature - 273.15))} graus Celsius e umidade de {str(current_humidiy)}%.")
        return f'{clima}'
    else:
        return 'Erro na requisição ou cidade não encontrada.'
        
def executa_comandos_em_threads(mensagem):
    thread = threading.Thread(target=executa_comandos, args=(mensagem,))
    thread.start()

def cotacao(moeda):
	requisicao = r.get(f'https://economia.awesomeapi.com.br/all/{moeda}-BRL')
	cotacao = requisicao.json()
	nome = cotacao[moeda]['name']
	data = cotacao[moeda]['create_date']
	valor = cotacao[moeda]['bid']
	return f'Cotação do {nome} em {data} é {locale.currency(float(valor), grouping=True)}'

def executa_comandos(mensagem):
    mensagem = re.findall(r'\{.*?\}|\S+', mensagem.lower().replace('?', '').replace('!', ''))
    response_mensagem = ''
    cumprimentos = ['noite', 'dia', 'tarde', 'oi', 'olá', 'ola', 'salve', 'eai', 'netuno']
    palavras_cotacoes = ['cotação', 'cotacao', 'cota']
    palavras_desligar_computador = ['desligar', 'tchau', 'embora', 'amanhã']
    palavras_pesquisa_navegador = ['pesquisar', 'pesquisa', 'joga']

    if any(cumprimento in cumprimentos for cumprimento in mensagem):
        indice_c = -1
        response_mensagem = ''
        for c in cumprimentos:
            if c in mensagem:
                if c == 'salve':
                    response_mensagem = 'E ai, meu faixa. O que tu manda hoje?'
                elif c == 'oi':
                    response_mensagem = 'Oi. O que você precisa, Bruno?'
                elif c == 'olá' or c == 'ola':
                    response_mensagem = 'Olá, Bruno. Do que precisa?'
                else:
                    indice_c = mensagem.index(c)
                    agora = datetime.now().time()
                    inicio_dia = datetime.strptime('05:00:00', '%H:%M:%S').time()
                    inicio_tarde = datetime.strptime('12:00:00', '%H:%M:%S').time()
                    inicio_noite = datetime.strptime('18:00:00', '%H:%M:%S').time()
                    saudacao = ''
                    if inicio_dia <= agora < inicio_tarde:
                        saudacao = "Bom dia"
                    elif inicio_tarde <= agora < inicio_noite:
                        saudacao = "Boa tarde"
                    else:
                        saudacao = "Boa noite"
                    if c == 'dia':
                        if (mensagem[indice_c - 1]) == 'bom':
                            response_mensagem = f'{saudacao}, Bruno! Como posso te ajudar hoje?'
                    elif c == 'tarde' or c == 'noite':
                        if (mensagem[indice_c - 1]) == 'boa':
                            response_mensagem = f'{saudacao}, Bruno! Como posso te ajudar hoje?'
                response_queue.put(response_mensagem)
                response_event.set()
                    
    # #fechar assistente
    # if 'fechar assistente' in mensagem:
    #     response_mensagem = 'Até logo!'
    #     response_queue.put(response_mensagem)
    #     response_event.set()
    #     t.sleep(1)
    #     s._exit(0)

    #desligar computador
    if any(palavra_desliga_pc in palavras_desligar_computador for palavra_desliga_pc in mensagem):
        indice_c = -1
        response_mensagem = ''
        for c in palavras_desligar_computador:
            if c in mensagem:
                if c == 'desligar':
                    indice_c = mensagem.index(c)
                    if mensagem[indice_c + 1] == 'computador':
                        if 'uma' in mensagem and 'hora' in mensagem:
                            response_mensagem = 'Computador agendado pra desligar daqui a uma hora.'
                            response_queue.put(response_mensagem)
                            response_event.set()
                            o.system("shutdown /s /f /t 3600")
                        elif 'meia' in mensagem and 'hora' in mensagem:
                            response_mensagem = 'Computador agendado pra desligar daqui a meia hora.'
                            response_queue.put(response_mensagem)
                            response_event.set()
                            o.system("shutdown /s /f /t 1800")  
                        elif '15' in mensagem and 'minutos' in mensagem:
                            response_mensagem = 'Computador agendado pra desligar daqui a 15 minutos.'
                            response_queue.put(response_mensagem)
                            response_event.set()
                            o.system("shutdown /s /f /t 900") 
                        elif 'agora' in mensagem:
                            response_mensagem = 'Computador irá desligar em 5 segundos.'
                            response_queue.put(response_mensagem)
                            response_event.set()
                            t.sleep(5)
                            o.system("shutdown /s /f /t 0")
                        elif 'cancelar' in mensagem:
                            response_mensagem = 'Retirado agendamento para desligar computador'
                            response_queue.put(response_mensagem)
                            response_event.set()
                            o.system("shutdown /a")

    if any(palavra_pesquisa in palavras_pesquisa_navegador for palavra_pesquisa in mensagem):
        indice_c = -1
        response_mensagem = ''
        for c in palavras_pesquisa_navegador:
            if c in mensagem:
                if 'google' in mensagem: 
                    indice_chave_pesquisa = next((i for i, s in enumerate(mensagem) if re.match(r'\{.*\}', s)), None) 
                    response_mensagem = 'Pesquisando no google...'
                    response_queue.put(response_mensagem)
                    response_event.set()
                    chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
                    browser.get(chrome_path).open(f"https://google.com/search?q={mensagem[indice_chave_pesquisa].replace('{', '').replace('}', '')}")
                elif 'youtube' in mensagem:
                    indice_chave_pesquisa = next((i for i, s in enumerate(mensagem) if re.match(r'\{.*\}', s)), None) 
                    response_mensagem = 'Pesquisando no youtube...'
                    response_queue.put(response_mensagem)
                    response_event.set()
                    chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
                    browser.get(chrome_path).open(f"https://youtube.com/results?search_query={mensagem[indice_chave_pesquisa].replace('{', '').replace('}', '')}")
    
    if 'gerar' and 'versao' in mensagem:
        versao_path = r'C:/Users/bruno.sena/Documents/gerar_versao/gerar_versao.exe'
        app = Application().start(versao_path)
        t.sleep(3)
        janela = app.window(title="gerar_versao")
        janela.ElevatedButton.click()

    #pesquisar google    
    # elif 'pesquisar' in mensagem and 'google' in mensagem:  
    #     response_mensagem = 'Pesquisando no google...'
    #     response_queue.put(response_mensagem)
    #     response_event.set()
    #     mensagem = mensagem.replace('pesquisar', '')
    #     mensagem = mensagem.replace('google', '')
    #     chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
    #     browser.get(chrome_path).open(f"https://google.com/search?q={mensagem}")
        
        
    # #pesquisar ytb 
    # elif 'pesquisar' in mensagem and 'youtube' in mensagem:
    #     response_mensagem = 'Pesquisando no youtube...'
    #     response_queue.put(response_mensagem)
    #     response_event.set()
    #     mensagem = mensagem.replace('pesquisar', '')
    #     mensagem = mensagem.replace('youtube', '')
    #     chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
    #     browser.get(chrome_path).open(f'https://youtube.com/results?search_query={mensagem}')
        
    #clima e temperatura    
    elif 'clima' in mensagem:
        mensagem = mensagem.replace('clima', '')
        mensagem = mensagem.replace('em', '')
        response_mensagem = clima(mensagem[2:])
        response_queue.put(response_mensagem)
        response_event.set()

    elif 'temperatura' in mensagem:
        mensagem = mensagem.replace('temperatura', '')
        mensagem = mensagem.replace('em', '')
        response_mensagem = clima(mensagem[2:])
        response_queue.put(response_mensagem)
        response_event.set()
        
    #cotação de moedas   
    # elif 'dólar' in mensagem:
    #     response_mensagem = cotacao('USD')
    #     response_queue.put(response_mensagem)
    #     response_event.set()

    if any(palavra_cotacao in palavras_cotacoes for palavra_cotacao in mensagem):
        if 'dolar' in mensagem:
            response_mensagem = cotacao('USD')
            response_queue.put(response_mensagem)
            response_event.set()
        elif 'dólar' in mensagem:
            response_mensagem = cotacao('USD')
            response_queue.put(response_mensagem)
            response_event.set()
        elif 'euro' in mensagem:
            response_mensagem = cotacao('EUR')
            response_queue.put(response_mensagem)
            response_event.set()
        elif 'eur' in mensagem:
            response_mensagem = cotacao('EUR')
            response_queue.put(response_mensagem)
            response_event.set()
        elif 'bitcoin' in mensagem:
            response_mensagem = cotacao('BTC')
            response_queue.put(response_mensagem)
            response_event.set()
        elif 'btc' in mensagem:
            response_mensagem = cotacao('BTC')
            response_queue.put(response_mensagem)
            response_event.set()
        
    #hora atual
    elif 'horas' in mensagem:
        hora = datetime.now().strftime('%H:%M')
        frase = f"Agora são {hora}"
        response_queue.put(frase)
        response_event.set()       
    
    
@app.route('/usermessage', methods=['POST'])
def server_run():
    data = request.json
    solicitacao = data.get('question')
    response_event.clear()
    response_queue.queue.clear()
    executa_comandos_em_threads(solicitacao)    
    response_event.wait()
    mensagem_resposta = response_queue.get()
    if mensagem_resposta == '':
        mensagem_resposta = 'Não entendi. Pode repetir?'
    return jsonify({"message": mensagem_resposta}), 200
    
if __name__ == '__main__':
    app.run(debug=True)
