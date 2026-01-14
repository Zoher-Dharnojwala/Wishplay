import React from "react";

function HomeScreen({ userName = "Mary", progress = 3, total = 10 }) {
  const percentage = Math.round((progress / total) * 100);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-100 via-pink-50 to-teal-100 font-sans">
      <div className="bg-white/80 backdrop-blur-md rounded-3xl shadow-xl p-10 max-w-md w-full text-center space-y-8 animate-fadeIn">
        
        {/* Header */}
        <header>
          <h1 className="text-4xl font-bold text-teal-800">🌿 Project Mimir</h1>
          <p className="text-gray-600 mt-2 text-lg">
            Welcome back, {userName}!  
            <br /> Ready to continue your story?
          </p>
        </header>

        {/* Start Reflection Button */}
        <button className="w-full px-6 py-4 text-xl bg-gradient-to-r from-teal-500 to-teal-600 text-white rounded-2xl shadow-md hover:shadow-lg hover:scale-105 transition transform">
          🎤 Start Reflection
        </button>

        {/* Progress Tracker */}
        <div>
          <p className="text-gray-700 mb-2">{progress} stories captured</p>
          <div className="w-full bg-gray-200 rounded-full h-4 shadow-inner">
            <div
              className="bg-teal-500 h-4 rounded-full transition-all duration-700"
              style={{ width: `${percentage}%` }}
            ></div>
          </div>
        </div>

        {/* Footer */}
        <footer className="flex justify-between text-gray-500 text-sm mt-4">
          <button className="hover:text-teal-600 transition">⚙️ Settings</button>
          <button className="hover:text-teal-600 transition">❓ Help</button>
        </footer>
      </div>
    </div>
  );
}

export default HomeScreen;

