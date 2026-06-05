import { useState } from "react";
import { Outlet, Link, useLocation, useNavigate } from "react-router-dom";
import { Home, BookOpen, Camera, Heart, User, Search, Plus, Upload, X } from "lucide-react";

export default function DashboardLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const [showSellModal, setShowSellModal] = useState(false);

  const navItems = [
    { name: "Home", path: "/dashboard", icon: <Home className="w-6 h-6" /> },
    { name: "My Books", path: "/dashboard/my-books", icon: <BookOpen className="w-6 h-6" /> },
    { name: "Wishlist", path: "/dashboard/wishlist", icon: <Heart className="w-6 h-6" /> },
    { name: "Profile", path: "/dashboard/profile", icon: <User className="w-6 h-6" /> },
  ];

  const SellModal = () => (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white w-full max-w-sm border-4 border-slate-900 shadow-brutal rounded-sm p-6 relative">
        <button 
          onClick={() => setShowSellModal(false)}
          className="absolute top-4 right-4 p-1 hover:bg-slate-100 rounded-sm transition-colors border-2 border-transparent hover:border-slate-900"
        >
          <X className="w-6 h-6" />
        </button>
        
        <h2 className="text-2xl font-black font-mono uppercase tracking-tight mb-2">Scan Book</h2>
        <p className="text-slate-500 text-sm mb-6 font-mono font-bold">Use AI to auto-fill details.</p>

        <div className="space-y-4">
          <button 
            className="w-full flex items-center gap-4 p-4 border-2 border-slate-900 rounded-sm shadow-brutal active-brutal bg-primary hover:bg-yellow-400 transition-colors group"
            onClick={() => {
              setShowSellModal(false);
              navigate("/dashboard/scan?source=camera");
            }}
          >
            <div className="bg-white p-3 border-2 border-slate-900 rounded-sm">
              <Camera className="w-6 h-6 text-slate-900" />
            </div>
            <div className="text-left">
              <div className="font-bold font-mono text-lg uppercase">Take Photo</div>
              <div className="text-xs text-slate-800 font-bold opacity-80">Use device camera</div>
            </div>
          </button>

          <button 
            className="w-full flex items-center gap-4 p-4 border-2 border-slate-900 rounded-sm shadow-brutal active-brutal bg-white hover:bg-slate-50 transition-colors group"
            onClick={() => {
              setShowSellModal(false);
              navigate("/dashboard/scan?source=gallery");
            }}
          >
            <div className="bg-slate-100 p-3 border-2 border-slate-900 rounded-sm group-hover:bg-white transition-colors">
              <Upload className="w-6 h-6 text-slate-900" />
            </div>
            <div className="text-left">
              <div className="font-bold font-mono text-lg uppercase text-slate-900">Gallery</div>
              <div className="text-xs text-slate-500 font-bold opacity-80">Choose existing photo</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* PC / Tablet Top Navbar */}
      <header className="hidden md:flex items-center justify-between px-8 py-4 bg-white border-b-4 border-slate-900 sticky top-0 z-40 shadow-sm">
        <Link to="/dashboard" className="flex items-center gap-3 group">
          <div className="bg-primary p-2 border-2 border-slate-900 shadow-[2px_2px_0px_rgba(15,23,42,1)] group-hover:translate-y-[2px] group-hover:translate-x-[2px] group-hover:shadow-none transition-all rounded-sm">
            <BookOpen className="w-6 h-6 text-slate-900" />
          </div>
          <span className="text-2xl font-black font-mono tracking-tighter uppercase text-slate-900">LocalShelf</span>
        </Link>

        <nav className="flex items-center gap-6">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link 
                key={item.path} 
                to={item.path}
                className={`font-mono font-bold uppercase tracking-wide flex items-center gap-2 px-3 py-2 border-2 rounded-sm transition-all ${
                  isActive 
                  ? "bg-slate-900 text-white border-slate-900 shadow-brutal" 
                  : "bg-transparent text-slate-600 border-transparent hover:border-slate-300 hover:text-slate-900"
                }`}
              >
                {item.icon}
                <span className="hidden lg:inline">{item.name}</span>
              </Link>
            );
          })}
          
          <div className="w-px h-8 bg-slate-300 mx-2"></div>
          
          <button 
            onClick={() => setShowSellModal(true)}
            className="flex items-center gap-2 bg-primary px-5 py-2.5 border-2 border-slate-900 shadow-brutal active-brutal rounded-sm font-mono font-black uppercase text-slate-900 hover:bg-yellow-400 transition-colors"
          >
            <Camera className="w-5 h-5" />
            <span>Scan Book</span>
          </button>
        </nav>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-5xl mx-auto px-4 sm:px-6 md:px-8 py-6 pb-28 md:pb-8">
        <Outlet />
      </main>

      {/* Mobile Bottom Navigation Bar */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t-2 border-slate-900 px-2 pb-safe pt-2 z-40 shadow-[0_-4px_20px_rgba(0,0,0,0.05)]">
        <div className="flex items-center justify-between relative max-w-md mx-auto">
          
          {/* Left items */}
          <div className="flex justify-evenly w-[40%]">
            {[navItems[0], navItems[1]].map((item) => (
              <Link 
                key={item.path}
                to={item.path} 
                className={`flex flex-col items-center p-2 rounded-sm transition-colors ${location.pathname === item.path ? 'text-slate-900' : 'text-slate-400 hover:text-slate-600'}`}
              >
                <div className={`${location.pathname === item.path ? 'scale-110 mb-1 transition-transform' : 'mb-1'}`}>
                  {item.icon}
                </div>
                <span className="text-[10px] font-mono font-bold uppercase">{item.name}</span>
              </Link>
            ))}
          </div>

          {/* Center Elevated Button */}
          <div className="absolute left-1/2 -translate-x-1/2 -top-8">
            <button 
              onClick={() => setShowSellModal(true)}
              className="bg-primary p-4 rounded-full border-4 border-slate-900 shadow-brutal active-brutal hover:bg-yellow-400 transition-all text-slate-900 flex items-center justify-center"
            >
              <Camera className="w-7 h-7" />
            </button>
            <div className="text-[10px] font-mono font-bold uppercase text-slate-900 text-center mt-2">Sell Now</div>
          </div>

          {/* Right items */}
          <div className="flex justify-evenly w-[40%]">
            {[navItems[2], navItems[3]].map((item) => (
              <Link 
                key={item.path}
                to={item.path} 
                className={`flex flex-col items-center p-2 rounded-sm transition-colors ${location.pathname === item.path ? 'text-slate-900' : 'text-slate-400 hover:text-slate-600'}`}
              >
                <div className={`${location.pathname === item.path ? 'scale-110 mb-1 transition-transform' : 'mb-1'}`}>
                  {item.icon}
                </div>
                <span className="text-[10px] font-mono font-bold uppercase">{item.name}</span>
              </Link>
            ))}
          </div>

        </div>
      </nav>

      {/* Sell Menu Modal */}
      {showSellModal && <SellModal />}
    </div>
  );
}
