#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Tryin to find duplicated accouts """
import pandas as pd
import re
import json

FL_REGEX = re.compile(r'^[^\w]*\.?(s|a|sa|s.a|de|c|v|cv|c.v|r|l|rl|r.l|[^\w]*|(plastico\w{0,2})|(textil\w{0,3})|(servic\w{3})|(internaciona\w{1,3})|(industri\w{1,4})|(technolog\w{1,3})|(maquila\w{0,4})|(produc\w{3,4})|(manufact\w{4,6})|(interna\w{4,6})|(electronic\w{1,2})|)\.?[^\w]*$')
TO_DELETE = ['.', ';', ':', ',', '-', '+', '/', '_', '(', ')', 'mexico', 'méxico', 'mexicana',
             'méxicana', 'ensambladora', 'packaging', 'agencia aduanal', 'monterrey', 'california', 'tijuana', 'mexicali', 'tecate', 'systems', 'sistemas']
FULL_MATCHS = []
CHECK_LIST = []

def nmFilter(nm):
    """ Elimina patrones poco utiles """
    return " ".join(list(filter(lambda x: FL_REGEX.match(x) == None, nm)))


def cleanData(df):
    """ Funcion para limpiar los nombres de las empresas """
    df['name'] = df['name'].str.lower().str.strip()
    df['name'] = df['name'].str.split(" ")
    df['name'] = df['name'].apply(nmFilter)

    for i in TO_DELETE:
        df['name'] = df['name'].str.replace(i, '')

    df['name'] = df['name'].str.strip()


class Acc:
    """ docstring """
    def __init__(self, name, id, score, get_name, proximity_criteria=0.6):
        self.fullName = name
        self.n_tokens = 0
        self.tokens = self.tokenize(name, set_tk_count=True)
        self.id = id
        self.neighbours = {}
        self.known_ids = []
        self.prox_cr = proximity_criteria
        self.score = score
        self.get_name = get_name


    def tokenize(self, str, tk_sz=3, set_tk_count=False):
        """ Convert a string into a list of tokens """
        tkns = [str[:tk_sz]]

        i = tk_sz + 1
        while (i <= len(str)):
            tkns.append(str[i - tk_sz : i])
            i += 1

        if set_tk_count:
            self.n_tokens = i - tk_sz

        return tkns


    def __str__(self):
        return self.fullName #f'Name: {self.fullName} - {self.n_tokens} tokens'


    def match(self, obj):
        """ Get the proximity estimation with another Acc """
        global FULL_MATCHS

        if (obj.id not in self.known_ids) and (obj.id not in self.neighbours):
            matched_indexes = []
            for tk in self.tokens:
                
                if len(matched_indexes) == len(obj.tokens):
                    break

                for i, tk2 in enumerate(obj.tokens):
                    if (i not in matched_indexes) and (tk == tk2):
                        matched_indexes.append(i)
            
            cp, np = len(matched_indexes)/self.n_tokens, len(matched_indexes)/obj.n_tokens
            full = False

            if cp >= self.prox_cr:
                self.neighbours[obj.id] = cp
                full = True
            else:
                self.known_ids.append(obj.id)

            if np >= obj.prox_cr:
                obj.neighbours[self.id] = np
                if full:

                    r, d = (obj.id, self.id) if (self.score > obj.score) else (obj.id, self.id)
                    
                    add = lambda arr: arr.append({"remains": r, "delete": d})

                    # request user confirmation
                    if __name__ == '__main__':
                        resp = input(f'Add\n\t{self.get_name(self.id)}\nand\n\t{self.get_name(obj.id)}\nto resulting list? (y/c (check list)/otherwise): ').strip()
                        if resp == 'y':
                            add(FULL_MATCHS)
                        elif resp == 'c':
                            add(CHECK_LIST)
                        print()
                    else:
                        add(FULL_MATCHS)
                    # print('FMATCH', cp, np)
                    # print(self.fullName, "\n", obj.fullName, "\n\n")
            else:
                obj.known_ids.append(self.id)
    

def main():
    df = pd.read_csv('accounts.csv')
    sdf = pd.read_csv('accounts.csv')
    cleanData(df)
    
    df['name'] = df.apply(lambda row: Acc(row['name'], row['id'], row['qnty'], lambda id: sdf[sdf['id'] == id]['name'].values[0]), axis=1)
    accounts = df['name'].values

    n_accounts = len(accounts) - 1

    for i, acc in enumerate(accounts):
        if i != n_accounts:
            for i in accounts[i+1:]:
                acc.match(i)

    print(len(FULL_MATCHS) , 'near accounts of', n_accounts + 1)
    with open('accounts_ids.json', 'wt') as file:
        file.write(json.dumps(FULL_MATCHS))
    with open('ck_ids.json', 'wt') as file:
        file.write(json.dumps(FULL_MATCHS))
    
    print('file "accounts_ids.json" created.')
    print('file "ck_ids.json" created.')

if __name__ == '__main__':
    main()