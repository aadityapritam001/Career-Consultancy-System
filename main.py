from flask import Flask,render_template,request
from werkzeug import secure_filename
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFSyntaxError
import io
import spacy
import en_core_web_sm
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
app=Flask(__name__)
@app.route('/')
def home():
    return (render_template('index.html'))
@app.route('/next')
def next():
    return (render_template('next.html'))
@app.route('/res')
def res():
    return (render_template('res.html'))

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      name=request.form.get('name')
      print(type(name))
      f = request.files['file']
      f.save(secure_filename("resume.pdf"))
      ttext=""
      for page in extract_text_from_pdf("resume.pdf"):
          ttext+=" "+page
      text=" ".join(ttext.split())
      nlp = en_core_web_sm.load()
      temp=nlp(text)
      skills=extract_skills(temp)
    #   skills=list(s)
      if len(skills)<=5:
          pass
      else:
          skills=skills[0:5]
    #   for token in temp:
    #       lis.append(token.text)
      print(skills)
      st=str(skills)
      df=pd.read_csv('app\\career.csv')
      Feature=pd.read_csv('app\\model.csv')
      X=Feature
      Y=df["Job_title"].values
      X_traindataset, X_testdataset, Y_traindataset, Y_testdataset = train_test_split( X, Y, test_size=0.3, random_state=1) 
      LR = LogisticRegression(C=0.01, solver='liblinear').fit(X_traindataset,Y_traindataset)
      arr=[[0]*1117]*1
      n=[]
      print(skills)
      for ele in skills:
        ele=ele.lower()
        c=Feature.columns.get_loc(ele)
        n.append(c)
        # print(n)
      for i in range(0,len(skills)):
          arr[0][n[i]]=1
        #   print(arr)
      df=pd.DataFrame(arr)
      pred = LR.predict(df)
    #   return f"Hey {name}!\n Your Skills : {skills}\nRecommended Career:{str(pred[0])}"
      return render_template("res.html",value=name,skill=str(skills),result=str(pred[0]))
      
# @app.route('/index')
#     return (render_template('index.html'))
def extract_skills(nlp_text):
    tokens = [token.text for token in nlp_text if not token.is_stop]
    data = pd.read_csv("app\\s.csv")
    skills = list(data.columns.values)
    skillset = []
    noun=nlp_text.noun_chunks
    for token in tokens:
        if token.lower() in skills:
            # if token.lower() not in skillset:
                skillset.append(token)
    for token in noun:
        token = token.text.lower().strip()
        if token in skills:
            # if token not in skillset:
                skillset.append(token)
    return [i.capitalize() for i in set([i.lower() for i in skillset])]
def extract_text_from_pdf(pdf_path):
    
    '''
    :return: iterator of string of extracted text
    '''
    with open(pdf_path, 'rb') as fh:
        try:
            for page in PDFPage.get_pages(fh,caching=True,check_extractable=True):
                resource_manager = PDFResourceManager()
#                 print(type(resource_manager))
                file_handle = io.StringIO()
                converter = TextConverter(resource_manager, file_handle, codec='utf-8', laparams=LAParams())
#                 print(type(converter))
                page_interpreter = PDFPageInterpreter(resource_manager, converter)
                page_interpreter.process_page(page)
#                 TextConverter()
                text = file_handle.getvalue()
                yield text
                converter.close()
                file_handle.close()
        except PDFSyntaxError:
            return
ttext=""
# for page in extract_text_from_pdf("C:\\Users\\amans\\Desktop\\Pdf\\AmanSahay.pdf"):
#     ttext+=" "+page
if __name__ == '__main__':
    app.run(debug=True)