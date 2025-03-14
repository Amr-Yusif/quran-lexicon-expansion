#!/usr/bin/env python
"""
معالجة وفهرسة المصادر الإسلامية في قاعدة بيانات Qdrant
يقوم هذا السكربت باستخراج النصوص من الملفات المختلفة (PDF, صوت) وتحميلها إلى Qdrant
"""

import os
import logging
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import tempfile
import re
import concurrent.futures
import traceback

import requests
import dotenv
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import PyPDF2
import numpy as np
import qdrant_client
from qdrant_client.http import models
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("IslamicResources-Processor")

# تحميل متغيرات البيئة
dotenv.load_dotenv()

# استخدام معلومات Qdrant API من المتغيرات البيئية أو تعيينها مباشرة
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.wzZ1xzWs5MjVqV_BhblVOcKbuQrMwFlrnUU9IxxGz60")
QDRANT_URL = os.getenv("QDRANT_URL", "https://9c41ece4-5e7f-4f91-8292-37e234f6c201.us-east4-0.gcp.cloud.qdrant.io:6333")

# تحديد المسارات المهمة
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = BASE_DIR / "data"
RESOURCES_DIR = DATA_DIR / "islamic_resources"

# أسماء المجموعات في Qdrant
COLLECTION_NAMES = {
    "quran": "quran_verses",
    "tafsir": "tafsir_explanations",
    "scientific_miracles": "scientific_miracles",
    "scholars_books": "scholars_books",
    "aqeedah": "aqeedah_books",  # العقيدة
    "fiqh": "fiqh_books",  # الفقه
    "hadith": "hadith_books",  # الحديث
    "seerah": "seerah_books",  # السيرة النبوية
    "akhlaq": "akhlaq_books",  # الأخلاق
    "history": "islamic_history_books",  # التاريخ الإسلامي
    "fatawa": "fatawa_books"  # الفتاوى
}

# تحديد المجلدات المهمة
TAFSIR_DIR = RESOURCES_DIR / "tafsir"
BOOKS_DIR = RESOURCES_DIR / "books"
SCHOLARS_DIR = RESOURCES_DIR / "scholars"
SCIENTIFIC_MIRACLES_DIR = RESOURCES_DIR / "scientific_miracles"
NUMERICAL_MIRACLES_DIR = RESOURCES_DIR / "numerical_miracles"
AUDIO_DIR = RESOURCES_DIR / "audio"
VIDEO_DIR = RESOURCES_DIR / "video"

# مجلدات الكتب المصنفة
AQEEDAH_DIR = BOOKS_DIR / "aqeedah"  # العقيدة
FIQH_DIR = BOOKS_DIR / "fiqh"  # الفقه
TAFSIR_BOOKS_DIR = BOOKS_DIR / "tafsir"  # كتب التفسير
HADITH_DIR = BOOKS_DIR / "hadith"  # الحديث
SEERAH_DIR = BOOKS_DIR / "seerah"  # السيرة النبوية
AKHLAQ_DIR = BOOKS_DIR / "akhlaq"  # الأخلاق
HISTORY_DIR = BOOKS_DIR / "history"  # التاريخ الإسلامي
FATAWA_DIR = BOOKS_DIR / "fatawa"  # الفتاوى

# تدفق العمل العام
def main():
    """الوظيفة الرئيسية لمعالجة وفهرسة المصادر الإسلامية"""
    logger.info("بدء معالجة وفهرسة المصادر الإسلامية...")
    
    # التحقق من تنزيل المصادر
    verify_resources_downloaded()
    
    # إنشاء عميل Qdrant
    qdrant_client_instance = setup_qdrant_client()
    
    # إنشاء مجموعات Qdrant إذا لم تكن موجودة
    setup_qdrant_collections(qdrant_client_instance)
    
    # معالجة وفهرسة جميع المصادر
    process_tafsir(qdrant_client_instance)
    process_scholars_books(qdrant_client_instance)
    process_scientific_miracles(qdrant_client_instance)
    
    # معالجة وفهرسة الكتب الإسلامية المصنفة
    process_aqeedah_books(qdrant_client_instance)
    process_fiqh_books(qdrant_client_instance)
    process_tafsir_books(qdrant_client_instance)
    process_hadith_books(qdrant_client_instance)
    process_seerah_books(qdrant_client_instance)
    process_akhlaq_books(qdrant_client_instance)
    process_history_books(qdrant_client_instance)
    process_fatawa_books(qdrant_client_instance)
    
    logger.info("✅ اكتملت معالجة وفهرسة المصادر الإسلامية!")

# التحقق من تنزيل المصادر
def verify_resources_downloaded():
    """التحقق من تنزيل المصادر الإسلامية"""
    if not RESOURCES_DIR.exists():
        logger.error("❌ مجلد المصادر الإسلامية غير موجود. يرجى تشغيل download_islamic_resources.py أولاً.")
        sys.exit(1)
    
    # التحقق من وجود بعض المجلدات الأساسية
    required_dirs = [
        RESOURCES_DIR / "tafsir",
        RESOURCES_DIR / "books",
        RESOURCES_DIR / "scholars",
        RESOURCES_DIR / "scientific_miracles"
    ]
    
    for directory in required_dirs:
        if not directory.exists():
            logger.warning(f"⚠️ المجلد {directory} غير موجود.")
    
    # التحقق من وجود مجلدات الكتب المصنفة
    category_dirs = [
        AQEEDAH_DIR,
        FIQH_DIR,
        TAFSIR_BOOKS_DIR,
        HADITH_DIR,
        SEERAH_DIR,
        AKHLAQ_DIR,
        HISTORY_DIR,
        FATAWA_DIR
    ]
    
    for directory in category_dirs:
        if not directory.exists():
            logger.warning(f"⚠️ مجلد الكتب {directory} غير موجود.")
    
    logger.info("✅ تم التحقق من تنزيل المصادر الإسلامية.")

# إعداد عميل Qdrant
def setup_qdrant_client() -> qdrant_client.QdrantClient:
    """إنشاء وإعداد عميل Qdrant"""
    try:
        client = qdrant_client.QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY
        )
        
        # التحقق من الاتصال
        client.get_collections()
        logger.info("✅ تم إنشاء الاتصال بـ Qdrant بنجاح.")
        return client
    
    except Exception as e:
        logger.error(f"❌ فشل الاتصال بـ Qdrant: {str(e)}")
        sys.exit(1)

# إنشاء مجموعات Qdrant
def setup_qdrant_collections(client: qdrant_client.QdrantClient):
    """إنشاء مجموعات Qdrant المطلوبة"""
    # نموذج تضمين النص
    embedding_model = load_embedding_model()
    vector_size = embedding_model.get_sentence_embedding_dimension()
    
    # التحقق من المجموعات الموجودة
    existing_collections = [collection.name for collection in client.get_collections().collections]
    logger.info(f"المجموعات الموجودة: {existing_collections}")
    
    # إنشاء المجموعات المطلوبة
    for name, collection_name in COLLECTION_NAMES.items():
        if collection_name not in existing_collections:
            logger.info(f"إنشاء مجموعة {collection_name}...")
            
            try:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"✅ تم إنشاء مجموعة {collection_name} بنجاح.")
            
            except Exception as e:
                logger.error(f"❌ فشل إنشاء مجموعة {collection_name}: {str(e)}")
        else:
            logger.info(f"مجموعة {collection_name} موجودة بالفعل.")

# تحميل نموذج التضمين
def load_embedding_model() -> SentenceTransformer:
    """تحميل نموذج تضمين النص"""
    try:
        # استخدام نموذج مناسب للغة العربية
        model_name = "UBC-NLP/ARBERT"  # نموذج BERT العربي
        model = SentenceTransformer(model_name)
        logger.info(f"✅ تم تحميل نموذج التضمين {model_name} بنجاح.")
        return model
    
    except Exception as e:
        logger.error(f"❌ فشل تحميل نموذج التضمين: {str(e)}")
        sys.exit(1)

# استخراج النص من ملف PDF
def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    استخراج النص من ملف PDF
    
    Args:
        pdf_path (Path): مسار ملف PDF
    
    Returns:
        str: النص المستخرج من الملف
    """
    try:
        text = ""
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        
        # تنظيف النص
        text = clean_text(text)
        
        return text
    
    except Exception as e:
        logger.error(f"❌ خطأ في استخراج النص من {pdf_path}: {str(e)}")
        return ""

# تنظيف النص
def clean_text(text: str) -> str:
    """
    تنظيف النص وإزالة المحتوى غير المرغوب فيه
    
    Args:
        text (str): النص المراد تنظيفه
    
    Returns:
        str: النص بعد التنظيف
    """
    # إزالة الأسطر الفارغة المتعددة
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # إزالة المسافات المتعددة
    text = re.sub(r'\s+', ' ', text)
    
    # إزالة أحرف التحكم
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    
    return text.strip()

# تقسيم النص إلى مقاطع
def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    تقسيم النص إلى مقاطع أصغر للفهرسة
    
    Args:
        text (str): النص المراد تقسيمه
        chunk_size (int, optional): حجم المقطع بالأحرف. الافتراضي هو 1000.
        overlap (int, optional): التداخل بين المقاطع بالأحرف. الافتراضي هو 200.
    
    Returns:
        List[str]: قائمة بالمقاطع النصية
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        # تحديد نهاية المقطع
        end = min(start + chunk_size, text_length)
        
        # البحث عن نهاية جملة أو فقرة لتقسيم المقطع بشكل أفضل
        if end < text_length:
            # محاولة البحث عن نهاية فقرة
            paragraph_end = text.rfind('\n\n', start, end)
            
            if paragraph_end != -1 and paragraph_end > start + chunk_size // 2:
                end = paragraph_end + 2
            else:
                # محاولة البحث عن نهاية جملة
                sentence_end = text.rfind('. ', start, end)
                
                if sentence_end != -1 and sentence_end > start + chunk_size // 2:
                    end = sentence_end + 2
        
        # إضافة المقطع إلى القائمة
        chunks.append(text[start:end])
        
        # تحديث موضع البداية للمقطع التالي مع مراعاة التداخل
        start = end - overlap
    
    return chunks

# معالجة التفاسير
def process_tafsir(client: qdrant_client.QdrantClient):
    """
    معالجة وفهرسة تفاسير القرآن
    
    Args:
        client (qdrant_client.QdrantClient): عميل Qdrant
    """
    logger.info("معالجة وفهرسة تفاسير القرآن...")
    
    tafsir_dir = RESOURCES_DIR / "tafsir"
    embedding_model = load_embedding_model()
    collection_name = COLLECTION_NAMES["tafsir"]
    
    if not tafsir_dir.exists():
        logger.warning(f"⚠️ مجلد التفاسير {tafsir_dir} غير موجود.")
        return
    
    # معالجة جميع ملفات PDF في مجلد التفاسير
    pdf_files = []
    
    for subdir, _, files in os.walk(tafsir_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(Path(subdir) / file)
    
    logger.info(f"وجدت {len(pdf_files)} ملف PDF للتفاسير.")
    
    for pdf_path in tqdm(pdf_files, desc="معالجة ملفات تفسير القرآن"):
        # استخراج النص من PDF
        text = extract_text_from_pdf(pdf_path)
        
        if not text:
            logger.warning(f"⚠️ لم يتم استخراج نص من {pdf_path}")
            continue
        
        # تقسيم النص إلى مقاطع
        chunks = split_text_into_chunks(text)
        logger.info(f"تم تقسيم {pdf_path.name} إلى {len(chunks)} مقطع.")
        
        # إعداد البيانات للإدخال في Qdrant
        points = []
        
        for i, chunk in enumerate(chunks):
            # إنشاء متجه التضمين
            embedding = embedding_model.encode(chunk)
            
            # إنشاء نقطة البيانات
            point = models.PointStruct(
                id=int(hash(f"{pdf_path.name}-{i}") % (10**10)),  # معرّف فريد
                vector=embedding.tolist(),
                payload={
                    "text": chunk,
                    "source": str(pdf_path),
                    "source_type": "tafsir",
                    "tafsir_name": pdf_path.parent.name,
                    "chunk_id": i,
                    "chunk_count": len(chunks)
                }
            )
            
            points.append(point)
        
        # إضافة النقاط إلى مجموعة Qdrant
        try:
            client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info(f"✅ تمت إضافة {len(points)} نقطة من {pdf_path.name} إلى مجموعة {collection_name}.")
        
        except Exception as e:
            logger.error(f"❌ فشل إضافة نقاط من {pdf_path.name}: {str(e)}")

# معالجة كتب العلماء
def process_scholars_books(client: qdrant_client.QdrantClient):
    """
    معالجة وفهرسة كتب العلماء
    
    Args:
        client (qdrant_client.QdrantClient): عميل Qdrant
    """
    logger.info("معالجة وفهرسة كتب العلماء...")
    
    scholars_dir = RESOURCES_DIR / "scholars"
    embedding_model = load_embedding_model()
    collection_name = COLLECTION_NAMES["scholars_books"]
    
    if not scholars_dir.exists():
        logger.warning(f"⚠️ مجلد كتب العلماء {scholars_dir} غير موجود.")
        return
    
    # معالجة جميع ملفات PDF في مجلد كتب العلماء
    pdf_files = []
    
    for subdir, _, files in os.walk(scholars_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(Path(subdir) / file)
    
    logger.info(f"وجدت {len(pdf_files)} ملف PDF لكتب العلماء.")
    
    for pdf_path in tqdm(pdf_files, desc="معالجة كتب العلماء"):
        # استخراج النص من PDF
        text = extract_text_from_pdf(pdf_path)
        
        if not text:
            logger.warning(f"⚠️ لم يتم استخراج نص من {pdf_path}")
            continue
        
        # تقسيم النص إلى مقاطع
        chunks = split_text_into_chunks(text)
        logger.info(f"تم تقسيم {pdf_path.name} إلى {len(chunks)} مقطع.")
        
        # تحديد اسم العالم من المسار
        scholar_name = pdf_path.parent.name
        
        # إعداد البيانات للإدخال في Qdrant
        points = []
        
        for i, chunk in enumerate(chunks):
            # إنشاء متجه التضمين
            embedding = embedding_model.encode(chunk)
            
            # إنشاء نقطة البيانات
            point = models.PointStruct(
                id=int(hash(f"{pdf_path.name}-{i}") % (10**10)),  # معرّف فريد
                vector=embedding.tolist(),
                payload={
                    "text": chunk,
                    "source": str(pdf_path),
                    "source_type": "scholar_book",
                    "scholar_name": scholar_name,
                    "book_name": pdf_path.name,
                    "chunk_id": i,
                    "chunk_count": len(chunks)
                }
            )
            
            points.append(point)
        
        # إضافة النقاط إلى مجموعة Qdrant
        try:
            client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info(f"✅ تمت إضافة {len(points)} نقطة من {pdf_path.name} إلى مجموعة {collection_name}.")
        
        except Exception as e:
            logger.error(f"❌ فشل إضافة نقاط من {pdf_path.name}: {str(e)}")

# معالجة الإعجاز العلمي
def process_scientific_miracles(client: qdrant_client.QdrantClient):
    """
    معالجة وفهرسة كتب الإعجاز العلمي
    
    Args:
        client (qdrant_client.QdrantClient): عميل Qdrant
    """
    logger.info("معالجة وفهرسة كتب الإعجاز العلمي...")
    
    miracles_dir = RESOURCES_DIR / "scientific_miracles"
    embedding_model = load_embedding_model()
    collection_name = COLLECTION_NAMES["scientific_miracles"]
    
    if not miracles_dir.exists():
        logger.warning(f"⚠️ مجلد الإعجاز العلمي {miracles_dir} غير موجود.")
        return
    
    # معالجة جميع ملفات PDF في مجلد الإعجاز العلمي
    pdf_files = []
    
    for subdir, _, files in os.walk(miracles_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(Path(subdir) / file)
    
    logger.info(f"وجدت {len(pdf_files)} ملف PDF للإعجاز العلمي.")
    
    for pdf_path in tqdm(pdf_files, desc="معالجة كتب الإعجاز العلمي"):
        # استخراج النص من PDF
        text = extract_text_from_pdf(pdf_path)
        
        if not text:
            logger.warning(f"⚠️ لم يتم استخراج نص من {pdf_path}")
            continue
        
        # تقسيم النص إلى مقاطع
        chunks = split_text_into_chunks(text)
        logger.info(f"تم تقسيم {pdf_path.name} إلى {len(chunks)} مقطع.")
        
        # إعداد البيانات للإدخال في Qdrant
        points = []
        
        for i, chunk in enumerate(chunks):
            # إنشاء متجه التضمين
            embedding = embedding_model.encode(chunk)
            
            # إنشاء نقطة البيانات
            point = models.PointStruct(
                id=int(hash(f"{pdf_path.name}-{i}") % (10**10)),  # معرّف فريد
                vector=embedding.tolist(),
                payload={
                    "text": chunk,
                    "source": str(pdf_path),
                    "source_type": "scientific_miracle",
                    "miracle_type": pdf_path.parent.name,
                    "book_name": pdf_path.name,
                    "chunk_id": i,
                    "chunk_count": len(chunks)
                }
            )
            
            points.append(point)
        
        # إضافة النقاط إلى مجموعة Qdrant
        try:
            client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info(f"✅ تمت إضافة {len(points)} نقطة من {pdf_path.name} إلى مجموعة {collection_name}.")
        
        except Exception as e:
            logger.error(f"❌ فشل إضافة نقاط من {pdf_path.name}: {str(e)}")

# وظيفة مشتركة لتحميل الكتب في مجموعة محددة
def process_books_category(client: qdrant_client.QdrantClient, 
                          directory: Path, 
                          collection_name: str, 
                          category_name: str):
    """
    معالجة وفهرسة كتب فئة معينة
    
    Args:
        client (qdrant_client.QdrantClient): عميل Qdrant
        directory (Path): مسار مجلد الكتب
        collection_name (str): اسم المجموعة في Qdrant
        category_name (str): اسم فئة الكتب
    """
    if not directory.exists():
        logger.warning(f"⚠️ مجلد {directory} غير موجود. تخطي معالجة كتب {category_name}.")
        return
    
    logger.info(f"بدء معالجة كتب {category_name}...")
    
    # تحميل نموذج التضمين
    embedding_model = load_embedding_model()
    
    # الحصول على قائمة ملفات PDF في المجلد
    pdf_files = list(directory.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"⚠️ لا توجد ملفات PDF في {directory}")
        return
    
    logger.info(f"معالجة {len(pdf_files)} ملف PDF في مجلد {category_name}...")
    
    # معالجة كل ملف PDF
    for pdf_file in tqdm(pdf_files, desc=f"معالجة كتب {category_name}"):
        try:
            # استخراج معلومات الكتاب من اسم الملف
            file_name = pdf_file.stem
            author, title = "غير معروف", file_name
            
            if " - " in file_name:
                parts = file_name.split(" - ", 1)
                if len(parts) == 2:
                    author, title = parts
            
            # استخراج النص من ملف PDF
            text = extract_text_from_pdf(pdf_file)
            
            if not text:
                logger.warning(f"⚠️ لم يتم استخراج أي نص من {pdf_file}")
                continue
            
            # تقسيم النص إلى مقاطع
            chunks = split_text_into_chunks(text)
            
            logger.info(f"تم تقسيم {pdf_file.name} إلى {len(chunks)} مقطع")
            
            # معالجة كل مقطع نصي
            points_to_upsert = []
            
            for i, chunk in enumerate(chunks):
                # تجنب المقاطع الفارغة أو القصيرة جداً
                if len(chunk.strip()) < 50:
                    continue
                
                # إنشاء معرف فريد لهذا المقطع
                point_id = f"{file_name.replace(' ', '_')}_{i}"
                
                # تضمين النص
                embedding = embedding_model.encode(chunk).tolist()
                
                # إنشاء نقطة البيانات
                point = models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "book_title": title,
                        "author": author,
                        "category": category_name,
                        "file_name": pdf_file.name,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                )
                
                points_to_upsert.append(point)
            
            # تحميل المقاطع إلى Qdrant
            if points_to_upsert:
                client.upsert(
                    collection_name=collection_name,
                    points=points_to_upsert
                )
                
                logger.info(f"✅ تم تحميل {len(points_to_upsert)} مقطع من {pdf_file.name} إلى مجموعة {collection_name}")
        
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة {pdf_file}: {str(e)}")
            traceback.print_exc()
    
    logger.info(f"✅ اكتملت معالجة كتب {category_name}!")

# معالجة كتب العقيدة
def process_aqeedah_books(client: qdrant_client.QdrantClient):
    """
    معالجة وفهرسة كتب العقيدة
    
    Args:
        client (qdrant_client.QdrantClient): عميل Qdrant
    """
    process_books_category(
        client=client,
        directory=AQEEDAH_DIR,
        collection_name=COLLECTION_NAMES["aqeedah"],
        category_name="العقيدة"
    )

# معالجة كتب الفقه
def process_fiqh_books(client: qdrant_client.QdrantClient):
    """
    معالجة وفهرسة كتب الفقه
    
    Args:
        client (qdrant_client.QdrantClient): عميل Qdrant
    """
    process_books_category(
        client=client,
        directory=FIQH_DIR,
        collection_name=COLLECTION_NAMES["fiqh"],
        category_name="الفقه"
    )

# معالجة كتب التفسير
def process_tafsir_books(client: qdrant_client.QdrantClient):
    """
    معالجة وفهرسة كتب التفسير
    
    Args:
        client (qdrant_client.QdrantClient): عميل Qdrant
    """
    process_books_category(
        client=client,
        directory=TAFSIR_BOOKS_DIR,
        collection_name=COLLECTION_NAMES["tafsir"],
        category_name="التفسير"
    )

# معالجة كتب الحديث
def process_hadith_books(client: qdrant_client.QdrantClient):
    """
    معالجة وفهرسة كتب الحديث
    
    Args:
        client (qdrant_client.QdrantClient): عميل Qdrant
    """
    process_books_category(
        client=client,
        directory=HADITH_DIR,
        collection_name=COLLECTION_NAMES["hadith"],
        category_name="الحديث"
    )

# معالجة كتب السيرة النبوية
def process_seerah_books(client: qdrant_client.QdrantClient):
    """
    معالجة وفهرسة كتب السيرة النبوية
    
    Args:
        client (qdrant_client.QdrantClient): عميل Qdrant
    """
    process_books_category(
        client=client,
        directory=SEERAH_DIR,
        collection_name=COLLECTION_NAMES["seerah"],
        category_name="السيرة النبوية"
    )

# معالجة كتب الأخلاق
def process_akhlaq_books(client: qdrant_client.QdrantClient):
    """
    معالجة وفهرسة كتب الأخلاق
    
    Args:
        client (qdrant_client.QdrantClient): عميل Qdrant
    """
    process_books_category(
        client=client,
        directory=AKHLAQ_DIR,
        collection_name=COLLECTION_NAMES["akhlaq"],
        category_name="الأخلاق"
    )

# معالجة كتب التاريخ الإسلامي
def process_history_books(client: qdrant_client.QdrantClient):
    """
    معالجة وفهرسة كتب التاريخ الإسلامي
    
    Args:
        client (qdrant_client.QdrantClient): عميل Qdrant
    """
    process_books_category(
        client=client,
        directory=HISTORY_DIR,
        collection_name=COLLECTION_NAMES["history"],
        category_name="التاريخ الإسلامي"
    )

# معالجة كتب الفتاوى
def process_fatawa_books(client: qdrant_client.QdrantClient):
    """
    معالجة وفهرسة كتب الفتاوى
    
    Args:
        client (qdrant_client.QdrantClient): عميل Qdrant
    """
    process_books_category(
        client=client,
        directory=FATAWA_DIR,
        collection_name=COLLECTION_NAMES["fatawa"],
        category_name="الفتاوى"
    )

if __name__ == "__main__":
    main()
