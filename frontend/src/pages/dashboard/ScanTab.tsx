import { useState, useRef , useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Camera, Upload, AlertTriangle, Loader2 } from "lucide-react";

export default function ScanTab() {
  const [searchParams] = useSearchParams();
  const source = searchParams.get("source") || "gallery";
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // State
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);
  const [isProfileComplete, setIsProfileComplete] = useState(true);
  const [checkingProfile, setCheckingProfile] = useState(true);
  
  // Form Data from AI and User
  const [formData, setFormData] = useState({
    title: "",
    author: "",
    description: "",
    genres: "",
    price: "",
    owner_note: "",
  });

  useEffect(() => {
    const checkProfile = async () => {
      try {
        const profileRes = await fetch("/api/auth/me", { credentials: "include" });
        if (profileRes.ok) {
          const profileData = await profileRes.json();
          if (!profileData.area || !profileData.pincode) {
            setIsProfileComplete(false);
          }
        }
      } catch(e) {}
      setCheckingProfile(false);
    }
    checkProfile();
  }, []);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
      await scanWithAI(file);
    }
  };

  const scanWithAI = async (file: File) => {
    setIsScanning(true);
    setScanError(null);
    try {
      const data = new FormData();
      data.append("image", file);

      const response = await fetch("/api/books/scan", {
        method: "POST",
        body: data,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to scan image");
      }

      const result = await response.json();
      if (result.status === "success" && result.suggested_data) {
        const ai = result.suggested_data;
        setFormData((prev) => ({
          ...prev,
          title: ai.title || "",
          author: ai.author || "",
          description: ai.description || "",
          genres: Array.isArray(ai.genres) ? ai.genres.join(", ") : (ai.genres || ""),
        }));
      }
    } catch (error) {
      setScanError(error.message || "Something went wrong during AI analysis.");
    } finally {
      setIsScanning(false);
    }
  };

  const handlePublish = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!imageFile || !formData.title || !formData.author || !formData.price) return;

    setIsUploading(true);
    try {
      const payload = new FormData();
      payload.append("title", formData.title);
      payload.append("author", formData.author);
      payload.append("description", formData.description);
      payload.append("genres", formData.genres);
      payload.append("price", formData.price);
      payload.append("owner_note", formData.owner_note);
      payload.append("image", imageFile);

      const response = await fetch("/api/books/upload", {
        method: "POST",
        body: payload,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`[${response.status}] ${errorText}`);
      }

      // Success, redirect to inventory or home
      navigate("/dashboard/my-books");
    } catch (error) {
      alert("Error: " + error.message);
    } finally {
      setIsUploading(false);
    }
  };

  if (checkingProfile) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-900">
        <Loader2 className="w-10 h-10 animate-spin mb-4" />
        <p className="font-mono font-bold uppercase tracking-widest">Verifying access...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-black font-mono uppercase tracking-tighter">
          {imagePreview ? "Review & Publish" : "Scan New Book"}
        </h1>
        <button 
          onClick={() => navigate(-1)}
          className="font-mono font-bold text-sm border-2 border-slate-900 px-3 py-1 rounded-sm shadow-[2px_2px_0px_rgba(15,23,42,1)] hover:bg-slate-100 active:translate-y-[2px] active:translate-x-[2px] active:shadow-none transition-all"
        >
          Cancel
        </button>
      </div>

      {!isProfileComplete ? (
        <div className="text-center py-20 border-4 border-slate-900 border-dashed bg-red-50 shadow-brutal rounded-sm flex flex-col items-center justify-center">
          <AlertTriangle className="w-16 h-16 text-red-600 mb-4" />
          <h2 className="font-mono font-black text-2xl uppercase text-slate-900 mb-2">Profile Incomplete</h2>
          <p className="font-mono font-bold text-slate-600 mb-6 max-w-sm">You must complete your campus location setup before you can scan or upload books.</p>
          <button 
            onClick={() => navigate("/dashboard/profile")}
            className="bg-slate-900 text-white px-6 py-3 font-mono font-bold uppercase tracking-widest shadow-[4px_4px_0px_#facc15] hover:-translate-y-1 hover:shadow-[6px_6px_0px_#facc15] transition-all"
          >
            Complete Setup
          </button>
        </div>
      ) : !imagePreview ? (
        <div className="p-8 border-4 border-slate-900 shadow-brutal bg-white rounded-sm text-center">
          <input 
            type="file" 
            accept="image/*"
            capture={source === "camera" ? "environment" : undefined}
            className="hidden"
            ref={fileInputRef}
            onChange={handleFileChange}
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-slate-900 bg-slate-50 hover:bg-slate-100 transition-colors group cursor-pointer"
          >
            <div className="bg-primary p-4 border-2 border-slate-900 rounded-sm mb-4 group-hover:scale-110 transition-transform">
              {source === "camera" ? <Camera className="w-8 h-8" /> : <Upload className="w-8 h-8" />}
            </div>
            <span className="font-mono font-bold text-xl uppercase">
              {source === "camera" ? "Tap to Take Photo" : "Select from Gallery"}
            </span>
            <span className="text-sm font-mono text-slate-500 mt-2">JPG, PNG, WEBP</span>
          </button>
        </div>
      ) : (
        <form onSubmit={handlePublish} className="space-y-6">
          <div className="flex flex-col md:flex-row gap-6">
            {/* Image Preview Area */}
            <div className="w-full md:w-1/3 space-y-4">
              <div className="border-4 border-slate-900 shadow-brutal bg-white p-2">
                <img src={imagePreview} alt="Book cover" className="w-full h-auto object-cover border-2 border-slate-900" />
              </div>
              <button
                type="button"
                onClick={() => {
                  setImageFile(null);
                  setImagePreview(null);
                  setFormData({ title: "", author: "", description: "", genres: "", price: "", owner_note: "" });
                }}
                className="w-full font-mono font-bold text-sm border-2 border-slate-900 px-3 py-2 rounded-sm hover:bg-slate-100"
              >
                Retake Photo
              </button>
            </div>

            {/* Form Area */}
            <div className="w-full md:w-2/3 space-y-4">
              {isScanning ? (
                <div className="p-6 border-4 border-slate-900 shadow-brutal bg-slate-900 text-green-400 font-mono flex flex-col items-center justify-center h-full min-h-[300px]">
                  <Loader2 className="w-12 h-12 animate-spin mb-4" />
                  <p className="uppercase font-bold tracking-widest animate-pulse text-center">
                    [AI] Analyzing cover...<br/>
                    Extracting metadata...
                  </p>
                </div>
              ) : (
                <div className="p-6 border-4 border-slate-900 shadow-brutal bg-white space-y-4">
                  {scanError && (
                    <div className="bg-red-100 border-2 border-red-900 text-red-900 p-3 text-sm font-mono flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5 shrink-0" />
                      {scanError}
                    </div>
                  )}

                  <div className="space-y-1">
                    <label className="font-mono font-bold uppercase text-sm">Book Title</label>
                    <input 
                      required
                      type="text" 
                      value={formData.title}
                      onChange={(e) => setFormData({...formData, title: e.target.value})}
                      className="w-full border-2 border-slate-900 p-2 font-mono focus:outline-none focus:bg-yellow-50" 
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="font-mono font-bold uppercase text-sm">Author</label>
                    <input 
                      required
                      type="text" 
                      value={formData.author}
                      onChange={(e) => setFormData({...formData, author: e.target.value})}
                      className="w-full border-2 border-slate-900 p-2 font-mono focus:outline-none focus:bg-yellow-50" 
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <label className="font-mono font-bold uppercase text-sm">Price (₹)</label>
                      <input 
                        required
                        type="number" 
                        min="0"
                        step="1"
                        placeholder="e.g. 150"
                        value={formData.price}
                        onChange={(e) => setFormData({...formData, price: e.target.value})}
                        className="w-full border-2 border-slate-900 p-2 font-mono font-bold text-lg focus:outline-none focus:bg-yellow-50 bg-green-50 text-green-900" 
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="font-mono font-bold uppercase text-sm">Genres</label>
                      <input 
                        type="text" 
                        placeholder="Comma separated"
                        value={formData.genres}
                        onChange={(e) => setFormData({...formData, genres: e.target.value})}
                        className="w-full border-2 border-slate-900 p-2 font-mono text-sm focus:outline-none focus:bg-yellow-50" 
                      />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label className="font-mono font-bold uppercase text-sm">Description</label>
                    <textarea 
                      rows={3}
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      className="w-full border-2 border-slate-900 p-2 font-mono text-sm focus:outline-none focus:bg-yellow-50 resize-none" 
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="font-mono font-bold uppercase text-sm">Owner Notes (Optional)</label>
                    <input 
                      type="text" 
                      placeholder="e.g. Will barter for Engineering Math vol 2"
                      value={formData.owner_note}
                      onChange={(e) => setFormData({...formData, owner_note: e.target.value})}
                      className="w-full border-2 border-slate-900 p-2 font-mono text-sm focus:outline-none focus:bg-yellow-50" 
                    />
                  </div>

                  <button 
                    type="submit"
                    disabled={isUploading}
                    className="w-full mt-4 bg-primary px-6 py-4 border-2 border-slate-900 shadow-brutal active-brutal rounded-sm font-mono font-black text-xl uppercase tracking-widest text-slate-900 flex items-center justify-center gap-2"
                  >
                    {isUploading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Upload className="w-6 h-6" />}
                    {isUploading ? "Uploading..." : "Publish Book"}
                  </button>
                </div>
              )}
            </div>
          </div>
        </form>
      )}
    </div>
  );
}
