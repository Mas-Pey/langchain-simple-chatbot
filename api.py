from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) 

openai.api_key = os.environ['OPENAI_API_KEY']

app = FastAPI()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, top_p=1)
output_parser = StrOutputParser()

# Struktur input
class RecipeInput(BaseModel):
    dokumen: str
    text: str
    history: str

@app.post("/tanya-resep")
async def tanya_resep(input: RecipeInput):
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"kamu adalah Astuti, seorang chef yang bisa memasak apa saja, semua informasi nama masakan, 
             ingridients, steps, dan url terkait dari masing masing resep dapat dilihat pada {input.dokumen}. 
             Gaya bahasamu santai dan casual. Jangan menjawab terlalu panjang jika tidak diperlukan. 
             jawablah hanya tentang apa yang diminta oleh user. Selalu rujuk pada data yang dimiliki, 
             bila tidak ada data yang sesuai, berikan jawaban bahwa saya tidak tahu secara sopan. 
             Sangat dilarang untuk menjawab di luar pengetahuan yang diberikan"),
            ("system", f"{input.history}"),
            ("user", f"{input.text}")
        ])
        chain = prompt | llm | output_parser
        response = chain.invoke({"input.dokumen": input.dokumen, "input.text": input.text})
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# endpoint cek gambar
class CekGambar(BaseModel):
    cek: bool
@app.post("/cek-gambar", response_model=CekGambar)
async def cek_gambar(input: RecipeInput):
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Apakah user meminta gambar makanan? jika iya, berikan jawaban true dan jika tidak, berikan jawaban false."),
            ("user", f"{input.text}")
        ])
        chain = prompt | llm | output_parser
        response = chain.invoke({"input.dokumen": input.dokumen, "input.text": input.text})
        return {"cek": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# endpoint kirim gambar
class KirimGambar(BaseModel):
    gambar: str
@app.post("/kirim-gambar", response_model=KirimGambar)
async def kirim_gambar(input: RecipeInput):
    try:
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"kirimkan url gambar yang diminta oleh user"),
            ("system", f"{input.history}"),
            ("user", f"{input.text}"),
            
        ])
        chain = prompt | llm | output_parser
        response = chain.invoke({"input.dokumen": input.dokumen, "input.text": input.text})
        return {"gambar": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

