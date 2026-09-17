import json
import os
import hashlib
import random
import uuid
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file

app = Flask(__name__)
app.secret_key = 'maktab_platformasi_secret_2025'

@app.context_processor
def inject_now():
    return {'now': datetime.now().strftime('%H:%M')}

DATA_FILE = os.path.join(os.path.dirname(__file__), 'school_system_data.json')
CUSTOM_QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), 'custom_questions.json')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SUBJECTS = [
    "Matematika", "Fizika", "Kimyo", "Biologiya",
    "Ona tili", "Ingliz tili", "Tarix",
    "Geografiya", "Informatika", "Adabiyot",
]

SUBJECT_ICONS = {
    "Matematika": "🔢", "Fizika": "⚡", "Kimyo": "🧪", "Biologiya": "🧬",
    "Ona tili": "📖", "Ingliz tili": "🌍", "Tarix": "📜",
    "Geografiya": "🗺️", "Informatika": "💻", "Adabiyot": "📚",
}

DAYS = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"]
PERIODS = [
    "1-dars (08:30)", "2-dars (09:20)", "3-dars (10:10)",
    "4-dars (11:00)", "5-dars (11:50)", "6-dars (12:40)",
    "7-dars (13:30)", "8-dars (14:20)"
]

SUBJECT_COLORS = {
    "Matematika": "subj-matematika",
    "Fizika": "subj-fizika",
    "Kimyo": "subj-kimyo",
    "Biologiya": "subj-biologiya",
    "Ona tili": "subj-ona-tili",
    "Ingliz tili": "subj-ingliz-tili",
    "Tarix": "subj-tarix",
    "Geografiya": "subj-geografiya",
    "Informatika": "subj-informatika",
    "Adabiyot": "subj-adabiyot",
}

SUBJECT_TIMERS = {
    "Matematika": 20, "Fizika": 25, "Kimyo": 20, "Biologiya": 15,
    "Ona tili": 15, "Ingliz tili": 15, "Tarix": 20,
    "Geografiya": 20, "Informatika": 20, "Adabiyot": 15,
}

# ===== QUESTION BANK =====
QUESTION_BANK = {
    "Matematika": {
        "Oson": [
            {"q": "2 + 2 necha?", "a": "4"}, {"q": "5 x 3 necha?", "a": "15"},
            {"q": "10 - 7 necha?", "a": "3"}, {"q": "8 + 6 necha?", "a": "14"},
            {"q": "12 / 4 necha?", "a": "3"}, {"q": "9 + 8 necha?", "a": "17"},
            {"q": "7 x 4 necha?", "a": "28"}, {"q": "15 - 9 necha?", "a": "6"},
            {"q": "20 + 13 necha?", "a": "33"}, {"q": "100 / 5 necha?", "a": "20"},
            {"q": "6 x 7 necha?", "a": "42"}, {"q": "45 - 18 necha?", "a": "27"},
            {"q": "3 x 9 necha?", "a": "27"}, {"q": "81 / 9 necha?", "a": "9"},
            {"q": "16 + 14 necha?", "a": "30"}, {"q": "5 x 8 necha?", "a": "40"},
            {"q": "72 - 36 necha?", "a": "36"}, {"q": "11 x 4 necha?", "a": "44"},
            {"q": "56 / 8 necha?", "a": "7"}, {"q": "23 + 47 necha?", "a": "70"},
            {"q": "90 - 45 necha?", "a": "45"}, {"q": "13 x 3 necha?", "a": "39"},
            {"q": "64 / 8 necha?", "a": "8"}, {"q": "19 + 24 necha?", "a": "43"},
            {"q": "7 x 9 necha?", "a": "63"},
        ],
        "O'rta": [
            {"q": "x^2 = 49 bo'lsa, x necha?", "a": "7"}, {"q": "15% 200 necha?", "a": "30"},
            {"q": "(3 + 5) x 2 necha?", "a": "16"}, {"q": "144 kvadrat ildizi necha?", "a": "12"},
            {"q": "2^3 necha?", "a": "8"}, {"q": "3^4 necha?", "a": "81"},
            {"q": "25% 80 necha?", "a": "20"}, {"q": "(12 - 4) x 5 necha?", "a": "40"},
            {"q": "225 kvadrat ildizi necha?", "a": "15"}, {"q": "5^2 + 3^2 necha?", "a": "34"},
            {"q": "10% 450 necha?", "a": "45"}, {"q": "81 kvadrat ildizi necha?", "a": "9"},
            {"q": "4^3 necha?", "a": "64"}, {"q": "(7 + 3) x 8 necha?", "a": "80"},
            {"q": "30% 60 necha?", "a": "18"}, {"q": "169 kvadrat ildizi necha?", "a": "13"},
            {"q": "6^2 necha?", "a": "36"}, {"q": "(15 / 3) + 7 necha?", "a": "12"},
            {"q": "50% 120 necha?", "a": "60"}, {"q": "196 kvadrat ildizi necha?", "a": "14"},
            {"q": "7^3 necha?", "a": "343"}, {"q": "(9 - 2) x 6 necha?", "a": "42"},
            {"q": "75% 200 necha?", "a": "150"}, {"q": "324 kvadrat ildizi necha?", "a": "18"},
            {"q": "8^2 necha?", "a": "64"},
        ],
        "Qiyin": [
            {"q": "log2(256) necha?", "a": "8"}, {"q": "sin(90 daraja) necha?", "a": "1"},
            {"q": "5 faktorial necha?", "a": "120"}, {"q": "C(5,2) necha?", "a": "10"},
            {"q": "log10(1000) necha?", "a": "3"}, {"q": "cos(60 daraja) necha?", "a": "0.5"},
            {"q": "6 faktorial necha?", "a": "720"}, {"q": "P(4,2) necha?", "a": "12"},
            {"q": "tan(45 daraja) necha?", "a": "1"}, {"q": "7 faktorial necha?", "a": "5040"},
            {"q": "C(6,3) necha?", "a": "20"}, {"q": "log3(81) necha?", "a": "4"},
            {"q": "sin(30 daraja) necha?", "a": "0.5"}, {"q": "cos(0 daraja) necha?", "a": "1"},
            {"q": "8 faktorial necha?", "a": "40320"}, {"q": "C(10,2) necha?", "a": "45"},
            {"q": "log2(1024) necha?", "a": "10"}, {"q": "sin2(x) + cos2(x) necha?", "a": "1"},
            {"q": "e^0 necha?", "a": "1"}, {"q": "ln(e) necha?", "a": "1"},
            {"q": "4 faktorial + 3 faktorial necha?", "a": "30"},
            {"q": "|-5| + |3| necha?", "a": "8"},
            {"q": "10^3 necha?", "a": "1000"}, {"q": "2^10 necha?", "a": "1024"},
            {"q": "9 kvadrat ildizi + 16 kvadrat ildizi necha?", "a": "7"},
        ],
    },
    "Fizika": {
        "Oson": [
            {"q": "Suv qaynash harorati necha gradus?", "a": "100"},
            {"q": "Yerning tabiiy yo'ldoshi nima?", "a": "oy"},
            {"q": "Suv kimyoviy formulasi nima?", "a": "h2o"},
            {"q": "Kuch birlik nima bilan o'lchanadi?", "a": "nyuton"},
            {"q": "Harakatsizlik qonuni nechanchi?", "a": "1"},
            {"q": "O'tkirlik birligi nima?", "a": "gerc"},
            {"q": "Quvvat birligi nima?", "a": "vatt"},
            {"q": "Harorat birligi nima?", "a": "kelvin"},
            {"q": "Ish birligi nima?", "a": "djoul"},
            {"q": "Bosim birligi nima?", "a": "paskal"},
            {"q": "Muz erish harorati necha?", "a": "0"},
            {"q": "Gravitatsiya kuchi nima?", "a": "tortishish"},
            {"q": "Zaryad birligi nima?", "a": "kulon"},
            {"q": "Oqim birligi nima?", "a": "amper"},
            {"q": "Kuchlanish birligi nima?", "a": "volt"},
            {"q": "Tezlik birligi nima?", "a": "m/s"},
            {"q": "Massa birligi nima?", "a": "kilogramm"},
            {"q": "Suv qotish harorati necha?", "a": "0"},
            {"q": "Elastiklik qonuni kimniki?", "a": "guk"},
            {"q": "Yorug'lik nurlari qanday tarqaladi?", "a": "to'g'ri"},
            {"q": "Yorug'lik tezligi qanday harakat?", "a": "to'g'ri"},
            {"q": "Inersiya tushunchasi nima?", "a": "harakatsizlik"},
            {"q": "Energiya saqlanish qonuni kimniki?", "a": "mayer"},
            {"q": "Atom yadrosi qanday zarralardan iborat?", "a": "proton neytron"},
            {"q": "Magnit maydon qayerda hosil bo'ladi?", "a": "oqim"},
        ],
        "O'rta": [
            {"q": "E = mc2 formulani kim yozgan?", "a": "eynshteyn"},
            {"q": "Nyutonning 2-qonuni formulasi?", "a": "f=ma"},
            {"q": "1 kVt necha Vt?", "a": "1000"},
            {"q": "Oqim birlik nima?", "a": "amper"},
            {"q": "Kuchlanish birlik nima?", "a": "volt"},
            {"q": "Kinematika formulasi: v = ?", "a": "v0+at"},
            {"q": "Potensial energiya formulasi?", "a": "mgh"},
            {"q": "Kinetik energiya formulasi?", "a": "mv2/2"},
            {"q": "Omm qonuni qanday?", "a": "i=ur"},
            {"q": "Kondensator sig'imi birligi?", "a": "farad"},
            {"q": "Induksiya qonuni kimniki?", "a": "faradey"},
            {"q": "Impuls formulasi?", "a": "mv"},
            {"q": "Ish formulasi?", "a": "fs"},
            {"q": "Quvvat formulasi?", "a": "p=wt"},
            {"q": "Kuch momenti formulasi?", "a": "m=fl"},
            {"q": "Obyektning og'irligi formulasi?", "a": "p=mg"},
            {"q": "Optika qonuni nima?", "a": "aks etish sindirish"},
            {"q": "To'lqin tezligi formulasi?", "a": "v=lf"},
            {"q": "Umumiy qarshilik ketma-ket ulanishda?", "a": "r1+r2"},
            {"q": "1 MPa necha Pa?", "a": "1000000"},
            {"q": "Energiya saqlanish qonuni?", "a": "e=const"},
            {"q": "Aralashma harorati formulasi?", "a": "m1t1+m2t2/m1+m2"},
            {"q": "1 eV necha J?", "a": "1.6e-19"},
            {"q": "Issiqlik o'tkazuvchanlik formulasi?", "a": "q=kt"},
            {"q": "O'zaro tortishish qonuni kimniki?", "a": "nyuton"},
        ],
        "Qiyin": [
            {"q": "Plank doimiysi h necha? (J*s)", "a": "6.63e-34"},
            {"q": "Yorug'lik tezligi necha m/s?", "a": "300000000"},
            {"q": "Entropiya qonuni qanday ataladi?", "a": "termodinamikaning 2-qonuni"},
            {"q": "Kvant mexanikasining asoschisi kim?", "a": "planck"},
            {"q": "Kulon doimiysi necha?", "a": "9e9"},
            {"q": "Boltzman doimiysi necha?", "a": "1.38e-23"},
            {"q": "Gravitatsiya doimiysi necha?", "a": "6.67e-11"},
            {"q": "Maxvel tenglamalari nechta?", "a": "4"},
            {"q": "Lorentz kuch formulasi?", "a": "f=qvb"},
            {"q": "Radioaktivlikni kim kashf etgan?", "a": "bekkerel"},
            {"q": "Lazer asoschisi kim?", "a": "meiman"},
            {"q": "Rezonans chastotasi formulasi?", "a": "1/2pi*sqrt(lc)"},
            {"q": "De-Broyl to'lqin uzunligi?", "a": "h/p"},
            {"q": "Energiya kvant formulasi?", "a": "e=hf"},
            {"q": "Elektron massasi necha kg?", "a": "9.1e-31"},
            {"q": "Proton massasi necha kg?", "a": "1.67e-27"},
            {"q": "Kvant sonlari nechta?", "a": "4"},
            {"q": "Atom radiusi formulasi?", "a": "rn=n2a0"},
            {"q": "Fotokvadrat effekti kim tomonidan?", "a": "eynshteyn"},
            {"q": "Rektifikasiya nima?", "a": "oqimni ozgartirish"},
            {"q": "Supero'tkazuvchanlik harorati?", "a": "0"},
            {"q": "Kvant sonlari nechta turi?", "a": "4"},
            {"q": "Spin kvant soni nechta?", "a": "2"},
            {"q": "Isomerlar nechta turi?", "a": "2"},
            {"q": "Hund qoidasi nechta?", "a": "3"},
        ],
    },
    "Kimyo": {
        "Oson": [
            {"q": "Suv formulasi nima?", "a": "h2o"}, {"q": "Oksigen belgisi nima?", "a": "o"},
            {"q": "Vodorod belgisi nima?", "a": "h"}, {"q": "Uglerod belgisi nima?", "a": "c"},
            {"q": "Natriy belgisi nima?", "a": "na"}, {"q": "Temir belgisi nima?", "a": "fe"},
            {"q": "Xlor belgisi nima?", "a": "cl"}, {"q": "Kaltsiy belgisi nima?", "a": "ca"},
            {"q": "Magniy belgisi nima?", "a": "mg"}, {"q": "Oltingugurt belgisi nima?", "a": "s"},
            {"q": "Azot belgisi nima?", "a": "n"}, {"q": "Fosfor belgisi nima?", "a": "p"},
            {"q": "Kaliy belgisi nima?", "a": "k"}, {"q": "Aluminiy belgisi nima?", "a": "al"},
            {"q": "Kumush belgisi nima?", "a": "ag"}, {"q": "Oltin belgisi nima?", "a": "au"},
            {"q": "Mis belgisi nima?", "a": "cu"}, {"q": "Sink belgisi nima?", "a": "zn"},
            {"q": "Yod belgisi nima?", "a": "i"}, {"q": "Geliy belgisi nima?", "a": "he"},
            {"q": "Litiy belgisi nima?", "a": "li"}, {"q": "Berilliy belgisi nima?", "a": "be"},
            {"q": "Bor belgisi nima?", "a": "b"}, {"q": "Fluor belgisi nima?", "a": "f"},
            {"q": "Argon belgisi nima?", "a": "ar"},
        ],
        "O'rta": [
            {"q": "Avogadro soni necha?", "a": "6.02e23"},
            {"q": "pH 7 nima anglatadi?", "a": "neytral"},
            {"q": "Kislota + ishqor nima hosil qiladi?", "a": "tuz"},
            {"q": "1 mol gaz STP da necha litr?", "a": "22.4"},
            {"q": "Molyar massaning birligi nima?", "a": "g/mol"},
            {"q": "Kovalent bog nima?", "a": "elektron juftlik"},
            {"q": "Ion bog nima?", "a": "elektron uzatish"},
            {"q": "Eritma foizi formulasi?", "a": "mass/mass*100"},
            {"q": "pH 7 dan kichik nima anglatadi?", "a": "kislota"},
            {"q": "pH 7 dan katta nima anglatadi?", "a": "ishqor"},
            {"q": "Valentlik nima?", "a": "bog soni"},
            {"q": "Reaktsiya turlari nechta?", "a": "4"},
            {"q": "Katalizator nima qiladi?", "a": "tezlatadi"},
            {"q": "Ekzotermik reaktsiya nima?", "a": "issiqlik ajraladi"},
            {"q": "Endotermik reaktsiya nima?", "a": "issiqlik yutadi"},
            {"q": "Kristall panjara turlari nechta?", "a": "4"},
            {"q": "Alkanlar formulasi?", "a": "cnh2n+2"},
            {"q": "Alkenlar formulasi?", "a": "cnh2n"},
            {"q": "Oksidlanish darajasi nima?", "a": "zaryad"},
            {"q": "Mendeleyev jadvali necha elementdan boshlangan?", "a": "63"},
            {"q": "Fe2O3 temir oksid rangi?", "a": "qizil"},
            {"q": "Metal bog qanday?", "a": "metall"},
            {"q": "Vodorod bog nima?", "a": "h bog"},
            {"q": "Molekula massasi formulasi?", "a": "mr"},
            {"q": "Elektr manfiylik osish tartibi?", "a": "chapdan o'ngga"},
        ],
        "Qiyin": [
            {"q": "Gibbs energiyasi formulasi?", "a": "g=h-ts"},
            {"q": "Benzol formulasi nima?", "a": "c6h6"},
            {"q": "R gaz doimiysi necha? (J/mol*K)", "a": "8.314"},
            {"q": "Entalpiya o'zgarishi formulasi?", "a": "dh"},
            {"q": "Le-Shatelier printsipi nima?", "a": "muvozanat"},
            {"q": "Gibbs doimiysi bo'lsa G<0 reaktsiya?", "a": "spontan"},
            {"q": "Arrenius formulasi?", "a": "k=ae-ea/rt"},
            {"q": "Osmotik bosim formulasi?", "a": "pi=icrt"},
            {"q": "Raoult qonuni formulasi?", "a": "p=xp0"},
            {"q": "Nernst tenglamasi?", "a": "e=e0-rtlnq/nf"},
            {"q": "Galvanik element EMF formulasi?", "a": "e=e0-e0"},
            {"q": "Faza diagrammasi nima?", "a": "p-t"},
            {"q": "Izotonik eritma konsentratsiyasi?", "a": "0.9"},
            {"q": "Molyarlik konsentratsiyasi formulasi?", "a": "c=n/v"},
            {"q": "Normallik formulasi?", "a": "cn=n*ekv/v"},
            {"q": "Molekula kinetik nazariya asosi?", "a": "harakat"},
            {"q": "Pauli printsipi nima?", "a": "taqiqlash"},
            {"q": "Gund printsipi nima?", "a": "energiya minimal"},
            {"q": "Hund qoidasi nechta?", "a": "3"},
            {"q": "Isomerlar nechta turi?", "a": "2"},
            {"q": "Van-Hoff faktori formulasi?", "a": "i"},
            {"q": "Kvant sonlari nechta?", "a": "4"},
            {"q": "Spin kvant soni nechta?", "a": "2"},
            {"q": "Polielektron atomlarda?", "a": "klapan"},
            {"q": "Rekombinant DNK texnologiyasi nima?", "a": "gen muhandislik"},
        ],
    },
    "Biologiya": {
        "Oson": [
            {"q": "Hujayraning asosiy qismi nima?", "a": "yadro"},
            {"q": "O'simliklar uchun fotosintez nima qiladi?", "a": "kislorod"},
            {"q": "Insonda nechta suyak bor?", "a": "206"},
            {"q": "Qon guruhlari nechta?", "a": "4"},
            {"q": "DNK to'liq nomi nima?", "a": "dezoksiribonuklein kislota"},
            {"q": "Hujayra qobiqning vazifasi nima?", "a": "himoya"},
            {"q": "Sitoplazma nima?", "a": "hujayra ichi"},
            {"q": "Xloroplast nima qiladi?", "a": "fotosintez"},
            {"q": "Oqsilning asosiy tarkibi nima?", "a": "aminokislota"},
            {"q": "Inson yuragi necha kamerali?", "a": "4"},
            {"q": "O'pka nechta?", "a": "2"},
            {"q": "Buyrak nechta?", "a": "2"},
            {"q": "Jigar necha bo'lakli?", "a": "2"},
            {"q": "Odam nechta xromosomaga ega?", "a": "46"},
            {"q": "O'simlikning yashil rangi nimadan?", "a": "xlorofill"},
            {"q": "Iliq qonli hayvonlarga nima kiradi?", "a": "sut emizuvchi"},
            {"q": "Sovuq qonli hayvonlar nima?", "a": "sudralib yuruvchi"},
            {"q": "Bakteriyalar qanday hujayrali?", "a": "prokariot"},
            {"q": "Zamburug'lar qanday hujayrali?", "a": "eukariot"},
            {"q": "Viruslar hujayralimi?", "a": "yo'q"},
            {"q": "Antitelo nima?", "a": "himoya oqsil"},
            {"q": "Uyqu necha soat bo'lishi kerak?", "a": "8"},
            {"q": "Vitamin C qaysi mevalarda bor?", "a": "sitrus"},
            {"q": "Tishlar nechta?", "a": "32"},
            {"q": "Teri nechta qavat?", "a": "3"},
        ],
        "O'rta": [
            {"q": "Mitoxondriya nima vazifani bajaradi?", "a": "energiya"},
            {"q": "DNK da adenin qaysi bazaga bog'lanadi?", "a": "timin"},
            {"q": "Oqsil sintezi qaysi organoida bo'ladi?", "a": "ribosoma"},
            {"q": "Fotosintez asosiy mahsuloti nima?", "a": "glyukoza"},
            {"q": "Neyron nima?", "a": "nerv hujayrasi"},
            {"q": "Mitoz nechta bosqichdan iborat?", "a": "4"},
            {"q": "Meoz natijasida nechta hujayra hosil bo'ladi?", "a": "4"},
            {"q": "Transkripsiya qayerda bo'ladi?", "a": "yadro"},
            {"q": "Translyatsiya qayerda bo'ladi?", "a": "ribosoma"},
            {"q": "Genetik kod nechta aminokislota?", "a": "20"},
            {"q": "Guanin qaysi bazaga bog'lanadi?", "a": "sitozin"},
            {"q": "RNK turlari nechta?", "a": "3"},
            {"q": "Fagotsit nima?", "a": "yutuvchi hujayra"},
            {"q": "Antigen nima?", "a": "begona modda"},
            {"q": "Ekotizim tarkibiy qismlari?", "a": "biotik abiotik"},
            {"q": "Oziq zanjiri necha bog'lam?", "a": "3-5"},
            {"q": "Simbiot nima?", "a": "hamkorlik"},
            {"q": "Parazitizm nima?", "a": "zararlash"},
            {"q": "Mutatsiya turlari nechta?", "a": "3"},
            {"q": "Dominant gen nima?", "a": "kuchli"},
            {"q": "Resessiv gen nima?", "a": "kuchsiz"},
            {"q": "Genotip nima?", "a": "genlar yig'indisi"},
            {"q": "Fenotip nima?", "a": "tashqi belgilar"},
            {"q": "Allel genlar nima?", "a": "juft genlar"},
            {"q": "Gomozigota nima?", "a": "bir xil allel"},
        ],
        "Qiyin": [
            {"q": "Krebs sikli qaysi organoida bo'ladi?", "a": "mitoxondriya"},
            {"q": "Meyozda nechta bo'linish bo'ladi?", "a": "2"},
            {"q": "ATP to'liq nomi nima?", "a": "adenozintrifosfat"},
            {"q": "Oksidlanish fosforlanish qayerda bo'ladi?", "a": "mitoxondriya"},
            {"q": "Kalvin sikli qayerda bo'ladi?", "a": "xloroplast"},
            {"q": "Lak operon modeli kimniki?", "a": "jakob monod"},
            {"q": "Polimeraza zanjir reaktsiyasi nima?", "a": "pcr"},
            {"q": "Restriktaza nima?", "a": "kesuvchi ferment"},
            {"q": "Ligaza nima?", "a": "biriktiruvchi ferment"},
            {"q": "Plazmid nima?", "a": "kichik dnk"},
            {"q": "Telomeraza nima qiladi?", "a": "uzaytiradi"},
            {"q": "Epigenetika nima?", "a": "gen ifodasi"},
            {"q": "RNA interferens nima?", "a": "gen o'chirish"},
            {"q": "Xromatin nima?", "a": "dnk+protein"},
            {"q": "Giston nima?", "a": "oqsil"},
            {"q": "Nukleosoma nima?", "a": "dnk+giston"},
            {"q": "Poliribosom nima?", "a": "bir nechta ribosoma"},
            {"q": "Okazaki fragmentlari nima?", "a": "dnk bo'lak"},
            {"q": "Primaza nima?", "a": "rna sintez"},
            {"q": "Helikaza nima?", "a": "dnk ochish"},
            {"q": "Sekvensiya nima?", "a": "tartiblash"},
            {"q": "Bioinformatika nima?", "a": "kompyuter biologiya"},
            {"q": "Genetik kod nechta aminokislota kodlaydi?", "a": "20"},
            {"q": "Poydoning xromosomalari nechta?", "a": "46"},
            {"q": "De-Broyl to'lqin uzunligi formulasi?", "a": "h/p"},
        ],
    },
    "Ona tili": {
        "Oson": [
            {"q": "O'zbek tilida nechta unli tovush bor?", "a": "6"},
            {"q": "O'zbek tilida nechta undosh tovush bor?", "a": "24"},
            {"q": "O'zbek alifbosi nechta harfdan iborat?", "a": "29"},
            {"q": "Unli tovushlar qanday hosil bo'ladi?", "a": "ovoz"},
            {"q": "Undosh tovushlar qanday hosil bo'ladi?", "a": "shovqin"},
            {"q": "O'zbek tili qaysi tillar oilasiga kiradi?", "a": "turkiy"},
            {"q": "Fe'l nima?", "a": "harakat"},
            {"q": "Ot nima?", "a": "buyum"},
            {"q": "Sifat nima?", "a": "belgi"},
            {"q": "Son nima?", "a": "miqdor"},
            {"q": "Olmosh nima?", "a": "o'rin"},
            {"q": "Fe'l nima qiladi?", "a": "harakatni bildiradi"},
            {"q": "Gapning asosiy qismlari?", "a": "egaliq kesim"},
            {"q": "Egaliq nima?", "a": "kim nima"},
            {"q": "Kesim nima?", "a": "nima qildi"},
            {"q": "Unsiz gap nima?", "a": "egaliq kesim"},
            {"q": "Sodda gap nima?", "a": "bitta grammatik asos"},
            {"q": "Murakkab gap nima?", "a": "bir nechta sodda gap"},
            {"q": "Qo'shma gap nima?", "a": "bir nechta predikativ qism"},
            {"q": "Uchi nima?", "a": "ot fe'l"},
            {"q": "Bo'g'in nima?", "a": "tovush"},
            {"q": "Bo'g'in turlari nechta?", "a": "3"},
            {"q": "Urg'u nima?", "a": "kuchli o'qish"},
            {"q": "Bosh urg'u qayerda bo'ladi?", "a": "oxirgi bo'g'inda"},
            {"q": "Chaqirim nima?", "a": "so'zning ohangi"},
        ],
        "O'rta": [
            {"q": "Alisher Navoiy qachon tug'ilgan?", "a": "1441"},
            {"q": "Navoiy asari 'Xamsa' nechta doston?", "a": "5"},
            {"q": "O'zbek tilining asosiy shevalari nechta?", "a": "3"},
            {"q": "To'g'ri gap nima?", "a": "kishi uchun gap"},
            {"q": "Inkor gap nima?", "a": "yo'q so'zli"},
            {"q": "So'roq gap nima?", "a": "savol"},
            {"q": "Undalma nima?", "a": "murojaat"},
            {"q": "Modal so'z nima?", "a": "munosabat"},
            {"q": "Kirichi nima?", "a": "to'ldiruvchi"},
            {"q": "Xol nima?", "a": "harakat holati"},
            {"q": "Aniqlowchi nima?", "a": "belgi"},
            {"q": "Toliqlovchi nima?", "a": "miqdor"},
            {"q": "O'zbek yozuvi qachon o'zgartirilgan?", "a": "1940"},
            {"q": "Lotin yozuviga o'tish qachon?", "a": "1993"},
            {"q": "O'zbek tili davlat tili qachon?", "a": "1989"},
            {"q": "Fe'l zamonlari nechta?", "a": "3"},
            {"q": "Hozirgi zamon fe'li qanday?", "a": "-yapman"},
            {"q": "O'tgan zamon fe'li qanday?", "a": "-dim"},
            {"q": "Kelasi zamon fe'li qanday?", "a": "-yman"},
            {"q": "Shakldosh nima?", "a": "fe'l shakli"},
            {"q": "Ravish nima?", "a": "harakat belgisi"},
            {"q": "Ravish turlari nechta?", "a": "5"},
            {"q": "Aloqador gap nima?", "a": "bog'lovchi"},
            {"q": "Bog'lovchi so'zlar nima?", "a": "va lekin ammo"},
            {"q": "Yordamchi fe'llar nechta?", "a": "5"},
        ],
        "Qiyin": [
            {"q": "Navoiy 'Muxokamot ul-lug'atayn' asarida nima haqida?", "a": "til"},
            {"q": "Babur 'Boburnoma' asarida nima haqida?", "a": "tarix"},
            {"q": "Furqat qachon tug'ilgan?", "a": "1858"},
            {"q": "Cho'lpon qachon tug'ilgan?", "a": "1897"},
            {"q": "Qodiriy qachon tug'ilgan?", "a": "1893"},
            {"q": "Hamza qachon tug'ilgan?", "a": "1889"},
            {"q": "Oybek qachon tug'ilgan?", "a": "1905"},
            {"q": "G'afur G'ulom qachon tug'ilgan?", "a": "1903"},
            {"q": "Zulfiya qachon tug'ilgan?", "a": "1915"},
            {"q": "Abdulla Qahhor qachon tug'ilgan?", "a": "1907"},
            {"q": "Said Ahmad qachon tug'ilgan?", "a": "1920"},
            {"q": "Hoji Abdulholiq G'ijduvoniy qachon yashagan?", "a": "12"},
            {"q": "Bahouddin Naqshband qachon yashagan?", "a": "14"},
            {"q": "Alisher Navoiy qachon vafot etgan?", "a": "1501"},
            {"q": "'Kecha va Kunduz' romanining muallifi kim?", "a": "cho'lpon"},
            {"q": "'O'tkan kunlar' romanining muallifi kim?", "a": "qodiriy"},
            {"q": "'Ming bir kecha' asari qaysi xalq?", "a": "arab"},
            {"q": "'Kalila va Dimna' asari qaysi xalq?", "a": "hind"},
            {"q": "'Shohnoma' asarining muallifi kim?", "a": "firdavsi"},
            {"q": "Qofiya nima?", "a": "ohangdos so'zlar"},
            {"q": "Vazn nima?", "a": "bo'g'in tuzilishi"},
            {"q": "Bahr nima?", "a": "she'r o'lchami"},
            {"q": "Aruz vazni necha turi?", "a": "8"},
            {"q": "She'riyatda band nima?", "a": "misralar guruhi"},
            {"q": "Navro'z she'ridan olingan misra?", "a": "navro'z"},
        ],
    },
    "Ingliz tili": {
        "Oson": [
            {"q": "'Hello' o'zbekcha nima?", "a": "salom"},
            {"q": "'Thank you' o'zbekcha nima?", "a": "rahmat"},
            {"q": "'Good morning' o'zbekcha nima?", "a": "xayrli tong"},
            {"q": "'Goodbye' o'zbekcha nima?", "a": "xayr"},
            {"q": "'Please' o'zbekcha nima?", "a": "iltimos"},
            {"q": "'Yes' o'zbekcha nima?", "a": "ha"},
            {"q": "'No' o'zbekcha nima?", "a": "yo'q"},
            {"q": "'Water' o'zbekcha nima?", "a": "suv"},
            {"q": "'Book' o'zbekcha nima?", "a": "kitob"},
            {"q": "'School' o'zbekcha nima?", "a": "maktab"},
            {"q": "'Teacher' o'zbekcha nima?", "a": "o'qituvchi"},
            {"q": "'Student' o'zbekcha nima?", "a": "o'quvchi"},
            {"q": "'Mother' o'zbekcha nima?", "a": "ona"},
            {"q": "'Father' o'zbekcha nima?", "a": "ota"},
            {"q": "'Friend' o'zbekcha nima?", "a": "do'st"},
            {"q": "'Apple' o'zbekcha nima?", "a": "olma"},
            {"q": "'House' o'zbekcha nima?", "a": "uy"},
            {"q": "'Cat' o'zbekcha nima?", "a": "mushuk"},
            {"q": "'Dog' o'zbekcha nima?", "a": "it"},
            {"q": "'Sun' o'zbekcha nima?", "a": "quyosh"},
            {"q": "'Moon' o'zbekcha nima?", "a": "oy"},
            {"q": "'Star' o'zbekcha nima?", "a": "yulduz"},
            {"q": "'Food' o'zbekcha nima?", "a": "ovqat"},
            {"q": "'Name' o'zbekcha nima?", "a": "ism"},
            {"q": "'Day' o'zbekcha nima?", "a": "kun"},
        ],
        "O'rta": [
            {"q": "Present Simple qachon ishlatiladi?", "a": "har kuni"},
            {"q": "Past Simple qachon ishlatiladi?", "a": "o'tgan"},
            {"q": "Future Simple qachon ishlatiladi?", "a": "kelajak"},
            {"q": "Present Continuous formulasi?", "a": "am is are + v-ing"},
            {"q": "Past Continuous formulasi?", "a": "was were + v-ing"},
            {"q": "Irregular verbs nechta?", "a": "200"},
            {"q": "Regular verbs qanday hosil bo'ladi?", "a": "ed"},
            {"q": "Article turlari nechta?", "a": "2"},
            {"q": "'A' article qachon ishlatiladi?", "a": "bosh undosh"},
            {"q": "'An' article qachon ishlatiladi?", "a": "bosh unli"},
            {"q": "'The' article qachon ishlatiladi?", "a": "aniq"},
            {"q": "Modal verb lar nechta?", "a": "9"},
            {"q": "'Can' modal verb nima qiladi?", "a": "qila olaman"},
            {"q": "'Must' modal verb nima qiladi?", "a": "shart"},
            {"q": "'Should' modal verb nima qiladi?", "a": "maslahat"},
            {"q": "Passive voice formulasi?", "a": "be + v3"},
            {"q": "Reported speech nima?", "a": "bilvosita gap"},
            {"q": "Conditionals nechta turi?", "a": "4"},
            {"q": "If clause + main clause nima?", "a": "shart gap"},
            {"q": "Comparative adjective qanday?", "a": "er"},
            {"q": "Superlative adjective qanday?", "a": "est"},
            {"q": "Countable nouns nima?", "a": "sanaluvchi"},
            {"q": "Uncountable nouns nima?", "a": "sanalmaydigan"},
            {"q": "Prepositions nima?", "a": "old kelgichi"},
            {"q": "Conjunctions nima?", "a": "bog'lovchi"},
        ],
        "Qiyin": [
            {"q": "Present Perfect formulasi?", "a": "have has + v3"},
            {"q": "Past Perfect formulasi?", "a": "had + v3"},
            {"q": "Future Perfect formulasi?", "a": "will have + v3"},
            {"q": "Present Perfect Continuous formulasi?", "a": "have been + v-ing"},
            {"q": "Past Perfect Continuous formulasi?", "a": "had been + v-ing"},
            {"q": "Future Continuous formulasi?", "a": "will be + v-ing"},
            {"q": "Subjunctive mood nima?", "a": "istak"},
            {"q": "Gerund nima?", "a": "v-ing ot"},
            {"q": "Infinitive nima?", "a": "to + v"},
            {"q": "Participle nima?", "a": "sifetdosh"},
            {"q": "Relative clauses nima?", "a": "bog'lovchi gap"},
            {"q": "Defining relative clause nima?", "a": "aniqlovchi"},
            {"q": "Non-defining relative clause nima?", "a": "qo'shimcha"},
            {"q": "Causative form formulasi?", "a": "have + object + v3"},
            {"q": "Wish formulasi?", "a": "wish + past"},
            {"q": "Used to formulasi?", "a": "used to + v"},
            {"q": "Be used to formulasi?", "a": "be used to + v-ing"},
            {"q": "Get used to formulasi?", "a": "get used to + v-ing"},
            {"q": "Inversion nima?", "a": "tartib o'zgarishi"},
            {"q": "Emphasis nima?", "a": "kuchaytirish"},
            {"q": "Phrasal verbs nechta?", "a": "5000"},
            {"q": "Idioms nima?", "a": "o'takma gap"},
            {"q": "Collocation nima?", "a": "birga keluvchi so'z"},
            {"q": "Discourse markers nima?", "a": "matn bog'lovchi"},
            {"q": "Cohesion nima?", "a": "matn uzviyligi"},
        ],
    },
    "Tarix": {
        "Oson": [
            {"q": "O'zbekiston mustaqillik kuni qachon?", "a": "1 sentyabr"},
            {"q": "O'zbekiston poytaxti qayer?", "a": "toshkent"},
            {"q": "Temuriylar imperiyasining asoschisi kim?", "a": "amir temur"},
            {"q": "Amir Temur qachon tug'ilgan?", "a": "1336"},
            {"q": "O'zbekiston konstitutsiyasi qachon qabul qilingan?", "a": "1992"},
            {"q": "Ipak yo'li nima?", "a": "savdo yo'l"},
            {"q": "Samarqand qanday shahar?", "a": "qadimiy"},
            {"q": "Buxoro qanday shahar?", "a": "qadimiy"},
            {"q": "Xiva qanday shahar?", "a": "qadimiy"},
            {"q": "O'zbek tili davlat tili qachon?", "a": "1989"},
            {"q": "O'zbekiston bayrog'i ranglari nechta?", "a": "3"},
            {"q": "O'zbekiston gerbi nima bor?", "a": "humo"},
            {"q": "O'zbekiston madhiyasi muallifi kim?", "a": "sulaymon"},
            {"q": "Ikkinchi jahon urushi qachon tugagan?", "a": "1945"},
            {"q": "Birinchi jahon urushi qachon boshlangan?", "a": "1914"},
            {"q": "Sovet Ittifoqi qachon tuzilgan?", "a": "1922"},
            {"q": "Sovet Ittifoqi qachon tugagan?", "a": "1991"},
            {"q": "Ulug'bek qanday olim?", "a": "astronom"},
            {"q": "Al-Xorazmiy qanday olim?", "a": "matematik"},
            {"q": "Ibn Sino qanday olim?", "a": "tabib"},
            {"q": "Beruniy qanday olim?", "a": "olim"},
            {"q": "O'zbekiston aholisi necha million?", "a": "36"},
            {"q": "O'zbekiston viloyatlari nechta?", "a": "12"},
            {"q": "O'zbekiston respublika qachon?", "a": "1991"},
            {"q": "Yerning tabiiy yo'ldoshi nima?", "a": "oy"},
        ],
        "O'rta": [
            {"q": "Amir Temur qachon vafot etgan?", "a": "1405"},
            {"q": "Temuriylar imperiyasi poytaxti qayer?", "a": "samarqand"},
            {"q": "Shayboniylar davlati qachon tuzilgan?", "a": "1500"},
            {"q": "Xonliklar davri qachon boshlangan?", "a": "18"},
            {"q": "Qo'qon xonligi qachon tuzilgan?", "a": "1709"},
            {"q": "Xiva xonligi qachon tuzilgan?", "a": "1511"},
            {"q": "Buxoro amirligi qachon tuzilgan?", "a": "1753"},
            {"q": "Rossiya imperiyasi O'rta Osiyoni qachon egallagan?", "a": "1865"},
            {"q": "Jadidchilik harakati qachon boshlangan?", "a": "19"},
            {"q": "O'zbekiston SSR qachon tuzilgan?", "a": "1924"},
            {"q": "Mustaqillik e'lon qilingan sana?", "a": "31 avgust 1991"},
            {"q": "O'zbekiston BMTga qachon a'zo bo'lgan?", "a": "1992"},
            {"q": "Islom dini qachon paydo bo'lgan?", "a": "7"},
            {"q": "Kushonlar davlati qachon?", "a": "1-3"},
            {"q": "Arablarning O'rta Osiyaga yurishi qachon?", "a": "8"},
            {"q": "Samanlar davlati qachon?", "a": "9-10"},
            {"q": "Qoraxoniylar davlati qachon?", "a": "10-13"},
            {"q": "Mo'g'ullar istilosi qachon?", "a": "13"},
            {"q": "Ulug'bek rasadxonasi qayerda?", "a": "samarqand"},
            {"q": "Mirzo Ulug'bek qachon tug'ilgan?", "a": "1394"},
            {"q": "Al-Xorazmiy qachon yashagan?", "a": "9"},
            {"q": "Sosoniylar davlati qayerda?", "a": "eron"},
            {"q": "Chig'atoy ulusi qachon?", "a": "13-14"},
            {"q": "Zardushtiylik qanday din?", "a": "otga sig'inish"},
            {"q": "Buddizm qanday din?", "a": "xotirjalik"},
        ],
        "Qiyin": [
            {"q": "Temuriylar saltanati qachon tugagan?", "a": "1507"},
            {"q": "Shayboniylar qachon hokimiyatni qo'lga olgan?", "a": "1500"},
            {"q": "Jadidlar harakatining asoschisi kim?", "a": "behbudiy"},
            {"q": "Behbudiy qachon shahid bo'lgan?", "a": "1919"},
            {"q": "Islom Karimov qachon prezident bo'lgan?", "a": "1991"},
            {"q": "O'zbekiston MDHga a'zo bo'lganmi?", "a": "ha"},
            {"q": "Shangtou shartnomasi qachon?", "a": "2001"},
            {"q": "OTM Tashkent shartnomasi tuzilgan sana?", "a": "1992"},
            {"q": "Suyun qo'zg'oloni qachon bo'lgan?", "a": "1916"},
            {"q": "Chor Rossiyaning Turkiston general-gubernatorligi qachon?", "a": "1867"},
            {"q": "Turkiston Muxtoriyati qachon e'lon qilingan?", "a": "1917"},
            {"q": "Buxoro inqilobi qachon?", "a": "1920"},
            {"q": "Xiva inqilobi qachon?", "a": "1920"},
            {"q": "Milliy hududiy chegaralanish qachon?", "a": "1924"},
            {"q": "O'zbekiston yangi konstitutsiyasi qachon?", "a": "2022"},
            {"q": "Qoraqalpog'iston Respublikasi qachon tuzilgan?", "a": "1936"},
            {"q": "Navoiy viloyati qachon tuzilgan?", "a": "1982"},
            {"q": "Sirdaryo viloyati qachon tuzilgan?", "a": "1963"},
            {"q": "Jizzax viloyati qachon tuzilgan?", "a": "1973"},
            {"q": "Seldjuqiylar davlati qachon?", "a": "11-14"},
            {"q": "Anushlar davlati qachon hukm surgan?", "a": "11-12"},
            {"q": "Qo'qon xonligining so'nggi xoni kim?", "a": "xudoyor"},
            {"q": "O'zbekiston demokratik yo'l bilan qachon o'tgan?", "a": "1991"},
            {"q": "O'zbekiston strategik rivojlanish konsepsiyasi qachon?", "a": "2017"},
            {"q": "O'zbekiston necha mamlakat bilan hamkorlik qiladi?", "a": "140"},
        ],
    },
    "Geografiya": {
        "Oson": [
            {"q": "O'zbekiston qaysi qit'ada?", "a": "osiy"},
            {"q": "O'zbekiston poytaxti qayer?", "a": "toshkent"},
            {"q": "Eng katta daryo O'zbekistonda?", "a": "amudaryo"},
            {"q": "Qizilqum nima?", "a": "cho'l"},
            {"q": "O'zbekiston iqlimi qanday?", "a": "keskin kontinental"},
            {"q": "Yozda harorat necha gradus?", "a": "45"},
            {"q": "Sirdaryo qayerdan oqadi?", "a": "tyan-shan"},
            {"q": "Amudaryo qayerdan oqadi?", "a": "pomir"},
            {"q": "O'zbekiston aholisi necha million?", "a": "36"},
            {"q": "Toshkent aholisi necha million?", "a": "3"},
            {"q": "O'zbekiston maydoni necha ming km2?", "a": "448"},
            {"q": "Ty'an-Shan tog'lari qayerda?", "a": "sharq"},
            {"q": "Pomir tog'lari qayerda?", "a": "janub"},
            {"q": "Ustyurt platosi qayerda?", "a": "g'arb"},
            {"q": "O'zbekiston necha viloyat?", "a": "12"},
            {"q": "Qoraqalpog'iston nima?", "a": "respublika"},
            {"q": "Samarqand aholisi necha million?", "a": "4"},
            {"q": "Buxoro aholisi necha million?", "a": "2"},
            {"q": "Namangan viloyati qayerda?", "a": "shimol-sharq"},
            {"q": "Surxondaryo viloyati qayerda?", "a": "janub"},
            {"q": "O'zbekistonning eng baland nuqtasi?", "a": "xazon"},
            {"q": "Eng katta ko'l O'zbekistonda?", "a": "oroldengiz"},
            {"q": "Qishda harorat necha gradus?", "a": "-20"},
            {"q": "Farg'ona vodiysi nima?", "a": "o'simlik"},
            {"q": "O'zbekiston poytaxti qayer?", "a": "toshkent"},
        ],
        "O'rta": [
            {"q": "O'zbekistonning tabiiy resurslari nima?", "a": "oltin gaz neft"},
            {"q": "Oltin zaxiralari bo'yicha O'zbekiston nechinchi?", "a": "10"},
            {"q": "Muruntov oltin koni qayerda?", "a": "navoiy"},
            {"q": "Shurtan gaz koni qayerda?", "a": "qashqadaryo"},
            {"q": "Farg'ona vodiy necha viloyatdan iborat?", "a": "3"},
            {"q": "Qoraqalpog'iston maydoni necha ming km2?", "a": "166"},
            {"q": "Amudaryo uzunligi necha km?", "a": "2540"},
            {"q": "Sirdaryo uzunligi necha km?", "a": "2137"},
            {"q": "Orol dengizi maydoni qanday o'zgarib borayotgan?", "a": "qisqarib"},
            {"q": "Orol dengizi muammosi qachon boshlangan?", "a": "1960"},
            {"q": "Chirchiq daryosi qayerdan oqadi?", "a": "tyan-shan"},
            {"q": "Zarafshon daryosi qayerdan oqadi?", "a": "zamin"},
            {"q": "O'zbekiston iqlimi qanday o'zgarib borayotgan?", "a": "issiqlash"},
            {"q": "O'zbekiston o'simlik dunyosi nechta turi?", "a": "5"},
            {"q": "Cho'l zonasi qaysi viloyatlarda?", "a": "buxoro navoiy"},
            {"q": "Tog' zonasi qaysi viloyatlarda?", "a": "surxondaryo qashqadaryo"},
            {"q": "O'zbekiston transport turlari nechta?", "a": "5"},
            {"q": "Toshkent metropoliteni qachon ochilgan?", "a": "1977"},
            {"q": "Toshkent metropoliteni necha liniya?", "a": "3"},
            {"q": "O'zbekiston temir yo'l uzunligi necha km?", "a": "6000"},
            {"q": "Toshkent aeroporti nomi nima?", "a": "islom karimov"},
            {"q": "Gaz zaxiralari bo'yicha O'zbekiston nechinchi?", "a": "15"},
            {"q": "Sirdaryo viloyati qachon tuzilgan?", "a": "1963"},
            {"q": "Tog' oldi zonasi qaysi viloyatlarda?", "a": "toshkent namangan"},
            {"q": "Farg'ona vodiysi qaysi viloyatlar?", "a": "farg'ona andijon namangan"},
        ],
        "Qiyin": [
            {"q": "Orol muammosining asosiy sababi nima?", "a": "suv ishlatish"},
            {"q": "Orol dengizini qayta tiklash dasturi qachon boshlangan?", "a": "2018"},
            {"q": "O'zbekiston suv resurslari necha km3?", "a": "50"},
            {"q": "Amudaryoning o'rtacha suv sarfi necha m3/s?", "a": "2000"},
            {"q": "Sirdaryoning o'rtacha suv sarfi necha m3/s?", "a": "500"},
            {"q": "O'zbekistonda necha turdagi tuproq bor?", "a": "12"},
            {"q": "Bo'z tuproqlar qaysi zonada?", "a": "cho'l"},
            {"q": "O'tloqi tuproqlar qaysi zonada?", "a": "tog' oldi"},
            {"q": "O'zbekiston o'rmon maydoni necha %?", "a": "7"},
            {"q": "Ty'an-Shan tog'lari balandligi necha m?", "a": "7439"},
            {"q": "Pomir tog'lari balandligi necha m?", "a": "7495"},
            {"q": "G'issar tizmasi balandligi necha m?", "a": "4643"},
            {"q": "Chatqal tizmasi balandligi necha m?", "a": "4503"},
            {"q": "O'zbekiston aholi soni o'sishi necha %?", "a": "2"},
            {"q": "Shahar aholisi ulushi necha %?", "a": "51"},
            {"q": "Qishloq aholisi ulushi necha %?", "a": "49"},
            {"q": "O'zbekiston EKI bo'yicha nechinchi o'rinda?", "a": "85"},
            {"q": "Oltin qazib olish bo'yicha O'zbekiston nechinchi?", "a": "10"},
            {"q": "Uran qazib olish bo'yicha O'zbekiston nechinchi?", "a": "7"},
            {"q": "Mis qazib olish bo'yicha O'zbekiston nechinchi?", "a": "12"},
            {"q": "O'zbekiston nechta iqlim zonasida joylashgan?", "a": "3"},
            {"q": "O'zbekiston nechta tabiat qo'riqxonasi bor?", "a": "8"},
            {"q": "O'zbekiston tabiiy sharoitini ta'sir etuvchi omillar nechta?", "a": "4"},
            {"q": "K global harorat ko'tarilishi O'zbekistonga ta'siri?", "a": "issiqlash"},
            {"q": "O'zbekiston necha mamlakat bilan hamkorlik qiladi?", "a": "140"},
        ],
    },
    "Informatika": {
        "Oson": [
            {"q": "Kompyuter nima?", "a": "hisoblash"},
            {"q": "CPU nima?", "a": "protsessor"},
            {"q": "RAM nima?", "a": "operativ xotira"},
            {"q": "HDD nima?", "a": "qattiq disk"},
            {"q": "SSD nima?", "a": "qattiq disk"},
            {"q": "Monitor nima?", "a": "ekran"},
            {"q": "Klaviatura nima?", "a": "kitob kiritish"},
            {"q": "Sichqoncha nima?", "a": "ko'rsatkich"},
            {"q": "Printer nima?", "a": "chop etish"},
            {"q": "Internet nima?", "a": "tarmoq"},
            {"q": "Wi-Fi nima?", "a": "simsiz tarmoq"},
            {"q": "Bluetooth nima?", "a": "simsiz ulanish"},
            {"q": "USB nima?", "a": "universal shina"},
            {"q": "Operatsion sistema nima?", "a": "tizim dastur"},
            {"q": "Windows nima?", "a": "operatsion sistema"},
            {"q": "Linux nima?", "a": "operatsion sistema"},
            {"q": "Fayl nima?", "a": "ma'lumot"},
            {"q": "Papka nima?", "a": "fayl joyi"},
            {"q": "Dastur nima?", "a": "ko'rsatmalar"},
            {"q": "Virus nima?", "a": "zararli dastur"},
            {"q": "Antivirus nima?", "a": "himoya dastur"},
            {"q": "Email nima?", "a": "elektron pochta"},
            {"q": "Brauzer nima?", "a": "internet dastur"},
            {"q": "Sayt nima?", "a": "web sahifa"},
            {"q": "Parol nima?", "a": "maxfiy so'z"},
        ],
        "O'rta": [
            {"q": "Binary sistema nechta raqamdan iborat?", "a": "2"},
            {"q": "1 bayt necha bit?", "a": "8"},
            {"q": "1 kilobayt necha bayt?", "a": "1024"},
            {"q": "1 megabayt necha kilobayt?", "a": "1024"},
            {"q": "1 gigabayt necha megabayt?", "a": "1024"},
            {"q": "HTML nima?", "a": "web til"},
            {"q": "CSS nima?", "a": "stil til"},
            {"q": "JavaScript nima?", "a": "skript til"},
            {"q": "Python nima?", "a": "dasturlash tili"},
            {"q": "Algoritm nima?", "a": "harakatlar ketma-ketligi"},
            {"q": "Sikl nima?", "a": "takrorlash"},
            {"q": "Shartli operator nima?", "a": "if"},
            {"q": "O'zgaruvchi nima?", "a": "qiymat saqlash"},
            {"q": "Massiv nima?", "a": "elementlar to'plami"},
            {"q": "Funksiya nima?", "a": "kichik dastur"},
            {"q": "IP manzil nima?", "a": "tarmoq manzil"},
            {"q": "DNS nima?", "a": "domen nom tizimi"},
            {"q": "HTTP nima?", "a": "web protokol"},
            {"q": "HTTPS nima?", "a": "xavfsiz protokol"},
            {"q": "Server nima?", "a": "xizmat ko'rsatuvchi"},
            {"q": "Mijoz nima?", "a": "foydalanuvchi"},
            {"q": "Ma'lumotlar bazasi nima?", "a": "malumotlar to'plami"},
            {"q": "SQL nima?", "a": "so'rov tili"},
            {"q": "API nima?", "a": "dastur interfeys"},
            {"q": "Git nima?", "a": "versiya boshqaru"},
        ],
        "Qiyin": [
            {"q": "Big O notatsiyasi nima?", "a": "murakkablik"},
            {"q": "O(1) murakkablik nima?", "a": "doimiy"},
            {"q": "O(n) murakkablik nima?", "a": "chiziqli"},
            {"q": "O(log n) murakkablik nima?", "a": "logarifmik"},
            {"q": "O(n^2) murakkablik nima?", "a": "kvadratik"},
            {"q": "Rekursiya nima?", "a": "o'z-o'ziga murojaat"},
            {"q": "Bubble sort murakkabligi?", "a": "o(n2)"},
            {"q": "Quick sort murakkabligi?", "a": "o(n log n)"},
            {"q": "Merge sort murakkabligi?", "a": "o(n log n)"},
            {"q": "Binariy qidiruv murakkabligi?", "a": "o(log n)"},
            {"q": "Chiziqli qidiruv murakkabligi?", "a": "o(n)"},
            {"q": "Graf algoritmlari nima?", "a": "tarmoq"},
            {"q": "BFS algoritmi nima?", "a": "kenglik bo'yicha"},
            {"q": "DFS algoritmi nima?", "a": "chuqurligi bo'yicha"},
            {"q": "Dijkstra algoritmi nima?", "a": "eng qisqa yo'l"},
            {"q": "DP Dinamik dasturlash nima?", "a": "kichik muammolar"},
            {"q": "Hash jadval murakkabligi?", "a": "o(1)"},
            {"q": "Stek nima?", "a": "lifo"},
            {"q": "Navbat nima?", "a": "fifo"},
            {"q": "Draxma nima?", "a": "daraxt"},
            {"q": "Graf nima?", "a": "tugunlar"},
            {"q": "SUN nima?", "a": "tarmoq qobiq"},
            {"q": "TCP/IP nima?", "a": "internet protokol"},
            {"q": "MVC nima?", "a": "model view controller"},
            {"q": "Saralash algoritmlari nechta?", "a": "10"},
        ],
    },
    "Adabiyot": {
        "Oson": [
            {"q": "Alisher Navoiy kim?", "a": "shoir"},
            {"q": "Navoiy qachon tug'ilgan?", "a": "1441"},
            {"q": "'Xamsa' asari nechta doston?", "a": "5"},
            {"q": "Lutfiy kim?", "a": "shoir"},
            {"q": "Babur kim?", "a": "shoir va hukmdor"},
            {"q": "Cho'lpon kim?", "a": "shoir"},
            {"q": "Hamza kim?", "a": "yozuvchi"},
            {"q": "Qodiriy kim?", "a": "yozuvchi"},
            {"q": "Oybek kim?", "a": "yozuvchi"},
            {"q": "G'afur G'ulom kim?", "a": "shoir"},
            {"q": "Zulfiya kim?", "a": "shoir"},
            {"q": "She'r nima?", "a": "she'riy asar"},
            {"q": "Doston nima?", "a": "katta she'r"},
            {"q": "Qissa nima?", "a": "qisqa hikoya"},
            {"q": "Roman nima?", "a": "katta nasriy asar"},
            {"q": "Hikoya nima?", "a": "kichik nasriy asar"},
            {"q": "Pyesa nima?", "a": "sahnalashtirish"},
            {"q": "Ertak nima?", "a": "badiiy asar"},
            {"q": "Maqol nima?", "a": "xalq donishmandligi"},
            {"q": "Topishmoq nima?", "a": "savol o'yin"},
            {"q": "Qo'shiq nima?", "a": "musiqiy asar"},
            {"q": "Muallif nima?", "a": "yaratuvchi"},
            {"q": "Qahramon nima?", "a": "asosiy shaxs"},
            {"q": "Sujet nima?", "a": "voqealar ketma-ketligi"},
            {"q": "G'oya nima?", "a": "asosiy fikr"},
        ],
        "O'rta": [
            {"q": "Navoiy 'Xamsa' asari qaysi tillarda?", "a": "fors"},
            {"q": "'Muxokamot ul-lug'atayn' nima haqida?", "a": "til"},
            {"q": "'Boburnoma' asari qanday janrda?", "a": "memuar"},
            {"q": "'O'tkan kunlar' muallifi kim?", "a": "qodiriy"},
            {"q": "'Kecha va Kunduz' muallifi kim?", "a": "cho'lpon"},
            {"q": "'Sarob' asari muallifi kim?", "a": "cho'lpon"},
            {"q": "'Navro'z' she'ri muallifi kim?", "a": "navoiy"},
            {"q": "'Qutadgubilig' asari muallifi kim?", "a": "yusuf xos hojib"},
            {"q": "'Hibat ul-haqoyiq' asari muallifi kim?", "a": "axmad yugnakiy"},
            {"q": "Raqim nima?", "a": "ovozli o'qish"},
            {"q": "Tanqidiy realizm nima?", "a": "tanqidiy yo'nalish"},
            {"q": "Sotsialistik realizm nima?", "a": "sovet yo'nalish"},
            {"q": "Mustaqillik adabiyoti qachon boshlangan?", "a": "1991"},
            {"q": "Usmon Nosir kim?", "a": "shoir"},
            {"q": "Usmon Nosir qachon tug'ilgan?", "a": "1912"},
            {"q": "Mirmuhsin kim?", "a": "yozuvchi"},
            {"q": "Shukrullo kim?", "a": "yozuvchi"},
            {"q": "Said Ahmad kim?", "a": "yozuvchi"},
            {"q": "Abdulla Qahhor kim?", "a": "yozuvchi"},
            {"q": "G'afur G'ulom qachon tug'ilgan?", "a": "1903"},
            {"q": "Hamza qachon tug'ilgan?", "a": "1889"},
            {"q": "Cho'lpon qachon tug'ilgan?", "a": "1897"},
            {"q": "Qodiriy qachon tug'ilgan?", "a": "1893"},
            {"q": "Oripov kim?", "a": "shoir"},
            {"q": "Toshmatov kim?", "a": "shoir"},
        ],
        "Qiyin": [
            {"q": "'Lison ut-tayr' dostonining mazmuni nima?", "a": "ruhiy sayohat"},
            {"q": "'Sabbai Sayyor' dostonining mazmuni?", "a": "7 sayyora"},
            {"q": "'Hayrat ul-abror' dostonining mazmuni?", "a": "odob-axloq"},
            {"q": "'Farhod va Shirin' dostoni nima haqida?", "a": "sevgi"},
            {"q": "'Layli va Majnun' dostoni nima haqida?", "a": "sevgi"},
            {"q": "'Sab'ai Sayyor' muallifi kim?", "a": "navoiy"},
            {"q": "Babur 'Boburnoma' asarida nima haqida?", "a": "tarix"},
            {"q": "Mashrab kim?", "a": "shoir"},
            {"q": "Mashrab qachon yashagan?", "a": "17"},
            {"q": "Nodira kim?", "a": "shoira"},
            {"q": "Nodira qachon yashagan?", "a": "19"},
            {"q": "Uvaysiy kim?", "a": "shoira"},
            {"q": "Muqimiy kim?", "a": "shoir"},
            {"q": "Zavqiy kim?", "a": "shoir"},
            {"q": "Furqat qachon tug'ilgan?", "a": "1858"},
            {"q": "Ogahiy kim?", "a": "shoir"},
            {"q": "Ogahiy qachon yashagan?", "a": "19"},
            {"q": "Avtobiografiya nima?", "a": "o'z hayoti haqida"},
            {"q": "Memuar nima?", "a": "xotiralar"},
            {"q": "Pamflet nima?", "a": "tanqidiy maqola"},
            {"q": "Felyeton nima?", "a": "hazil maqola"},
            {"q": "Ocherk nima?", "a": "hujjatli hikoya"},
            {"q": "Navoiy 'Bedor zig' dasarchiligi kimniki?", "a": "navoiy"},
            {"q": "'Sadriya firdavsiya' dostoni muallifi?", "a": "navoiy"},
            {"q": "Ozod Shirinuho'glisi kim?", "a": "shoir"},
        ],
    },
}

# ===== HELPER FUNCTIONS =====
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'users': [],
        'schedules': {},
        'attendance': [],
        'support_messages': [],
        'teacher_attendance': [],
        'comments': [],
    }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_custom_questions():
    if os.path.exists(CUSTOM_QUESTIONS_FILE):
        with open(CUSTOM_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_custom_questions(qdata):
    with open(CUSTOM_QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(qdata, f, ensure_ascii=False, indent=2)

def get_all_questions(subject, level):
    builtin = QUESTION_BANK.get(subject, {}).get(level, [])
    custom = load_custom_questions().get(subject, {}).get(level, [])
    return builtin + custom

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('index'))
            if session['user']['role'] != role:
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ===== ROUTES =====

# --- Index / Login ---
@app.route('/')
def index():
    if 'user' in session:
        if session['user']['role'] == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        return redirect(url_for('student_dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        data = load_data()
        pw_hash = hash_password(password)
        for u in data['users']:
            if u['username'] == username and u['password_hash'] == pw_hash:
                session['user'] = {'username': u['username'], 'role': u['role'], 'name': u.get('name', username)}
                if u['role'] == 'teacher':
                    return redirect(url_for('teacher_dashboard'))
                return redirect(url_for('student_dashboard'))
        flash("Login yoki parol noto'g'ri!", 'error')
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# ===== TEACHER ROUTES =====

@app.route('/teacher/dashboard')
@role_required('teacher')
def teacher_dashboard():
    return render_template('teacher/dashboard.html', subjects=SUBJECTS, subject_icons=SUBJECT_ICONS)

@app.route('/teacher/students')
@role_required('teacher')
def teacher_students():
    data = load_data()
    students = [u for u in data['users'] if u['role'] == 'student']
    return render_template('teacher/students.html', students=students)

@app.route('/teacher/create-student', methods=['GET', 'POST'])
@role_required('teacher')
def teacher_create_student():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        name = request.form.get('name', '').strip()
        student_class = request.form.get('class', '').strip()
        if not username or not password:
            flash("Login va parol kiritilishi shart!", 'error')
            return redirect(url_for('teacher_create_student'))
        data = load_data()
        if any(u['username'] == username for u in data['users']):
            flash("Bu login bilan o'quvchi allaqachon mavjud!", 'error')
            return redirect(url_for('teacher_create_student'))
        data['users'].append({
            'username': username,
            'password_hash': hash_password(password),
            'role': 'student',
            'name': name or username,
            'class': student_class,
            'created_at': datetime.now().isoformat(),
        })
        save_data(data)
        flash(f"O'quvchi '{name or username}' muvaffaqiyatli qo'shildi!", 'success')
        return redirect(url_for('teacher_students'))
    return render_template('teacher/create_student.html')

@app.route('/teacher/student/delete/<username>', methods=['POST'])
@role_required('teacher')
def teacher_delete_student(username):
    data = load_data()
    data['users'] = [u for u in data['users'] if not (u['username'] == username and u['role'] == 'student')]
    save_data(data)
    flash(f"O'quvchi '{username}' o'chirildi.", 'success')
    return redirect(url_for('teacher_students'))

# --- Schedule ---
@app.route('/teacher/schedule', methods=['GET', 'POST'])
@role_required('teacher')
def teacher_schedule():
    data = load_data()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            day = request.form.get('day')
            period = request.form.get('period')
            subject = request.form.get('subject')
            if day and period and subject:
                if day not in data['schedules']:
                    data['schedules'][day] = {}
                data['schedules'][day][period] = subject
                save_data(data)
        elif action == 'delete':
            day = request.form.get('day')
            period = request.form.get('period')
            if day in data['schedules'] and period in data['schedules'][day]:
                del data['schedules'][day][period]
                save_data(data)
        return redirect(url_for('teacher_schedule'))
    return render_template('teacher/schedule.html', schedules=data.get('schedules', {}), days=DAYS, periods=PERIODS, subjects=SUBJECTS, subject_colors=SUBJECT_COLORS, subject_icons=SUBJECT_ICONS)

# --- Comments / Notes ---
@app.route('/teacher/comments', methods=['GET', 'POST'])
@role_required('teacher')
def teacher_comments():
    data = load_data()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            student_username = request.form.get('student_username', '').strip()
            text = request.form.get('text', '').strip()
            if text:
                data.setdefault('comments', []).append({
                    'id': str(uuid.uuid4())[:8],
                    'student_username': student_username,
                    'text': text,
                    'author': session['user']['username'],
                    'created_at': datetime.now().isoformat(),
                })
                save_data(data)
                flash("Izoh muvaffaqiyatli qo'shildi!", 'success')
        elif action == 'delete':
            comment_id = request.form.get('comment_id')
            data['comments'] = [c for c in data.get('comments', []) if c.get('id') != comment_id]
            save_data(data)
            flash("Izoh o'chirildi.", 'success')
        return redirect(url_for('teacher_comments'))
    students = [u for u in data['users'] if u['role'] == 'student']
    comments = data.get('comments', [])
    return render_template('teacher/comments.html', students=students, comments=comments)

# --- Attendance ---
@app.route('/teacher/attendance', methods=['GET', 'POST'])
@role_required('teacher')
def teacher_attendance():
    data = load_data()
    if request.method == 'POST':
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        student_username = request.form.get('student_username')
        status = request.form.get('status', 'present')
        data['attendance'].append({
            'date': date,
            'student_username': student_username,
            'status': status,
            'marked_by': session['user']['username'],
        })
        save_data(data)
        flash("Davomat belgilandi!", 'success')
        return redirect(url_for('teacher_attendance'))
    students = [u for u in data['users'] if u['role'] == 'student']
    today = datetime.now().strftime('%Y-%m-%d')
    records = [r for r in data['attendance'] if r.get('date') == today]
    return render_template('teacher/attendance.html', students=students, records=records, today=today)

# --- Teacher own attendance ---
@app.route('/teacher/my-attendance', methods=['GET', 'POST'])
@role_required('teacher')
def teacher_my_attendance():
    data = load_data()
    if request.method == 'POST':
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        status = request.form.get('status', 'present')
        note = request.form.get('note', '')
        data['teacher_attendance'].append({
            'date': date,
            'teacher_username': session['user']['username'],
            'status': status,
            'note': note,
        })
        save_data(data)
        flash("Davomat belgilandi!", 'success')
        return redirect(url_for('teacher_my_attendance'))
    records = [r for r in data.get('teacher_attendance', []) if r.get('teacher_username') == session['user']['username']]
    return render_template('teacher/my_attendance.html', records=records)

# --- Custom Questions ---
@app.route('/teacher/questions', methods=['GET', 'POST'])
@role_required('teacher')
def teacher_questions():
    if request.method == 'POST':
        subject = request.form.get('subject')
        level = request.form.get('level')
        question_text = request.form.get('question', '').strip()
        answer_text = request.form.get('answer', '').strip()
        if question_text and answer_text:
            qdata = load_custom_questions()
            if subject not in qdata:
                qdata[subject] = {}
            if level not in qdata[subject]:
                qdata[subject][level] = []
            qdata[subject][level].append({'q': question_text, 'a': answer_text})
            save_custom_questions(qdata)
            flash("Savol muvaffaqiyatli qo'shildi!", 'success')
        return redirect(url_for('teacher_questions'))
    custom = load_custom_questions()
    return render_template('teacher/questions.html', subjects=SUBJECTS, custom=custom)

# --- Results ---
@app.route('/teacher/results')
@role_required('teacher')
def teacher_results():
    data = load_data()
    test_results = data.get('test_results', [])
    return render_template('teacher/results.html', results=test_results)

# --- Support ---
@app.route('/teacher/support', methods=['GET', 'POST'])
@role_required('teacher')
def teacher_support():
    data = load_data()
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        if text:
            data['support_messages'].append({
                'id': str(uuid.uuid4())[:8],
                'text': text,
                'author': session['user']['username'],
                'role': 'teacher',
                'created_at': datetime.now().isoformat(),
            })
            save_data(data)
            flash("Xabar yuborildi!", 'success')
        return redirect(url_for('teacher_support'))
    messages = data.get('support_messages', [])
    return render_template('teacher/support.html', messages=messages)

# ===== STUDENT ROUTES =====

@app.route('/student/dashboard')
@role_required('student')
def student_dashboard():
    data = load_data()
    user_comments = [c for c in data.get('comments', []) if c.get('student_username') == session['user']['username']]
    return render_template('student/dashboard.html', subjects=SUBJECTS, subject_icons=SUBJECT_ICONS, comments=user_comments)

@app.route('/student/test', methods=['GET', 'POST'])
@role_required('student')
def student_test():
    if request.method == 'POST':
        subject = request.form.get('subject')
        level = request.form.get('level')
        return redirect(url_for('start_test', subject=subject, level=level))
    return render_template('student/test.html', subjects=SUBJECTS, subject_icons=SUBJECT_ICONS)

@app.route('/student/start-test/<subject>/<level>')
@role_required('student')
def start_test(subject, level):
    questions = get_all_questions(subject, level)
    if not questions:
        flash("Bu fan va daraja uchun savollar mavjud emas!", 'error')
        return redirect(url_for('student_test'))
    selected = random.sample(questions, min(15, len(questions)))
    session['test'] = {
        'subject': subject,
        'level': level,
        'questions': selected,
        'current': 0,
        'score': 0,
        'total': len(selected),
        'start_time': datetime.now().isoformat(),
        'timer': SUBJECT_TIMERS.get(subject, 15),
    }
    return redirect(url_for('quiz'))

@app.route('/student/quiz', methods=['GET', 'POST'])
@role_required('student')
def quiz():
    test = session.get('test')
    if not test:
        return redirect(url_for('student_test'))
    if request.method == 'POST':
        answer = request.form.get('answer', '').strip().lower()
        correct = test['questions'][test['current']]['a'].lower()
        if answer == correct:
            test['score'] += 1
        test['current'] += 1
        if test['current'] >= test['total']:
            return redirect(url_for('quiz_result'))
        session['test'] = test
    q = test['questions'][test['current']]
    progress = int((test['current'] / test['total']) * 100)
    return render_template('student/quiz.html',
        question=q,
        current=test['current'] + 1,
        total=test['total'],
        score=test['score'],
        subject=test['subject'],
        level=test['level'],
        progress=progress,
        timer=test['timer'])

@app.route('/student/quiz-result')
@role_required('student')
def quiz_result():
    test = session.pop('test', None)
    if not test:
        return redirect(url_for('student_test'))
    percentage = int((test['score'] / test['total']) * 100)
    # Save result
    data = load_data()
    data.setdefault('test_results', []).append({
        'student': session['user']['username'],
        'subject': test['subject'],
        'level': test['level'],
        'score': test['score'],
        'total': test['total'],
        'percentage': percentage,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
    })
    save_data(data)
    return render_template('student/quiz_result.html',
        score=test['score'],
        total=test['total'],
        percentage=percentage,
        subject=test['subject'],
        level=test['level'])

# --- Student Schedule ---
@app.route('/student/schedule')
@role_required('student')
def student_schedule():
    data = load_data()
    return render_template('student/schedule_view.html', schedules=data.get('schedules', {}), days=DAYS, periods=PERIODS, subject_colors=SUBJECT_COLORS, subject_icons=SUBJECT_ICONS)

# --- Student Attendance ---
@app.route('/student/attendance')
@role_required('student')
def student_attendance():
    data = load_data()
    records = [r for r in data['attendance'] if r.get('student_username') == session['user']['username']]
    return render_template('student/attendance.html', records=records)

# --- Student Support ---
@app.route('/student/support', methods=['GET', 'POST'])
@role_required('student')
def student_support():
    data = load_data()
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        if text:
            data['support_messages'].append({
                'id': str(uuid.uuid4())[:8],
                'text': text,
                'author': session['user']['username'],
                'role': 'student',
                'created_at': datetime.now().isoformat(),
            })
            save_data(data)
            flash("Xabar yuborildi!", 'success')
        return redirect(url_for('student_support'))
    messages = data.get('support_messages', [])
    return render_template('student/support.html', messages=messages)

# --- Student Comments ---
@app.route('/student/comments')
@role_required('student')
def student_comments():
    data = load_data()
    user_comments = [c for c in data.get('comments', []) if c.get('student_username') == session['user']['username']]
    return render_template('student/comments.html', comments=user_comments)

# ===== PWA =====
@app.route('/manifest.json')
def manifest():
    return send_file(os.path.join(app.static_folder, 'manifest.json'), mimetype='application/json')

@app.route('/sw.js')
def sw():
    return send_file(os.path.join(app.static_folder, 'sw.js'), mimetype='application/javascript')

# ===== DEFAULT TEACHER ACCOUNT =====
def init_default_data():
    data = load_data()
    if not any(u['username'] == 'admin' for u in data['users']):
        data['users'].append({
            'username': 'admin',
            'password_hash': hash_password('admin123'),
            'role': 'teacher',
            'name': 'Administrator',
            'class': '',
            'created_at': datetime.now().isoformat(),
        })
        save_data(data)

init_default_data()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
