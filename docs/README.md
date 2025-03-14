# نظام الوكلاء المتعددين للتحليل النصي

## نظرة عامة

نظام الوكلاء المتعددين هو إطار عمل متكامل لتحليل النصوص العربية والإسلامية باستخدام مجموعة من الوكلاء المتخصصين. يوفر النظام واجهة موحدة للتفاعل مع الوكلاء المختلفة، ويدعم تنسيق عملها وحل التعارضات بينها.

## الوكلاء المتوفرة

النظام يتضمن الوكلاء التالية:

1. **وكيل التحليل اللغوي (LinguisticAgent)**: يقوم بتحليل النص من الناحية اللغوية، بما في ذلك التحليل الصرفي والنحوي والدلالي والبلاغي.

2. **وكيل اكتشاف الأنماط (PatternDiscoveryAgent)**: يكتشف الأنماط والعلاقات في النصوص، مثل التكرار والتوازي والتقابل.

3. **وكيل الاستدلال (ReasoningAgent)**: يستخلص الاستدلالات والاستنتاجات المنطقية من النصوص.

4. **وكيل البحث (SearchAgent)**: يبحث عن المعلومات ذات الصلة في مصادر البيانات المختلفة.

5. **وكيل المعجزات العلمية (ScientificMiraclesAgent)**: يحلل الآيات المتعلقة بالظواهر العلمية ويربطها بالاكتشافات العلمية الحديثة.

6. **وكيل استخراج المسارات الموضوعية (ThematicPathAgent)**: يستخرج المسارات الموضوعية والمفاهيمية في النصوص.

## الميزات الرئيسية

- **تحليل متعدد الأبعاد**: يجمع النظام بين مختلف أنواع التحليل (لغوي، موضوعي، علمي، إلخ).
- **قابلية التوسع**: يمكن إضافة وكلاء جديدة بسهولة.
- **تكوين مرن**: يمكن تكوين الوكلاء باستخدام ملفات YAML.
- **تسجيل تلقائي**: يمكن اكتشاف وتسجيل الوكلاء تلقائياً.
- **استراتيجيات تنفيذ متعددة**: يدعم التنفيذ المتوازي والمتسلسل للوكلاء.
- **حل التعارضات**: يوفر آليات لحل التعارضات بين نتائج الوكلاء المختلفة.

## الوثائق

- [آلية تحميل الوكلاء من ملفات YAML](agent_loader.md)
- [وكيل التحليل اللغوي](linguistic_agent.md)
- [وكيل المعجزات العلمية](scientific_miracles_agent.md)
- [وكيل استخراج المسارات الموضوعية](thematic_path_agent.md)

## استخدام النظام

### التهيئة البسيطة

```python
from core.ai.multi_agent_system import MultiAgentSystem

# إنشاء نظام الوكلاء المتعددين
system = MultiAgentSystem()

# تسجيل الوكلاء يدوياً
from core.ai.multi_agent_system import LinguisticAgent, PatternDiscoveryAgent
system.register_agent(LinguisticAgent(name="linguistic"))
system.register_agent(PatternDiscoveryAgent(name="pattern"))

# معالجة استعلام
results = system.process_query("ما هي الآيات التي تتحدث عن خلق الإنسان؟")
```

### التهيئة باستخدام التسجيل التلقائي

```python
from core.ai.multi_agent_system import MultiAgentSystem

# إنشاء نظام الوكلاء المتعددين مع تفعيل التسجيل التلقائي
system = MultiAgentSystem(auto_register=True)

# معالجة استعلام
results = system.process_query("ما هي الآيات التي تتحدث عن خلق الإنسان؟")
```

## التطوير والمساهمة

### إضافة وكيل جديد

1. قم بإنشاء فئة جديدة ترث من الفئة الأساسية `Agent`:

```python
from core.ai.multi_agent_system import Agent

class NewSpecializedAgent(Agent):
    def __init__(self, name, param1=None, param2=None):
        super().__init__(name)
        self.param1 = param1
        self.param2 = param2
    
    def process(self, query, context=None):
        # تنفيذ منطق المعالجة الخاص بالوكيل
        return {
            "result": "نتيجة المعالجة",
            "param1": self.param1,
            "param2": self.param2
        }
```

2. أضف الوكيل إلى ملف التكوين:

```yaml
agents:
  # الوكيل الجديد
  - name: new_agent
    type: NewSpecializedAgent
    enabled: true
    file: new_agent.yaml
```

### اختبار النظام

```bash
# تشغيل جميع الاختبارات
python -m pytest tests/

# تشغيل اختبارات وحدة محددة
python -m pytest tests/test_ai/test_agent_loader.py -v
``` 