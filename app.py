import streamlit as st

# 시놉시스 정보를 출력하는 함수
def getSynopsis(synopsises,indexes):
    synopsisList = []
    for i in range(10):
        synopsisList[i] = synopsises[indexes[i]]
    return synopsisList

# OTT 제공 정보 출력하는 함수
def getOTT(titlesDic):
    ottList = list(titlesDic.values())
    ottStr = []
    ott_idx = {
        0 : "seezn",
        1 : "series_on",
        2 : "watcha",
        3 : "wavve",
        4 : "netflix",
        5 : "tiving"
    }
    for i in range(10):
        num = 0
        temp2 = []
        temp = ottList[i] # [1, 1, 0, 1, 0, 0]
        for k in range(6):
            if (temp[k] == 1):
                temp2[num] = ott_idx[k]
                num = num + 1
            else:
                pass
        ottStr[i] = temp2
    return ottStr

# 이미지url를 받아오는 함수
def getImage(titlesDic):
    titles = list(titlesDic.keys())
    otts = list(titlesDic.values())
    imageList = []
    for i in range(10):
        if (otts[i][4] == 1):
            image_url = f"""'netflix img/{titles[i]}.jpg'"""
            imageList[i] = image_url
        elif (otts[i][5] == 1):
            image_url = f"""'tving img/{titles[i]}.jpg'"""
            imageList[i] = image_url
        else:
            image_url = f"""'img/no_image.jpg'"""
            imageList[i] = image_url
    return imageList

# 가장 추천하는 ott 정보를 가져오는 함수
def getbestOTT(ott_dict):
    temp = list(ott_dict.values())
    result = temp[5] # 0~5까지의 숫자로 출력
    ott_idx = {
        0 : "seezn",
        1 : "series_on",
        2 : "watcha",
        3 : "wavve",
        4 : "netflix",
        5 : "tiving"
    }
    finResult = ott_idx[result]
    return finResult

def model(title):
    search_value = title
    # 데이터 불러오기
    import pandas as pd
    data = pd.read_csv('data.csv',engine='python',encoding='CP949')

    # 데이터 전처리
    from konlpy.tag import Okt
    synopsis = data['synopsis']
    
    # 한국어 형태소 분석
    okt = Okt()
    synopsis_array = []
    for i in data['index']:
        synopsis_array.append(" ".join(okt.nouns(synopsis[i])))
    
    data['synopsis_preprocessing'] = synopsis_array

    # 데이터 벡터화 진행
    from sklearn.feature_extraction.text import TfidfVectorizer
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(data['synopsis_preprocessing'])

    # 코사인 유사도 과정 진행
    from sklearn.metrics.pairwise import linear_kernel

    cos_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # 드라마제목을 입력하면 인덱스를 가져온다.
    indices = pd.Series(data.index, index=data['name']).drop_duplicates()

    # 드라마의 제목을 입력받으면 코사인 유사도를 통해서 가장 유사도가 높은 상위 10개의 영화 목록 반환
    import numpy as np

    # return data type
    return_dict = {}
    ott_dict = {}

    # ott 가격정보 상수화하기
    seezn_price = 6300
    watcha_price = 7900
    wavve_price =7900
    netflix_price = 9500
    tving_price = 7900  

    idx = indices[search_value] # 영화 제목을 통해서 전체 데이터 기준 그 영화의 index 값을 얻기

    # 코사인 유사도 매트릭스 에서 idx에 해당하는 데이터를 (idx, 유사도 형태로 얻기)
    sim_scores = list(enumerate(cos_sim[idx]))

    # 정렬하기
    # 자기 자신을 제외한 10개의 추천 영화를 슬라이싱
    sim_scores = sorted(sim_scores, key=lambda x : x[1], reverse=True)

    # 자기 자신을 제외한 10개의 추천 영화를 슬라이싱
    sim_scores = sim_scores[1:11] # 자기 자신을 제외함

    # 추천 영화 목록 10개의 인덱스 정보 추출 (리스트)
    drama_indices = [i[0] for i in sim_scores]

    # title + ott_info 딕셔너리 생성
    for item in drama_indices:
        return_dict[data['name'].iloc[item]] = list(data.iloc[item, 3:])

    # 가성비 확인 ott dict 만들기 
    # ott 이름 + 액수 / 마지막 인덱스는 bestchoice
    ott_list = []
    for _, ott in return_dict.items():
        ott_list.append(ott)
    ott_nparray = np.array(ott_list)
    ott_sum = np.sum(ott_nparray, axis=0)

    try :
        ott_dict['seezn'] = int(seezn_price / ott_sum[0])
    except:
        ott_dict['seezn'] = seezn_price
    # seris_on은 편당 가격제이기 때문에 가성비 체크에서 제외
    try:
        ott_dict['watcha'] = int(watcha_price / ott_sum[2])
    except:
        ott_dict['watcha'] = watcha_price
    try:
        ott_dict['wavve'] = int(wavve_price / ott_sum[3])
    except:
        ott_dict['wavve'] = wavve_price
    try:
        ott_dict['netflix'] = int(netflix_price / ott_sum[4])
    except:
        ott_dict['netflix'] = netflix_price
    try:
        ott_dict['tving'] = int(tving_price / ott_sum[5])
    except:
        ott_dict['tving'] = tving_price

    # 최선의 선택 출력
    best_choice = np.argmin(np.array(ott_dict.values))
    # print(vest_choice)
    ott_dict['best_choice'] = 0 if best_choice == 0 else best_choice + 1

    # synopsis를 리스트에 저장하는 함수 호출
    synopsisList = synopsis.tolist()
    finSynopsisList = getSynopsis(synopsisList,drama_indices)

    # title은 return_dict의 key값이용
    finTitleList= list(return_dict.keys())

    # image는 getImage 함수를 이용해 이미지 경로를 스트링으로 담은 리스트 반환
    finImageURLList = getImage(return_dict)

    # ott-info는 getOTT함수를 이용해 해당되는 오티티 정보(스트링) 담긴 리스트 반환
    finOTTlist = getOTT(return_dict)

    # best-choice는 ott_dict의 마지막 값을 이용해 해당되는 best 오티티의 정보와 가격을 반환
    finBestPrice = str(ott_dict['best_choice'])
    finBestOTT = getbestOTT(ott_dict)

    
    # 추천페이지 출력 함수 호출 
    return finTitleList, finImageURLList, finSynopsisList, finOTTlist, finBestOTT, finBestPrice

def getAllTitle():
  import pandas as pd
  data = pd.read_csv('data.csv',engine='python',encoding='CP949')
  # 전체 제목 데이터(셀렉트 박스를 위하여)
  allTitles = data['name'].tolist()
  return allTitles

st.set_page_config(layout='wide')
st.header('Stolio_Flix') # 제목으로 출력
st.subheader('드라마를 선택해주세요. 관련이 높은 드라마 10개를 추천해드립니다!!!')
title = st.selectbox('드라마 선택 하기', getAllTitle()) # 선택한 결과가 title에 들어간다. 셀렉트 박스 생성, 밑에 영화 리스트가 다 들어간다.
finTitleList, finImageURLList, finSynopsisList, finOTTlist, finBestOTT, finBestPrice = model(title)
if st.button('추천 뿅!!'): # 버튼 생성
    with st.spinner('영화 고르는 중...'): # 밑의 모든 작업이 끝날때까지 빙글빙글 도는 로딩중 바가 생긴다.
        idx = 0
        for i in range(0,2): # 두번 반복
            cols = st.columns(5)
            for col in cols:
                col.write(finTitleList[idx])           
                col.image(finImageURLList[idx])
                col.write(finSynopsisList[idx])
                col.write("ott제공 : ")
                k = 0
                for k in range(len(finOTTlist)):
                  col.write(finOTTlist[i])
                col.write("최고의 갓성비 OTT:" + finBestOTT[idx])
                col.write("가격은?" + finBestPrice[idx])
                idx += 1

# 웹사이트 실행하고 싶다면 streamlit run 파일이름 을 터미널에 치기