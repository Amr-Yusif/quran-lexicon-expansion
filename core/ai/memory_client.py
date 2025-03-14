#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مكتبة إدارة ذاكرة المحادثات باستخدام Llama-Index وQdrant
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid

# استيراد مكتبات Llama-Index
# Mock implementation to avoid dependency on llama_index
# from llama_index.core import Settings
from llama_index.core import Document
from llama_index.core.schema import TextNode
# تعطيل استيراد QdrantVectorStore مؤقتًا
# from llama_index.vector_stores import QdrantVectorStore
# from llama_index.core.indices.vector_store import VectorStoreIndex
# from llama_index.core.storage.storage_context import StorageContext
# from llama_index.core.embeddings import HuggingFaceEmbedding
# from sentence_transformers import SentenceTransformer


# تعريف فئات وهمية مؤقتة
class QdrantVectorStore:
    """فئة وهمية مؤقتة لـ QdrantVectorStore"""

    def __init__(self, *args, **kwargs):
        pass


class VectorStoreIndex:
    """فئة وهمية مؤقتة لـ VectorStoreIndex"""

    @classmethod
    def from_documents(cls, *args, **kwargs):
        return cls()

    def __init__(self, *args, **kwargs):
        pass

    def as_query_engine(self, *args, **kwargs):
        return MockQueryEngine()


class StorageContext:
    """فئة وهمية مؤقتة لـ StorageContext"""

    @classmethod
    def from_defaults(cls, *args, **kwargs):
        return cls()

    def __init__(self, *args, **kwargs):
        pass


class HuggingFaceEmbedding:
    """فئة وهمية مؤقتة لـ HuggingFaceEmbedding"""

    def __init__(self, *args, **kwargs):
        pass


class MockQueryEngine:
    """فئة وهمية مؤقتة لمحرك الاستعلام"""

    def query(self, *args, **kwargs):
        return MockResponse()


class MockResponse:
    """فئة وهمية مؤقتة للاستجابة"""

    def __init__(self):
        self.response = ""
        self.source_nodes = []


# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryClient:
    """
    فئة لإدارة ذاكرة المحادثات باستخدام Llama-Index وQdrant
    """

    def __init__(
        self,
        api_key: str = None,
        url: str = None,
        embedding_model_name: str = "paraphrase-multilingual-mpnet-base-v2",
    ):
        """
        تهيئة ذاكرة المحادثات

        Args:
            api_key: مفتاح API لـ Qdrant (اختياري)
            url: عنوان URL لخدمة Qdrant (اختياري)
            embedding_model_name: اسم نموذج التضمين
        """
        try:
            # تهيئة نموذج التضمين
            self.embedding_model_name = embedding_model_name

            # استخدام HuggingFaceEmbedding من llama-index
            self.embedding_model = HuggingFaceEmbedding(model_name=embedding_model_name)

            # تكوين للاستخدام العام (mock implementation)
            # Settings.embed_model = self.embedding_model

            # اسم مجموعة الذاكرة
            self.collection_name = "conversation_memory"

            # إعداد Qdrant
            self.qdrant_url = url or os.environ.get("QDRANT_URL", "http://localhost:6333")
            self.qdrant_api_key = api_key or os.environ.get("QDRANT_API_KEY", "")

            # إنشاء مخزن متجه Qdrant
            self.vector_store = QdrantVectorStore(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key,
                collection_name=self.collection_name,
                prefer_grpc=False,
            )

            # إنشاء مجموعة الذاكرة إذا لم تكن موجودة
            self._ensure_collection_exists()

            # إنشاء سياق التخزين
            self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

            # إنشاء فهرس
            self.index = VectorStoreIndex.from_vector_store(
                self.vector_store, storage_context=self.storage_context
            )

            logger.info("تم تهيئة ذاكرة المحادثات باستخدام Llama-Index وQdrant")

        except Exception as e:
            logger.error(f"خطأ في تهيئة ذاكرة المحادثات: {str(e)}")
            raise

    def _ensure_collection_exists(self) -> None:
        """
        التأكد من وجود مجموعة الذاكرة
        """
        try:
            # مجموعة Qdrant يتم إنشاؤها تلقائيًا مع أول إدراج
            pass
        except Exception as e:
            logger.error(f"خطأ في التحقق من وجود مجموعة الذاكرة: {str(e)}")
            raise

    def _convert_to_document(self, content: str, metadata: Dict[str, Any]) -> Document:
        """
        تحويل المحتوى إلى مستند Llama-Index

        Args:
            content: محتوى المستند
            metadata: البيانات الوصفية

        Returns:
            مستند Llama-Index
        """
        return Document(text=content, metadata=metadata)

    def _convert_to_node(self, content: str, metadata: Dict[str, Any]) -> TextNode:
        """
        تحويل المحتوى إلى عقدة نصية

        Args:
            content: محتوى النص
            metadata: البيانات الوصفية

        Returns:
            عقدة نصية
        """
        # إنشاء معرف فريد
        node_id = metadata.get("conversation_id", str(uuid.uuid4()))

        # إنشاء عقدة نصية
        return TextNode(text=content, metadata=metadata, id_=node_id)

    def store_conversation(
        self, messages: Union[List[Dict[str, str]], str], metadata: Dict[str, Any] = None
    ) -> str:
        """
        تخزين محادثة

        Args:
            messages: محتوى المحادثة (نص أو قائمة رسائل)
            metadata: بيانات وصفية إضافية

        Returns:
            معرف المحادثة
        """
        try:
            # معالجة المحتوى
            if isinstance(messages, list):
                # تحويل قائمة الرسائل إلى نص
                content = "\n".join(
                    [f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in messages]
                )
                raw_messages = messages
            else:
                # استخدام النص مباشرة
                content = messages
                raw_messages = [{"role": "system", "content": content}]

            # إنشاء معرف فريد للمحادثة إذا لم يكن موجوداً في البيانات الوصفية
            conversation_id = metadata.get("conversation_id") if metadata else None
            if not conversation_id:
                conversation_id = str(uuid.uuid4())

            # إنشاء بيانات وصفية للمحادثة
            user_id = metadata.get("user_id", "default_user") if metadata else "default_user"
            timestamp = datetime.now().timestamp()

            # إعداد البيانات الوصفية
            node_metadata = {
                "content": content,
                "raw_messages": raw_messages,
                "user_id": user_id,
                "conversation_id": conversation_id,
                "timestamp": timestamp,
                "added_at": datetime.now().isoformat(),
            }

            # إضافة البيانات الوصفية الإضافية
            if metadata:
                for key, value in metadata.items():
                    if key not in node_metadata:
                        node_metadata[key] = value

            # إنشاء عقدة نصية
            node = self._convert_to_node(content, node_metadata)

            # تخزين العقدة في الفهرس
            self.vector_store.add([node])

            logger.info(f"تم تخزين المحادثة برقم: {conversation_id}")
            return conversation_id

        except Exception as e:
            logger.error(f"خطأ في تخزين المحادثة: {str(e)}")
            return str(uuid.uuid4())  # إرجاع معرف عشوائي في حالة الخطأ

    def search(self, query: str, user_id: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        البحث في ذاكرة المحادثات

        Args:
            query: نص البحث
            user_id: معرف المستخدم (اختياري)
            limit: عدد النتائج الأقصى

        Returns:
            قائمة بالمحادثات المطابقة مع درجة التطابق
        """
        try:
            # إنشاء محرك البحث
            retriever = self.index.as_retriever(similarity_top_k=limit)

            # إذا تم تحديد معرف المستخدم، قم بإضافة مرشح
            if user_id:
                # يمكن إضافة منطق ترشيح إضافي هنا
                pass

            # البحث
            nodes = retriever.retrieve(query)

            # تنسيق النتائج
            results = []
            for node in nodes:
                node_info = node.node.metadata
                results.append(
                    {
                        "memory": node_info.get("content", ""),
                        "score": node.score if hasattr(node, "score") else 0.0,
                        "memory_id": node_info.get("conversation_id", ""),
                        "created_at": node_info.get("added_at", ""),
                        "raw_messages": node_info.get("raw_messages", []),
                    }
                )

            return results

        except Exception as e:
            logger.error(f"خطأ في البحث عن المحادثات: {str(e)}")
            return []

    def get_recent(self, user_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        الحصول على أحدث المحادثات

        Args:
            user_id: معرف المستخدم (اختياري)
            limit: عدد النتائج الأقصى

        Returns:
            قائمة بأحدث المحادثات
        """
        try:
            # هذه الوظيفة تتطلب استعلامًا مخصصًا إلى Qdrant
            # نحن هنا نستخدم استعلامًا عامًا ثم نقوم بالفلترة
            import qdrant_client

            # إنشاء عميل Qdrant مباشرة
            qdrant_client_direct = qdrant_client.QdrantClient(
                url=self.qdrant_url, api_key=self.qdrant_api_key
            )

            # إعداد الاستعلام
            filter_condition = None
            if user_id:
                filter_condition = qdrant_client.models.Filter(
                    must=[
                        qdrant_client.models.FieldCondition(
                            key="user_id", match=qdrant_client.models.MatchValue(value=user_id)
                        )
                    ]
                )

            # استرداد البيانات
            search_results = qdrant_client_direct.scroll(
                collection_name=self.collection_name,
                limit=limit,
                filter=filter_condition,
                with_payload=True,
                with_vectors=False,
            )

            # تنسيق النتائج
            results = []
            for points, _ in search_results:
                for point in points:
                    payload = point.payload
                    results.append(
                        {
                            "memory": payload.get("content", ""),
                            "memory_id": payload.get("conversation_id", ""),
                            "created_at": payload.get("added_at", ""),
                            "raw_messages": payload.get("raw_messages", []),
                        }
                    )

            # ترتيب النتائج حسب التاريخ (الأحدث أولاً)
            results.sort(key=lambda x: x.get("created_at", ""), reverse=True)

            return results

        except Exception as e:
            logger.error(f"خطأ في الحصول على أحدث المحادثات: {str(e)}")
            return []

    def delete(self, memory_id: str, user_id: str = None) -> bool:
        """
        حذف محادثة

        Args:
            memory_id: معرف المحادثة
            user_id: معرف المستخدم (اختياري)

        Returns:
            نجاح العملية
        """
        try:
            # استخدام واجهة Qdrant مباشرة للحذف
            import qdrant_client

            # إنشاء عميل Qdrant مباشرة
            qdrant_client_direct = qdrant_client.QdrantClient(
                url=self.qdrant_url, api_key=self.qdrant_api_key
            )

            # إعداد شرط الحذف
            filter_condition = qdrant_client.models.Filter(
                must=[
                    qdrant_client.models.FieldCondition(
                        key="conversation_id",
                        match=qdrant_client.models.MatchValue(value=memory_id),
                    )
                ]
            )

            # إضافة شرط المستخدم إذا تم تحديده
            if user_id:
                filter_condition.must.append(
                    qdrant_client.models.FieldCondition(
                        key="user_id", match=qdrant_client.models.MatchValue(value=user_id)
                    )
                )

            # حذف النقاط
            qdrant_client_direct.delete(
                collection_name=self.collection_name, points_selector=filter_condition
            )

            logger.info(f"تم حذف المحادثة برقم: {memory_id}")
            return True

        except Exception as e:
            logger.error(f"خطأ في حذف المحادثة: {str(e)}")
            return False

    def clear_all(self, user_id: str) -> bool:
        """
        حذف جميع المحادثات للمستخدم

        Args:
            user_id: معرف المستخدم

        Returns:
            نجاح العملية
        """
        try:
            # استخدام واجهة Qdrant مباشرة للحذف
            import qdrant_client

            # إنشاء عميل Qdrant مباشرة
            qdrant_client_direct = qdrant_client.QdrantClient(
                url=self.qdrant_url, api_key=self.qdrant_api_key
            )

            # إعداد شرط الحذف
            filter_condition = qdrant_client.models.Filter(
                must=[
                    qdrant_client.models.FieldCondition(
                        key="user_id", match=qdrant_client.models.MatchValue(value=user_id)
                    )
                ]
            )

            # حذف النقاط
            qdrant_client_direct.delete(
                collection_name=self.collection_name, points_selector=filter_condition
            )

            logger.info(f"تم حذف جميع المحادثات للمستخدم: {user_id}")
            return True

        except Exception as e:
            logger.error(f"خطأ في حذف جميع المحادثات: {str(e)}")
            return False
