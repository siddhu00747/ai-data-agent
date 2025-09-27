import React, {useState} from "react";
import PlotlyWrapper from "./plotlyWrapper";

export default function ChatComponent({uploadInfo}){
  const [sheet, setSheet] = useState(Object.keys(uploadInfo.metadata)[0]);
  const [q, setQ] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  async function ask(){
    if(!q) return;
    setLoading(true);
    const res = await fetch("http://localhost:8000/query", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({file_id: uploadInfo.file_id, sheet_name: sheet, question: q})
    });
    const j = await res.json();
    setLoading(false);
    const entry = {question:q, answer:j};
    setHistory([entry, ...history]);
    setQ("");
  }

  return (
    <div>
      <h3>File: {uploadInfo.filename}</h3>
      <label>Choose sheet: </label>
      <select value={sheet} onChange={e=>setSheet(e.target.value)}>
        {Object.keys(uploadInfo.metadata).map(s => <option key={s} value={s}>{s}</option>)}
      </select>

      <div style={{marginTop:12}}>
        <input style={{width:"70%"}} value={q} onChange={e=>setQ(e.target.value)} placeholder="Ask in Hinglish: e.g. Top 10 customers by revenue" />
        <button onClick={ask} disabled={loading} style={{marginLeft:8}}>{loading?"..." : "Ask"}</button>
      </div>

      <div style={{marginTop:20}}>
        {history.map((h, idx) => (
          <div key={idx} style={{border:"1px solid #ddd", padding:12, marginBottom:12}}>
            <b>Q:</b> {h.question}
            <div style={{marginTop:8}}>
              {h.answer.error ? <div style={{color:"red"}}>{h.answer.error}</div> :
                <>
                  <div><b>SQL:</b> <code style={{fontSize:12}}>{h.answer.sql}</code></div>
                  <div style={{marginTop:8}}><b>Explanation:</b> {h.answer.explain}</div>
                  {h.answer.chart && <PlotlyWrapper chart={h.answer.chart} type={h.answer.chart_type} />}
                  {h.answer.table &&
                    <div style={{marginTop:8, maxHeight:250, overflow:"auto"}}>
                      <table style={{width:"100%", borderCollapse:"collapse"}}>
                        <thead><tr>{h.answer.table.columns.map(c=> <th key={c} style={{borderBottom:"1px solid #ccc", textAlign:"left"}}>{c}</th>)}</tr></thead>
                        <tbody>
                          {h.answer.table.rows.map((r,ri) => <tr key={ri}>{h.answer.table.columns.map((c,ci)=><td key={ci} style={{padding:"6px 4px", borderBottom:"1px solid #f2f2f2"}}>{String(r[c]??"")}</td>)}</tr>)}
                        </tbody>
                      </table>
                    </div>
                  }
                </>
              }
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
