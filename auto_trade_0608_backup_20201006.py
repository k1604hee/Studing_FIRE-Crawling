import sys
from PyQt5.QtWidgets import *
import Kiwoom
import time
import pandas as pd
import datetime
import numpy as np
import os
import matplotlib.pyplot as plt
import mpl_finance
import matplotlib.ticker as ticker

MARKET_KOSPI = 0
MARKET_KOSDAQ = 10

"""
seq_00      :   PyMon 초기 셋팅
seq_01      :   kiwoom에서 코스피, 코스닥 코드 받아오기
seq_02      :   seq_01에서 받아온 주식 코드를 통해 건강한 코드를 걸러 냄
        01  :   이전에 거른 healthy code가 있는 지 확인하고 없으면 healthy code를 걸러냄
        02  :
"""


class auto_trade:
    ### 이니시
    ### seq_00
    def __init__(self):
        super().__init__()
        # self._create_auto_trade_instance()
        self.kiwoom = Kiwoom.Kiwoom()
        self.kiwoom.comm_connect()

        # ### 경로 지정
        self.path_file_dir = 'Open_API/Event_Log/{today}'.format(
            today=datetime.datetime.strftime(datetime.datetime.today(), '%Y.%m.%d'))
        self.path_health_kospi_code = 'health_kospi_code_list_{today}.csv'.format(
            today=datetime.datetime.strftime(datetime.datetime.today(), '%Y.%m.%d'))
        self.path_health_kosdaq_code = 'health_kosdaq_code_list_{today}.csv'.format(
            today=datetime.datetime.strftime(datetime.datetime.today(), '%Y.%m.%d'))
        self.path_triger_by_volume = 'triger_volume/{section}_{today}.csv'.format(section='none',
                                                                                  today=datetime.datetime.strftime(
                                                                                      datetime.datetime.today(),
                                                                                      '%Y.%m.%d.%H.%M.%S'))
        self.path_file_dir = os.path.join('C:/Users/user/PycharmProjects/project_FIRE', self.path_file_dir)
        self.path_health_kospi_code = os.path.join(self.path_file_dir, self.path_health_kospi_code)
        self.path_health_kosdaq_code = os.path.join(self.path_file_dir, self.path_health_kosdaq_code)
        self.path_triger_by_volume = os.path.join(self.path_file_dir, self.path_triger_by_volume)
        self.path_triger_by_volume_summary = self.path_triger_by_volume
        self.trade_count = 0

        path_file_dir = 'Open_API/Event_Log/{today}'.format(
            today=datetime.datetime.strftime(datetime.datetime.today(), '%Y.%m.%d'))
        path_file_dir = os.path.join('C:/Users/user/PycharmProjects/project_FIRE', path_file_dir)
        if not os.path.exists(path_file_dir):
            os.makedirs(path_file_dir)
        self.sell_list = os.path.join(path_file_dir, 'Sell_List_{today}.txt'.format(
            today=datetime.datetime.strftime(datetime.datetime.today(), '%Y%m%d')))
        self.buy_list = os.path.join(path_file_dir, 'Buy_List_{today}.txt'.format(
            today=datetime.datetime.strftime(datetime.datetime.today(), '%Y%m%d')))

        ### triger volume 파일 저장 소 만들기
        path_triger_volume_file = os.path.join(self.path_file_dir, 'triger_volume')
        if not os.path.exists(path_triger_volume_file):
            os.makedirs(path_triger_volume_file)

        self.get_code_list()
        self.health_kospi_codes = []  ### 건정성 평가한 code들만 따로 분리하여 저장
        self.health_kosdaq_codes = []  ### 위와 같음

        start_time = time.time()
        self.health_code_kosdaq = []
        self.list_lbb_high = []
        self.list_score_volin = []

    def _create_auto_trade_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    ### seq_01
    def get_code_list(self):
        self.kospi_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSPI)
        self.df_health_kospi_code = self.make_code_df(self.kospi_codes)
        print(self.df_health_kospi_code)

        self.kosdaq_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSDAQ)
        self.df_health_kosdaq_code = self.make_code_df(self.kosdaq_codes)

        print(self.df_health_kosdaq_code)

    def test(self):
        print("Test success")

    ### seq_01_01
    ### df에 Status 추가
    def make_code_df(self, code_list):
        status = []
        for i in code_list:
            status.append(False)
        dic_code = {'code': code_list, 'state': status}
        return pd.DataFrame(dic_code)

    def insert_status(self, dataframe, String_what='status', filling=False):
        status = []
        for i in dataframe['code']:
            status.append(filling)
        dataframe[String_what] = status
        return dataframe

    ###
    ### 삼성전자 코드를 통해 기업실적 분석 table을 가져와 표를 한줄로 변경하는 Index를 만들어서 code 분석에 붙인다
    def get_frame_samsung(self):
        code = '005930'  # 삼성 코드
        df = self.get_healthy_code_list(code)
        # print(df)
        # print(len(df))
        # print(len(df.columns))
        columns_name = []
        index_name = []
        for i in df.columns:
            columns_name.append(i)
        for i in df[df.columns[0]]:
            index_name.append(i)
        columns_name.pop(0)
        index_name.pop(0)
        index_name.pop(0)
        self.health_index = []
        for a in index_name:
            for i in columns_name:
                str_temp = i + "*" + a
                self.health_index.append(str_temp)
            if i == 'EPS(원)':
                break

        # print(columns_name)
        # print(index_name)
        # print(df.columns)
        # print(self.health_index)

        ### seq_02_02

    def save_health_code_csv(self, dataframe, path):
        dataframe.to_csv(path, index=False, encoding='CP949')
        function_Event_Log(Time=datetime.datetime.now(), function="save_health_code_csv()",
                           Run_Time=0, State=0, Log=f"{path} has saved",
                           code="")

    def judge_healthy_code_structure_build(self, dataframe, path):
        start_time_ghcl = time.time()
        function_Event_Log(Time=datetime.datetime.now(), function="judge_healthy_code_structure_build()", Run_Time=0,
                           State=0,
                           Log="judge_healthy_code_structure_build() start", code=False)
        # earn_money_time = ["2017.12","2018.12","2019.12","2020.12(E)","2019.03","2019.06","2019.09","2020.03","2020.06(E)"]     #분기마다 바꿔줘야함
        if os.path.exists(path):
            df_health_code = self.judge_healthy_code_detail(path)
            code_val = []
            for i, row in df_health_code.iterrows():
                val = str(df_health_code.loc[i]['code'])
                ###code를 크롤링 해오면서 생기는 갯수 달라짐(숫자로 인식해서 앞의 0이 없어짐)을 다시 문자열로 바꿔서 6자리 code로 변환하는 과정
                while len(val) != 6:
                    val = '0{val}'.format(val=val)
                ###6자리가 된 code를 code_val이라는 문자열에 추가(배열.append(value)가 추가하는 코드)
                code_val.append(val)

            ###code에 기준 데이터와 치환
            # print(code_val)
            df_health_code['code'] = code_val

            return df_health_code
        else:
            self.insert_status(dataframe, 'profit_status')
            self.get_frame_samsung()
            self.insert_status(dataframe=dataframe, String_what='주식수', filling=False)
            list_code_by_Naver = ['주식수', '전일', '고가', '거래량', '종가', '저가', '거래대금', "52주 고가", "52주 저가"]
            for i in list_code_by_Naver:
                self.insert_status(dataframe=dataframe, String_what=i, filling=False)
            # self.insert_status(dataframe=dataframe, String_what='전일', filling=False)
            # self.insert_status(dataframe=dataframe, String_what='고가', filling=False)
            # self.insert_status(dataframe=dataframe, String_what='거래량', filling=False)
            # self.insert_status(dataframe=dataframe, String_what='종가', filling=False)
            # self.insert_status(dataframe=dataframe, String_what='저가', filling=False)
            # self.insert_status(dataframe=dataframe, String_what='거래대금', filling=False)
            for i in self.health_index:
                self.insert_status(dataframe, i, 0)
            # print(self.df_health_kospi_code)
            Temp_code_list = dataframe['code']
            for ii, code in enumerate(Temp_code_list):
                ### 네이버에서 주식수,전일 고가 거래량 종가 저가 거래대금 52주 고가 저가 가져오기
                for aa, state in enumerate(self.get_healthy_code_by_Naver(code)):
                    dataframe.loc[ii, list_code_by_Naver[aa]] = state

                ### 실적 가져오기
                df = self.get_healthy_code_list(code)
                # print(dataframe[list_code_status])

                if df is False:
                    dataframe.loc[ii, 'profit_status'] = False
                    print(code, " 안돼  ")
                    continue
                else:
                    dataframe.loc[ii, 'profit_status'] = True
                    pass
                df = self.get_healthy_code_list(code)
                df = df.fillna(0)
                # print(df)
                columns_name = []
                index_name = []
                for i in df.columns:
                    columns_name.append(i)
                for i in df[df.columns[0]]:
                    index_name.append(i)
                columns_name.pop(0)
                index_name.pop(0)
                index_name.pop(0)
                self.health_index = []

                ### Naver 기업 실적 분석 에서 추출한 data를 DataFrame에 Column 추가한다
                for row, a in enumerate(index_name):
                    for i in columns_name:

                        str_temp = i + "*" + a
                        # print(str_temp)
                        if df.loc[row + 2, i] == '-':
                            dataframe.loc[ii, str_temp] = 0
                        else:
                            dataframe.loc[ii, str_temp] = float(df.loc[row + 2, i])
                print(dataframe)
            self.save_health_code_csv(dataframe, path)
            print(dataframe)
            function_Event_Log(Time=datetime.datetime.now(), function="judge_healthy_code_structure_build()",
                               Run_Time=time.time() - start_time_ghcl, State=0,
                               Log="judge_healthy_code_structure_build() end",
                               code=False)
            return self.judge_healthy_code_detail(path)

    ###기업실적분석 Raw Data로 분석
    def judge_healthy_code_detail(self, path):
        df_health_code = pd.read_csv(path, encoding='CP949')
        df_health_code = df_health_code.fillna(0)
        columns_name = []
        for i in df_health_code.columns:
            columns_name.append(i)
        sell = ["*매출액", "*영업이익", "*부채비율"]
        period = ["연간", "분기"]
        for a in sell:
            for b in period:
                sell_list = []
                for i in columns_name:
                    if a in i and b in i:
                        sell_list.append(i)
                temp_df = df_health_code[sell_list].sum(axis=1)
                if a != "*부채비율":
                    print(temp_df)
                    df_health_code[b + a] = temp_df > 0
                else:
                    df_health_code[b + a] = temp_df < 500
        list_ab = []
        for a in sell:
            for b in period:
                list_ab.append(b + a)
        print(list_ab)
        print(df_health_code[list_ab].sum(axis=1))
        df_health_code["profit_status"] = df_health_code[list_ab].sum(axis=1)
        df_health_code["profit_status"] = df_health_code["profit_status"] > 5
        self.save_health_code_csv(df_health_code, path)
        return df_health_code

    ### seq_02_01
    """
    여기서 기존 csv 파일이 있는지 없는 지 Check 하고 Code를 6자리로 변경해서 내준다.
    """

    def chect_health_code_list(self, path):
        if os.path.exists(path):
            df_health_code = pd.read_csv(path, encoding='CP949')
        else:
            return self.get_healthy_code_list_all()
        code_val = []
        for i, row in df_health_code.iterrows():
            val = str(df_health_code.loc[i]['code'])
            ###code를 크롤링 해오면서 생기는 갯수 달라짐(숫자로 인식해서 앞의 0이 없어짐)을 다시 문자열로 바꿔서 6자리 code로 변환하는 과정
            while len(val) != 6:
                val = '0{val}'.format(val=val)
            ###6자리가 된 code를 code_val이라는 문자열에 추가(배열.append(value)가 추가하는 코드)
            code_val.append(val)

        ###code에 기준 데이터와 치환
        # print(code_val)
        df_health_code['code'] = code_val

        return df_health_code

    ### seq_02_03
    def get_healthy_code_list(self, code="000000"):
        start_time_ghcl = time.time()
        # function_Event_Log(Time=datetime.datetime.now(), function="get_healty_code_list()", Run_Time=0, State=0,
        #                    Log=f"{code}get_healty_code_list() start", code=code)
        import requests
        from bs4 import BeautifulSoup
        url_main = f'http://finance.naver.com/item/main.nhn?code={code}'
        res_main = requests.get(url_main)
        res_main.encoding = 'ms949'  # utf-8 : 한글 깨짐 현상 생김  # utf-8-sig # euc-kr # cp949 다안됨 #ms949도 안됨 ###적용을 안시킴;;;; ㅎㅎ
        res_main.status_code

        from bs4 import BeautifulSoup
        soap_main = BeautifulSoup(res_main.text, 'lxml')
        # function_Event_Log(Time=datetime.datetime.now(), function="get_healty_code_list()",
        #                    Run_Time=time.time() - start_time_ghcl, State=0, Log=f"{code}get_healty_code_list() end",
        #                    code=code)
        try:
            df = pd.read_html(str(soap_main.find("table", class_="tb_type1 tb_num tb_type1_ifrs")), header=0)[0]
            # print(df)
        except ValueError:
            return False
        else:
            return df

    ### Naver 금융에서 가져오는 데이터 종합 List로 return 해주는 함수
    def get_healthy_code_by_Naver(self, code="000000"):
        ##Log 남기는 함수 : 시작함수  용량 문제로 주석처리
        # function_Event_Log(Time=datetime.datetime.now(), function="get_healty_code_list()", Run_Time=0, State=0,
        #                    Log=f"{code}get_healty_code_list() start", code=code)
        import requests
        url_main = f'http://finance.naver.com/item/main.nhn?code={code}'
        res_main = requests.get(url_main)
        res_main.encoding = 'ms949'  # utf-8 : 한글 깨짐 현상 생김  # utf-8-sig # euc-kr # cp949 다안됨 #ms949도 안됨 ###적용을 안시킴;;;; ㅎㅎ
        res_main.status_code

        from bs4 import BeautifulSoup
        soap_main = BeautifulSoup(res_main.text, 'lxml')  ##웹페이지 crawling해옴
        table_all = soap_main.find_all("table")  ###웹페이지에서 모든 Table에 대해 가져옴
        ###Log 남기는 함수: 끝함수 용량문제로 주석 처리
        # function_Event_Log(Time=datetime.datetime.now(), function="get_healthy_code_sigachong_summary()",
        #                    Run_Time=time.time() - start_time_ghcl, State=0, Log=f"{code}get_healthy_code_sigachong_summary() end",
        #                    code=code)
        try:
            list_data = []
            try:
                ###amount 가져오기
                df = pd.read_html(str(table_all[5]), header=0)[0]
            except ValueError:
                list_data.append(False)
                function_Event_Log(Time=datetime.datetime.now(), function="get_healthy_code_by_Naver()", Run_Time=0,
                                   State=0,
                                   Log=f"{code}get_healthy_code_by_Naver() 주식수가져오기 Value Error", code=code)
            except AttributeError:
                list_data.append(False)
                function_Event_Log(Time=datetime.datetime.now(), function="get_healthy_code_by_Naver()", Run_Time=0,
                                   State=0,
                                   Log=f"{code}get_healthy_code_by_Naver() 주식수 가져오기 AttributeError", code=code)
            else:
                list_data.append(df.loc[1][df.columns[1]])
            try:
                #### 전일 고가 거래량 종가 저가 거래대금 에 대해서 Naver 창에서 가져옴
                for i in range(0, 7):
                    list_data.append((table_all[0].find_all("span", class_='blind')[i].get_text()))
                list_data.pop(2)
            except ValueError:
                list_data.append(False)
                function_Event_Log(Time=datetime.datetime.now(), function="get_healthy_code_by_Naver()", Run_Time=0,
                                   State=0,
                                   Log=f"{code}get_healthy_code_by_Naver() 거래대금 가져오기 Value Error", code=code)
            except AttributeError:
                list_data.append(False)
                function_Event_Log(Time=datetime.datetime.now(), function="get_healthy_code_by_Naver()", Run_Time=0,
                                   State=0,
                                   Log=f"{code}get_healthy_code_by_Naver() 거래대금 가져오기 AttributeError", code=code)

            try:
                ###52주 고가 가져오기
                for i in range(2, 4):
                    list_data.append(soap_main.find("table", class_="rwidth").find_all("em")[i].get_text())
            except ValueError:
                list_data.append(False)
                function_Event_Log(Time=datetime.datetime.now(), function="get_healthy_code_by_Naver()", Run_Time=0,
                                   State=0,
                                   Log=f"{code}get_healthy_code_by_Naver() 52주 고가 가져오기 Value Error", code=code)
            except AttributeError:
                list_data.append(False)
                function_Event_Log(Time=datetime.datetime.now(), function="get_healthy_code_by_Naver()", Run_Time=0,
                                   State=0,
                                   Log=f"{code}get_healthy_code_by_Naver() 52주 고가 가져오기 AttributeError", code=code)
            except IndexError:
                list_data.append(False)
                function_Event_Log(Time=datetime.datetime.now(), function="get_healthy_code_by_Naver()", Run_Time=0,
                                   State=0,
                                   Log=f"{code}get_healthy_code_by_Naver() 52주 고가 가져오기 Index Error", code=code)
        except ValueError:
            return False
        except AttributeError:
            return False
        else:
            return list_data

    def check_health_code(self, df):
        list_true = []
        for i, row in df.iterrows():
            print(df.loc[i]['state'])
            if df.loc[i]['state']:
                list_true.append(df.loc[i]['code'])
        return list_true

    ##########여기까지 코드 불러오는 곳

    def bb(self, x, w=1.9, k=2, df=np.nan, code='000000'):
        """
        Calculate Bollinger Bands
        ubb = MA_w(x) + k * sd(x)
        mbb = MA_w(x)
        lbb = MA_w(x) - k * sd(x)
        :param x:
        :return: (ubb, mbb, lbb)
        """

        x = pd.Series(x)
        mbb = x.rolling(w).mean()
        ubb = mbb + k * x.rolling(w).std()
        lbb = mbb - k * x.rolling(w).std()

        high = df['close']
        # print(ubb[-1])
        # print(high[-1])
        # print(lbb[-1])
        score = lbb[-1] - high[-1]
        if score >= 0:
            score = 100
        else:
            # score = score/mbb[-1] *100
            score = format(0 - (score / mbb[-1] * 100), ".2f")
        self.list_score_volin.append(score)
        print(format((mbb[-1] - lbb[-1]) / mbb[-1] * 100, ".2f"))
        print(score)
        if (lbb[-1] > high[-1]):
            self.list_lbb_high.append(code)
        return score

    def get_ohlcv(self, code, count, start):
        self.kiwoom.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.set_input_value("기준일자", start)
        self.kiwoom.set_input_value("수정주가구분", 1)
        ### comm_rq_data 메서드를 통해 TR을 한번 요청하면 과거 900 일에 대한 데이터를 가져올 수 있다.
        self.kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")

        # 0.2초로 하면 99에서 과도 조회로 멈춤
        # 0.5,0.7,1,1초로 하면 999개에서 조회 과도로 멈춤

        time_gap = 0.5
        time.sleep(time_gap)

        df = pd.DataFrame(self.kiwoom.ohlcv, columns=['open', 'high', 'low', 'close', 'volume'],
                          index=self.kiwoom.ohlcv['date'])
        # print(df.index)
        df = df.sort_index(ascending=True)
        # print(df)

        # print(df)

        # print(df['rateCMA5C'],code)
        return df

    def check_speedy_rising_volume(self, code, count):
        today = datetime.datetime.today().strftime("%Y%m%d")
        df = self.get_ohlcv(code, count, today)
        volumes = df['volume']
        self.bb(df['close'], w=20, k=1.5, df=df, code=code)
        if len(volumes) < 21:
            return False

        sum_vol20 = 0
        today_vol = 0

        for i, vol in enumerate(volumes):
            if i == 0:
                today_vol = vol
            elif 1 <= i <= 20:
                sum_vol20 += vol
            else:
                break

        avg_vol20 = sum_vol20 / 20
        if today_vol > avg_vol20 * 10:
            return True

    def check_balance(self, step):
        self.kiwoom.reset_opw00018_output()
        account_number = self.kiwoom.get_login_info("ACCNO")
        account_number = account_number.split(';')[1]

        # print(account_number)
        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "2000")

        while self.kiwoom.remained_data:
            time.sleep(0.2)
            self.kiwoom.set_input_value("계좌번호", account_number)
            self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 2, "2000")

        # opw00001
        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00001_req", "opw00001", 0, "2000")

        # for i in range(1, 6):
        # print(self.kiwoom.opw00018_output['single'][i - 1])

        # Item list
        item_count = len(self.kiwoom.opw00018_output['multi'])

        for j in range(item_count):
            row = self.kiwoom.opw00018_output['multi'][j]
            print(row)
            self.Test_Log(datetime.datetime.now(), row)

            # if j==1:
            #     print(float(row[6]))
            #     if float(row[6]) > 2.5:
            #         self.trade_stocks_sell()

        # self.kiwoom.set_input_value("시장구분", "000")
        # self.kiwoom.set_input_value("정렬구분", 1)
        # self.kiwoom.set_input_value("시간구분", 1)
        # self.kiwoom.set_input_value("거래량구분", 5)
        # self.kiwoom.set_input_value("시간", 1)
        #
        # self.kiwoom.set_input_value("종목조건", 1)
        # self.kiwoom.set_input_value("가격구분", 0)
        # self.kiwoom.comm_rq_data("OPT10023_req", "OPT10023", 0, "0101")
        #

        step_divide = 2
        if step % step_divide == 0:
            self.kiwoom.set_input_value("시장구분", "001")
            self.path_triger_by_volume = 'triger_volume/{section}_{today}.csv'.format(section='kospi',
                                                                                      today=datetime.datetime.strftime(
                                                                                          datetime.datetime.today(),
                                                                                          '%Y.%m.%d.%H.%M.%S'))
            self.path_triger_by_volume_summary = 'triger_volume/{section}_summary.csv'.format(section='kospi')
        elif step % step_divide == 1:
            self.kiwoom.set_input_value("시장구분", "101")
            self.path_triger_by_volume = 'triger_volume/{section}_{today}.csv'.format(section='kosdaq',
                                                                                      today=datetime.datetime.strftime(
                                                                                          datetime.datetime.today(),
                                                                                          '%Y.%m.%d.%H.%M.%S'))
            self.path_triger_by_volume_summary = 'triger_volume/{section}_summary.csv'.format(section='kosdaq')
        if step % step_divide < 2:
            self.path_triger_by_volume = os.path.join(self.path_file_dir, self.path_triger_by_volume)
            self.path_triger_by_volume_summary = os.path.join(self.path_file_dir, self.path_triger_by_volume_summary)
            self.kiwoom.set_input_value("정렬구분", 1)
            self.kiwoom.set_input_value("시간구분", 1)
            self.kiwoom.set_input_value("거래량구분", 5)
            self.kiwoom.set_input_value("시간", 1)

            self.kiwoom.set_input_value("종목조건", 1)
            self.kiwoom.set_input_value("가격구분", 8)
            self.kiwoom.triger_volume = {'name': [], 'code': [], 'price_now': [], 'up_down': [], 'pre_volume': [],
                                         'volume': [], 'up_mount': [], 'up_rate': []}
            self.kiwoom.comm_rq_data("OPT10023_req", "OPT10023", 0, "0101")
            df = pd.DataFrame(self.kiwoom.triger_volume,
                              columns=['name', 'code', 'price_now', 'up_down', 'pre_volume', 'volume', 'up_mount',
                                       'up_rate'],
                              index=self.kiwoom.triger_volume['name'])
            # print(self.path_triger_by_volume)
            df.to_csv(self.path_triger_by_volume, index=False, encoding='CP949')
            # print(df)

    def trade_stocks_sell(self):
        hoga_lookup = {'지정가': "00", '시장가': "03"}

        f = open(self.sell_list, 'rt', encoding='CP949')
        sell_list = f.readlines()
        f.close()

        account = self.kiwoom.get_login_info("ACCNO")
        account = account.split(';')[1]

        # sell list
        for row_data in sell_list:
            split_row_data = row_data.split(';')
            hoga = split_row_data[2]
            code = split_row_data[1]
            num = split_row_data[3]
            price = split_row_data[4]

            if split_row_data[-1].rstrip() == '매도전':
                self.kiwoom.send_order("send_order_req", "0101", account, 2, code, num, price,
                                       hoga_lookup[hoga], "")

        # sell list
        for i, row_data in enumerate(sell_list):
            sell_list[i] = sell_list[i].replace("매도전", "주문완료")

        # file update
        f = open(self.sell_list, 'wt')
        for row_data in sell_list:
            f.write(row_data)
        f.close()
        function_Event_Log(Time=datetime.datetime.now(), function="trade_stocks_sell()", Run_Time=0,
                           State=0,
                           Log=f"{code}trade_stocks_sell() 매도", code=code)

    def trade_stocks_sell_auto(self, list):  ###20200921 수정
        print('Auto_sell')
        hoga_lookup = {'지정가': "00", '시장가': "03"}

        account = self.kiwoom.get_login_info("ACCNO")
        account = account.split(';')[1]

        # sell list
        hoga = "시장가"
        # print(list)
        code = list[0]
        code = code[1:]
        # print(code)
        num = list[2]
        price = list[5]
        # print( "0101", account, 2, code, num, price,hoga_lookup[hoga], "")
        self.kiwoom.send_order("send_order_req", "0101", account, 2, code, num, price,
                               hoga_lookup[hoga], "")  ### 중간에 숫자 1: 매수 2: 매도

        # sell list

        # file update
        function_Event_Log(Time=datetime.datetime.now(), function="trade_stocks_sell_auto()", Run_Time=0,
                           State=0,
                           Log=f"{code}trade_stocks_sell() 매도", code=code)

    ###20200909

    def choice_trade_method(self, list, method=0):
        if method == 0:
            self.trade_half(list)

    ###자동 샐링 2% 이상 수익발생시 반만 따가기

    def trade_half(self, list):
        profit = list[6] > 2
        self.trade_stocks_sell_auto(list)

    ###자동 샐링 2% 이상 수익발생시 반만 따가기 끝

    def trade_stocks_buy(self):

        hoga_lookup = {'지정가': "00", '시장가': "03"}

        f = open(self.buy_list, 'rt', encoding='CP949')
        buy_list = f.readlines()
        print(buy_list)
        f.close()

        account = self.kiwoom.get_login_info("ACCNO")
        account = account.split(';')[1]
        # buy list
        for row_data in buy_list:
            split_row_data = row_data.split(';')
            hoga = split_row_data[2]
            code = split_row_data[1]
            num = split_row_data[3]
            price = split_row_data[4]

            if split_row_data[-1].rstrip() == '매수전':
                self.kiwoom.send_order("send_order_req", "0101", account, 1, code, num, price,
                                       hoga_lookup[hoga], "")

        # buy list
        for i, row_data in enumerate(buy_list):
            buy_list[i] = buy_list[i].replace("매수전", "주문완료")

        # file update
        f = open(self.buy_list, 'wt')
        for row_data in buy_list:
            f.write(row_data)
        f.close()
        function_Event_Log(Time=datetime.datetime.now(), function="trade_stocks_buy()", Run_Time=0,
                           State=0,
                           Log=f"{code}trade_stocks_buy() 매수", code=code)

    def time_gap(self, gap):
        start_time = datetime.datetime.now()
        while datetime.datetime.now() - start_time < datetime.timedelta(seconds=gap):
            pass
        print(start_time, datetime.datetime.now())

        return True

    def run(self):

        # self.trade_stocks_buy()
        count_step = 0
        total_count = 0
        while (self.time_gap(10)):

            time_jang_end_hour = int(datetime.datetime.strftime(datetime.datetime.now(), '%H'))
            time_jang_end_minute = int(datetime.datetime.strftime(datetime.datetime.now(), '%M'))
            print(time_jang_end_hour, time_jang_end_minute)
            print(time_jang_end_hour + time_jang_end_minute)
            if time_jang_end_hour <= 15 & time_jang_end_minute <= 20:
                print('ok')
                pass
            elif time_jang_end_hour >= 15:
                if time_jang_end_minute >= 20:
                    function_Event_Log(datetime.datetime.now(), "auto_trade Time Out",
                                       format(time.time() - start_time, ".2f"),
                                       0, "auto_trade Program Time OUT")
                    print('no')
                    quit()
                    return 0
                else:

                    print('ok')
                    pass

            print(datetime.datetime.now())
            self.check_balance(count_step)
            count_step = count_step + 1
            total_count = total_count + 1

            if total_count > 499:
                self.kiwoom.comm_connect()
                total_count = 0
                Trading_Event_Log(Time=datetime.datetime.now(), function="run() re connect to server", Run_Time=0,
                                  State=0,
                                  Log=log, code=False)
                time.sleep(10)

            log = "total count" + str(total_count)
            Trading_Event_Log(Time=datetime.datetime.now(), function="run()", Run_Time=0,
                              State=0,
                              Log=log, code=False)
            if count_step == 60:
                count_step = 0
                Trading_Event_Log(Time=datetime.datetime.now(), function="run()", Run_Time=0,
                                  State=0,
                                  Log="Run", code=False)

    def Test_Log(self, Time, list):
        """
        :param Time: Log 함수 호출 시간
        :param function: 함수 이름
        :param Run_Time: 함수 구동 시간
        :param State: 0--> Start, 1 --> End
        :param Log: 남길 내용
        :return:
        """
        import os
        import datetime

        # path_file_dir = 'Open_API/Event_Log/{today}'.format(today=datetime.datetime.strftime(datetime.datetime.today(), '%Y.%m.%d'))
        # path_file_dir = os.path.join('C:/Users/user/PycharmProjects/project_FIRE', path_file_dir)
        path_file_dir = 'C:/Users/user/PycharmProjects/project_FIRE/Trade'

        buy = 0
        son = 0
        sell = 1
        if not os.path.exists(path_file_dir):
            os.makedirs(path_file_dir)
        path_Event = os.path.join(path_file_dir, 'Trade_{code}.csv'.format(code=list[1]))
        if os.path.exists(path_Event):
            E_df = pd.read_csv(path_Event, encoding='CP949')
            # print(E_df['최고수익률'][0])
            if float(E_df['최고수익률'][0]) < float(list[6]):
                good = list[6]
                pass
            else:
                good = float(E_df['최고수익률'][0])
                buy = E_df['매수코드'][0]
                son = E_df['손절코드'][0]
                sell = E_df['매도코드'][0]
        else:
            Event_Frame = {'Time': [], '종목명': [], '보유량': [], '매입가': [], '현재가': [], '평가손익': [], '수익률': [], '최고수익률': [],
                           '매수코드': [], '손절코드': [], '매도코드': []}
            E_df = pd.DataFrame(Event_Frame)
            E_df.to_csv(path_Event, index=False, encoding='CP949')
            good = float(list[6])
            buy = 0
            son = 0
            sell = 1

        E_df.loc[0] = [Time, list[1], list[2], list[3], list[4], list[5], list[6], good, buy, son, sell]
        # print(E_df)
        E_df.to_csv(path_Event, index=False, encoding='CP949')

        #########################################################################################
        ###20200921
        ###반만따 진행
        if sell == 1:
            if float(good) > 1:
                print('sell----------------------------------------------------------------------------')
                print('selling list : ', list)
                self.trade_stocks_sell_auto(list)
                #### 트레이드 된 로그 가져오기
                function_Event_Log(datetime.datetime.now(), "auto_trade Seliing",
                                   0,
                                   0, "Test_Log")
                print('sell----------------------------------------------------------------------------')


def function_Event_Log(Time, function, Run_Time, State, Log, code=0):
    """
    :param Time: Log 함수 호출 시간
    :param function: 함수 이름
    :param Run_Time: 함수 구동 시간
    :param State: 0--> Start, 1 --> End
    :param Log: 남길 내용
    :return:
    """
    import os
    import datetime

    path_file_dir = 'Open_API/Event_Log/{today}'.format(
        today=datetime.datetime.strftime(datetime.datetime.today(), '%Y.%m.%d'))
    path_file_dir = os.path.join('C:/Users/user/PycharmProjects/project_FIRE', path_file_dir)
    if not os.path.exists(path_file_dir):
        os.makedirs(path_file_dir)
    path_Event = os.path.join(path_file_dir, 'Time_{today}.csv'.format(
        today=datetime.datetime.strftime(datetime.datetime.today(), '%Y%m%d')))
    if os.path.exists(path_Event):
        E_df = pd.read_csv(path_Event, encoding='CP949')
    else:
        Event_Frame = {'Time': [], 'function': [], 'Run Time': [], 'State': [], 'Log': []}
        E_df = pd.DataFrame(Event_Frame)
        E_df.to_csv(path_Event, index=False, encoding='CP949')
    E_df.loc[len(E_df) + 1] = [Time, function, Run_Time, State, Log]
    # print(E_df)
    E_df.to_csv(path_Event, index=False, encoding='CP949')


def Trading_Event_Log(Time, function, Run_Time, State, Log, code=0):
    """
    :param Time: Log 함수 호출 시간
    :param function: 함수 이름
    :param Run_Time: 함수 구동 시간
    :param State: 0--> Start, 1 --> End
    :param Log: 남길 내용
    :return:
    """
    import os
    import datetime

    path_file_dir = 'Open_API/Event_Log/{today}'.format(
        today=datetime.datetime.strftime(datetime.datetime.today(), '%Y.%m.%d'))
    path_file_dir = os.path.join('C:/Users/user/PycharmProjects/project_FIRE', path_file_dir)
    if not os.path.exists(path_file_dir):
        os.makedirs(path_file_dir)
    path_Event = os.path.join(path_file_dir, 'Trading_{today}.csv'.format(
        today=datetime.datetime.strftime(datetime.datetime.today(), '%Y%m%d')))
    if os.path.exists(path_Event):
        E_df = pd.read_csv(path_Event, encoding='CP949')
    else:
        Event_Frame = {'Time': [], 'function': [], 'Run Time': [], 'State': [], 'Log': []}
        E_df = pd.DataFrame(Event_Frame)
        E_df.to_csv(path_Event, index=False, encoding='CP949')
    E_df.loc[len(E_df) + 1] = [Time, function, Run_Time, State, Log]
    # print(E_df)
    E_df.to_csv(path_Event, index=False, encoding='CP949')

# ###모듈화를 위하여 Main 함수 주석화 ###20200917
# if __name__ == "__main__":
# start_time = time.time()
# function_Event_Log(Time = datetime.datetime.now(),function= "auto_trade Start", Run_Time=0,State= 0, Log="auto_trade Program Start")
# app = QApplication(sys.argv)
# auto_trade = auto_trade()
#
# # print("app login")
# auto_trade.run()
### 구동 시간 설정 시작 ###20200825


### 구동 시간 설정 끝

# function_Event_Log(datetime.datetime.now(), "auto_trade End",  format(time.time() - start_time, ".2f"), 0, "auto_trade Program END")
