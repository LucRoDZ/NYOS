import { useState, useEffect } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Clock, Download } from 'lucide-react';
import { api } from '../api';

const dataTypes = [
  { id: 'batch', label: 'Lots de production', description: 'manufacturing_extended_*.csv' },
  { id: 'qc', label: 'Résultats QC', description: 'qc_lab_extended_*.csv' },
  { id: 'complaint', label: 'Plaintes clients', description: 'customer_complaints_*.csv' },
  { id: 'capa', label: 'CAPAs', description: 'capa_records_*.csv' },
  { id: 'equipment', label: 'Équipements', description: 'equipment_calibration_*.csv' },
  { id: 'environmental', label: 'Environnement', description: 'environmental_monitoring_*.csv' },
  { id: 'stability', label: 'Stabilité', description: 'stability_data_*.csv' },
  { id: 'raw_material', label: 'Matières premières', description: 'raw_materials_*.csv' },
  { id: 'batch_release', label: 'Libération lots', description: 'batch_release_*.csv' },
];

export default function DataUpload() {
  const [selectedType, setSelectedType] = useState('batch');
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploads, setUploads] = useState([]);

  useEffect(() => {
    loadUploads();
  }, []);

  async function loadUploads() {
    try {
      const data = await api.getUploads();
      setUploads(data);
    } catch (e) {
      console.error(e);
    }
  }

  async function handleFile(file) {
    if (!file.name.endsWith('.csv')) {
      setUploadResult({ error: 'Seuls les fichiers CSV sont acceptés' });
      return;
    }

    setUploading(true);
    setUploadResult(null);

    try {
      const result = await api.uploadFile(file, selectedType);
      setUploadResult({ success: true, ...result });
      loadUploads();
    } catch (e) {
      setUploadResult({ error: 'Erreur lors de l\'upload' });
    } finally {
      setUploading(false);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }

  function handleChange(e) {
    if (e.target.files?.[0]) {
      handleFile(e.target.files[0]);
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Import de Données</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Type de données</h3>
            <div className="grid grid-cols-2 gap-3">
              {dataTypes.map(type => (
                <button
                  key={type.id}
                  onClick={() => setSelectedType(type.id)}
                  className={`p-4 rounded-lg border-2 text-left transition-colors ${
                    selectedType === type.id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <p className="font-medium text-gray-900">{type.label}</p>
                  <p className="text-xs text-gray-500">{type.description}</p>
                </button>
              ))}
            </div>
          </div>

          <div
            onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
            className={`bg-white rounded-xl border-2 border-dashed p-8 text-center transition-colors ${
              dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300'
            }`}
          >
            <Upload className={`mx-auto mb-4 ${dragActive ? 'text-primary-500' : 'text-gray-400'}`} size={48} />
            <p className="text-gray-600 mb-2">
              Glissez votre fichier CSV ici ou
            </p>
            <label className="inline-block">
              <span className="px-4 py-2 bg-primary-600 text-white rounded-lg cursor-pointer hover:bg-primary-700">
                Parcourir
              </span>
              <input
                type="file"
                accept=".csv"
                onChange={handleChange}
                className="hidden"
                disabled={uploading}
              />
            </label>
            <p className="text-xs text-gray-400 mt-4">Format: CSV uniquement</p>
          </div>

          {uploading && (
            <div className="bg-primary-50 border border-primary-200 rounded-xl p-4 flex items-center gap-3">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
              <p className="text-primary-700">Import en cours...</p>
            </div>
          )}

          {uploadResult?.success && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-center gap-3">
              <CheckCircle className="text-green-500" size={24} />
              <div>
                <p className="font-semibold text-green-800">Import réussi</p>
                <p className="text-green-600 text-sm">
                  {uploadResult.records_imported} enregistrements importés depuis {uploadResult.filename}
                </p>
              </div>
            </div>
          )}

          {uploadResult?.error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
              <AlertCircle className="text-red-500" size={24} />
              <p className="text-red-700">{uploadResult.error}</p>
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Clock size={18} />
            Historique des imports
          </h3>
          {uploads.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Aucun fichier importé</p>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {uploads.map((upload, i) => (
                <div key={i} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <FileText className="text-gray-400" size={20} />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">{upload.filename}</p>
                    <p className="text-xs text-gray-500">
                      {upload.records_count} enregistrements • {upload.data_type}
                    </p>
                  </div>
                  <span className="text-xs text-gray-400">
                    {new Date(upload.uploaded_at).toLocaleDateString('fr-FR')}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
