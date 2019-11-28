#!/usr/bin/env python
# coding: utf-8

'''
	abre o whatsapp web e navega entre todas as conversas pegando todo o historico de cada uma delas e tambem as informacoes de contato com o qual a conversa aconteceu
'''

# In[286]:


import bs4
import time
import os
from datetime import datetime, date
import pprint
import pandas as pd
# pd.set_option('display.max_rows', 1000)


# In[327]:


from engines import saveData


# In[265]:


from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

#instance headless
options = webdriver.ChromeOptions()
#options.add_argument('headless')
#options.add_argument('--window-size-1920x1080')

# open with saved informations in cache
options.add_argument("profile")
options.add_argument("user-data-dir=./whatsapp_nabike")

driver = webdriver.Chrome(options=options, executable_path="./webdriver/chromedriver")
driver.get('https://web.whatsapp.com/')


# In[3]:


# FUNCOES QUE PEGAM AS INFORMACOES DO CONTATO
def getImage():
    # PEGA IMAGEM
    try:
        contact_info['image'] = div_right.find_element_by_xpath('//div[@class="_2vJOg"]').find_element_by_css_selector('img').get_property('src')  
        return True
    except Exception as error:
        pass
        #print('getImage() error: {}'.format(error))

def getCaption():
    # PEGA LEGENDA
    try:
        contact_info['caption'] = div_right.find_element_by_xpath('//span[@class="_19RFN"]').text
        return True
    except Exception as error:
        pass
        #print('getCaption() error: {}'.format(error))

def getPhone():
    # PEGA O TELEFONE E SE EH CONTA COMERCIAL
    elements = div_right.find_elements_by_xpath('//span[@class="_6xQdq"]')
    for fone in elements:
        #verifica se eh conta comercial
        if fone.text == 'Conta comercial':
            contact_info['business'] = True
        #salva o numero
        if fone.text.startswith('+'):
            contact_info['phone'] = fone.text
            
def get_Name():
    # RETORNA TRUE SE O CONTATO ESTIVER SALVO E FALSE CASO CONTRARIO, SE NAO ESTIVER VERIFICA SE O USUARIO DEIXOU O NOME PUBLICO
    try:
        c_name = div_right.find_element_by_xpath('//span[@class="_1drsQ"]').text
        if c_name.startswith('+'):
            #verifica se o nome esta publico entao salva o nome e false porque nao esta salvo
            try:
                #salva o nome de contato
                c_name = div_right.find_element_by_xpath('//span[@class="_1qWhd"]').text
                contact_info['saved'] = False
                contact_info['name'] = c_name
            except Exception as error:
                print('getImageName() [step 1] error: {}'.format(error))
        else:
            #se nao comecar com + eh porque o contato esta salvo
            contact_info['saved'] = True
            
            c_name = driver.find_element_by_class_name('_1drsQ').text
            contact_info['name'] = c_name
            
            #POR ALGUMA RAZAO ELE NAO PEGA O NOME DE PRIMEIRA ALGUMAS VEZES
            if c_name == '':
                for i in range(10):
                    c_name = driver.find_element_by_class_name('_1drsQ').text
                    contact_info['name'] = c_name
                    if c_name != '':
                        break
            ################################################################
    except Exception as error:
        pass
        #print('getName() [step 2] error: {}'.format(error))


# In[4]:


# FUNCOES DE NAVEGACAO PELO WHATSAPP COM CLIQUES E TECLAS DO TECLADO
def down_chat(force=False):
    #force = True ira clicar na caixa de pesquisa e reiniciar o processo de clicar nos botoes
    if 'press_down' not in globals() or force == True:
        # CLICA NA CAIXA DE PESQUISA DE CONVERSAS
        driver.find_element_by_class_name('_2zCfw').click()
        
        # PRESSIONA A TECLA DOWN PARA NAVEGAR ENTRE AS CONVERSAS
        global press_down
        press_down = ActionChains(driver)
        press_down.send_keys(Keys.DOWN)
        press_down.perform()
    else:
        press_down.perform()

def click_on_contact():
    try:
        c_info = div_right.find_element_by_xpath('//header[@class="_3fs0K"]')
        time.sleep(0.5)
        c_info.click()
        time.sleep(0.5)
        return True
    except:
        return False
        
def esc_conversation():
    press_esc = ActionChains(driver)
    press_esc.send_keys(Keys.ESCAPE)
    press_esc.perform()


# In[5]:


# PEGA AS INFORMACOES DO CONTATO COM O QUAL TEVE A CONVERSA
def getContactData():
    # INFORMACOES DA CONVERSA E DO USUARIO
    global div_right
    div_right = driver.find_element_by_class_name('_3HZor')

    global contact_info
    contact_info = {'business': False, 'image': None, 'caption': None, 'phone': None, 'name': None, 'saved': False}
    
    # clica no contato
    if click_on_contact():
        time.sleep(1)
    else:
        return 'Nao conseguiu clicar no contato'
    
    # CHAMA TODAS AS FUNCOES E MONTA UM DICIONARIO COM TODAS AS INFORMACOES
    getImage()
    time.sleep(0.3)
    getCaption()
    time.sleep(0.3)
    get_Name()
    time.sleep(0.3)
    getPhone()
    time.sleep(0.3)
    
    #fecha informacoes do contato
    esc_conversation()

    return contact_info


# In[9]:


# FUNCOES QUE LIDAM COM O SCROLL UP DAS CONVERSAS PARA CAPUTRAR TODO O HISTORICO
def block_time(mensagem):
    days_week = ['TODAY', 'YESTERDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY', 
                'HOJE', 'ONTEM', 'SEGUNDA-FEIRA', 'TERÇA-FEIRA', 'QUARTA-FEIRA', 'QUINTA-FEIRA', 'SEXTA-FEIRA', 'SÁBADO', 'DOMINGO']
    try:
        content = mensagem.text
        if len(content) == 10 and content[2] == '/' and content[5] == '/':
            return content
        elif content in days_week:
            return content
        else:
            return False
    except Exception as error:
        return False

# VERIFICA SE EH O FIM DA CONVERSA
def verify_end():
    engine_messages = ['As mensagens e chamadas dessa conversa estão protegidas com criptografia de ponta a ponta.']
    try:
        for element in driver.find_elements_by_xpath('//div[@role="button"]'):
            if element.text in engine_messages:    
                return True
        return False
    except:
        return False

def scroll_history():
    #se nao for o fim da conversa, ira dar scroll para cima
    run = True
    while run: 
        if not verify_end():
            try:
                div_chat = driver.find_element_by_class_name('_1ays2')
                driver.execute_script("arguments[0].scrollIntoView(true);", div_chat)
                time.sleep(0.3)
            except:
                return False
        else:
            run = False
    return True


# In[262]:


# FUNCOES PARA TRATAR CADA MENSAGEM, TIME, STATUS, SE FOI ENVIADA OU RECEBIDA E CONTEUDO
def get_time(mensagem):
    #verifica o horario da mensagem
    #pega o tempo de cada mensagem
    try:
        time = mensagem.find_element_by_css_selector('span._3fnHB').text
        return time
    except:
        return 'ENGINE'
        pass

def get_source_status(mensagem, time):
    #verifica se eh mensagem recebida ou enviada
    #se for enviada verifica o status
    try:
        status = mensagem.find_element_by_css_selector('path').get_attribute('fill') 
        if status == 'FFF':
            return 'sent'
        elif status == '92A58C':
            return 'delivered'
        else:
            return 'viewed'
    except:
        #se nao tiver icone de status e nao for o balao de data do whatsapp, eh mensagem recebida
        if time != 'ENGINE':
            return 'received'
        else:
            #criar metodo que ira organizar as mensagens em um bloco de tempo
            return 'ENGINE'

def verify_content(mensagem):
    #verifica qual o conteudo da mensagem
    content = {'content': '', 'type': ''}
    
    #verifica se eh um audio
    try:
        audio = mensagem.find_element_by_css_selector('audio').get_attribute('src')
        content['content'] = 'audio: ' + str(audio)
        content['type'] = 'audio'
    except:
        #verifica se eh umagem
        try:
            link = mensagem.find_element_by_css_selector('img').get_attribute('src')
            content['content'] = link
            content['type'] = 'image'
        except:
            try:
                video = mensagem.find_element_by_class_name('_3_IKd')
                content['content'] = 'duracao do video: ' + str(video.text)
                content['type'] = 'video'
            except:
                #se nao for imagem nem video nem audio eh texto, se for documento pegara o nome do arquivo
                try:
                    content_msg = mensagem.text.split('\n')
                    if len(content_msg) > 2 and content[0].startswith('+55') and content[2].startswith('+55') :
                        content['content'] = '|'.join(content_msg)
                        content['type'] = 'replie'
                    else:
                        #verifica se eh mensagem deletada
                        try:
                            mensagem.find_element_by_class_name('-bh0C')
                            content['content'] = 'This message was deleted'
                            content['type'] = 'deleted'
                        except:
                            #se nao for nenhuma das possibilidaes anteriores, eh texto
                            content['content'] = mensagem.text.split('\n')[0]
                            content['type'] = 'text'
                except Exception as error:
                    content['content'] = 'desconhecido'
                    content['type'] = 'unknown' 
    
    return content


# In[275]:


# PEGA O CONTEUDO DAS MENSAGENS E DO CONTATO
def getContent():
    div_chat = driver.find_element_by_class_name('_1ays2')
    #driver.execute_script("arguments[0].scrollIntoView(true);", div_chat)
    mensagens = div_chat.find_elements_by_class_name('FTBzM')

    
    history = {}
    
    #pega informacoes do contato
    contanct_data = getContactData() 
    
    timeline = []
    date = 'no date'
    
    for msg in mensagens:
        message = {'status': None, 'time': None, 'content': None, 'type': None}
        
        #pega o tempo de cada mensagem
        message['time'] = get_time(msg)
        
        #verifica se eh mensagem enviada ou recebida, se a mensagem nao tiver tempo eh o balao com a data
        message['status'] = get_source_status(msg, message['time'])
        
        content = verify_content(msg)
        
        message['type'] = content['type']
        message['content'] = content['content']
        
        is_time = block_time(msg)
        if is_time != False:
            #se for tempo, cria um dicionario que armazena o a lista de dicionarios com dados de cada mensagem
            date = is_time
            timeline.append({date: []})
        else:
            #adiciona o dicionario de dados na lista que ja existe
            try:
                timeline[-1][date].append(message)
            except IndexError:
                timeline.append({date: []})
                timeline[-1][date].append(message)
        
    data = {'contact': contanct_data, 'history': timeline}
    return data


# In[424]:





# In[412]:


# SALVA AS INFORMACOES COLETADAS NO BANCO DE DADOS
def save_to_db(data):
    #RECEBE O DICIONARIO GERADO COM AS DUAS CHAVES PRINCIPAIS E SALVA NO BANCO DA DADOS
    
    #salva as informacoes de contato no banco
    database.save_contact_info(data['contact'])

    #salva o historico de conversas no banco
    for date in data['history']:
        #o historico esta salvo como uma lista de dicionarios onde cada dicionario possui uma data como chave e uma lista de dicionarios com dados da mensagem
        date_key = [key for key in date.keys()][0] #extrai a chave data
        print('saving history from day {}...'.format(date_key))
        database.save_history(date[date_key], date_key, carlos_296['contact']['phone'], carlos_296['contact']['name'])
    
    print('Saved!')


# In[439]:


# SALVA LOCALMENTE AS INFORMACOES COLETADAS
def contact_info_txt(contact_info):
    if 'history' not in os.listdir():
        os.mkdir('history')
    
    contact_name = 'history/' + str(''.join(filter(str.isdigit, contact_info['phone']))) + '_contact.txt'
    
    with open(contact_name, 'a') as filee:
        for key in contact_info.keys():
            line = str(key) + ': ' + str(data_contact['contact'][key]) + '\n'
            filee.writelines(line)
    
    
    return 'contact info saved as: ' + str(contact_name)

def history_csv(history, contact_name):
    # CRIA UM DATAFRAME COM O HISTORICO DE CONVERSAS
    df = pd.DataFrame(columns=['date', 'status', 'content', 'time', 'type'])
    
    for date in history:
        #o historico esta salvo como uma lista de dicionarios onde cada dicionario possui uma data como chave e uma lista de dicionarios com dados da mensagem
        date_key = [key for key in date.keys()][0] #extrai a chave data
        for msg in date[date_key]:
            df = df.append({'date': date_key, 'status': msg['status'], 'content': msg['content'], 'time': msg['time'], 'type': msg['type']}, ignore_index=True)
            
    # EXPORTA EM CSV
    if 'history' not in os.listdir():
        os.mkdir('history')
    
    history_name = 'history/' + str(''.join(filter(str.isdigit, contact_name))) + '_history.csv'
    df.to_csv(history_name, encoding='utf-8')
    
    return 'history info saved as: ' + str(history_name)


# In[435]:





# In[ ]:


database = saveData.Database()


# In[276]:


for i in range(3):
    down_chat(force=True)
    time.sleep(1)
    if scroll_history():
        data_contact = getContent()
        
        save_to_db(data_contact)
        contact_info_txt(data_contact['contact'])
        history_csv(data_contact['history'], data_contact['contact']['phone'])


# In[ ]:





# In[ ]:


#criar funcao que limpa as datas caso seja um dia da semana e exclui ENGINES do historico

