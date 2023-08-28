from HttpClient import HttpClient
from data import characters
import json
import time

class Character(HttpClient):

    _json_folder = 'characters'
    
    def __init__(self, id, order):
        try: 
            self._endpoint = id
            self.order = order
            self.main_info = {}
            self.main_info['id'] = id
            self.stats = []
            self.skills = []
            self.gallery = []
            super().__init__()
            self.getMainTableInfo()
            self.getStatsTableInfo()
            self.getSkillsTableInfo()
            self.getGallerySectionInfo()
            self.saveCharacterJSONFile()
        except Exception as e:
            print(e)
            print('Class Error. Sleeping 30 seconds')
            time.sleep(30)
            self.__init__(id)

    def getMainTableInfo(self):
        main_table = self.findAll(r'<table class="genshin_table main_table">(.+?)</table>', self._response)
        
        # main_info['description'] = None
        if(len(main_table) > 0):
            main_table_rows = self.findAll(r'<tr>(.+?)</tr>', main_table[0])
            for i in range(len(main_table_rows)):
                row = self.findAll(r'<td>(.+?)</td>', main_table_rows[i])
                match row[0]:
                    case "Rarity":
                        stars = row[1].count('<img decoding=async alt=Raritystr class=cur_icon src=/img/icons/star_35.webp')
                        if(stars == 0): stars = row[1].count('<img decoding="async" alt="Raritystr" class="cur_icon" src="/img/icons/star_35.webp')
                        self.main_info[row[0].lower()] = stars
                    case "Weapon":
                        weapon = self.findAll('/img/icons/weapon_types/(.+?)_35.webp', row[1])     
                        if(len(weapon) > 0):
                            self.main_info['weapon_type'] = weapon[0].capitalize()
                        else:
                            self.main_info['weapon_type'] = 'unknown'
                    case "Element":
                        element = self.findAll('<img decoding=async loading=lazy alt=Element class=cur_icon src=/img/icons/element/(.+?)_35.webp', row[1])     
                        if(len(element) == 0): element = self.findAll('<img decoding="async" loading="lazy" alt="Element" class="cur_icon" src="/img/icons/element/(.+?)_35.webp"', row[1])     
                        
                        if(len(element) > 0):
                            self.main_info[row[0].lower()] = element[0].capitalize()
                        else:
                            self.main_info[row[0].lower()] = 'unknown'
                    case "Vision (Introduced)":
                        self.main_info['Vision'.lower()] = row[1]
                    case "Constellation (Introduced)":
                        self.main_info['Constellation'.lower()] = row[1]
                    case "Association":
                        self.main_info['Association'.lower()] = row[1].capitalize()
                    case "Character Ascension Materials":
                        ascension_materials = self.findAll(r'<img decoding=async loading=lazy alt="(.+?)" src=/img/(.+?).webp', row[1]) 
                        if(len(ascension_materials) == 0): ascension_materials = self.findAll(r'<img decoding="async" loading="lazy" alt="(.+?)" src="/img/(.+?).webp', row[1]) 
                        self.main_info['ascension_materials'] = []
                        if(len(ascension_materials) > 0):
                            for material in ascension_materials:
                                self.main_info['ascension_materials'].append({'id': self.cleanMaterialId(material[1]), 'name': material[0]})
                    case "Skill Ascension Materials":
                        ascension_materials = self.findAll(r'<img decoding=async loading=lazy alt="(.+?)" src=/img/(.+?).webp', row[1]) 
                        if(len(ascension_materials) == 0): ascension_materials = self.findAll(r'<img decoding="async" loading="lazy" alt="(.+?)" src="/img/(.+?).webp', row[1]) 
                        self.main_info['skill_ascension_materials'] = []
                        if(len(ascension_materials) > 0):
                            for material in ascension_materials:
                                self.main_info['skill_ascension_materials'].append({'id': self.cleanMaterialId(material[1]), 'name': material[0]})
                                
                    case "Day of Birth":
                        self.main_info['day_of_birth'] = row[1]
                    case "Month of Birth":
                        self.main_info['month_of_birth'] = row[1]
                    case _:
                        if("seuyu" in row[0].lower()):
                            continue
                        self.main_info[row[0].lower()] = self.cleanHtml(row[1])
        if(not('description' in self.main_info)): self.main_info['description'] = '(Without description)'
    
    def getStatsTableInfo(self):
        stat_table = self.findAll(r'<table class="genshin_table stat_table">(.+?)</table>', self._response)
        variable_stat = None
        if(len(stat_table) > 0):
            stat_table_header = self.findAll(r'<thead>(.+?)</thead>', stat_table[0])
            if(len(stat_table_header) > 0):
                stat_table_heder_columns = self.findAll(r'<td>(.+?)</td>', stat_table_header[0])
                if(len(stat_table_heder_columns) > 6): 
                    variable_stat = stat_table_heder_columns[6].replace("Bonus ", "")
                    variable_stat = variable_stat.replace("Bonuse ", "")
            stat_table_content = self.findAll(r'<tr>(.+?)</tr>', stat_table[0])
            if(len(stat_table_content) > 0):
                stat_table_row_ascension_materials = None
                for i in range(1, len(stat_table_content)):
                    stat_table_content_columns = self.findAll(r'<td>(.+?)</td>', stat_table_content[i])
                    stat_table_content_advanced_columns = self.findAll(r'<td rowspan=2 class=hmb>(.+?)</td>', stat_table_content[i])
                    if(len(stat_table_content_advanced_columns) == 0): stat_table_content_advanced_columns = self.findAll(r'<td rowspan="2" class="hmb">(.+?)</td>', stat_table_content[i])
                    stat_data = {}
                    stat_data['level'] = stat_table_content_columns[0]
                    stat_data['hp'] = float(stat_table_content_columns[1])
                    stat_data['atk'] = float(stat_table_content_columns[2])
                    stat_data['def'] = float(stat_table_content_columns[3])
                    stat_data['crit_rate'] = float(stat_table_content_columns[4].replace("%", ""))
                    stat_data['crit_dmg'] = float(stat_table_content_columns[5].replace("%", ""))
                    stat_data['variable_stat'] = variable_stat
                    stat_data['variable_stat_value'] = float(stat_table_content_columns[6].replace("%", ""))
                    stat_data['materials'] = []
                    
                    if "+" in stat_data['level'] and len(stat_table_row_ascension_materials) > 0:
                        for j in range(len(stat_table_row_ascension_materials)):
                            name = self.cleanHtml(stat_table_row_ascension_materials[j][0])
                            id = self.cleanMaterialId(stat_table_row_ascension_materials[j][1])
                            quantity = int(self.parseSufixes(self.cleanHtml(stat_table_row_ascension_materials[j][3])))
                            stat_data['materials'].append({ 'id': id, 'name': name, 'quantity': quantity})
                            
                    self.stats.append(stat_data)
                    if(len(stat_table_content_advanced_columns) > 0):
                        stat_table_row_ascension_materials = self.findAll(r'<img decoding=async loading=lazy alt="(.+?)" src=/img/(.+?).webp(.+?)><span>(.+?)</span>', stat_table_content_advanced_columns[0])
                        if(len(stat_table_row_ascension_materials) == 0): stat_table_row_ascension_materials = self.findAll(r'<img decoding="async" loading="lazy" alt="(.+?)" src="/img/(.+?).webp(.+?)><span>(.+?)</span>', stat_table_content_advanced_columns[0])
                        # stat_table_row_mora = self.findAll(r'<img loading=lazy alt=Mora src=/img/(.+?).webp(.+?)><span>(.+?)</span>', stat_table_content_advanced_columns[0])
                        # if(len(stat_table_row_mora) == 0): stat_table_row_mora = self.findAll(r'<img loading="lazy" alt="Mora" src="/img/(.+?).webp(.+?)><span>(.+?)</span>', stat_table_content_advanced_columns[0])
                        # if(len(stat_table_row_mora) > 0):
                        #     print(stat_table_row_mora[0])
                        #     mora_row_tuple = ("Mora", stat_table_row_mora[0][0], stat_table_row_mora[0][1], stat_table_row_mora[0][2])
                        #     stat_table_row_ascension_materials.append(mora_row_tuple)
        
    def getSkillsTableInfo(self):
        asc_table = self.findAll(r'<table class="genshin_table asc_table">(.+?)</table>', self._response)
        if(len(asc_table) > 0):
            asc_table_content = self.findAll(r'<tr>(.+?)</tr>', asc_table[0])
            for i in range(2, len(asc_table_content)):
                asc_table_content_columns = self.findAll(r'<td>(.+?)</td>', asc_table_content[i])
                asc_table_row_ascension_materials = self.findAll(r'<img decoding=async loading=lazy alt=(.+?) src=/img/(.+?).webp(.+?)><span>(.+?)</span></div></a>', asc_table_content_columns[1])
                if(len(asc_table_row_ascension_materials) == 0): asc_table_row_ascension_materials = self.findAll(r'<img decoding="async" loading="lazy" alt="(.+?)" src="/img/(.+?).webp(.+?)><span>(.+?)</span></div></a>', asc_table_content_columns[1])
                asc_data = {}
                asc_data['level'] = asc_table_content_columns[0]
                asc_data['materials'] = []
                for j in range(len(asc_table_row_ascension_materials)):
                    name = self.cleanHtml(asc_table_row_ascension_materials[j][0])
                    id = self.cleanMaterialId(asc_table_row_ascension_materials[j][1])
                    quantity = int(self.parseSufixes(self.cleanHtml(asc_table_row_ascension_materials[j][3])))
                    asc_data['materials'].append({ 'id': id, 'name': name, 'quantity': quantity})
                self.skills.append(asc_data)

    def appendImage(self, type, url):
        lower_type = None
        match(type):
            case 'Icon':
                lower_type = 'icon'
            case 'Side Icon':
                lower_type = 'side_icon'
            case 'Gacha Card':
                lower_type = 'gacha_card'
            case 'Gacha Splash':
                lower_type = 'gacha_splash'
        
        if(lower_type != None):
            self.gallery.append({ 'type': lower_type, 'url': url})
            image_response = self.requestUrl(url)
            fp = open('.assets/characters/'+self.main_info['id']+'_'+lower_type.lower()+'.webp', 'wb')
            fp.write(image_response.content)
            fp.close()

    def getGallerySectionInfo(self):
        gallery_section = self.findAll(r'<section id=char_gallery class="tab-panel tab-panel-1">(.+?)</section>', self._response)
        if(len(gallery_section) == 0): gallery_section = self.findAll(r'<section id="char_gallery" class="tab-panel tab-panel-1">(.+?)</section>', self._response)
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
        data['order'] = self.order
        data['stats'] = self.stats
        data['skills'] = self.skills
        # data['gallery'] = self.gallery
        return data

    def saveCharacterJSONFile(self):
        json_file = open(".data/characters/"+self.main_info['id']+".json", "w")

        json_file.write(self.dumpJSON(self.parseData()))
        json_file.close()


if(__name__ == '__main__'):
    characters_data = []
    materials_list = []
    counter = 0
    for character in characters:
        data = Character(character, counter)
        characters_data.append(data.parseData())
        counter += 1
        print(' - '+data.main_info['name'] + ': ok')
    
    json_file = open(".data/characters.json", "w")
    json_file.write(json.dumps({'list': characters_data}))
    json_file.close()
