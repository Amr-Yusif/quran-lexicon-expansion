#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام التحليل اللغوي للنصوص الإسلامية
يقدم تحليلًا صرفيًا ونحويًا وبلاغيًا للنصوص العربية والقرآنية
"""

import re
import json
import logging
from typing import List, Dict, Any
from pathlib import Path

# استيراد أدوات معالجة اللغة العربية
try:
    import pyarabic.araby as araby
    from camel_tools.morphology.database import MorphologyDB
    from camel_tools.morphology.analyzer import Analyzer
    from camel_tools.tokenizers.word import simple_word_tokenize
except ImportError:
    print("تثبيت المكتبات المطلوبة للتحليل اللغوي...")
    import os
    os.system("pip install pyarabic camel-tools")
    import pyarabic.araby as araby
    from camel_tools.morphology.database import MorphologyDB
    from camel_tools.morphology.analyzer import Analyzer
    from camel_tools.tokenizers.word import simple_word_tokenize

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IslamicTextAnalyzer:
    def __init__(self):
        """
        تهيئة أدوات التحليل اللغوي للنصوص الإسلامية
        """
        logger.info("تحميل أدوات التحليل الصرفي للغة العربية...")
        # تهيئة أدوات التحليل الصرفي للغة العربية
        self.db = MorphologyDB.builtin_db()
        self.analyzer = Analyzer(self.db)
        
        # قاموس الأنماط البلاغية
        self.rhetorical_patterns = {
            'استعارة': [
                r'ك[^.]+مثل', 
                r'كأن[^.]+', 
                r'يشبه[^.]+'
            ],
            'كناية': [
                r'يقصد[^.]+', 
                r'يعني[^.]+'
            ],
            'مجاز': [
                r'مجاز[ًاى][^.]+', 
                r'غير حقيق[يةى][^.]+'
            ],
            'طباق': [
                r'[^.]+و[^.]+ضد'
            ],
            'جناس': [
                r'[^.]+تشابه[^.]+لفظ'
            ]
        }
        
        # المصطلحات القرآنية الشائعة
        self.quran_terms = {
            'توحيد': ['الله', 'الرحمن', 'الرحيم', 'الرب', 'الإله'],
            'عبادات': ['صلاة', 'زكاة', 'صوم', 'حج', 'ذكر', 'تسبيح', 'دعاء'],
            'قصص': ['نوح', 'إبراهيم', 'موسى', 'عيسى', 'يوسف', 'آدم'],
            'آخرة': ['جنة', 'نار', 'قيامة', 'بعث', 'حساب', 'ميزان'],
            'أخلاق': ['صدق', 'عدل', 'رحمة', 'إحسان', 'صبر']
        }
        
        logger.info("تم تهيئة محلل النصوص الإسلامية بنجاح")
    
    def analyze_morphology(self, text: str) -> List[Dict]:
        """
        تحليل صرفي للنص
        
        Args:
            text: النص المراد تحليله
            
        Returns:
            قائمة بنتائج التحليل الصرفي
        """
        logger.info("إجراء تحليل صرفي للنص")
        # تقسيم النص إلى كلمات
        tokens = simple_word_tokenize(text)
        
        # تحليل كل كلمة
        analysis_results = []
        for token in tokens:
            # تحليل الكلمة
            analyses = self.analyzer.analyze(token)
            
            if analyses:
                best_analysis = analyses[0]  # أخذ التحليل الأول
                result = {
                    'word': token,
                    'lemma': best_analysis.get('lex', ''),
                    'root': best_analysis.get('root', ''),
                    'pos': best_analysis.get('pos', ''),
                    'gender': best_analysis.get('gen', ''),
                    'number': best_analysis.get('num', ''),
                    'person': best_analysis.get('per', ''),
                    'case': best_analysis.get('cas', ''),
                    'state': best_analysis.get('stt', ''),
                    'voice': best_analysis.get('vox', ''),
                    'aspect': best_analysis.get('asp', '')
                }
                analysis_results.append(result)
            else:
                # إذا لم يتم العثور على تحليل
                analysis_results.append({'word': token, 'analysis': 'غير معروف'})
        
        return analysis_results
    
    def analyze_syntax(self, text: str) -> Dict:
        """
        تحليل نحوي للنص (تبسيط للإعراب)
        
        Args:
            text: النص المراد تحليله
            
        Returns:
            قاموس يحتوي على نتائج التحليل النحوي
        """
        logger.info("إجراء تحليل نحوي للنص")
        # تقسيم النص إلى جمل
        sentences = re.split(r'[.،؛؟!]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        syntax_analysis = []
        for sentence in sentences:
            tokens = simple_word_tokenize(sentence)
            
            # تحليل بسيط للإعراب
            sentence_analysis = {
                'sentence': sentence,
                'tokens': [],
                'structure': {}
            }
            
            for i, token in enumerate(tokens):
                analyses = self.analyzer.analyze(token)
                if analyses:
                    # تحديد دور الكلمة في الجملة (تبسيط)
                    pos = analyses[0].get('pos', '')
                    case = analyses[0].get('cas', '')
                    
                    role = 'غير محدد'
                    if pos == 'noun' and case == 'n':
                        if i > 0 and 'verb' in self.analyzer.analyze(tokens[i-1])[0].get('pos', ''):
                            role = 'فاعل'
                        elif i > 1 and 'noun' in self.analyzer.analyze(tokens[i-1])[0].get('pos', ''):
                            role = 'مضاف إليه'
                    elif pos == 'noun' and case == 'a':
                        role = 'مفعول به'
                    elif pos == 'verb':
                        role = 'فعل'
                    elif pos == 'adj':
                        role = 'صفة'
                    elif pos == 'prep':
                        role = 'حرف جر'
                    elif pos == 'conj':
                        role = 'حرف عطف'
                    
                    token_analysis = {
                        'word': token,
                        'pos': pos,
                        'case': case,
                        'role': role
                    }
                    
                    sentence_analysis['tokens'].append(token_analysis)
            
            # تحليل بسيط لتركيب الجملة
            if sentence_analysis['tokens']:
                sentence_structure = self._determine_sentence_structure(sentence_analysis['tokens'])
                sentence_analysis['structure'] = sentence_structure
            
            syntax_analysis.append(sentence_analysis)
        
        return {'syntax_analysis': syntax_analysis}
    
    def _determine_sentence_structure(self, tokens: List[Dict]) -> Dict:
        """
        تحديد تركيب الجملة (فعلية أو اسمية)
        
        Args:
            tokens: قائمة التحليلات للكلمات
            
        Returns:
            قاموس يحتوي على تركيب الجملة
        """
        # التحقق من وجود فعل في بداية الجملة
        if tokens and tokens[0].get('pos') == 'verb':
            structure_type = 'جملة فعلية'
            components = {
                'فعل': tokens[0].get('word'),
                'فاعل': next((t.get('word') for t in tokens if t.get('role') == 'فاعل'), None),
                'مفعول به': next((t.get('word') for t in tokens if t.get('role') == 'مفعول به'), None)
            }
        else:
            structure_type = 'جملة اسمية'
            # البحث عن المبتدأ والخبر
            subject = tokens[0].get('word') if tokens else None
            predicate = None
            
            # تبسيط: افتراض أن الخبر هو الكلمة الثانية في الجملة الاسمية
            if len(tokens) > 1:
                predicate = tokens[1].get('word')
            
            components = {
                'مبتدأ': subject,
                'خبر': predicate
            }
        
        return {
            'نوع': structure_type,
            'مكونات': components
        }
    
    def detect_rhetorical_patterns(self, text: str) -> Dict:
        """
        اكتشاف الأنماط البلاغية في النص
        
        Args:
            text: النص المراد تحليله
            
        Returns:
            قاموس يحتوي على الأنماط البلاغية المكتشفة
        """
        logger.info("اكتشاف الأنماط البلاغية في النص")
        rhetorical_findings = {pattern: [] for pattern in self.rhetorical_patterns}
        
        for pattern_type, patterns in self.rhetorical_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    # استخراج الجملة المحيطة بالنمط البلاغي
                    start = max(0, match.start() - 30)
                    end = min(len(text), match.end() + 30)
                    context = text[start:end]
                    
                    rhetorical_findings[pattern_type].append({
                        'text': match.group(),
                        'context': context,
                        'position': match.start()
                    })
        
        return {'rhetorical_patterns': rhetorical_findings}
    
    def analyze_roots_and_derivatives(self, text: str) -> Dict:
        """
        تحليل الجذور والمشتقات في النص
        
        Args:
            text: النص المراد تحليله
            
        Returns:
            قاموس يحتوي على تحليل الجذور والمشتقات
        """
        logger.info("تحليل الجذور والمشتقات في النص")
        tokens = simple_word_tokenize(text)
        
        # جمع الجذور وكلماتها
        root_dict = {}
        for token in tokens:
            analyses = self.analyzer.analyze(token)
            if analyses and 'root' in analyses[0]:
                root = analyses[0]['root']
                if root not in root_dict:
                    root_dict[root] = []
                if token not in root_dict[root]:
                    root_dict[root].append(token)
        
        # ترتيب النتائج حسب عدد المشتقات
        sorted_roots = sorted(root_dict.items(), key=lambda x: len(x[1]), reverse=True)
        
        return {
            'roots_analysis': {
                'total_roots': len(sorted_roots),
                'roots': [{
                    'root': root,
                    'derivatives': derivatives,
                    'count': len(derivatives)
                } for root, derivatives in sorted_roots]
            }
        }
    
    def categorize_islamic_terms(self, text: str) -> Dict:
        """
        تصنيف المصطلحات الإسلامية في النص
        
        Args:
            text: النص المراد تحليله
            
        Returns:
            قاموس يحتوي على تصنيف المصطلحات الإسلامية
        """
        logger.info("تصنيف المصطلحات الإسلامية في النص")
        tokens = simple_word_tokenize(text)
        
        # تصنيف المصطلحات
        categories = {category: [] for category in self.quran_terms}
        
        for token in tokens:
            # تطبيع الكلمة
            normalized_token = araby.strip_tashkeel(token)
            
            # البحث عن الكلمة في المصطلحات
            for category, terms in self.quran_terms.items():
                if any(term in normalized_token or normalized_token in term for term in terms):
                    if token not in categories[category]:
                        categories[category].append(token)
        
        # التصنيفات التي بها مصطلحات فقط
        found_categories = {
            category: terms
            for category, terms in categories.items()
            if terms
        }
        
        return {'islamic_terms': found_categories}
    
    def analyze_sentence_complexity(self, text: str) -> Dict:
        """
        تحليل تعقيد الجملة
        
        Args:
            text: النص المراد تحليله
            
        Returns:
            قاموس يحتوي على تحليل تعقيد الجملة
        """
        logger.info("تحليل تعقيد الجملة")
        # تقسيم النص إلى جمل
        sentences = re.split(r'[.،؛؟!]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        complexity_analysis = []
        
        for sentence in sentences:
            tokens = simple_word_tokenize(sentence)
            
            # حساب طول الجملة
            sentence_length = len(tokens)
            
            # حساب عدد الكلمات الفريدة
            unique_words = len(set(tokens))
            
            # حساب نسبة التنوع (عدد الكلمات الفريدة / إجمالي الكلمات)
            lexical_diversity = unique_words / sentence_length if sentence_length > 0 else 0
            
            # حساب متوسط طول الكلمات
            avg_word_length = sum(len(token) for token in tokens) / sentence_length if sentence_length > 0 else 0
            
            # تحديد مستوى التعقيد
            if sentence_length > 15 and lexical_diversity > 0.8:
                complexity_level = "عالٍ"
            elif sentence_length > 10 and lexical_diversity > 0.6:
                complexity_level = "متوسط"
            else:
                complexity_level = "بسيط"
            
            complexity_analysis.append({
                'sentence': sentence,
                'length': sentence_length,
                'unique_words': unique_words,
                'lexical_diversity': lexical_diversity,
                'avg_word_length': avg_word_length,
                'complexity_level': complexity_level
            })
        
        return {'sentence_complexity': complexity_analysis}
    
    def comprehensive_analysis(self, text: str) -> Dict:
        """
        تحليل شامل للنص يجمع كل التحليلات المتاحة
        
        Args:
            text: النص المراد تحليله
            
        Returns:
            قاموس يحتوي على التحليل الشامل
        """
        logger.info("إجراء تحليل شامل للنص")
        results = {
            'text': text,
            'morphology': self.analyze_morphology(text),
            'syntax': self.analyze_syntax(text),
            'rhetorical_patterns': self.detect_rhetorical_patterns(text),
            'roots_analysis': self.analyze_roots_and_derivatives(text),
            'islamic_terms': self.categorize_islamic_terms(text),
            'sentence_complexity': self.analyze_sentence_complexity(text)
        }
        
        return results
    
    def analyze_quranic_rhetoric(self, text: str) -> Dict:
        """
        تحليل بلاغي خاص بالنصوص القرآنية
        
        Args:
            text: النص القرآني المراد تحليله
            
        Returns:
            قاموس يحتوي على التحليل البلاغي الخاص بالقرآن
        """
        logger.info("إجراء تحليل بلاغي خاص بالقرآن الكريم")
        
        # تحليل بلاغي أساسي
        basic_rhetoric = self.analyze_rhetoric(text)
        
        # توسيع التحليل البلاغي بأنماط خاصة بالقرآن
        quranic_patterns = {
            'تناسق فواصل': [
                r'[^.]+[اًنا]$',  # فواصل تنتهي بألف ونون
                r'[^.]+[ينون]$'   # فواصل تنتهي بياء ونون
            ],
            'مقابلة': [
                r'[^.]+وَ[^.]+',  # جمل فيها مقابلة بين جزئين
            ],
            'التفات': [
                r'[^.]+هم[^.]+كم[^.]+',  # تغيير الضمير من الغائب للمخاطب
                r'[^.]+نا[^.]+هو[^.]+'    # تغيير الضمير من المتكلم للغائب
            ],
            'تقديم وتأخير': [
                r'إياك [^.]+',  # تقديم المفعول به على الفعل
                r'لله [^.]+',   # تقديم الجار والمجرور
            ],
            'إيجاز': [
                r'[^.]{5,50}[.،؛؟!]'  # جمل قصيرة نسبيًا
            ],
            'إطناب': [
                r'[^.]{150,}[.،؛؟!]'  # جمل طويلة نسبيًا
            ]
        }
        
        # دمج الأنماط البلاغية العامة مع الأنماط الخاصة بالقرآن
        all_patterns = {**self.rhetorical_patterns, **quranic_patterns}
        
        # تحليل الأنماط البلاغية القرآنية
        quranic_analysis = {
            "pattern_instances": {},
            "pattern_counts": {}
        }
        
        for pattern_name, patterns in all_patterns.items():
            instances = []
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    instances.append({
                        "text": match.group(),
                        "pattern": pattern_name,
                        "position": (match.start(), match.end())
                    })
            
            quranic_analysis["pattern_instances"][pattern_name] = instances
            quranic_analysis["pattern_counts"][pattern_name] = len(instances)
        
        # تحليل الكلمات المختصة بالقرآن
        quranic_terms = {
            "divine_names": ["الله", "الرحمن", "الرحيم", "الملك", "القدوس", "السلام", "المؤمن", "المهيمن"],
            "eschatology": ["جنة", "نار", "قيامة", "بعث", "حساب", "ميزان", "صراط"],
            "prophets": ["نوح", "إبراهيم", "موسى", "عيسى", "محمد", "آدم", "سليمان", "داود", "يوسف"],
            "ethics": ["صدق", "عدل", "إحسان", "صبر", "شكر", "توكل", "تقوى"]
        }
        
        # حساب تكرار المصطلحات القرآنية
        term_counts = {}
        for category, terms in quranic_terms.items():
            category_counts = {}
            for term in terms:
                count = len(re.findall(r'\b' + term + r'\b', text))
                if count > 0:
                    category_counts[term] = count
            
            term_counts[category] = category_counts
        
        # تحليل أسلوب الخطاب (مباشر أو غير مباشر)
        direct_address_count = len(re.findall(r'\bيا\b|\bأيها\b|\bأنتم\b|\bأنت\b|\bإياك\b', text))
        indirect_address_count = len(re.findall(r'\bهم\b|\bهو\b|\bهي\b|\bأولئك\b|\bالذين\b', text))
        
        discourse_style = {
            "direct_address": direct_address_count,
            "indirect_address": indirect_address_count,
            "dominant_style": "مباشر" if direct_address_count > indirect_address_count else "غير مباشر"
        }
        
        return {
            "basic_rhetoric": basic_rhetoric,
            "quranic_patterns": quranic_analysis,
            "term_usage": term_counts,
            "discourse_style": discourse_style
        }
    
    def analyze_word_significance(self, word: str, context: str = None) -> Dict:
        """
        تحليل أهمية ودلالة كلمة في السياق القرآني
        
        Args:
            word: الكلمة المراد تحليلها
            context: سياق الكلمة (اختياري)
            
        Returns:
            قاموس يحتوي على تحليل دلالة الكلمة
        """
        logger.info(f"تحليل دلالة الكلمة: {word}")
        
        # التحليل الصرفي للكلمة
        morphology = self.analyzer.analyze(word) if word else []
        
        if not morphology:
            return {"error": "لم يتم التعرف على الكلمة"}
        
        # اختيار أفضل تحليل
        best_analysis = morphology[0]
        
        # استخراج الجذر والوزن
        root = best_analysis.get('root', '')
        pattern = best_analysis.get('pattern', '')
        pos = best_analysis.get('pos', '')
        
        # دلالات محتملة بناءً على الوزن
        pattern_meanings = {
            "فَعَلَ": "للدلالة على حدث",
            "فَعِلَ": "للدلالة على صفة ثابتة",
            "فَعُلَ": "للدلالة على صفة متغيرة",
            "أفْعَلَ": "للتعدية أو الدخول في الشيء",
            "فَعَّلَ": "للتكثير والمبالغة",
            "فَاعَلَ": "للمشاركة بين اثنين",
            "تَفَعَّلَ": "للتكلف أو المطاوعة",
            "انْفَعَلَ": "للمطاوعة",
            "افْتَعَلَ": "للاتخاذ أو المطاوعة",
            "استفعل": "للطلب أو اعتقاد الصفة"
        }
        
        # تحليل السياق إذا كان متوفراً
        context_analysis = {}
        if context:
            # تحليل بسيط للسياق
            surrounding_words = context.split()
            position = -1
            
            try:
                position = surrounding_words.index(word)
            except ValueError:
                # قد لا تكون الكلمة بالضبط في السياق (بسبب التشكيل مثلاً)
                for i, w in enumerate(surrounding_words):
                    if word in w:
                        position = i
                        break
            
            if position >= 0:
                before = surrounding_words[max(0, position-3):position]
                after = surrounding_words[position+1:min(len(surrounding_words), position+4)]
                
                context_analysis = {
                    "position": position,
                    "before": before,
                    "after": after,
                    "collocations": self._analyze_collocations(word, surrounding_words, position)
                }
        
        return {
            "word": word,
            "root": root,
            "pattern": pattern,
            "part_of_speech": pos,
            "pattern_meaning": pattern_meanings.get(pattern, "غير معروف"),
            "morphology": {k: v for k, v in best_analysis.items() if k not in ['word', 'source', 'gloss']},
            "context_analysis": context_analysis
        }
    
    def _analyze_collocations(self, word: str, words: List[str], position: int) -> Dict:
        """
        تحليل المتلازمات اللفظية للكلمة في السياق
        
        Args:
            word: الكلمة المستهدفة
            words: قائمة الكلمات في السياق
            position: موقع الكلمة المستهدفة
            
        Returns:
            قاموس المتلازمات اللفظية
        """
        collocations = {
            "noun_adj": [],  # صفة ومصوف
            "idafa": [],     # إضافة
            "verb_subj": [], # فعل وفاعل
            "verb_obj": [],  # فعل ومفعول به
            "prep_noun": []  # حرف جر واسم مجرور
        }
        
        if not words or position < 0 or position >= len(words):
            return collocations
            
        # تحليل صرفي للكلمات المحيطة
        analysis = []
        for w in words:
            morph = self.analyzer.analyze(w)
            if morph:
                analysis.append((w, morph[0].get('pos', ''), morph[0].get('cas', '')))
            else:
                analysis.append((w, '', ''))
        
        # تحليل المتلازمات
        current_word, current_pos, current_case = analysis[position]
        
        # إذا كانت الكلمة الحالية اسما
        if current_pos == 'noun':
            # البحث عن صفة ومصوف
            if position < len(analysis) - 1:
                next_word, next_pos, next_case = analysis[position + 1]
                if next_pos == 'adj' and next_case == current_case:
                    collocations["noun_adj"].append((current_word, next_word))
            
            # البحث عن مضاف ومضاف إليه
            if position < len(analysis) - 1:
                next_word, next_pos, next_case = analysis[position + 1]
                if next_pos == 'noun' and next_case == 'g':  # مجرور
                    collocations["idafa"].append((current_word, next_word))
            
            # البحث عن حرف جر واسم مجرور
            if position > 0:
                prev_word, prev_pos, prev_case = analysis[position - 1]
                if prev_pos == 'prep' and current_case == 'g':  # مجرور
                    collocations["prep_noun"].append((prev_word, current_word))
        
        # إذا كانت الكلمة الحالية فعلا
        elif current_pos == 'verb':
            # البحث عن فعل وفاعل
            if position < len(analysis) - 1:
                next_word, next_pos, next_case = analysis[position + 1]
                if next_pos == 'noun' and next_case == 'n':  # مرفوع
                    collocations["verb_subj"].append((current_word, next_word))
            
            # البحث عن فعل ومفعول به
            for i in range(position + 1, min(position + 3, len(analysis))):
                if i < len(analysis):
                    next_word, next_pos, next_case = analysis[i]
                    if next_pos == 'noun' and next_case == 'a':  # منصوب
                        collocations["verb_obj"].append((current_word, next_word))
                        break
        
        return collocations

# مثال للاستخدام
if __name__ == "__main__":
    analyzer = IslamicTextAnalyzer()
    
    sample_text = "إِنَّ فِي خَلْقِ السَّمَاوَاتِ وَالْأَرْضِ وَاخْتِلَافِ اللَّيْلِ وَالنَّهَارِ لَآيَاتٍ لِأُولِي الْأَلْبَابِ"
    
    # تحليل صرفي
    morphology_results = analyzer.analyze_morphology(sample_text)
    print("\nنتائج التحليل الصرفي:")
    print(json.dumps(morphology_results[:3], ensure_ascii=False, indent=2))
    
    # تحليل الجذور
    roots_analysis = analyzer.analyze_roots_and_derivatives(sample_text)
    print("\nتحليل الجذور:")
    print(json.dumps(roots_analysis, ensure_ascii=False, indent=2))
    
    # تحليل شامل
    print("\nإجراء تحليل شامل...")
    comprehensive = analyzer.comprehensive_analysis(sample_text)
    print("تم الانتهاء من التحليل الشامل!")
