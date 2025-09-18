import requests
import json
import time

from core.lib.HTTPClient.HTTPClient import HTTPClient

class Api():
    
    @staticmethod
    async def get_ticket(account, password, try_nr=0, max_trys=10):
        data={'account': account, 'password': password}
        
        try:
            request = await HTTPClient.post('https://www.f-list.net/json/getApiTicket.php', data)
            
            if "error" in request:
                print(request["error"])
                
            if "ticket" in request:
                return request['ticket']
            
            exit(0)
        
        except Exception as e:
            if try_nr <= max_trys:
                time.sleep(1)
                return await Api.get_ticket(account, password, try_nr=try_nr+1)
            else:
                print(f"ERROR: Too many reconnect trys failed ({try_nr})")
                print(f"ERROR: {e} [{type(e).__name__}]")
                exit(0)   
    
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
        