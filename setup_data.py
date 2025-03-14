#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
إعداد البيانات الأولية - تحميل وإعداد البيانات القرآنية والتفاسير والمعجزات العلمية
"""

import os
import sys
import logging
import json
import requests
import tempfile
import shutil
from pathlib import Path
import dotenv
from tqdm import tqdm
import qdrant_client
from qdrant_client.http import models

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("QuranAssistant-DataSetup")

# تحميل متغيرات البيئة
dotenv.load_dotenv()

# تحديد المسارات المهمة
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = BASE_DIR / "data"
QURAN_DIR = DATA_DIR / "quran"
TAFSEER_DIR = DATA_DIR / "tafseer"
MIRACLE_DIR = DATA_DIR / "miracles"
AUDIO_DIR = DATA_DIR / "audio"
VIDEO_DIR = DATA_DIR / "video"

# إنشاء المجلدات إذا لم تكن موجودة
for directory in [DATA_DIR, QURAN_DIR, TAFSEER_DIR, MIRACLE_DIR, AUDIO_DIR, VIDEO_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ تأكيد وجود المجلد: {directory}")

# الحصول على بيانات الاتصال بـ Qdrant من ملف .env
QDRANT_URL = os.getenv("QDRANT_URL", "https://9c41ece4-5e7f-4f91-8292-37e234f6c201.us-east4-0.gcp.cloud.qdrant.io:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.wzZ1xzWs5MjVqV_BhblVOcKbuQrMwFlrnUU9IxxGz60")

def download_quran_data():
    """تحميل بيانات القرآن الكريم"""
    logger.info("جاري تحميل بيانات القرآن الكريم...")
    
    quran_url = "https://api.alquran.cloud/v1/quran/ar.asad"
    quran_file = QURAN_DIR / "quran.json"
    
    # تخطي التحميل إذا كان الملف موجودًا
    if quran_file.exists():
        logger.info(f"ملف القرآن موجود بالفعل: {quran_file}")
        return
    
    try:
        response = requests.get(quran_url)
        data = response.json()
        
        # حفظ الملف
        with open(quran_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"✅ تم تحميل بيانات القرآن بنجاح: {quran_file}")
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل بيانات القرآن: {str(e)}")

def download_tafseer_data():
    """تحميل بيانات التفاسير"""
    logger.info("جاري تحميل بيانات التفاسير...")
    
    # قائمة التفاسير المتاحة
    tafseer_list = [
        {"id": "ar.muyassar", "name": "التفسير الميسر"},
        {"id": "ar.jalalayn", "name": "تفسير الجلالين"}
    ]
    
    for tafseer in tafseer_list:
        tafseer_id = tafseer["id"]
        tafseer_name = tafseer["name"]
        tafseer_file = TAFSEER_DIR / f"{tafseer_id}.json"
        
        # تخطي التحميل إذا كان الملف موجودًا
        if tafseer_file.exists():
            logger.info(f"ملف التفسير موجود بالفعل: {tafseer_file}")
            continue
        
        try:
            # إنشاء قائمة لتخزين بيانات التفسير لجميع الآيات
            all_tafseer_data = []
            
            # التحميل لكل سورة (1-114)
            for surah_number in tqdm(range(1, 115), desc=f"تحميل {tafseer_name}"):
                tafseer_url = f"https://api.quran-tafseer.com/tafseer/{tafseer_id}/{surah_number}"
                response = requests.get(tafseer_url)
                
                if response.status_code == 200:
                    tafseer_data = response.json()
                    # إضافة بيانات التفسير لهذه السورة
                    all_tafseer_data.extend(tafseer_data)
                else:
                    logger.warning(f"⚠️ خطأ في تحميل تفسير السورة {surah_number} للتفسير {tafseer_name}: {response.status_code}")
            
            # حفظ الملف
            with open(tafseer_file, 'w', encoding='utf-8') as f:
                json.dump(all_tafseer_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"✅ تم تحميل تفسير {tafseer_name} بنجاح: {tafseer_file}")
        except Exception as e:
            logger.error(f"❌ خطأ في تحميل تفسير {tafseer_name}: {str(e)}")

def create_initial_miracle_data():
    """إنشاء بيانات أولية للمعجزات العلمية"""
    logger.info("جاري إنشاء بيانات أولية للمعجزات العلمية...")
    
    miracle_file = MIRACLE_DIR / "scientific_miracles.json"
    
    # تخطي الإنشاء إذا كان الملف موجودًا
    if miracle_file.exists():
        logger.info(f"ملف المعجزات العلمية موجود بالفعل: {miracle_file}")
        return
    
    # إنشاء بيانات أولية للمعجزات العلمية
    initial_miracles = [
        {
            "id": "miracle_1",
            "title": "وصف دقيق لتكوين الجنين",
            "category": "علم الأجنة",
            "description": "وصف القرآن الكريم مراحل تكوين الجنين بشكل دقيق قبل اكتشاف علم الأجنة الحديث",
            "evidence": "اكتشف العلم الحديث أن الجنين يمر بمراحل كما وصفها القرآن: النطفة، العلقة، المضغة، العظام، ثم كسوة العظام باللحم",
            "verses": [
                {"surah": "المؤمنون", "ayah": 12, "text": "وَلَقَدْ خَلَقْنَا الْإِنسَانَ مِن سُلَالَةٍ مِّن طِينٍ"},
                {"surah": "المؤمنون", "ayah": 13, "text": "ثُمَّ جَعَلْنَاهُ نُطْفَةً فِي قَرَارٍ مَّكِينٍ"},
                {"surah": "المؤمنون", "ayah": 14, "text": "ثُمَّ خَلَقْنَا النُّطْفَةَ عَلَقَةً فَخَلَقْنَا الْعَلَقَةَ مُضْغَةً فَخَلَقْنَا الْمُضْغَةَ عِظَامًا فَكَسَوْنَا الْعِظَامَ لَحْمًا ثُمَّ أَنشَأْنَاهُ خَلْقًا آخَرَ ۚ فَتَبَارَكَ اللَّهُ أَحْسَنُ الْخَالِقِينَ"}
            ],
            "year_discovered": 1942,
            "references": ["Moore, Keith L. (1986). The Developing Human: Clinically Oriented Embryology"]
        },
        {
            "id": "miracle_2",
            "title": "توسع الكون",
            "category": "علم الفلك",
            "description": "أشار القرآن الكريم إلى توسع الكون، وهو ما أكده العلم الحديث في القرن العشرين",
            "evidence": "اكتشف علماء الفلك في بداية القرن العشرين أن الكون يتوسع، وهو ما أشار إليه القرآن الكريم قبل 1400 سنة",
            "verses": [
                {"surah": "الذاريات", "ayah": 47, "text": "وَالسَّمَاءَ بَنَيْنَاهَا بِأَيْدٍ وَإِنَّا لَمُوسِعُونَ"}
            ],
            "year_discovered": 1929,
            "references": ["Hubble, Edwin (1929). A relation between distance and radial velocity among extra-galactic nebulae"]
        },
        {
            "id": "miracle_3",
            "title": "الحاجز بين البحرين",
            "category": "علم المحيطات",
            "description": "وصف القرآن الكريم وجود حاجز بين البحرين يمنع اختلاطهما، وهو ما أكده علم المحيطات الحديث",
            "evidence": "اكتشف علماء المحيطات وجود حواجز مائية بين البحار تمنع الاختلاط الكامل بينها، وهو ما وصفه القرآن بدقة",
            "verses": [
                {"surah": "الرحمن", "ayah": 19, "text": "مَرَجَ الْبَحْرَيْنِ يَلْتَقِيَانِ"},
                {"surah": "الرحمن", "ayah": 20, "text": "بَيْنَهُمَا بَرْزَخٌ لَّا يَبْغِيَانِ"}
            ],
            "year_discovered": 1962,
            "references": ["Oceanography studies on water barriers between seas"]
        }
    ]
    
    # حفظ البيانات
    with open(miracle_file, 'w', encoding='utf-8') as f:
        json.dump(initial_miracles, f, ensure_ascii=False, indent=4)
    
    logger.info(f"✅ تم إنشاء بيانات أولية للمعجزات العلمية: {miracle_file}")

def setup_qdrant_collections():
    """إعداد مجموعات Qdrant"""
    logger.info("جاري إعداد مجموعات Qdrant...")
    
    try:
        # إنشاء عميل Qdrant
        client = qdrant_client.QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY
        )
        
        # إنشاء مجموعات البيانات المختلفة
        collections = [
            {
                "name": "quran_verses",
                "description": "مجموعة الآيات القرآنية",
                "vector_size": 768  # بُعد التضمين
            },
            {
                "name": "tafseer",
                "description": "مجموعة التفاسير",
                "vector_size": 768
            },
            {
                "name": "scientific_miracles",
                "description": "مجموعة المعجزات العلمية",
                "vector_size": 768
            },
            {
                "name": "audio_text",
                "description": "مجموعة النصوص المستخرجة من التسجيلات الصوتية",
                "vector_size": 768
            },
            {
                "name": "video_text",
                "description": "مجموعة النصوص المستخرجة من الفيديوهات",
                "vector_size": 768
            }
        ]
        
        # إنشاء كل مجموعة
        for collection in collections:
            # التحقق من وجود المجموعة
            try:
                client.get_collection(collection["name"])
                logger.info(f"✅ المجموعة موجودة بالفعل: {collection['name']}")
            except Exception:
                # إنشاء المجموعة إذا لم تكن موجودة
                client.create_collection(
                    collection_name=collection["name"],
                    vectors_config=models.VectorParams(
                        size=collection["vector_size"],
                        distance=models.Distance.COSINE
                    ),
                    metadata={
                        "description": collection["description"]
                    }
                )
                logger.info(f"✅ تم إنشاء المجموعة: {collection['name']}")
        
        # التحقق من الاتصال
        logger.info(f"✅ تم الاتصال بـ Qdrant بنجاح: {QDRANT_URL}")
        collections_list = client.get_collections().collections
        logger.info(f"✅ المجموعات المتاحة: {[c.name for c in collections_list]}")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إعداد مجموعات Qdrant: {str(e)}")

def download_sample_media():
    """تحميل عينات من الملفات الصوتية والمرئية للاختبار"""
    logger.info("جاري تحميل عينات من الملفات الصوتية والمرئية...")
    
    # عينة ملف صوتي
    sample_audio_url = "https://www.everyayah.com/data/Abdul_Basit_Murattal_192kbps/001001.mp3"
    sample_audio_file = AUDIO_DIR / "sample_quran_recitation.mp3"
    
    # عينة ملف فيديو
    sample_video_url = "https://github.com/Quran-Tafseer/quran-tafseer-api/raw/master/docs/assets/quran_recitation_sample.mp4"
    sample_video_file = VIDEO_DIR / "sample_quran_video.mp4"
    
    # تحميل الملف الصوتي
    if not sample_audio_file.exists():
        try:
            response = requests.get(sample_audio_url)
            with open(sample_audio_file, 'wb') as f:
                f.write(response.content)
            logger.info(f"✅ تم تحميل عينة الملف الصوتي: {sample_audio_file}")
        except Exception as e:
            logger.error(f"❌ خطأ في تحميل عينة الملف الصوتي: {str(e)}")
    else:
        logger.info(f"✅ عينة الملف الصوتي موجودة بالفعل: {sample_audio_file}")
    
    # تحميل ملف الفيديو
    if not sample_video_file.exists():
        try:
            response = requests.get(sample_video_url)
            if response.status_code == 200:
                with open(sample_video_file, 'wb') as f:
                    f.write(response.content)
                logger.info(f"✅ تم تحميل عينة ملف الفيديو: {sample_video_file}")
            else:
                # إذا لم يتم العثور على الملف، قم بإنشاء ملف نصي بدلاً منه
                with open(str(sample_video_file) + ".txt", 'w', encoding='utf-8') as f:
                    f.write("لم يتم العثور على عينة فيديو مناسبة للتحميل، يرجى تحميل ملف فيديو يدويًا")
                logger.warning(f"⚠️ لم يتم العثور على عينة فيديو مناسبة، إنشاء ملف نصي بدلاً منه")
        except Exception as e:
            logger.error(f"❌ خطأ في تحميل عينة ملف الفيديو: {str(e)}")
    else:
        logger.info(f"✅ عينة ملف الفيديو موجودة بالفعل: {sample_video_file}")

def create_config_from_env():
    """إنشاء ملف تكوين من ملف .env إذا لم يكن موجودًا"""
    logger.info("جاري إنشاء ملف تكوين...")
    
    config_dir = BASE_DIR / "config"
    config_file = config_dir / "settings.json"
    
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
    
    if not config_file.exists():
        config = {
            "qdrant": {
                "url": QDRANT_URL,
                "api_key": QDRANT_API_KEY
            },
            "ollama": {
                "host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
                "model": os.getenv("OLLAMA_MODEL", "mistral")
            },
            "data": {
                "quran_dir": str(QURAN_DIR),
                "tafseer_dir": str(TAFSEER_DIR),
                "miracle_dir": str(MIRACLE_DIR),
                "audio_dir": str(AUDIO_DIR),
                "video_dir": str(VIDEO_DIR)
            },
            "ui": {
                "theme": "dark",
                "language": "ar"
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        
        logger.info(f"✅ تم إنشاء ملف التكوين: {config_file}")
    else:
        logger.info(f"✅ ملف التكوين موجود بالفعل: {config_file}")

def main():
    """الدالة الرئيسية للإعداد"""
    logger.info("🚀 بدء إعداد البيانات لمساعد القرآن الذكي")
    
    # إنشاء ملف التكوين
    create_config_from_env()
    
    # تحميل بيانات القرآن
    download_quran_data()
    
    # تحميل بيانات التفاسير
    download_tafseer_data()
    
    # إنشاء بيانات أولية للمعجزات العلمية
    create_initial_miracle_data()
    
    # إعداد مجموعات Qdrant
    setup_qdrant_collections()
    
    # تحميل عينات من الملفات الصوتية والمرئية
    download_sample_media()
    
    logger.info("✅ اكتمل إعداد البيانات بنجاح")
    logger.info("🔍 يمكنك الآن تشغيل التطبيق باستخدام: python run_local.py")

if __name__ == "__main__":
    main()
