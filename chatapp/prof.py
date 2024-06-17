from bs4 import BeautifulSoup
import requests
import pprint
from base64 import b64decode
from tqdm import tqdm
import multiprocessing
import sys
import time

class professor:
    def __init__(self):    
        if type(self) is professor:
            raise NotImplementedError("Subclasses must implement this method")
        self.cname = ""
        self.ename = ""  
        self.ename_strip = ""      
        self.dept = ""
        self.lab = ""
        self.laburl = ""
        self.research = []
        self.url = ""
        self.imageurl = ""
        self.email = ""
        self.personalurl = ""
        return
    def print(self):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.__dict__)
    def to_dict(self):        
        return {
            'url': self.url,
            'cname': self.cname, 
            'ename': self.ename,
            'ename_strip': self.ename_strip, 
            'dept': self.dept, 
            'lab': self.lab, 
            'laburl': self.laburl,
            'research': self.research, 
            'imageurl': self.imageurl,
            'email': self.email,
            'personalurl': self.personalurl}
    
class NTU_prof(professor):
    def __init__(self, url):
        super().__init__()
        self.url = url
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        name = soup.find('td', class_='member-data-value-name').get_text(strip=True)
        try:
            self.cname = name.split('(')[0][:-1]
            self.ename = name.split('(')[1][:-1]
        except:
            self.cname = name.split('（')[0]
            self.ename = name.split('（')[1][:-1]
        self.ename_strip = self.ename.replace(" ", "-").replace(".", "-")
        self.dept = "資訊工程學系"

        try:
            lab = soup.find('td', class_='member-data-value-8').find('a')
            self.lab = lab.get_text(strip=True)
            self.laburl = lab.get('href')
        except:
            pass       
        
        res_element = soup.find('td', class_='member-data-value-7')
        res = res_element.get_text(strip=True).split("、")
        if len(res) == 1:
            self.research = res[0].split(', ')
        else:
            self.research = res
        
        imageurl = soup.find('div', class_='member-pic col-xs-3').find('img').get('src')
        self.imageurl = "https://csie.ntu.edu.tw" + imageurl        

        email_raw = soup.find('td', class_='member-data-value-email').find('script').get_text(strip=True)
        email_b64 = email_raw.split("atob(\"")[1].split("\"")[0]
        self.email = b64decode(email_b64).decode("UTF-8")

        self.personalurl = soup.find('td', class_='member-data-value-6').find('a').get('href')
        
    
class NYCU_prof(professor):    
    def __init__(self, url):
        super().__init__()
        self.url = url
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        name = soup.find('h1')
        try:
            self.cname = name.get_text(strip=True, separator='|').split('|')[0]
        except:
            pass
        self.ename = name.find('small').get_text(strip=True)
        self.ename_strip = self.ename.replace(" ", "-")
        # print(self.ename)
        # print(self.ename_strip)
        self.dept = "資訊工程學系"
        
        try:
            lab_info = soup.find_all('ul', class_="info-list")[1]
            self.lab = lab_info.find('i', class_='fa-building-o').find_parent('li').get_text(strip=True)
        except:
            pass       
        try:
            self.laburl = lab_info.find_all('a')[1].get_text(strip=True)
        except:
            pass

        self.email = soup.find('i', class_='fa fa-envelope-o').find_parent('li').get_text(strip=True).replace("[at]", "@")
        self.imageurl = soup.find('img', class_='avatar').get('src')
        research = soup.find('div', class_='researchs').get_text(strip=True)
        if '，' in research:
            self.research = research.split("，")
        elif "\r\n" in research:
            self.research = [s.strip() for s in research.split('\r\n')]
        elif '、' in research:
            self.research = research.split("、")        
        elif ", " in research:
            self.research = [s.strip('and ').strip() for s in research.split(', ')]
        elif "," in research:
            self.research = research.split(",")
        else:
            self.research = [research]
        try:
            self.personalurl = soup.find('i', class_='fa fa-home').find_next_sibling('a').get('href')
        except:
            pass
        
    
    
class NTHU_prof(professor):    
    def __init__(self, url, prof):
        super().__init__()
        self.url = url
        try:
            self.personalurl = prof.find_all('td')[0].find('a').get('href')
        except:
            pass
        if self.personalurl == 'target=':
            self.personalurl = ""
        imageurl = prof.find_all('td')[0].find('img').get('src')
        self.imageurl = "https://dcs.site.nthu.edu.tw" + imageurl
        name = prof.find_all("td")[1]
        self.cname = name.find_all('div')[0].get_text(strip=True).split(' ')[0]
        if len(name.find_all('div')) == 4:
            self.ename = name.find_all('div')[3].get_text(strip=True).split('(')[0]
        elif len(name.find_all('div')) == 3:
            self.ename = name.find_all('div')[2].get_text(strip=True).split('(')[0]
        else:
            self.ename = name.find_all('div')[1].get_text(strip=True).split('(')[0]
        self.ename_strip = self.ename.replace(" ", "-")

        self.dept = "資訊工程學系"
        self.email = prof.find_all("td")[2].get_text(strip=True)[3:]
        if len(prof.find_all('td')) == 6:
            research = prof.find_all("td")[4].get_text(strip=True)[3:]
        else:
            research = prof.find_all("td")[3].get_text(strip=True)[3:]
        if '、' in research:
            self.research = research.split('、')
        elif ', ' in research:
            self.research = [s.strip() for s in research.split(', ')]            
        else:
            self.research = research
        # self.print()

def main():
    pass
        

if __name__ == '__main__':
    main()