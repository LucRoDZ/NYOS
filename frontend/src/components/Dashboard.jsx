import { useState, useEffect } from 'react';
import { Package, AlertTriangle, CheckCircle, Clock, FileWarning, Wrench, TrendingUp, FileText, Download } from 'lucide-react';
import { api } from '../api';

function parseMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/### (.*?)(\n|$)/g, '<h4 class="font-semibold text-lg mt-4 mb-2">$1</h4>')
    .replace(/## (.*?)(\n|$)/g, '<h3 class="font-bold text-xl mt-4 mb-2">$1</h3>')
    .replace(/# (.*?)(\n|$)/g, '<h2 class="font-bold text-2xl mt-4 mb-3">$1</h2>')
    .replace(/- (.*?)(\n|$)/g, '<li class="ml-4">$1</li>')
    .replace(/\n/g, '<br/>');
}

function StatCard({ icon: Icon, label, value, color = 'blue', subtext }) {
  const colors = {
    blue: 'bg-primary-100 text-primary-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
  };
  return (
    <div className="bg-white rounded-xl p-6 border border-gray-200">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500 mb-1">{label}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {subtext && <p className="text-xs text-gray-400 mt-1">{subtext}</p>}
        </div>
        <div className={`p-3 rounded-lg ${colors[color]}`}>
          <Icon size={24} />
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [summary, setSummary] = useState('');
  const [report, setReport] = useState('');
  const [loading, setLoading] = useState(true);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);
  const [showReport, setShowReport] = useState(false);

  useEffect(() => { loadData(); }, []);

  async function loadData() {
    try {
      const data = await api.getDashboard();
      setStats(data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }

  function generateSummary() {
    setSummaryLoading(true);
    setSummary('');
    api.streamSummary(
      (text) => setSummary(prev => prev + text),
      () => setSummaryLoading(false),
      (error) => { setSummary("Erreur: " + error); setSummaryLoading(false); }
    );
  }

  async function generateReport() {
    setReportLoading(true);
    try {
      const data = await api.getReport();
      setReport(data.report);
      setShowReport(true);
    } catch (e) { setReport("Erreur lors de la génération."); }
    finally { setReportLoading(false); }
  }

  function downloadReport() {
    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rapport_apr_nyos.md';
    a.click();
    URL.revokeObjectURL(url);
  }

  function printReport() {
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`<html><head><title>Rapport APR NYOS</title><style>body{font-family:Arial,sans-serif;padding:40px;max-width:800px;margin:0 auto}h1,h2,h3,h4{color:#1e40af}ul{margin-left:20px}</style></head><body>${parseMarkdown(report)}</body></html>`);
    printWindow.document.close();
    printWindow.print();
  }

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h2 className="text-2xl font-bold text-gray-900">Vue d'ensemble</h2>
        <div className="flex gap-2">
          <button onClick={generateSummary} disabled={summaryLoading} className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50">
            {summaryLoading ? <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div> : <TrendingUp size={18} />}
            Résumé IA
          </button>
          <button onClick={generateReport} disabled={reportLoading} className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50">
            {reportLoading ? <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div> : <FileText size={18} />}
            Rapport Complet
          </button>
        </div>
      </div>

      {summary && (
        <div className="bg-primary-50 border border-primary-200 rounded-xl p-6">
          <h3 className="font-semibold text-primary-900 mb-3 flex items-center gap-2"><TrendingUp size={20} /> Résumé Exécutif IA</h3>
          <div className="text-gray-700 prose max-w-none" dangerouslySetInnerHTML={{ __html: parseMarkdown(summary) }} />
        </div>
      )}

      {showReport && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
            <div className="p-4 border-b flex items-center justify-between">
              <h3 className="font-bold text-lg">Rapport APR Complet</h3>
              <div className="flex gap-2">
                <button onClick={downloadReport} className="flex items-center gap-1 px-3 py-1 bg-gray-100 rounded hover:bg-gray-200"><Download size={16} /> .md</button>
                <button onClick={printReport} className="flex items-center gap-1 px-3 py-1 bg-primary-600 text-white rounded hover:bg-primary-700"><FileText size={16} /> PDF</button>
                <button onClick={() => setShowReport(false)} className="px-3 py-1 text-gray-500 hover:bg-gray-100 rounded">✕</button>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-6 prose max-w-none" dangerouslySetInnerHTML={{ __html: parseMarkdown(report) }} />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard icon={Package} label="Total Lots" value={stats?.total_batches || 0} color="blue" subtext={`${stats?.batches_this_month || 0} ce mois`} />
        <StatCard icon={CheckCircle} label="Rendement Moyen" value={`${stats?.avg_yield || 0}%`} color="green" />
        <StatCard icon={AlertTriangle} label="Plaintes Ouvertes" value={stats?.complaints_open || 0} color={stats?.complaints_open > 5 ? 'red' : 'yellow'} />
        <StatCard icon={FileWarning} label="CAPAs Ouvertes" value={stats?.capas_open || 0}
          color={stats?.capas_open > 3 ? 'red' : 'yellow'}
        />
        <StatCard
          icon={Wrench}
          label="Équipements à calibrer"
          value={stats?.equipment_due || 0}
          color={stats?.equipment_due > 0 ? 'yellow' : 'green'}
          subtext="Dans les 7 prochains jours"
        />
        <StatCard
          icon={Clock}
          label="Période d'analyse"
          value="6 ans"
          color="blue"
          subtext="2020 - 2025"
        />
      </div>

      {stats?.total_batches === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center">
          <AlertTriangle className="mx-auto text-yellow-500 mb-3" size={48} />
          <h3 className="font-semibold text-yellow-800 mb-2">Aucune donnée</h3>
          <p className="text-yellow-600">
            Importez des données via l'onglet "Import Data" pour commencer l'analyse.
          </p>
        </div>
      )}
    </div>
  );
}
