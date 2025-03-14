#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
تشغيل محلي لمساعد القرآن الذكي - نسخة محلية للتطوير والاختبار
"""

import os
import sys
import streamlit as st
import dotenv
import logging
from pathlib import Path
import subprocess
import signal
import time

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("QuranAssistant-Local")

# تحميل متغيرات البيئة
dotenv.load_dotenv()

def check_dependencies():
    """التحقق من وجود التبعيات المطلوبة وتثبيتها إذا لزم الأمر"""
    
    try:
        import streamlit
        import ollama
        from sentence_transformers import SentenceTransformer
        import qdrant_client
        import fitz  # PyMuPDF
        import pandas as pd
        import nltk
        import matplotlib.pyplot as plt
        import numpy as np
        import cv2  # لمعالجة الفيديو
        import speech_recognition as sr  # لمعالجة الصوت
        
        logger.info("✅ جميع التبعيات متوفرة")
        return True
    except ImportError as e:
        missing_package = str(e).split("'")[1]
        logger.error(f"❌ مكتبة مفقودة: {missing_package}")
        
        if input(f"هل ترغب في تثبيت {missing_package}? (y/n): ").lower() == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install", missing_package])
            logger.info(f"✅ تم تثبيت {missing_package}")
            return check_dependencies()
        else:
            logger.error("❌ لم يتم تثبيت جميع التبعيات المطلوبة")
            return False

def check_ollama():
    """التحقق من تشغيل Ollama"""
    try:
        import ollama
        models = ollama.list()
        logger.info(f"✅ Ollama يعمل، النماذج المتوفرة: {len(models['models'])}")
        return True
    except Exception as e:
        logger.error(f"❌ خطأ في الاتصال بـ Ollama: {str(e)}")
        logger.info("ℹ️ تأكد من تثبيت وتشغيل Ollama: https://ollama.ai/download")
        return False

def check_data_directories():
    """التحقق من وجود مجلدات البيانات وإنشائها إذا لزم الأمر"""
    base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    data_dirs = [
        base_dir / "data",
        base_dir / "data" / "quran",
        base_dir / "data" / "tafseer",
        base_dir / "data" / "miracles",
        base_dir / "data" / "audio",
        base_dir / "data" / "video",
        base_dir / "data" / "temp"
    ]
    
    for data_dir in data_dirs:
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ تم إنشاء مجلد: {data_dir}")
    
    logger.info("✅ جميع مجلدات البيانات متوفرة")
    return True

def run_streamlit():
    """تشغيل تطبيق Streamlit"""
    app_path = Path(os.path.dirname(os.path.abspath(__file__))) / "app.py"
    
    if not app_path.exists():
        logger.error(f"❌ ملف التطبيق غير موجود: {app_path}")
        return False
    
    # تشغيل Streamlit
    logger.info(f"🚀 جاري تشغيل التطبيق: {app_path}")
    
    try:
        # تخزين عملية Streamlit لإيقافها لاحقًا
        streamlit_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port=8501"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # فتح المتصفح (اختياري)
        import webbrowser
        webbrowser.open("http://localhost:8501")
        
        logger.info("✅ تم تشغيل التطبيق بنجاح، يمكنك فتح المتصفح على العنوان: http://localhost:8501")
        
        # الانتظار للضغط على Ctrl+C
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("⏹️ جاري إيقاف التطبيق...")
            streamlit_process.send_signal(signal.SIGTERM)
            streamlit_process.wait()
            logger.info("✅ تم إيقاف التطبيق بنجاح")
        
        return True
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل التطبيق: {str(e)}")
        return False

def check_audio_video_support():
    """التحقق من دعم الصوت والفيديو"""
    audio_support = False
    video_support = False
    
    # التحقق من دعم الصوت
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        audio_support = True
        logger.info("✅ يدعم النظام معالجة الملفات الصوتية")
    except Exception as e:
        logger.warning(f"⚠️ دعم الصوت غير متوفر: {str(e)}")
        logger.info("ℹ️ قم بتثبيت SpeechRecognition: pip install SpeechRecognition")
    
    # التحقق من دعم الفيديو
    try:
        import cv2
        video_support = True
        logger.info("✅ يدعم النظام معالجة ملفات الفيديو")
    except Exception as e:
        logger.warning(f"⚠️ دعم الفيديو غير متوفر: {str(e)}")
        logger.info("ℹ️ قم بتثبيت OpenCV: pip install opencv-python")
    
    return audio_support, video_support

def setup_audio_processor():
    """إعداد معالج الملفات الصوتية"""
    # إذا لم يكن المعالج موجودًا، قم بإنشائه
    audio_processor_path = Path(os.path.dirname(os.path.abspath(__file__))) / "core" / "media_processors" / "audio_processor.py"
    
    if not audio_processor_path.exists():
        # إنشاء الدليل إذا لم يكن موجودًا
        audio_processor_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(audio_processor_path, 'w', encoding='utf-8') as f:
            f.write("""#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
معالج الملفات الصوتية - للتعامل مع المدخلات الصوتية واستخراج النصوص
\"\"\"

import os
import speech_recognition as sr
from typing import Dict, List, Any, Optional, Tuple
import logging
import tempfile
import subprocess
from pathlib import Path

class AudioProcessor:
    \"\"\"
    معالج للملفات الصوتية، يستخرج النص من الملفات الصوتية
    \"\"\"
    
    def __init__(self, language: str = "ar-AR"):
        \"\"\"
        تهيئة معالج الملفات الصوتية
        
        Args:
            language: رمز اللغة المستخدمة للتعرف على الكلام
        \"\"\"
        self.recognizer = sr.Recognizer()
        self.language = language
        self.logger = logging.getLogger("AudioProcessor")
    
    def extract_text_from_file(self, audio_file_path: str) -> Dict[str, Any]:
        \"\"\"
        استخراج النص من ملف صوتي
        
        Args:
            audio_file_path: مسار الملف الصوتي
        
        Returns:
            قاموس يحتوي على النص المستخرج ومعلومات إضافية
        \"\"\"
        if not os.path.exists(audio_file_path):
            self.logger.error(f"الملف غير موجود: {audio_file_path}")
            return {"success": False, "error": "الملف غير موجود"}
        
        try:
            # التحويل إلى WAV إذا لم يكن كذلك
            wav_file = self._convert_to_wav(audio_file_path)
            
            # استخراج النص
            with sr.AudioFile(wav_file) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language=self.language)
                
                return {
                    "success": True,
                    "text": text,
                    "language": self.language,
                    "duration": self._get_audio_duration(wav_file),
                    "file_path": audio_file_path
                }
        except sr.UnknownValueError:
            self.logger.warning(f"لم يتم التعرف على الكلام في الملف: {audio_file_path}")
            return {"success": False, "error": "لم يتم التعرف على الكلام"}
        except sr.RequestError as e:
            self.logger.error(f"خطأ في خدمة التعرف على الكلام: {str(e)}")
            return {"success": False, "error": f"خطأ في خدمة التعرف على الكلام: {str(e)}"}
        except Exception as e:
            self.logger.error(f"خطأ غير متوقع: {str(e)}")
            return {"success": False, "error": f"خطأ غير متوقع: {str(e)}"}
    
    def _convert_to_wav(self, audio_file_path: str) -> str:
        \"\"\"
        تحويل الملف الصوتي إلى تنسيق WAV إذا لم يكن كذلك
        
        Args:
            audio_file_path: مسار الملف الصوتي
        
        Returns:
            مسار ملف WAV
        \"\"\"
        # إذا كان الملف بالفعل بتنسيق WAV
        if audio_file_path.lower().endswith('.wav'):
            return audio_file_path
        
        # تحويل الملف إلى WAV
        out_path = tempfile.gettempdir() + os.sep + os.path.basename(audio_file_path) + ".wav"
        
        try:
            # استخدام ffmpeg للتحويل
            subprocess.call(['ffmpeg', '-i', audio_file_path, out_path], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
            return out_path
        except Exception as e:
            self.logger.error(f"خطأ في تحويل الملف الصوتي: {str(e)}")
            # إذا فشل التحويل، نستخدم الملف الأصلي (قد لا يعمل)
            return audio_file_path
    
    def _get_audio_duration(self, audio_file_path: str) -> float:
        \"\"\"
        الحصول على مدة الملف الصوتي بالثواني
        
        Args:
            audio_file_path: مسار الملف الصوتي
        
        Returns:
            مدة الملف الصوتي بالثواني
        \"\"\"
        try:
            with sr.AudioFile(audio_file_path) as source:
                return source.DURATION
        except Exception:
            return 0.0
    
    def record_from_microphone(self, duration: int = 5) -> Dict[str, Any]:
        \"\"\"
        تسجيل الصوت من الميكروفون
        
        Args:
            duration: مدة التسجيل بالثواني
        
        Returns:
            قاموس يحتوي على النص المستخرج ومعلومات إضافية
        \"\"\"
        try:
            with sr.Microphone() as source:
                self.logger.info(f"جاري التسجيل لمدة {duration} ثواني...")
                audio_data = self.recognizer.record(source, duration=duration)
                
                # استخراج النص
                text = self.recognizer.recognize_google(audio_data, language=self.language)
                
                return {
                    "success": True,
                    "text": text,
                    "language": self.language,
                    "duration": duration,
                    "source": "microphone"
                }
        except Exception as e:
            self.logger.error(f"خطأ في التسجيل من الميكروفون: {str(e)}")
            return {"success": False, "error": f"خطأ في التسجيل: {str(e)}"}
""")
        logger.info(f"✅ تم إنشاء معالج الملفات الصوتية: {audio_processor_path}")
    else:
        logger.info(f"✅ معالج الملفات الصوتية موجود: {audio_processor_path}")

def setup_video_processor():
    """إعداد معالج ملفات الفيديو"""
    # إذا لم يكن المعالج موجودًا، قم بإنشائه
    video_processor_path = Path(os.path.dirname(os.path.abspath(__file__))) / "core" / "media_processors" / "video_processor.py"
    
    if not video_processor_path.exists():
        # إنشاء الدليل إذا لم يكن موجودًا
        video_processor_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(video_processor_path, 'w', encoding='utf-8') as f:
            f.write("""#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
معالج ملفات الفيديو - للتعامل مع ملفات الفيديو واستخراج النصوص والصور
\"\"\"

import os
import cv2
import tempfile
import subprocess
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional, Tuple
import json
import time

class VideoProcessor:
    \"\"\"
    معالج لملفات الفيديو، يستخرج الإطارات والنصوص من ملفات الفيديو
    \"\"\"
    
    def __init__(self):
        \"\"\"
        تهيئة معالج ملفات الفيديو
        \"\"\"
        self.logger = logging.getLogger("VideoProcessor")
    
    def extract_frames(self, video_path: str, output_dir: Optional[str] = None, 
                      frame_rate: int = 1) -> Dict[str, Any]:
        \"\"\"
        استخراج إطارات من ملف فيديو
        
        Args:
            video_path: مسار ملف الفيديو
            output_dir: مجلد الإخراج للإطارات (اختياري)
            frame_rate: معدل استخراج الإطارات (إطار لكل X ثانية)
        
        Returns:
            قاموس يحتوي على معلومات الإطارات المستخرجة
        \"\"\"
        if not os.path.exists(video_path):
            self.logger.error(f"الملف غير موجود: {video_path}")
            return {"success": False, "error": "الملف غير موجود"}
        
        try:
            # إنشاء مجلد الإخراج إذا لم يكن متوفرًا
            if output_dir is None:
                output_dir = tempfile.mkdtemp()
            else:
                os.makedirs(output_dir, exist_ok=True)
            
            # فتح ملف الفيديو
            video = cv2.VideoCapture(video_path)
            
            # الحصول على معلومات الفيديو
            fps = video.get(cv2.CAP_PROP_FPS)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            # حساب عدد الإطارات التي سيتم استخراجها
            frame_interval = int(fps * frame_rate)
            
            # استخراج الإطارات
            count = 0
            frame_count = 0
            frame_paths = []
            
            while True:
                ret, frame = video.read()
                
                if not ret:
                    break
                
                if count % frame_interval == 0:
                    frame_path = os.path.join(output_dir, f"frame_{frame_count:04d}.jpg")
                    cv2.imwrite(frame_path, frame)
                    frame_paths.append(frame_path)
                    frame_count += 1
                
                count += 1
            
            # إغلاق الفيديو
            video.release()
            
            return {
                "success": True,
                "frame_count": frame_count,
                "frame_paths": frame_paths,
                "output_dir": output_dir,
                "fps": fps,
                "duration": duration,
                "total_frames": total_frames
            }
        except Exception as e:
            self.logger.error(f"خطأ في استخراج الإطارات: {str(e)}")
            return {"success": False, "error": f"خطأ في استخراج الإطارات: {str(e)}"}
    
    def extract_text_from_video(self, video_path: str, language: str = "ar") -> Dict[str, Any]:
        \"\"\"
        استخراج النص من ملف فيديو باستخدام OCR
        
        Args:
            video_path: مسار ملف الفيديو
            language: لغة النص
        
        Returns:
            قاموس يحتوي على النص المستخرج
        \"\"\"
        try:
            # استخراج الإطارات
            frames_result = self.extract_frames(video_path, frame_rate=5)
            
            if not frames_result["success"]:
                return frames_result
            
            # فحص وجود مكتبة pytesseract
            try:
                import pytesseract
                has_tesseract = True
            except ImportError:
                has_tesseract = False
                self.logger.warning("مكتبة pytesseract غير متوفرة، لن يتم استخراج النص")
                return {
                    "success": False, 
                    "error": "مكتبة pytesseract غير متوفرة، قم بتثبيتها باستخدام: pip install pytesseract"
                }
            
            # استخراج النص من الإطارات
            texts = []
            
            for frame_path in frames_result["frame_paths"]:
                img = cv2.imread(frame_path)
                text = pytesseract.image_to_string(img, lang=language)
                
                if text.strip():
                    texts.append(text)
            
            # دمج النصوص المستخرجة
            combined_text = " ".join(texts)
            
            return {
                "success": True,
                "text": combined_text,
                "frame_count": frames_result["frame_count"],
                "duration": frames_result["duration"]
            }
        except Exception as e:
            self.logger.error(f"خطأ في استخراج النص من الفيديو: {str(e)}")
            return {"success": False, "error": f"خطأ في استخراج النص: {str(e)}"}
    
    def extract_audio_from_video(self, video_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        \"\"\"
        استخراج الصوت من ملف فيديو
        
        Args:
            video_path: مسار ملف الفيديو
            output_path: مسار ملف الصوت الناتج (اختياري)
        
        Returns:
            قاموس يحتوي على معلومات ملف الصوت
        \"\"\"
        if not os.path.exists(video_path):
            self.logger.error(f"الملف غير موجود: {video_path}")
            return {"success": False, "error": "الملف غير موجود"}
        
        try:
            # تحديد مسار الإخراج
            if output_path is None:
                output_path = os.path.splitext(video_path)[0] + ".wav"
            
            # استخدام ffmpeg لاستخراج الصوت
            subprocess.call(['ffmpeg', '-i', video_path, '-y', '-q:a', '0', '-map', 'a', output_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(output_path):
                return {
                    "success": True,
                    "audio_path": output_path
                }
            else:
                return {
                    "success": False,
                    "error": "فشل في استخراج الصوت"
                }
        except Exception as e:
            self.logger.error(f"خطأ في استخراج الصوت من الفيديو: {str(e)}")
            return {"success": False, "error": f"خطأ في استخراج الصوت: {str(e)}"}
""")
        logger.info(f"✅ تم إنشاء معالج ملفات الفيديو: {video_processor_path}")
    else:
        logger.info(f"✅ معالج ملفات الفيديو موجود: {video_processor_path}")

def main():
    """الدالة الرئيسية للتشغيل المحلي"""
    logger.info("🚀 بدء تشغيل مساعد القرآن الذكي نسخة محلية")
    
    # التحقق من التبعيات
    if not check_dependencies():
        logger.error("❌ فشل في التحقق من التبعيات")
        return
    
    # التحقق من Ollama
    if not check_ollama():
        logger.warning("⚠️ Ollama غير متوفر، قد لا تعمل بعض وظائف المشروع")
    
    # التحقق من مجلدات البيانات
    if not check_data_directories():
        logger.error("❌ فشل في إعداد مجلدات البيانات")
        return
    
    # التحقق من دعم الصوت والفيديو
    audio_support, video_support = check_audio_video_support()
    
    # إعداد معالجات الصوت والفيديو
    if audio_support:
        setup_audio_processor()
    
    if video_support:
        setup_video_processor()
    
    # تشغيل التطبيق
    run_streamlit()

if __name__ == "__main__":
    main()
