# مكونات لوحات التحكم

## 1. المكونات المشتركة (Shared Components)

### 1.1 الرسوم البيانية الأساسية
```typescript
// components/charts/BaseChart.tsx
import { Line, Bar, Pie } from 'react-chartjs-2';

interface ChartProps {
  data: any;
  type: 'line' | 'bar' | 'pie';
  options?: any;
}

export const BaseChart: React.FC<ChartProps> = ({ data, type, options }) => {
  const ChartComponent = {
    line: Line,
    bar: Bar,
    pie: Pie
  }[type];

  return (
    <div className="chart-container">
      <ChartComponent data={data} options={options} />
    </div>
  );
};
```

### 1.2 خريطة المفاهيم
```typescript
// components/graphs/ConceptMap.tsx
import { Network } from 'vis-network/standalone';

interface ConceptMapProps {
  nodes: ConceptNode[];
  edges: ConceptEdge[];
  onNodeClick?: (node: ConceptNode) => void;
}

export const ConceptMap: React.FC<ConceptMapProps> = ({ nodes, edges, onNodeClick }) => {
  const options = {
    nodes: {
      shape: 'dot',
      scaling: {
        min: 10,
        max: 30
      }
    },
    edges: {
      smooth: {
        type: 'continuous'
      }
    },
    physics: {
      stabilization: true,
      barnesHut: {
        gravitationalConstant: -80000,
        springConstant: 0.001,
        springLength: 200
      }
    }
  };

  return (
    <div className="concept-map">
      <Network
        data={{ nodes, edges }}
        options={options}
        events={{
          click: (event) => {
            const nodeId = event.nodes[0];
            const node = nodes.find(n => n.id === nodeId);
            if (node && onNodeClick) onNodeClick(node);
          }
        }}
      />
    </div>
  );
};
```

## 2. مكونات داشبورد المستخدمين

### 2.1 البطاقات الإحصائية
```typescript
// components/user/StatCard.tsx
interface StatCardProps extends StatCard {
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  icon,
  className
}) => {
  const isPositive = change >= 0;
  
  return (
    <div className={`stat-card ${className}`}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-content">
        <h3>{title}</h3>
        <div className="stat-value">{value}</div>
        <div className={`stat-change ${isPositive ? 'positive' : 'negative'}`}>
          {change}%
        </div>
      </div>
    </div>
  );
};
```

### 2.2 محرك البحث المتقدم
```typescript
// components/user/AdvancedSearch.tsx
interface AdvancedSearchProps {
  onSearch: (filters: SearchFilters) => void;
  initialFilters?: Partial<SearchFilters>;
}

export const AdvancedSearch: React.FC<AdvancedSearchProps> = ({
  onSearch,
  initialFilters
}) => {
  const [filters, setFilters] = useState<SearchFilters>({
    type: [],
    date: { start: null, end: null },
    confidence: 0,
    topics: [],
    ...initialFilters
  });

  return (
    <div className="advanced-search">
      <MultiSelect
        label="نوع البحث"
        options={searchTypes}
        value={filters.type}
        onChange={(value) => setFilters({ ...filters, type: value })}
      />
      <DateRangePicker
        label="النطاق الزمني"
        value={filters.date}
        onChange={(value) => setFilters({ ...filters, date: value })}
      />
      <Slider
        label="مستوى الثقة"
        min={0}
        max={1}
        step={0.1}
        value={filters.confidence}
        onChange={(value) => setFilters({ ...filters, confidence: value })}
      />
      <TopicSelector
        value={filters.topics}
        onChange={(value) => setFilters({ ...filters, topics: value })}
      />
      <Button onClick={() => onSearch(filters)}>بحث</Button>
    </div>
  );
};
```

## 3. مكونات داشبورد الإدارة

### 3.1 مراقبة النظام
```typescript
// components/admin/SystemMonitor.tsx
interface SystemMonitorProps {
  metrics: SystemMetrics;
  refreshInterval?: number;
}

export const SystemMonitor: React.FC<SystemMonitorProps> = ({
  metrics,
  refreshInterval = 5000
}) => {
  const [currentMetrics, setCurrentMetrics] = useState(metrics);

  useEffect(() => {
    const timer = setInterval(async () => {
      const newMetrics = await fetchSystemMetrics();
      setCurrentMetrics(newMetrics);
    }, refreshInterval);

    return () => clearInterval(timer);
  }, [refreshInterval]);

  return (
    <div className="system-monitor">
      <ResourceGauge
        type="cpu"
        value={currentMetrics.cpu.usage}
        threshold={metricsChartConfig.alerts.cpu}
      />
      <ResourceGauge
        type="memory"
        value={(currentMetrics.memory.used / currentMetrics.memory.total) * 100}
        threshold={metricsChartConfig.alerts.memory}
      />
      <ResourceGauge
        type="disk"
        value={(currentMetrics.disk.used / currentMetrics.disk.total) * 100}
        threshold={metricsChartConfig.alerts.disk}
      />
      <PerformanceChart metrics={currentMetrics} />
    </div>
  );
};
```

### 3.2 مراقبة الوكلاء
```typescript
// components/admin/AgentMonitor.tsx
interface AgentMonitorProps {
  agents: AgentStatus[];
  onAgentAction: (agentId: string, action: string) => void;
}

export const AgentMonitor: React.FC<AgentMonitorProps> = ({
  agents,
  onAgentAction
}) => {
  return (
    <div className="agent-monitor">
      <div className="agent-list">
        {agents.map(agent => (
          <AgentCard
            key={agent.id}
            agent={agent}
            onAction={(action) => onAgentAction(agent.id, action)}
          />
        ))}
      </div>
      <AgentPerformanceChart agents={agents} />
      <ResourceAllocationTable agents={agents} />
    </div>
  );
};
```

## 4. التنسيقات والأنماط

### 4.1 الألوان والمتغيرات
```scss
// styles/variables.scss
:root {
  // الألوان الأساسية
  --primary-color: #2c3e50;
  --secondary-color: #34495e;
  --accent-color: #3498db;
  
  // ألوان الحالة
  --success-color: #2ecc71;
  --warning-color: #f1c40f;
  --error-color: #e74c3c;
  
  // المسافات
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  // الخطوط
  --font-primary: 'Cairo', sans-serif;
  --font-secondary: 'Tajawal', sans-serif;
}
```

### 4.2 تنسيقات المكونات
```scss
// styles/components.scss
.stat-card {
  background: var(--primary-color);
  border-radius: 8px;
  padding: var(--spacing-md);
  color: white;
  
  .stat-value {
    font-size: 2rem;
    font-weight: bold;
  }
  
  .stat-change {
    &.positive { color: var(--success-color); }
    &.negative { color: var(--error-color); }
  }
}

.chart-container {
  background: white;
  border-radius: 8px;
  padding: var(--spacing-md);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.concept-map {
  height: 600px;
  border: 1px solid var(--secondary-color);
  border-radius: 8px;
}
``` 