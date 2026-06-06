import { useState, useEffect } from "react";
import { Loader2, MapPin, Phone, Save, Navigation, CheckCircle2, LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function ProfileTab() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    area: "",
    pincode: "",
    mobile_number: "",
    latitude: null as number | null,
    longitude: null as number | null
  });

  // Dynamically calculate completion percentage
  let completeCount = 0;
  if (formData.name) completeCount++;
  if (formData.email) completeCount++;
  if (formData.area) completeCount++;
  if (formData.pincode) completeCount++;
  if (formData.mobile_number) completeCount++;
  // GPS represents an implicit 6th chunk if we want, or we just rely on the 5 textual ones 
  // to match the Dashboard Layout logic exactly. Let's match the layout (5 fields).
  const completionPercentage = (completeCount / 5) * 100;

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await fetch("/api/auth/me", {
        credentials: "include"
      });
      if (response.ok) {
        const data = await response.json();
        setFormData(prev => ({
          ...prev,
          name: data.name || "",
          email: data.email || "",
          area: data.area || "",
          pincode: data.pincode || "",
          mobile_number: data.mobile_number || ""
        }));
      }
    } catch (err) {
      console.error("Failed to load profile", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCaptureLocation = () => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser.");
      return;
    }
    
    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setFormData(prev => ({
          ...prev,
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        }));
        setLoading(false);
        setError("");
      },
      (err) => {
        setLoading(false);
        setError("Failed to access GPS. Please ensure location permissions are enabled.");
      },
      { enableHighAccuracy: true }
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!formData.area || !formData.pincode || !formData.mobile_number) {
      setError("Please fill in all required fields.");
      return;
    }

    if (formData.latitude === null || formData.longitude === null) {
      setError("Please capture your GPS location to enable proximity search.");
      return;
    }

    try {
      setSubmitting(true);
      const response = await fetch("/api/auth/onboarding", {
        method: "PATCH",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          area: formData.area,
          pincode: formData.pincode,
          mobile_number: formData.mobile_number,
          latitude: formData.latitude,
          longitude: formData.longitude
        }),
      });

      if (response.ok) {
        setSuccess("Profile attributes fully synchronized and GPS locked!");
        // We do NOT reset the form data, we want it to stay populated
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Failed to synchronize profile. Please try again.");
      }
    } catch (err) {
      setError("An unexpected error occurred while communicating with the server.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
      sessionStorage.removeItem('onboarding_seen');
      navigate("/login");
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  if (loading && !formData.name) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-900">
        <Loader2 className="w-10 h-10 animate-spin mb-4" />
        <p className="font-mono font-bold uppercase tracking-widest">Loading Profile...</p>
      </div>
    );
  }

  const isProfileComplete = formData.area && formData.pincode && formData.mobile_number;

  return (
    <div className="space-y-6 animate-in fade-in duration-300 max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-3xl font-black font-mono uppercase tracking-tighter">My Profile</h1>
      </div>

      <div className="mb-8 border-4 border-slate-900 p-4 bg-white shadow-brutal">
        <div className="flex justify-between items-end mb-2 font-mono font-black uppercase">
          <span className="text-slate-600 tracking-tight">Profile Completion</span>
          <span className={`text-xl ${completionPercentage === 100 ? 'text-green-600' : 'text-slate-900'}`}>
            {completionPercentage}%
          </span>
        </div>
        <div className="w-full bg-slate-200 border-2 border-slate-900 h-6 relative overflow-hidden">
          <div 
            className={`h-full border-r-2 border-slate-900 transition-all duration-700 ease-out ${
              completionPercentage === 100 ? 'bg-green-400' : 'bg-yellow-400'
            }`}
            style={{ width: `${completionPercentage}%` }}
          />
        </div>
      </div>

      {!isProfileComplete && !success && (
        <div className="bg-red-50 border-4 border-red-600 p-6 shadow-[6px_6px_0px_rgba(220,38,38,1)] mb-8">
          <h2 className="font-black text-xl mb-2 flex items-center text-red-700">
            <Navigation className="w-6 h-6 mr-2 text-red-600" />
            Location Missing
          </h2>
          <p className="font-mono text-red-900 font-bold">
            You must complete your campus location and GPS setup before you can list books on the marketplace.
          </p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 text-red-600 p-4 border-2 border-red-500 font-mono font-bold uppercase shadow-[4px_4px_0px_rgba(239,68,68,1)]">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-50 text-green-700 p-6 border-4 border-green-600 font-mono font-bold uppercase shadow-[6px_6px_0px_rgba(22,163,74,1)] flex items-center">
          <CheckCircle2 className="w-8 h-8 mr-4" />
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white border-4 border-slate-900 shadow-brutal p-8 space-y-8">
        
        {/* Core Info (Read Only) */}
        <div className="space-y-4">
          <h3 className="font-black text-lg border-b-4 border-slate-900 pb-2 uppercase tracking-tight">Account Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block font-mono font-bold text-sm mb-2 uppercase">Display Name</label>
              <input type="text" disabled value={formData.name} className="w-full border-2 border-slate-200 bg-slate-50 p-3 font-mono text-slate-500 cursor-not-allowed" />
            </div>
            <div>
              <label className="block font-mono font-bold text-sm mb-2 uppercase">Verified Email</label>
              <input type="text" disabled value={formData.email} className="w-full border-2 border-slate-200 bg-slate-50 p-3 font-mono text-slate-500 cursor-not-allowed" />
            </div>
          </div>
        </div>

        {/* Location Info */}
        <div className="space-y-4">
          <h3 className="font-black text-lg border-b-4 border-slate-900 pb-2 uppercase tracking-tight flex items-center">
            <MapPin className="w-5 h-5 mr-2" /> Demographics & Campus
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block font-mono font-bold text-sm mb-2 uppercase">Campus / Area Name *</label>
              <input 
                type="text" 
                value={formData.area} 
                onChange={(e) => setFormData({...formData, area: e.target.value})}
                placeholder="e.g. Adani University"
                className="w-full border-2 border-slate-900 p-3 font-mono focus:outline-none focus:ring-4 focus:ring-primary focus:border-slate-900 transition-all shadow-[4px_4px_0px_rgba(15,23,42,1)]" 
              />
            </div>
            <div>
              <label className="block font-mono font-bold text-sm mb-2 uppercase">Pincode *</label>
              <input 
                type="text" 
                value={formData.pincode} 
                onChange={(e) => setFormData({...formData, pincode: e.target.value})}
                placeholder="e.g. 380060"
                className="w-full border-2 border-slate-900 p-3 font-mono focus:outline-none focus:ring-4 focus:ring-primary focus:border-slate-900 transition-all shadow-[4px_4px_0px_rgba(15,23,42,1)]" 
              />
            </div>
            <div className="md:col-span-2">
              <label className="block font-mono font-bold text-sm mb-2 uppercase">WhatsApp / Mobile *</label>
              <div className="flex items-center">
                <span className="bg-slate-900 text-white px-4 py-3 font-mono border-2 border-slate-900 border-r-0"><Phone className="w-5 h-5" /></span>
                <input 
                  type="text" 
                  value={formData.mobile_number} 
                  onChange={(e) => setFormData({...formData, mobile_number: e.target.value})}
                  placeholder="+91 9999999999"
                  className="flex-1 border-2 border-slate-900 p-3 font-mono focus:outline-none focus:ring-4 focus:ring-primary focus:border-slate-900 transition-all shadow-[4px_4px_0px_rgba(15,23,42,1)]" 
                />
              </div>
            </div>
          </div>
        </div>

        {/* GPS Capture Layer */}
        <div className="bg-slate-50 border-2 border-dashed border-slate-300 p-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div>
              <h4 className="font-black uppercase mb-1 flex items-center">
                <Navigation className="w-4 h-4 mr-2" /> GPS Radar Fix
              </h4>
              <p className="font-mono text-sm text-slate-500">
                Required to show your books to students within your radius.
              </p>
              {formData.latitude && (
                <p className="font-mono text-xs font-bold text-green-600 mt-2 bg-green-100 px-2 py-1 inline-block border border-green-600">
                  COORDINATES LOCKED: {formData.latitude.toFixed(4)}, {formData.longitude?.toFixed(4)}
                </p>
              )}
            </div>
            <button 
              type="button" 
              onClick={handleCaptureLocation}
              disabled={loading}
              className="shrink-0 bg-white border-2 border-slate-900 px-6 py-3 font-mono font-bold uppercase shadow-[4px_4px_0px_rgba(15,23,42,1)] hover:-translate-y-1 hover:shadow-[6px_6px_0px_rgba(15,23,42,1)] active:translate-y-0 active:shadow-none transition-all disabled:opacity-50 flex items-center"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <MapPin className="w-5 h-5 mr-2" />}
              {formData.latitude ? "Recapture GPS" : "Grant GPS Access"}
            </button>
          </div>
        </div>

        {/* Submit Layer */}
        <div className="pt-6 border-t-4 border-slate-900 flex justify-between items-center">
          <button 
            type="button" 
            onClick={handleLogout}
            className="bg-slate-100 text-red-600 border-2 border-slate-900 px-6 py-4 font-mono font-black text-lg uppercase shadow-[4px_4px_0px_rgba(15,23,42,1)] hover:-translate-y-1 hover:shadow-[6px_6px_0px_rgba(15,23,42,1)] hover:bg-red-50 active:translate-y-0 active:shadow-none transition-all flex items-center"
          >
            <LogOut className="w-5 h-5 mr-2" />
            Log Out
          </button>
          
          <button 
            type="submit" 
            disabled={submitting}
            className="bg-primary text-slate-900 border-2 border-slate-900 px-8 py-4 font-mono font-black text-lg uppercase shadow-[6px_6px_0px_rgba(15,23,42,1)] hover:-translate-y-1 hover:shadow-[8px_8px_0px_rgba(15,23,42,1)] active:translate-y-0 active:shadow-none transition-all disabled:opacity-50 flex items-center"
          >
            {submitting ? <Loader2 className="w-6 h-6 animate-spin mr-2" /> : <Save className="w-6 h-6 mr-2" />}
            Synchronize Profile
          </button>
        </div>

      </form>
    </div>
  );
}
