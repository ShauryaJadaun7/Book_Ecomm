export default function MyBooksTab() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-black font-mono uppercase tracking-tighter">My Inventory</h1>
      </div>
      <div className="p-8 border-4 border-slate-900 shadow-brutal bg-white rounded-sm">
        <p className="font-mono text-slate-500">Your uploaded books will go here...</p>
      </div>
    </div>
  );
}
