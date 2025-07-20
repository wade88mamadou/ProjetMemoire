import React from 'react';
import logo from '../conformed.png';

const roleColors = {
  Admin: 'text-blue-700',
  Médecin: 'text-green-700',
  Utilisateur: 'text-purple-700',
  default: 'text-gray-700',
};

const LogoHeader = ({ role = '' }) => {
  const colorClass = roleColors[role] || roleColors.default;
  return (
    <div className="flex items-center gap-3">
      <div className="relative group">
        <img 
          src={logo} 
          alt="Logo Conformed" 
          className="h-10 w-10 rounded-full shadow-lg transition-all duration-300 ease-in-out transform hover:scale-110 hover:rotate-3 hover:shadow-xl animate-pulse" 
        />
        <div className="absolute inset-0 rounded-full bg-blue-500 opacity-0 group-hover:opacity-20 transition-opacity duration-300 animate-ping"></div>
      </div>
      {role && (
        <span className={`font-bold text-xl ${colorClass} transition-all duration-300 hover:text-blue-600 transform hover:scale-105`}>
          {role}
        </span>
      )}
    </div>
  );
};

export default LogoHeader; 