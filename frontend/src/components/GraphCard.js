import React, { useEffect } from 'react';
import { Chart } from 'react-chartjs-2';
import { motion } from 'framer-motion';

const GraphCard = ({ index, graphData }) => {
  const [chartType, setChartType] = React.useState('bar');

  useEffect(() => {
    // Placeholder for dynamic graph data
  }, [chartType, graphData]);

  const data = {
    labels: graphData?.labels || ['A', 'B', 'C'],
    datasets: [{
      label: 'Data',
      data: graphData?.data || [1, 2, 3],
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      borderColor: 'rgba(75, 192, 192, 1)',
      borderWidth: 1,
    }],
  };

  return (
    <motion.div 
      className="graph-item"
      whileHover={{ scale: 1.05 }}
      style={{ marginBottom: '10px', padding: '10px', border: '1px solid #ddd', borderRadius: '5px' }}
    >
      <Chart type={chartType} data={data} />
      <select onChange={(e) => setChartType(e.target.value)} style={{ marginTop: '5px', padding: '2px', width: '100%' }}>
        <option value="bar">Bar Chart</option>
        <option value="pie">Donut Chart</option>
        <option value="line">Line Chart</option>
        <option value="scatter">Scatter Plot</option>
        <option value="bar">Histogram</option>
        <option value="heatmap">Heatmap</option>
      </select>
    </motion.div>
  );
};

export default GraphCard;
