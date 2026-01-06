import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { TrendingUp, TrendingDown, Minus, AlertTriangle } from 'lucide-react';
import { api } from '../api';

const parameters = [
  { id: 'hardness', label: 'Dureté (N)', min: 60, max: 120, target: 90 },
  { id: 'yield_percent', label: 'Rendement (%)', min: 95, max: 100, target: 98 },
  { id: 'compression_force', label: 'Force compression (kN)', min: 15, max: 25, target: 20 },
  { id: 'weight', label: 'Poids (mg)', min: 490, max: 510, target: 500 },
];

export default function Trends() {
  const [selectedParam, setSelectedParam] = useState('hardness');
  const [days, setDays] = useState(30);
  const [trendData, setTrendData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTrends();
  }, [selectedParam, days]);

  async function loadTrends() {
    setLoading(true);
    try {
      const data = await api.getTrends(selectedParam, days);
      setTrendData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  const param = parameters.find(p => p.id === selectedParam);
  const chartData = trendData?.dates?.map((date, i) => ({
    date: date.slice(5),
    value: trendData.values[i]
  })) || [];

  const TrendIcon = trendData?.trend_direction === 'hausse' ? TrendingUp 
    : trendData?.trend_direction === 'baisse' ? TrendingDown : Minus;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <h2 className="text-2xl font-bold text-gray-900">Analyse des Tendances</h2>
        <div className="flex gap-3">
          <select
            value={selectedParam}
            onChange={(e) => setSelectedParam(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            {parameters.map(p => (
              <option key={p.id} value={p.id}>{p.label}</option>
            ))}
          </select>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value={7}>7 jours</option>
            <option value={30}>30 jours</option>
            <option value={90}>90 jours</option>
            <option value={365}>1 an</option>
          </select>
        </div>
      </div>

      {trendData?.alert && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 flex items-center gap-3">
          <AlertTriangle className="text-yellow-500" size={24} />
          <div>
            <p className="font-semibold text-yellow-800">Tendance détectée</p>
            <p className="text-yellow-600 text-sm">
              Le paramètre {param?.label} montre une tendance à la {trendData.trend_direction} significative.
            </p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="font-semibold text-gray-900">{param?.label}</h3>
            <p className="text-sm text-gray-500">Derniers {days} jours</p>
          </div>
          {trendData && !trendData.error && (
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-gray-500">Moyenne</p>
                <p className="text-xl font-bold text-gray-900">{trendData.average}</p>
              </div>
              <div className={`p-3 rounded-lg ${
                trendData.alert ? 'bg-yellow-100' : 'bg-green-100'
              }`}>
                <TrendIcon size={24} className={trendData.alert ? 'text-yellow-600' : 'text-green-600'} />
              </div>
            </div>
          )}
        </div>

        {loading ? (
          <div className="h-80 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : trendData?.error ? (
          <div className="h-80 flex items-center justify-center text-gray-500">
            <p>{trendData.error}</p>
          </div>
        ) : chartData.length === 0 ? (
          <div className="h-80 flex items-center justify-center text-gray-500">
            <p>Aucune donnée disponible. Importez des données pour voir les tendances.</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
              <YAxis stroke="#6b7280" fontSize={12} domain={[param?.min || 'auto', param?.max || 'auto']} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px'
                }}
              />
              {param?.target && (
                <ReferenceLine y={param.target} stroke="#22c55e" strokeDasharray="5 5" label="Target" />
              )}
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#2563eb" 
                strokeWidth={2}
                dot={{ fill: '#2563eb', strokeWidth: 2 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
