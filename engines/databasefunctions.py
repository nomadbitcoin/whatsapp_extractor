import pymysql, warnings
from datetime import datetime


class Database:
    def connect(self):
        trying = True
        while trying:
            try:
                self.db = pymysql.connect(host='instagram-bot.ccmmdvzb8vos.us-west-2.rds.amazonaws.com', user='admin', passwd='54203538', db='whatsapp_nabike', autocommit=True)
                trying = False
                return self.db
            except BaseException as error:
                if str(error).startswith('(2003,'):
                    trying = True
                else:
                    print('Error ocurred in: DB - connect --> {}'.format(error))
    
    def startCursor(self):
        self.cursor = self.db.cursor()
        warnings.simplefilter('ignore')
        return self.cursor
    
    def commitChanges(self):
        self.db.commit()

    def closeConnection(self):
        self.cursor.close()
        



    ## -------------------------------------------------------------------- ##

    '''
        Funcoes para salvar os dados do contato e historico
    '''
    ## -------------------------------------------------------------------- ##

    ##########################################################################

    def save_contact_info(self, contact_info):
        #recece um dicionario com dados do contato com o qual a conversa aconteceu
        try:
            self.connect()
            self.startCursor()
            query = 'insert into history(image, business, saved, name, caption, phone, obs, saved_at) values(%s,%s,%s,%s,%s,%s,%s,%s)'
            self.cursor.execute(query, (contact_info['image'], contact_info['business'], contact_info['saved'], contact_info['name'], contact_info['caption'], contact_info['phone'], 'contact_info', datetime.now().strftime('%y/%m/%d %H:%M:%S')))
            self.cursor.close()
        except Exception as error:
            print(type(error))
            print(error)

    def save_history(self, history, date, from_contact, name):
        #recebe uma data e uma lista de dicionarios com os dados das conversas
        try:
            for msg in history:
                self.connect()
                self.startCursor()
                query = 'insert into history(obs, date, content, status, time, type, from_contact, name, saved_at) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                self.cursor.execute(query, ('history', date, msg['content'], msg['status'], msg['time'], msg['type'], from_contact, name, datetime.now().strftime('%y/%m/%d %H:%M:%S')))
            self.cursor.close()
        except Exception as error:
            print(type(error))
            print(error)