import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Loader2, ArrowLeft, MapPin, IndianRupee, MessageCircle, Calendar, Book } from "lucide-react";

type BookDetails = {
  id: string;
  title: string;
  author: string;
  description: string;
  genres: string[];
  price: number;
  owner_note: string | null;
  image_url: string | null;
  created_at: string;
  owner_id: string;
  owner_name: string;
  campus_name: string;
};

export default function BookDetailsTab() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [book, setBook] = useState<BookDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const [contacting, setContacting] = useState(false);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        setLoading(true);
        // Fetch current user so we know if they own this book
        const userRes = await fetch("/api/auth/me", { credentials: "include" });
        if (userRes.ok) {
          const userData = await userRes.json();
          setCurrentUserId(userData.user_id);
        }

        const res = await fetch(`/api/books/${id}`, { credentials: "include" });
        if (res.ok) {
          const data = await res.json();
          setBook(data);
        } else {
          setError("Failed to load book details. It may have been deleted.");
        }
      } catch (err) {
        setError("Error connecting to server.");
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchDetails();
  }, [id]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-32 text-slate-900">
        <Loader2 className="w-12 h-12 animate-spin mb-4" />
        <p className="font-mono font-bold uppercase tracking-widest">Loading Details...</p>
      </div>
    );
  }

  if (error || !book) {
    return (
      <div className="text-center py-20">
        <div className="bg-red-50 border-4 border-red-600 shadow-brutal p-8 inline-block">
          <h2 className="text-2xl font-black font-mono uppercase text-red-600 mb-2">Error</h2>
          <p className="font-mono font-bold text-slate-700 mb-6">{error}</p>
          <button 
            onClick={() => navigate(-1)}
            className="bg-slate-900 text-white px-6 py-3 font-mono font-bold uppercase shadow-[4px_4px_0px_rgba(220,38,38,1)] hover:-translate-y-1 transition-all"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const handleContactSeller = async () => {
    try {
      setContacting(true);
      const res = await fetch(`/api/books/${id}/click-interest`, {
        method: "POST",
        credentials: "include"
      });
      
      if (res.ok) {
        const data = await res.json();
        // Construct the WhatsApp URL as per user's format request
        const phone = data.target_mobile.replace(/\D/g,''); // strip non-numeric
        // ensure country code is present (assuming India 91 if not present and length is 10)
        const formattedPhone = phone.length === 10 ? `91${phone}` : phone;
        const text = encodeURIComponent(data.prefilled_text);
        
        const whatsappUrl = `https://api.whatsapp.com/send/?phone=${formattedPhone}&text=${text}&type=phone_number&app_absent=0`;
        window.open(whatsappUrl, "_blank");
      } else {
        const errData = await res.json();
        alert(errData.detail || "Failed to generate contact link.");
      }
    } catch (err) {
      alert("Network error while trying to contact seller.");
    } finally {
      setContacting(false);
    }
  };

  const isOwner = currentUserId === book.owner_id;

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12 animate-in fade-in duration-300">
      <button 
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 font-mono font-bold uppercase text-sm border-2 border-slate-900 px-4 py-2 rounded-sm shadow-[2px_2px_0px_rgba(15,23,42,1)] hover:bg-slate-100 hover:-translate-y-0.5 transition-all"
      >
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Left: Image Box */}
        <div className="border-4 border-slate-900 shadow-[8px_8px_0px_rgba(15,23,42,1)] bg-slate-50 p-4 h-80 md:h-[500px] flex items-center justify-center overflow-hidden relative">
          {book.image_url ? (
            <img src={book.image_url} alt={book.title} className="w-full h-full object-contain drop-shadow-lg" />
          ) : (
            <div className="text-center font-mono text-slate-400">
              <Book className="w-16 h-16 mx-auto mb-2 opacity-50" />
              <p>No Image Available</p>
            </div>
          )}
          <div className="absolute top-4 left-4 bg-primary border-4 border-slate-900 px-4 py-2 font-mono font-black text-2xl flex items-center shadow-[4px_4px_0px_rgba(15,23,42,1)]">
            <IndianRupee className="w-6 h-6 mr-1" />
            {book.price === 0 ? "FREE" : book.price}
          </div>
        </div>

        {/* Right: Details */}
        <div className="space-y-6">
          <div>
            <h1 className="text-4xl md:text-5xl font-black font-mono uppercase tracking-tighter leading-none mb-2">{book.title}</h1>
            <p className="text-xl font-mono font-bold text-slate-500 uppercase border-b-4 border-slate-900 pb-4 inline-block">By {book.author}</p>
          </div>

          <div className="flex flex-wrap gap-2">
            {(book.genres || []).map((g: string, i: number) => (
              <span key={i} className="bg-slate-100 border-2 border-slate-900 px-3 py-1 text-xs font-mono font-bold uppercase shadow-[2px_2px_0px_rgba(15,23,42,1)]">
                {g}
              </span>
            ))}
          </div>

          <div className="bg-white border-4 border-slate-900 p-6 shadow-[4px_4px_0px_rgba(15,23,42,1)]">
            <h3 className="font-black uppercase text-sm mb-2 opacity-50 tracking-widest">Description</h3>
            <p className="text-slate-800 leading-relaxed font-medium whitespace-pre-wrap">
              {book.description || "No description provided by the seller."}
            </p>
          </div>

          {book.owner_note && (
            <div className="bg-yellow-50 border-4 border-yellow-500 p-6 shadow-[4px_4px_0px_rgba(234,179,8,1)] text-yellow-900">
              <h3 className="font-black uppercase text-sm mb-2 opacity-50 tracking-widest">Seller's Note</h3>
              <p className="font-mono font-bold text-sm">
                "{book.owner_note}"
              </p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4 border-t-4 border-slate-900 pt-6">
            <div>
              <p className="text-xs font-mono font-bold text-slate-500 uppercase mb-1">Listed By</p>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center font-bold font-mono">
                  {book.owner_name.charAt(0).toUpperCase()}
                </div>
                <p className="font-bold truncate">{book.owner_name}</p>
              </div>
            </div>
            <div>
              <p className="text-xs font-mono font-bold text-slate-500 uppercase mb-1">Location</p>
              <p className="font-bold flex items-center gap-1">
                <MapPin className="w-4 h-4 text-red-500" />
                {book.campus_name || "Unknown"}
              </p>
            </div>
            <div>
              <p className="text-xs font-mono font-bold text-slate-500 uppercase mb-1">Listed On</p>
              <p className="font-bold flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                {new Date(book.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>

          <div className="pt-8">
            {!isOwner ? (
              <button 
                onClick={handleContactSeller}
                disabled={contacting}
                className="w-full bg-green-400 text-slate-900 px-6 py-4 border-4 border-slate-900 font-mono font-black text-xl uppercase tracking-widest shadow-[6px_6px_0px_rgba(15,23,42,1)] hover:-translate-y-1 hover:shadow-[8px_8px_0px_rgba(15,23,42,1)] active:translate-y-0 active:shadow-none transition-all flex items-center justify-center gap-3 disabled:opacity-70"
              >
                {contacting ? <Loader2 className="w-6 h-6 animate-spin" /> : <MessageCircle className="w-6 h-6" />}
                {contacting ? "Connecting..." : "Contact Seller"}
              </button>
            ) : (
              <div className="w-full bg-slate-100 text-slate-500 px-6 py-4 border-4 border-slate-300 font-mono font-black text-xl uppercase tracking-widest flex items-center justify-center text-center border-dashed">
                This is your listing
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
