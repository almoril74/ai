import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Patientenakte</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              {user?.username} ({user?.role})
            </span>
            <button
              onClick={logout}
              className="text-sm text-red-600 hover:text-red-800"
            >
              Abmelden
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link
            to="/patients"
            className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition"
          >
            <h2 className="text-xl font-semibold text-gray-900">Patienten</h2>
            <p className="mt-2 text-gray-600">
              Patientenverwaltung und -suche
            </p>
          </Link>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold text-gray-900">Behandlungen</h2>
            <p className="mt-2 text-gray-600">
              Behandlungsdokumentation
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold text-gray-900">Einstellungen</h2>
            <p className="mt-2 text-gray-600">
              System-Konfiguration
            </p>
          </div>
        </div>

        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900">DSGVO-Hinweis</h3>
          <p className="mt-2 text-sm text-blue-800">
            Alle Zugriffe werden protokolliert. Patientendaten sind verschlüsselt gespeichert.
          </p>
        </div>
      </main>
    </div>
  )
}
