#!
import requests
from datetime import datetime, date, timedelta
import schedule
import time


def getProvinces():
    url = "http://ncpscxx.moa.gov.cn/product/livestock-product-info/select/province?varietyCode=AL01001"
    data = requests.get(url)
    provinces = data.json()["data"]
    unique_elements = {}
    for item in provinces:
        code = item["PROVINCE_CODE"]
        name = item["PROVINCE_NAME"]
        if code in unique_elements:
            if len(name) > len(unique_elements[code]):
                unique_elements[code] = name
        else:
            unique_elements[code] = name

    unique_data = [
        {"PROVINCE_NAME": name, "PROVINCE_CODE": code}
        for code, name in unique_elements.items()
    ]
    return unique_data


def getAllRiceProduction():
    year = date.today().year - 1
    for prvince in getProvinces():
        url = "http://ncpscxx.moa.gov.cn/product/food-product-info/getProductTrendCount?varietyCode=AA01005&provinceCode=" + \
              prvince['PROVINCE_CODE'] + "&queryStartTime=" + str(year) + "&queryEndTime=" + str(year)
        data = requests.get(url)
        print(url)
        list = data.json()["data"]["data"]
        for item in list:
            postUrl = "http://39.104.87.35:8081/farmv2/public/index.php/api/farm_produce/riceProductionCreate"
            parms = {"year": item["reportTime"],
                     "area": prvince['PROVINCE_NAME'],
                     "area_seed": item["areaSeed"],
                     "yield_total": item["yieldTotal"]
                     }
            requests.post(postUrl, data=parms)


def nationalRiceConsumptionStructure():
    year = date.today().year - 1
    url = "http://ncpscxx.moa.gov.cn/product/food-consume-other/getFoodConsumptionStructure?date=" + str(
        year) + "&varietyCode=AA01005"
    data = requests.get(url)
    list = data.json()["data"]
    for item in list:
        if item["name"] != "总数" and item["name"] != "时间":
            postUrl = "http://39.104.87.35:8081/farmv2/public/index.php/api/farm_produce/riceConsumptionStructureCreate"
            parms = {"year": year,
                     "name": item["name"],
                     "value": item["value"]
                     }
            requests.post(postUrl, data=parms)


def rice():
    current_date = datetime.now()
    yesterday = current_date - timedelta(days=1)
    formatted_date = yesterday.strftime("%Y-%m-%d")
    url = "http://ncpscxx.moa.gov.cn/product/common-price-info/wholesale/price/count?varietyCode=AA01006&date=" + formatted_date
    data = requests.get(url).json()
    dataList = data["data"]
    for item in dataList:
        postUrl = "http://39.104.87.35:8081/farmv2/public/index.php/api/farm_produce/ricePriceCreate"
        parameter = {
            "same_date": item["REPORT_TIME"],
            "province_name": item["PROVINCE_NAME"],
            "province_code": item["PROVINCE_CODE"],
            "market_name": item["MARKET_NAME"],
            "market_code": item["MARKET_CODE"],
            "longitude": item["LONGITUDE"],
            "latitude": item["LATITUDE"],
            "next_price_market": item["NEXT_PRICE_MARKET"],
            "price_market": item["PRICE_MARKET"],
            "price_difference": item["PRICE_DIFFERENCE"],
            "price_market_rate": item["PRICE_MARKET_RATE"],
        }
        result = requests.post(postUrl, data=parameter)
        try:
            print(result.text)
        except IOError as e:
            print(e)


def riceNews():
    url = "http://ncpscxx.moa.gov.cn/product/common-opinion-info/selectListByPage"
    parameters = {"currentPage": 1, "pageSize": 20, "varietyCode": "AA01005", "title": ""}
    data = requests.post(url, json=parameters)
    dataList = data.json()["data"]["records"]
    for item in dataList:
        postUrl = "http://39.104.87.35:8081/farmv2/public/index.php/api/farm_produce/publicSentimentNewsCreate"
        parameter = {
            "title": item["title"],
            "url": item["url"],
            "report_time": item["reportTime"]
        }
        result = requests.post(postUrl, data=parameter)
        try:
            print(result.json())
        except IOError as e:
            print(e)


def trendOfNationalCattleProduction():
    year = date.today().year - 1
    url = "http://ncpscxx.moa.gov.cn/product/livestock-product-stock-cattle/getCattleProductTrend"
    parameters = {"varietyCode": "AL01005", "queryStartTime": year, "queryEndTime": year}
    data = requests.post(url, json=parameters)
    list = data.json()["data"]["data"]
    for item in list:
        postUrl = "http://39.104.87.35:8081/farmv2/public/index.php/api/farm_produce/cattleProductTrendCreate"
        parms = {
            "amount_slaught": item["amountSlaught"],
            "amount_stock": item["amountStock"],
            "stock_beef": str(item["stockBeef"]),
            "stock_cow": str(item["stockCow"]),
            "year": item["quarterTime"][0:4]
        }
        result = requests.post(postUrl, data=parms)
        try:
            print(result.text)
        except IOError as e:
            print(e)


def nationalConsumerPriceIndexOfBeef():
    current_date = datetime.now()
    last_month_date = current_date.replace(day=1) - timedelta(days=1)
    timeStr = last_month_date.strftime("%Y-%m")
    url = "http://ncpscxx.moa.gov.cn/product/livestock-consume-index/consume/price/index/count?varietyCode=AL01005&queryStartTime=" + timeStr + "&queryEndTime=" + timeStr
    data = requests.get(url)
    list = data.json()["data"]
    for item in list:
        postUrl = "http://39.104.87.35:8081/farmv2/public/index.php/api/farm_produce/consumeIndexCreate"
        parms = {
            "consume_index": item["CONSUME_INDEX"],
            "month": time.strftime('%Y-%m', time.struct_time(time.strptime(item["REPORT_TIME"], '%Y年%m月')))
        }
        print(parms)
        result = requests.post(postUrl, data=parms)
        try:
            print(result.json())
        except IOError as e:
            print(e)


def proportionOfImportsAndExportsOfCattleByProvince():
    current_date = datetime.now()
    last_month_date = current_date.replace(day=1) - timedelta(days=1)
    timeStr = last_month_date.strftime("%Y-%m")
    url = "http://ncpscxx.moa.gov.cn/product/common-trade-info/provinces/percentage/count?varietyCode=AL01005&date=" + timeStr + "&code=1&type=3"
    data = requests.get(url)
    list = data.json()["data"]
    for item in list:
        postUrl = "http://39.104.87.35:8081/farmv2/public/index.php/api/farm_produce/percentageCreate"
        parms = {
            "province_name": item["PROVINCE_NAME"],
            "month": timeStr,
            "import_volume": item["IMPORT_VOLUME"],
            "type": "1"
        }
        print(parms)
        result = requests.post(postUrl, data=parms)
        try:
            print(result.json())
        except IOError as e:
            print(e)

    url2 = "http://ncpscxx.moa.gov.cn/product/common-trade-info/provinces/percentage/count?varietyCode=AL01005&date=" + timeStr + "&code=3&type=4"
    data2 = requests.get(url2)
    list2 = data2.json()["data"]
    for item in list2:
        postUrl = "http://39.104.87.35:8081/farmv2/public/index.php/api/farm_produce/percentageCreate"
        parms = {
            "province_name": item["PROVINCE_NAME"],
            "month": timeStr,
            "import_volume": item["EXPORT_VOLUME"],
            "type": "2"
        }
        print(parms)
        result = requests.post(postUrl, data=parms)
        try:
            print(result.json())
        except IOError as e:
            print(e)



def nationalWholesaleBeefPrices():
    current_date = datetime.now()
    yesterday = current_date - timedelta(days=1)
    formatted_date = yesterday.strftime("%Y-%m-%d")
    url = "http://ncpscxx.moa.gov.cn/product/common-price-info/wholesale/price/count?varietyCode=AL01006&date=" + str(formatted_date)
    data = requests.get(url)
    list = data.json()["data"]
    for item in list:
        postUrl = "http://39.104.87.35:8081/farmv2/public/index.php/api/farm_produce/wholesalePriceCreate"
        parms = {
            "same_date": item["REPORT_TIME"],
            "province_name": item["PROVINCE_NAME"],
            "province_code": item["PROVINCE_CODE"],
            "market_name": item["MARKET_NAME"],
            "market_code": item["MARKET_CODE"],
            "longitude": item["LONGITUDE"],
            "latitude": item["LATITUDE"],
            "next_price_market": item["NEXT_PRICE_MARKET"],
            "price_market": item["PRICE_MARKET"],
            "price_difference": item["PRICE_DIFFERENCE"],
            "price_market_rate": item["PRICE_MARKET_RATE"],
        }
        result = requests.post(postUrl, data=parms)
        try:
            print(result.text)
        except IOError as e:
            print(e)


def nationalCattlePriceTrend():
    current_date = datetime.now()
    yesterday = current_date - timedelta(days=1)
    formatted_date = yesterday.strftime("%Y-%m-%d")
    url = "http://ncpscxx.moa.gov.cn/product/common-price-avg/meat/price/compared/count?varietyCode=AL01005010,AL01005008,AL01005009,AL01005007,AL01005006&dataSource=1&queryStartTime="+str(formatted_date) + "&queryEndTime="+str(formatted_date)
    data = requests.get(url)
    list = data.json()["data"]
    for item in list:
        postUrl = "http://39.104.87.35:8081/farmv2/public/index.php/api/farm_produce/comparedPriceCreate"
        parms = {
            "date": time.strftime('%Y-%m-%d', time.struct_time(time.strptime(item["REPORT_TIME"], '%Y年%m月%d日'))),
            "yfn": item["C_AL01005010"] if "C_AL01005010" in item else "null",  # 育肥牛
            "hn": item["C_AL01005008"] if "C_AL01005008" in item else "null",  # 黄牛
            "mn": item["C_AL01005007"] if "C_AL01005007" in item else "null",  # 牦牛
            "sn": item["C_AL01005009"] if "C_AL01005009" in item else "null",  # 水牛
            "rn": item["C_AL01005006"] if "C_AL01005006" in item else "null"  # 肉牛
        }
        print(parms)
        result = requests.post(postUrl, data=parms)
        try:
            print(result.json())
        except IOError as e:
            print(e)


def nationalCattleBreedingCostStructure():
    year = date.today().year - 1
    url = "http://ncpscxx.moa.gov.cn/product/common-cost-info/getPieChart?areaId=101&year=" + str(
        year) + "&varietyCode=AL01005"
    data = requests.get(url)
    print(url)
    costPie = data.json()["data"]["costPie"]
    matterPie = data.json()["data"]["matterPie"]
    manPie = data.json()["data"]["manPie"]
    list = costPie + matterPie + manPie
    for item in list:
        postUrl = "http://39.104.87.35:8081/farmv2/public/index.php/api/farm_produce/commonConstsCreate"
        parms = {
            "year": year,
            "province_name": "全国",
            "type": 1,
            "rate": item["rate"],
            "name": item["name"],
            "value": item["value"]
        }
        print(parms)
        result = requests.post(postUrl, data=parms)
        try:
            print(result.json())
        except IOError as e:
            print(e)


def rankingOfWholesaleBeefPricesInEachProvince():
    current_date = datetime.now()
    yesterday = current_date - timedelta(days=7)
    year, week_number, _ = yesterday.isocalendar()
    url = "http://ncpscxx.moa.gov.cn/product/common-price-info/quote/change/rank/count?varietyCode=AL01006&date=" + str(
        year) + "-" + str(week_number)
    print(url)
    data = requests.get(url)
    fallList = data.json()["data"]["fall"]
    riseList = data.json()["data"]["rise"]
    list = fallList + riseList
    for item in list:
        postUrl = "http://39.104.87.35:8081/farmv2/public/index.php/api/farm_produce/commonChangeRankCreate"
        parms = {
            "province_name": item["PROVINCE_NAME"],
            "province_code": item["PROVINCE_CODE"],
            "price_market_rate": item["PRICE_MARKET_RATE"],
            "price_market": item["PRICE_MARKET"],
            "next_price_market": item["NEXT_PRICE_MARKET"],
            "report_time": item["REPORT_TIME"]
        }
        print(parms)
        result = requests.post(postUrl, data=parms)
        try:
            print(result.json())
        except IOError as e:
            print(e)


def cattleNews():
    url = "http://ncpscxx.moa.gov.cn/product/common-opinion-info/selectListByPage"
    parameters = {"currentPage": 1, "pageSize": 20, "varietyCode": "AL01005", "title": ""}
    data = requests.post(url, json=parameters)
    dataList = data.json()["data"]["records"]
    for item in dataList:
        postUrl = "http://39.104.87.35:8081/farmv2/public/index.php/api/farm_produce/publicSentimentNewsCreate"
        parameter = {
            "title": item["title"],
            "url": item["url"],
            "report_time": item["reportTime"],
            "type": 2
        }
        result = requests.post(postUrl, data=parameter)
        try:
            print(result.json())
        except IOError as e:
            print(e)


def yearlyTask():
    getAllRiceProduction()
    nationalRiceConsumptionStructure()
    trendOfNationalCattleProduction()


def weeklyTask():
    nationalConsumerPriceIndexOfBeef()
    proportionOfImportsAndExportsOfCattleByProvince()
    rankingOfWholesaleBeefPricesInEachProvince()


def dailyTask():
    riceNews()
    rice()
    nationalWholesaleBeefPrices()
    nationalCattlePriceTrend()
    cattleNews()


def runTask():
    print("running...")
    # cattleNews()
    # schedule.every(365).days.do(yearlyTask)
    # schedule.every().week.do(weeklyTask)
    # schedule.every().day.at("09:33").do(dailyTask)

    start_date = datetime(2023, 7, 30)
    end_date = datetime(2023, 8, 17)

    current_date = start_date
    while current_date <= end_date:
        print(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

runTask()

while True:
    schedule.run_pending()
    time.sleep(1)
