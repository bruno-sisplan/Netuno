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
	return f'Cotação do {nome} em {data} é {valor}'

def executa_comandos(mensagem):
    mensagem = mensagem.lower()
    response_mensagem = ''
    cumprimentos = ['boa noite', 'bom dia', 'boa tarde', 'oi', 'olá', 'ola', 'salve']
    
    if any(cumprimento in mensagem for cumprimento in cumprimentos):
        x = ''
        for c in cumprimentos:
            if c in mensagem:
                x = c
        agora = datetime.now().time()
        inicio_dia = datetime.strptime('05:00:00', '%H:%M:%S').time()
        inicio_tarde = datetime.strptime('12:00:00', '%H:%M:%S').time()
        inicio_noite = datetime.strptime('18:00:00', '%H:%M:%S').time()
        saudacao = ''
        response_mensagem = ''
        if inicio_dia <= agora < inicio_tarde:
            saudacao = "Bom dia"
        elif inicio_tarde <= agora < inicio_noite:
            saudacao = "Boa tarde"
        else:
            saudacao = "Boa noite"
        
        if x == 'salve':
            response_mensagem = 'E ai, meu faixa. O que tu manda hoje?'
        elif x == 'oi':
            response_mensagem = 'Oi. O que você precisa, Bruno?'
        elif x == 'olá' or x == 'ola':
            response_mensagem = 'Olá, Bruno. Do que precisa?'
        else:
            response_mensagem = f'{saudacao}, Bruno! Como posso te ajudar hoje?'
        response_queue.put(response_mensagem)
        response_event.set()
        
    #fechar assistente
    if 'fechar assistente' in mensagem:
        response_mensagem = 'Até logo!'
        response_queue.put(response_mensagem)
        response_event.set()
        t.sleep(1)
        s._exit(0)

    #desligar computador
    elif 'desligar computador' in mensagem and 'uma hora' in mensagem:
        response_mensagem = 'Computador agendado pra desligar daqui a uma hora.'
        response_queue.put(response_mensagem)
        response_event.set()
        o.system("shutdown /s /f /t 3600")
    elif 'desligar computador' in mensagem and 'meia hora' in mensagem:
        response_mensagem = 'Computador agendado pra desligar daqui a meia hora.'
        response_queue.put(response_mensagem)
        response_event.set()
        o.system("shutdown /s /f /t 1800")
    elif 'desligar computador' in mensagem and 'agora' in mensagem:
        response_mensagem = 'Computador irá desligar em 5 segundos.'
        response_queue.put(response_mensagem)
        response_event.set()
        t.sleep(5)
        o.system("shutdown /s /f /t 0")
    elif 'cancelar desligamento' in mensagem:
        o.system("shutdown -a")
        
        
    #pesquisar google    
    elif 'pesquisar' in mensagem and 'google' in mensagem:  
        response_mensagem = 'Pesquisando no google...'
        response_queue.put(response_mensagem)
        response_event.set()
        mensagem = mensagem.replace('pesquisar', '')
        mensagem = mensagem.replace('google', '')
        chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
        browser.get(chrome_path).open(f"https://google.com/search?q={mensagem}")
        
        
    #pesquisar ytb 
    elif 'pesquisar' in mensagem and 'youtube' in mensagem:
        response_mensagem = 'Pesquisando no youtube...'
        response_queue.put(response_mensagem)
        response_event.set()
        mensagem = mensagem.replace('pesquisar', '')
        mensagem = mensagem.replace('youtube', '')
        chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
        browser.get(chrome_path).open(f'https://youtube.com/results?search_query={mensagem}')
        
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
    elif 'dólar' in mensagem:
        response_mensagem = cotacao('USD')
        response_queue.put(response_mensagem)
        response_event.set()
    elif 'euro' in mensagem:
        response_mensagem = cotacao('EUR')
        response_queue.put(response_mensagem)
        response_event.set()
  
    elif 'bitcoin' in mensagem:
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
    executa_comandos_em_threads(solicitacao)    
    response_event.wait()
    mensagem_resposta = response_queue.get()
    return jsonify({"message": mensagem_resposta}), 200
    
if __name__ == '__main__':
    app.run(debug=True)
