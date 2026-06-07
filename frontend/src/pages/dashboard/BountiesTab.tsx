import { useState, useEffect } from "react";
import { Loader2, Search, Plus, X, Trash2, MessageCircle, AlertCircle, Zap, BookOpen } from "lucide-react";

interface Candidate {
  owner_name: string;
  owner_mobile: string;
  matched_via: string;
  prefilled_text: string;
}

interface Bounty {
  id: string;
  title: string;
  genres: string[];
  created_at: string;
}

interface MatchResult {
  bounty_id: string;
  matches_found: number;
  candidates: Candidate[];
}

export default function BountiesTab() {
  const [bounties, setBounties] = useState<Bounty[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  
  // Form State
  const [title, setTitle] = useState("");
  const [genreInput, setGenreInput] = useState("");
  const [genres, setGenres] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Polling / Matching State
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [pollingStatus, setPollingStatus] = useState<string>("");
  const [matchResults, setMatchResults] = useState<MatchResult | null>(null);
  const [selectedBountyId, setSelectedBountyId] = useState<string | null>(null);

  const PRESET_GENRES = ["Computer Science", "Fiction & Fantasy", "Business & Economics", "Medical", "Self-Help", "Mathematics", "Russian Lit", "Novel", "History"];

  useEffect(() => {
    fetchBounties();
  }, []);

  // Poll for Celery task completion
  useEffect(() => {
    if (!activeTaskId) return;

    setPollingStatus("STARTED");
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/bounties/task/${activeTaskId}`, {
          credentials: "include"
        });
        if (res.ok) {
          const data = await res.json();
          if (data.state === "SUCCESS") {
            setMatchResults(data.result);
            setPollingStatus("SUCCESS");
            setActiveTaskId(null);
            clearInterval(interval);
          } else if (data.state === "FAILURE") {
            setError("The search matching engine encountered a system failure.");
            setPollingStatus("FAILURE");
            setActiveTaskId(null);
            clearInterval(interval);
          } else {
            setPollingStatus(data.state); // PENDING, STARTED, etc.
          }
        }
      } catch (err) {
        console.error("Error polling task status", err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [activeTaskId]);

  const fetchBounties = async () => {
    try {
      const res = await fetch("/api/bounties/me", {
        credentials: "include"
      });
      if (res.ok) {
        const data = await res.json();
        setBounties(data);
      }
    } catch (err) {
      console.error("Failed to load bounties", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddGenre = (g: string) => {
    const clean = g.trim();
    if (clean && !genres.includes(clean)) {
      setGenres([...genres, clean]);
    }
    setGenreInput("");
  };

  const handleRemoveGenre = (idx: number) => {
    setGenres(genres.filter((_, i) => i !== idx));
  };

  const handleCreateBounty = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setMatchResults(null);

    if (!title.trim()) {
      setError("Please specify a book title.");
      return;
    }

    if (genres.length === 0) {
      setError("Please add at least one genre tag.");
      return;
    }

    try {
      setSubmitting(true);
      const res = await fetch("/api/bounties/create", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: title.trim(),
          genres: genres
        })
      });

      if (res.ok) {
        const data = await res.json();
        setSuccess("Bounty placement accepted by campus trackers!");
        setTitle("");
        setGenres([]);
        fetchBounties();
        
        // Auto-trigger matching polling
        setSelectedBountyId(data.bounty_id);
        setActiveTaskId(data.task_id);
      } else {
        const data = await res.json();
        setError(data.detail || "Failed to launch bounty hunt.");
      }
    } catch (err) {
      setError("Error communicating with backend server.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteBounty = async (bountyId: string) => {
    if (!confirm("Are you sure you want to cancel this bounty hunt?")) return;
    try {
      const res = await fetch(`/api/bounties/${bountyId}`, {
        method: "DELETE",
        credentials: "include"
      });
      if (res.ok) {
        setBounties(bounties.filter(b => b.id !== bountyId));
        if (selectedBountyId === bountyId) {
          setSelectedBountyId(null);
          setMatchResults(null);
          setActiveTaskId(null);
        }
      }
    } catch (err) {
      console.error("Failed to cancel bounty", err);
    }
  };

  const triggerSearch = async (bounty: Bounty) => {
    setError("");
    setSuccess("");
    setMatchResults(null);
    setSelectedBountyId(bounty.id);
    
    try {
      setPollingStatus("INIT");
      const res = await fetch("/api/bounties/create", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: bounty.title,
          genres: bounty.genres
        })
      });
      if (res.ok) {
        const data = await res.json();
        setActiveTaskId(data.task_id);
      } else {
        setError("Failed to run the matching engine search.");
      }
    } catch (err) {
      setError("Server connection failure.");
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300 max-w-5xl mx-auto">
      <div className="flex items-center gap-3">
        <div className="bg-primary p-2 border-2 border-slate-900 shadow-[2px_2px_0px_rgba(15,23,42,1)] rounded-sm">
          <Zap className="w-8 h-8 text-slate-900" />
        </div>
        <div>
          <h1 className="text-3xl font-black font-mono uppercase tracking-tighter text-slate-900">Bounty Board</h1>
          <p className="font-mono text-xs text-slate-500 font-bold uppercase">Launch campus-wide automated book hunts</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 border-2 border-red-500 font-mono font-bold uppercase shadow-[4px_4px_0px_rgba(239,68,68,1)] flex items-center gap-2">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="bg-green-50 text-green-700 p-4 border-2 border-green-600 font-mono font-bold uppercase shadow-[4px_4px_0px_rgba(22,163,74,1)] flex items-center gap-2">
          <BookOpen className="w-5 h-5 shrink-0" />
          <span>{success}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Side: Create Bounty Hunt */}
        <div className="lg:col-span-5 bg-white border-4 border-slate-900 shadow-brutal p-6 space-y-6">
          <h2 className="font-black text-xl border-b-4 border-slate-900 pb-2 uppercase tracking-tight">Place a Bounty</h2>
          
          <form onSubmit={handleCreateBounty} className="space-y-6">
            <div>
              <label className="block font-mono font-bold text-sm mb-2 uppercase">Book Title *</label>
              <input 
                type="text" 
                value={title} 
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Introduction to Algorithms"
                className="w-full border-2 border-slate-900 p-3 font-mono focus:outline-none focus:ring-4 focus:ring-primary focus:border-slate-900 transition-all shadow-[4px_4px_0px_rgba(15,23,42,1)]" 
              />
            </div>

            <div>
              <label className="block font-mono font-bold text-sm mb-2 uppercase">Genre Tags *</label>
              <div className="flex gap-2 mb-3">
                <input 
                  type="text" 
                  value={genreInput} 
                  onChange={(e) => setGenreInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleAddGenre(genreInput);
                    }
                  }}
                  placeholder="Type genre & press Enter"
                  className="flex-1 border-2 border-slate-900 p-3 font-mono focus:outline-none focus:ring-4 focus:ring-primary focus:border-slate-900 transition-all shadow-[4px_4px_0px_rgba(15,23,42,1)]" 
                />
                <button 
                  type="button" 
                  onClick={() => handleAddGenre(genreInput)}
                  className="bg-white border-2 border-slate-900 px-4 font-mono font-black text-lg shadow-[2px_2px_0px_rgba(15,23,42,1)] hover:bg-slate-50 transition-colors"
                >
                  <Plus className="w-5 h-5" />
                </button>
              </div>

              {/* Tag Containers */}
              {genres.length > 0 && (
                <div className="flex flex-wrap gap-2 p-3 bg-slate-50 border-2 border-slate-900 mb-4">
                  {genres.map((genre, idx) => (
                    <span key={idx} className="bg-slate-900 text-white px-2 py-1 font-mono text-xs font-bold uppercase flex items-center gap-1.5">
                      {genre}
                      <button type="button" onClick={() => handleRemoveGenre(idx)} className="hover:text-red-400">
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </span>
                  ))}
                </div>
              )}

              {/* Preset suggestions */}
              <div className="space-y-1">
                <span className="font-mono text-[10px] uppercase font-bold text-slate-400">Quick Adds:</span>
                <div className="flex flex-wrap gap-1.5">
                  {PRESET_GENRES.map((preset) => (
                    <button 
                      type="button" 
                      key={preset} 
                      disabled={genres.includes(preset)}
                      onClick={() => handleAddGenre(preset)}
                      className="border border-slate-300 hover:border-slate-900 bg-white px-2 py-0.5 font-mono text-[10px] font-bold uppercase text-slate-600 hover:text-slate-900 transition-all rounded-sm disabled:opacity-40"
                    >
                      +{preset}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <button 
              type="submit" 
              disabled={submitting}
              className="w-full bg-primary text-slate-900 border-2 border-slate-900 py-3.5 font-mono font-black text-md uppercase shadow-[4px_4px_0px_rgba(15,23,42,1)] hover:-translate-y-0.5 hover:shadow-[5px_5px_0px_rgba(15,23,42,1)] active:translate-y-0 active:shadow-none transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {submitting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
              <span>Launch Bounty Hunt</span>
            </button>
          </form>
        </div>

        {/* Right Side: Active Bounties and Realtime Polling matches */}
        <div className="lg:col-span-7 space-y-6">
          
          {/* List of active bounties */}
          <div className="bg-white border-4 border-slate-900 shadow-brutal p-6 space-y-4">
            <h2 className="font-black text-xl border-b-4 border-slate-900 pb-2 uppercase tracking-tight">My Active Bounty Hunts</h2>
            
            {loading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="w-8 h-8 animate-spin text-slate-500" />
              </div>
            ) : bounties.length === 0 ? (
              <div className="text-center py-8 font-mono text-slate-400 uppercase text-sm border-2 border-dashed border-slate-300">
                No active bounties. Place a bounty to get started.
              </div>
            ) : (
              <div className="divide-y-2 divide-slate-100 max-h-[350px] overflow-y-auto pr-1">
                {bounties.map((b) => (
                  <div key={b.id} className={`py-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 ${selectedBountyId === b.id ? 'bg-amber-50/50 px-2' : ''}`}>
                    <div className="space-y-1.5">
                      <div className="font-bold text-slate-900 text-lg uppercase tracking-tight">{b.title}</div>
                      <div className="flex flex-wrap gap-1">
                        {b.genres.map((g, idx) => (
                          <span key={idx} className="bg-slate-100 text-slate-700 px-2 py-0.5 font-mono text-[9px] font-bold uppercase border border-slate-200">
                            {g}
                          </span>
                        ))}
                      </div>
                      <div className="font-mono text-[9px] text-slate-400 uppercase">Placed: {new Date(b.created_at).toLocaleDateString()}</div>
                    </div>
                    
                    <div className="flex gap-2 w-full sm:w-auto">
                      <button 
                        onClick={() => triggerSearch(b)}
                        disabled={activeTaskId !== null}
                        className="flex-1 sm:flex-initial bg-primary text-slate-900 border-2 border-slate-900 px-4 py-2 font-mono font-black text-xs uppercase shadow-[2px_2px_0px_rgba(15,23,42,1)] hover:bg-yellow-400 active:translate-y-0.5 active:shadow-none transition-all disabled:opacity-40"
                      >
                        Search Matches
                      </button>
                      <button 
                        onClick={() => handleDeleteBounty(b.id)}
                        className="bg-red-50 text-red-600 border-2 border-red-600 p-2 hover:bg-red-100 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Matches Polling and Results Panel */}
          {selectedBountyId && (
            <div className="bg-white border-4 border-slate-900 shadow-brutal p-6 space-y-4 animate-in fade-in duration-300">
              <div className="flex justify-between items-center border-b-4 border-slate-900 pb-2">
                <h2 className="font-black text-xl uppercase tracking-tight">Bounty Hunt Results</h2>
                <button onClick={() => { setSelectedBountyId(null); setMatchResults(null); }} className="p-1 hover:bg-slate-100 rounded-sm">
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Loader during Celery polling */}
              {activeTaskId && (
                <div className="flex flex-col items-center justify-center py-10 space-y-4">
                  <div className="w-12 h-12 bg-primary border-4 border-slate-900 shadow-[4px_4px_0px_rgba(15,23,42,1)] rounded-full flex items-center justify-center animate-bounce">
                    <Zap className="w-6 h-6 text-slate-900" />
                  </div>
                  <div className="text-center space-y-1">
                    <div className="font-mono font-black uppercase text-sm">Matching Engine Running...</div>
                    <div className="font-mono text-xs text-slate-500 uppercase">Status: {pollingStatus}</div>
                  </div>
                </div>
              )}

              {/* Polling completed but no task running */}
              {!activeTaskId && matchResults && (
                <div className="space-y-4">
                  <div className="font-mono text-xs font-bold uppercase text-slate-500">
                    Matches Found: <span className="text-green-600 text-sm font-black">{matchResults.matches_found}</span>
                  </div>

                  {matchResults.matches_found === 0 ? (
                    <div className="text-center py-8 font-mono text-slate-400 uppercase text-xs border-2 border-dashed border-slate-200">
                      No candidate peers currently found on campus for this title/genre combination. We will keep tracking!
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[300px] overflow-y-auto pr-1">
                      {matchResults.candidates.map((c, idx) => (
                        <div key={idx} className="bg-white border-2 border-slate-900 p-4 shadow-[3px_3px_0px_rgba(15,23,42,1)] flex flex-col justify-between space-y-3">
                          <div>
                            <div className="font-bold text-slate-900 uppercase text-md tracking-tight">{c.owner_name}</div>
                            <span className={`inline-block font-mono text-[9px] font-black uppercase px-2 py-0.5 border border-slate-900 ${c.matched_via === "Exact Title Match" ? "bg-green-100 text-green-800" : "bg-blue-100 text-blue-800"}`}>
                              {c.matched_via}
                            </span>
                          </div>

                          {c.owner_mobile === "Unlinked Contact" ? (
                            <div className="bg-amber-50 text-amber-800 p-2 border border-amber-300 font-mono text-[9px] font-bold uppercase">
                              WhatsApp contact unlinked by user.
                            </div>
                          ) : (
                            <a 
                              href={`https://wa.me/${c.owner_mobile.replace(/[^0-9]/g, "")}?text=${encodeURIComponent(c.prefilled_text)}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="w-full bg-slate-900 hover:bg-slate-800 text-white font-mono font-bold text-xs uppercase py-2 px-3 flex items-center justify-center gap-2 rounded-sm shadow-[2px_2px_0px_rgba(251,191,36,1)] transition-transform active:translate-y-0.5 active:shadow-none"
                            >
                              <MessageCircle className="w-4 h-4 text-green-400 fill-green-400" />
                              <span>Ping on WhatsApp</span>
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

        </div>

      </div>

    </div>
  );
}
