import React from 'react';
import { Shield, Settings, Clock, Wifi, UploadCloud } from 'lucide-react';

const Navbar = ({}) => {
  return (
    <header className="glass backdrop-blur-lg p-6 rounded-3xl border border-white/10 shadow-xl flex justify-between items-center mb-8 sticky top-4 z-50">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center animate-pulse shadow-glow-primary">
          <Shield className="w-6 h-6 text-black" />
        </div>
        <h1 className="text-3xl font-bold glitch text-[#00ff41]">GEMINIRECON</h1>
      </div>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-gray-400" />
          <span className="text-xs">{new Date().toUTCString().split(' ')[4]} UTC</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
          <span className="text-xs text-green-400 font-bold">SYSTEM NOMINAL</span>
        </div>
        <Settings className="w-5 h-5 text-gray-400 hover:text-primary transition-colors cursor-pointer" />
      </div>
    </header>
  );
};

export default Navbar;
