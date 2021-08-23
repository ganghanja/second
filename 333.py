import pybithumb
import time
import datetime
import telegram

# 주석은 최초 volatility-3 에 만들어서 조금 다를수 있음
# 21-08-20 k값 다양화, MT적용 ,텔레그램 메시지 기능 추가

def get_target_price(ticker,k): # 목표가 구하는 함수                                            
    df = pybithumb.get_ohlcv(ticker) # BTC의 ohlcv 값을 df:데이터프레임 형식??  으로 가리킴
    volatility = (df.iloc[-2]['high'] - df.iloc[-2]['low']) * k    #iloc[-2] 는 뒤에서 두번째 행, 즉 어제 고가-저가 계산
    target_price = df.iloc[-1]['open'] + volatility  # iloc[-1]은 오늘
    return target_price     # 목표가를 리턴

def buy_crypto_currency(bithumb, price, krw, ticker):  #매수함수(빗썸클래스와, 목표가, 원화잔고 , 티커를 입력받음)
    krw = krw/5     # 자정에 매도 후 krw로 한화 잔고 받아서 코인별로 나눠서 매수
    print("주문금액",krw)  # 한화 잔고 제대로 됐는지 확인
    unit = round(((krw * 0.9) / price),4)      # round함수로 소수점 4자리로 반올림해서 매수량 unit 계산
    print("주문수량",unit)  #주문 수량 확인/ 지정가 해보려했는데, 잘안되서 시장가 매수 중
    print(pybithumb.get_orderbook(ticker)['asks'][0]['price']) # 매도최하 값을 매수 값으로 지정가 해보려고 했으나, 잘안되네....
    return bithumb.buy_market_order(ticker, unit )    #buy_market_order("BTC", unit)  #buy_market_order은 시장가 매수 / 주문과 동시에 결과도 리턴해주는 코드
#bithumb.buy_limit_order(ticker, pybithumb.get_orderbook(ticker)['asks'][0]['price'] , unit ) 시장가 매수

def sell_crypto_currency(bithumb,ticker):  # 매도함수(빗썸클래스만 입력으로 받고 있네?여러코인 할때는 수정필요?)
    unit = bithumb.get_balance(ticker)[0]   # get_balance 함수 첫번째에는 코인 잔고가 있나 보네? 튜플형식? 튜플은 변경할수 없고, 딕셔너리{}와 리스트[] 는 수정 가능
    return bithumb.sell_market_order(ticker, unit)     # 시장가 매도 하고 결과도 리턴


def get_krw():  # 자산 평가 원화로 계산 하는 함수
    cash = 0   # cash 0으로 초기화
    for tiker in coin:   # coin 목록 순서대로 실행
        cash = cash + (bithumb.get_balance(tiker)[0] * pybithumb.get_current_price(tiker))  # 보유코인*현재가로 원화기준계산하여 합산
        time.sleep(0.1) # 0.1초 쉬자
    cash = cash + bithumb.get_balance("BTC")[2]   # 보유코인*현재가 + 남은 현금으로 원화기준 총 자산 계산
    return cash

def get_yesterday_ma(ticker,n): # 어제의 n일 종가 이동평균구하는 함수
     df = pybithumb.get_ohlcv(ticker)[-30:] 
     close = df['close']         #종가만 모아서
     ma = close.rolling(n).mean() # n개 평균
     return ma[-2]  # 마지막에서 2번째, 즉 어제포함 n일 이동 평균값 리턴

def MT_what(): #어제 기준 이동평균 값 구하는 함수
    for i in coin:
        if i=='BTC':
            if pybithumb.get_ohlcv(i)['close'][-2] > get_yesterday_ma(i,3): #3일이평
                MT_flag[i] = True
        elif i=='ETH':
            if pybithumb.get_ohlcv(i)['close'][-2] > get_yesterday_ma(i,3) or pybithumb.get_ohlcv(i)['close'][-2] > get_yesterday_ma(i,5) or pybithumb.get_ohlcv(i)['close'][-2] > get_yesterday_ma(i,10):
                MT_flag[i] = True
        elif i=='ADA':
            if pybithumb.get_ohlcv(i)['close'][-2] > get_yesterday_ma(i,5): #5일 이평
                MT_flag[i] = True
        elif i=='XRP':
            if pybithumb.get_ohlcv(i)['close'][-2] > get_yesterday_ma(i,3): 
                MT_flag[i] = True             
        elif i=='VET':
            if pybithumb.get_ohlcv(i)['close'][-2] > get_yesterday_ma(i,10):
                MT_flag[i] = True     
        elif i=='DOT':
            if pybithumb.get_ohlcv(i)['close'][-2] > get_yesterday_ma(i,5):
                MT_flag[i] = True      

#############################################################################################################################################################

with open("bithumb.txt", "r") as f :  # txt 파일에서 r 읽기형식으로 파일 오픈
    key1 = f.readline().strip()       # 1줄 읽어들이고, strip는 빈공간 잘라내는것? 
    key2 = f.readline().strip()       # 또 한줄 읽어 들이면 되겠쥬

bithumb = pybithumb.Bithumb(key1, key2)   # 키 2개를 입력해서 내계정 클래스를 bithumb 로 가리킴 

coin = ["BTC","ETH","ADA","XRP","VET","DOT"]
bal = {"BTC":0.001,"ETH":0.013, "ADA":20 ,"XRP":35, "VET":330, "DOT":1.5} # 잔고가 5만원 이상인지 확인해서 프로그램 종료 후 재시작시 다시 주문이 나가지 않도록 하기위해 필요 #코인 변경시 수정요!!
k_value = {"BTC":0.3,"ETH":0.4, "ADA":0.5 ,"XRP":0.7,"VET":0.4,"DOT":0.12} # k값 코인별로 상이

hold_flag = {"BTC":False, "ETH":False, "ADA":False, "XRP":False,"VET":False,"DOT":False}  # 플래그 초기화 False 상태여야 매수 주문이 나감 # 매수했다면 True / 그렇지않다면 False #코인 변경시 수정요!!
MT_flag = {"BTC":False, "ETH":False, "ADA":False, "XRP":False, "VET":False,"DOT":False} # True 면 상승장이라 매수

krw = get_krw()   # 원화기준 자산계산
cash = bithumb.get_balance('BTC')[2] # 매수 가능 원화 

print(hold_flag) # 시작시 Fasle 상태인지 확인 할 것.
print("원화기준 자산 평가", krw)
print("남은 현금", cash)
MT_what()       # MT 계산
print('MT_flag', MT_flag) 

#print(bithumb.get_balance())
#target_price = {'BTC':get_target_price("BTC",0.4),  'ETH':get_target_price("ETH",0.4) }
#print(target_price)
bot = telegram.Bot(token='1979429946:AAFxw9OCeNMgBvJxsoivKVJm9nB4xeXS604')
chat_id = 1063516017


for i in hold_flag: #프로그램 껏다 켤때 재매수 방지를 위해 5만원이상 잔고 인것은 플래그를 True로 변경해준다.
    if bal[i] <= bithumb.get_balance(i)[0]: #코인 잔고가 5만원 이상이면,
        hold_flag[i] = True  # 해당 플래그를 True로 변경/ True시 매수 주문 불가하며, 매도가 가능


while True:  # 현재가를 계속 감시하다가 목표가가 되면 매수하고, 자정이되면 매도
    try: #에러 처리를 위해서
        for i in coin:  #코인리스트로  반복 중 #코인 변경시 수정요!!
            now = datetime.datetime.now()  # 현재 시각
            mid = datetime.datetime(now.year, now.month, now.day) #자정 / datetime.datetime(now.year, now.month, now.day , 1 , 2 , 3)  => 같은날 1시,2분,3초를 표현
            delta = datetime.timedelta(seconds=60) # 시간 더 하기 할때 사용. 10초를 표현. seconds, minutes, hours 사용가능하겠지???????????
            target_price = get_target_price(i, k_value[i])    # 코인별로 목표가를 target_price로 가리킴/k값이 통일된 상태인데, 코인별로 달리하려면 딕셔너리 사용하면 될 듯
            price = pybithumb.get_current_price(i)  # 해당코인 현재가 불러오고

            if mid <= now <= mid + delta:  # 현재 시각이 자정과 자정+delta초(100초) 사이에 있을 때, 백테나 실전 확인후 delta나 매도 시간 변경 필요.
                if hold_flag[i] == True:      # 해당 코인 플래그가 True 라면
                    ret = sell_crypto_currency(bithumb, i)  # 매도함수 실행
                    time.sleep(3) #매도 중복 막기위해서 1초 쉬어봄....
                    ret = bithumb.get_order_completed(ret) # 매도결과 ret으로 가리킴
                    print("매도", ret)  # '매도'문자 출력 및 매도 결과 출력
                    hold_flag[i] = False  # 플래그를 False 로 만들어서 매수 할 수 있는 상태로 만듬
                    target_price = get_target_price(i, k_value[i])  # 다시 새로운 목표가 계산
                    message = ret      #매도 결과 메세지에 싣기
                    bot.sendMessage(chat_id=chat_id, text=str(message)) #텔레그램에 문자 형식으로 보내기
                krw = get_krw() # krw 잔고정리
                MT_what() # 자정에 다 팔고 MT계산
                print('MT_flag', MT_flag)

            else:     # 현재 시각이 자정~자정+10초가 아니라면
                price = pybithumb.get_current_price(i)  # 해당코인 현재가 불러오고
                if bithumb.get_balance(i)[0] < bal[i]: #해당코인 잔고가 5만원 이하라면 
                    if (MT_flag[i] == True):
                        if (target_price <= price <= target_price*1.01) and (hold_flag[i] == False) :#and  #  현재가가 목표가와 목표가+1% 이내 일때, 매수플래그 False이고, MT_플래그 True이면,
                            ret = buy_crypto_currency(bithumb, price, krw,i)  # 계정클래스와 현재가 매수함수로 보내주고, ret로 결과 받음
                            time.sleep(1) #매수 중복 막기위해서 1초 쉬어봄....
                            print("매수", ret) # 매수결과 출력
                            hold_flag[i] = True # 플래그 True로 만들어서 매도 할수 있게 만듬.

                            message = ret      #매도 결과 메세지에 싣기
                            bot.sendMessage(chat_id=chat_id, text=str(message)) #텔레그램에 문자 형식으로 보내기

                            krw = get_krw() # 매수 로직 동작 했으니 krw 잔고정리 한번 하고.
                            cash = bithumb.get_balance('BTC')[2] # 남은 현금 정리

            print(f'{i:4}', "현재/목표" , round(price/target_price,3), "목표가",  f'{target_price:10}', "현재가", f'{price:10}'  , bithumb.get_balance(i), now, sep='  ')
            print('   ','총 자산(원)',f'{krw:,.0f}', '원화',f'{cash:,.0f}','\n','', '매수하는날?',MT_flag,'\n','','매수했는가?', hold_flag,              sep='   ')
                                     #시작or 자정에or 매수한 후 krw계산/즉, 실시간이 아님. 매수 금액계산을 위한 변수
    except: 
        print("에러 발생") 
        bot.sendMessage(chat_id=chat_id, text="에러 발생") # 텔레그램에 에러 메세지 전송

    time.sleep(1)  #1초 휴식, 빗썸은 초당 125회, 업비트는 초당 60회???????? 불확실. 확인요/ 위반시 계정 차단

