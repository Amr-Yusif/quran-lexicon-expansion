"""ملف تكوين pytest لإعداد بيئة الاختبار."""

import os
import pytest
from unittest.mock import MagicMock, patch
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional

# تكوين بيئة الاختبار
@pytest.fixture(scope="session")
def test_data_dir():
    """إرجاع مسار دليل بيانات الاختبار."""
    base_dir = Path(__file__).parent
    return base_dir / "data"

@pytest.fixture(scope="session", autouse=True)
def setup_test_env(test_data_dir):
    """إعداد بيئة الاختبار وإنشاء ملفات بيانات الاختبار."""
    # إنشاء دليل بيانات الاختبار إذا لم يكن موجودًا
    test_data_dir.mkdir(exist_ok=True)
    
    # إنشاء بيانات اختبار للقرآن الكريم (مصغرة للاختبار)
    quran_test_data = {
        "data": {
            "surahs": [
                {
                    "number": 1,
                    "name": "الفاتحة",
                    "englishName": "Al-Fatiha",
                    "ayahs": [
                        {"number": 1, "text": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ", "numberInSurah": 1},
                        {"number": 2, "text": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ", "numberInSurah": 2},
                        {"number": 3, "text": "الرَّحْمَٰنِ الرَّحِيمِ", "numberInSurah": 3},
                        {"number": 4, "text": "مَالِكِ يَوْمِ الدِّينِ", "numberInSurah": 4},
                        {"number": 5, "text": "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ", "numberInSurah": 5},
                        {"number": 6, "text": "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ", "numberInSurah": 6},
                        {"number": 7, "text": "صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ", "numberInSurah": 7}
                    ]
                },
                {
                    "number": 2,
                    "name": "البقرة",
                    "englishName": "Al-Baqarah",
                    "ayahs": [
                        {"number": 8, "text": "الم", "numberInSurah": 1},
                        {"number": 9, "text": "ذَٰلِكَ الْكِتَابُ لَا رَيْبَ فِيهِ هُدًى لِلْمُتَّقِينَ", "numberInSurah": 2},
                        {"number": 10, "text": "الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ وَمِمَّا رَزَقْنَاهُمْ يُنْفِقُونَ", "numberInSurah": 3}
                    ]
                }
            ]
        }
    }
    
    # إنشاء بيانات اختبار للتفسير (مصغرة للاختبار)
    tafseer_test_data = [
        {"surah": 1, "ayah": 1, "text": "بسم الله الرحمن الرحيم: ابتداء بالتبرك باسم الله المتصف بصفات الرحمة العامة والخاصة."},
        {"surah": 1, "ayah": 2, "text": "الحمد لله رب العالمين: الثناء على الله بصفات الكمال وأفعال الجمال، وهو تعالى المربي جميع العوالم."},
        {"surah": 1, "ayah": 3, "text": "الرحمن الرحيم: المتصف بالرحمة الشاملة لجميع الخلق في الدنيا، والخاصة بالمؤمنين في الآخرة."}
    ]
    
    # إنشاء بيانات اختبار للمعجزات العلمية
    scientific_miracles_test_data = [
        {
            "title": "دورة الماء في الطبيعة",
            "ayahs": [
                {"surah": 30, "ayah": 48, "text": "اللَّهُ الَّذِي يُرْسِلُ الرِّيَاحَ فَتُثِيرُ سَحَابًا فَيَبْسُطُهُ فِي السَّمَاءِ كَيْفَ يَشَاءُ وَيَجْعَلُهُ كِسَفًا فَتَرَى الْوَدْقَ يَخْرُجُ مِنْ خِلَالِهِ"},
                {"surah": 24, "ayah": 43, "text": "أَلَمْ تَرَ أَنَّ اللَّهَ يُزْجِي سَحَابًا ثُمَّ يُؤَلِّفُ بَيْنَهُ ثُمَّ يَجْعَلُهُ رُكَامًا فَتَرَى الْوَدْقَ يَخْرُجُ مِنْ خِلَالِهِ"}
            ],
            "explanation": "وصف القرآن لدورة الماء في الطبيعة بدقة علمية، حيث يذكر دور الرياح في تكوين السحب وتراكمها ثم نزول المطر منها.",
            "scientific_reference": "دورة الماء هي العملية التي ينتقل فيها الماء باستمرار بين سطح الأرض والغلاف الجوي."
        },
        {
            "title": "توسع الكون",
            "ayahs": [
                {"surah": 51, "ayah": 47, "text": "وَالسَّمَاءَ بَنَيْنَاهَا بِأَيْدٍ وَإِنَّا لَمُوسِعُونَ"}
            ],
            "explanation": "تشير الآية إلى توسع الكون المستمر، وهو ما أكدته النظريات العلمية الحديثة مثل نظرية الانفجار العظيم.",
            "scientific_reference": "اكتشف العلماء في القرن العشرين أن الكون يتوسع باستمرار، وهو ما يتوافق مع ما ذكره القرآن قبل 14 قرنًا."
        }
    ]
    
    # كتابة ملفات الاختبار
    with open(test_data_dir / "quran_test.json", "w", encoding="utf-8") as f:
        json.dump(quran_test_data, f, ensure_ascii=False, indent=2)
        
    with open(test_data_dir / "tafseer_test.json", "w", encoding="utf-8") as f:
        json.dump(tafseer_test_data, f, ensure_ascii=False, indent=2)
        
    with open(test_data_dir / "scientific_miracles_test.json", "w", encoding="utf-8") as f:
        json.dump(scientific_miracles_test_data, f, ensure_ascii=False, indent=2)
    
    yield
    
    # يمكن تنظيف الملفات بعد انتهاء الاختبارات إذا لزم الأمر
    # لكن في الغالب نحتفظ بها للتحقق اليدوي


# أوهام للمكتبات الخارجية
@pytest.fixture
def mock_qdrant_client():
    """وهم لعميل Qdrant للاختبارات."""
    with patch("local_mem0_agent.core.rag.qdrant_manager.QdrantClient") as mock:
        client = MagicMock()
        mock.return_value = client
        
        # محاكاة استجابات العميل
        client.get_collection.return_value = MagicMock(exists=True)
        client.search.return_value = [
            {"id": "1", "payload": {"text": "نص اختبار", "metadata": {"source": "القرآن"}}, "score": 0.95},
            {"id": "2", "payload": {"text": "نص آخر للاختبار", "metadata": {"source": "التفسير"}}, "score": 0.85}
        ]
        
        yield client

# إضافة fixtures متقدمة لنظام الوكلاء المتعددين
@pytest.fixture
def agent_base():
    """إنشاء وكيل أساسي للاختبارات."""
    from core.ai.multi_agent_system import Agent
    
    class TestAgent(Agent):
        def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
            return {"result": f"معالجة {query} بواسطة {self.name}"}
    
    return TestAgent

@pytest.fixture
def mock_agents(agent_base):
    """إنشاء مجموعة من الوكلاء الوهميين للاختبارات."""
    agents = {
        "linguistic_agent": agent_base("linguistic_agent"),
        "pattern_agent": agent_base("pattern_agent"),
        "reasoning_agent": agent_base("reasoning_agent"),
        "search_agent": agent_base("search_agent")
    }
    
    # تخصيص سلوك كل وكيل
    agents["linguistic_agent"].process = MagicMock(return_value={"analysis": "تحليل لغوي للنص"})
    agents["pattern_agent"].process = MagicMock(return_value={"patterns": ["نمط1", "نمط2"]})
    agents["reasoning_agent"].process = MagicMock(return_value={"conclusions": ["استنتاج1", "استنتاج2"]})
    agents["search_agent"].process = MagicMock(return_value={"results": ["نتيجة1", "نتيجة2"]})
    
    return agents

@pytest.fixture
def coordinator_factory():
    """مصنع لإنشاء منسقي وكلاء بإعدادات مختلفة."""
    from core.ai.multi_agent_system import AgentCoordinator
    
    def _create_coordinator(execution_strategy="parallel", conflict_resolution_strategy="weighted", 
                           weights=None, trust_scores=None):
        coordinator = AgentCoordinator(execution_strategy, conflict_resolution_strategy)
        
        if weights:
            coordinator.set_agent_weights(weights)
        
        if trust_scores:
            coordinator.set_agent_trust_scores(trust_scores)
            
        return coordinator
    
    return _create_coordinator


@pytest.fixture
def mock_sentence_transformer():
    """وهم لنموذج SentenceTransformer للاختبارات."""
    with patch("sentence_transformers.SentenceTransformer") as mock:
        model = MagicMock()
        mock.return_value = model
        
        # محاكاة استجابات النموذج
        model.encode.return_value = [[0.1, 0.2, 0.3, 0.4, 0.5]]
        model.get_sentence_embedding_dimension.return_value = 5
        
        yield model


@pytest.fixture
def mock_ollama():
    """وهم لـ Ollama للاختبارات."""
    with patch("ollama.chat") as mock:
        mock.return_value = {
            "model": "mistral",
            "created_at": "2023-01-01T12:00:00Z",
            "message": {"role": "assistant", "content": "هذه إجابة وهمية للاختبار."},
            "done": True
        }
        yield mock


@pytest.fixture
def mock_pdf_file():
    """إنشاء ملف PDF وهمي للاختبار."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        # يمكن إضافة محتوى PDF فعلي هنا إذا لزم الأمر
        tmp_file_path = tmp_file.name
    
    yield tmp_file_path
    
    # تنظيف الملف بعد الانتهاء
    if os.path.exists(tmp_file_path):
        os.unlink(tmp_file_path)


@pytest.fixture
def mock_sentence_transformer():
    """وهم لنموذج SentenceTransformer للاختبارات."""
    with patch("sentence_transformers.SentenceTransformer") as mock:
        model = MagicMock()
        mock.return_value = model
        
        # محاكاة استجابات النموذج
        model.encode.return_value = [[0.1, 0.2, 0.3, 0.4, 0.5]]
        model.get_sentence_embedding_dimension.return_value = 5
        
        yield model


@pytest.fixture
def mock_ollama():
    """وهم لـ Ollama للاختبارات."""
    with patch("ollama.chat") as mock:
        mock.return_value = {
            "model": "mistral",
            "created_at": "2023-01-01T12:00:00Z",
            "message": {"role": "assistant", "content": "هذه إجابة وهمية للاختبار."},
            "done": True
        }
        yield mock


@pytest.fixture
def mock_pdf_file():
    """إنشاء ملف PDF وهمي للاختبار."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        # يمكن إضافة محتوى PDF فعلي هنا إذا لزم الأمر
        tmp_file_path = tmp_file.name
    
    yield tmp_file_path
    
    # تنظيف الملف بعد الانتهاء
    try:
        os.unlink(tmp_file_path)
    except:
        pass
