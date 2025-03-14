# آلية تحميل الوكلاء من ملفات YAML

## نظرة عامة

توفر هذه الآلية طريقة مرنة لتكوين وتحميل وتسجيل الوكلاء في نظام الوكلاء المتعددين باستخدام ملفات YAML. تسمح هذه الآلية بتعريف الوكلاء وإعداداتها بشكل منفصل عن الكود، مما يسهل تخصيص النظام دون الحاجة إلى تعديل الكود المصدري.

## الميزات الرئيسية

- تحميل تكوين الوكلاء من ملفات YAML
- اكتشاف فئات الوكلاء تلقائياً في المسارات المحددة
- تسجيل الوكلاء تلقائياً في نظام الوكلاء المتعددين
- دعم تمرير المعلمات المخصصة لكل وكيل
- تفعيل/تعطيل الوكلاء بسهولة من خلال ملفات التكوين

## هيكل ملفات التكوين

### ملف التكوين الرئيسي (`config/agents.yaml`)

يحتوي هذا الملف على الإعدادات العامة لنظام الوكلاء وقائمة بالوكلاء المراد تسجيلها:

```yaml
general:
  auto_register: true                # تفعيل التسجيل التلقائي
  config_dir: "config/agents"        # مسار مجلد ملفات تكوين الوكلاء
  default_enabled: true              # الحالة الافتراضية للوكلاء
  scan_directories:                  # مسارات البحث عن فئات الوكلاء
    - "core/ai"

agents:
  # وكيل التحليل اللغوي
  - name: linguistic_analyzer        # اسم الوكيل
    type: LinguisticAgent            # نوع الوكيل (اسم الفئة)
    enabled: true                    # حالة الوكيل (مفعل/معطل)
    file: linguistic_agent.yaml      # ملف تكوين الوكيل (اختياري)
  
  # وكيل اكتشاف الأنماط
  - name: pattern_discoverer
    type: PatternDiscoveryAgent
    enabled: true
    
  # وكيل الاستدلال
  - name: reasoner
    type: ReasoningAgent
    enabled: true
```

### ملفات تكوين الوكلاء الفردية

يمكن تعريف ملف تكوين منفصل لكل وكيل لتحديد المعلمات الخاصة به:

```yaml
# config/agents/linguistic_agent.yaml
name: linguistic_analyzer
type: LinguisticAgent
description: "وكيل متخصص في التحليل اللغوي للنصوص العربية"
enabled: true
parameters:
  analysis_types:
    - morphological
    - syntactic
    - semantic
    - rhetorical
  root_dictionary: "data/dictionaries/arabic_roots.json"
  rhetorical_figures:
    - استعارة
    - تشبيه
    - كناية
    - مجاز
  max_text_length: 10000
  max_sentences: 100
  weight: 0.8
  default_confidence: 0.75
```

## استخدام آلية التحميل التلقائي

### التسجيل التلقائي عند إنشاء النظام

```python
from core.ai.multi_agent_system import MultiAgentSystem

# إنشاء نظام الوكلاء المتعددين مع تفعيل التسجيل التلقائي
system = MultiAgentSystem(auto_register=True)

# طباعة قائمة الوكلاء المسجلين
print(f"عدد الوكلاء المسجلين: {len(system.agents)}")
print(f"الوكلاء المسجلين: {list(system.agents.keys())}")

# معالجة استعلام باستخدام الوكلاء المسجلين
results = system.process_query("ما هي الآيات التي تتحدث عن خلق الإنسان؟")
```

### التسجيل من ملف تكوين مخصص

```python
from core.ai.multi_agent_system import MultiAgentSystem

# إنشاء نظام الوكلاء المتعددين بدون تسجيل تلقائي
system = MultiAgentSystem(auto_register=False)

# تسجيل الوكلاء من ملف تكوين مخصص
registered = system.register_agents_from_config("config/custom_agents.yaml")

print(f"تم تسجيل {registered} وكيل بنجاح")
```

### استخدام محمل الوكلاء مباشرة

```python
from core.ai.agent_loader import AgentLoader
from core.ai.multi_agent_system import MultiAgentSystem

# إنشاء محمل الوكلاء
loader = AgentLoader("config/agents.yaml")

# اكتشاف فئات الوكلاء المتاحة
agent_classes = loader.discover_agent_classes()
print(f"فئات الوكلاء المكتشفة: {list(agent_classes.keys())}")

# إنشاء نظام الوكلاء المتعددين
system = MultiAgentSystem()

# تسجيل الوكلاء في النظام
registered = loader.register_agents(system)
print(f"تم تسجيل {registered} وكيل بنجاح")
```

## إضافة وكلاء جديدة

لإضافة وكيل جديد إلى النظام، اتبع الخطوات التالية:

1. قم بإنشاء فئة الوكيل الجديد التي ترث من الفئة الأساسية `Agent`:

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

2. أضف الوكيل إلى ملف التكوين الرئيسي:

```yaml
agents:
  # ... الوكلاء الحالية ...
  
  # الوكيل الجديد
  - name: new_agent
    type: NewSpecializedAgent
    enabled: true
    file: new_agent.yaml
```

3. قم بإنشاء ملف تكوين للوكيل الجديد (اختياري):

```yaml
# config/agents/new_agent.yaml
name: new_agent
type: NewSpecializedAgent
description: "وصف الوكيل الجديد"
enabled: true
parameters:
  param1: "قيمة1"
  param2: "قيمة2"
```

## ملاحظات هامة

- يجب أن تنتهي أسماء فئات الوكلاء بـ `Agent` ليتم اكتشافها تلقائياً.
- يجب أن ترث جميع فئات الوكلاء من الفئة الأساسية `Agent`.
- يجب أن تنفذ جميع فئات الوكلاء طريقة `process` التي تأخذ استعلاماً وسياقاً اختيارياً.
- يمكن تفعيل أو تعطيل الوكلاء من خلال تعيين خاصية `enabled` في ملف التكوين.
- يمكن تخصيص مسارات البحث عن فئات الوكلاء من خلال خاصية `scan_directories` في ملف التكوين الرئيسي. 