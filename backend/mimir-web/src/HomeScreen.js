import React from "react";

function HomeScreen({ userName = "Mary", progress = 3, total = 10 }) {
  const percentage = Math.round((progress / total) * 100);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-green-50 to-purple-50 font-sans">
      <header className="w-full p-6 text-center">
        <h1 className="text-3xl font-bold text-green-900">🌿 Project Mimir</h1>
        <p className="text-lg text-gray-700 mt-2">
          Welcome back, {userName}! <br />
          Ready to continue your story?
        </p>
      </header>

      <main className="flex flex-col items-center mt-10 space-y-6">
        <button className="px-8 py-4 text-xl bg-green-600 text-white rounded-2xl shadow-lg hover:bg-green-700 transition">
          🎤 Start Reflection
        </button>

        <div className="w-64 text-center">
          <p className="text-gray-700 mb-2">
            {progress} stories captured
          </p>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div
              className="bg-green-600 h-4 rounded-full"
              style={{ width: `${percentage}%` }}
            ></div>
          </div>
        </div>
      </main>

      <footer className="absolute bottom-6 flex w-full justify-between px-8">
        <button className="text-gray-700">⚙️ Settings</button>
        <button className="text-gray-700">❓ Help</button>
      </footer>
    </div>
  );
}

export default HomeScreen;
