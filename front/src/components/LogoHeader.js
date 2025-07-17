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
      <img src={logo} alt="Logo Conformed" className="h-10 w-10 rounded-full shadow" />
      {role && <span className={`font-bold text-xl ${colorClass}`}> {role}</span>}
    </div>
  );
};

export default LogoHeader; 