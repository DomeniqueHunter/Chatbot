import requests
import json
import aiohttp

from lib.HTTPClient.HTTPClient import HTTPClient

class Api():
    
    @staticmethod
    async def get_ticket(account, password):
        data={'account': account, 'password': password}
                    
        #request = requests.post('https://www.f-list.net/json/getApiTicket.php', data)
        request = await HTTPClient.post('https://www.f-list.net/json/getApiTicket.php', data)
        
        #print ("GOT: "+ str(request['ticket']))
                
        try:
            #assert request.status_code == 200        # from requests
            #data = json.loads(request.text)
            #return data['ticket']
            return request['ticket']
        except:
            print("ERROR, could not require a ticket")
            exit(1) 
        
    
    @staticmethod    
    def send_friend_request(account, ticket, from_char, to_char):
        #ticket = Api.get_ticket(account, password)
        data={'account': account,
              'ticket': ticket,
              'source_name': from_char,
              'dest_name': to_char           
              }
        request = requests.post('https://www.f-list.net/json/request-send.php', data)
        print(request.text)
        
        if (request.status_code == 200):
            data = json.loads(request.text)
            return data
        else:
            print("ERROR, could not require a ticket")
            exit(1)

    @staticmethod
    def get_character_data(ticket, account, charactername):
        data = {'ticket': ticket,
                'account': account,
                'name': charactername
                }
        request = requests.post('https://www.f-list.net/json/api/character-data.php', data)
        if request.status_code == 200:
            data = json.loads(request.text)
            print ( data )
        else:
            print ( " error ")
        