import pymysql, warnings
from datetime import datetime, timedelta


class Database:
    def connect(self):
        trying = True
        while trying:
            try:
                self.db = pymysql.connect(host='instagram-bot.ccmmdvzb8vos.us-west-2.rds.amazonaws.com', user='admin', passwd='54203538', db='makaway_poster', autocommit=True)
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
        



    #----------------------------------------#-----------------------------------------#


        '''
            FUNCTIONS TO GETFEED
        '''


    #----------------------------------------#-----------------------------------------#


    '''
        seleciona o perfil adicionado primeiro na lista de perfis, para o getFeed usar
    ''' 

    def getProfile(self):
        self.connect()
        self.startCursor()
        query = 'select username from profiles where ready_data=0 order by created_at desc limit 1'
        self.cursor.execute(query)
        resposta = self.cursor.fetchone()
        self.cursor.close()
        return resposta


    def updateProfile(self, username):
        self.connect()
        self.startCursor()
        query = 'update profiles set ready_data=1 where username=%s'
        self.cursor.execute(query, username)
        self.db.close()
        return True

    #----------------------------------------#-----------------------------------------#

    '''
        Salva informacoes do perfil
    '''

    def saveProfileInfo(self, profile_info):
        #recebe um dicionario com dados sobre o perfil
        try:
            self.connect()
            self.startCursor()
            query =  'insert into users(updated, username, address_street, biography, category, city_id, city_name, contact_phone_number, external_url, follower_count, following_count, full_name, profile_pic_url, zip, is_business, is_private, media_count, pk, public_email, total_igtv_videos, usertags_count) values(%s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            self.cursor.execute(query,(datetime.now().strftime('%y/%m/%d %H:%M:%S'), profile_info['username'], profile_info['address_street'], profile_info['biography'], profile_info['category'], profile_info['city_id'], profile_info['city_name'], profile_info['contact_phone_number'], profile_info['external_url'], profile_info['follower_count'], profile_info['following_count'], profile_info['full_name'], profile_info['profile_pic_url'], profile_info['zip'], profile_info['is_business'], profile_info['is_private'], profile_info['media_count'], profile_info['pk'], profile_info['public_email'], profile_info['total_igtv_videos'], profile_info['usertags_count']))
            #self.db.commit()
            self.cursor.close()
        except BaseException as error:
            print('Error ocurred in: DB - saveProfileInfo --> {}'.format(error))

    #----------------------------------------#-----------------------------------------#

    '''
        Salva o feed
    ''' 
            
    def saveFeed(self, feed):
        #recebe uma lista de dicionarios com dados sobre a midia
        try:
            self.connect()
            self.startCursor()
            for media_info in feed:
                query =  'insert into feed(updated, text, pk, usertags, status, code, comment_count, url, like_count, taken_at, username, location, location_id, location_name) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                self.cursor.execute(query,(datetime.now().strftime('%y/%m/%d %H:%M:%S'), media_info['text'], media_info['pk'], str(media_info['usertags']), media_info['status'], media_info['code'], media_info['comment_count'], media_info['url'], media_info['like_count'], media_info['taken_at'], media_info['username'], media_info['location'], media_info['location_id'], media_info['location_name']))
            self.cursor.close()
            return 'Feed Saved'
        except BaseException as error:
            if str(error).startswith('(1062,'):
                pass
            else:
                print('Error ocurred in: DB - saveFeed --> {}'.format(error))
            
    #----------------------------------------#-----------------------------------------#


        '''
            FUNCTIONS TO ORGANIZE TABLE
        '''


    #----------------------------------------#-----------------------------------------#


    '''
       Pega os posts salvos dos perfis de referencia e cria um ranking dos quais postar
    ''' 
            
    def getFeed(self):
        #ira pegar o feed e alguns dados para organizar a tabela e escolher as melhores imagens para repostar
        try:
            self.connect()
            self.startCursor()
            query = 'select pk, url, like_count from feed where url!=""'  
            self.cursor.execute(query)
            resposta = self.cursor.fetchall()
            self.cursor.close()
            return resposta
        except BaseException as error:
            print('Error ocurred in: DB - saveFeed --> {}'.format(error))
            
    #----------------------------------------#-----------------------------------------#












   #----------------------------------------#-----------------------------------------#

    '''
        Salva informaceos da midia
    ''' 
            
    def saveMediaInfo(self, media_info):
        #recebe um dicionario com dados sobre a midia
        try:
            self.connect()
            self.startCursor()
            query =  'insert into media(updated, text, pk, usertags, status, code, comment_count, url, like_count, taken_at, username, location, location_id, location_name) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            self.cursor.execute(query,(datetime.now().strftime('%y/%m/%d %H:%M:%S'), media_info['text'], media_info['pk'], str(media_info['usertags']), media_info['status'], media_info['code'], media_info['comment_count'], media_info['url'], media_info['like_count'], media_info['taken_at'], media_info['username'], media_info['location'], media_info['location_id'], media_info['location_name']))
            #self.db.commit()
            self.cursor.close()
        except BaseException as error:
            if str(error).startswith('(1062,'):
                pass
            else:
                print('Error ocurred in: DB - saveMediaInfo --> {}'.format(error))
            
    #----------------------------------------#-----------------------------------------#

    #----------------------------------------#-----------------------------------------#

    def updatePoster(self, posts):
        #recebe um dicionario com ids de media como chave e suas urls como valores  
        self.connect()
        self.startCursor()
        for media_id in posts.keys():
            try:
                query =  'insert into poster(created_at, media_id, url, download_name) values(%s,%s,%s,%s,%s)'
                self.cursor.execute(query,(datetime.now().strftime('%y/%m/%d %H:%M:%S'),media_id, posts[media_id]['url'], str('downloaded/photo' + str(media_id) + '.jpg')))
            except BaseException as error:
                if str(error).startswith('(1062,'):
                    continue
                else:
                    print('Error ocurred in: DB - updatePoster --> {}'.format(error))
        self.cursor.close()

    def saveScheduledPosts(self):
        self.connect()
        self.startCursor()
        query = 'select scheduled from poster where scheduled is not null order by scheduled desc'
        self.cursor.execute(query)
        resposta = self.cursor.fetchone()
        self.cursor.close()
        return resposta

    def getScheduledPosts(self):
        self.connect()
        self.startCursor()
        query = 'select  url, download_name, posted, username from poster order by created_at asc limit 1'
        self.cursor.execute(query)
        resposta = self.cursor.fetchone()
        self.cursor.close()
        return resposta

    def updatePosted(self, download_name):
        self.connect()
        self.startCursor()
        query = 'update poster set posted=1, set posted_at=%s here download_name=%s'
        self.cursor.execute(query, (datetime.now().strftime('%y/%m/%d %H:%M:%S'),download_name))
        self.cursor.close()


    #----------------------------------------#-----------------------------------------#    
    #----------------------------------------#-----------------------------------------#
    #----------------------------------------#-----------------------------------------#



if __name__ == '__main__':
    dt = Database()
    print(dt.getProfiles('full'))
    # horario_atual =  dt.getScheduledPosts()
    # novo_horario = horario_atual+2
    # print(novo_horario)
