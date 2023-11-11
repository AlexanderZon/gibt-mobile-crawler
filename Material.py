from HttpClient import HttpClient
import json
import time

class Material(HttpClient):

    _json_folder = 'materials'
    
    def __init__(self, id, write_files = False):
        try: 
            self._endpoint = id
            self.main_info = {
                'id': None,
                'name': None,
                'rarity': None,
                'description': None,
                'material_type': None,
                'weekdays': [],
            }
            self.main_info['id'] = id
            self.gallery = []
            super().__init__()
            self.getMainTableInfo()
            self.getGallerySectionInfo()
            self.saveMaterialJSONFile()
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
                        stars = row[1].count('<img decoding=async alt=Raritystr class=cur_icon src=/img/icons/star_35.webp')
                        if(stars == 0): stars = row[1].count('<img decoding="async" alt="Raritystr" class="cur_icon" src="/img/icons/star_35.webp')
                        self.main_info[row[0].lower()] = stars
                    case "Family":
                        self.main_info['material_type'] = None
                        material_type = self.findAll(r'\[(.+?)\]', self.cleanHtml(row[1]))
                        for j in range(len(material_type)):
                            match(material_type[j]):
                                case "CharJewel":
                                    self.main_info['material_type'] = 'Jewel'
                                case "Char Jewel":
                                    self.main_info['material_type'] = 'Jewel'
                                case "Char Elemental Stone":
                                    self.main_info['material_type'] = 'ElementalStone'
                                case "Char ElementalStone":
                                    self.main_info['material_type'] = 'ElementalStone'
                                case "Char Common Item":
                                    self.main_info['material_type'] = 'CommonItem'
                                case "Char CommonItem":
                                    self.main_info['material_type'] = 'CommonItem'
                                case "Char Local Material":
                                    self.main_info['material_type'] = 'LocalMaterial'
                                case "Char LocalMaterial":
                                    self.main_info['material_type'] = 'LocalMaterial'
                                case "Talent Book":
                                    self.main_info['material_type'] = 'Book'
                                case "TalentBook":
                                    self.main_info['material_type'] = 'Book'
                                case "Talent Boss Item":
                                    self.main_info['material_type'] = 'BossItem'
                                case "Talent BossItem":
                                    self.main_info['material_type'] = 'BossItem'
                                case "Wep Common Item":
                                    self.main_info['material_type'] = 'CommonItem'
                                case "Wep CommonItem":
                                    self.main_info['material_type'] = 'CommonItem'
                                case "Talent Common Item":
                                    self.main_info['material_type'] = 'CommonItem'
                                case "Talent CommonItem":
                                    self.main_info['material_type'] = 'CommonItem'
                                case "Talent Reward Item":
                                    self.main_info['material_type'] = 'RewardItem'
                                case "Talent RewardItem":
                                    self.main_info['material_type'] = 'RewardItem'
                                case "Wep Primary Ascension Material":
                                    self.main_info['material_type'] = 'PrimaryAscensionMaterial'
                                case "Wep Primary AscensionMaterial":
                                    self.main_info['material_type'] = 'PrimaryAscensionMaterial'
                                case "Wep Secondary Ascension Material":
                                    self.main_info['material_type'] = 'SecondaryAscensionMaterial'
                                case "Wep Secondary AscensionMaterial":
                                    self.main_info['material_type'] = 'SecondaryAscensionMaterial'
                    case "Open in Weekday":
                        weekdays = row[1].split(',')
                        for weekday in weekdays:
                            weekday = weekday.strip()
                            match(weekday):
                                case 'Monday':
                                    self.main_info['weekdays'].append(weekday)
                                case 'Tuesday':
                                    self.main_info['weekdays'].append(weekday)
                                case 'Wednesday':
                                    self.main_info['weekdays'].append(weekday)
                                case 'Thursday':
                                    self.main_info['weekdays'].append(weekday)
                                case 'Friday':
                                    self.main_info['weekdays'].append(weekday)
                                case 'Saturday':
                                    self.main_info['weekdays'].append(weekday)
                                case 'Sunday':
                                    self.main_info['weekdays'].append(weekday)
                    case "Description":
                        self.main_info['Description'.lower()] = self.cleanHtml(row[1])
      
    def appendImage(self, type, url):
        lower_type = None
        match(type):
            case 'Icon':
                lower_type = 'icon'
        
        if(lower_type != None):
            self.gallery.append({ 'type': lower_type, 'url': url})
            image_response = self.requestUrl(url)
            fp = open('assets/materials/'+self.main_info['id']+'_'+lower_type+'.webp', 'wb')
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
        return data

    def saveMaterialJSONFile(self):
        json_file = open("data/materials/"+self.main_info['id']+".json", "w")

        json_file.write(self.dumpJSON(self.parseData()))
        json_file.close()


if(__name__ == '__main__'):
    characters_json_file = open("data/characters.json", "r")
    characters_data = json.load(characters_json_file)
    weapons_json_file = open("data/weapons.json", "r")
    weapons_data = json.load(weapons_json_file)

    materials_list = []
    for character in characters_data['list']:
        for ascension_material in character['ascension_materials']:
            if(not ascension_material['id'] in materials_list):
                materials_list.append(ascension_material['id'])
        for ascension_material in character['skill_ascension_materials']:
            if(not ascension_material['id'] in materials_list):
                materials_list.append(ascension_material['id'])
    for weapon in weapons_data['list']:
        for ascension_material in weapon['ascension_materials']:
            if(not ascension_material['id'] in materials_list):
                materials_list.append(ascension_material['id'])
    
    clean_35 = True
    if(clean_35):
        materials_list = list(map(lambda material: material[0:(len(material))], materials_list))
    
    materials_data = []
    for material in materials_list:
        print(material)
        data = Material(material, write_files=False)
        materials_data.append(data.parseData())
        print(' - '+data.main_info['name'] + ': ok')
    
    json_file = open("data/materials.json", "w")

    json_file.write(json.dumps({'list': materials_data }))
    json_file.close()
