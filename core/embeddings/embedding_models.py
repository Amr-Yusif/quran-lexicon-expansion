"""
نماذج التضمين المتخصصة للنصوص العربية والإسلامية
"""
from sentence_transformers import SentenceTransformer
import os
import numpy as np
from typing import List, Dict, Any, Union, Optional

class ArabicEmbeddingModel:
    """
    نموذج تضمين متخصص للنصوص العربية، مع تحسينات للنصوص الدينية الإسلامية
    """
    
    def __init__(self, model_name: str = "paraphrase-multilingual-mpnet-base-v2"):
        """
        تهيئة نموذج التضمين العربي

        Args:
            model_name: اسم نموذج التضمين (افتراضياً: paraphrase-multilingual-mpnet-base-v2)
        """
        try:
            self.model = SentenceTransformer(model_name)
            self.vector_size = self.model.get_sentence_embedding_dimension()
            self.model_name = model_name
        except Exception as e:
            print(f"خطأ في تحميل نموذج التضمين: {str(e)}")
            # استخدام نموذج بديل إذا فشل التحميل
            fallback_model = "distiluse-base-multilingual-cased-v1"
            print(f"محاولة استخدام النموذج البديل: {fallback_model}")
            self.model = SentenceTransformer(fallback_model)
            self.vector_size = self.model.get_sentence_embedding_dimension()
            self.model_name = fallback_model
    
    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        تضمين نص أو قائمة نصوص

        Args:
            text: النص أو قائمة النصوص للتضمين

        Returns:
            مصفوفة التضمينات للنصوص
        """
        if isinstance(text, str):
            text = [text]
        
        return self.model.encode(text)
    
    def embed_documents(self, documents: List[Dict[str, Any]], text_key: str = "text") -> List[Dict[str, Any]]:
        """
        تضمين مجموعة من الوثائق

        Args:
            documents: قائمة من الوثائق للتضمين
            text_key: مفتاح النص في الوثائق

        Returns:
            قائمة الوثائق مع التضمينات
        """
        # استخراج النصوص
        texts = [doc.get(text_key, "") for doc in documents]
        
        # تضمين النصوص
        embeddings = self.embed_text(texts)
        
        # إضافة التضمينات إلى الوثائق
        embedded_documents = []
        for i, doc in enumerate(documents):
            doc_copy = doc.copy()
            doc_copy["embedding"] = embeddings[i].tolist()
            embedded_documents.append(doc_copy)
        
        return embedded_documents
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        حساب التشابه بين نصين

        Args:
            text1: النص الأول
            text2: النص الثاني

        Returns:
            درجة التشابه (0-1)
        """
        # تضمين النصوص
        embedding1 = self.embed_text(text1)
        embedding2 = self.embed_text(text2)
        
        # حساب تشابه جيب التمام
        dot_product = np.dot(embedding1, embedding2.T)[0][0]
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        return dot_product / (norm1 * norm2)
    
    def preprocess_arabic_text(self, text: str) -> str:
        """
        معالجة أولية للنص العربي لتحسين التضمين

        Args:
            text: النص العربي

        Returns:
            النص بعد المعالجة
        """
        # إزالة التشكيل (الحركات)
        arabic_diacritics = [
            '\u064B', '\u064C', '\u064D', '\u064E', '\u064F',
            '\u0650', '\u0651', '\u0652', '\u0653', '\u0654', '\u0655'
        ]
        for diacritic in arabic_diacritics:
            text = text.replace(diacritic, '')
        
        # توحيد أشكال الألف
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        
        # توحيد أشكال الهاء والتاء المربوطة
        text = text.replace('ة', 'ه')
        
        # إزالة المسافات الزائدة
        text = ' '.join(text.split())
        
        return text
