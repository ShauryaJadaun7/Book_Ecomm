import { useState, useEffect } from "react";
import { Search, MapPin, Loader2, IndianRupee } from "lucide-react";

type Book = {
  book_id: string;
  title: string;
  author: string;
  description: string;
  genres: string[];
  price: number;
  owner_note: string | null;
  image_url: string | null;
  owner_name: string;
  campus_name: string;
  distance_display: string;
};

export default function HomeTab() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [radius, setRadius] = useState<string>("any");

  const fetchBooks = async () => {
    setLoading(true);
    try {
      const url = new URL(window.location.origin + "/api/books/book");
      url.searchParams.append("page", "1");
      url.searchParams.append("limit", "20");
      if (search) url.searchParams.append("search", search);
      if (radius !== "any") url.searchParams.append("max_radius_km", radius);

      const res = await fetch(url.pathname + url.search);
      if (res.ok) {
        const data = await res.json();
        setBooks(data.books || []);
      }
    } catch (err) {
      console.error("Failed to fetch books", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch, debounce could be added here for search
    const timer = setTimeout(() => {
      fetchBooks();
    }, 300);
    return () => clearTimeout(timer);
  }, [search, radius]);

  return (
    <div className="space-y-6">
      {/* Sticky Search & Filter Bar */}
      <div className="sticky top-0 z-30 bg-slate-50/90 backdrop-blur-md pt-2 pb-4 -mx-4 px-4 sm:mx-0 sm:px-0">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search title, author, genre..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border-2 border-slate-900 shadow-[2px_2px_0px_rgba(15,23,42,1)] rounded-sm font-mono focus:outline-none focus:bg-yellow-50 transition-colors"
            />
          </div>
          <div className="relative w-full sm:w-48">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <select 
              value={radius}
              onChange={(e) => setRadius(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border-2 border-slate-900 shadow-[2px_2px_0px_rgba(15,23,42,1)] rounded-sm font-mono font-bold appearance-none bg-white focus:outline-none focus:bg-yellow-50 cursor-pointer"
            >
              <option value="any">Anywhere</option>
              <option value="5">Within 5 km</option>
              <option value="10">Within 10 km</option>
              <option value="25">Within 25 km</option>
            </select>
          </div>
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-slate-900">
          <Loader2 className="w-10 h-10 animate-spin mb-4" />
          <p className="font-mono font-bold uppercase tracking-widest">Scanning local radars...</p>
        </div>
      ) : books.length === 0 ? (
        <div className="text-center py-20 border-4 border-slate-900 border-dashed bg-white shadow-brutal rounded-sm">
          <p className="font-mono font-bold text-xl uppercase text-slate-500">No books found in this radius.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {books.map((book) => (
            <div key={book.book_id} className="group flex flex-col border-4 border-slate-900 bg-white shadow-brutal hover:-translate-y-1 hover:shadow-[8px_8px_0px_rgba(15,23,42,1)] transition-all rounded-sm overflow-hidden">
              {/* Image Header */}
              <div className="relative h-56 border-b-4 border-slate-900 bg-white flex items-center justify-center overflow-hidden p-4">
                {book.image_url ? (
                  <img src={book.image_url} alt={book.title} className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500 drop-shadow-md" />
                ) : (
                  <span className="font-mono text-slate-300">No Image</span>
                )}
                <div className="absolute top-2 left-2 bg-primary border-2 border-slate-900 px-2 py-1 font-mono font-black text-sm flex items-center shadow-[2px_2px_0px_rgba(15,23,42,1)]">
                  <IndianRupee className="w-4 h-4 mr-1" />
                  {book.price === 0 ? "FREE" : book.price}
                </div>
                <div className="absolute bottom-2 right-2 bg-white border-2 border-slate-900 px-2 py-1 font-mono font-bold text-xs shadow-[2px_2px_0px_rgba(15,23,42,1)] flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-red-500" />
                  {book.distance_display}
                </div>
              </div>
              
              {/* Content Body */}
              <div className="p-4 flex flex-col flex-1">
                <h3 className="font-black font-mono text-lg uppercase leading-tight line-clamp-1 mb-1" title={book.title}>
                  {book.title}
                </h3>
                <p className="text-slate-600 font-mono text-xs mb-3 truncate">By {book.author}</p>
                
                <p className="text-slate-700 text-sm mb-4 line-clamp-2 flex-1">
                  {book.description || "No description provided."}
                </p>

                <div className="flex flex-wrap gap-1 mb-4">
                  {book.genres && book.genres.slice(0, 3).map((g, i) => (
                    <span key={i} className="bg-slate-100 border border-slate-900 px-2 py-0.5 text-[10px] font-mono font-bold uppercase rounded-sm">
                      {g}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between pt-3 border-t-2 border-slate-100">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full bg-slate-900 text-white flex items-center justify-center font-bold text-xs uppercase">
                      {book.owner_name.charAt(0)}
                    </div>
                    <span className="font-mono font-bold text-xs truncate max-w-[100px]">{book.owner_name}</span>
                  </div>
                  <button className="bg-white border-2 border-slate-900 shadow-[2px_2px_0px_rgba(15,23,42,1)] hover:bg-slate-900 hover:text-white px-3 py-1 font-mono font-bold text-xs uppercase transition-colors rounded-sm">
                    Contact
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
