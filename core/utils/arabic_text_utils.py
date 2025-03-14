"""
أدوات مساعدة لمعالجة النصوص العربية والإسلامية
"""
import re
from typing import List, Dict, Any, Union, Optional, Tuple

class ArabicTextProcessor:
    """
    معالج متخصص للنصوص العربية مع تركيز على النصوص القرآنية والإسلامية
    """
    
    # قائمة علامات التشكيل العربية
    DIACRITICS = [
        '\u064B', '\u064C', '\u064D', '\u064E', '\u064F',
        '\u0650', '\u0651', '\u0652', '\u0653', '\u0654', '\u0655'
    ]
    
    # أنماط التعبير النمطي للتعرف على الآيات القرآنية
    QURAN_VERSE_PATTERN = r'﴿([^﴾]+)﴾'
    QURAN_CITATION_PATTERN = r'\(([\u0600-\u06FF\s]+):\s*(\d+)\)'  # مثال: (البقرة: 255)
    
    # أسماء السور القرآنية
    SURAH_NAMES = [
        'الفاتحة', 'البقرة', 'آل عمران', 'النساء', 'المائدة', 'الأنعام', 'الأعراف', 'الأنفال', 'التوبة', 'يونس',
        'هود', 'يوسف', 'الرعد', 'إبراهيم', 'الحجر', 'النحل', 'الإسراء', 'الكهف', 'مريم', 'طه',
        'الأنبياء', 'الحج', 'المؤمنون', 'النور', 'الفرقان', 'الشعراء', 'النمل', 'القصص', 'العنكبوت', 'الروم',
        'لقمان', 'السجدة', 'الأحزاب', 'سبأ', 'فاطر', 'يس', 'الصافات', 'ص', 'الزمر', 'غافر',
        'فصلت', 'الشورى', 'الزخرف', 'الدخان', 'الجاثية', 'الأحقاف', 'محمد', 'الفتح', 'الحجرات', 'ق',
        'الذاريات', 'الطور', 'النجم', 'القمر', 'الرحمن', 'الواقعة', 'الحديد', 'المجادلة', 'الحشر', 'الممتحنة',
        'الصف', 'الجمعة', 'المنافقون', 'التغابن', 'الطلاق', 'التحريم', 'الملك', 'القلم', 'الحاقة', 'المعارج',
        'نوح', 'الجن', 'المزمل', 'المدثر', 'القيامة', 'الإنسان', 'المرسلات', 'النبأ', 'النازعات', 'عبس',
        'التكوير', 'الانفطار', 'المطففين', 'الانشقاق', 'البروج', 'الطارق', 'الأعلى', 'الغاشية', 'الفجر', 'البلد',
        'الشمس', 'الليل', 'الضحى', 'الشرح', 'التين', 'العلق', 'القدر', 'البينة', 'الزلزلة', 'العاديات',
        'القارعة', 'التكاثر', 'العصر', 'الهمزة', 'الفيل', 'قريش', 'الماعون', 'الكوثر', 'الكافرون', 'النصر',
        'المسد', 'الإخلاص', 'الفلق', 'الناس'
    ]
    
    # كلمات العلوم الشائعة للكشف عن المعجزات العلمية
    SCIENTIFIC_KEYWORDS = [
        'سماء', 'أرض', 'نجم', 'شمس', 'قمر', 'كوكب', 'كون', 'مجرة', 'فلك',
        'ماء', 'بحر', 'نهر', 'محيط', 'سحاب', 'مطر', 'رعد', 'برق', 'رياح',
        'جبال', 'حديد', 'معدن', 'صخر', 'تراب', 'طين', 'رمل', 'زرع', 'نبات',
        'إنسان', 'خلق', 'جنين', 'مضغة', 'علقة', 'جسم', 'قلب', 'دم', 'عظم',
        'فضاء', 'توسع', 'انفجار', 'دوران', 'مدار', 'جاذبية', 'ضوء', 'ظلمة',
        'يوم', 'سنة', 'زمن', 'قياس', 'وزن', 'ميزان', 'نسبة', 'حساب', 'عدد'
    ]
    
    @classmethod
    def remove_diacritics(cls, text: str) -> str:
        """
        إزالة علامات التشكيل من النص العربي

        Args:
            text: النص العربي المراد معالجته

        Returns:
            النص بدون علامات التشكيل
        """
        for diacritic in cls.DIACRITICS:
            text = text.replace(diacritic, '')
        return text
    
    @classmethod
    def normalize_arabic_text(cls, text: str) -> str:
        """
        توحيد شكل النص العربي لتحسين عمليات المطابقة والبحث

        Args:
            text: النص العربي المراد توحيده

        Returns:
            النص بعد التوحيد
        """
        # إزالة التشكيل
        text = cls.remove_diacritics(text)
        
        # توحيد أشكال الألف
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        
        # توحيد أشكال الهاء والتاء المربوطة
        text = text.replace('ة', 'ه')
        
        # إزالة المسافات الزائدة
        text = ' '.join(text.split())
        
        return text
    
    @classmethod
    def extract_quran_verses(cls, text: str) -> List[str]:
        """
        استخراج الآيات القرآنية من النص

        Args:
            text: النص المراد استخراج الآيات منه

        Returns:
            قائمة بالآيات المستخرجة
        """
        # البحث عن الآيات المحاطة بعلامات الاقتباس القرآنية
        verses_with_brackets = re.findall(cls.QURAN_VERSE_PATTERN, text)
        
        # البحث عن الآيات المتبوعة باسم السورة ورقم الآية
        possible_verses = []
        for line in text.split('\n'):
            for surah_name in cls.SURAH_NAMES:
                pattern = rf'([\u0600-\u06FF\s]+)\s+\({surah_name}:\s*(\d+)\)'
                matches = re.findall(pattern, line)
                possible_verses.extend([match[0] for match in matches])
        
        # دمج النتائج
        all_verses = verses_with_brackets + possible_verses
        
        # تنظيف النتائج
        cleaned_verses = [verse.strip() for verse in all_verses if verse.strip()]
        
        return cleaned_verses
    
    @classmethod
    def extract_verse_references(cls, text: str) -> List[Dict[str, Union[str, int]]]:
        """
        استخراج مراجع الآيات القرآنية من النص

        Args:
            text: النص المراد استخراج المراجع منه

        Returns:
            قائمة بمراجع الآيات (اسم السورة، رقم الآية)
        """
        references = []
        
        # البحث عن مراجع الآيات بالصيغة (اسم السورة: رقم الآية)
        citations = re.findall(cls.QURAN_CITATION_PATTERN, text)
        
        for citation in citations:
            surah_name = citation[0].strip()
            verse_number = int(citation[1])
            
            if surah_name in cls.SURAH_NAMES:
                references.append({
                    "surah": surah_name,
                    "ayah": verse_number
                })
        
        return references
    
    @classmethod
    def detect_scientific_content(cls, text: str) -> Tuple[bool, List[str]]:
        """
        الكشف عن المحتوى العلمي في النص

        Args:
            text: النص المراد فحصه

        Returns:
            زوج من (هل يحتوي على محتوى علمي، قائمة بالكلمات العلمية المكتشفة)
        """
        found_keywords = []
        
        # البحث عن الكلمات المفتاحية العلمية
        for keyword in cls.SCIENTIFIC_KEYWORDS:
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, text):
                found_keywords.append(keyword)
        
        # اعتبار النص علميًا إذا وجدت كلمتان علميتان على الأقل
        has_scientific_content = len(found_keywords) >= 2
        
        return has_scientific_content, found_keywords
    
    @classmethod
    def chunker(cls, text: str, chunk_size: int = 200, chunk_overlap: int = 50) -> List[str]:
        """
        تقسيم النص إلى قطع متداخلة للمعالجة

        Args:
            text: النص المراد تقسيمه
            chunk_size: حجم القطعة بالأحرف
            chunk_overlap: حجم التداخل بين القطع

        Returns:
            قائمة بقطع النص
        """
        # تقسيم النص إلى جمل
        sentences = re.split(r'[.!?؟\n]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            # إذا كانت الجملة الحالية وحدها أكبر من حجم القطعة
            if sentence_size > chunk_size:
                # إذا كان هناك محتوى في القطعة الحالية، أضفه أولاً
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_size = 0
                
                # تقسيم الجملة الطويلة
                words = sentence.split()
                temp_chunk = []
                temp_size = 0
                
                for word in words:
                    word_size = len(word) + 1  # +1 للمسافة
                    
                    if temp_size + word_size <= chunk_size:
                        temp_chunk.append(word)
                        temp_size += word_size
                    else:
                        chunks.append(' '.join(temp_chunk))
                        temp_chunk = [word]
                        temp_size = word_size
                
                # إضافة آخر جزء من القطعة المقسمة
                if temp_chunk:
                    chunks.append(' '.join(temp_chunk))
                
            # إذا كانت إضافة الجملة الحالية ستتجاوز حجم القطعة
            elif current_size + sentence_size + 1 > chunk_size:
                # إنهاء القطعة الحالية
                chunks.append(' '.join(current_chunk))
                
                # ابدأ قطعة جديدة مع التداخل
                overlap_start = max(0, len(current_chunk) - chunk_overlap)
                current_chunk = current_chunk[overlap_start:] + [sentence]
                current_size = sum(len(s) for s in current_chunk) + len(current_chunk) - 1
                
            else:
                # إضافة الجملة إلى القطعة الحالية
                current_chunk.append(sentence)
                current_size += sentence_size + 1  # +1 للمسافة
        
        # إضافة القطعة الأخيرة إذا وجدت
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    @classmethod
    def get_surah_number(cls, surah_name: str) -> Optional[int]:
        """
        الحصول على رقم السورة من اسمها

        Args:
            surah_name: اسم السورة

        Returns:
            رقم السورة (1-114) أو None إذا لم يتم العثور عليها
        """
        try:
            return cls.SURAH_NAMES.index(surah_name) + 1
        except ValueError:
            return None
