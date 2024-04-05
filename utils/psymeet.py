from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import json
import re
import time

class PsyMeet:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get('https://www.psymeetsocial.com/busca')
        self.driver.maximize_window()
        self.quantidade_de_buscas = 500
        self.psicologos = {'psicologos': []}
        self.localidade_por_ddd = ""
        self.wait = WebDriverWait(self.driver, 10)

    def obter_crp(self, elemento):
        return elemento.find_elements(by='tag name', value='p')[3].text.split(' ')[1].replace('CRP:', '')
    def extrair_numero_de_telefone(self, texto):
        regex = r'(\(?\d{2}\)?\s)?(\d{4,5}-\d{4})'
        telefone = ''
        lista = re.findall(regex, texto)
        for numero in lista:
            telefone += numero[0] + numero[1]
        return telefone
    
    def obter_sexo(self, elemento):
        nomeclatura = elemento.find_element(by='class name', value='PsychologistCard_genderName__WCR4n').text
        if nomeclatura == 'Psicóloga':
            return 'F'
        elif nomeclatura == 'Psicólogo':
            return 'M'
        else:
            return 'N'
    
        
    #o parametro elemento é um objeto do selenium
    def obter_lista_de_especialidades(self, elemento):
        lista_de_especialidades = []
        especialidades = elemento.find_elements(by='class name', value='PsychologistCard_background__fIIBV')
        for especialidade in especialidades:
            lista_de_especialidades.append(especialidade.text)
        return lista_de_especialidades
    
    def salvar_em_json(self):
        try:
            # Carregar dados existentes
            with open('data/psicologos.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            # Se o arquivo não existir, criar um novo dicionário
            data = {'psicologos': []}

        # Adicionar novos dados
        data['psicologos'].extend(self.psicologos['psicologos'])

        # Escrever dados de volta ao arquivo
        with open('data/psicologos.json', 'w') as file:
            json.dump(data, file, indent=4)

    def obter_estado(self, elemento):
       ddds = {
              '11': 'SP',
              '12': 'SP',
              '13': 'SP',
              '14': 'SP',
              '15': 'SP',
              '16': 'SP',
              '17': 'SP',
              '18': 'SP',
              '19': 'SP',
              '21': 'RJ',
              '22': 'RJ',
              '24': 'RJ',
              '27': 'ES',
              '28': 'ES',
              '31': 'MG',
              '32': 'MG',
              '33': 'MG',
              '34': 'MG',
              '35': 'MG',
              '37': 'MG',
              '38': 'MG',
              '41': 'PR',
              '42': 'PR',
              '43': 'PR',
              '44': 'PR',
              '45': 'PR',
              '46': 'PR',
              '47': 'SC',
              '48': 'SC',
              '49': 'SC',
              '51': 'RS',
              '53': 'RS',
              '54': 'RS',
              '55': 'RS',
              '61': 'DF',
              '62': 'GO',
              '63': 'TO',
              '64': 'GO',
              '65': 'MT',
              '66': 'MT',
              '67': 'MS',
              '68': 'AC',
              '69': 'RO',
              '71': 'BA',
              '73': 'BA',
              '74': 'BA',
              '75': 'BA',
              '77': 'BA',
              '79': 'SE',
              '81': 'PE',
              '82': 'AL',
              '83': 'PB',
              '84': 'RN',
              '85': 'CE',
              '86': 'PI',
              '87': 'PE',
              '88': 'CE',
              '89': 'PI',
              '91': 'PA',
                '92': 'AM',
            
              '93': 'PA',
              '94': 'PA',
              '95': 'RR',
              '96': 'AP',
              '97': 'AM',
              '98': 'MA',
              '99': 'MA',
        }
       return ddds[elemento]

    

            

    def scrape(self):
        self.driver.execute_script('window.scrollBy(0, 100)')
        time.sleep(2)
        while self.quantidade_de_buscas > 0:
            lista_psicologo = self.driver.execute_script('return document.getElementsByClassName("PsychologistCard_cardContainer__RKgDL layout_container__1KHHo")')
            try:
                for psicologo in lista_psicologo:
                    numero_telefone = psicologo.find_element(by='class name', value='WhatsappContactButton_phoneNumber__EJ2bP')   
                    ddd = numero_telefone.text.split(' ')[1][1:3]
                    if ddd == self.localidade_por_ddd or self.localidade_por_ddd == '':
                        
                        crp = self.obter_crp(psicologo)
                        # Verifique se o CRP já existe na lista
                        if not any(p['crp'] == crp for p in self.psicologos['psicologos']):
                            profissional = {
                                'crp': crp,
                                'nome': psicologo.find_element(by='class name', value='PsychologistCard_name__1begB').text,
                                'link': psicologo.find_element(by='class name', value='PsychologistCard_profileImageContainer__3iDMG').get_attribute('href'),
                                'especialidades': self.obter_lista_de_especialidades(psicologo),
                                'sexo': self.obter_sexo(psicologo),
                                'estado': self.obter_estado(ddd),
                            }
                            self.psicologos['psicologos'].append(profissional)
                    psicologo.parent.execute_script('return arguments[0].remove()', psicologo)
                
                if self.psicologos['psicologos'] != []:
                    self.salvar_em_json()
                self.psicologos = {'psicologos': []}
                try:
                    self.driver.find_element(by='class name', value='SeeMoreProfilesButton_seeMoreProfilesButton__1FHZ-').click()
                except:
                    break
                
                self.quantidade_de_buscas -= 1


            except Exception as e:
                print(e)


