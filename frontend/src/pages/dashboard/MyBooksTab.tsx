import { useState, useEffect } from "react";
import { Loader2, Book, Calendar, IndianRupee } from "lucide-react";
import { Link } from "react-router-dom";

const BookImage = ({ src, alt, className }: { src: string | null, alt: string, className?: string }) => {
  const [error, setError] = useState(false);
  if (!src || error) {
    return (
      <div className={`flex flex-col items-center justify-center bg-slate-100 text-slate-400 p-4 ${className || "w-full h-full"}`}>
        <span className="font-mono text-xs text-center line-clamp-3">{alt}</span>
      </div>
    );
  }
  return <img src={src} alt={alt} className={className} onError={() => setError(true)} />;
};

export default function MyBooksTab() {
  const [books, setBooks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isProfileComplete, setIsProfileComplete] = useState(true); // Default to true so it doesn't flash

  const fetchProfileAndBooks = async () => {
    try {
      setLoading(true);
      
      // First check if profile is complete
      const profileRes = await fetch("/api/auth/me", { credentials: "include" });
      if (profileRes.ok) {
        const profileData = await profileRes.json();
        if (!profileData.area || !profileData.pincode) {
          setIsProfileComplete(false);
          setLoading(false);
          return; // Stop here, don't load books
        }
      }

      // If complete, fetch books
      const response = await fetch("/api/books/my-books", { credentials: "include" });
      if (response.ok) {
        const data = await response.json();
        setBooks(data);
      } else {
        setError("Failed to fetch inventory.");
      }
    } catch (err) {
      setError("An error occurred while connecting to the server.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfileAndBooks();
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h1 className="text-3xl font-black font-mono uppercase tracking-tighter text-slate-900">My Inventory</h1>
        {isProfileComplete && (
          <Link 
            to="/dashboard/scan?source=camera"
            className="bg-primary px-4 py-2 border-2 border-slate-900 font-mono font-bold uppercase shadow-brutal active-brutal hover:bg-yellow-400 transition-colors"
          >
            + Add Book
          </Link>
        )}
      </div>

      {!isProfileComplete && (
        <div className="bg-red-50 text-red-700 p-8 border-4 border-red-600 shadow-[6px_6px_0px_rgba(220,38,38,1)] flex flex-col items-center justify-center text-center mt-8">
          <h2 className="font-black text-2xl mb-4 uppercase tracking-tight">Action Required</h2>
          <p className="font-mono font-bold mb-6 max-w-md">
            You must complete your campus location and setup your profile before you can upload and sell books.
          </p>
          <Link 
            to="/dashboard/profile"
            className="bg-red-600 text-white px-8 py-3 border-2 border-slate-900 font-mono font-black uppercase tracking-widest shadow-[4px_4px_0px_rgba(15,23,42,1)] hover:-translate-y-1 hover:shadow-[6px_6px_0px_rgba(15,23,42,1)] transition-all"
          >
            Complete Profile
          </Link>
        </div>
      )}

      {error && isProfileComplete && (
        <div className="bg-red-50 text-red-600 p-4 border-2 border-red-500 font-mono font-bold uppercase shadow-[4px_4px_0px_rgba(239,68,68,1)]">
          {error}
        </div>
      )}

      {isProfileComplete && (
        loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-slate-900">
          <Loader2 className="w-10 h-10 animate-spin mb-4" />
          <p className="font-mono font-bold uppercase tracking-widest">Loading inventory...</p>
        </div>
      ) : books.length === 0 ? (
        <div className="text-center py-20 border-4 border-slate-900 border-dashed bg-white shadow-brutal rounded-sm flex flex-col items-center justify-center">
          <Book className="w-16 h-16 text-slate-300 mb-4" />
          <p className="font-mono font-bold text-xl uppercase text-slate-500 mb-6">Your inventory is empty.</p>
          <Link 
            to="/dashboard/scan?source=camera"
            className="bg-slate-900 text-white px-6 py-3 font-mono font-bold uppercase tracking-widest shadow-[4px_4px_0px_#facc15] hover:-translate-y-1 hover:shadow-[6px_6px_0px_#facc15] transition-all"
          >
            Start Selling Now
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
          {books.map((book) => (
            <Link key={book.id} to={`/dashboard/books/${book.id}`} className="group flex flex-col border-4 border-slate-900 bg-white shadow-brutal hover:-translate-y-1 hover:shadow-[8px_8px_0px_rgba(15,23,42,1)] transition-all rounded-sm overflow-hidden">
              {/* Image Header */}
              <div className="relative h-40 sm:h-56 border-b-4 border-slate-900 bg-slate-50 flex items-center justify-center overflow-hidden p-2 sm:p-4">
                <BookImage src={book.image_url} alt={book.title} className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500 drop-shadow-md" />
                <div className="absolute top-2 left-2 bg-primary border-2 border-slate-900 px-2 py-1 font-mono font-black text-[10px] sm:text-sm flex items-center shadow-[2px_2px_0px_rgba(15,23,42,1)]">
                  <IndianRupee className="w-3 h-3 sm:w-4 sm:h-4 mr-1" />
                  {book.price === 0 ? "FREE" : book.price}
                </div>
              </div>
              
              {/* Card Body */}
              <div className="p-4 flex-1 flex flex-col bg-white">
                <h3 className="font-black text-xl leading-tight mb-1 uppercase line-clamp-1">{book.title}</h3>
                <p className="text-slate-600 font-mono font-bold text-sm mb-3 uppercase line-clamp-1 border-b-2 border-dashed border-slate-200 pb-3">{book.author}</p>
                
                <div className="flex flex-wrap gap-2 mb-4">
                  {(book.genres || []).map((g: string, i: number) => (
                    <span key={i} className="text-[10px] font-mono font-bold bg-slate-100 border-2 border-slate-900 px-2 py-0.5 uppercase">
                      {g}
                    </span>
                  ))}
                </div>

                <div className="mt-auto pt-4 border-t-2 border-slate-900 flex justify-between items-center text-xs font-mono font-bold text-slate-500 uppercase">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" /> 
                    {book.created_at ? new Date(book.created_at).toLocaleDateString() : 'Unknown'}
                  </span>
                  <span className="bg-green-100 text-green-700 px-2 py-1 border-2 border-green-700">Listed</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )
      )}
    </div>
  );
}
