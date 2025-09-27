import React from "react";
import Plot from "react-plotly.js";
export default function PlotlyWrapper({chart, type}){
  if(!chart) return null;
  const data = [{ x: chart.x, y: chart.y, type: type === "line" ? "scatter" : "bar", mode: type==="line" ? "lines+markers": undefined, name: chart.series_name }];
  return <div style={{height:350}}><Plot data={data} layout={{margin:{t:20}}} useResizeHandler style={{width:"100%",height:"100%"}} /></div>;
}
