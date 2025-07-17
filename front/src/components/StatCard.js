import React from 'react';

function StatCard({ title, value, color }) {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 text-center border-t-4 ${color}`}>
      <div className="text-lg font-bold text-gray-700 dark:text-gray-200">{title}</div>
      <div className="text-3xl font-extrabold mt-2">{value}</div>
    </div>
  );
}

export default StatCard; 