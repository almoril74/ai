import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { patientsApi } from '../services/api'

export default function PatientDetailPage() {
  const { id } = useParams<{ id: string }>()

  const { data: patient, isLoading, error } = useQuery({
    queryKey: ['patient', id],
    queryFn: () => patientsApi.get(Number(id)),
  })

  if (isLoading) return <div className="p-8">Lädt...</div>
  if (error) return <div className="p-8 text-red-600">Fehler beim Laden</div>
  if (!patient) return <div className="p-8">Patient nicht gefunden</div>

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">
            {patient.nachname}, {patient.vorname}
          </h1>
          <Link
            to="/patients"
            className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
          >
            Zurück
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <section>
            <h2 className="text-xl font-semibold mb-4">Persönliche Daten</h2>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Geburtsdatum</dt>
                <dd className="mt-1 text-sm text-gray-900">{patient.geburtsdatum}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">E-Mail</dt>
                <dd className="mt-1 text-sm text-gray-900">{patient.email || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Telefon</dt>
                <dd className="mt-1 text-sm text-gray-900">{patient.telefon || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Adresse</dt>
                <dd className="mt-1 text-sm text-gray-900">{patient.adresse || '-'}</dd>
              </div>
            </dl>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-4">Medizinische Daten</h2>
            <dl className="space-y-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Anamnese</dt>
                <dd className="mt-1 text-sm text-gray-900">{patient.anamnese || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Allergien</dt>
                <dd className="mt-1 text-sm text-gray-900">{patient.allergien || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Medikation</dt>
                <dd className="mt-1 text-sm text-gray-900">{patient.medikation || '-'}</dd>
              </div>
            </dl>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-4">DSGVO-Status</h2>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Einwilligung</dt>
                <dd className="mt-1">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    patient.consent_given
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {patient.consent_given ? 'Erteilt' : 'Ausstehend'}
                  </span>
                </dd>
              </div>
              {patient.consent_date && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Einwilligungsdatum</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(patient.consent_date).toLocaleDateString('de-DE')}
                  </dd>
                </div>
              )}
            </dl>
          </section>
        </div>
      </div>
    </div>
  )
}
