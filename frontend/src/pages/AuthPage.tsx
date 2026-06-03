import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Book, Lock, ChevronRight, User, Mail, MapPin, Hash } from "lucide-react";

type AuthMode = "login" | "signup";
type Step = 1 | 2;

export default function AuthPage() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Default to signup if they came from /signup, else login
  const [mode, setMode] = useState<AuthMode>(location.pathname === "/signup" ? "signup" : "login");
  const [step, setStep] = useState<Step>(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    area: "",
    pincode: ""
  });
  const [otp, setOtp] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    
    // For login, we only need email strictly, but backend might require dummy data
    // if using the exact same schema. Let's send dummy for login if they are empty.
    const payload = mode === "signup" ? formData : {
      email: formData.email,
      name: "LoginUser",
      area: "Auto",
      pincode: "000000"
    };

    try {
      const res = await fetch("/api/auth/send-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (res.ok) {
        setStep(2);
        console.log("Dev Bypass Token:", data.dev_bypass_token);
      } else {
        setError(data.detail || "Failed to send OTP");
      }
    } catch (err) {
      console.log(err);
      setError("An error occurred connecting to the server.");
    }
    setLoading(false);
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/auth/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: formData.email, otp }),
      });
      const data = await res.json();
      if (res.ok) {
        navigate("/dashboard");
      } else {
        setError(data.detail || "Invalid OTP");
      }
    } catch (err) {
      console.log(err);
      setError("An error occurred during verification.");
    }
    setLoading(false);
  };

  const switchMode = (newMode: AuthMode) => {
    setMode(newMode);
    setStep(1);
    setError("");
    // Update URL silently
    window.history.pushState(null, "", `/${newMode}`);
  };

  // UI Components
  const Screw = () => (
    <div className="w-2 h-2 rounded-full bg-slate-200 shadow-inner border border-slate-300 absolute" />
  );

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4" 
         style={{ backgroundImage: 'radial-gradient(#cbd5e1 1px, transparent 1px)', backgroundSize: '20px 20px' }}>
      
      <div className="relative w-full max-w-md bg-white border-2 border-slate-900 shadow-brutal-dark p-8 rounded-sm">
        {/* Decorative Screws */}
        <div className="top-2 left-2 absolute"><Screw /></div>
        <div className="top-2 right-2 absolute"><Screw /></div>
        <div className="bottom-2 left-2 absolute"><Screw /></div>
        <div className="bottom-2 right-2 absolute"><Screw /></div>

        {/* Header */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-10 h-8 bg-primary border-2 border-secondary flex items-center justify-center rounded-sm mb-3">
            <Book className="text-secondary w-5 h-5" />
          </div>
          <h1 className="text-2xl font-black uppercase tracking-tight text-secondary">LocalShelf</h1>
          <p className="font-mono text-xs text-slate-500 mt-1 uppercase tracking-widest font-bold">
            {mode === "login" ? "Welcome Back" : "Create an Account"}
          </p>
        </div>

        {/* Mode Switcher */}
        {step === 1 && (
          <div className="flex w-full mb-8 border-2 border-slate-200 p-1 rounded-sm bg-slate-50">
            <button 
              onClick={() => switchMode("login")}
              className={`flex-1 py-2 font-mono text-xs uppercase font-bold transition-colors ${
                mode === "login" 
                  ? "bg-white border-2 border-secondary text-secondary shadow-[2px_2px_0_0_#0f172a]" 
                  : "text-slate-400 hover:text-slate-600"
              }`}
            >
              Login
            </button>
            <button 
              onClick={() => switchMode("signup")}
              className={`flex-1 py-2 font-mono text-xs uppercase font-bold transition-colors ${
                mode === "signup" 
                  ? "bg-white border-2 border-secondary text-secondary shadow-[2px_2px_0_0_#0f172a]" 
                  : "text-slate-400 hover:text-slate-600"
              }`}
            >
              Sign Up
            </button>
          </div>
        )}

        {error && (
          <div className="mb-6 p-3 bg-red-50 border-2 border-red-500 text-red-600 font-mono text-xs uppercase font-bold flex items-center gap-2">
            <span className="bg-red-500 text-white w-4 h-4 flex items-center justify-center rounded-full">!</span>
            {error}
          </div>
        )}

        <div className="space-y-6">
          {step === 1 ? (
            <form onSubmit={handleSendOtp} className="space-y-5">
              
              {mode === "signup" && (
                <div className="space-y-2">
                  <label htmlFor="name" className="font-mono text-xs font-bold text-slate-600 uppercase tracking-wider block">
                    Full Name
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                    <input 
                      id="name" 
                      value={formData.name} 
                      onChange={handleChange} 
                      required 
                      placeholder="John Doe"
                      className="w-full pl-9 pr-4 py-2 bg-slate-100 border-2 border-transparent focus:border-secondary focus:bg-white focus:outline-none font-mono text-sm transition-all rounded-sm"
                    />
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <label htmlFor="email" className="font-mono text-xs font-bold text-slate-600 uppercase tracking-wider block">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                  <input 
                    id="email" 
                    type="email"
                    value={formData.email} 
                    onChange={handleChange} 
                    required 
                    placeholder="user@example.com"
                    className="w-full pl-9 pr-4 py-2 bg-slate-100 border-2 border-transparent focus:border-secondary focus:bg-white focus:outline-none font-mono text-sm transition-all rounded-sm"
                  />
                </div>
              </div>

              {mode === "signup" && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label htmlFor="area" className="font-mono text-xs font-bold text-slate-600 uppercase tracking-wider block">
                      Area (City)
                    </label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                      <input 
                        id="area" 
                        value={formData.area} 
                        onChange={handleChange} 
                        required 
                        placeholder="Bharuch"
                        className="w-full pl-9 pr-3 py-2 bg-slate-100 border-2 border-transparent focus:border-secondary focus:bg-white focus:outline-none font-mono text-sm transition-all rounded-sm"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label htmlFor="pincode" className="font-mono text-xs font-bold text-slate-600 uppercase tracking-wider block">
                      Pincode
                    </label>
                    <div className="relative">
                      <Hash className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                      <input 
                        id="pincode" 
                        value={formData.pincode} 
                        onChange={handleChange} 
                        required 
                        placeholder="392001"
                        className="w-full pl-9 pr-3 py-2 bg-slate-100 border-2 border-transparent focus:border-secondary focus:bg-white focus:outline-none font-mono text-sm transition-all rounded-sm"
                      />
                    </div>
                  </div>
                </div>
              )}

              <button 
                type="submit" 
                disabled={loading}
                className="w-full mt-4 bg-secondary text-white font-mono font-bold uppercase tracking-widest py-3 border-2 border-secondary hover:bg-slate-800 transition-all flex items-center justify-center gap-2 rounded-sm shadow-brutal active-brutal"
              >
                {loading ? "Processing..." : (mode === "login" ? "Login" : "Create Account")}
                <ChevronRight className="w-5 h-5" />
              </button>
            </form>
          ) : (
            <form onSubmit={handleVerifyOtp} className="space-y-5 animate-in fade-in zoom-in duration-300">
              <div className="space-y-2">
                <label htmlFor="otp" className="font-mono text-xs font-bold text-slate-600 uppercase tracking-wider block text-center">
                  Enter One-Time Password
                </label>
                <div className="relative max-w-[200px] mx-auto">
                  <Lock className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                  <input 
                    id="otp" 
                    type="text"
                    value={otp} 
                    onChange={(e) => setOtp(e.target.value)} 
                    required 
                    maxLength={6}
                    placeholder="------"
                    className="w-full pl-10 pr-4 py-3 bg-slate-100 border-2 border-transparent focus:border-secondary focus:bg-white focus:outline-none font-mono text-center text-xl tracking-[0.5em] transition-all rounded-sm font-bold"
                  />
                </div>
                <p className="text-center font-mono text-xs text-slate-400 mt-2">Sent to {formData.email}</p>
              </div>

              <button 
                type="submit" 
                disabled={loading}
                className="w-full mt-6 bg-primary text-secondary font-mono font-bold uppercase tracking-widest py-3 border-2 border-secondary hover:bg-yellow-400 transition-all flex items-center justify-center gap-2 rounded-sm shadow-[4px_4px_0_0_#0f172a] active:translate-y-[2px] active:translate-x-[2px] active:shadow-inner"
              >
                {loading ? "Verifying..." : "Verify"}
                <Lock className="w-5 h-5" />
              </button>
              
              <button 
                type="button"
                onClick={() => setStep(1)}
                className="w-full text-center font-mono text-xs text-slate-500 hover:text-slate-800 uppercase font-bold mt-4"
              >
                ← Back
              </button>
            </form>
          )}
        </div>
      </div>
      
      <Link to="/" className="absolute top-6 left-6 font-mono text-xs uppercase font-bold text-slate-500 hover:text-secondary flex items-center gap-2">
        <ChevronRight className="w-4 h-4 rotate-180" /> Back to Home
      </Link>
    </div>
  );
}
