#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار معالجة ملفات الصوت والفيديو للتأكد من صحة عملها
"""

import os
import sys
import logging
import argparse
from pathlib import Path
import dotenv
import json

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MediaProcessing-Test")

# تحميل متغيرات البيئة
dotenv.load_dotenv()

# تحديد المسارات المهمة
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = BASE_DIR / "data"
AUDIO_DIR = DATA_DIR / "audio"
VIDEO_DIR = DATA_DIR / "video"
TEMP_DIR = DATA_DIR / "temp"

# التأكد من وجود المجلدات
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def test_audio_processing(audio_file=None):
    """
    اختبار معالجة الملفات الصوتية
    
    Args:
        audio_file: مسار الملف الصوتي للاختبار (اختياري)
    """
    logger.info("== بدء اختبار معالجة الملفات الصوتية ==")
    
    try:
        # استيراد معالج الملفات الصوتية
        sys.path.append(str(BASE_DIR))
        from core.media_processors.audio_processor import AudioProcessor
        
        # إنشاء كائن معالج الصوت
        audio_processor = AudioProcessor(language="ar-AR")
        logger.info("✅ تم إنشاء معالج الصوت بنجاح")
        
        # تحديد ملف الصوت للاختبار
        if audio_file is None:
            # البحث عن ملف صوتي في مجلد الصوت
            audio_files = list(AUDIO_DIR.glob("*.mp3")) + list(AUDIO_DIR.glob("*.wav"))
            if audio_files:
                audio_file = str(audio_files[0])
                logger.info(f"🔍 تم العثور على ملف صوتي للاختبار: {audio_file}")
            else:
                logger.error("❌ لم يتم العثور على ملفات صوتية للاختبار")
                logger.info("ℹ️ يرجى تشغيل سكريبت setup_data.py لتحميل ملفات صوتية نموذجية أو تحميل ملفات صوتية يدويًا")
                return False
        
        # التحقق من وجود الملف
        if not os.path.exists(audio_file):
            logger.error(f"❌ ملف الصوت غير موجود: {audio_file}")
            return False
        
        # محاولة استخراج النص من الملف الصوتي
        logger.info(f"🔍 جاري استخراج النص من الملف الصوتي: {audio_file}")
        result = audio_processor.extract_text_from_file(audio_file)
        
        if result.get("success", False):
            logger.info(f"✅ تم استخراج النص بنجاح: {result.get('text', '')[:100]}...")
            
            # حفظ النتائج في ملف
            output_file = TEMP_DIR / "audio_extraction_result.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            logger.info(f"✅ تم حفظ النتائج في: {output_file}")
            
            return True
        else:
            logger.error(f"❌ فشل استخراج النص: {result.get('error', 'خطأ غير معروف')}")
            return False
            
    except ImportError:
        logger.error("❌ لم يتم العثور على معالج الصوت، تأكد من تشغيل run_local.py لإنشاء الملفات اللازمة")
        return False
    except Exception as e:
        logger.error(f"❌ خطأ أثناء اختبار معالجة الصوت: {str(e)}")
        return False

def test_video_processing(video_file=None):
    """
    اختبار معالجة ملفات الفيديو
    
    Args:
        video_file: مسار ملف الفيديو للاختبار (اختياري)
    """
    logger.info("== بدء اختبار معالجة ملفات الفيديو ==")
    
    try:
        # استيراد معالج ملفات الفيديو
        sys.path.append(str(BASE_DIR))
        from core.media_processors.video_processor import VideoProcessor
        
        # إنشاء كائن معالج الفيديو
        video_processor = VideoProcessor()
        logger.info("✅ تم إنشاء معالج الفيديو بنجاح")
        
        # تحديد ملف الفيديو للاختبار
        if video_file is None:
            # البحث عن ملف فيديو في مجلد الفيديو
            video_files = list(VIDEO_DIR.glob("*.mp4")) + list(VIDEO_DIR.glob("*.avi")) + list(VIDEO_DIR.glob("*.mkv"))
            if video_files:
                video_file = str(video_files[0])
                logger.info(f"🔍 تم العثور على ملف فيديو للاختبار: {video_file}")
            else:
                logger.error("❌ لم يتم العثور على ملفات فيديو للاختبار")
                logger.info("ℹ️ يرجى تشغيل سكريبت setup_data.py لتحميل ملفات فيديو نموذجية أو تحميل ملفات فيديو يدويًا")
                return False
        
        # التحقق من وجود الملف
        if not os.path.exists(video_file):
            logger.error(f"❌ ملف الفيديو غير موجود: {video_file}")
            return False
        
        # 1. اختبار استخراج الإطارات
        logger.info(f"🔍 جاري استخراج الإطارات من ملف الفيديو: {video_file}")
        frames_dir = TEMP_DIR / "video_frames"
        frames_result = video_processor.extract_frames(video_file, str(frames_dir))
        
        if frames_result.get("success", False):
            logger.info(f"✅ تم استخراج {frames_result.get('frame_count', 0)} إطار بنجاح")
            
            # حفظ معلومات الإطارات
            frames_info_file = TEMP_DIR / "video_frames_info.json"
            with open(frames_info_file, 'w', encoding='utf-8') as f:
                # إزالة مسارات الإطارات لتوفير المساحة
                info = frames_result.copy()
                info.pop("frame_paths", None)
                json.dump(info, f, ensure_ascii=False, indent=4)
            logger.info(f"✅ تم حفظ معلومات الإطارات في: {frames_info_file}")
        else:
            logger.error(f"❌ فشل استخراج الإطارات: {frames_result.get('error', 'خطأ غير معروف')}")
            return False
        
        # 2. اختبار استخراج النص من الفيديو
        logger.info(f"🔍 جاري استخراج النص من ملف الفيديو: {video_file}")
        text_result = video_processor.extract_text_from_video(video_file)
        
        if text_result.get("success", False):
            logger.info(f"✅ تم استخراج النص بنجاح: {text_result.get('text', '')[:100]}...")
            
            # حفظ النص المستخرج
            text_file = TEMP_DIR / "video_extracted_text.json"
            with open(text_file, 'w', encoding='utf-8') as f:
                json.dump(text_result, f, ensure_ascii=False, indent=4)
            logger.info(f"✅ تم حفظ النص المستخرج في: {text_file}")
        else:
            logger.warning(f"⚠️ فشل استخراج النص من الفيديو: {text_result.get('error', 'خطأ غير معروف')}")
            logger.info("ℹ️ هذا قد يكون بسبب عدم وجود نص في الفيديو أو عدم تثبيت pytesseract")
        
        # 3. اختبار استخراج الصوت من الفيديو
        logger.info(f"🔍 جاري استخراج الصوت من ملف الفيديو: {video_file}")
        audio_output = TEMP_DIR / "extracted_audio.wav"
        audio_result = video_processor.extract_audio_from_video(video_file, str(audio_output))
        
        if audio_result.get("success", False):
            logger.info(f"✅ تم استخراج الصوت بنجاح: {audio_result.get('audio_path', '')}")
            
            # محاولة استخراج النص من الصوت المستخرج
            if test_audio_processing(audio_result.get('audio_path')):
                logger.info("✅ تم استخراج النص من الصوت المستخرج من الفيديو بنجاح")
        else:
            logger.warning(f"⚠️ فشل استخراج الصوت من الفيديو: {audio_result.get('error', 'خطأ غير معروف')}")
            logger.info("ℹ️ هذا قد يكون بسبب عدم وجود صوت في الفيديو أو عدم تثبيت ffmpeg")
        
        return True
        
    except ImportError:
        logger.error("❌ لم يتم العثور على معالج الفيديو، تأكد من تشغيل run_local.py لإنشاء الملفات اللازمة")
        return False
    except Exception as e:
        logger.error(f"❌ خطأ أثناء اختبار معالجة الفيديو: {str(e)}")
        return False

def main():
    """الدالة الرئيسية للاختبار"""
    parser = argparse.ArgumentParser(description="اختبار معالجة ملفات الصوت والفيديو")
    parser.add_argument("--audio", help="مسار ملف صوتي لاختباره")
    parser.add_argument("--video", help="مسار ملف فيديو لاختباره")
    parser.add_argument("--all", action="store_true", help="اختبار كل من معالجة الصوت والفيديو")
    parser.add_argument("--audio-only", action="store_true", help="اختبار معالجة الصوت فقط")
    parser.add_argument("--video-only", action="store_true", help="اختبار معالجة الفيديو فقط")
    
    args = parser.parse_args()
    
    logger.info("🚀 بدء اختبار معالجة ملفات الوسائط")
    
    # تحديد ما سيتم اختباره
    test_audio = args.all or args.audio_only or args.audio
    test_video = args.all or args.video_only or args.video
    
    # إذا لم يتم تحديد أي خيار، اختبر كل شيء
    if not (test_audio or test_video):
        test_audio = test_video = True
    
    # إجراء الاختبارات
    results = []
    
    if test_audio:
        audio_success = test_audio_processing(args.audio)
        results.append(("معالجة الصوت", audio_success))
    
    if test_video:
        video_success = test_video_processing(args.video)
        results.append(("معالجة الفيديو", video_success))
    
    # عرض ملخص النتائج
    logger.info("== ملخص نتائج الاختبار ==")
    all_success = True
    
    for name, success in results:
        status = "✅ نجاح" if success else "❌ فشل"
        logger.info(f"{name}: {status}")
        all_success = all_success and success
    
    if all_success:
        logger.info("🎉 جميع الاختبارات نجحت!")
    else:
        logger.warning("⚠️ فشلت بعض الاختبارات، راجع السجل أعلاه للتفاصيل")
    
    logger.info(f"📁 يمكنك العثور على ملفات نتائج الاختبار في: {TEMP_DIR}")

if __name__ == "__main__":
    main()
