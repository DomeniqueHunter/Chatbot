#!/usr/bin/env python3
import json
import sys


def load_from_file(file:str):
    with open(file, 'r') as fp:
        return json.load(fp)

    
def save_to_file(file:str, content:str):
    with open(file, 'w') as fp:
        json.dump(content, fp)
        

def dictvals_to_list(data:dict):
    data_list = []
    for entry in data.values():
        data_list.append(entry.lower())
        
    return data_list


def dry_run(content):
    print('Dry Run!')
    print(type(content))
    print(content)

def main():
    args = sys.argv
    
    if len(args) == 1:
        exit()
        
    if len(args) == 2:
        # dry run
        file_path = args[1]
        
        content = load_from_file(file_path)
        dry_run(content)
        
    else:
        file_path = args[1]
        do_it = args[2]
        
        content = load_from_file(file_path)
        if type(content) == dict and do_it == '-y':
            print("we have work to do")
            content = dictvals_to_list(content)
            save_to_file(file_path, content)
            print("done")
        
        if type(content) == dict and do_it != '-y':
            dry_run(content)
            print('can become:')
            print(dictvals_to_list(content))
            
            
        elif type(content) == list:
            print("Is already a list, nothing to do")
        
        else:
            print("i don't know what to do")
            print(type(content))


if __name__ == "__main__":
    main()        
