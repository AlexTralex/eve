from requests import request
import re
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from datetime import datetime
updCell = "R2"
processCelltext = "Q3"
processCell = "R3"
while (1):
    try:
        start_time = time.time()
        google_data = request("GET", "https://drive.google.com/uc?export=download&id=1TqBhBvDKevkSgs4wTGPZ6I_WoB9rWEuV").text
        with open("cre.json", "w") as f:
            f.write(google_data)
        f.close()
        google_time = time.time()
        shLink = ("https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive")
        my_creds = ServiceAccountCredentials.from_json_keyfile_name("cre.json", shLink)
        client = gspread.authorize(my_creds)
        os.remove("cre.json")
        sheet = client.open("BEEK")
        sheet = sheet.worksheet("ЦЕНЫ БОТА")
        pricesheet = client.open("BEEK")
        pricesheet = pricesheet.worksheet("данные по ресурсам")

        def numbers(line):
            data = ""
            for i in (re.findall("\d+", line)):
                data += i
            return (data)

        while(1):
            lookSheet = client.open("BEEK")
            lookSheet = lookSheet.worksheet("скиллы/цены")
            sheet.update(processCelltext, "В процессе")
            readtable = lookSheet.get("B17:B18")
            avgMathDays = int(readtable[0][0]) * 24
            freq = int(readtable[1][0]) * 60
            start_time = time.time()
            updCellTime = time.time()
            ids = sheet.col_values(10)[1:]
            sumIds = len(ids)
            st = 1
            data = []
            mathSell = 0
            mathBuy = 0
            mathVol = 0

            for i in ids:
                dataRow = []
                st += 1
                pr = (str(round((((st -1)/sumIds)*100),1)) + " %")
                t = request('GET', "https://api.eve-echoes-market.com/market-stats/" + i).json()
                if ((time.time() - updCellTime) > 1.2):
                    sheet.update(processCell, pr)
                    updCellTime = time.time()
                idData = t[-1]
                for i in range(2, avgMathDays + 2):
                    try: mathSell += t[-i]['sell']
                    except: pass
                    try: mathBuy += t[-i]['buy']
                    except: pass
                    try: mathVol += t[i]['volume']
                    except: pass
                mathSell /= avgMathDays
                mathBuy /= avgMathDays
                mathVol /= avgMathDays
                dataRow.append(t[-1]['sell'])
                dataRow.append(t[-1]['buy'])
                dataRow.append(t[-1]['volume'])
                dataRow.append(mathSell)
                dataRow.append(mathBuy)
                dataRow.append(mathVol)
                data.append(dataRow)
            sheet.update('K2:P2268', data)
            sheet.update(processCelltext, "Обновление цен ресурсов")
            resList = [42001000000, 42001000001, 42001000002, 42001000003, 42001000004, 42001000005, 42001000006, 42001000007,
                       42001000008, 42001000009, 42001000010, 42001000011, 42001000018, 42001000019, 42001000020, 42001000021,
                       42001000022, 42001000023, 42001000024, 42001000025, 42001000026, 42001000027, 42001000028, 42001000029,
                       42001000030, 42001000031, 42001000032, 42001000033, 42002000012, 42002000013, 42002000014, 42002000015,
                       42002000016, 42002000017, 41000000000, 41000000002, 41000000003, 41000000004, 41000000005, 41000000006,
                       41000000007, 41000000008, 28007000000]
            t = request('GET', "https://api.eve-echoes-market.com/market-stats/" + str(resList[0])).json()
            num = len(t)
            n = -1
            resourses = [[] for _ in range(num)]
            for i in t:
                n += 1
                resourses[n].append(datetime.utcfromtimestamp(i["time"]).strftime('%d.%m.%Y %H:%M:%S'))
            for i in resList:
                t = request('GET', "https://api.eve-echoes-market.com/market-stats/" + str(i)).json()
                n = -1
                for j in range(num):
                    n += 1
                    try:
                        sell = int(((t)[j])["sell"])
                    except:
                        sell = 0
                        buy = 0
                    if (sell != 0):
                        try:
                            buy = int(((t)[j])["buy"])
                        except:
                            buy = 0
                            sell = 0
                    cena = (sell + buy) / 2
                    resourses[n].append(cena)
                    try: resourses[n].append(int(((t)[j])["volume"]))
                    except: resourses[n].append(0)
            pricesheet.update('D2:CL2376', resourses)
            sheet.update(processCelltext, "До следующего запуска, минут")
            sheet.update(processCell, "Рассчет...")
            updCellTime = time.time()
            curTime = datetime.now()
            sheet.update(updCell, str(curTime.day) + "." + str(curTime.month) + "." + str(curTime.year) + " " + str(curTime.hour) + ":" + str(curTime.minute) + ":" + str(curTime.second))
            while ((time.time() - start_time) < freq):
                nextUpd = round((freq - (time.time() - start_time))//60)
                if ((time.time() - updCellTime) > 60):
                    sheet.update(processCell, nextUpd)
                    updCellTime = time.time()
    except: pass
