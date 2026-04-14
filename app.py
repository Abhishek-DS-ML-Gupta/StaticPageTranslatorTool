import torch
import traceback
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit import IndicProcessor

LANGUAGES = {
    "English": "eng_Latn", "Hindi": "hin_Deva", "Bengali": "ben_Beng",
    "Tamil": "tam_Taml", "Telugu": "tel_Telu", "Marathi": "mar_Deva",
    "Gujarati": "guj_Gujr", "Kannada": "kan_Knda", "Malayalam": "mal_Mlym",
    "Punjabi": "pan_Guru", "Urdu": "urd_Arab", "Odia": "ory_Orya",
    "Assamese": "asm_Beng", "Sanskrit": "san_Deva", "Kashmiri": "kas_Arab",
    "Sindhi": "snd_Arab", "Manipuri": "mni_Mtei", "Santali": "sat_Olch",
    "Nepali": "npi_Deva", "Konkani": "gom_Deva", "Dogri": "doi_Deva",
    "Bodo": "brx_Deva", "Maithili": "mai_Deva"
}

# A6000 Strategy: Load all models onto GPU 0
MODELS_INFO = {
    "en-indic": {"name": "ai4bharat/indictrans2-en-indic-1B", "gpu": "cuda:0"},
    "indic-en": {"name": "ai4bharat/indictrans2-indic-en-1B", "gpu": "cuda:0"},
    "indic-indic": {"name": "ai4bharat/indictrans2-indic-indic-1B", "gpu": "cuda:0"} 
}
app = FastAPI(title="IndicTrans2 Production API - A6000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

loaded_models = {}

@app.on_event("startup")
async def startup_event():
    print("Loading models onto A6000 GPUs...")
    for model_key, model_data in MODELS_INFO.items():
        device = model_data["gpu"]
        model_name = model_data["name"]
        print(f"Loading {model_key} onto {device}...")
        
        ip = IndicProcessor(inference=True)
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name, trust_remote_code=True, torch_dtype=torch.float16
        ).to(device)
        
        loaded_models[model_key] = {'model': model, 'tokenizer': tokenizer, 'ip': ip}
    print("All models loaded successfully! API is ready.")

def translate_chunk(batch, m, t, p, src_lang, tgt_lang):
    try:
        preprocessed = p.preprocess_batch(batch, src_lang=src_lang, tgt_lang=tgt_lang)
        inputs = t(preprocessed, truncation=True, padding="longest", return_tensors="pt").to(m.device)
        
        with torch.no_grad():
            generated_tokens = m.generate(**inputs, use_cache=True, max_length=512, num_beams=4, early_stopping=True)
        
        decoded = t.batch_decode(generated_tokens.detach().cpu().tolist(), skip_special_tokens=True)
        return p.postprocess_batch(decoded, lang=tgt_lang)
    
    except RuntimeError as e:
        if 'out of memory' in str(e).lower():
            print(f"OOM hit with batch size {len(batch)}. Splitting and retrying...")
            torch.cuda.empty_cache()
            mid = len(batch) // 2
            if mid == 0: return batch
            top_half = translate_chunk(batch[:mid], m, t, p, src_lang, tgt_lang)
            bottom_half = translate_chunk(batch[mid:], m, t, p, src_lang, tgt_lang)
            return top_half + bottom_half
        else:
            raise e

@app.post("/translate")
async def translate_text(sentences: list[str] = Form(...), src_lang: str = Form(...), tgt_lang: str = Form(...)):
    if not sentences:
        return {"translations": []}

    src_lang_name = [k for k, v in LANGUAGES.items() if v == src_lang][0]
    tgt_lang_name = [k for k, v in LANGUAGES.items() if v == tgt_lang][0]

    if src_lang_name == "English" and tgt_lang_name != "English": model_key = "en-indic"
    elif tgt_lang_name == "English" and src_lang_name != "English": model_key = "indic-en"
    elif src_lang_name != "English" and tgt_lang_name != "English": model_key = "indic-indic"
    else: return {"translations": sentences}

    m = loaded_models[model_key]['model']
    t = loaded_models[model_key]['tokenizer']
    p = loaded_models[model_key]['ip']

    valid_indices = [idx for idx, s in enumerate(sentences) if s.strip()]
    valid_sentences = [sentences[idx] for idx in valid_indices]
    translations = [""] * len(sentences)

    if valid_sentences:
        batch_size = 32
        for i in range(0, len(valid_sentences), batch_size):
            batch = valid_sentences[i:i+batch_size]
            translated_batch = translate_chunk(batch, m, t, p, src_lang, tgt_lang)
            
            for idx_offset, trans in enumerate(translated_batch):
                translations[valid_indices[i + idx_offset]] = trans
                
            torch.cuda.empty_cache()

    return {"translations": translations}

@app.get("/languages")
async def get_languages():
    return LANGUAGES
