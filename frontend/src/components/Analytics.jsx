import { useState, useEffect } from 'react';
import { 
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, PieChart, Pie, Cell, RadarChart, Radar, 
  PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend
} from 'recharts';
import { 
  Search, Filter, Zap, TrendingUp, AlertTriangle, Users, 
  Factory, FileText, Layers, ArrowRight, ChevronDown
} from 'lucide-react';
import { api } from '../api';

const COLORS = ['#2563eb', '#22c55e', '#f97316', '#8b5cf6', '#ec4899', '#06b6d4'];

export default function Analytics() {
  const [activeTab, setActiveTab] = useState('overview');
  const [overview, setOverview] = useState(null);
  const [yearly, setYearly] = useState(null);
  const [suppliers, setSuppliers] = useState(null);
  const [equipment, setEquipment] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAllData();
  }, []);

  async function loadAllData() {
    setLoading(true);
    try {
      const [overviewData, yearlyData, suppliersData, equipmentData, comparisonData] = await Promise.all([
        api.getAnalyticsOverview(),
        api.getYearlySummary(),
        api.getSupplierPerformance(),
        api.getEquipmentAnalysis(),
        api.getPeriodComparison()
      ]);
      setOverview(overviewData);
      setYearly(yearlyData);
      setSuppliers(suppliersData);
      setEquipment(equipmentData);
      setComparison(comparisonData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  const tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: Layers },
    { id: 'production', label: 'Production', icon: Factory },
    { id: 'suppliers', label: 'Fournisseurs', icon: Users },
    { id: 'equipment', label: 'Équipements', icon: Factory },
    { id: 'comparison', label: 'Comparaison', icon: TrendingUp },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Chargement des analyses avancées...</p>
        </div>
      </div>
    );
  }

  if (!overview?.has_data) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-8 text-center">
        <AlertTriangle className="mx-auto text-yellow-500 mb-4" size={56} />
        <h3 className="font-semibold text-yellow-800 text-xl mb-2">Aucune donnée disponible</h3>
        <p className="text-yellow-600">
          Importez des données pour accéder aux analyses avancées.
        </p>
      </div>
    );
  }

  // Prepare radar chart data
  const radarData = [
    { metric: 'Rendement', value: overview?.production?.avg_yield || 0, fullMark: 100 },
    { metric: 'QC Pass', value: overview?.quality?.pass_rate || 0, fullMark: 100 },
    { metric: 'Calibrations OK', value: overview?.equipment?.calibration_pass_rate || 0, fullMark: 100 },
    { metric: 'Score Qualité', value: overview?.quality?.quality_score || 0, fullMark: 100 },
  ];

  // Yearly evolution data
  const yearlyChartData = yearly?.years || [];

  // Supplier pie chart data
  const supplierPieData = suppliers?.suppliers?.slice(0, 5).map(s => ({
    name: s.supplier_name || s.supplier_id,
    value: s.total_deliveries,
    rate: s.approval_rate
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analyses Avancées</h2>
          <p className="text-sm text-gray-500">
            Insights détaillés sur {overview?.period?.years} années de données
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-4">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 py-3 px-1 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon size={18} />
              <span className="font-medium">{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Performance Radar */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-4">Performance Globale</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis angle={30} domain={[0, 100]} />
                <Radar
                  name="Performance"
                  dataKey="value"
                  stroke="#2563eb"
                  fill="#2563eb"
                  fillOpacity={0.3}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Key Metrics */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-4">Métriques Clés</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Total lots analysés</span>
                <span className="text-xl font-bold">{overview?.production?.total_batches?.toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Tests QC effectués</span>
                <span className="text-xl font-bold">{overview?.quality?.total_tests?.toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Total plaintes</span>
                <span className="text-xl font-bold">{overview?.compliance?.total_complaints}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">CAPAs traitées</span>
                <span className="text-xl font-bold">{overview?.compliance?.total_capas}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-green-700">Score qualité global</span>
                <span className="text-xl font-bold text-green-700">{overview?.quality?.quality_score}/100</span>
              </div>
            </div>
          </div>

          {/* Yearly Evolution */}
          {yearlyChartData.length > 0 && (
            <div className="bg-white rounded-xl p-6 border border-gray-200 lg:col-span-2">
              <h3 className="font-semibold text-gray-900 mb-4">Évolution sur 6 ans</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={yearlyChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="year" stroke="#6b7280" />
                  <YAxis yAxisId="left" stroke="#6b7280" />
                  <YAxis yAxisId="right" orientation="right" stroke="#6b7280" />
                  <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }} />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="batches" name="Lots" stroke="#2563eb" strokeWidth={2} />
                  <Line yAxisId="right" type="monotone" dataKey="complaints" name="Plaintes" stroke="#ef4444" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* Production Tab */}
      {activeTab === 'production' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <p className="text-sm text-gray-500 mb-1">Production totale</p>
              <p className="text-3xl font-bold text-gray-900">{overview?.production?.total_batches?.toLocaleString()}</p>
              <p className="text-sm text-gray-400 mt-1">lots sur {overview?.period?.years} ans</p>
            </div>
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <p className="text-sm text-gray-500 mb-1">Rendement moyen</p>
              <p className="text-3xl font-bold text-green-600">{overview?.production?.avg_yield}%</p>
              <p className="text-sm text-gray-400 mt-1">
                Min: {overview?.production?.yield_range?.min}% | Max: {overview?.production?.yield_range?.max}%
              </p>
            </div>
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <p className="text-sm text-gray-500 mb-1">Production mensuelle</p>
              <p className="text-3xl font-bold text-gray-900">{overview?.production?.recent_batches}</p>
              <p className="text-sm text-gray-400 mt-1">lots ce mois</p>
            </div>
          </div>

          {/* Production by Year */}
          {yearlyChartData.length > 0 && (
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-4">Production par Année</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={yearlyChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="year" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }} />
                  <Bar dataKey="batches" name="Lots" fill="#2563eb" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* Suppliers Tab */}
      {activeTab === 'suppliers' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <p className="text-sm text-gray-500 mb-1">Total fournisseurs</p>
              <p className="text-3xl font-bold text-gray-900">{suppliers?.total_suppliers}</p>
            </div>
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <p className="text-sm text-gray-500 mb-1">Fournisseurs à risque</p>
              <p className="text-3xl font-bold text-red-600">{suppliers?.at_risk}</p>
            </div>
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <p className="text-sm text-gray-500 mb-1">Taux d'approbation moyen</p>
              <p className="text-3xl font-bold text-green-600">
                {suppliers?.suppliers?.length > 0
                  ? (suppliers.suppliers.reduce((acc, s) => acc + s.approval_rate, 0) / suppliers.suppliers.length).toFixed(1)
                  : 0}%
              </p>
            </div>
          </div>

          {/* Supplier Table */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-4">Performance par Fournisseur</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 font-medium text-gray-500">Fournisseur</th>
                    <th className="text-center py-3 font-medium text-gray-500">Livraisons</th>
                    <th className="text-center py-3 font-medium text-gray-500">Approuvés</th>
                    <th className="text-center py-3 font-medium text-gray-500">Rejetés</th>
                    <th className="text-center py-3 font-medium text-gray-500">Quarantaine</th>
                    <th className="text-center py-3 font-medium text-gray-500">Taux</th>
                    <th className="text-center py-3 font-medium text-gray-500">Statut</th>
                  </tr>
                </thead>
                <tbody>
                  {suppliers?.suppliers?.map((s, i) => (
                    <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 font-medium">{s.supplier_name || s.supplier_id}</td>
                      <td className="text-center py-3">{s.total_deliveries}</td>
                      <td className="text-center py-3 text-green-600">{s.approved}</td>
                      <td className="text-center py-3 text-red-600">{s.rejected}</td>
                      <td className="text-center py-3 text-yellow-600">{s.quarantine}</td>
                      <td className="text-center py-3">
                        <span className={`font-medium ${
                          s.approval_rate >= 98 ? 'text-green-600' :
                          s.approval_rate >= 95 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {s.approval_rate}%
                        </span>
                      </td>
                      <td className="text-center py-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          s.status === 'good' ? 'bg-green-100 text-green-700' :
                          s.status === 'warning' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-red-100 text-red-700'
                        }`}>
                          {s.status === 'good' ? 'Conforme' : s.status === 'warning' ? 'À surveiller' : 'Critique'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Supplier Distribution Pie */}
          {supplierPieData.length > 0 && (
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-4">Répartition des Livraisons</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={supplierPieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {supplierPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* Equipment Tab */}
      {activeTab === 'equipment' && (
        <div className="space-y-6">
          {equipment?.equipment?.length > 0 && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {equipment.lowest_yield && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
                    <p className="text-sm text-yellow-700 mb-1">⚠️ Rendement le plus bas</p>
                    <p className="text-2xl font-bold text-yellow-800">{equipment.lowest_yield.equipment_id}</p>
                    <p className="text-sm text-yellow-600 mt-1">
                      Rendement: {equipment.lowest_yield.avg_yield}% | {equipment.lowest_yield.batches} lots
                    </p>
                  </div>
                )}
                {equipment.highest_variability && (
                  <div className="bg-red-50 border border-red-200 rounded-xl p-6">
                    <p className="text-sm text-red-700 mb-1">⚠️ Variabilité la plus élevée</p>
                    <p className="text-2xl font-bold text-red-800">{equipment.highest_variability.equipment_id}</p>
                    <p className="text-sm text-red-600 mt-1">
                      Écart-type dureté: ±{equipment.highest_variability.hardness_variability} kp
                    </p>
                  </div>
                )}
              </div>

              <div className="bg-white rounded-xl p-6 border border-gray-200">
                <h3 className="font-semibold text-gray-900 mb-4">Performance par Équipement</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={equipment.equipment}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="equipment_id" stroke="#6b7280" />
                    <YAxis domain={[90, 100]} stroke="#6b7280" />
                    <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }} />
                    <Bar dataKey="avg_yield" name="Rendement %" fill="#22c55e" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          )}
        </div>
      )}

      {/* Comparison Tab */}
      {activeTab === 'comparison' && comparison && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Period 1 */}
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">{comparison.period1?.label}</h3>
                <span className="text-sm text-gray-500">
                  {comparison.period1?.start} → {comparison.period1?.end}
                </span>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span>Lots produits</span>
                  <span className="font-bold">{comparison.period1?.batches}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span>Rendement moyen</span>
                  <span className="font-bold text-green-600">{comparison.period1?.avg_yield}%</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span>Dureté moyenne</span>
                  <span className="font-bold">{comparison.period1?.avg_hardness} kp</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span>Plaintes</span>
                  <span className="font-bold text-orange-600">{comparison.period1?.complaints}</span>
                </div>
              </div>
            </div>

            {/* Period 2 */}
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">{comparison.period2?.label}</h3>
                <span className="text-sm text-gray-500">
                  {comparison.period2?.start} → {comparison.period2?.end}
                </span>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span>Lots produits</span>
                  <span className="font-bold">{comparison.period2?.batches}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span>Rendement moyen</span>
                  <span className="font-bold text-green-600">{comparison.period2?.avg_yield}%</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span>Dureté moyenne</span>
                  <span className="font-bold">{comparison.period2?.avg_hardness} kp</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span>Plaintes</span>
                  <span className="font-bold text-orange-600">{comparison.period2?.complaints}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Changes Summary */}
          <div className="bg-gradient-to-r from-primary-50 to-blue-50 rounded-xl p-6 border border-primary-200">
            <h3 className="font-semibold text-primary-900 mb-4">Évolution</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className={`text-2xl font-bold ${comparison.changes?.batches_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {comparison.changes?.batches_pct >= 0 ? '+' : ''}{comparison.changes?.batches_pct}%
                </p>
                <p className="text-sm text-gray-600">Production</p>
              </div>
              <div className="text-center">
                <p className={`text-2xl font-bold ${comparison.changes?.yield_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {comparison.changes?.yield_pct >= 0 ? '+' : ''}{comparison.changes?.yield_pct}%
                </p>
                <p className="text-sm text-gray-600">Rendement</p>
              </div>
              <div className="text-center">
                <p className={`text-2xl font-bold ${comparison.changes?.hardness_pct >= 0 ? 'text-blue-600' : 'text-blue-600'}`}>
                  {comparison.changes?.hardness_pct >= 0 ? '+' : ''}{comparison.changes?.hardness_pct}%
                </p>
                <p className="text-sm text-gray-600">Dureté</p>
              </div>
              <div className="text-center">
                <p className={`text-2xl font-bold ${comparison.changes?.complaints_pct <= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {comparison.changes?.complaints_pct >= 0 ? '+' : ''}{comparison.changes?.complaints_pct}%
                </p>
                <p className="text-sm text-gray-600">Plaintes</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
