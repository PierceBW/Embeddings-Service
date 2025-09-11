// @ts-nocheck
import Layout from './components/features/Layout';

export default function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-blue-600 text-white p-4 shadow">
        <div className="max-w-6xl flex items-center gap-10">
          <img src="/workday_logo.png" alt="Logo" className="h-8 w-auto" />
          <h1 className="text-2xl font-bold">Risk Analysis Dashboard</h1>
        </div>
      </header>
      <main className="p-0">
        <Layout />
      </main>
    </div>
  );
} 