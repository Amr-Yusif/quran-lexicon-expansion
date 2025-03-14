# دليل اختبارات مشروع تحليل النصوص القرآنية والإسلامية

هذا الدليل يشرح منهجية الاختبارات المتبعة في المشروع وكيفية استخدام الأدوات المتاحة لكتابة اختبارات فعالة.

## منهجية الاختبارات

نستخدم إطار عمل pytest لتنفيذ الاختبارات، مع التركيز على:

1. **استخدام Fixtures**: لإعداد بيانات مشتركة بين الاختبارات
2. **استخدام Parametrization**: لتشغيل نفس الاختبار ببيانات مختلفة
3. **اختبارات الوحدة**: لاختبار المكونات الفردية
4. **اختبارات التكامل**: لاختبار تفاعل المكونات مع بعضها

## هيكل الاختبارات

```
tests/
├── conftest.py         # تعريف الـ fixtures المشتركة
├── data/               # بيانات الاختبار
├── integration/        # اختبارات التكامل
└── unit/               # اختبارات الوحدة
```

## استخدام Fixtures

الـ fixtures هي دوال تعيد قيمًا يمكن استخدامها في الاختبارات. يتم تعريفها في ملف `conftest.py` ويمكن استخدامها في أي اختبار.

### أمثلة على الـ fixtures المتاحة:

- `test_data_dir`: مسار دليل بيانات الاختبار
- `mock_agents`: مجموعة من الوكلاء الوهميين للاختبارات
- `coordinator_factory`: مصنع لإنشاء منسقي وكلاء بإعدادات مختلفة
- `mock_sentence_transformer`: وهم لنموذج SentenceTransformer
- `mock_ollama`: وهم لـ Ollama

### مثال على استخدام fixture:

```python
def test_multi_agent_system(mock_agents):
    # إنشاء نظام الوكلاء المتعددين
    system = MultiAgentSystem()
    
    # تسجيل الوكلاء من fixture
    for agent_name, agent in mock_agents.items():
        system.register_agent(agent)
    
    # اختبار النظام
    # ...
```

## استخدام Parametrization

الـ parametrization تسمح بتشغيل نفس الاختبار ببيانات مختلفة، مما يقلل من تكرار الكود ويزيد من تغطية الاختبارات.

### مثال على استخدام parametrization:

```python
@pytest.mark.parametrize(
    "strategy,weights,trust_scores,conflicting_data,expected_value",
    [
        # استراتيجية الترجيح
        (
            "weighted", 
            {"agent1": 0.7, "agent2": 0.3}, 
            None, 
            {"key": {"agent1": "value1", "agent2": "value2"}},
            "value1"  # الوكيل 1 له وزن أعلى
        ),
        # استراتيجية الأغلبية
        (
            "majority", 
            None, 
            None, 
            {"key": {"agent1": "value1", "agent2": "value1", "agent3": "value2"}},
            "value1"  # القيمة 1 لها أغلبية
        ),
    ]
)
def test_conflict_resolution_strategies(coordinator_factory, strategy, weights, trust_scores, conflicting_data, expected_value):
    # إنشاء منسق الوكلاء
    coordinator = coordinator_factory(conflict_resolution_strategy=strategy)
    
    # تعيين الأوزان ودرجات الثقة
    # ...
    
    # اختبار استراتيجية حل التعارضات
    # ...
```

## تشغيل الاختبارات

### تشغيل جميع الاختبارات:

```bash
pytest
```

### تشغيل اختبارات وحدة محددة:

```bash
pytest tests/unit/test_multi_agent_system.py
```

### تشغيل اختبار محدد:

```bash
pytest tests/unit/test_multi_agent_system.py::TestMultiAgentSystem::test_initialization
```

### تشغيل الاختبارات مع تقرير تغطية الكود:

```bash
pytest --cov=core tests/
```

## أفضل الممارسات

1. **استخدام fixtures**: استخدم fixtures لإعداد البيانات المشتركة بين الاختبارات
2. **استخدام parametrization**: استخدم parametrization لاختبار نفس الوظيفة ببيانات مختلفة
3. **تسمية الاختبارات**: استخدم أسماء وصفية للاختبارات تشرح ما يتم اختباره
4. **تنظيم الاختبارات**: نظم الاختبارات في فئات وملفات منطقية
5. **استخدام mock**: استخدم mock للمكونات الخارجية لتسريع الاختبارات وتقليل الاعتماد على الخدمات الخارجية
6. **تشغيل الاختبارات بانتظام**: شغل الاختبارات بعد كل تعديل في الكود
7. **دمج الاختبارات في CI/CD**: دمج الاختبارات في نظام CI/CD لتشغيلها تلقائيًا عند دفع التغييرات

## إضافة اختبارات جديدة

1. حدد المكون الذي تريد اختباره
2. حدد السلوك المتوقع من المكون
3. اكتب اختبارًا يتحقق من السلوك المتوقع
4. استخدم fixtures وparametrization لتقليل تكرار الكود
5. تأكد من تغطية جميع حالات الاستخدام والحالات الحدية

## تنفيذ الاختبارات في CI/CD

يمكن دمج الاختبارات في نظام CI/CD باستخدام GitHub Actions أو أي نظام CI/CD آخر. يمكن إعداد سير عمل يقوم بتشغيل الاختبارات تلقائيًا عند دفع التغييرات إلى المستودع.

### مثال على ملف GitHub Actions:

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov
        pip install -r requirements.txt
    - name: Test with pytest
      run: |
        pytest --cov=core tests/
```