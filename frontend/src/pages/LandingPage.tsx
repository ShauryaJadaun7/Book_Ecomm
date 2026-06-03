import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { 
  Book, Camera, Map, MessageSquare, ChevronRight, Search, Clock, Zap, 
  ArrowRightLeft, IndianRupee, ShieldCheck, Leaf, Trophy, Star, Download,
  Mail, MessageCircle, ChevronDown
} from "lucide-react";

// --- QUOTES ARRAY (15 Quotes) ---
const QUOTES = [
  { text: "A reader lives a thousand lives before he dies.", author: "George R.R. Martin" },
  { text: "There is no friend as loyal as a book.", author: "Ernest Hemingway" },
  { text: "A room without books is like a body without a soul.", author: "Marcus Tullius Cicero" },
  { text: "Good friends, good books, and a sleepy conscience.", author: "Mark Twain" },
  { text: "So many books, so little time.", author: "Frank Zappa" },
  { text: "I have always imagined that Paradise will be a kind of library.", author: "Jorge Luis Borges" },
  { text: "The only thing that you absolutely have to know, is the location of the library.", author: "Albert Einstein" },
  { text: "If you only read the books that everyone else is reading, you can only think what everyone else is thinking.", author: "Haruki Murakami" },
  { text: "That is part of the beauty of all literature.", author: "F. Scott Fitzgerald" },
  { text: "Books are a uniquely portable magic.", author: "Stephen King" },
  { text: "There is no such thing as a moral or an immoral book.", author: "Oscar Wilde" },
  { text: "We read to know we're not alone.", author: "William Nicholson" },
  { text: "Let us read, and let us dance.", author: "Voltaire" },
  { text: "Books serve to show a man that those original thoughts of his aren't very new after all.", author: "Abraham Lincoln" },
  { text: "Sleep is good, he said, and books are better.", author: "George R.R. Martin" }
];

export default function LandingPage() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [quoteIndex, setQuoteIndex] = useState(0);
  const [openFaq, setOpenFaq] = useState<number | null>(0);
  const [bountyStep, setBountyStep] = useState(0);

  // Lazy load simulation
  useEffect(() => {
    const timer = setTimeout(() => setIsLoaded(true), 1200);
    return () => clearTimeout(timer);
  }, []);

  // Quote Rotator
  useEffect(() => {
    if (!isLoaded) return;
    const quoteTimer = setInterval(() => {
      setQuoteIndex((prev) => (prev + 1) % QUOTES.length);
    }, 5000);
    return () => clearInterval(quoteTimer);
  }, [isLoaded]);

  // Bounty Animation Simulation
  useEffect(() => {
    if (!isLoaded) return;
    const bountyTimer = setInterval(() => {
      setBountyStep((prev) => (prev + 1) % 3);
    }, 3000);
    return () => clearInterval(bountyTimer);
  }, [isLoaded]);

  // --- SKELETON LOADER ---
  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col p-6 animate-pulse">
        <div className="h-16 bg-slate-200 rounded-sm mb-12 w-full max-w-7xl mx-auto"></div>
        <div className="max-w-7xl mx-auto w-full grid grid-cols-1 md:grid-cols-2 gap-12 mb-20">
          <div className="space-y-6">
            <div className="h-16 bg-slate-200 rounded-sm w-3/4"></div>
            <div className="h-16 bg-slate-200 rounded-sm w-2/4"></div>
            <div className="h-8 bg-slate-200 rounded-sm w-full"></div>
            <div className="h-8 bg-slate-200 rounded-sm w-5/6"></div>
            <div className="h-12 bg-slate-200 rounded-sm w-40 mt-8"></div>
          </div>
          <div className="h-[400px] bg-slate-200 rounded-sm w-full"></div>
        </div>
        <div className="max-w-7xl mx-auto w-full grid grid-cols-4 gap-6">
          <div className="h-64 bg-slate-200 rounded-sm"></div>
          <div className="h-64 bg-slate-200 rounded-sm"></div>
          <div className="h-64 bg-slate-200 rounded-sm"></div>
          <div className="h-64 bg-slate-200 rounded-sm"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 overflow-x-hidden">
      
      {/* 1. Global Navigation Bar (Sticky) */}
      <nav className="sticky top-0 z-50 bg-white border-b-2 border-slate-900 px-6 py-4 flex items-center justify-between shadow-sm transition-all duration-300">
        <div className="flex items-center gap-2">
          <Book className="text-secondary w-6 h-6" />
          <span className="font-black text-xl tracking-tight text-secondary uppercase">LocalShelf</span>
        </div>
        
        <div className="hidden lg:flex items-center gap-8 font-mono text-xs font-bold uppercase tracking-wider text-slate-600">
          <a href="#explore" className="hover:text-secondary transition-colors">Explore</a>
          <a href="#bounties" className="hover:text-primary transition-colors flex items-center gap-1"><Zap className="w-3 h-3 text-primary" /> Bounty Board</a>
          <a href="#leaderboard" className="hover:text-secondary transition-colors">Leaderboard</a>
          <a href="#faq" className="hover:text-secondary transition-colors">FAQ</a>
        </div>
        
        <div className="flex items-center gap-4">
          <Link to="/login" className="bg-slate-100 text-secondary border-2 border-slate-300 font-mono text-xs font-bold uppercase tracking-wider px-4 py-2 hover:bg-slate-200 transition-transform active-brutal shadow-[2px_2px_0_0_#cbd5e1] rounded-sm hidden sm:block">
            Login
          </Link>
          <Link to="/signup" className="bg-primary text-secondary border-2 border-secondary font-mono text-xs font-bold uppercase tracking-wider px-4 py-2 hover:bg-yellow-400 transition-transform active-brutal shadow-[2px_2px_0_0_#0f172a] rounded-sm">
            Sign Up
          </Link>
        </div>
      </nav>

      <main className="flex-1 flex flex-col">
        
        {/* 2. Hero Section */}
        <section className="px-6 py-16 md:py-24 max-w-7xl mx-auto w-full grid grid-cols-1 md:grid-cols-12 gap-12 items-center animate-in fade-in slide-in-from-bottom-4 duration-700">
          
          <div className="md:col-span-6 space-y-8">
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-black leading-[1.1] text-secondary">
              Your Campus.<br />
              <span className="text-blue-700">Your Books.</span><br />
              <span className="bg-secondary text-primary px-3 inline-block shadow-brutal mt-3">Zero Friction.</span>
            </h1>
            
            {/* Animated Quote */}
            <div className="min-h-[80px] border-l-4 border-primary pl-4 py-1 italic text-slate-600 relative overflow-hidden">
              <div key={quoteIndex} className="animate-in fade-in slide-in-from-right-4 duration-500">
                <p className="text-lg font-medium">"{QUOTES[quoteIndex].text}"</p>
                <p className="text-sm font-mono font-bold text-slate-400 mt-2">~ {QUOTES[quoteIndex].author}</p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
              <Link to="/signup" className="bg-primary text-secondary border-2 border-secondary font-mono text-sm font-bold uppercase tracking-wider px-8 py-4 hover:bg-yellow-400 transition-transform active-brutal shadow-brutal flex items-center gap-2 rounded-sm w-full sm:w-auto justify-center">
                Explore Near You <Search className="w-5 h-5" />
              </Link>
              <span className="font-mono text-xs font-bold text-slate-500 uppercase px-4 py-2 bg-slate-200 border-2 border-slate-300 rounded-sm flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span> 150+ Students Trading
              </span>
            </div>
          </div>
          
          <div className="md:col-span-6 relative bg-secondary border-2 border-slate-900 rounded-sm p-2 shadow-brutal h-[450px] flex items-center justify-center overflow-hidden">
            <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)', backgroundSize: '20px 20px' }}></div>
            <div className="z-10 bg-slate-900/90 p-8 border border-slate-700 font-mono text-primary text-sm shadow-2xl backdrop-blur-sm rounded-sm w-3/4 transform rotate-2 hover:rotate-0 transition-transform duration-500">
              <p className="text-xs text-slate-400 mb-2">// LOCAL_SHELF AI SCANNER</p>
              <p className="text-white mb-1">@ RADIUS: <span className="text-primary">5.0KM</span></p>
              <p className="text-white mb-4">SUBJECT: <span className="text-primary">INTRO TO ALGORITHMS</span></p>
              <div className="w-full bg-slate-800 h-2 mb-4 rounded-full overflow-hidden">
                <div className="bg-primary h-full w-[80%] animate-pulse"></div>
              </div>
              <p className="animate-pulse text-green-400 font-bold">» 4 COPIES FOUND NEAR YOU_</p>
            </div>
            <div className="absolute top-0 left-0 w-full h-1 bg-primary shadow-[0_0_20px_rgba(251,191,36,1)] animate-[scan_3s_ease-in-out_infinite]"></div>
          </div>
        </section>

        {/* 3. Value Proposition: Buy, Sell, Barter */}
        <section className="px-6 py-16 bg-white border-y-2 border-slate-200">
          <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-8 border-2 border-slate-200 rounded-sm hover:border-secondary hover:shadow-brutal transition-all group bg-slate-50">
              <div className="w-14 h-14 bg-blue-100 text-blue-700 border-2 border-blue-200 rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <IndianRupee className="w-6 h-6" />
              </div>
              <h3 className="text-2xl font-black text-secondary mb-3">Buy Cheap</h3>
              <p className="text-slate-600">Get textbooks at a fraction of the cost directly from seniors on campus. No shipping fees.</p>
            </div>
            <div className="p-8 border-2 border-secondary rounded-sm shadow-brutal group bg-secondary text-white transform md:-translate-y-4">
              <div className="w-14 h-14 bg-primary text-secondary border-2 border-primary rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-brutal-dark">
                <ArrowRightLeft className="w-6 h-6" />
              </div>
              <h3 className="text-2xl font-black text-white mb-3">Barter Smarter</h3>
              <p className="text-slate-300">Done with Physics? Swap it for Chemistry. Trade books directly without spending a single rupee.</p>
            </div>
            <div className="p-8 border-2 border-slate-200 rounded-sm hover:border-secondary hover:shadow-brutal transition-all group bg-slate-50">
              <div className="w-14 h-14 bg-green-100 text-green-700 border-2 border-green-200 rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-2xl font-black text-secondary mb-3">Sell Fast</h3>
              <p className="text-slate-600">Clear your shelf and make cash instantly. Hand off the book locally today.</p>
            </div>
          </div>
        </section>

        {/* 4. Trending Genres & Authors */}
        <section className="px-6 py-20 max-w-7xl mx-auto w-full">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            <div className="lg:col-span-8">
              <h2 className="text-3xl font-black text-secondary mb-8">Explore Top Genres</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {["Computer Science", "Fiction & Fantasy", "Business & Economics", "Medical", "Self-Help", "Mathematics"].map((genre) => (
                  <Link key={genre} to="/signup" className="p-4 border-2 border-slate-200 rounded-sm text-center font-bold text-secondary hover:bg-primary hover:border-secondary hover:shadow-brutal transition-all">
                    {genre}
                  </Link>
                ))}
              </div>
            </div>
            <div className="lg:col-span-4">
              <h2 className="text-3xl font-black text-secondary mb-8">Top Authors</h2>
              <div className="flex flex-wrap gap-4">
                {[
                  { name: "J.K. Rowling", color: "bg-red-200" },
                  { name: "Don Norman", color: "bg-blue-200" },
                  { name: "Robert Martin", color: "bg-green-200" },
                  { name: "Stephen King", color: "bg-purple-200" }
                ].map((author, i) => (
                  <div key={i} className="flex flex-col items-center gap-2 group cursor-pointer">
                    <div className={`w-16 h-16 rounded-full border-2 border-secondary shadow-[2px_2px_0_0_#0f172a] group-hover:-translate-y-1 transition-transform flex items-center justify-center text-xl font-black ${author.color}`}>
                      {author.name.charAt(0)}
                    </div>
                    <span className="text-xs font-bold text-slate-600">{author.name.split(' ')[0]}</span>
                  </div>
                ))}
                <div className="flex flex-col items-center gap-2 cursor-pointer">
                  <div className="w-16 h-16 rounded-full border-2 border-slate-300 bg-slate-100 flex items-center justify-center text-sm font-black text-slate-500 hover:bg-slate-200 transition-colors">
                    +50
                  </div>
                  <span className="text-xs font-bold text-slate-500">More</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <hr className="border-t-2 border-slate-200" />

        {/* 5. Trending in Your Radius */}
        <section id="explore" className="px-6 py-20 max-w-7xl mx-auto w-full">
          <div className="flex justify-between items-end mb-10">
            <h2 className="text-3xl font-black text-secondary">Available Right Now <span className="text-slate-400 text-xl font-medium">(Within 5km)</span></h2>
            <Link to="/signup" className="font-mono text-xs font-bold uppercase text-blue-700 hover:underline flex items-center gap-1">View All <ChevronRight className="w-3 h-3" /></Link>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { title: "Design of Everyday Things", author: "Don Norman", owner: "Ujjawal", days: "02" },
              { title: "Principles of Physics", author: "Resnick Halliday", owner: "Adani Library", days: "12" },
              { title: "Clean Code", author: "Robert C. Martin", owner: "Alice", days: "05" },
              { title: "Dune", author: "Frank Herbert", owner: "Paul", days: "01" }
            ].map((book, idx) => (
              <div key={idx} className="bg-white border-2 border-slate-900 p-5 rounded-sm shadow-brutal flex flex-col group hover:-translate-y-2 transition-transform duration-300">
                <div className="bg-slate-100 aspect-[3/4] mb-5 border-2 border-slate-300 flex items-center justify-center relative overflow-hidden group-hover:border-secondary transition-colors">
                  <div className="w-20 h-28 bg-slate-300 opacity-30 shadow-inner rotate-3 group-hover:rotate-0 transition-transform"></div>
                  <div className="absolute top-2 right-2 bg-secondary text-primary font-mono text-[10px] font-bold px-2 py-1 rounded-sm flex items-center gap-1 shadow-sm">
                    <Clock className="w-3 h-3" /> {book.days}D LEFT
                  </div>
                </div>
                <h3 className="font-bold text-secondary text-lg leading-tight truncate mb-1" title={book.title}>{book.title}</h3>
                <p className="text-slate-500 text-sm mb-5 truncate">{book.author}</p>
                <div className="mt-auto flex flex-col gap-3">
                  <span className="font-mono text-[10px] uppercase font-bold text-slate-400 bg-slate-100 self-start px-2 py-1 rounded-sm border border-slate-200">Listed by {book.owner}</span>
                  <button className="w-full py-3 bg-slate-100 border-2 border-slate-300 font-mono text-xs font-bold uppercase hover:bg-secondary hover:text-white hover:border-secondary transition-colors rounded-sm active-brutal shadow-[2px_2px_0_0_#cbd5e1] hover:shadow-[2px_2px_0_0_#0f172a]">
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 6. The Bounty System (REVISED) */}
        <section id="bounties" className="px-6 py-24 bg-slate-900 w-full text-white border-y-4 border-primary relative overflow-hidden">
          <div className="absolute inset-0 opacity-5" style={{ backgroundImage: 'radial-gradient(#fbbf24 2px, transparent 2px)', backgroundSize: '30px 30px' }}></div>
          <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center relative z-10">
            <div>
              <div className="inline-flex items-center gap-2 bg-primary text-secondary px-3 py-1 rounded-sm font-mono text-xs font-bold uppercase mb-6 shadow-brutal-dark">
                <Zap className="w-4 h-4" /> Platform Feature
              </div>
              <h2 className="text-4xl md:text-5xl font-black mb-6 leading-tight">Can't find a book?<br/>Place a <span className="text-primary">Bounty.</span></h2>
              <p className="text-slate-400 text-lg mb-8 leading-relaxed">
                If the book you need isn't currently listed, hit Request. Our system immediately pings other students on campus who read similar genres, letting them know there is high demand for their idle books.
              </p>
              <Link to="/signup" className="bg-primary text-secondary border-2 border-primary font-mono text-sm font-bold uppercase tracking-wider px-8 py-4 hover:bg-yellow-400 transition-transform active-brutal shadow-brutal-dark inline-block rounded-sm">
                Request a Book Now
              </Link>
            </div>
            
            {/* Animated Bounty Concept UI */}
            <div className="bg-secondary border-2 border-slate-700 p-6 rounded-sm shadow-2xl relative">
              {bountyStep === 0 && (
                <div className="animate-in fade-in zoom-in duration-300 text-center py-12">
                  <Search className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                  <h3 className="font-mono text-slate-400">Search: "White Nights"</h3>
                  <p className="text-red-400 font-bold mt-2">0 Results Found Locally.</p>
                </div>
              )}
              {bountyStep === 1 && (
                <div className="animate-in fade-in slide-in-from-bottom-4 duration-300 text-center py-12">
                  <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4 shadow-brutal-dark animate-bounce">
                    <Zap className="w-8 h-8 text-secondary" />
                  </div>
                  <h3 className="font-bold text-xl text-white">Placing Bounty...</h3>
                  <p className="font-mono text-primary text-sm mt-2">Targeting 'Russian Lit' readers...</p>
                </div>
              )}
              {bountyStep === 2 && (
                <div className="animate-in fade-in zoom-in duration-300 text-center py-8">
                  <div className="bg-green-500/20 border border-green-500 p-4 rounded-sm inline-block mb-4">
                    <ShieldCheck className="w-8 h-8 text-green-400 mx-auto" />
                  </div>
                  <h3 className="font-bold text-xl text-white mb-2">Bounty Placed!</h3>
                  <p className="text-slate-400">12 students nearby have been notified.</p>
                  <p className="font-mono text-xs text-green-400 mt-4">Awaiting matches...</p>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* 7. Start Selling CTA Banner */}
        <section className="px-6 py-12 bg-primary border-b-2 border-slate-900 w-full text-center">
          <h2 className="text-3xl md:text-4xl font-black text-secondary mb-6">Start selling or bartering your books today.</h2>
          <Link to="/signup" className="bg-secondary text-white border-2 border-secondary font-mono text-sm font-bold uppercase tracking-wider px-10 py-4 hover:bg-slate-800 transition-transform active-brutal shadow-brutal-dark inline-block rounded-sm">
            List Your First Book Free
          </Link>
        </section>

        {/* 8. Top Traders & Environmental Impact */}
        <section id="leaderboard" className="px-6 py-20 max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-16">
          {/* Leaderboard */}
          <div>
            <div className="flex items-center gap-3 mb-8">
              <Trophy className="w-8 h-8 text-primary" />
              <h2 className="text-3xl font-black text-secondary">Top Traders This Month</h2>
            </div>
            <div className="space-y-4">
              {[
                { name: "Rahul S.", books: 14, color: "bg-yellow-100 border-yellow-400", medal: "🥇" },
                { name: "Ananya M.", books: 9, color: "bg-slate-200 border-slate-400", medal: "🥈" },
                { name: "Vikram P.", books: 7, color: "bg-orange-100 border-orange-300", medal: "🥉" }
              ].map((trader, i) => (
                <div key={i} className={`p-4 border-2 rounded-sm flex items-center justify-between ${trader.color} shadow-sm`}>
                  <div className="flex items-center gap-4">
                    <span className="text-2xl">{trader.medal}</span>
                    <span className="font-bold text-lg text-secondary">{trader.name}</span>
                  </div>
                  <div className="font-mono text-xs font-bold bg-white px-3 py-1 border border-slate-300 rounded-sm">
                    {trader.books} Books Swapped
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Environmental */}
          <div className="bg-green-50 border-2 border-green-200 p-10 rounded-sm shadow-brutal flex flex-col justify-center text-center">
            <Leaf className="w-16 h-16 text-green-500 mx-auto mb-6" />
            <h2 className="text-3xl font-black text-secondary mb-4">Our Environmental Impact</h2>
            <p className="text-lg text-slate-600 mb-6 font-medium">By buying and bartering used textbooks, our campus network has saved:</p>
            <div className="text-5xl font-black text-green-600 font-mono mb-2 tracking-tighter">1,204</div>
            <p className="font-bold text-slate-500 uppercase tracking-widest text-sm">Trees this semester</p>
          </div>
        </section>

        <hr className="border-t-2 border-slate-200" />

        {/* 9. Testimonials */}
        <section className="px-6 py-20 bg-slate-100 w-full">
          <div className="max-w-7xl mx-auto">
            <h2 className="text-3xl font-black text-secondary text-center mb-16">Word on Campus</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                { text: "Got my Engineering Math textbook in 15 minutes. Met the guy at the library cafe. Absolute game changer.", name: "Karan", dept: "CS '25" },
                { text: "I placed a bounty for 'Atomic Habits' and got a ping the next morning. Traded it for an old sci-fi novel I had.", name: "Priya", dept: "MBA '24" },
                { text: "Made enough cash selling my 1st-year books to pay for my entire semester's coffee budget.", name: "Amit", dept: "Mech '26" }
              ].map((test, i) => (
                <div key={i} className="bg-white p-8 border-2 border-slate-900 rounded-sm shadow-brutal relative">
                  <MessageCircle className="w-8 h-8 text-primary absolute -top-4 -left-4 bg-white rounded-full" />
                  <div className="flex gap-1 mb-4 text-primary">
                    <Star className="fill-primary w-4 h-4"/>
                    <Star className="fill-primary w-4 h-4"/>
                    <Star className="fill-primary w-4 h-4"/>
                    <Star className="fill-primary w-4 h-4"/>
                    <Star className="fill-primary w-4 h-4"/>
                  </div>
                  <p className="text-slate-600 italic mb-6">"{test.text}"</p>
                  <p className="font-bold text-secondary font-mono text-sm">{test.name} <span className="text-slate-400 font-normal">| {test.dept}</span></p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* 10. Expandable FAQs */}
        <section id="faq" className="px-6 py-20 max-w-3xl mx-auto w-full">
          <h2 className="text-3xl font-black text-secondary text-center mb-10">Frequently Asked Questions</h2>
          <div className="space-y-4">
            {[
              { q: "Is the platform really free?", a: "Yes! Listing books, bartering, and placing bounties are 100% free for students. We don't take a cut of your cash sales either." },
              { q: "How does the AI Scanner work?", a: "Just take a picture of the book cover. Our system automatically reads the text and fetches the exact book details from the internet so you don't have to type anything." },
              { q: "What is a Bounty?", a: "If nobody is selling the book you want, place a bounty. We'll automatically notify students who might own it so they can list it for you." },
              { q: "How do I exchange the book?", a: "Once you match with someone, a private chat opens. You can arrange to meet somewhere safe on campus, like the library or cafeteria, to do the physical swap." }
            ].map((faq, i) => (
              <div key={i} className="border-2 border-slate-200 bg-white rounded-sm overflow-hidden transition-all duration-300">
                <button 
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full px-6 py-4 flex items-center justify-between font-bold text-secondary text-left hover:bg-slate-50 transition-colors"
                >
                  {faq.q}
                  <ChevronDown className={`w-5 h-5 transition-transform duration-300 ${openFaq === i ? 'rotate-180 text-primary' : 'text-slate-400'}`} />
                </button>
                <div 
                  className={`px-6 overflow-hidden transition-all duration-500 ease-in-out bg-slate-50 border-t-2 border-slate-100 ${openFaq === i ? 'max-h-[200px] py-4' : 'max-h-0 py-0 border-t-0'}`}
                >
                  <p className="text-slate-600 text-sm leading-relaxed">{faq.a}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 11. Contact Us & Newsletter */}
        <section className="px-6 py-20 bg-secondary w-full border-t-4 border-primary">
          <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-16">
            
            {/* Contact Form */}
            <div className="bg-slate-800 p-8 border-2 border-slate-700 rounded-sm shadow-brutal-dark">
              <h3 className="text-2xl font-black text-white mb-6">Contact Support</h3>
              <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
                <div>
                  <label className="font-mono text-xs text-slate-400 uppercase font-bold block mb-2">Email</label>
                  <input type="email" placeholder="you@university.edu" className="w-full bg-slate-900 border-2 border-slate-600 text-white p-3 font-mono text-sm focus:border-primary focus:outline-none rounded-sm" />
                </div>
                <div>
                  <label className="font-mono text-xs text-slate-400 uppercase font-bold block mb-2">Message</label>
                  <textarea rows={4} placeholder="How can we help?" className="w-full bg-slate-900 border-2 border-slate-600 text-white p-3 font-mono text-sm focus:border-primary focus:outline-none rounded-sm"></textarea>
                </div>
                <button className="w-full bg-primary text-secondary font-bold font-mono uppercase py-3 rounded-sm hover:bg-yellow-400 transition-colors">
                  Send Transmission
                </button>
              </form>
            </div>

            {/* Newsletter & App Promo */}
            <div className="flex flex-col justify-between space-y-12 text-white">
              <div>
                <h3 className="text-2xl font-black mb-4 flex items-center gap-2"><Mail className="text-primary"/> Stay Updated</h3>
                <p className="text-slate-400 mb-6">Join 500+ students on our newsletter. Get alerted when rare books drop or massive bounties are placed.</p>
                <div className="flex gap-2">
                  <input type="email" placeholder="Email Address" className="flex-1 bg-slate-800 border-2 border-slate-700 text-white p-3 font-mono text-sm focus:border-primary focus:outline-none rounded-sm" />
                  <button className="bg-white text-secondary font-bold font-mono px-6 rounded-sm border-2 border-white hover:bg-slate-200 transition-colors">Subscribe</button>
                </div>
              </div>

              <div className="p-8 border-2 border-slate-700 bg-slate-900/50 rounded-sm">
                <h3 className="text-xl font-black mb-2 flex items-center gap-2"><Download className="text-primary"/> Get the Mobile App</h3>
                <p className="text-sm text-slate-400 mb-6">Scan books and chat with matches instantly from your phone.</p>
                <div className="flex gap-4">
                  <button className="bg-slate-800 border border-slate-600 hover:border-slate-400 px-4 py-2 rounded-sm flex items-center gap-2 transition-colors">
                    <span className="font-bold text-sm">App Store</span>
                  </button>
                  <button className="bg-slate-800 border border-slate-600 hover:border-slate-400 px-4 py-2 rounded-sm flex items-center gap-2 transition-colors">
                    <span className="font-bold text-sm">Google Play</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

      </main>

      {/* 12. Global Footer */}
      <footer className="bg-slate-950 text-slate-400 py-12 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <Book className="text-primary w-6 h-6" />
            <span className="font-black text-xl text-white uppercase tracking-tight">LocalShelf</span>
          </div>
          <div className="flex gap-6 font-mono text-xs font-bold uppercase">
            <a href="#" className="hover:text-primary transition-colors">Terms</a>
            <a href="#" className="hover:text-primary transition-colors">Privacy</a>
            <a href="#" className="hover:text-primary transition-colors">Guidelines</a>
          </div>
          <div className="text-xs font-mono">
            &copy; {new Date().getFullYear()} LocalShelf. All rights reserved.
          </div>
        </div>
      </footer>
      
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes scan {
          0% { top: 0%; opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { top: 100%; opacity: 0; }
        }
      `}} />
    </div>
  );
}
