import os as o
import sys as s
#import speech_recognition as sr 
import webbrowser as browser
#import urllib.request, json, requests
#import translateimport urllib.request, json, requests
#import translate
#from gtts import gTTS
#from playsound import playsound
from datetime import datetime
import time as t
#from bs4 import BeautifulSoup
import requests as r
#from translate import Translator


def monitora_prompt():
    print('Sou o Netuno, como posso te ajudar hoje?')
    solicitacao = input('')
    executa_comandos(solicitacao)
    
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
        clima = (f"Em {cidade} a temperatura é de {str(int(current_temperature - 273.15))} graus Celsius e umidade de {str(current_humidiy)}%")
        print(f"{clima}")
    else:
        print("Erro na requisição ou cidade não encontrada.")

def cotacao(moeda):
	requisicao = r.get(f'https://economia.awesomeapi.com.br/all/{moeda}-BRL')
	cotacao = requisicao.json()
	nome = cotacao[moeda]['name']
	data = cotacao[moeda]['create_date']
	valor = cotacao[moeda]['bid']
	print(f"Cotação do {nome} em {data} é {valor}")


def executa_comandos(mensagem):
    mensagem = mensagem.lower()
    #fechar assistente
    if 'fechar assistente' in mensagem:
        print('Até logo!')
        t.sleep(1)
        s.exit()

    #desligar computador
    elif 'desligar computador' in mensagem and 'uma hora' in mensagem:
        o.system("shutdown /s /f /t 3600")
    elif 'desligar computador' in mensagem and 'meia hora' in mensagem:
        o.system("shutdown /s /f /t 1800")
    elif 'desligar computador' in mensagem and 'agora' in mensagem:
        o.system("shutdown /s /f /t 0")
    elif 'cancelar desligamento' in mensagem:
        o.system("shutdown -a")
        
        
    #pesquisar google    
    elif 'pesquisar' in mensagem and 'google' in mensagem:  
        mensagem = mensagem.replace('pesquisar', '')
        mensagem = mensagem.replace('google', '')
        chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
        browser.get(chrome_path).open(f"https://google.com/search?q={mensagem}")
        
        
    #pesquisar ytb 
    elif 'pesquisar' in mensagem and 'youtube' in mensagem:
        mensagem = mensagem.replace('pesquisar', '')
        mensagem = mensagem.replace('youtube', '')
        chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
        browser.get(chrome_path).open(f'https://youtube.com/results?search_query={mensagem}')
        
        
    #clima e temperatura    
    elif 'clima' in mensagem:
        mensagem = mensagem.replace('clima', '')
        mensagem = mensagem.replace('em', '')
        clima(mensagem[2:])
    elif 'temperatura' in mensagem:
        mensagem = mensagem.replace('temperatura', '')
        mensagem = mensagem.replace('em', '')
        clima(mensagem[2:])
        
    #cotação de moedas   
    elif 'dólar' in mensagem:
	    cotacao('USD')
     
    elif 'euro' in mensagem:
        cotacao('EUR')
  
    elif 'bitcoin' in mensagem:
        cotacao('BTC')
        
    #hora atual
    elif 'horas' in mensagem:
        hora = datetime.now().strftime('%H:%M')
        frase = f"Agora são {hora}"
        print(frase)

        
    print('')

def main():
    while True:
        monitora_prompt()
    

main()