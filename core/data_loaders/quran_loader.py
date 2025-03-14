"""
محمل بيانات القرآن - يوفر وظائف لتحميل وإدارة بيانات القرآن والتفسير والمعجزات العلمية
"""
import os
import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union

class QuranLoader:
    """
    محمل بيانات القرآن - يقوم بإدارة تنزيل وتخزين وتحميل وتجهيز بيانات القرآن
    """
    
    def __init__(self, data_dir: str = None):
        """
        تهيئة محمل بيانات القرآن

        Args:
            data_dir: مسار مجلد البيانات (اختياري)
        """
        if data_dir is None:
            # استخدام المجلد الافتراضي إذا لم يتم تحديد مجلد
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        else:
            self.data_dir = data_dir
        
        # التأكد من وجود مجلد البيانات
        self.quran_dir = os.path.join(self.data_dir, "quran")
        os.makedirs(self.quran_dir, exist_ok=True)
        
        # تحديد مسارات الملفات
        self.quran_file = os.path.join(self.quran_dir, "quran.json")
        self.tafseer_file = os.path.join(self.quran_dir, "tafseer.json")
        self.scientific_miracles_file = os.path.join(self.quran_dir, "scientific_miracles.json")
    
    def download_quran_text(self, edition: str = "ar.asad") -> List[Dict[str, Any]]:
        """
        تنزيل نص القرآن الكريم من API

        Args:
            edition: إصدار القرآن (افتراضيًا: ar.asad)

        Returns:
            قائمة من السور مع الآيات
        """
        try:
            # التحقق مما إذا كان الملف موجودًا بالفعل
            if os.path.exists(self.quran_file):
                with open(self.quran_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # تنزيل البيانات من API
            url = f"https://api.alquran.cloud/v1/quran/{edition}"
            response = requests.get(url)
            response.raise_for_status()  # رفع استثناء إذا فشل الطلب
            
            data = response.json()
            surahs = data.get("data", {}).get("surahs", [])
            
            # حفظ البيانات في ملف
            with open(self.quran_file, 'w', encoding='utf-8') as f:
                json.dump(surahs, f, ensure_ascii=False, indent=4)
            
            return surahs
        
        except Exception as e:
            print(f"خطأ في تنزيل نص القرآن: {str(e)}")
            # إذا حدث خطأ ولكن الملف موجود، قم بتحميله
            if os.path.exists(self.quran_file):
                with open(self.quran_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
    
    def download_tafseer(self, tafseer_name: str = "ar.muyassar", 
                        surah_range: Tuple[int, int] = (1, 114), 
                        ayah_range: Tuple[int, Optional[int]] = (1, None)) -> List[Dict[str, Any]]:
        """
        تنزيل تفسير القرآن الكريم من API

        Args:
            tafseer_name: اسم التفسير (افتراضيًا: ar.muyassar)
            surah_range: نطاق السور للتنزيل (من، إلى) - بشكل افتراضي كل السور
            ayah_range: نطاق الآيات للتنزيل (من، إلى) - بشكل افتراضي كل الآيات

        Returns:
            قائمة من تفاسير الآيات
        """
        try:
            # التحقق مما إذا كان الملف موجودًا بالفعل
            if os.path.exists(self.tafseer_file):
                with open(self.tafseer_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # تنزيل التفسير من API
            tafseer_data = []
            
            # نطاق السور (الافتراضي: 1-114)
            start_surah, end_surah = surah_range
            
            # تنزيل التفسير لكل سورة وآية
            for surah in range(start_surah, end_surah + 1):
                # الحصول على عدد الآيات في هذه السورة
                quran_data = self.download_quran_text()
                if not quran_data:
                    continue
                
                # العثور على السورة المناسبة
                surah_data = None
                for s in quran_data:
                    if s.get("number") == surah:
                        surah_data = s
                        break
                
                if not surah_data:
                    continue
                
                # عدد الآيات في السورة
                ayah_count = len(surah_data.get("ayahs", []))
                
                # نطاق الآيات (الافتراضي: كل الآيات في السورة)
                start_ayah = ayah_range[0]
                end_ayah = ayah_range[1] if ayah_range[1] is not None else ayah_count
                
                # تنزيل التفسير لكل آية
                for ayah in range(start_ayah, min(end_ayah + 1, ayah_count + 1)):
                    url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/{tafseer_name}"
                    response = requests.get(url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        ayah_data = data.get("data", {})
                        
                        tafseer_item = {
                            "sura": surah,
                            "ayah": ayah,
                            "text": ayah_data.get("text", "")
                        }
                        
                        tafseer_data.append(tafseer_item)
            
            # حفظ البيانات في ملف
            with open(self.tafseer_file, 'w', encoding='utf-8') as f:
                json.dump(tafseer_data, f, ensure_ascii=False, indent=4)
            
            return tafseer_data
        
        except Exception as e:
            print(f"خطأ في تنزيل التفسير: {str(e)}")
            # إذا حدث خطأ ولكن الملف موجود، قم بتحميله
            if os.path.exists(self.tafseer_file):
                with open(self.tafseer_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
    
    def load_scientific_miracles(self) -> List[Dict[str, Any]]:
        """
        تحميل المعجزات العلمية في القرآن

        Returns:
            قائمة من المعجزات العلمية
        """
        try:
            # التحقق مما إذا كان الملف موجودًا
            if os.path.exists(self.scientific_miracles_file):
                with open(self.scientific_miracles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # إنشاء ملف فارغ إذا لم يكن موجودًا
                with open(self.scientific_miracles_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=4)
                return []
        
        except Exception as e:
            print(f"خطأ في تحميل المعجزات العلمية: {str(e)}")
            return []
    
    def add_scientific_miracle(self, miracle: Dict[str, Any]) -> bool:
        """
        إضافة معجزة علمية جديدة إلى القاعدة

        Args:
            miracle: بيانات المعجزة العلمية (عنوان، آية، سورة، رقم الآية، شرح)

        Returns:
            نجاح العملية
        """
        try:
            # تحميل المعجزات الموجودة
            miracles = self.load_scientific_miracles()
            
            # إضافة المعجزة الجديدة
            miracles.append(miracle)
            
            # حفظ القائمة المحدثة
            with open(self.scientific_miracles_file, 'w', encoding='utf-8') as f:
                json.dump(miracles, f, ensure_ascii=False, indent=4)
            
            return True
        
        except Exception as e:
            print(f"خطأ في إضافة معجزة علمية: {str(e)}")
            return False
    
    def search_quran(self, query: str) -> List[Dict[str, Any]]:
        """
        البحث في القرآن عن نص معين

        Args:
            query: نص البحث

        Returns:
            قائمة الآيات المطابقة
        """
        results = []
        
        try:
            # تحميل بيانات القرآن
            quran_data = self.download_quran_text()
            
            # البحث في كل سورة وآية
            for surah in quran_data:
                surah_name = surah.get("name", "")
                surah_number = surah.get("number", 0)
                
                for ayah in surah.get("ayahs", []):
                    ayah_text = ayah.get("text", "")
                    ayah_number = ayah.get("numberInSurah", 0)
                    
                    # البحث عن النص في الآية
                    if query in ayah_text:
                        results.append({
                            "surah_name": surah_name,
                            "surah_number": surah_number,
                            "ayah_number": ayah_number,
                            "text": ayah_text
                        })
            
            return results
        
        except Exception as e:
            print(f"خطأ في البحث في القرآن: {str(e)}")
            return []
    
    def search_tafseer(self, query: str) -> List[Dict[str, Any]]:
        """
        البحث في التفسير عن نص معين

        Args:
            query: نص البحث

        Returns:
            قائمة التفاسير المطابقة
        """
        results = []
        
        try:
            # تحميل بيانات التفسير
            tafseer_data = self.download_tafseer()
            
            # البحث في كل تفسير
            for tafseer in tafseer_data:
                tafseer_text = tafseer.get("text", "")
                surah_number = tafseer.get("sura", 0)
                ayah_number = tafseer.get("ayah", 0)
                
                # البحث عن النص في التفسير
                if query in tafseer_text:
                    results.append({
                        "surah_number": surah_number,
                        "ayah_number": ayah_number,
                        "text": tafseer_text
                    })
            
            return results
        
        except Exception as e:
            print(f"خطأ في البحث في التفسير: {str(e)}")
            return []
    
    def search_scientific_miracles(self, query: str) -> List[Dict[str, Any]]:
        """
        البحث في المعجزات العلمية عن نص معين

        Args:
            query: نص البحث

        Returns:
            قائمة المعجزات العلمية المطابقة
        """
        results = []
        
        try:
            # تحميل بيانات المعجزات العلمية
            miracles = self.load_scientific_miracles()
            
            # البحث في كل معجزة
            for miracle in miracles:
                title = miracle.get("title", "")
                verse = miracle.get("verse", "")
                explanation = miracle.get("explanation", "")
                
                # البحث عن النص في العنوان أو الآية أو الشرح
                if query in title or query in verse or query in explanation:
                    results.append(miracle)
            
            return results
        
        except Exception as e:
            print(f"خطأ في البحث في المعجزات العلمية: {str(e)}")
            return []
    
    def prepare_quran_embeddings(self) -> List[Dict[str, Any]]:
        """
        إعداد بيانات القرآن للتضمين
        
        Returns:
            قائمة من بيانات الآيات المعدة للتضمين
        """
        embedding_data = []
        
        try:
            # تحميل بيانات القرآن
            quran_data = self.download_quran_text()
            
            # إعداد كل آية للتضمين
            for surah in quran_data:
                surah_name = surah.get("name", "")
                surah_number = surah.get("number", 0)
                
                for ayah in surah.get("ayahs", []):
                    ayah_text = ayah.get("text", "")
                    ayah_number = ayah.get("numberInSurah", 0)
                    
                    # إنشاء سجل للتضمين
                    embedding_record = {
                        "id": f"quran_{surah_number}_{ayah_number}",
                        "text": ayah_text,
                        "metadata": {
                            "source": "quran",
                            "surah_name": surah_name,
                            "surah_number": surah_number,
                            "ayah_number": ayah_number
                        }
                    }
                    
                    embedding_data.append(embedding_record)
            
            return embedding_data
        
        except Exception as e:
            print(f"خطأ في إعداد تضمينات القرآن: {str(e)}")
            return []
            
    def _load_topics_index(self) -> Dict[str, List[str]]:
        """
        تحميل فهرس المواضيع القرآنية
        
        Returns:
            قاموس يربط بين الموضوع وقائمة الآيات المرتبطة به
        """
        try:
            topics_file = os.path.join(self.quran_dir, "topics_index.json")
            
            # التحقق مما إذا كان الملف موجودًا
            if os.path.exists(topics_file):
                with open(topics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # إنشاء فهرس مواضيع أولي إذا لم يكن الملف موجودًا
                # هذا مجرد مثال، يجب استبداله بفهرس حقيقي
                initial_topics = {
                    "الصيام": ["2:183", "2:184", "2:185", "2:187", "2:196"],
                    "الصلاة": ["2:3", "2:43", "2:45", "2:83", "2:110", "4:101-103", "17:78"],
                    "الزكاة": ["2:43", "2:83", "2:110", "9:60"],
                    "الحج": ["2:158", "2:189", "2:196-200", "3:97", "5:1-2", "22:27-29"],
                    "الإيمان": ["2:8-20", "2:62", "2:177", "3:84-85", "4:136", "49:14-15"],
                    "التوحيد": ["2:163", "2:255", "3:2", "3:18", "112:1-4"],
                    "الأخلاق": ["2:83", "3:134", "4:36", "17:23-39", "31:12-19", "49:11-12"]
                }
                
                # حفظ الفهرس الأولي
                with open(topics_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_topics, f, ensure_ascii=False, indent=4)
                
                return initial_topics
        
        except Exception as e:
            print(f"خطأ في تحميل فهرس المواضيع: {str(e)}")
            return {}
    
    def _load_roots_index(self) -> Dict[str, List[str]]:
        """
        تحميل فهرس الجذور اللغوية للكلمات القرآنية
        
        Returns:
            قاموس يربط بين الجذر اللغوي وقائمة الآيات المرتبطة به
        """
        try:
            roots_file = os.path.join(self.quran_dir, "roots_index.json")
            
            # التحقق مما إذا كان الملف موجودًا
            if os.path.exists(roots_file):
                with open(roots_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # إنشاء فهرس جذور أولي إذا لم يكن الملف موجودًا
                # هذا مجرد مثال، يجب استبداله بفهرس حقيقي
                initial_roots = {
                    "رحم": ["1:1", "1:3", "2:163", "19:18-19", "21:107", "55:1-2"],
                    "علم": ["2:31-32", "2:151", "2:255", "5:109", "12:76", "20:114", "96:4-5"],
                    "قرأ": ["17:14", "73:20", "96:1-3"],
                    "كتب": ["2:178-180", "2:183", "2:187", "4:103", "5:32", "6:12", "6:54"],
                    "أمن": ["2:3-4", "2:8-9", "2:62", "2:126", "2:136", "3:84", "4:136"]
                }
                
                # حفظ الفهرس الأولي
                with open(roots_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_roots, f, ensure_ascii=False, indent=4)
                
                return initial_roots
        
        except Exception as e:
            print(f"خطأ في تحميل فهرس الجذور: {str(e)}")
            return {}
    
    def _parse_reference(self, reference: str) -> List[Dict[str, int]]:
        """
        تحليل مرجع آية أو مجموعة آيات
        
        Args:
            reference: مرجع الآية بصيغة "سورة:آية" أو "سورة:آية-آية"
            
        Returns:
            قائمة من القواميس تحتوي على أرقام السور والآيات
        """
        results = []
        
        try:
            # تقسيم المرجع إلى سورة وآية
            parts = reference.split(":")
            if len(parts) != 2:
                return results
            
            surah = int(parts[0])
            ayah_part = parts[1]
            
            # التحقق مما إذا كان نطاق آيات
            if "-" in ayah_part:
                ayah_range = ayah_part.split("-")
                start_ayah = int(ayah_range[0])
                end_ayah = int(ayah_range[1])
                
                for ayah in range(start_ayah, end_ayah + 1):
                    results.append({"surah": surah, "ayah": ayah})
            else:
                # آية واحدة
                ayah = int(ayah_part)
                results.append({"surah": surah, "ayah": ayah})
            
            return results
        
        except Exception as e:
            print(f"خطأ في تحليل مرجع الآية: {str(e)}")
            return results
    
    def search_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """
        البحث في القرآن حسب الموضوع
        
        Args:
            topic: الموضوع المراد البحث عنه
            
        Returns:
            قائمة الآيات المرتبطة بالموضوع
        """
        results = []
        
        try:
            # تحميل فهرس المواضيع
            topics = self._load_topics_index()
            
            # التحقق مما إذا كان الموضوع موجودًا
            if topic not in topics:
                return results
            
            # الحصول على قائمة مراجع الآيات للموضوع
            references = topics[topic]
            
            # تحميل بيانات القرآن
            quran_data = self.download_quran_text()
            
            # استخراج الآيات المطلوبة
            for reference in references:
                ayah_refs = self._parse_reference(reference)
                
                for ayah_ref in ayah_refs:
                    surah_number = ayah_ref["surah"]
                    ayah_number = ayah_ref["ayah"]
                    
                    # البحث عن السورة
                    surah = None
                    for s in quran_data:
                        if s.get("number") == surah_number:
                            surah = s
                            break
                    
                    if not surah:
                        continue
                    
                    # البحث عن الآية
                    ayah = None
                    for a in surah.get("ayahs", []):
                        if a.get("numberInSurah") == ayah_number:
                            ayah = a
                            break
                    
                    if not ayah:
                        continue
                    
                    # إضافة الآية إلى النتائج
                    results.append({
                        "surah_name": surah.get("name", ""),
                        "surah_number": surah_number,
                        "ayah_number": ayah_number,
                        "text": ayah.get("text", "")
                    })
            
            return results
        
        except Exception as e:
            print(f"خطأ في البحث حسب الموضوع: {str(e)}")
            return []
    
    def search_by_root(self, root: str) -> List[Dict[str, Any]]:
        """
        البحث في القرآن حسب الجذر اللغوي
        
        Args:
            root: الجذر اللغوي المراد البحث عنه
            
        Returns:
            قائمة الآيات المرتبطة بالجذر
        """
        results = []
        
        try:
            # تحميل فهرس الجذور
            roots = self._load_roots_index()
            
            # التحقق مما إذا كان الجذر موجودًا
            if root not in roots:
                return results
            
            # الحصول على قائمة مراجع الآيات للجذر
            references = roots[root]
            
            # تحميل بيانات القرآن
            quran_data = self.download_quran_text()
            
            # استخراج الآيات المطلوبة
            for reference in references:
                ayah_refs = self._parse_reference(reference)
                
                for ayah_ref in ayah_refs:
                    surah_number = ayah_ref["surah"]
                    ayah_number = ayah_ref["ayah"]
                    
                    # البحث عن السورة
                    surah = None
                    for s in quran_data:
                        if s.get("number") == surah_number:
                            surah = s
                            break
                    
                    if not surah:
                        continue
                    
                    # البحث عن الآية
                    ayah = None
                    for a in surah.get("ayahs", []):
                        if a.get("numberInSurah") == ayah_number:
                            ayah = a
                            break
                    
                    if not ayah:
                        continue
                    
                    # إضافة الآية إلى النتائج
                    results.append({
                        "surah_name": surah.get("name", ""),
                        "surah_number": surah_number,
                        "ayah_number": ayah_number,
                        "text": ayah.get("text", "")
                    })
            
            return results
        
        except Exception as e:
            print(f"خطأ في البحث حسب الجذر: {str(e)}")
            return []
    
    def get_surah_info(self, surah_number: int) -> Optional[Dict[str, Any]]:
        """
        الحصول على معلومات سورة محددة
        
        Args:
            surah_number: رقم السورة
            
        Returns:
            معلومات السورة أو None إذا لم تكن موجودة
        """
        try:
            # تحميل بيانات القرآن
            quran_data = self.download_quran_text()
            
            # البحث عن السورة
            for surah in quran_data:
                if surah.get("number") == surah_number:
                    # إرجاع نسخة من معلومات السورة بدون الآيات
                    surah_info = surah.copy()
                    return surah_info
            
            return None
        
        except Exception as e:
            print(f"خطأ في الحصول على معلومات السورة: {str(e)}")
            return None
    
    def get_ayah_with_tafseer(self, surah_number: int, ayah_number: int) -> Optional[Dict[str, Any]]:
        """
        الحصول على آية مع تفسيرها
        
        Args:
            surah_number: رقم السورة
            ayah_number: رقم الآية
            
        Returns:
            قاموس يحتوي على الآية وتفسيرها أو None إذا لم تكن موجودة
        """
        try:
            # تحميل بيانات القرآن
            quran_data = self.download_quran_text()
            
            # البحث عن السورة
            surah = None
            for s in quran_data:
                if s.get("number") == surah_number:
                    surah = s
                    break
            
            if not surah:
                return None
            
            # البحث عن الآية
            ayah = None
            for a in surah.get("ayahs", []):
                if a.get("numberInSurah") == ayah_number:
                    ayah = a
                    break
            
            if not ayah:
                return None
            
            # تحميل التفسير
            tafseer_data = self.download_tafseer()
            
            # البحث عن تفسير الآية
            tafseer_text = ""
            for tafseer in tafseer_data:
                if tafseer.get("sura") == surah_number and tafseer.get("ayah") == ayah_number:
                    tafseer_text = tafseer.get("text", "")
                    break
            
            # إنشاء النتيجة
            result = {
                "surah_number": surah_number,
                "surah_name": surah.get("name", ""),
                "ayah_number": ayah_number,
                "ayah_text": ayah.get("text", ""),
                "tafseer": tafseer_text
            }
            
            return result
        
        except Exception as e:
            print(f"خطأ في الحصول على الآية مع التفسير: {str(e)}")
            return None
