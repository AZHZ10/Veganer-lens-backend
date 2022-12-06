import cv2 #openCV 
import numpy as np
import pandas as pd
import math
import json
from io import BytesIO
from PIL import Image 
import urllib.request
from hangul_utils import split_syllable_char, split_syllables, join_jamos
from symspellpy import SymSpell, Verbosity

class VeganerOCR():
  def __init__(self):
    self.initialize()
  def initialize(self, ):
    import easyocr
    self.reader = easyocr.Reader(['ko']) # need to run only once to load model into memory
    self.dictionary_path = "dataset/menu_dic_depo.txt"
    self.menudata = "dataset/menu_dataset.csv"
  def send_info(self, ):
     #1. grayscale
     #사진 파일 경로 
    url = 's3-bucket-img-url' 
    res = urllib.request.urlopen(url).read()
    img = np.array(Image.open(BytesIO(res)))
    gray = cv2.cvtColor(img , cv2.COLOR_BGR2GRAY) #컬러 체계 변경
    
    #binary
    ret, dst = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY) 

    text = self.reader.readtext(dst)

    #OCR 출력 결과로 나온 단어 목록 저장할 리스트
    result_words = []

    #OCR 결과 리스트에서 글자만 추출해서 단어 목록 리스트에서 저장
    #공백 제거 -> 마지막 문자가 원이라면 제거 -> 숫자 + 특수 문자 제거
    for i in text:
     word = i[1].replace(" ", "")
     if word.strip()[-1] == '원':
       word = word[:-1]
     newstring = ''.join([i for i in word if not i.isdigit() and i.isalnum()])
     if not newstring == '':
       result_words.append(newstring)

    #오타 교정 알고리즘

    sym_spell = SymSpell(max_dictionary_edit_distance=3)
    sym_spell.load_dictionary(self.dictionary_path, 0, 1)

    for i in range(len(result_words)):
        term = result_words[i]
        term = split_syllables(term)
        suggestions = sym_spell.lookup(term, Verbosity.ALL, max_edit_distance=2)
        for sugg in suggestions:
         result_words[i] = join_jamos(sugg.term)
     
    #data에서 대조 후 출력하기 
    #result_words -> 하나하나 엑셀 파일과 비교 -> 결과 출력

    df = pd.read_csv(self.menudata)
    menu = []
    
    df_indexs = df.shape[0] -1

    for word in result_words: 
      for idx in range(df_indexs):
       if(df.loc[idx, '음식명'] == word):
         nonv = df.loc[idx, '구분']
         name = df.loc[idx, '음식명']
         info = df.loc[idx, '주의 재료']
         new_menu = {}
         new_menu['nonv'] = nonv
         new_menu['name'] = name
         new_menu['info'] = info
         menu.append(new_menu)

    result1 = json.dumps(menu,ensure_ascii=False)
    return result1
