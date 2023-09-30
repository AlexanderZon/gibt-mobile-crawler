from HttpClient import HttpClient
from data import weapons
import json
import time

class Weapon(HttpClient):

    _json_folder = 'weapons'
    
    def __init__(self, id):
        try: 
            self._endpoint = id
            self.main_info = {
                'id': None,
                'name': None,
                'rarity': None,
                'description': None,
                'weapon_type': None,
                'ascension_materials': [],
            }
            self.main_info['id'] = id
            self.stats = []
            self.skills = []
            self.gallery = []
            super().__init__()
            self.getMainTableInfo()
            self.getStatsTableInfo()
            self.getGallerySectionInfo()
            self.saveWeaponJSONFile()
        except Exception as e:
            print('Class Error. Sleeping 30 seconds')
            print(e)
            time.sleep(30)
            self.__init__(id)


    def getMainTableInfo(self):
        main_table = self.findAll(r'<table class="genshin_table main_table">(.+?)</table>', self._response)
        if(len(main_table) > 0):
            main_table_rows = self.findAll(r'<tr>(.+?)</tr>', main_table[0])
            for i in range(len(main_table_rows)):
                row = self.findAll(r'<td>(.+?)</td>', main_table_rows[i])
                match row[0]:
                    case "Name":
                        self.main_info['Name'.lower()] = self.cleanHtml(row[1])
                    case "Rarity":
                        stars = row[1].count('<img decoding=async  alt=Raritystr class=cur_icon src=/img/icons/star_35.webp')
                        if(stars == 0): stars = row[1].count('<img decoding="async" alt="Raritystr" class="cur_icon" src="/img/icons/star_35.webp')
                        self.main_info[row[0].lower()] = stars
                    case "Family":
                        weapon_type = self.findAll(r'\[(.+?)\]', self.cleanHtml(row[1]))
                        for j in range(len(weapon_type)):
                            match(weapon_type[j]):
                                case "Sword":
                                    self.main_info['weapon_type'] = 'Sword'
                                case "Claymore":
                                    self.main_info['weapon_type'] = 'Claymore'
                                case "Polearm":
                                    self.main_info['weapon_type'] = 'Polearm'
                                case "Bow":
                                    self.main_info['weapon_type'] = 'Bow'
                                case "Catalyst":
                                    self.main_info['weapon_type'] = 'Catalyst'
                    case "Description":
                        self.main_info['Description'.lower()] = self.cleanHtml(row[1])
                    case "Affix Description":
                        self.main_info['Description'.lower()] = self.cleanHtml(row[1])
                    case "Weapon Ascension Materials":
                        ascension_materials = self.findAll(r'<img decoding=async loading=lazy alt="(.+?)" src=/img/(.+?).webp', row[1]) 
                        if(len(ascension_materials) == 0): ascension_materials = self.findAll(r'<img decoding="async" loading="lazy" alt="(.+?)" src="/img/(.+?).webp', row[1]) 
                        if(len(ascension_materials) > 0):
                            self.main_info['ascension_materials'] = []
                            for material in ascension_materials:
                                self.main_info['ascension_materials'].append({'id': self.cleanMaterialId(material[1]), 'name': material[0]})

    def getStatsTableInfo(self):
        stat_table = self.findAll(r'<table class="genshin_table stat_table">(.+?)</table>', self._response)
        variable_stat = None
        if(len(stat_table) > 0):
            stat_table_header = self.findAll(r'<thead>(.+?)</thead>', stat_table[0])
            if(len(stat_table_header) > 0):
                stat_table_heder_columns = self.findAll(r'<td>(.+?)</td>', stat_table_header[0])
                if(len(stat_table_heder_columns) > 4): 
                    variable_stat = stat_table_heder_columns[2].replace("Bonus ", "")
                    variable_stat = variable_stat.replace("Bonuse ", "")
            stat_table_content = self.findAll(r'<tr>(.+?)</tr>', stat_table[0])
            if(len(stat_table_content) > 0):
                stat_table_row_ascension_materials = None
                for i in range(1, len(stat_table_content)):
                    stat_table_content_columns = self.findAll(r'<td>(.+?)</td>', stat_table_content[i])
                    stat_table_content_advanced_columns = self.findAll(r'<td rowspan=2>(.+?)</td>', stat_table_content[i])
                    if(len(stat_table_content_advanced_columns) == 0): stat_table_content_advanced_columns = self.findAll(r'<td rowspan="2">(.+?)</td>', stat_table_content[i])

                    stat_data = {}
                    stat_data['level'] = stat_table_content_columns[0]
                    stat_data['atk'] = float(stat_table_content_columns[1])
                    if(self.main_info['rarity'] > 2):
                        stat_data['variable_stat'] = variable_stat
                        stat_data['variable_stat_value'] = float(stat_table_content_columns[2].replace("%", ""))
                    stat_data['materials'] = []
                    
                    if "+" in stat_data['level'] and len(stat_table_row_ascension_materials) > 0:
                        for j in range(len(stat_table_row_ascension_materials)):
                            name = self.cleanText(self.cleanHtml(stat_table_row_ascension_materials[j][0]))
                            id = self.cleanMaterialId(stat_table_row_ascension_materials[j][1])
                            quantity = int(self.parseSufixes(self.cleanHtml(stat_table_row_ascension_materials[j][3])))
                            stat_data['materials'].append({ 'id': id, 'name': name, 'quantity': quantity})
                    self.stats.append(stat_data)

                    if(len(stat_table_content_advanced_columns) > 0):
                        stat_table_row_ascension_materials = self.findAll(r'<img decoding=async loading=lazy alt="(.+?)" src=/img/(.+?).webp(.+?)><span>(.+?)</span>', stat_table_content_advanced_columns[0])
                        if(len(stat_table_row_ascension_materials) == 0): stat_table_row_ascension_materials = self.findAll(r'<img decoding="async" loading="lazy" alt="(.+?)" src="/img/(.+?).webp(.+?)><span>(.+?)</span>', stat_table_content_advanced_columns[0])

                        # stat_table_row_mora = self.findAll(r'<img loading=lazy alt=Mora (.+?)><span>(.+?)</span>', stat_table_content_advanced_columns[0])
                        # if(len(stat_table_row_mora) == 0): stat_table_row_mora = self.findAll(r'<img loading="lazy" alt="Mora" (.+?)><span>(.+?)</span>', stat_table_content_advanced_columns[0])

                        # if(len(stat_table_row_mora) > 0):
                        #     mora_row_tuple = ("Mora", stat_table_row_mora[0][0], stat_table_row_mora[0][1])
                        #     stat_table_row_ascension_materials.append(mora_row_tuple)
                        

    def appendImage(self, type, url):
        lower_type = None
        match(type):
            case 'Icon':
                lower_type = 'icon'
            case 'Awakened Icon':
                lower_type = 'awakened_icon'
            case 'Gacha Icon':
                lower_type = 'gacha_icon'
        
        if(lower_type != None):
            self.gallery.append({ 'type': lower_type, 'url': url})
            image_response = self.requestUrl(url)
            fp = open('.assets/weapons/'+self.main_info['id']+'_'+lower_type+'.webp', 'wb')
            fp.write(image_response.content)
            fp.close()

    def getGallerySectionInfo(self):
        gallery_section = self.findAll(r'<section id=item_gallery class="tab-panel tab-panel-1">(.+?)</section>', self._response)
        if(len(gallery_section) == 0): gallery_section = self.findAll(r'<section id="item_gallery" class="tab-panel tab-panel-1">(.+?)</section>', self._response)
        if(len(gallery_section) > 0):
            gallery_section_content = self.findAll(r'<div class=gallery_cont>(.+?)</div>', gallery_section[0])
            if(len(gallery_section_content) == 0): gallery_section_content = self.findAll(r'<div class="gallery_cont">(.+?)</div>', gallery_section[0])
            for i in range(len(gallery_section_content)):
                gallery_element = self.findAll(r'<a target=_blank href=(.+?)><span class=gallery_cont_span>(.+?)</span>', gallery_section_content[i])
                if(len(gallery_element) == 0): gallery_element = self.findAll(r'<a target="_blank" href="(.+?)"><span class="gallery_cont_span">(.+?)</span>', gallery_section_content[i])
                if(len(gallery_element) > 0 and len(gallery_element[0]) > 1):
                    image_url = self.getFileFullURL(gallery_element[0][0])
                    self.appendImage(gallery_element[0][1], image_url)


    def parseData(self):
        data = self.main_info
        data['stats'] = self.stats
        # data['gallery'] = self.gallery
        return data

    def saveWeaponJSONFile(self):
        json_file = open("data/weapons/"+self.main_info['id']+".json", "w")

        json_file.write(self.dumpJSON(self.parseData()))
        json_file.close()


if(__name__ == '__main__'):
    weapons_data = []
    for weapon in weapons:
        data = Weapon(weapon)
        weapons_data.append(data.parseData())
        print(' - '+data.main_info['name'] + ': ok')
    
    json_file = open("data/weapons.json", "w")

    json_file.write(json.dumps({'list': weapons_data }))
    json_file.close()
