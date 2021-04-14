# Coding for Take Impormation In Naver Finance

import datetime
import pandas as pd
import time

def read_naver_toronbang():
    start_time_all = time.time()

    #2021.02.27 goal now is get jongtobang all data

    """
    #  step 1
              - get page 1's date
              - get page's date file on directory
    :return:
    """
    code = '096040'
    # code = '019550'
    import os
    year =  datetime.datetime.strftime(datetime.datetime.today(), '%Y')  # 년 가져오는 코드              #2021.02.21
    month = datetime.datetime.strftime(datetime.datetime.today(), '%m')  # 월 가져오는 코드              #2021.02.21
    day = datetime.datetime.strftime(datetime.datetime.today(), '%d')  # 일 가져오는 코드              #2021.02.21
    pre_year = year
    pre_month = month
    pre_day = day
    path_month = f'C:/Users/user/PycharmProjects/project_FIRE/toronbang/{year}/{month}/{day}'  # 경로 만들기 코드        #2021.02.21
    path_code_df = f'{code}.csv'
    path_df = os.path.join(path_month, path_code_df)
    # print(path_month)
    path = 'jongtobang.csv'

    if os.path.exists(path_month):
        pass
    else:
        os.makedirs(path_month)
        print('check')


    pre_title = [] # before this title check that it has happen before
    import requests
    start_date = None
    except_list = ['\xa0','\xa1','\xa2','\xa3','\xa4','\xa5','\xa6','\xa7','\xa8','\xa9','\xaa','\xab','\xac','\xad','\xae','\xaf',
                   '\xb0','\xb1','\xb2','\xb3','\xb4','\xb5','\xb6','\xb7','\xb8','\xb9','\xba','\xbb','\xbc','\xbd','\xbe','\xbf',
                   '\xc0','\xc1','\xc2','\xc3','\xc4','\xc5','\xc6','\xc7','\xc8','\xc9','\xca','\xcb','\xcc','\xcd','\xce','\xcf',
                   '\xd0','\xd1','\xd2','\xd3','\xd4','\xd5','\xd6','\xd7','\xd8','\xd9','\xda','\xdb','\xdc','\xdd','\xde','\xdf',
                   '\xe0', '\xe1', '\xe2', '\xe3', '\xe4', '\xe5', '\xe6', '\xe7', '\xe8', '\xe9', '\xea', '\xeb','\xec', '\xed', '\xee', '\xef',
                   '\xf0','\xf1','\xf2','\xf3','\xf4','\xf5','\xf6','\xf7','\xf8','\xf9','\xfa','\xfb','\xfc','\xfd','\xfe','\xff',


                   '\xe1','\xed','\xfd',
                   '\xe0','\xe1','\xe2','\xe3','\xe4','\xe5','\xe6','\xe7','\xe8','\xe9',
                   '\u2000','\u2001','\u2002','\u2003','\u2004','\u2005','\u2006','\u2007','\u2008','\u2009',
                   '\u2010','\u2011','\u2012','\u2013','\u2014','\u2015','\u2016','\u2017','\u2018','\u2019',
                   '\u2022','\u2023','\u2024','\u2025','\u2026',
                   '\u0160','\u0161'
                   ]
    # except_list =[]
    count = 0 # count 돌리기
    # count = 646
    start = count
    while 1:
        start_time = time.time()

        # 수정 Test 진행

        #
        year_list = []
        month_list = []
        day = []
        time_list = []
        insight = []
        title = []
        source = []



        page = count +1
        print(page)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}
        url_main = f'https://finance.naver.com/item/board.nhn?code={code}&page={page}'
        url_base = 'https://finance.naver.com'
        # url_main = f'https://finance.naver.com/item/main.nhn?code=038880'
        res_main = requests.get(url_main, headers=headers)
        # res_main.encoding = 'ms949'  # utf-8 : 한글 깨짐 현상 생김  # utf-8-sig # euc-kr # cp949 다안됨 #ms949도 안됨 ###적용을 안시킴;;;; ㅎㅎ
        res_main.status_code

        from bs4 import BeautifulSoup
        soap_main = BeautifulSoup(res_main.text, 'lxml')  ##웹페이지 crawling해옴
        table_all = soap_main.find_all('table', class_='type2')  ###웹페이지 종토방 불러오기
        day_all = soap_main.find_all('span', class_='tah p10 gray03')  ###웹페이지 종토방 불러오기
        title_all = soap_main.find_all('td', class_='title')


        # print(title_all)
        # title_all = table_all.find(class_='title')

        # href_all = title_all[0].find("a")["href"]
        # print(href_all)
        # print(url_main)
        # print(soap_main)
        # print(table_all)
        # print(day_all)
        # print(len(day_all))
        # print(title_all[0].get_text())

        # page 추가 시키면 됨

        url_main = f'https://finance.naver.com/item/board.nhn?code={code}&page={page}'

        # print(len(title_all))
        # print(len(day_all))

        # title 분리하는 방법
        for i in range(len(title_all)):
            temp = title_all[i].get_text()
            temp = temp.split('\n')[1]
            title.append(temp)

            # 해당 제목에 대한 URL 가져오기
            href = title_all[i].find("a")["href"] # 링크 가져오기
            # print(href)
            url_new = url_base + href # 내용 URL
            # print(url_new)
            res_deep = requests.get(url_new, headers=headers)
            soap_deep = BeautifulSoup(res_deep.text, 'lxml')  ##웹페이지 crawling해옴
            source_deep = soap_deep.find(class_='view_se').get_text()  ###웹페이지 종토방 불러오기 내용 불러오기
            source_deep = source_deep.replace('\r','___')

            # 내용 불러온거에 쓸데 없는 내용 제거
            # source_deep = source_deep.replace('\xa0', '_xa0_')
            # source_deep = source_deep.replace('\xa0', ' ') # 이게 맞는거 같아
            # source_deep = source_deep.replace('\xa9', ' ') # 이게 맞는거 같아
            # source_deep = source_deep.replace('\u2013', ' ') # 이게 맞는거 같아
            # source_deep = source_deep.replace('\u2014', ' ') # 이게 맞는거 같아
            # source_deep = source_deep.replace('\u2015', ' ') # 이게 맞는거 같아
            # source_deep = source_deep.replace('\u2016 ', ' ')  # 이게 맞는거 같아
            # source_deep = source_deep.replace('\xf3 ', ' ')  # 이게 맞는거 같아

            for list_i in except_list:
                source_deep = source_deep.replace(list_i, ' ') # 이게 맞는거 같아
                # print('replace', list_i,' :to empty space')

            # 내용 제거 끝
            source.append(source_deep)




        print(title[-20:])

        # day 분리하는 방법
        for i in range(len(day_all)):
            if i % 2 == 0:
                slicing_date = day_all[i].get_text()
                # day.append(slicing_date)
                slicing_year = slicing_date[:4]
                year_list.append(slicing_year)
                # print(slicing_year)
                slicing_month = slicing_date[5:7]
                month_list.append(slicing_month)
                # print(slicing_month)
                slicing_day = slicing_date[8:10]
                day.append(slicing_day)

                slicing_time = slicing_date[11:]
                time_list.append(slicing_time)
                # print(time_list)

                # print(slicing_day)

            elif i % 2 == 1:
                insight.append(day_all[i].get_text())

        print(day[-20:])
        """
        date file
        """
        if len(title_all) <20:
            break

        # if slicing_month != pre_month:


        #여기서 날짜로 잘라
        if count == start:
            df = pd.DataFrame({'year': year_list,'month':month_list,'day': day,'time':time_list, 'title': title, 'source': source})
            pre_month = slicing_month
            pre_day = slicing_day
            pre_year = slicing_year
        else :
            _df = pd.DataFrame({'year': year_list,'month':month_list,'day': day,'time':time_list, 'title': title, 'source': source})

            if pre_day == slicing_day:
                df = pd.concat([df,_df])
                df.to_csv(path_df, encoding='CP949', index=False)
            else:
                print(df)
                df_now = df[pre_day == df['day']]
                print(df_now)
                df_now.to_csv(path_df, encoding='CP949', index=False)

                year = slicing_year
                month = slicing_month
                day = slicing_day

                path_month = f'C:/Users/user/PycharmProjects/project_FIRE/toronbang/{year}/{month}/{day}'  # 경로 만들기 코드        #2021.02.21

                if os.path.exists(path_month):
                    pass
                else:
                    os.makedirs(path_month)
                    print('check')

                path_code_df = f'{code}.csv'
                path_df = os.path.join(path_month, path_code_df)

                if os.path.exists(path_df):
                    df_last = pd.read_csv(path_df, encoding= 'CP949')
                    print(df_last)
                    break
                else:
                    pass

                df = df[pre_day != df['day']]
                pre_day=day
                pre_month = month
                pre_year = year




            #
            # path_month = f'C:/Users/user/PycharmProjects/project_FIRE/toronbang/{year}/{month}'  # 경로 만들기 코드        #2021.02.21
            # path_code_df = f'{code}.csv'
            # path_df = os.path.join(path_month, path_code_df)
            #
            # if os.path.exists(path_month):
            #     pass
            # else:
            #     os.makedirs(path_month)
            #     print('check')
            #
            # df.to_csv(path_df, encoding='CP949', index=False)
            # df.to_csv(path_df, encoding='UTF-8', index=False)





        pre_year = slicing_year
        pre_month = slicing_month
        count = count + 1
        Run_Time = time.time() - start_time
        print(Run_Time)


    print(len(day))
    print(len(insight))
    print(day)
    print(insight)
    print(source)

    print(df)
    Run_Time = time.time() - start_time_all
    print(Run_Time)

read_naver_toronbang()
