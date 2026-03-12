import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, ScatterChart, Scatter
} from 'recharts';
import type { VisualisationSpec } from '../types';

interface ChartRendererProps {
  spec: VisualisationSpec;
  data: any;
}

const ChartRenderer: React.FC<ChartRendererProps> = ({ spec, data }) => {
  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  const renderChart = () => {
    switch (spec.type) {
      case 'bar_chart':
        // Transform data if necessary
        const barData = Array.isArray(data) ? data : [data];
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'table':
        if (!Array.isArray(data)) return <p>No data for table</p>;
        const keys = data.length > 0 ? Object.keys(data[0]) : [];
        return (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {keys.map(key => (
                    <th key={key} className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.map((row, idx) => (
                  <tr key={idx}>
                    {keys.map(key => (
                      <td key={key} className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">
                        {String(row[key])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );

      case 'gauge':
        const value = typeof data === 'number' ? data : 0;
        const gaugeData = [
          { name: 'Completed', value: value },
          { name: 'Remaining', value: 100 - value }
        ];
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={gaugeData}
                cx="50%"
                cy="50%"
                startAngle={180}
                endAngle={0}
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                <Cell fill="#3b82f6" />
                <Cell fill="#e2e8f0" />
              </Pie>
              <Tooltip />
              <text x="50%" y="45%" textAnchor="middle" dominantBaseline="middle" className="text-2xl font-bold">
                {value}%
              </text>
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return <div className="p-4 bg-gray-100 rounded">Visualisation type {spec.type} coming soon</div>;
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">{spec.title}</h3>
      {renderChart()}
    </div>
  );
};

export default ChartRenderer;
