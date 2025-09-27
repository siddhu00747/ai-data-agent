import React, {useState} from "react";
export default function UploadComponent({onUploaded}){
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  async function send(){
    if(!file) return alert("Choose file");
    setLoading(true);
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch("http://localhost:8000/upload", { method: "POST", body: fd });
    const j = await res.json();
    setLoading(false);
    if(res.ok) onUploaded(j);
    else alert(JSON.stringify(j));
  }
  return (
    <div>
      <p>Upload koi Excel file (multi-sheet supported). Example: sales, customers etc.</p>
      <input type="file" accept=".xls,.xlsx" onChange={e=>setFile(e.target.files[0])} />
      <button onClick={send} disabled={loading} style={{marginLeft:10}}>
        {loading? "Uploading...":"Upload"}
      </button>
    </div>
  );
}
