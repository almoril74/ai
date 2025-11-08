import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { patientsApi } from '../services/api'

export default function PatientsPage() {
  const { data: patients, isLoading, error } = useQuery({
    queryKey: ['patients'],
    queryFn: () => patientsApi.list(),
  })

  if (isLoading) return <div className="p-8">Lädt...</div>
  if (error) return <div className="p-8 text-red-600">Fehler beim Laden</div>

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Patienten</h1>
          <Link
            to="/dashboard"
            className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
          >
            Zurück
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Geburtsdatum
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Aktionen
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {patients?.map((patient: any) => (
                <tr key={patient.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    {patient.nachname}, {patient.vorname}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                    {patient.geburtsdatum}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                      {patient.is_active ? 'Aktiv' : 'Inaktiv'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link
                      to={`/patients/${patient.id}`}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      Details
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
